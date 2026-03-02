# Kata 09: Bedrock Knowledge Base

## Objective

Build a fully-managed RAG (Retrieval-Augmented Generation) pipeline on AWS. Instead of running your own vector database (like ChromaDB in kata-04), delegate everything to AWS: S3 for document storage, S3 Vectors for the vector index, Bedrock Knowledge Bases for chunking and embedding — no OpenSearch or Pinecone required.

## Learning Goals

- Create an S3 bucket and upload documents programmatically with `boto3`
- Create an S3 Vectors bucket and index for managed vector storage
- Auto-provision an IAM role with Bedrock, S3, and S3 Vectors permissions
- Create a Bedrock Knowledge Base using `S3_VECTORS` storage
- Run and monitor an ingestion job via `start_ingestion_job()` + polling loop
- Query the knowledge base with `retrieve()`
- Wrap KB retrieval as a Strands `@tool` for a conversational agent
- Chat interactively with the agent using `chat.py`

## Prerequisites

- Completed Kata 04 (Local RAG) — understand RAG concepts
- AWS account with Bedrock + Bedrock Knowledge Bases enabled
- `AWS_BEARER_TOKEN_BEDROCK` and `AWS_REGION` environment variables set

```bash
pip install 'strands-agents[bedrock]' boto3 python-dotenv
export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
export AWS_REGION=us-east-1
```

**Optional** — skip auto IAM role creation (useful for restricted accounts):
```bash
export KB_ROLE_ARN=arn:aws:iam::123456789012:role/your-existing-kb-role
```

## Documents

Place PDF files in the `DOCS/` folder at the repository root. The sample Vaisala technical documents (AP10 access point manuals, VaiNet firmware guide, SSL/TLS certificate guide) are already there.

## Time Estimate

45–60 minutes

## Difficulty

⭐⭐⭐ (Advanced — involves AWS infrastructure provisioning)

---

## Background

### Kata 04 vs Kata 09: Local vs Managed RAG

| Aspect | Kata 04 (Local) | Kata 09 (Bedrock KB) |
|--------|----------------|----------------------|
| Embeddings | HuggingFace (local CPU) | Amazon Titan Embed v2 |
| Vector store | ChromaDB (local disk) | S3 Vectors (AWS managed) |
| Chunking | LlamaIndex default | Bedrock default (512 tokens) |
| Scaling | Single machine | Serverless, auto-scales |
| Cost | Free (local compute) | Pay per token + S3 storage |
| Setup time | Minutes | 5–15 min (ingestion) |

### Architecture

```
┌──────────┐     ┌──────────────┐     ┌─────────────────────────┐
│  DOCS/   │────▶│  S3 Bucket   │────▶│  Bedrock Knowledge Base  │
│  (PDFs)  │     │  (storage)   │     │  - Titan Embed v2        │
└──────────┘     └──────────────┘     │  - S3 Vectors store      │
                                      └────────────┬────────────┘
                 ┌──────────────┐                  │
                 │  S3 Vectors  │◀─────────────────┘
                 │  bucket/index│  vectors written during ingestion
                 └──────────────┘
                                                   │ retrieve()
                 ┌─────────────────────────────────▼──────────────────┐
                 │             Strands Agent (BedrockModel)            │
                 │  @tool search_vaisala_docs → retrieve() API call    │
                 └────────────────────────────────────────────────────┘
```

### S3 Vectors: Bedrock's Built-in Vector Store

`S3_VECTORS` storage type uses Amazon S3 Vectors — a dedicated vector storage service built into S3. Unlike OpenSearch, you only pay for what you store and query, with no always-on cluster. You must create the S3 Vectors bucket and index **before** creating the Knowledge Base, and the KB role must have `s3vectors:*` permissions on that specific index ARN.

### IAM Role Requirements

The Knowledge Base service role needs three sets of permissions:
- `bedrock:InvokeModel` on the Titan Embed v2 foundation model
- `s3:GetObject` + `s3:ListBucket` on your documents bucket
- `s3vectors:GetIndex/QueryVectors/PutVectors/GetVectors/DeleteVectors` on the S3 Vectors index

The starter auto-creates this role if `KB_ROLE_ARN` is not set. For accounts where `iam:CreateRole` is restricted, set `KB_ROLE_ARN` before running (ensure it already has all three permission sets).

### boto3 Session Ordering

`strands-agents[bedrock]` patches `boto3` at import time to use `AWS_BEARER_TOKEN_BEDROCK` for all `bedrock*` service endpoints. That bearer token is inference-only — it breaks management-plane APIs (`bedrock-agent`, `s3vectors`, S3, IAM).

**Fix**: capture `_mgmt_session = boto3.Session()` **before** importing `strands`, then use `_mgmt_session.client(...)` for all management calls throughout the script.

