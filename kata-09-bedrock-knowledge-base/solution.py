"""
Kata 09: Bedrock Knowledge Base - Solution

Managed RAG pipeline on AWS: upload documents to S3, create an S3 Vectors
bucket+index, provision a Bedrock Knowledge Base backed by those vectors,
ingest the docs, then query with a Strands agent.

Prerequisites:
    pip install 'strands-agents[bedrock]' boto3 python-dotenv
    export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
    export AWS_REGION=us-east-1   (must match the region your key was created in)

    Optional: export KB_ROLE_ARN=arn:aws:iam::...  (skip auto IAM role creation)

    To use eu-central-1: set AWS_REGION=eu-central-1 and change DEFAULT_MODEL
    prefix from "us." to "eu.".

Documents: Place PDFs in the DOCS/ folder at the repo root before running.
"""

import os
import glob
import time
import json
import uuid

# boto3 MUST be imported and the management session captured BEFORE strands is
# imported. strands-agents[bedrock] patches boto3 at import time to use
# AWS_BEARER_TOKEN_BEDROCK for all bedrock* service endpoints. That token is
# inference-only and breaks management-plane APIs (bedrock-agent, S3, IAM).
# Capturing a clean session here gives us unpatched IAM credentials for all
# management calls throughout the script.
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Clean management session — created before strands patches boto3
_mgmt_session = boto3.Session()

# strands imports come AFTER the session is captured
from strands import Agent, tool  # noqa: E402
from strands.models.bedrock import BedrockModel  # noqa: E402

DEFAULT_MODEL = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "DOCS")

# Single run ID shared across all resource names — avoids conflicts when
# multiple participants use the same AWS account simultaneously.
RUN_ID = uuid.uuid4().hex[:8]
BUCKET_NAME = f"kata09-kb-docs-{RUN_ID}"
VECTOR_BUCKET_NAME = f"kata09-vectors-{RUN_ID}"
VECTOR_INDEX_NAME = "bedrock-kb-index"
KB_NAME = f"kata09-vaisala-kb-{RUN_ID}"
DS_NAME = "vaisala-docs"

