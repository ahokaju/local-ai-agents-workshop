"""
Kata 06: Atlassian Agent - Solution

This script creates a Strands agent that integrates with Jira and Confluence
for natural language project management and documentation access.

Prerequisites:
    pip install 'strands-agents[anthropic]' atlassian-python-api
    export ATLASSIAN_URL="https://your-domain.atlassian.net"
    export ATLASSIAN_EMAIL="your-email@example.com"
    export ATLASSIAN_API_TOKEN="your-api-token"
    export ANTHROPIC_API_KEY="your-key-here"
"""

import os
import re
from dotenv import load_dotenv
from strands import Agent, tool
from strands.models.anthropic import AnthropicModel
from atlassian import Jira, Confluence

load_dotenv()

# Atlassian configuration
ATLASSIAN_URL = os.getenv("ATLASSIAN_URL")
ATLASSIAN_EMAIL = os.getenv("ATLASSIAN_EMAIL")
ATLASSIAN_API_TOKEN = os.getenv("ATLASSIAN_API_TOKEN")

# Global clients
jira = None
confluence = None


def setup_atlassian_clients():
    """Initialize Jira and Confluence clients."""
    global jira, confluence

    jira = Jira(
        url=ATLASSIAN_URL,
        username=ATLASSIAN_EMAIL,
        password=ATLASSIAN_API_TOKEN,
        cloud=True
    )

    confluence = Confluence(
        url=ATLASSIAN_URL,
        username=ATLASSIAN_EMAIL,
        password=ATLASSIAN_API_TOKEN,
        cloud=True
    )

    return jira, confluence


# ==============================================================================
# Jira Tools
# ==============================================================================

@tool
def search_jira_issues(jql_query: str, max_results: int = 10) -> str:
    """Search Jira issues using JQL (Jira Query Language).

    Common JQL examples:
    - 'project = PROJ AND status = Open'
    - 'assignee = currentUser() AND status != Done'
    - 'created >= -7d' (created in last 7 days)
    - 'type = Bug AND priority = High'

    Args:
        jql_query: JQL query string.
        max_results: Maximum number of results to return (default: 10).
    """
    if jira is None:
        return "Error: Jira client not initialized"

    try:
        results = jira.jql(jql_query, limit=max_results)
        issues = results.get("issues", [])

        if not issues:
            return f"No issues found matching query: {jql_query}"

        output = [f"Found {len(issues)} issue(s):\n"]

        for issue in issues:
            key = issue["key"]
            fields = issue["fields"]
            summary = fields.get("summary", "No summary")
            status = fields.get("status", {}).get("name", "Unknown")
            issue_type = fields.get("issuetype", {}).get("name", "Unknown")
            priority = fields.get("priority", {}).get("name", "None")
            assignee = fields.get("assignee")
            assignee_name = assignee["displayName"] if assignee else "Unassigned"

            output.append(f"[{key}] {summary}")
            output.append(f"   Type: {issue_type} | Status: {status} | Priority: {priority}")
            output.append(f"   Assignee: {assignee_name}")
            output.append("")

        return "\n".join(output)

    except Exception as e:
        return f"Error searching Jira: {e}"


@tool
def get_jira_issue(issue_key: str) -> str:
    """Get detailed information about a specific Jira issue.

    Args:
        issue_key: The issue key (e.g., 'PROJ-123').
    """
    if jira is None:
        return "Error: Jira client not initialized"

    try:
        issue = jira.get_issue(issue_key)
        fields = issue["fields"]

        # Extract relevant fields
        details = [
            f"Issue: {issue_key}",
            f"Summary: {fields.get('summary', 'No summary')}",
            f"Type: {fields.get('issuetype', {}).get('name', 'Unknown')}",
            f"Status: {fields.get('status', {}).get('name', 'Unknown')}",
            f"Priority: {fields.get('priority', {}).get('name', 'None')}",
            f"Assignee: {fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned'}",
            f"Reporter: {fields.get('reporter', {}).get('displayName', 'Unknown') if fields.get('reporter') else 'Unknown'}",
            f"Created: {fields.get('created', 'Unknown')[:10]}",
            f"Updated: {fields.get('updated', 'Unknown')[:10]}",
        ]

        # Add labels if present
        labels = fields.get("labels", [])
        if labels:
            details.append(f"Labels: {', '.join(labels)}")

        # Add description (truncated)
        description = fields.get("description", "No description")
        if description:
            if len(description) > 500:
                description = description[:500] + "... [truncated]"
            details.append(f"\nDescription:\n{description}")

        # Add comments count
        comments = fields.get("comment", {}).get("comments", [])
        if comments:
            details.append(f"\nComments: {len(comments)}")
            # Show last comment
            last_comment = comments[-1]
            author = last_comment.get("author", {}).get("displayName", "Unknown")
            body = last_comment.get("body", "")[:200]
            details.append(f"Last comment by {author}: {body}")

        return "\n".join(details)

    except Exception as e:
        return f"Error getting issue {issue_key}: {e}"


