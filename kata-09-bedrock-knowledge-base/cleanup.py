"""
Kata 09: Cleanup Script

Deletes the exact AWS resources created by solution.py / starter.py by reading
the IDs from kata09_state.json. Safe to run in a shared AWS account — only
resources from *your* run are deleted.

Resources removed:
  - Bedrock Knowledge Base + its data source
  - S3 bucket (emptied first)
  - IAM role (only if it was auto-created — skipped when KB_ROLE_ARN was set)

Run after you have finished the kata:
    python cleanup.py
"""

import json
import os
import sys

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

STATE_FILE = os.path.join(os.path.dirname(__file__), "kata09_state.json")


# ANSI colors
class Colors:
    HEADER = '\033[96m'
    OK = '\033[92m'
    WARN = '\033[93m'
    ERR = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    @classmethod
    def header(cls, t): return f"{cls.BOLD}{cls.HEADER}{t}{cls.RESET}"
    @classmethod
    def ok(cls, t):     return f"{cls.OK}{t}{cls.RESET}"
    @classmethod
    def warn(cls, t):   return f"{cls.WARN}{t}{cls.RESET}"
    @classmethod
    def err(cls, t):    return f"{cls.ERR}{t}{cls.RESET}"


# ==============================================================================
# Load state
# ==============================================================================

def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        print(Colors.err(f"State file not found: {STATE_FILE}"))
        print("Run solution.py (or starter.py) first to create AWS resources.")
        sys.exit(1)
    with open(STATE_FILE) as f:
        return json.load(f)


# ==============================================================================
# Bedrock Knowledge Base: delete data source then the KB
# ==============================================================================

def cleanup_knowledge_base(state: dict) -> None:
    kb_id = state.get("kb_id")
    ds_id = state.get("ds_id")
    region = state.get("region", os.getenv("AWS_REGION", "us-east-1"))

    if not kb_id:
        print(Colors.warn("  kb_id not in state — skipping Knowledge Base cleanup"))
        return

    bedrock_agent = boto3.client("bedrock-agent", region_name=region)

    # Delete data source first (required before KB deletion)
    if ds_id:
        try:
            bedrock_agent.delete_data_source(knowledgeBaseId=kb_id, dataSourceId=ds_id)
            print(Colors.ok(f"  Deleted data source: {ds_id}"))
        except ClientError as e:
            print(Colors.err(f"  Failed to delete data source {ds_id}: {e}"))

    try:
        bedrock_agent.delete_knowledge_base(knowledgeBaseId=kb_id)
        print(Colors.ok(f"  Deleted Knowledge Base: {kb_id}"))
    except ClientError as e:
        print(Colors.err(f"  Failed to delete Knowledge Base {kb_id}: {e}"))


# ==============================================================================
# S3: empty all objects then delete the bucket
# ==============================================================================

def cleanup_s3_bucket(state: dict) -> None:
    bucket_name = state.get("bucket_name")
    region = state.get("region", os.getenv("AWS_REGION", "us-east-1"))

    if not bucket_name:
        print(Colors.warn("  bucket_name not in state — skipping S3 cleanup"))
        return

    s3 = boto3.client("s3", region_name=region)
    print(f"  Emptying s3://{bucket_name} ...")

    try:
        # Delete versioned objects and delete markers
        paginator = s3.get_paginator("list_object_versions")
        for page in paginator.paginate(Bucket=bucket_name):
            objects = [
                {"Key": o["Key"], "VersionId": o["VersionId"]}
                for o in page.get("Versions", []) + page.get("DeleteMarkers", [])
            ]
            if objects:
                s3.delete_objects(Bucket=bucket_name, Delete={"Objects": objects})

        # Delete non-versioned objects
        paginator2 = s3.get_paginator("list_objects_v2")
        for page in paginator2.paginate(Bucket=bucket_name):
            objects = [{"Key": o["Key"]} for o in page.get("Contents", [])]
            if objects:
                s3.delete_objects(Bucket=bucket_name, Delete={"Objects": objects})

        s3.delete_bucket(Bucket=bucket_name)
        print(Colors.ok(f"  Deleted bucket: {bucket_name}"))
    except ClientError as e:
        print(Colors.err(f"  Failed to delete bucket {bucket_name}: {e}"))


