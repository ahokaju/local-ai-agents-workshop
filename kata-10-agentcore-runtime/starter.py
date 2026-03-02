"""
Kata 10: AgentCore Runtime - Starter Template

Complete the TODOs to wrap a Strands agent in BedrockAgentCoreApp and serve it
as a production-ready HTTP API with health checks and session isolation.

Prerequisites:
    pip install 'strands-agents[bedrock]' bedrock-agentcore boto3 python-dotenv
    export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
    export AWS_REGION=us-east-1   (must match the region your key was created in)

Run:
    python starter.py

Test (in another terminal):
    curl -X POST http://localhost:8080/invocations \\
         -H 'Content-Type: application/json' \\
         -d '{"prompt": "What is AWS AgentCore?"}'

    curl http://localhost:8080/ping
"""

import os

from dotenv import load_dotenv
# TODO 1: Import BedrockAgentCoreApp from bedrock_agentcore.runtime
# from bedrock_agentcore.runtime import BedrockAgentCoreApp
# TODO 1 (cont): Import Agent from strands and BedrockModel from strands.models.bedrock
# from strands import Agent
# from strands.models.bedrock import BedrockModel

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
# TODO 2: Create the BedrockAgentCoreApp instance and configure the agent
# ==============================================================================

# TODO 2a: Create app instance
# app = BedrockAgentCoreApp()

# TODO 2b: Create a BedrockModel with DEFAULT_MODEL and AWS_REGION

# TODO 2c: Create an Agent with the model and a helpful system prompt


# ==============================================================================
# TODO 3: Write the invoke handler and register it with @app.entrypoint
# ==============================================================================

# TODO 3: Define the invoke function with @app.entrypoint decorator
# The function receives a payload dict and should return a dict with 'response' and 'session_id'.
#
# @app.entrypoint
# def invoke(payload: dict) -> dict:
#     """Handle agent invocation requests from AgentCore Runtime.
#
#     Args:
#         payload: Dict with at least a 'prompt' key.
#
#     Returns:
#         Dict with 'response' and 'session_id' keys.
#     """
#     prompt = payload.get("prompt", "Hello!")
#     session_id = payload.get("session_id", "local")
#     result = agent(prompt)
#     return {"response": str(result), "session_id": session_id}


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 10: AgentCore Runtime"))
    print(Colors.header(f" Region: {AWS_REGION}  |  Model: {DEFAULT_MODEL}"))
    print(Colors.header("=" * 70))

    print(Colors.stats("\nTest with (in another terminal):"))
    print(Colors.stats("  curl -X POST http://localhost:8080/invocations \\"))
    print(Colors.stats("       -H 'Content-Type: application/json' \\"))
    print(Colors.stats("       -d '{\"prompt\": \"What is AWS AgentCore?\"}'"))
    print()
    print(Colors.stats("  curl http://localhost:8080/ping"))
    print()

    # TODO 4: Start the app with app.run()
    print(Colors.todo("TODO 4: Call app.run() to start the HTTP server"))
    print(Colors.todo("        (Ctrl+C to stop)"))
