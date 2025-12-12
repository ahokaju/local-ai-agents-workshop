# Kata 06: Atlassian Agent (Jira/Confluence)

## Objective

Build a Strands agent that integrates with Atlassian Jira and Confluence, enabling natural language interaction with project management and documentation systems.

## Learning Goals

- Set up Atlassian API authentication
- Use the `atlassian-python-api` library
- Create Strands tools for Jira operations
- Create Strands tools for Confluence operations
- Build a practical agent for team productivity

## Prerequisites

- Completed Kata 03 (Strands Tools)
- Atlassian Cloud account (free tier works)
- Atlassian API token
- Python 3.12

## Time Estimate

35-45 minutes

## Difficulty

⭐⭐ (Intermediate)

---

## Background

### Why Atlassian Integration?

Jira and Confluence are widely used in software development:
- **Jira**: Issue tracking, project management, sprint planning
- **Confluence**: Documentation, knowledge bases, wikis

An AI agent that can interact with these tools enables:
- Natural language issue creation
- Quick project status queries
- Documentation search without leaving your IDE
- Automated reporting and updates

### Authentication Setup

Atlassian Cloud uses API tokens for authentication:

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "AI Agent")
4. Copy and save the token securely

```bash
# Set environment variables
export ATLASSIAN_URL="https://your-domain.atlassian.net"
export ATLASSIAN_EMAIL="your-email@example.com"
export ATLASSIAN_API_TOKEN="your-api-token"
```

---

## Level 1: Challenge

Build an agent that can:

1. Search Jira issues using JQL
2. Get issue details
3. Create new Jira issues
4. Search Confluence pages
5. Get Confluence page content

### Success Criteria

- [ ] Successfully authenticates with Atlassian
- [ ] Can search and display Jira issues
- [ ] Can create new issues via natural language
- [ ] Can search Confluence documentation
- [ ] Agent handles errors gracefully

---

## Level 2: Step-by-Step Guide

### Step 1: Install Dependencies

```bash
pip install atlassian-python-api
```

### Step 2: Set Up Atlassian Clients

```python
import os
from atlassian import Jira, Confluence

# Initialize Jira client
jira = Jira(
    url=os.getenv("ATLASSIAN_URL"),
    username=os.getenv("ATLASSIAN_EMAIL"),
    password=os.getenv("ATLASSIAN_API_TOKEN"),
    cloud=True
)

# Initialize Confluence client
confluence = Confluence(
    url=os.getenv("ATLASSIAN_URL"),
    username=os.getenv("ATLASSIAN_EMAIL"),
    password=os.getenv("ATLASSIAN_API_TOKEN"),
    cloud=True
)
```

### Step 3: Create Jira Tools

```python
from strands import tool

@tool
def search_jira_issues(jql_query: str, max_results: int = 10) -> str:
    """Search Jira issues using JQL (Jira Query Language).

    Common JQL examples:
    - 'project = PROJ AND status = Open'
    - 'assignee = currentUser() AND status != Done'
    - 'created >= -7d'  (created in last 7 days)

    Args:
        jql_query: JQL query string.
        max_results: Maximum number of results to return.
    """
    try:
        results = jira.jql(jql_query, limit=max_results)
        issues = results.get("issues", [])

        if not issues:
            return "No issues found matching the query."

        output = []
        for issue in issues:
            key = issue["key"]
            summary = issue["fields"]["summary"]
            status = issue["fields"]["status"]["name"]
            assignee = issue["fields"].get("assignee")
            assignee_name = assignee["displayName"] if assignee else "Unassigned"

            output.append(f"- [{key}] {summary}")
            output.append(f"  Status: {status} | Assignee: {assignee_name}")

        return "\n".join(output)
    except Exception as e:
        return f"Error searching Jira: {e}"


@tool
def get_jira_issue(issue_key: str) -> str:
    """Get details of a specific Jira issue.

    Args:
        issue_key: The issue key (e.g., 'PROJ-123').
    """
    try:
        issue = jira.get_issue(issue_key)
        fields = issue["fields"]

        details = [
            f"Issue: {issue_key}",
            f"Summary: {fields['summary']}",
            f"Status: {fields['status']['name']}",
            f"Type: {fields['issuetype']['name']}",
            f"Priority: {fields.get('priority', {}).get('name', 'None')}",
            f"Assignee: {fields.get('assignee', {}).get('displayName', 'Unassigned')}",
            f"Reporter: {fields.get('reporter', {}).get('displayName', 'Unknown')}",
            f"Description: {fields.get('description', 'No description')[:500]}",
        ]

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
        summary: Brief summary of the issue.
        description: Detailed description.
        issue_type: Type of issue (Task, Bug, Story, etc.).
    """
    try:
        issue = jira.create_issue(
            fields={
                "project": {"key": project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": issue_type},
            }
        )
        return f"Created issue: {issue['key']} - {summary}"
    except Exception as e:
        return f"Error creating issue: {e}"
```

### Step 4: Create Confluence Tools