# ==============================================================================
# IAM: delete inline policies then the role (only if auto-created)
# ==============================================================================

def cleanup_iam_role(state: dict) -> None:
    role_name = state.get("role_name")
    region = state.get("region", os.getenv("AWS_REGION", "us-east-1"))

    if not role_name:
        print(Colors.warn("  role_name not in state — IAM role was pre-existing, skipping"))
        return

    iam = boto3.client("iam", region_name=region)

    try:
        # Remove inline policies first
        for policy_name in iam.list_role_policies(RoleName=role_name).get("PolicyNames", []):
            iam.delete_role_policy(RoleName=role_name, PolicyName=policy_name)
            print(f"    Removed inline policy: {policy_name}")

        # Detach any managed policies
        for p in iam.list_attached_role_policies(RoleName=role_name).get("AttachedPolicies", []):
            iam.detach_role_policy(RoleName=role_name, PolicyArn=p["PolicyArn"])
            print(f"    Detached managed policy: {p['PolicyArn']}")

        iam.delete_role(RoleName=role_name)
        print(Colors.ok(f"  Deleted IAM role: {role_name}"))
    except ClientError as e:
        print(Colors.err(f"  Failed to delete IAM role {role_name}: {e}"))


# ==============================================================================
# S3 Vectors: delete index then bucket
# ==============================================================================

def cleanup_vector_store(state: dict) -> None:
    vector_bucket_name = state.get("vector_bucket_name")
    vector_index_arn = state.get("vector_index_arn")
    region = state.get("region", os.getenv("AWS_REGION", "us-east-1"))

    if not vector_bucket_name:
        print(Colors.warn("  vector_bucket_name not in state — skipping S3 Vectors cleanup"))
        return

    s3v = boto3.client("s3vectors", region_name=region)

    # Derive index name from ARN or use default
    index_name = None
    if vector_index_arn:
        index_name = vector_index_arn.split("/index/")[-1]

    if index_name:
        try:
            s3v.delete_index(vectorBucketName=vector_bucket_name, indexName=index_name)
            print(Colors.ok(f"  Deleted vector index: {index_name}"))
        except ClientError as e:
            print(Colors.err(f"  Failed to delete vector index {index_name}: {e}"))

    try:
        s3v.delete_vector_bucket(vectorBucketName=vector_bucket_name)
        print(Colors.ok(f"  Deleted vector bucket: {vector_bucket_name}"))
    except ClientError as e:
        print(Colors.err(f"  Failed to delete vector bucket {vector_bucket_name}: {e}"))


# ==============================================================================
# Main
# ==============================================================================

def main():
    print(Colors.header("=" * 60))
    print(Colors.header(" Kata 09: AWS Resource Cleanup"))
    print(Colors.header("=" * 60))

    try:
        state = load_state()
    except SystemExit:
        raise

    print(Colors.header("\nResources to delete (from kata09_state.json):"))
    for key, val in state.items():
        print(f"  {key}: {val}")
    print()

    try:
        print(Colors.header("1. Bedrock Knowledge Base + data source"))
        print("-" * 40)
        cleanup_knowledge_base(state)

        print(Colors.header("\n2. S3 bucket"))
        print("-" * 40)
        cleanup_s3_bucket(state)

        print(Colors.header("\n3. S3 Vectors store"))
        print("-" * 40)
        cleanup_vector_store(state)

        print(Colors.header("\n4. IAM role"))
        print("-" * 40)
        cleanup_iam_role(state)

    except NoCredentialsError:
        print(Colors.err("\nError: AWS credentials not configured."))
        print("Set AWS_BEARER_TOKEN_BEDROCK and AWS_REGION environment variables.")
        sys.exit(1)

    # Remove state file so a fresh run starts clean
    os.remove(STATE_FILE)
    print(Colors.ok(f"\nRemoved {os.path.basename(STATE_FILE)}"))

    print(Colors.header("\n" + "=" * 60))
    print(Colors.ok(" Cleanup complete."))
    print(Colors.header("=" * 60))


if __name__ == "__main__":
    main()
