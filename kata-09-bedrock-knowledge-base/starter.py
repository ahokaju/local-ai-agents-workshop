"""
Kata 09: Bedrock Knowledge Base - Starter Template

Complete the TODOs to build a fully-managed RAG pipeline on AWS:
upload documents to S3, create an S3 Vectors index, provision a Bedrock
Knowledge Base, ingest the docs, then query with a Strands agent.

Prerequisites:
    pip install 'strands-agents[bedrock]' boto3 python-dotenv
    export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
    export AWS_REGION=us-east-1   (must match the region your key was created in)

    Optional: export KB_ROLE_ARN=arn:aws:iam::...  (skip auto IAM role creation)

Documents: Place PDFs in the DOCS/ folder at the repo root before running.
"""

import os
import glob
import time
import json
import uuid

# boto3 MUST be imported and the management session captured BEFORE strands is
# imported. strands-agents[bedrock] patches boto3 at import time to use
# AWS_BEARER_TOKEN_BEDROCK for all bedrock* endpoints. That token is
# inference-only — management APIs (bedrock-agent, S3, IAM, s3vectors) need
# standard IAM credentials.
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Clean management session — captured before strands patches boto3
_mgmt_session = boto3.Session()

# TODO 1: Import Agent, tool from strands and BedrockModel from strands.models.bedrock
# (keep these AFTER _mgmt_session is created)

DEFAULT_MODEL = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "DOCS")

# Single run ID shared across all resource names — avoids conflicts when
# multiple participants use the same AWS account simultaneously.
RUN_ID = uuid.uuid4().hex[:8]
BUCKET_NAME = f"kata09-kb-docs-{RUN_ID}"
VECTOR_BUCKET_NAME = f"kata09-vectors-{RUN_ID}"
VECTOR_INDEX_NAME = "bedrock-kb-index"
KB_NAME = f"kata09-workshop-kb-{RUN_ID}"
DS_NAME = "workshop-docs"

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
    TODO = '\033[91m'
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

    @classmethod
    def todo(cls, text):
        return f"{cls.TODO}{text}{cls.RESET}"


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
# TODO 2: Create S3 bucket and upload documents
# ==============================================================================

def create_bucket_and_upload(bucket_name: str) -> list[str]:
    """Create an S3 bucket and upload all PDFs from the DOCS/ folder.

    Steps:
        1. Create boto3 s3 client with AWS_REGION
        2. Call s3.create_bucket() — note: us-east-1 doesn't need LocationConstraint
        3. Call save_state({"bucket_name": bucket_name, "region": AWS_REGION})
        4. Glob for *.pdf files in DOCS_DIR
        5. Call s3.upload_file() for each PDF
        6. Return list of uploaded file keys
    """
    # TODO: Implement bucket creation and file upload
    # s3 = _mgmt_session.client("s3", region_name=AWS_REGION)
    # if AWS_REGION == "us-east-1":
    #     s3.create_bucket(Bucket=bucket_name)
    # else:
    #     s3.create_bucket(Bucket=bucket_name,
    #                      CreateBucketConfiguration={"LocationConstraint": AWS_REGION})
    # save_state({"bucket_name": bucket_name, "region": AWS_REGION})
    # pdfs = glob.glob(os.path.join(DOCS_DIR, "*.pdf"))
    # for pdf_path in pdfs:
    #     s3.upload_file(pdf_path, bucket_name, os.path.basename(pdf_path))

    print(Colors.todo("TODO 2: Implement create_bucket_and_upload()"))
    return []


# ==============================================================================
# TODO 3: Create the S3 Vectors bucket and index
# ==============================================================================

