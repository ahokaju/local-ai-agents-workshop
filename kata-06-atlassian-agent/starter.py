"""
Kata 06: Atlassian Agent - Starter Template

Build a Strands agent that integrates with Jira and Confluence.

Prerequisites:
    pip install 'strands-agents[anthropic]' atlassian-python-api
    export ATLASSIAN_URL="https://your-domain.atlassian.net"
    export ATLASSIAN_EMAIL="your-email@example.com"
    export ATLASSIAN_API_TOKEN="your-api-token"
    export ANTHROPIC_API_KEY="your-key-here"
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Atlassian configuration
ATLASSIAN_URL = os.getenv("ATLASSIAN_URL")
ATLASSIAN_EMAIL = os.getenv("ATLASSIAN_EMAIL")
ATLASSIAN_API_TOKEN = os.getenv("ATLASSIAN_API_TOKEN")

# Global clients (will be initialized in setup)
jira = None
confluence = None


def setup_atlassian_clients():
    """Initialize Jira and Confluence clients."""
    global jira, confluence

    # TODO 1: Import Jira and Confluence from atlassian
    # Hint: from atlassian import Jira, Confluence

    # TODO 2: Initialize Jira client
    # Hint: jira = Jira(url=..., username=..., password=..., cloud=True)

    # TODO 3: Initialize Confluence client
    # Hint: confluence = Confluence(url=..., username=..., password=..., cloud=True)

    pass


# TODO 4: Create search_jira_issues tool
# Hint: Use the @tool decorator
def search_jira_issues(jql_query: str, max_results: int = 10) -> str:
    """Search Jira issues using JQL (Jira Query Language).

    Args:
        jql_query: JQL query string.
        max_results: Maximum number of results to return.
    """
    # TODO: Implement using jira.jql(jql_query, limit=max_results)
    pass


# TODO 5: Create get_jira_issue tool
def get_jira_issue(issue_key: str) -> str:
    """Get details of a specific Jira issue.

    Args:
        issue_key: The issue key (e.g., 'PROJ-123').
    """
    # TODO: Implement using jira.get_issue(issue_key)
    pass


# TODO 6: Create create_jira_issue tool
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
    # TODO: Implement using jira.create_issue(fields={...})
    pass


# TODO 7: Create search_confluence tool
def search_confluence(query: str, space_key: str = None, max_results: int = 5) -> str:
    """Search Confluence for pages matching a query.

    Args:
        query: Search query text.
        space_key: Optional space key to limit search.
        max_results: Maximum number of results.
    """
    # TODO: Implement using confluence.cql(cql, limit=max_results)
    pass


# TODO 8: Create get_confluence_page tool
def get_confluence_page(page_title: str, space_key: str) -> str:
    """Get the content of a Confluence page.

    Args:
        page_title: The title of the page.
        space_key: The space key where the page is located.
    """
    # TODO: Implement using confluence.get_page_by_title(...)
    pass


def create_atlassian_agent():
    """Create the Atlassian agent."""
    # TODO 9: Import Agent and AnthropicModel
    # TODO 10: Create agent with all Atlassian tools

    return None


def main():
    """Run the Atlassian agent demo."""
    print("=" * 70)
    print(" Kata 06: Atlassian Agent (Jira/Confluence)")
    print("=" * 70)

    # Check configuration
    if not all([ATLASSIAN_URL, ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN]):
        print("\nError: Missing Atlassian configuration!")
        print("Please set the following environment variables:")
        print("  - ATLASSIAN_URL")
        print("  - ATLASSIAN_EMAIL")
        print("  - ATLASSIAN_API_TOKEN")
        print("\nSee README.md for setup instructions.")
        return

    # Setup clients
    print("\n1. Setting up Atlassian clients...")
    setup_atlassian_clients()
    if jira is None or confluence is None:
        print("TODO: Implement setup_atlassian_clients()")
        return
    print("   Clients ready!")

    # Create agent
    print("\n2. Creating Atlassian agent...")
    agent = create_atlassian_agent()
    if agent is None:
        print("TODO: Implement create_atlassian_agent()")
        return
    print("   Agent ready!")

    # Test queries
    print("\n" + "=" * 70)
    print(" Testing the Agent")
    print("=" * 70)

    # Note: Replace these with queries relevant to your Atlassian instance
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
