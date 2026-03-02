"""
Kata 11: AgentCore Memory - Starter Template

Complete the TODOs to give agents persistent long-term memory.
Short-term memory holds recent turns; long-term memory extracts and indexes
facts that survive across sessions using semantic search.

Prerequisites:
    pip install bedrock-agentcore bedrock-agentcore-starter-toolkit boto3 python-dotenv
    export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
    export AWS_REGION=us-east-1   (must match the region your key was created in)
"""

import json
import os
import time

from dotenv import load_dotenv
from botocore.exceptions import ClientError, NoCredentialsError
# TODO 1: Import memory classes
# from bedrock_agentcore_starter_toolkit.operations.memory.manager import MemoryManager
# from bedrock_agentcore_starter_toolkit.operations.memory.models.strategies import SemanticStrategy
# from bedrock_agentcore.memory.session import MemorySessionManager
# from bedrock_agentcore.memory.constants import ConversationalMessage, MessageRole

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
MEMORY_NAME = "kata11_workshop_memory"
MEMORY_DESCRIPTION = "Demo long-term memory for kata-11 workshop"
ACTOR_ID = "alice"
STATE_FILE = os.path.join(os.path.dirname(__file__), "kata11_state.json")


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


# ==============================================================================
# TODO 2: Create (or reuse) Memory Store and wait for ACTIVE status
# ==============================================================================

def provision_memory(memory_manager) -> dict:
    """Create a memory store with SemanticStrategy, or reuse an existing one.

    Steps:
        1. Call memory_manager.get_or_create_memory() with name, description,
           and strategies=[SemanticStrategy(...)]
        2. Poll memory_manager.get_memory(memory_id)["status"] until "ACTIVE"
        3. Return the memory dict
    """
    # TODO 2: Implement memory provisioning
    # memory = memory_manager.get_or_create_memory(
    #     name=MEMORY_NAME,
    #     description=MEMORY_DESCRIPTION,
    #     strategies=[
    #         SemanticStrategy(
    #             name="semanticMemory",
    #             namespaces=["/strategies/{memoryStrategyId}/actors/{actorId}/"]
    #         )
    #     ]
    # )
    # memory_id = memory["id"]
    # while memory_manager.get_memory(memory_id)["status"] != "ACTIVE":
    #     time.sleep(5)
    # return memory

    print(Colors.todo("TODO 2: Implement provision_memory()"))
    return {"id": "TODO-memory-id"}


# ==============================================================================
# TODO 3: Session 1 — Store 4+ conversation turns introducing the user
# ==============================================================================

def run_session_one(memory_id: str) -> None:
    """Simulate the first session. Stores conversation turns for long-term extraction.

    Steps:
        1. Create MemorySessionManager(memory_id=memory_id, region_name=AWS_REGION)
        2. Call create_memory_session(actor_id=ACTOR_ID, session_id="session-001")
        3. Build a list of ConversationalMessage objects (at least 4 turns)
           that introduce: user name, job role, project, tech preferences
        4. Call session.add_turns(messages=[...])
        5. Sleep 30 s to allow async long-term memory extraction
    """
    print(Colors.todo("TODO 3: Implement run_session_one()"))
    print(Colors.stats("  Add 4+ conversation turns that introduce the user (name, role, project, preferences)"))


# ==============================================================================
# TODO 4: Session 2 — Retrieve memories from session 1 using semantic search
# ==============================================================================

def run_session_two(memory_id: str) -> None:
    """Simulate a second session. Retrieves facts extracted from session 1.

    Steps:
        1. Create MemorySessionManager and create_memory_session("session-002")
        2. Call session.search_long_term_memories(
               query="...", namespace_prefix="/", top_k=3)
        3. Print the retrieved memories (content.text and score)
    """
    print(Colors.todo("TODO 4: Implement run_session_two()"))
    print(Colors.stats("  Use semantic search to recall facts from session-001"))


# ==============================================================================
# Main
# ==============================================================================

def main():
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 11: AgentCore Memory"))
    print(Colors.header(f" Region: {AWS_REGION}"))
    print(Colors.header("=" * 70))

    try:
        print(Colors.header("\n1. Provisioning memory store"))
        print("-" * 40)
        # TODO 5: Create MemoryManager and call provision_memory()
        # memory_manager = MemoryManager(region_name=AWS_REGION)
        # memory = provision_memory(memory_manager)
        # memory_id = memory["id"]
        # Save state so cleanup.py can delete the memory later:
        # state = {"memory_id": memory_id, "memory_name": MEMORY_NAME, "region": AWS_REGION}
        # with open(STATE_FILE, "w") as f:
        #     json.dump(state, f, indent=2)
        memory_id = "TODO-memory-id"
        print(Colors.todo("TODO 5: Instantiate MemoryManager, provision memory, and save state to kata11_state.json"))

        print(Colors.header("\n2. Simulating Session 1 (storing turns)"))
        print("-" * 40)
        run_session_one(memory_id)

        print(Colors.header("\n3. Simulating Session 2 (semantic recall)"))
        print("-" * 40)
        run_session_two(memory_id)

    except NoCredentialsError:
        print("\nError: AWS credentials not configured.")
        print("Set AWS_BEARER_TOKEN_BEDROCK and AWS_REGION environment variables.")
    except ClientError as e:
        print(f"\nAWS error: {e}")
        raise

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 11 Complete!"))
    print(Colors.header("=" * 70))


if __name__ == "__main__":
    main()