def create_vector_store() -> str:
    """Create an S3 Vectors bucket and index for the Knowledge Base.

    S3_VECTORS requires a pre-existing vector index — Bedrock validates that
    the KB role has s3vectors permissions on this exact index before allowing
    KB creation. Titan Embed v2 produces 1024-dimensional float32 vectors.

    Steps:
        1. Create boto3 's3vectors' client
        2. Call create_vector_bucket(vectorBucketName=VECTOR_BUCKET_NAME)
        3. Call save_state({"vector_bucket_name": VECTOR_BUCKET_NAME})
        4. Call create_index() with dimension=1024, dataType="float32",
           distanceMetric="euclidean", and the AMAZON_BEDROCK_* metadata keys
        5. Call save_state({"vector_index_arn": index_arn})
        6. Return the indexArn
    """
    # TODO: Implement S3 Vectors bucket and index creation
    # s3v = _mgmt_session.client("s3vectors", region_name=AWS_REGION)
    # s3v.create_vector_bucket(vectorBucketName=VECTOR_BUCKET_NAME)
    # save_state({"vector_bucket_name": VECTOR_BUCKET_NAME})
    # resp = s3v.create_index(
    #     vectorBucketName=VECTOR_BUCKET_NAME,
    #     indexName=VECTOR_INDEX_NAME,
    #     dataType="float32",
    #     dimension=1024,
    #     distanceMetric="euclidean",
    #     metadataConfiguration={
    #         "nonFilterableMetadataKeys": ["AMAZON_BEDROCK_TEXT", "AMAZON_BEDROCK_METADATA"]
    #     }
    # )
    # index_arn = resp["indexArn"]
    # save_state({"vector_index_arn": index_arn})
    # return index_arn

    print(Colors.todo("TODO 3: Implement create_vector_store()"))
    return "TODO-index-arn"


# ==============================================================================
# Helper: IAM Role (provided — no need to modify)
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
    time.sleep(20)  # IAM propagation delay
    return role_arn


def get_kb_role_arn(bucket_name: str, index_arn: str) -> str:
    """Return KB_ROLE_ARN env var if set; otherwise auto-create a role."""
    env_arn = os.getenv("KB_ROLE_ARN")
    if env_arn:
        # Not auto-created — cleanup.py will leave it alone
        return env_arn
    return _create_kb_iam_role(bucket_name, index_arn)


# ==============================================================================
# TODO 4: Create the Knowledge Base with S3_VECTORS storage
# ==============================================================================

def create_knowledge_base(role_arn: str, index_arn: str) -> str:
    """Create a Bedrock Knowledge Base backed by the given S3 Vectors index.

    Steps:
        1. Create boto3 'bedrock-agent' client
        2. Call create_knowledge_base() with:
               knowledgeBaseConfiguration.type = "VECTOR"
               vectorKnowledgeBaseConfiguration.embeddingModelArn = Titan Embed v2
               storageConfiguration.type = "S3_VECTORS"
               s3VectorsConfiguration.indexArn = index_arn
        3. Call save_state({"kb_id": kb_id})
        4. Return the knowledgeBaseId
    """
    # TODO: Implement Knowledge Base creation
    # bedrock_agent = _mgmt_session.client("bedrock-agent", region_name=AWS_REGION)
    # kb = bedrock_agent.create_knowledge_base(
    #     name=KB_NAME,
    #     roleArn=role_arn,
    #     knowledgeBaseConfiguration={
    #         "type": "VECTOR",
    #         "vectorKnowledgeBaseConfiguration": {
    #             "embeddingModelArn": (
    #                 f"arn:aws:bedrock:{AWS_REGION}::foundation-model/"
    #                 "amazon.titan-embed-text-v2:0"
    #             )
    #         }
    #     },
    #     storageConfiguration={
    #         "type": "S3_VECTORS",
    #         "s3VectorsConfiguration": {"indexArn": index_arn}
    #     },
    # )
    # kb_id = kb["knowledgeBase"]["knowledgeBaseId"]
    # save_state({"kb_id": kb_id})
    # return kb_id

    print(Colors.todo("TODO 4: Implement create_knowledge_base()"))
    return "TODO-kb-id"


# ==============================================================================
# TODO 5: Create data source and run ingestion job
# ==============================================================================