@tool
def create_jira_issue(
    project_key: str,
    summary: str,
    description: str,
    issue_type: str = "Task"
) -> str:
    """Create a new Jira issue.

    Args:
        project_key: The project key (e.g., 'PROJ').
        summary: Brief summary of the issue (title).
        description: Detailed description of the issue.
        issue_type: Type of issue - Task, Bug, Story, Epic (default: Task).
    """
    if jira is None:
        return "Error: Jira client not initialized"

    try:
        issue_dict = {
            "project": {"key": project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type},
        }

        new_issue = jira.create_issue(fields=issue_dict)
        issue_key = new_issue["key"]

        return f"Successfully created {issue_type}: {issue_key}\nSummary: {summary}\nURL: {ATLASSIAN_URL}/browse/{issue_key}"

    except Exception as e:
        return f"Error creating issue: {e}"


@tool
def add_jira_comment(issue_key: str, comment: str) -> str:
    """Add a comment to a Jira issue.

    Args:
        issue_key: The issue key (e.g., 'PROJ-123').
        comment: The comment text to add.
    """
    if jira is None:
        return "Error: Jira client not initialized"

    try:
        jira.issue_add_comment(issue_key, comment)
        return f"Added comment to {issue_key}"
    except Exception as e:
        return f"Error adding comment: {e}"


@tool
def list_jira_projects() -> str:
    """List all accessible Jira projects."""
    if jira is None:
        return "Error: Jira client not initialized"

    try:
        projects = jira.projects()

        if not projects:
            return "No projects found"

        output = ["Available projects:\n"]
        for project in projects[:20]:  # Limit to 20
            key = project.get("key", "Unknown")
            name = project.get("name", "Unknown")
            output.append(f"  [{key}] {name}")

        if len(projects) > 20:
            output.append(f"\n  ... and {len(projects) - 20} more")

        return "\n".join(output)

    except Exception as e:
        return f"Error listing projects: {e}"


# ==============================================================================
# Confluence Tools
# ==============================================================================

@tool
def search_confluence(query: str, space_key: str = None, max_results: int = 5) -> str:
    """Search Confluence for pages matching a query.

    Args:
        query: Search query text.
        space_key: Optional space key to limit search (e.g., 'ENG', 'DOC').
        max_results: Maximum number of results (default: 5).
    """
    if confluence is None:
        return "Error: Confluence client not initialized"

    try:
        # Build CQL query
        cql = f'text ~ "{query}"'
        if space_key:
            cql += f' AND space = "{space_key}"'

        results = confluence.cql(cql, limit=max_results)
        pages = results.get("results", [])

        if not pages:
            return f"No pages found matching: {query}"

        output = [f"Found {len(pages)} page(s):\n"]

        for page in pages:
            title = page.get("title", "Unknown")
            content = page.get("content", {})
            space_info = page.get("resultGlobalContainer", {})
            space_title = space_info.get("title", "Unknown space")

            # Build URL
            page_url = page.get("url", "")
            if page_url:
                full_url = f"{ATLASSIAN_URL}/wiki{page_url}"
            else:
                full_url = "URL not available"

            output.append(f"- {title}")
            output.append(f"  Space: {space_title}")
            output.append(f"  URL: {full_url}")
            output.append("")

        return "\n".join(output)

    except Exception as e:
        return f"Error searching Confluence: {e}"


@tool
def get_confluence_page(page_title: str, space_key: str) -> str:
    """Get the content of a Confluence page.

    Args:
        page_title: The exact title of the page.
        space_key: The space key where the page is located.
    """
    if confluence is None:
        return "Error: Confluence client not initialized"

    try:
        page = confluence.get_page_by_title(
            space=space_key,
            title=page_title,
            expand="body.storage,version"
        )

        if not page:
            return f"Page '{page_title}' not found in space '{space_key}'"

        # Extract content
        body = page.get("body", {}).get("storage", {}).get("value", "")

        # Strip HTML tags for readability
        text = re.sub(r'<[^>]+>', ' ', body)
        text = re.sub(r'\s+', ' ', text).strip()

        # Truncate if too long
        if len(text) > 3000:
            text = text[:3000] + "\n\n... [content truncated, page is longer]"

        version = page.get("version", {}).get("number", "Unknown")

        output = [
            f"Page: {page_title}",
            f"Space: {space_key}",
            f"Version: {version}",
            f"URL: {ATLASSIAN_URL}/wiki/spaces/{space_key}/pages/{page.get('id', '')}",
            f"\n--- Content ---\n",
            text
        ]

        return "\n".join(output)

    except Exception as e:
        return f"Error getting page: {e}"


