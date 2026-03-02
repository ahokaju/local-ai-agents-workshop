"""
Kata 13: Cleanup Script

Deletes the AgentCore Gateway (and its targets) and the auto-created IAM role
by reading the IDs from kata13_state.json. Use this if solution.py crashed before
its own cleanup ran and resources are still alive in your AWS account.

Resources removed:
  - AgentCore Gateway target
  - AgentCore Gateway
  - IAM role (only if auto-created — skipped when GATEWAY_ROLE_ARN was set)
  - Secrets Manager secret (only if auto-created)

Run after you have finished the kata (or to recover from a failed run):
    python cleanup.py
"""

import json
import os
import sys
import time

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

STATE_FILE = os.path.join(os.path.dirname(__file__), "kata13_state.json")


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
        print("Run solution.py (or starter.py) first to create the gateway.")
        print("If solution.py already cleaned up successfully, there is nothing to do.")
        sys.exit(1)
    with open(STATE_FILE) as f:
        return json.load(f)


# ==============================================================================
# Delete gateway targets then the gateway
# ==============================================================================

def cleanup_gateway(state: dict) -> None:
    gateway_id = state.get("gateway_id")
    region = state.get("region", os.getenv("AWS_REGION", "us-east-1"))

    if not gateway_id:
        print(Colors.warn("  gateway_id not in state — skipping gateway cleanup"))
        return

    control_client = boto3.client("bedrock-agentcore-control", region_name=region)

    try:
        targets = control_client.list_gateway_targets(gatewayIdentifier=gateway_id)
        for target in targets.get("items", []):
            tid = target["targetId"]
            try:
                control_client.delete_gateway_target(
                    gatewayIdentifier=gateway_id,
                    targetId=tid
                )
                print(Colors.ok(f"  Deleted target: {tid}"))
            except ClientError as e:
                print(Colors.err(f"  Failed to delete target {tid}: {e}"))
        time.sleep(3)  # allow target deletion to propagate before deleting gateway
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "ResourceNotFoundException":
            print(Colors.warn(f"  Gateway not found (already deleted?): {gateway_id}"))
            return
        raise

    try:
        control_client.delete_gateway(gatewayIdentifier=gateway_id)
        print(Colors.ok(f"  Deleted gateway: {gateway_id}"))
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "ResourceNotFoundException":
            print(Colors.warn(f"  Gateway not found (already deleted?): {gateway_id}"))
        else:
            print(Colors.err(f"  Failed to delete gateway {gateway_id}: {e}"))
            raise


# ==============================================================================
# Delete auto-created Secrets Manager secret (skipped if secret_arn is None)
# ==============================================================================

def cleanup_secret(state: dict) -> None:
    secret_arn = state.get("secret_arn")
    region = state.get("region", os.getenv("AWS_REGION", "us-east-1"))

    if not secret_arn:
        print(Colors.warn("  secret_arn not in state — secret was pre-existing or not created, skipping"))
        return

    sm = boto3.client("secretsmanager", region_name=region)
    try:
        sm.delete_secret(SecretId=secret_arn, ForceDeleteWithoutRecovery=True)
        print(Colors.ok(f"  Deleted secret: {secret_arn}"))
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "ResourceNotFoundException":
            print(Colors.warn(f"  Secret not found (already deleted?): {secret_arn}"))
        else:
            print(Colors.err(f"  Failed to delete secret {secret_arn}: {e}"))


# ==============================================================================
# Delete auto-created IAM role (skipped if role_name is None)
# ==============================================================================

def cleanup_iam_role(state: dict) -> None:
    role_name = state.get("role_name")

    if not role_name:
        print(Colors.warn("  role_name not in state — IAM role was pre-existing or GATEWAY_ROLE_ARN was set, skipping"))
        return

    iam = boto3.client("iam")
    try:
        for policy_name in iam.list_role_policies(RoleName=role_name).get("PolicyNames", []):
            iam.delete_role_policy(RoleName=role_name, PolicyName=policy_name)
            print(f"    Removed inline policy: {policy_name}")

        for p in iam.list_attached_role_policies(RoleName=role_name).get("AttachedPolicies", []):
            iam.detach_role_policy(RoleName=role_name, PolicyArn=p["PolicyArn"])
            print(f"    Detached managed policy: {p['PolicyArn']}")

        iam.delete_role(RoleName=role_name)
        print(Colors.ok(f"  Deleted IAM role: {role_name}"))
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "NoSuchEntityException":
            print(Colors.warn(f"  IAM role not found (already deleted?): {role_name}"))
        else:
            print(Colors.err(f"  Failed to delete IAM role {role_name}: {e}"))


# ==============================================================================
# Main
# ==============================================================================

def main():
    print(Colors.header("=" * 60))
    print(Colors.header(" Kata 13: AWS Resource Cleanup"))
    print(Colors.header("=" * 60))

    try:
        state = load_state()
    except SystemExit:
        raise

    print(Colors.header("\nResources to delete (from kata13_state.json):"))
    for key, val in state.items():
        print(f"  {key}: {val}")
    print()

    try:
        print(Colors.header("1. AgentCore Gateway + targets"))
        print("-" * 40)
        cleanup_gateway(state)

        print(Colors.header("\n2. IAM role"))
        print("-" * 40)
        cleanup_iam_role(state)

        print(Colors.header("\n3. Secrets Manager secret"))
        print("-" * 40)
        cleanup_secret(state)

    except NoCredentialsError:
        print(Colors.err("\nError: AWS credentials not configured."))
        print("Set AWS_BEARER_TOKEN_BEDROCK and AWS_REGION environment variables.")
        sys.exit(1)

    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
        print(Colors.ok(f"\nRemoved {os.path.basename(STATE_FILE)}"))

    print(Colors.header("\n" + "=" * 60))
    print(Colors.ok(" Cleanup complete."))
    print(Colors.header("=" * 60))


if __name__ == "__main__":
    main()
