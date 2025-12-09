#!/usr/bin/env python3
"""
Kata 07: Simple HTTP-based MCP Server for Atlassian (Jira + Confluence)

This is a lightweight MCP server that exposes Jira and Confluence operations
via HTTP endpoints. It's designed for learning and demos, not production use.

Usage:
    export ATLASSIAN_URL="https://your-domain.atlassian.net"
    export ATLASSIAN_EMAIL="your-email@example.com"
    export ATLASSIAN_API_TOKEN="your-api-token"
    python mcp_server.py

Endpoints:
    GET  /health          - Health check
    GET  /mcp/v1/tools    - List available tools
    POST /mcp/v1/invoke   - Execute a tool
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote
import requests
from dotenv import load_dotenv

load_dotenv()

# Atlassian configuration (consistent with kata-06)
ATLASSIAN_URL = os.getenv("ATLASSIAN_URL", "").rstrip("/")
ATLASSIAN_EMAIL = os.getenv("ATLASSIAN_EMAIL")
ATLASSIAN_API_TOKEN = os.getenv("ATLASSIAN_API_TOKEN")

# Tool definitions
TOOLS = [
    # Jira tools
    {
        "name": "jira_get_projects",
        "description": "List all Jira projects accessible to the user",
        "parameters": []
    },
    {
        "name": "jira_search_issues",
        "description": "Search Jira issues using JQL (Jira Query Language)",
        "parameters": [
            {"name": "jql", "type": "string", "description": "JQL query string", "required": False},
            {"name": "max_results", "type": "integer", "description": "Maximum results (default 10)", "required": False}
        ]
    },
    {
        "name": "jira_get_issue",
        "description": "Get details of a specific Jira issue by key",
        "parameters": [
            {"name": "issue_key", "type": "string", "description": "Issue key (e.g., PROJ-123)", "required": True}
        ]
    },
    {
        "name": "jira_create_issue",
        "description": "Create a new Jira issue",
        "parameters": [
            {"name": "project_key", "type": "string", "description": "Project key (e.g., PROJ)", "required": True},
            {"name": "summary", "type": "string", "description": "Issue summary/title", "required": True},
            {"name": "issue_type", "type": "string", "description": "Issue type (Task, Bug, Story)", "required": False},
            {"name": "description", "type": "string", "description": "Issue description", "required": False}
        ]
    },
    # Confluence tools
    {
        "name": "confluence_get_spaces",
        "description": "List all Confluence spaces accessible to the user",
        "parameters": []
    },
    {
        "name": "confluence_search",
        "description": "Search Confluence pages by text",
        "parameters": [
            {"name": "query", "type": "string", "description": "Search query text", "required": True},
            {"name": "max_results", "type": "integer", "description": "Maximum results (default 10)", "required": False}
        ]
    },
    {
        "name": "confluence_get_page",
        "description": "Get content of a specific Confluence page",
        "parameters": [
            {"name": "page_id", "type": "string", "description": "Page ID", "required": True}
        ]
    }
]


def get_auth():
    """Return authentication tuple."""
    return (ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN)


def jira_request(method, endpoint, data=None):
    """Make a request to Jira API."""
    url = f"{ATLASSIAN_URL}/rest/api/3{endpoint}"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        auth=get_auth(),
        json=data if data else None
    )
    return response


def confluence_request(method, endpoint, data=None):
    """Make a request to Confluence API."""
    url = f"{ATLASSIAN_URL}/wiki/rest/api{endpoint}"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        auth=get_auth(),
        json=data if data else None
    )
    return response


# Tool implementations
def tool_jira_get_projects(params):
    """List all Jira projects."""
    response = jira_request("GET", "/project")
    if response.status_code == 200:
        projects = response.json()
        return {
            "projects": [
                {"key": p["key"], "name": p["name"], "id": p["id"]}
                for p in projects
            ]
        }
    return {"error": response.text, "status_code": response.status_code}


def tool_jira_search_issues(params):
    """Search Jira issues with JQL."""
    jql = params.get("jql", "ORDER BY created DESC")
    max_results = params.get("max_results", 10)

    # Use the new /search/jql endpoint (old /search was removed in 2024)
    # Need to request fields explicitly with new API
    fields = "summary,status,issuetype,created"
    response = jira_request("GET", f"/search/jql?jql={quote(jql)}&maxResults={max_results}&fields={fields}")
    if response.status_code == 200:
        data = response.json()
        issues = []
        # New API returns issues directly or in 'issues' key
        issue_list = data if isinstance(data, list) else data.get("issues", [])
        for issue in issue_list:
            # Handle both old format (fields nested) and new format (flat)
            if "fields" in issue:
                # Old format
                issues.append({
                    "key": issue["key"],
                    "summary": issue["fields"]["summary"],
                    "status": issue["fields"]["status"]["name"],
                    "type": issue["fields"]["issuetype"]["name"],
                    "created": issue["fields"]["created"]
                })
            else:
                # New format - fields may be at top level or use different keys
                issues.append({
                    "key": issue.get("key", issue.get("id", "unknown")),
                    "summary": issue.get("summary", issue.get("summaryText", "No summary")),
                    "status": issue.get("status", {}).get("name", "Unknown") if isinstance(issue.get("status"), dict) else str(issue.get("status", "Unknown")),
                    "type": issue.get("issuetype", {}).get("name", "Unknown") if isinstance(issue.get("issuetype"), dict) else str(issue.get("issuetype", "Unknown")),
                    "created": issue.get("created", "Unknown")
                })
        total = data.get("total", len(issues)) if isinstance(data, dict) else len(issues)
        return {"total": total, "issues": issues}
    return {"error": response.text, "status_code": response.status_code}


def tool_jira_get_issue(params):
    """Get a specific Jira issue."""
    issue_key = params.get("issue_key")
    if not issue_key:
        return {"error": "issue_key is required"}

    response = jira_request("GET", f"/issue/{issue_key}")
    if response.status_code == 200:
        issue = response.json()
        return {
            "key": issue["key"],
            "summary": issue["fields"]["summary"],
            "description": issue["fields"].get("description"),
            "status": issue["fields"]["status"]["name"],
            "type": issue["fields"]["issuetype"]["name"],
            "priority": issue["fields"].get("priority", {}).get("name"),
            "assignee": issue["fields"].get("assignee", {}).get("displayName") if issue["fields"].get("assignee") else None,
            "created": issue["fields"]["created"],
            "updated": issue["fields"]["updated"]
        }
    return {"error": response.text, "status_code": response.status_code}


def tool_jira_create_issue(params):
    """Create a new Jira issue."""
    project_key = params.get("project_key")
    summary = params.get("summary")
    issue_type = params.get("issue_type", "Task")
    description = params.get("description", "")

    if not project_key or not summary:
        return {"error": "project_key and summary are required"}

    data = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": issue_type},
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}]
                    }
                ] if description else []
            }
        }
    }

    response = jira_request("POST", "/issue", data)
    if response.status_code in (200, 201):
        result = response.json()
        return {"key": result["key"], "id": result["id"], "self": result["self"]}
    return {"error": response.text, "status_code": response.status_code}


def tool_confluence_get_spaces(params):
    """List all Confluence spaces."""
    response = confluence_request("GET", "/space")
    if response.status_code == 200:
        data = response.json()
        spaces = []
        for space in data.get("results", []):
            spaces.append({
                "key": space["key"],
                "name": space["name"],
                "type": space["type"],
                "id": space["id"]
            })
        return {"spaces": spaces}
    return {"error": response.text, "status_code": response.status_code}


def tool_confluence_search(params):
    """Search Confluence pages."""
    query = params.get("query")
    max_results = params.get("max_results", 10)

    if not query:
        return {"error": "query is required"}

    # Search by title first (more precise), fall back to text search
    # Use title~ for title search, text~ for full-text search
    cql = f'type=page AND title~"{query}"'
    response = confluence_request("GET", f"/content/search?cql={quote(cql)}&limit={max_results}")
    if response.status_code == 200:
        data = response.json()
        pages = []
        for page in data.get("results", []):
            # Extract space key from _expandable.space (format: "/rest/api/space/KEY")
            space_key = None
            expandable_space = page.get("_expandable", {}).get("space", "")
            if expandable_space:
                # Extract key from "/rest/api/space/HR" -> "HR"
                space_key = expandable_space.split("/")[-1] if "/" in expandable_space else None

            pages.append({
                "id": page["id"],
                "title": page["title"],
                "type": page["type"],
                "space": space_key
            })
        # Use "size" field as total (totalSize doesn't exist in this API response)
        return {"total": data.get("size", len(pages)), "pages": pages}
    return {"error": response.text, "status_code": response.status_code}


def tool_confluence_get_page(params):
    """Get a specific Confluence page."""
    page_id = params.get("page_id")
    if not page_id:
        return {"error": "page_id is required"}

    response = confluence_request("GET", f"/content/{page_id}?expand=body.storage,space,version")
    if response.status_code == 200:
        page = response.json()
        return {
            "id": page["id"],
            "title": page["title"],
            "space": page.get("space", {}).get("key"),
            "version": page.get("version", {}).get("number"),
            "body": page.get("body", {}).get("storage", {}).get("value", "")
        }
    return {"error": response.text, "status_code": response.status_code}


# Tool dispatcher
TOOL_HANDLERS = {
    "jira_get_projects": tool_jira_get_projects,
    "jira_search_issues": tool_jira_search_issues,
    "jira_get_issue": tool_jira_get_issue,
    "jira_create_issue": tool_jira_create_issue,
    "confluence_get_spaces": tool_confluence_get_spaces,
    "confluence_search": tool_confluence_search,
    "confluence_get_page": tool_confluence_get_page,
}


class MCPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP server."""

    def _send_json(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/health":
            self._send_json({"status": "healthy", "service": "atlassian-mcp"})

        elif path == "/mcp/v1/tools":
            self._send_json({"tools": TOOLS})

        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        if path == "/mcp/v1/invoke":
            tool_name = data.get("name")
            parameters = data.get("parameters", {})

            if not tool_name:
                self._send_json({"error": "Tool name is required"}, 400)
                return

            handler = TOOL_HANDLERS.get(tool_name)
            if not handler:
                self._send_json({"error": f"Unknown tool: {tool_name}"}, 404)
                return

            try:
                result = handler(parameters)
                self._send_json({"result": result, "error": None})
            except Exception as e:
                self._send_json({"result": None, "error": str(e)}, 500)

        else:
            self._send_json({"error": "Not found"}, 404)

    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[MCP] {args[0]}")


def main():
    """Run the MCP server."""
    # Validate configuration
    if not all([ATLASSIAN_URL, ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN]):
        print("Error: Missing Atlassian configuration!")
        print("Please set the following environment variables:")
        print("  - ATLASSIAN_URL")
        print("  - ATLASSIAN_EMAIL")
        print("  - ATLASSIAN_API_TOKEN")
        return

    port = int(os.getenv("MCP_PORT", 8000))

    print("=" * 60)
    print(" Atlassian MCP Server")
    print("=" * 60)
    print(f"\nAtlassian URL: {ATLASSIAN_URL}")
    print(f"User: {ATLASSIAN_EMAIL}")
    print(f"\nStarting server on http://localhost:{port}")
    print("\nEndpoints:")
    print(f"  GET  http://localhost:{port}/health")
    print(f"  GET  http://localhost:{port}/mcp/v1/tools")
    print(f"  POST http://localhost:{port}/mcp/v1/invoke")
    print("\nPress Ctrl+C to stop\n")
    print("=" * 60)

    server = HTTPServer(("", port), MCPRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
