"""
Kata 08: Strands GitHub PR Agent - Bedrock Starter Template

Complete the TODO to build a GitHub PR agent backed by AWS Bedrock instead of
the Anthropic API directly.  All GitHub tools are imported from github_tools.py
(unchanged) — only the model provider changes in create_github_pr_agent().

Prerequisites:
    pip install 'strands-agents[bedrock]' PyGithub boto3 python-dotenv

    Set these environment variables before running:
        AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
        AWS_REGION=eu-central-1   (must match the region your key was created in)
        GITHUB_TOKEN=your-github-token

    boto3 picks up AWS_BEARER_TOKEN_BEDROCK and AWS_REGION automatically.

Usage:
    python starter_bedrock.py              # Run interactive demo (once TODOs are done)
    python solution_bedrock.py --mock      # Run with mock tools (no GitHub API)
"""

import os
from dotenv import load_dotenv
from strands import Agent, tool
# TODO 1: Import BedrockModel instead of AnthropicModel
# Hint: from strands.models.bedrock import BedrockModel

from github_tools import (
    github_create_branch,
    github_commit_file,
    github_create_pr,
    github_list_prs,
    github_get_pr,
    github_get_file,
)

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")
DEFAULT_MODEL = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def create_github_pr_agent(
    model_id: str = DEFAULT_MODEL,
    max_tokens: int = 2048
):
    """Create a GitHub PR agent backed by AWS Bedrock.

    TODO 2: Implement this function
    - Create a BedrockModel with model_id, region_name=AWS_REGION, and max_tokens
    - Create an Agent with:
      - The model
      - All GitHub tools imported from github_tools.py
      - A system prompt describing the OSS Risk Mitigation purpose

    Hint: from strands.models.bedrock import BedrockModel
    Hint: model = BedrockModel(model_id=model_id, region_name=AWS_REGION, max_tokens=max_tokens)
    Hint: The system prompt should explain branch naming conventions (rmp/update-<component>-<date>)
    Key difference from starter.py: BedrockModel replaces AnthropicModel
    """
    pass


def main():
    """Run a demo of the GitHub PR agent."""
    print("=" * 60)
    print(" Kata 08: GitHub PR Agent - Bedrock Starter")
    print(f" Region: {AWS_REGION}")
    print("=" * 60)

    if not GITHUB_TOKEN:
        print("\nWarning: GITHUB_TOKEN not set.")
        print("Set it to use real GitHub API, or run solution_bedrock.py --mock")
        return

    # TODO 3: Create the agent and test it
    # agent = create_github_pr_agent()
    # if agent is None:
    #     print("TODO: Implement create_github_pr_agent()")
    #     return
    #
    # response = agent("List open PRs in owner/repo")
    # print(f"Agent: {response}")

    print("\nImplement the TODOs and run again!")


if __name__ == "__main__":
    main()