---

## Level 1: Challenge

Build a Python script that:

1. Creates an S3 bucket and uploads all PDFs from `DOCS/`
2. Creates an S3 Vectors bucket and index (1024-dim float32, euclidean)
3. Creates (or reuses) an IAM role with Bedrock + S3 + S3 Vectors permissions
4. Creates a Bedrock Knowledge Base pointing at the S3 Vectors index
5. Starts an ingestion job and polls until `COMPLETE`
6. Defines a `search_vaisala_docs` `@tool` that calls `retrieve()`
7. Creates a Strands agent with the search tool and answers Vaisala-specific questions

### Success Criteria

- [ ] S3 bucket created and PDFs uploaded
- [ ] S3 Vectors bucket and index created
- [ ] Knowledge Base created with `S3_VECTORS`
- [ ] Ingestion job completes with `COMPLETE` status
- [ ] Agent uses the retrieval tool to answer document-grounded questions
- [ ] Answers reference specific content from the Vaisala PDFs
- [ ] `chat.py` connects to the running KB for interactive Q&A

---

## Level 2: Step-by-Step Guide

### Step 1: Create S3 Bucket and Upload Documents

```python
# Use _mgmt_session (captured before strands import) for all management calls
s3 = _mgmt_session.client("s3", region_name=AWS_REGION)

# Note: us-east-1 does NOT accept LocationConstraint
if AWS_REGION == "us-east-1":
    s3.create_bucket(Bucket=BUCKET_NAME)
else:
    s3.create_bucket(
        Bucket=BUCKET_NAME,
        CreateBucketConfiguration={"LocationConstraint": AWS_REGION}
    )

for pdf in glob.glob(f"{DOCS_DIR}/*.pdf"):
    s3.upload_file(pdf, BUCKET_NAME, os.path.basename(pdf))
```

### Step 2: Create S3 Vectors Store

S3_VECTORS requires a pre-existing vector index. Bedrock validates the role's `s3vectors:*` permissions against this specific `indexArn` before allowing KB creation.

```python
s3v = _mgmt_session.client("s3vectors", region_name=AWS_REGION)

s3v.create_vector_bucket(vectorBucketName=VECTOR_BUCKET_NAME)

resp = s3v.create_index(
    vectorBucketName=VECTOR_BUCKET_NAME,
    indexName=VECTOR_INDEX_NAME,
    dataType="float32",
    dimension=1024,           # Titan Embed v2 output dimension
    distanceMetric="euclidean",
    metadataConfiguration={
        "nonFilterableMetadataKeys": ["AMAZON_BEDROCK_TEXT", "AMAZON_BEDROCK_METADATA"]
    }
)
index_arn = resp["indexArn"]
```

### Step 3: Create Knowledge Base

```python
bedrock_agent = _mgmt_session.client("bedrock-agent", region_name=AWS_REGION)

kb = bedrock_agent.create_knowledge_base(
    name=KB_NAME,
    roleArn=role_arn,
    knowledgeBaseConfiguration={
        "type": "VECTOR",
        "vectorKnowledgeBaseConfiguration": {
            "embeddingModelArn": (
                f"arn:aws:bedrock:{AWS_REGION}::foundation-model/"
                "amazon.titan-embed-text-v2:0"
            )
        }
    },
    storageConfiguration={
        "type": "S3_VECTORS",
        "s3VectorsConfiguration": {"indexArn": index_arn}  # must exist
    },
)
kb_id = kb["knowledgeBase"]["knowledgeBaseId"]
```

### Step 4: Ingest Documents

```python
ds = bedrock_agent.create_data_source(
    knowledgeBaseId=kb_id, name="vaisala-docs",
    dataSourceConfiguration={
        "type": "S3",
        "s3Configuration": {"bucketArn": f"arn:aws:s3:::{BUCKET_NAME}"}
    }
)
ds_id = ds["dataSource"]["dataSourceId"]

job = bedrock_agent.start_ingestion_job(
    knowledgeBaseId=kb_id, dataSourceId=ds_id
)
job_id = job["ingestionJob"]["ingestionJobId"]

# Poll until done
while True:
    resp = bedrock_agent.get_ingestion_job(
        knowledgeBaseId=kb_id, dataSourceId=ds_id, ingestionJobId=job_id
    )
    status = resp["ingestionJob"]["status"]
    if status in ("COMPLETE", "FAILED", "STOPPED"):
        break
    time.sleep(10)
```

### Step 5: Define Retrieval Tool

