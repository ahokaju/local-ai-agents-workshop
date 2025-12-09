"""
Kata 07: Atlassian MCP Server - Starter Template

Learn to use the Model Context Protocol (MCP) with Atlassian services.

This kata explores MCP as an alternative to direct API integration (Kata 06),
using a standardized protocol for tool discovery and invocation.

Prerequisites:
    1. Start the MCP server in another terminal:
       python mcp_server.py

    2. Make sure your .env file has the Atlassian credentials
       (same as Kata 06)
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# MCP Server configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")


# ==============================================================================
# MCP Client - TODO: Complete the implementation
# ==============================================================================

class MCPClient:
    """Simple HTTP client for our MCP server."""

    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip("/")

    def health_check(self) -> bool:
        """Check if the MCP server is running."""
        # TODO 1: Implement health check
        # Hint: GET request to {server_url}/health
        # Return True if status code is 200
        pass

    def list_tools(self) -> list:
        """Get list of available tools from the MCP server."""
        # TODO 2: Implement tool listing
        # Hint: GET request to {server_url}/mcp/v1/tools
        # Return the "tools" list from the JSON response
        pass

    def invoke(self, tool_name: str, parameters: dict = None) -> dict:
        """Invoke an MCP tool."""
        # TODO 3: Implement tool invocation
        # Hint: POST request to {server_url}/mcp/v1/invoke
        # Body: {"name": tool_name, "parameters": parameters or {}}
        # Return the JSON response
        pass


# ==============================================================================
# Demo Functions - TODO: Complete the implementation
# ==============================================================================

def demo_list_tools(client: MCPClient):
    """List all available MCP tools."""
    print("\n--- Available MCP Tools ---")

    # TODO 4: Use client.list_tools() and print each tool
    # For each tool, print:
    #   - {name}
    #     {description}

    print("   TODO: Implement demo_list_tools()")


def demo_jira_projects(client: MCPClient):
    """List Jira projects via MCP."""
    print("\n--- Jira Projects ---")

    # TODO 5: Use client.invoke("jira_get_projects", {})
    # Print each project: [{key}] {name}

    print("   TODO: Implement demo_jira_projects()")


def demo_jira_search(client: MCPClient):
    """Search Jira issues via MCP."""
    print("\n--- Jira Issue Search ---")

    # TODO 6: Use client.invoke("jira_search_issues", {...})
    # Parameters: {"jql": "assignee = currentUser() ORDER BY updated DESC", "max_results": 5}
    # Print each issue: [{key}] {summary}
    # Note: You can also try "project = YOUR_PROJECT_KEY" for project-specific search

    print("   TODO: Implement demo_jira_search()")


def demo_confluence_spaces(client: MCPClient):
    """List Confluence spaces via MCP."""
    print("\n--- Confluence Spaces ---")

    # TODO 7: Use client.invoke("confluence_get_spaces", {})
    # Print each space: [{key}] {name}

    print("   TODO: Implement demo_confluence_spaces()")


def demo_confluence_search(client: MCPClient):
    """Search Confluence pages via MCP."""
    print("\n--- Confluence Search ---")

    # TODO 8: Use client.invoke("confluence_search", {...})
    # Parameters: {"query": "Benefits", "max_results": 5}
    # Print each page: {title} (Space: {space})

    print("   TODO: Implement demo_confluence_search()")


# ==============================================================================
# Main
# ==============================================================================

def main():
    """Run the MCP demo."""
    print("=" * 70)
    print(" Kata 07: Atlassian MCP Server")
    print("=" * 70)

    # Create MCP client
    print(f"\n1. Connecting to MCP server at {MCP_SERVER_URL}...")
    client = MCPClient(MCP_SERVER_URL)

    # Check server health
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

    print("\n" + "=" * 70)
    print(" Kata 07 Complete!")
    print("=" * 70)
    print("\nReflection Questions:")
    print("- How does this compare to Kata 06 (direct API)?")
    print("- What are the benefits of using MCP?")
    print("- When would you choose MCP vs direct API?")


if __name__ == "__main__":
    main()