@tool
def list_confluence_spaces() -> str:
    """List all accessible Confluence spaces."""
    if confluence is None:
        return "Error: Confluence client not initialized"

    try:
        spaces = confluence.get_all_spaces(limit=25)
        results = spaces.get("results", [])

        if not results:
            return "No spaces found"

        output = ["Available spaces:\n"]
        for space in results:
            key = space.get("key", "Unknown")
            name = space.get("name", "Unknown")
            space_type = space.get("type", "Unknown")
            output.append(f"  [{key}] {name} ({space_type})")

        return "\n".join(output)

    except Exception as e:
        return f"Error listing spaces: {e}"


# ==============================================================================
# Agent Creation
# ==============================================================================

def create_atlassian_agent():
    """Create the Atlassian agent with Jira and Confluence tools."""
    model = AnthropicModel(
        model_id="claude-haiku-4-5-20251001",
        max_tokens=1024
    )

    agent = Agent(
        model=model,
        tools=[
            # Jira tools
            search_jira_issues,
            get_jira_issue,
            create_jira_issue,
            add_jira_comment,
            list_jira_projects,
            # Confluence tools
            search_confluence,
            get_confluence_page,
            list_confluence_spaces,
        ],
        system_prompt="""You are an Atlassian assistant that helps with Jira and Confluence.

JIRA CAPABILITIES:
- Search issues using JQL (Jira Query Language)
- Get detailed information about specific issues
- Create new issues (Tasks, Bugs, Stories)
- Add comments to issues
- List available projects

CONFLUENCE CAPABILITIES:
- Search for documentation and pages
- Get page content
- List available spaces

JQL TIPS:
- 'project = KEY' - filter by project
- 'status = Open' - filter by status
- 'assignee = currentUser()' - your issues
- 'created >= -7d' - last 7 days
- 'type = Bug' - filter by type
- Combine with AND/OR

When creating issues:
- Ask for the project key if not provided
- Use clear, concise summaries
- Include relevant details in description
- Suggest appropriate issue type

Be helpful, efficient, and always confirm before creating or modifying data."""
    )

    return agent


# ==============================================================================
# Main Demo
# ==============================================================================

def main():
    """Run the Atlassian agent demo."""
    print("=" * 70)
    print(" Kata 06: Atlassian Agent - Solution")
    print("=" * 70)

    # Check configuration
    if not all([ATLASSIAN_URL, ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN]):
        print("\nError: Missing Atlassian configuration!")
        print("Please set the following environment variables:")
        print("  - ATLASSIAN_URL (e.g., https://your-domain.atlassian.net)")
        print("  - ATLASSIAN_EMAIL (your Atlassian account email)")
        print("  - ATLASSIAN_API_TOKEN (from id.atlassian.com)")
        print("\nSee README.md for detailed setup instructions.")
        return

    # Setup clients
    print("\n1. Setting up Atlassian clients...")
    try:
        setup_atlassian_clients()
        print(f"   Connected to: {ATLASSIAN_URL}")
    except Exception as e:
        print(f"   Error connecting: {e}")
        return

    # Create agent
    print("\n2. Creating Atlassian agent...")
    agent = create_atlassian_agent()
    print("   Agent ready!")

    # Test queries
    print("\n" + "=" * 70)
    print(" Testing the Agent")
    print("=" * 70)

    # These queries should work with any Atlassian instance
    test_queries = [
        "List all available Jira projects",
        "List all Confluence spaces",
        "Show me the 5 most recently updated issues",
        "Search Confluence for 'getting started'",
    ]

    for query in test_queries:
        print(f"\nUser: {query}")
        print("-" * 40)
        try:
            response = agent(query)
            print(f"Agent: {response}")
        except Exception as e:
            print(f"Error: {e}")

    # Interactive mode
    print("\n" + "=" * 70)
    print(" Interactive Mode (type 'quit' to exit)")
    print("=" * 70)
    print("\nTry queries like:")
    print("  - 'Show me open bugs in PROJECT'")
    print("  - 'Create a task in PROJECT to fix the login issue'")
    print("  - 'Find documentation about API'")
    print("  - 'What's the status of PROJECT-123?'")

    while True:
        try:
            query = input("\nYour query: ").strip()
            if query.lower() in ["quit", "exit", "q"]:
                break
            if not query:
                continue

            response = agent(query)
            print(f"\nAgent: {response}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "=" * 70)
    print(" Kata 06 Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
