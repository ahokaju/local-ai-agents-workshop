"""
Kata 12: Cleanup Script

Deletes the AgentCore Memory store created by solution.py / starter.py by reading
the memory ID from kata12_state.json. Safe to run in a shared AWS account — only
the memory from *your* run is deleted.

Resources removed:
  - AgentCore Memory store (identified by memory_id in kata12_state.json)

Run after you have finished the kata:
    python cleanup.py
"""

import json
import os
import sys

from dotenv import load_dotenv
from botocore.exceptions import ClientError, NoCredentialsError
from bedrock_agentcore_starter_toolkit.operations.memory.manager import MemoryManager

load_dotenv()

STATE_FILE = os.path.join(os.path.dirname(__file__), "kata12_state.json")


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
        print("Run solution.py (or starter.py) first to create the memory store.")
        sys.exit(1)
    with open(STATE_FILE) as f:
        return json.load(f)


# ==============================================================================
# Delete AgentCore Memory store
# ==============================================================================

def cleanup_memory(state: dict) -> None:
    memory_id = state.get("memory_id")
    region = state.get("region", os.getenv("AWS_REGION", "us-east-1"))

    if not memory_id:
        print(Colors.warn("  memory_id not in state — skipping memory cleanup"))
        return

    memory_manager = MemoryManager(region_name=region)

    try:
        memory_manager.delete_memory(memory_id)
        print(Colors.ok(f"  Deleted memory store: {memory_id}"))
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "ResourceNotFoundException":
            print(Colors.warn(f"  Memory store not found (already deleted?): {memory_id}"))
        else:
            print(Colors.err(f"  Failed to delete memory store {memory_id}: {e}"))
            raise


# ==============================================================================
# Main
# ==============================================================================

def main():
    print(Colors.header("=" * 60))
    print(Colors.header(" Kata 12: AWS Resource Cleanup"))
    print(Colors.header("=" * 60))

    try:
        state = load_state()
    except SystemExit:
        raise

    print(Colors.header("\nResources to delete (from kata12_state.json):"))
    for key, val in state.items():
        print(f"  {key}: {val}")
    print()

    try:
        print(Colors.header("1. AgentCore Memory store"))
        print("-" * 40)
        cleanup_memory(state)

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