```python
from strands import tool

@tool
def search_vaisala_docs(query: str) -> str:
    """Search the Vaisala technical documentation knowledge base.

    Args:
        query: The question or topic to search for.
    """
    # Use _mgmt_session — bypasses the bearer token patch
    runtime = _mgmt_session.client("bedrock-agent-runtime", region_name=AWS_REGION)
    result = runtime.retrieve(
        knowledgeBaseId=_kb_id,
        retrievalQuery={"text": query},
        retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 3}}
    )
    chunks = [r["content"]["text"] for r in result["retrievalResults"]]
    return "\n\n---\n\n".join(chunks) if chunks else "No results found."
```

### Step 6: Build and Run Agent

```python
from strands import Agent
from strands.models.bedrock import BedrockModel

agent = Agent(
    model=BedrockModel(model_id=DEFAULT_MODEL, region_name=AWS_REGION),
    tools=[search_vaisala_docs],
    system_prompt="You are a Vaisala technical support assistant. Always search documentation before answering."
)

response = agent("What are the steps to update VaiNet device firmware?")
print(response)
```

---

## Running the Solution

```bash
# Ensure PDFs are in DOCS/ at the repo root, then:
python solution.py
```

Expected output:
```
1. Uploading documents to S3
Creating S3 bucket: kata09-kb-docs-a1b2c3d4
  Uploading: AP10_User_Guide.pdf
  Uploading: VaiNet_Firmware_Guide.pdf
  [state saved → kata09_state.json]

2. Creating S3 Vectors store
Creating S3 Vectors bucket: kata09-vectors-a1b2c3d4
Creating vector index: bedrock-kb-index
Vector index created: arn:aws:s3vectors:us-east-1:...

3. Preparing IAM role
Created IAM role: arn:aws:iam::123456789:role/kata09-kb-role-abc123

4. Creating Knowledge Base (S3_VECTORS)
Knowledge Base created: ABCDEF1234

5. Ingesting documents
[STARTING] [COMPLETE]
Ingestion complete!

6. Querying with Strands agent
User: What are the steps to update VaiNet device firmware?
Agent: According to the VaiNet documentation, firmware updates involve ...
```

> **Note:** Ingestion is typically fast (under a minute for a few PDFs). `kata09_state.json` is written after each step — if the script fails partway through, run `python cleanup.py` before retrying.

---

## Interactive Chat

After `solution.py` completes, use `chat.py` to explore the Knowledge Base interactively. It reads the KB ID automatically from `kata09_state.json` — no configuration needed.

```bash
python chat.py
```

```
============================================================
 Vaisala KB Chat
 KB: ABCDEF1234  |  Region: us-east-1
============================================================
 Type your question and press Enter.
 Commands: /quit  /clear  /help

You: What is the default login for the AP10 web interface?
Agent: The default login credentials for the AP10 web interface are:
  Username: apadmin
  Password: ap123456
...

You: /clear
Conversation cleared.

You: /quit
Goodbye!
```

**Commands:**

| Command | Effect |
|---------|--------|
| `/quit` | Exit the chat |
| `/clear` | Start a fresh conversation (clears history) |
| `/help` | Show available commands |

The agent maintains full conversation history within a session — follow-up questions work naturally. Each call to `search_vaisala_docs` retrieves the top 5 chunks from the KB.

---

## Cleanup

When you are done, delete all AWS resources created by this kata:

```bash
python cleanup.py
```

This reads `kata09_state.json` and deletes:
- Bedrock Knowledge Base + data source
- S3 documents bucket (emptied first)
- S3 Vectors bucket + index
- IAM role (only if auto-created — skipped when `KB_ROLE_ARN` was set)

---

## Extension Challenges

1. **retrieve_and_generate**: Use `retrieve_and_generate()` for one-shot RAG without a Strands agent
2. **Metadata filters**: Add document metadata to S3 objects and filter retrievals by document type
3. **Multiple data sources**: Add a second data source pointing to a different S3 bucket
4. **Streaming responses**: Modify `chat.py` to stream agent responses token by token

---

## Key Concepts

### Why Managed RAG?

Local RAG (kata-04) is great for development and small datasets. Managed Bedrock Knowledge Bases shine when you need:
- **Scale**: Millions of documents without managing infrastructure
- **Currency**: Connect web crawler or Confluence as a live data source
- **Integration**: Combine with Bedrock Agents for complex workflows
- **Operations**: No vector DB to patch, tune, or monitor

### Ingestion Pipeline

When you call `start_ingestion_job()`, Bedrock automatically:
1. Downloads documents from S3
2. Splits them into chunks (default: 512 tokens with 20% overlap)
3. Computes embeddings with Titan Embed v2 (1024 dimensions)
4. Stores vectors in the S3 Vectors index

---

## Resources

- [Bedrock Knowledge Bases Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [Amazon S3 Vectors](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors.html)
- [Strands BedrockModel](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/models/bedrock/)
