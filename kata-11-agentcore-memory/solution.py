"""
Kata 11: AgentCore Memory - Solution

Give agents persistent long-term memory using AgentCore Memory.
Short-term memory holds recent turns; long-term memory extracts and indexes
facts that survive across sessions.

Prerequisites:
    pip install bedrock-agentcore bedrock-agentcore-starter-toolkit boto3 python-dotenv
    export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
    export AWS_REGION=us-east-1   (must match the region your key was created in)

    To use eu-central-1: set AWS_REGION=eu-central-1.
"""

import json
import os
import time

from dotenv import load_dotenv
from botocore.exceptions import ClientError, NoCredentialsError
from bedrock_agentcore_starter_toolkit.operations.memory.manager import MemoryManager
from bedrock_agentcore_starter_toolkit.operations.memory.models.strategies import SemanticStrategy
from bedrock_agentcore.memory.session import MemorySessionManager
from bedrock_agentcore.memory.constants import ConversationalMessage, MessageRole

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


# ==============================================================================
# Step 1: Create (or reuse) Memory Store
# ==============================================================================

def provision_memory(memory_manager: MemoryManager) -> dict:
    """Create a memory store with semantic strategy, or reuse an existing one."""
    print(Colors.stats(f"Provisioning memory store: '{MEMORY_NAME}'"))

    memory = memory_manager.get_or_create_memory(
        name=MEMORY_NAME,
        description=MEMORY_DESCRIPTION,
        strategies=[
            SemanticStrategy(
                name="semanticMemory",
                # Namespace template — {memoryStrategyId} and {actorId} are substituted at runtime
                namespaces=["/strategies/{memoryStrategyId}/actors/{actorId}/"]
            )
        ]
    )
    memory_id = memory["id"]
    print(Colors.stats(f"Memory ID: {memory_id}"))

    # Poll until ACTIVE
    print(Colors.stats("Waiting for memory store to become ACTIVE "), end="")
    while True:
        status = memory_manager.get_memory(memory_id)["status"]
        print(Colors.stats(f"[{status}]"), end=" ", flush=True)
        if status == "ACTIVE":
            break
        if status in ("FAILED", "DELETING"):
            raise RuntimeError(f"Memory store entered status: {status}")
        time.sleep(5)
    print()
    print(Colors.stats("Memory store is ACTIVE."))
    return memory


# ==============================================================================
# Step 2: Session 1 — Store conversation turns
# ==============================================================================

def run_session_one(memory_id: str) -> None:
    """Simulate the first session with the user. Stores conversation turns."""
    print(Colors.header("\n--- Session 1: Introduction ---"))

    session_mgr = MemorySessionManager(memory_id=memory_id, region_name=AWS_REGION)
    session = session_mgr.create_memory_session(
        actor_id=ACTOR_ID,
        session_id="session-001"
    )

    turns = [
        (MessageRole.USER,      "Hi! My name is Alice and I'm a cloud architect at Vaisala."),
        (MessageRole.ASSISTANT, "Hello Alice! Great to meet you. How can I help with your cloud work?"),
        (MessageRole.USER,      "I'm building a real-time data pipeline for IoT sensor data on AWS."),
        (MessageRole.ASSISTANT, "That sounds like a great project! AWS IoT Core, Kinesis, and Lambda work well together for that."),
        (MessageRole.USER,      "I prefer Python and I'm using CDK for infrastructure as code."),
        (MessageRole.ASSISTANT, "Python + CDK is a great combination. The constructs library makes IoT pipelines clean to define."),
    ]

    messages = [ConversationalMessage(text, role) for role, text in
                [(r, t) for t, r in [(t, r) for r, t in turns]]]

    # Reformat: turns is list of (role, text)
    messages = [ConversationalMessage(text, role) for role, text in turns]
    session.add_turns(messages=messages)

    print(Colors.stats(f"Stored {len(turns)} conversation turns in session-001."))
    for role, text in turns:
        label = "User" if role == MessageRole.USER else "Agent"
        print(f"  {Colors.prompt(label)}: {text}")

    # AgentCore extracts long-term memories asynchronously — allow time
    print(Colors.stats("\nWaiting for long-term memory extraction (30 s)..."))
    time.sleep(30)


# ==============================================================================
# Step 3: Session 2 — Retrieve memories from previous session
# ==============================================================================

def run_session_two(memory_id: str) -> None:
    """Simulate a second session. Retrieves facts extracted from session 1."""
    print(Colors.header("\n--- Session 2: Recall from memory ---"))

    session_mgr = MemorySessionManager(memory_id=memory_id, region_name=AWS_REGION)
    session = session_mgr.create_memory_session(
        actor_id=ACTOR_ID,
        session_id="session-002"
    )

    queries = [
        "Who is this user and what is their job role?",
        "What AWS project is the user working on?",
        "What programming language and IaC tool does the user prefer?",
    ]

    for query in queries:
        print(Colors.prompt(f"\nQuery: {query}"))
        results = session.search_long_term_memories(
            query=query,
            namespace_prefix="/",
            top_k=3
        )

        if not results:
            print(Colors.stats("  (no memories found yet — try running again after a short delay)"))
        else:
            for i, r in enumerate(results, 1):
                score = r.get("score", "n/a")
                text = r.get("content", {}).get("text", str(r))
                print(Colors.response(f"  [{i}] (score={score:.3f}) {text}"))


# ==============================================================================
# Main
# ==============================================================================

def main():
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 11: AgentCore Memory - Solution"))
    print(Colors.header(f" Region: {AWS_REGION}"))
    print(Colors.header("=" * 70))

    try:
        # Step 1: Provision memory
        print(Colors.header("\n1. Provisioning memory store"))
        print("-" * 40)
        memory_manager = MemoryManager(region_name=AWS_REGION)
        memory = provision_memory(memory_manager)
        memory_id = memory["id"]

        # Persist memory ID so cleanup.py can delete it later
        state = {"memory_id": memory_id, "memory_name": MEMORY_NAME, "region": AWS_REGION}
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
        print(Colors.stats(f"State saved to {os.path.basename(STATE_FILE)}"))

        # Step 2: Session 1 — introduce user
        print(Colors.header("\n2. Simulating Session 1 (storing turns)"))
        print("-" * 40)
        run_session_one(memory_id)

        # Step 3: Session 2 — recall
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
    print(Colors.stats("\nTip: Run the script again — session-002 will find richer memories"))
    print(Colors.stats("     because the extraction from session-001 has had more time."))


if __name__ == "__main__":
    main()
