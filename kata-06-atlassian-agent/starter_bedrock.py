"""
Kata 06: Atlassian Agent - Bedrock Starter Template

Complete the TODO to build a Strands agent that integrates with Jira and
Confluence, backed by AWS Bedrock instead of the Anthropic API directly.
All Atlassian tools are identical to starter.py — only the model provider
changes in create_atlassian_agent().

Prerequisites:
    pip install 'strands-agents[bedrock]' atlassian-python-api boto3 python-dotenv

    Set these environment variables before running:
        AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
        AWS_REGION=eu-central-1   (must match the region your key was created in)
        ATLASSIAN_URL=https://your-domain.atlassian.net
        ATLASSIAN_EMAIL=your-email@example.com
        ATLASSIAN_API_TOKEN=your-api-token

    boto3 picks up AWS_BEARER_TOKEN_BEDROCK and AWS_REGION automatically.
"""

import os
import re
from dotenv import load_dotenv
from strands import Agent, tool
# TODO 1: Import BedrockModel instead of AnthropicModel
# Hint: from strands.models.bedrock import BedrockModel

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")
DEFAULT_MODEL = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"

# Atlassian configuration
ATLASSIAN_URL = os.getenv("ATLASSIAN_URL")
ATLASSIAN_EMAIL = os.getenv("ATLASSIAN_EMAIL")
ATLASSIAN_API_TOKEN = os.getenv("ATLASSIAN_API_TOKEN")

# Global clients (will be initialized in setup)
jira = None
confluence = None


def setup_atlassian_clients():
    """Initialize Jira and Confluence clients (unchanged from starter.py)."""
    global jira, confluence

    # TODO 2: Import Jira and Confluence from atlassian
    # Hint: from atlassian import Jira, Confluence

    # TODO 3: Initialize Jira client
    # Hint: jira = Jira(url=ATLASSIAN_URL, username=ATLASSIAN_EMAIL, password=ATLASSIAN_API_TOKEN, cloud=True)

    # TODO 4: Initialize Confluence client
    # Hint: confluence = Confluence(url=ATLASSIAN_URL, username=ATLASSIAN_EMAIL, password=ATLASSIAN_API_TOKEN, cloud=True)

    pass


# ==============================================================================
# Jira Tools (implement with @tool decorator — identical logic to starter.py)
# ==============================================================================

# TODO 5: Add @tool decorator and implement search_jira_issues
def search_jira_issues(jql_query: str, max_results: int = 10) -> str:
    """Search Jira issues using JQL (Jira Query Language).

    Common JQL examples:
    - 'project = PROJ AND status = Open'
    - 'assignee = currentUser() AND status != Done'
    - 'created >= -7d' (created in last 7 days)

    Args:
        jql_query: JQL query string.
        max_results: Maximum number of results to return.
    """
    # TODO: Use jira.jql(jql_query, limit=max_results)
    pass


# TODO 6: Add @tool decorator and implement get_jira_issue
def get_jira_issue(issue_key: str) -> str:
    """Get detailed information about a specific Jira issue.

    Args:
        issue_key: The issue key (e.g., 'PROJ-123').
    """
    # TODO: Use jira.get_issue(issue_key)
    pass


# TODO 7: Add @tool decorator and implement create_jira_issue
def create_jira_issue(
    project_key: str,
    summary: str,
    description: str,
    issue_type: str = "Task"
) -> str:
    """Create a new Jira issue.

    Args:
        project_key: The project key (e.g., 'PROJ').
        summary: Brief summary of the issue.
        description: Detailed description.
        issue_type: Type of issue (Task, Bug, Story, etc.).
    """
    # TODO: Use jira.create_issue(fields={...})
    pass


# ==============================================================================
# Confluence Tools (implement with @tool decorator — identical logic to starter.py)
# ==============================================================================

# TODO 8: Add @tool decorator and implement search_confluence
def search_confluence(query: str, space_key: str = None, max_results: int = 5) -> str:
    """Search Confluence for pages matching a query.

    Args:
        query: Search query text.
        space_key: Optional space key to limit search.
        max_results: Maximum number of results.
    """
    # TODO: Use confluence.cql(cql, limit=max_results)
    pass


# TODO 9: Add @tool decorator and implement get_confluence_page
def get_confluence_page(page_title: str, space_key: str) -> str:
    """Get the content of a Confluence page.

    Args:
        page_title: The title of the page.
        space_key: The space key where the page is located.
    """
    # TODO: Use confluence.get_page_by_title(space=space_key, title=page_title, expand="body.storage,version")
    pass


def create_atlassian_agent():
    """Create the Atlassian agent."""
    # TODO 10: Create BedrockModel instead of AnthropicModel
    # Hint: from strands.models.bedrock import BedrockModel
    # Hint: model = BedrockModel(model_id=DEFAULT_MODEL, region_name=AWS_REGION, max_tokens=1024)
    # Everything else (tools list, system_prompt) is identical to starter.py

    return None


def main():
    """Run the Atlassian agent demo."""
    print("=" * 70)
    print(" Kata 06: Atlassian Agent - Bedrock Starter")
    print(f" Region: {AWS_REGION}")
    print("=" * 70)

    if not all([ATLASSIAN_URL, ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN]):
        print("\nError: Missing Atlassian configuration!")
        print("Please set the following environment variables:")
        print("  - ATLASSIAN_URL")
        print("  - ATLASSIAN_EMAIL")
        print("  - ATLASSIAN_API_TOKEN")
        print("\nSee README.md for setup instructions.")
        return

    print("\n1. Setting up Atlassian clients...")
    setup_atlassian_clients()
    if jira is None or confluence is None:
        print("TODO: Implement setup_atlassian_clients()")
        return
    print("   Clients ready!")

    print("\n2. Creating Atlassian agent...")
    agent = create_atlassian_agent()
    if agent is None:
        print("TODO: Implement create_atlassian_agent() using BedrockModel")
        return
    print("   Agent ready!")

    print("\n" + "=" * 70)
    print(" Testing the Agent")
    print("=" * 70)

    test_queries = [
        "Show me the most recent issues in the PROJ project",
        "Search for documentation about deployment",
        "What's the status of PROJ-1?",
    ]

    for query in test_queries:
        print(f"\nUser: {query}")
        print("-" * 40)
        try:
            response = agent(query)
            print(f"Agent: {response}")
        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "=" * 70)
    print(" Kata 06 Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
