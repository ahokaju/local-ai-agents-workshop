"""
Kata 10: AgentCore Runtime - Solution

Wrap a Strands agent with BedrockAgentCoreApp to create a production-ready
HTTP server with health checks and session isolation — then test it locally.

Prerequisites:
    pip install 'strands-agents[bedrock]' bedrock-agentcore boto3 python-dotenv
    export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
    export AWS_REGION=us-east-1   (must match the region your key was created in)

    To use eu-central-1: set AWS_REGION=eu-central-1 and change DEFAULT_MODEL
    prefix from "us." to "eu.".

Run:
    python solution.py

Test (in another terminal):
    curl -X POST http://localhost:8080/invocations \\
         -H 'Content-Type: application/json' \\
         -d '{"prompt": "What is AWS AgentCore?"}'

    curl http://localhost:8080/ping
"""

import os

from dotenv import load_dotenv
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models.bedrock import BedrockModel

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DEFAULT_MODEL = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"


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
# AgentCore Runtime App
# ==============================================================================

app = BedrockAgentCoreApp()

agent = Agent(
    model=BedrockModel(model_id=DEFAULT_MODEL, region_name=AWS_REGION, max_tokens=1024),
    system_prompt=(
        "You are a helpful assistant specializing in AWS services and cloud architecture. "
        "Provide clear, accurate, and concise answers."
    )
)


@app.entrypoint
def invoke(payload: dict) -> dict:
    """Handle agent invocation requests from AgentCore Runtime.

    AgentCore calls this function for every POST /invocations request.
    The payload is the parsed JSON body from the HTTP request.

    Args:
        payload: Dict with at least a 'prompt' key.

    Returns:
        Dict with 'response' and 'session_id' keys.
    """
    prompt = payload.get("prompt", "Hello!")
    session_id = payload.get("session_id", "local")

    print(Colors.prompt(f"[{session_id}] User: {prompt}"))
    result = agent(prompt)
    response_text = str(result)
    print(Colors.response(f"[{session_id}] Agent: {response_text[:120]}..."))

    return {
        "response": response_text,
        "session_id": session_id,
    }


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 10: AgentCore Runtime - Solution"))
    print(Colors.header(f" Region: {AWS_REGION}  |  Model: {DEFAULT_MODEL}"))
    print(Colors.header("=" * 70))

    print(Colors.stats("\nAgentCore Runtime starting on http://localhost:8080"))
    print(Colors.stats("\nTest with (in another terminal):"))
    print(Colors.stats("  curl -X POST http://localhost:8080/invocations \\"))
    print(Colors.stats("       -H 'Content-Type: application/json' \\"))
    print(Colors.stats("       -d '{\"prompt\": \"What is AWS AgentCore?\"}'"))
    print()
    print(Colors.stats("  curl http://localhost:8080/ping"))
    print()
    print(Colors.stats("  curl -X POST http://localhost:8080/invocations \\"))
    print(Colors.stats("       -H 'Content-Type: application/json' \\"))
    print(Colors.stats("       -d '{\"prompt\": \"Explain Bedrock Knowledge Bases in 2 sentences.\", \"session_id\": \"alice\"}'"))
    print()
    print(Colors.header("Starting server... (Ctrl+C to stop)"))

    app.run()