```python
@tool
def search_confluence(query: str, space_key: str = None, max_results: int = 5) -> str:
    """Search Confluence for pages matching a query.

    Args:
        query: Search query text.
        space_key: Optional space key to limit search.
        max_results: Maximum number of results.
    """
    try:
        cql = f'text ~ "{query}"'
        if space_key:
            cql += f' AND space = "{space_key}"'

        results = confluence.cql(cql, limit=max_results)
        pages = results.get("results", [])

        if not pages:
            return "No pages found matching the query."

        output = []
        for page in pages:
            title = page["title"]
            space = page.get("resultGlobalContainer", {}).get("title", "Unknown")
            url = f"{os.getenv('ATLASSIAN_URL')}/wiki{page.get('url', '')}"
            output.append(f"- {title} (Space: {space})")
            output.append(f"  URL: {url}")

        return "\n".join(output)
    except Exception as e:
        return f"Error searching Confluence: {e}"


@tool
def get_confluence_page(page_title: str, space_key: str) -> str:
    """Get the content of a Confluence page.

    Args:
        page_title: The title of the page.
        space_key: The space key where the page is located.
    """
    try:
        page = confluence.get_page_by_title(
            space=space_key,
            title=page_title,
            expand="body.storage"
        )

        if not page:
            return f"Page '{page_title}' not found in space '{space_key}'"

        # Extract text content (remove HTML tags for readability)
        import re
        content = page.get("body", {}).get("storage", {}).get("value", "")
        text = re.sub(r'<[^>]+>', '', content)  # Simple HTML stripping
        text = ' '.join(text.split())  # Normalize whitespace

        # Truncate if too long
        if len(text) > 2000:
            text = text[:2000] + "... [truncated]"

        return f"Page: {page_title}\n\nContent:\n{text}"
    except Exception as e:
        return f"Error getting page: {e}"
```

### Step 5: Create the Agent

```python
from strands import Agent
from strands.models.anthropic import AnthropicModel

model = AnthropicModel(
    model_id="claude-haiku-4-5-20251001",
    max_tokens=1024
)

agent = Agent(
    model=model,
    tools=[
        search_jira_issues,
        get_jira_issue,
        create_jira_issue,
        search_confluence,
        get_confluence_page,
    ],
    system_prompt="""You are an Atlassian assistant that helps with Jira and Confluence.

Your capabilities:
- Search and view Jira issues
- Create new Jira issues
- Search Confluence documentation
- Retrieve page content

When creating issues:
- Ask for clarification if project key is not provided
- Suggest appropriate issue types (Task, Bug, Story)
- Write clear summaries and descriptions

When searching:
- Use JQL for precise Jira searches
- Suggest relevant search terms

Be helpful and efficient in managing project work."""
)
```

### Step 6: Test the Agent

```python
# Search issues
response = agent("Show me all open bugs in the PROJ project")
print(response)

# Get issue details
response = agent("What's the status of PROJ-123?")
print(response)

# Create an issue
response = agent("Create a task in PROJ to update the documentation for the new API")
print(response)

# Search documentation
response = agent("Find documentation about the deployment process")
print(response)
```

---

## Expected Output

```
================================================================================
 Kata 06: Atlassian Agent
================================================================================

User: Show me all open bugs assigned to me

Agent: Here are your open bugs:

- [PROJ-45] Login page throws 500 error on mobile
  Status: In Progress | Assignee: You

- [PROJ-38] Data export missing timestamp column
  Status: Open | Assignee: You

- [PROJ-32] Search results not paginating correctly
  Status: Open | Assignee: You

User: Create a bug for the payment timeout issue we discussed

Agent: I'll create a bug for the payment timeout issue. Here are the details:

Created issue: PROJ-67 - Payment processing timeout after 30 seconds

Summary: Payment processing timeout after 30 seconds
Type: Bug
Description: Users are experiencing timeouts when processing payments.
The system fails after 30 seconds without completing the transaction.

User: Find documentation about our API authentication

Agent: I found these relevant Confluence pages:

- API Authentication Guide (Space: Engineering)
  URL: https://your-domain.atlassian.net/wiki/spaces/ENG/pages/123

- OAuth 2.0 Setup Instructions (Space: Engineering)
  URL: https://your-domain.atlassian.net/wiki/spaces/ENG/pages/456

Would you like me to retrieve the content of any of these pages?
```

---

## JQL Quick Reference

| Query | Description |
|-------|-------------|
| `project = PROJ` | Issues in project PROJ |
| `status = Open` | Open issues |
| `assignee = currentUser()` | Assigned to you |
| `created >= -7d` | Created in last 7 days |
| `updated >= -1d` | Updated in last day |
| `priority = High` | High priority |
| `type = Bug` | Bug issues only |
| `labels = urgent` | Has label "urgent" |

Combine with AND/OR:
```
project = PROJ AND status = Open AND assignee = currentUser()
```

---

## Extension Challenges

1. **Add comments**: Create a tool to add comments to issues
2. **Transition issues**: Move issues through workflow states
3. **Create pages**: Add ability to create Confluence pages
4. **Sprint info**: Get current sprint status and velocity
5. **Bulk operations**: Update multiple issues at once

---

## Troubleshooting

### Authentication Errors

```
401 Unauthorized
```
- Check API token is correct
- Verify email matches Atlassian account
- Ensure URL includes `https://`

### Permission Errors

```
403 Forbidden
```
- Check you have access to the project/space
- Verify API token has required permissions

### Rate Limiting

```
429 Too Many Requests
```
- Add delays between requests
- Implement exponential backoff

---

## Security Notes

- **Never commit API tokens** to version control
- Use environment variables or secret managers
- Tokens have same permissions as your account
- Regularly rotate tokens
- Use least-privilege access when possible

---

## Resources

- [Atlassian Python API Documentation](https://atlassian-python-api.readthedocs.io/)
- [Jira Cloud REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Confluence Cloud REST API](https://developer.atlassian.com/cloud/confluence/rest/v1/)
- [JQL Documentation](https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/)
- [API Token Management](https://id.atlassian.com/manage-profile/security/api-tokens)
