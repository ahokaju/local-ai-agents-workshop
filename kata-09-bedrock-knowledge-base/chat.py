"""
Kata 09: Interactive KB Chat

Connects to the Knowledge Base created by solution.py and starts an
interactive conversation with a Strands agent that retrieves from it.

Usage:
    python chat.py

Reads kata09_state.json to find the KB ID — run solution.py first.
"""

import os
import json
import sys

# Capture management session BEFORE strands patches boto3
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
_mgmt_session = boto3.Session()

from strands import Agent, tool  # noqa: E402
from strands.models.bedrock import BedrockModel  # noqa: E402

DEFAULT_MODEL = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
STATE_FILE = os.path.join(os.path.dirname(__file__), "kata09_state.json")


class Colors:
    HEADER  = '\033[96m'
    USER    = '\033[93m'
    AGENT   = '\033[92m'
    TOOL    = '\033[95m'
    ERROR   = '\033[91m'
    DIM     = '\033[2m'
    BOLD    = '\033[1m'
    RESET   = '\033[0m'


def load_kb_id() -> str:
    if not os.path.exists(STATE_FILE):
        print(f"{Colors.ERROR}Error: {STATE_FILE} not found.{Colors.RESET}")
        print("Run  python solution.py  first to create the Knowledge Base.")
        sys.exit(1)
    with open(STATE_FILE) as f:
        state = json.load(f)
    kb_id = state.get("kb_id")
    if not kb_id:
        print(f"{Colors.ERROR}Error: kb_id not found in state file.{Colors.RESET}")
        sys.exit(1)
    return kb_id


_kb_id: str = ""


@tool
def search_vaisala_docs(query: str) -> str:
    """Search the Vaisala technical documentation knowledge base for answers.

    Args:
        query: The question or topic to search for in the documentation.
    """
    bedrock_runtime = _mgmt_session.client("bedrock-agent-runtime", region_name=AWS_REGION)
    result = bedrock_runtime.retrieve(
        knowledgeBaseId=_kb_id,
        retrievalQuery={"text": query},
        retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 5}},
    )
    chunks = [r["content"]["text"] for r in result["retrievalResults"]]
    if not chunks:
        return "No relevant documentation found."
    return "\n\n---\n\n".join(chunks)


def build_agent() -> Agent:
    model = BedrockModel(model_id=DEFAULT_MODEL, region_name=AWS_REGION, max_tokens=2048)
    return Agent(
        model=model,
        tools=[search_vaisala_docs],
        system_prompt=(
            "You are a helpful technical support assistant for Vaisala products. "
            "Always search the documentation before answering questions. "
            "Be concise but complete. If the documentation doesn't contain the answer, "
            "say so clearly."
        ),
    )


def print_banner(kb_id: str) -> None:
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.HEADER} Vaisala KB Chat{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.HEADER} KB: {kb_id}  |  Region: {AWS_REGION}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.DIM} Type your question and press Enter.{Colors.RESET}")
    print(f"{Colors.DIM} Commands: /quit  /clear  /help{Colors.RESET}\n")


def print_help() -> None:
    print(f"{Colors.DIM}Commands:")
    print(f"  /quit  — exit the chat")
    print(f"  /clear — start a fresh conversation (clears history)")
    print(f"  /help  — show this message{Colors.RESET}\n")


def main() -> None:
    global _kb_id
    _kb_id = load_kb_id()
    print_banner(_kb_id)

    agent = build_agent()
    turn = 0

    while True:
        try:
            user_input = input(f"{Colors.USER}You: {Colors.RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{Colors.DIM}Goodbye!{Colors.RESET}")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/quit", "/exit", "quit", "exit"):
            print(f"{Colors.DIM}Goodbye!{Colors.RESET}")
            break

        if user_input.lower() == "/clear":
            agent = build_agent()
            turn = 0
            print(f"{Colors.DIM}Conversation cleared.\n{Colors.RESET}")
            continue

        if user_input.lower() == "/help":
            print_help()
            continue

        turn += 1
        try:
            response = agent(user_input)
            print(f"\n{Colors.AGENT}Agent: {response}{Colors.RESET}\n")
        except NoCredentialsError:
            print(f"{Colors.ERROR}Error: AWS credentials not configured.{Colors.RESET}\n")
        except ClientError as e:
            print(f"{Colors.ERROR}AWS error: {e}{Colors.RESET}\n")


if __name__ == "__main__":
    main()