def create_data_source_and_ingest(kb_id: str, bucket_name: str) -> None:
    """Create an S3 data source and poll the ingestion job until COMPLETE.

    Steps:
        1. Call create_data_source() pointing to the S3 bucket ARN
        2. Call save_state({"ds_id": ds_id})
        3. Call start_ingestion_job()
        4. Poll get_ingestion_job() every 10 s until status is COMPLETE/FAILED
    """
    # TODO: Implement data source creation and ingestion polling
    # bedrock_agent = _mgmt_session.client("bedrock-agent", region_name=AWS_REGION)
    # ds = bedrock_agent.create_data_source(
    #     knowledgeBaseId=kb_id, name=DS_NAME,
    #     dataSourceConfiguration={
    #         "type": "S3",
    #         "s3Configuration": {"bucketArn": f"arn:aws:s3:::{bucket_name}"}
    #     }
    # )
    # ds_id = ds["dataSource"]["dataSourceId"]
    # save_state({"ds_id": ds_id})
    # job = bedrock_agent.start_ingestion_job(knowledgeBaseId=kb_id, dataSourceId=ds_id)
    # job_id = job["ingestionJob"]["ingestionJobId"]
    # while True:
    #     resp = bedrock_agent.get_ingestion_job(
    #         knowledgeBaseId=kb_id, dataSourceId=ds_id, ingestionJobId=job_id)
    #     status = resp["ingestionJob"]["status"]
    #     if status in ("COMPLETE", "FAILED", "STOPPED"):
    #         break
    #     time.sleep(10)

    print(Colors.todo("TODO 5: Implement create_data_source_and_ingest()"))


# ==============================================================================
# TODO 6: Define @tool and build Strands agent
# ==============================================================================

# Module-level KB ID (populated in main)
_kb_id: str = ""


# TODO 6a: Add @tool decorator and implement KB retrieval
def search_docs(query: str) -> str:
    """Search the technical documentation knowledge base for answers.

    Args:
        query: The question or topic to search for in the documentation.

    Steps:
        1. Create boto3 'bedrock-agent-runtime' client
        2. Call retrieve() with knowledgeBaseId=_kb_id and numberOfResults=3
        3. Join the content.text of each result and return
    """
    # TODO: Implement retrieval using bedrock-agent-runtime client
    # bedrock_runtime = _mgmt_session.client("bedrock-agent-runtime", region_name=AWS_REGION)
    # result = bedrock_runtime.retrieve(
    #     knowledgeBaseId=_kb_id,
    #     retrievalQuery={"text": query},
    #     retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 3}}
    # )
    # chunks = [r["content"]["text"] for r in result["retrievalResults"]]
    # return "\n\n---\n\n".join(chunks) if chunks else "No results found."

    return Colors.todo("TODO 6a: Implement search_docs tool")


def build_agent():
    """Build a Strands agent backed by Bedrock, with the KB search tool.

    Steps:
        1. Create BedrockModel with DEFAULT_MODEL and AWS_REGION
        2. Create Agent with model, tools=[search_docs], system_prompt
    """
    # TODO 6b: Build and return the agent
    # model = BedrockModel(model_id=DEFAULT_MODEL, region_name=AWS_REGION, max_tokens=1024)
    # return Agent(model=model, tools=[search_docs], system_prompt="...")

    print(Colors.todo("TODO 6b: Implement build_agent()"))
    return None


# ==============================================================================
# Main
# ==============================================================================

def main():
    global _kb_id

    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 09: Bedrock Knowledge Base"))
    print(Colors.header(f" Region: {AWS_REGION}  |  Run ID: {RUN_ID}"))
    print(Colors.header("=" * 70))

    try:
        print(Colors.header("\n1. Uploading documents to S3"))
        print("-" * 40)
        create_bucket_and_upload(BUCKET_NAME)

        print(Colors.header("\n2. Creating S3 Vectors store"))
        print("-" * 40)
        index_arn = create_vector_store()

        print(Colors.header("\n3. Preparing IAM role"))
        print("-" * 40)
        role_arn = get_kb_role_arn(BUCKET_NAME, index_arn)

        print(Colors.header("\n4. Creating Knowledge Base (S3_VECTORS)"))
        print("-" * 40)
        _kb_id = create_knowledge_base(role_arn, index_arn)

        print(Colors.header("\n5. Ingesting documents"))
        print("-" * 40)
        create_data_source_and_ingest(_kb_id, BUCKET_NAME)

        print(Colors.header("\n6. Querying with Strands agent"))
        print("-" * 40)
        agent = build_agent()

        if not agent:
            print(Colors.todo("\nComplete TODO 6 to enable the agent."))
            return

        questions = [
            "What are the steps to update MeshLink device firmware?",
            "How do I replace an SSL/TLS certificate on the device?",
            "What wireless standards does the AP-100 access point support?",
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
