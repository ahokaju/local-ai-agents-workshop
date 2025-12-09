"""
Kata 07: Atlassian MCP Server - Solution

This script demonstrates using MCP (Model Context Protocol) with Atlassian
services via our simple HTTP MCP server.

Prerequisites:
    1. Start the MCP server in another terminal:
       python mcp_server.py

    2. Make sure your .env file has the Atlassian credentials:
       ATLASSIAN_URL=https://your-domain.atlassian.net
       ATLASSIAN_EMAIL=your-email@example.com
       ATLASSIAN_API_TOKEN=your-api-token
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# MCP Server configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")


# ==============================================================================
# MCP Client
# ==============================================================================

class MCPClient:
    """Simple HTTP client for our MCP server."""

    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip("/")

    def health_check(self) -> bool:
        """Check if the MCP server is running."""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def list_tools(self) -> list:
        """Get list of available tools from the MCP server."""
        try:
            response = requests.get(f"{self.server_url}/mcp/v1/tools")
            response.raise_for_status()
            return response.json().get("tools", [])
        except requests.exceptions.RequestException as e:
            print(f"Error listing tools: {e}")
            return []

    def invoke(self, tool_name: str, parameters: dict = None) -> dict:
        """Invoke an MCP tool."""
        try:
            response = requests.post(
                f"{self.server_url}/mcp/v1/invoke",
                json={"name": tool_name, "parameters": parameters or {}},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "result": None}


# ==============================================================================
# Demo Functions
# ==============================================================================

def demo_list_tools(client: MCPClient):
    """List all available MCP tools."""
    print("\n--- Available MCP Tools ---")

    tools = client.list_tools()

    if not tools:
        print("   No tools found (is the server running?)")
        return []

    for tool in tools:
        name = tool.get("name", "Unknown")
        desc = tool.get("description", "No description")
        print(f"   - {name}")
        print(f"     {desc}")

    return tools


def demo_jira_projects(client: MCPClient):
    """List Jira projects via MCP."""
    print("\n--- Jira Projects ---")

    result = client.invoke("jira_get_projects")

    if result.get("error"):
        print(f"   Error: {result['error']}")
        return

    projects = result.get("result", {}).get("projects", [])
    if projects:
        for proj in projects:
            print(f"   - [{proj['key']}] {proj['name']}")
    else:
        print("   No projects found")


def demo_jira_search(client: MCPClient):
    """Search Jira issues via MCP."""
    print("\n--- Jira Issue Search ---")

    # Use assignee query to find issues assigned to current user
    # Alternative JQL queries you can try:
    #   - "ORDER BY created DESC" (all issues, may be empty due to permissions)
    #   - "project = YOUR_PROJECT_KEY" (specific project)
    #   - "assignee = currentUser()" (your assigned issues)
    jql = "assignee = currentUser() ORDER BY updated DESC"
    print(f"   JQL: {jql}")

    result = client.invoke("jira_search_issues", {
        "jql": jql,
        "max_results": 5
    })

    if result.get("error"):
        print(f"   Error: {result['error']}")
        return

    data = result.get("result", {})
    issues = data.get("issues", [])
    total = data.get("total", 0)

    print(f"   Found {total} issues (showing first {len(issues)}):")
    for issue in issues:
        print(f"   - [{issue['key']}] {issue['summary'][:50]}")
        print(f"     Status: {issue['status']}, Type: {issue['type']}")


def demo_confluence_spaces(client: MCPClient):
    """List Confluence spaces via MCP."""
    print("\n--- Confluence Spaces ---")

    result = client.invoke("confluence_get_spaces")

    if result.get("error"):
        print(f"   Error: {result['error']}")
        return

    spaces = result.get("result", {}).get("spaces", [])
    if spaces:
        for space in spaces:
            print(f"   - [{space['key']}] {space['name']} ({space['type']})")
    else:
        print("   No spaces found")


def demo_confluence_search(client: MCPClient):
    """Search Confluence pages via MCP."""
    print("\n--- Confluence Search ---")

    query = "Benefits"
    print(f"   Query: {query}")

    result = client.invoke("confluence_search", {
        "query": query,
        "max_results": 5
    })

    if result.get("error"):
        print(f"   Error: {result['error']}")
        return

    data = result.get("result", {})
    pages = data.get("pages", [])
    total = data.get("total", 0)

    print(f"   Found {total} pages (showing first {len(pages)}):")
    for page in pages:
        space = page.get('space', '???')
        print(f"   - {page['title']} (Space: {space})")


def print_comparison():
    """Print comparison of MCP vs Direct API approaches."""
    print("\n" + "=" * 70)
    print(" MCP vs Direct API Comparison")
    print("=" * 70)

    print("""
    | Aspect          | Direct API (Kata 06)      | MCP Server (Kata 07)     |
    |-----------------|---------------------------|--------------------------|
    | Setup           | Write tools yourself      | Use pre-built server     |
    | Maintenance     | You maintain code         | Server provider maintains|
    | Flexibility     | Full control              | Limited to MCP spec      |
    | Tool Discovery  | Manual definition         | Automatic from server    |
    | Portability     | Tied to your code         | Works with any MCP client|

    When to use Direct API:
    - Need custom tool behavior
    - Performance-critical applications
    - Full control over requests

    When to use MCP:
    - Rapid prototyping
    - Standard CRUD operations
    - Using Claude Desktop/IDE integrations
    - Want maintained implementations
    """)


# ==============================================================================
# Main
# ==============================================================================

def main():
    """Run the MCP demo."""
    print("=" * 70)
    print(" Kata 07: Atlassian MCP Server - Solution")
    print("=" * 70)

    # Create MCP client
    print(f"\n1. Connecting to MCP server at {MCP_SERVER_URL}...")
    client = MCPClient(MCP_SERVER_URL)

    if not client.health_check():
        print("\n   ERROR: MCP server is not running!")
        print("\n   Please start the server first:")
        print("   $ python mcp_server.py")
        print("\n   Then run this script again.")
        return

    print("   Connected!")

    # List available tools
    print("\n2. Listing MCP tools...")
    demo_list_tools(client)

    # Demo Jira
    print("\n3. Testing Jira tools...")
    demo_jira_projects(client)
    demo_jira_search(client)

    # Demo Confluence
    print("\n4. Testing Confluence tools...")
    demo_confluence_spaces(client)
    demo_confluence_search(client)

    # Print comparison
    print_comparison()

    print("\n" + "=" * 70)
    print(" Kata 07 Complete!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("- MCP provides a standardized protocol for tool access")
    print("- The same tools work with any MCP-compatible client")
    print("- Compare this to Kata 06 where we wrote tools directly")


if __name__ == "__main__":
    main()