# State file — records the exact IDs/names of every resource created so that
# cleanup.py can delete precisely those resources (not someone else's).
STATE_FILE = os.path.join(os.path.dirname(__file__), "kata09_state.json")


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for pretty terminal output."""
    HEADER = '\033[96m'
    PROMPT = '\033[93m'
    RESPONSE = '\033[92m'
    STATS = '\033[95m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    @classmethod
    def header(cls, text):
        return f"{cls.BOLD}{cls.HEADER}{text}{cls.RESET}"

    @classmethod
    def prompt(cls, text):
        return f"{cls.PROMPT}{text}{cls.RESET}"

    @classmethod
    def response(cls, text):
        return f"{cls.RESPONSE}{text}{cls.RESET}"

    @classmethod
    def stats(cls, text):
        return f"{cls.STATS}{text}{cls.RESET}"


def save_state(updates: dict) -> None:
    """Merge *updates* into the state file (creates it if missing)."""
    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            state = json.load(f)
    state.update(updates)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    print(Colors.stats(f"  [state saved → {os.path.basename(STATE_FILE)}]"))


# ==============================================================================
# Step 1: S3 Bucket + Document Upload
# ==============================================================================

def create_bucket_and_upload(bucket_name: str) -> list[str]:
    """Create an S3 bucket and upload all PDFs from the DOCS/ folder."""
    s3 = _mgmt_session.client("s3", region_name=AWS_REGION)

    print(Colors.stats(f"Creating S3 bucket: {bucket_name}"))
    if AWS_REGION == "us-east-1":
        s3.create_bucket(Bucket=bucket_name)
    else:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": AWS_REGION}
        )
    save_state({"bucket_name": bucket_name, "region": AWS_REGION})

    pdfs = glob.glob(os.path.join(DOCS_DIR, "*.pdf"))
    if not pdfs:
        print(Colors.stats(f"No PDFs found in {DOCS_DIR}. Add PDF files to continue."))
        return []

    uploaded = []
    for pdf_path in pdfs:
        key = os.path.basename(pdf_path)
        print(Colors.stats(f"  Uploading: {key}"))
        s3.upload_file(pdf_path, bucket_name, key)
        uploaded.append(key)

    print(Colors.stats(f"Uploaded {len(uploaded)} document(s) to s3://{bucket_name}/"))
    return uploaded


# ==============================================================================
# Step 2: S3 Vectors bucket + index
# ==============================================================================

def create_vector_store() -> str:
    """Create an S3 Vectors bucket and index for the Knowledge Base.

    S3_VECTORS storage requires a pre-existing vector index. Bedrock uses
    Titan Embed v2 (1024-dimensional float32 vectors with euclidean distance).

    Returns the indexArn to pass to create_knowledge_base().
    """
    s3v = _mgmt_session.client("s3vectors", region_name=AWS_REGION)

    print(Colors.stats(f"Creating S3 Vectors bucket: {VECTOR_BUCKET_NAME}"))
    s3v.create_vector_bucket(vectorBucketName=VECTOR_BUCKET_NAME)
    save_state({"vector_bucket_name": VECTOR_BUCKET_NAME})

    print(Colors.stats(f"Creating vector index: {VECTOR_INDEX_NAME}"))
    resp = s3v.create_index(
        vectorBucketName=VECTOR_BUCKET_NAME,
        indexName=VECTOR_INDEX_NAME,
        dataType="float32",
        dimension=1024,
        distanceMetric="euclidean",
        metadataConfiguration={
            "nonFilterableMetadataKeys": ["AMAZON_BEDROCK_TEXT", "AMAZON_BEDROCK_METADATA"]
        }
    )
    index_arn = resp["indexArn"]
    print(Colors.stats(f"Vector index created: {index_arn}"))
    save_state({"vector_index_arn": index_arn})
    return index_arn


# ==============================================================================
# Step 3: IAM Role for Knowledge Base
# ==============================================================================

def _create_kb_iam_role(bucket_name: str, index_arn: str) -> str:
    """Auto-create a minimal IAM role for the Bedrock Knowledge Base."""
    iam = _mgmt_session.client("iam", region_name=AWS_REGION)
    sts = _mgmt_session.client("sts", region_name=AWS_REGION)
    account_id = sts.get_caller_identity()["Account"]
    role_name = f"kata09-kb-role-{RUN_ID}"

    # Bedrock Knowledge Bases require both SourceAccount and SourceArn conditions
    trust_policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "AmazonBedrockKnowledgeBaseTrustPolicy",
            "Effect": "Allow",
            "Principal": {"Service": "bedrock.amazonaws.com"},
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {"aws:SourceAccount": account_id},
                "ArnLike": {
                    "aws:SourceArn": f"arn:aws:bedrock:{AWS_REGION}:{account_id}:knowledge-base/*"
                }
            }
        }]
    })

    role = iam.create_role(
        RoleName=role_name,
        Path="/service-role/",
        AssumeRolePolicyDocument=trust_policy,
        Description="Kata 09 - Bedrock Knowledge Base role"
    )
    role_arn = role["Role"]["Arn"]

    # Bedrock InvokeModel permission for embedding
    iam.put_role_policy(
        RoleName=role_name,
        PolicyName="kata09-bedrock-policy",
        PolicyDocument=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": ["bedrock:InvokeModel"],
                "Resource": (
                    f"arn:aws:bedrock:{AWS_REGION}::foundation-model/"
                    "amazon.titan-embed-text-v2:0"
                )
            }]
        })
    )

    # S3 read permission for documents bucket
    iam.put_role_policy(
        RoleName=role_name,
        PolicyName="kata09-s3-policy",
        PolicyDocument=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket"],
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ],
                "Condition": {"StringEquals": {"aws:ResourceAccount": account_id}}
            }]
        })
    )

    # S3 Vectors permission — Bedrock validates this before allowing KB creation
    iam.put_role_policy(
        RoleName=role_name,
        PolicyName="kata09-s3vectors-policy",
        PolicyDocument=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Sid": "S3VectorsPermissions",
                "Effect": "Allow",
                "Action": [
                    "s3vectors:GetIndex",
                    "s3vectors:QueryVectors",
                    "s3vectors:PutVectors",
                    "s3vectors:GetVectors",
                    "s3vectors:DeleteVectors"
                ],
                "Resource": index_arn,
                "Condition": {"StringEquals": {"aws:ResourceAccount": account_id}}
            }]
        })
    )

    print(Colors.stats(f"Created IAM role: {role_arn}"))
    save_state({"role_name": role_name})
    # IAM changes take time to propagate globally
    time.sleep(20)
    return role_arn


def get_kb_role_arn(bucket_name: str, index_arn: str) -> str:
    """Return KB_ROLE_ARN env var if set; otherwise auto-create a role."""
    env_arn = os.getenv("KB_ROLE_ARN")
    if env_arn:
        print(Colors.stats(f"Using existing IAM role from KB_ROLE_ARN: {env_arn}"))
        # Not auto-created — cleanup.py will leave it alone
        return env_arn
    print(Colors.stats("KB_ROLE_ARN not set — creating IAM role automatically..."))
    return _create_kb_iam_role(bucket_name, index_arn)


# ==============================================================================
# Step 4 & 5: Knowledge Base + Ingestion
# ==============================================================================

def create_knowledge_base(role_arn: str, index_arn: str) -> str:
    """Create a Bedrock Knowledge Base backed by the given S3 Vectors index."""
    bedrock_agent = _mgmt_session.client("bedrock-agent", region_name=AWS_REGION)

    print(Colors.stats(f"Creating Knowledge Base: {KB_NAME}"))
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
            "s3VectorsConfiguration": {"indexArn": index_arn}
        },
    )
    kb_id = kb["knowledgeBase"]["knowledgeBaseId"]
    print(Colors.stats(f"Knowledge Base created: {kb_id}"))
    save_state({"kb_id": kb_id})
    return kb_id


def create_data_source_and_ingest(kb_id: str, bucket_name: str) -> None:
    """Create an S3 data source and run (and poll) the ingestion job."""
    bedrock_agent = _mgmt_session.client("bedrock-agent", region_name=AWS_REGION)

    # Create data source
    print(Colors.stats("Creating S3 data source..."))
    ds = bedrock_agent.create_data_source(
        knowledgeBaseId=kb_id,
        name=DS_NAME,
        dataSourceConfiguration={
            "type": "S3",
            "s3Configuration": {
                "bucketArn": f"arn:aws:s3:::{bucket_name}"
            }
        }
    )
    ds_id = ds["dataSource"]["dataSourceId"]
    print(Colors.stats(f"Data source created: {ds_id}"))
    save_state({"ds_id": ds_id})

    # Start ingestion job
    print(Colors.stats("Starting ingestion job..."))
    job = bedrock_agent.start_ingestion_job(
        knowledgeBaseId=kb_id,
        dataSourceId=ds_id
    )
    job_id = job["ingestionJob"]["ingestionJobId"]

    # Poll until COMPLETE or FAILED
    print(Colors.stats("Polling ingestion status "), end="")
    while True:
        status_resp = bedrock_agent.get_ingestion_job(
            knowledgeBaseId=kb_id,
            dataSourceId=ds_id,
            ingestionJobId=job_id
        )
        status = status_resp["ingestionJob"]["status"]
        print(Colors.stats(f"[{status}]"), end=" ", flush=True)
        if status in ("COMPLETE", "FAILED", "STOPPED"):
            break
        time.sleep(10)

    print()
    if status != "COMPLETE":
        raise RuntimeError(f"Ingestion job ended with status: {status}")
    print(Colors.stats("Ingestion complete!"))


# ==============================================================================
# Step 6: Strands Agent with KB retrieval tool
# ==============================================================================

# Module-level variable populated in main()
_kb_id: str = ""


@tool
def search_vaisala_docs(query: str) -> str:
    """Search the Vaisala technical documentation knowledge base for answers.

    Args:
        query: The question or topic to search for in the documentation.
    """
    # Use the management session so retrieval also bypasses the bearer token patch
    bedrock_runtime = _mgmt_session.client("bedrock-agent-runtime", region_name=AWS_REGION)
    result = bedrock_runtime.retrieve(
        knowledgeBaseId=_kb_id,
        retrievalQuery={"text": query},
        retrievalConfiguration={
            "vectorSearchConfiguration": {"numberOfResults": 3}
        }
    )
    chunks = [r["content"]["text"] for r in result["retrievalResults"]]
    if not chunks:
        return "No relevant documentation found."
    return "\n\n---\n\n".join(chunks)


def build_agent() -> Agent:
    """Build a Strands agent backed by Bedrock, with the KB search tool."""
    model = BedrockModel(model_id=DEFAULT_MODEL, region_name=AWS_REGION, max_tokens=1024)
    return Agent(
        model=model,
        tools=[search_vaisala_docs],
        system_prompt=(
            "You are a technical support assistant for Vaisala products. "
            "Always search the documentation before answering questions."
        )
    )


# ==============================================================================
# Main
# ==============================================================================

def main():
    global _kb_id

    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 09: Bedrock Knowledge Base - Solution"))
    print(Colors.header(f" Region: {AWS_REGION}  |  Run ID: {RUN_ID}"))
    print(Colors.header("=" * 70))

    try:
        # Step 1: Upload documents
        print(Colors.header("\n1. Uploading documents to S3"))
        print("-" * 40)
        create_bucket_and_upload(BUCKET_NAME)

        # Step 2: Create S3 Vectors store
        print(Colors.header("\n2. Creating S3 Vectors store"))
        print("-" * 40)
        index_arn = create_vector_store()

        # Step 3: IAM role (needs both bucket and index ARN)
        print(Colors.header("\n3. Preparing IAM role"))
        print("-" * 40)
        role_arn = get_kb_role_arn(BUCKET_NAME, index_arn)

        # Step 4: Create Knowledge Base
        print(Colors.header("\n4. Creating Knowledge Base (S3_VECTORS)"))
        print("-" * 40)
        _kb_id = create_knowledge_base(role_arn, index_arn)

        # Step 5: Ingest
        print(Colors.header("\n5. Ingesting documents"))
        print("-" * 40)
        create_data_source_and_ingest(_kb_id, BUCKET_NAME)

        # Step 6: Query
        print(Colors.header("\n6. Querying with Strands agent"))
        print("-" * 40)
        agent = build_agent()

        questions = [
            "What are the steps to update VaiNet device firmware?",
            "How do I replace an SSL/TLS certificate on a Vaisala device?",
            "What wireless standards does the AP10 access point support?",
        ]

        for question in questions:
            print(Colors.prompt(f"\nUser: {question}"))
            response = agent(question)
            print(Colors.response(f"Agent: {response}"))

    except NoCredentialsError:
        print("\nError: AWS credentials not configured.")
        print("Set AWS_BEARER_TOKEN_BEDROCK and AWS_REGION environment variables.")
    except ClientError as e:
        print(f"\nAWS error: {e}")
        raise

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 09 Complete!"))
    print(Colors.header("=" * 70))
    print(Colors.stats(f"\nResource IDs saved to: {os.path.basename(STATE_FILE)}"))
    print(Colors.stats("Run  python cleanup.py  when you are done to delete all AWS resources."))


if __name__ == "__main__":
    main()
