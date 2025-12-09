# Kata 07: Atlassian MCP Server

## Objective

Learn to use the Model Context Protocol (MCP) with Atlassian services, comparing the MCP approach to direct API integration (Kata 06) and understanding when to use each.

## Learning Goals

- Understand MCP (Model Context Protocol) architecture
- Run a simple MCP server for Atlassian
- Use MCP tools via HTTP endpoints
- Compare MCP vs direct API approaches

## Prerequisites

- Completed Kata 06 (Atlassian Agent)
- Atlassian Cloud account with API access (same credentials as Kata 06)

## Time Estimate

30-40 minutes

## Difficulty

**Intermediate**

---

## Background

### What is MCP?

Model Context Protocol (MCP) is a standard protocol for connecting AI models to external data sources and tools:

- **Standardized interface**: Common protocol across different tools
- **Tool discovery**: Automatic tool schema exposure
- **Portability**: Same tools work with any MCP client

### MCP Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Your Application                            │
│   ┌─────────────┐                                                   │
│   │   Client    │                                                   │
│   │  (Python)   │                                                   │
│   └──────┬──────┘                                                   │
│          │                                                          │
│          ▼                                                          │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐          │
│   │ HTTP Client │────▶│ MCP Server  │────▶│  Atlassian  │          │
│   │             │     │ (mcp_server │     │   API       │          │
│   │             │     │    .py)     │     │             │          │
│   └─────────────┘     └─────────────┘     └─────────────┘          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Kata 06 vs Kata 07

| Aspect | Kata 06 (Direct API) | Kata 07 (MCP Server) |
|--------|---------------------|----------------------|
| Tools | Write yourself | Pre-built on server |
| Discovery | Manual | Automatic via `/mcp/v1/tools` |
| Invocation | Direct function call | HTTP POST to `/mcp/v1/invoke` |
| Portability | Tied to your code | Any MCP client works |

---

## Part 1: Running the MCP Server

### Step 1: Start the Server

Open a terminal and run:

```bash
cd kata-07-atlassian-mcp
python mcp_server.py
```

You should see:

```
============================================================
 Atlassian MCP Server
============================================================

Atlassian URL: https://your-domain.atlassian.net
User: your-email@example.com

Starting server on http://localhost:8000

Endpoints:
  GET  http://localhost:8000/health
  GET  http://localhost:8000/mcp/v1/tools
  POST http://localhost:8000/mcp/v1/invoke

Press Ctrl+C to stop
============================================================
```

### Step 2: Test with curl

In another terminal:

```bash
# Health check
curl http://localhost:8000/health

# List available tools
curl http://localhost:8000/mcp/v1/tools | python -m json.tool
```

---

## Part 2: Using MCP Tools with curl

### Jira Tools

**List All Projects**
```bash
curl -X POST http://localhost:8000/mcp/v1/invoke \
  -H "Content-Type: application/json" \
  -d '{"name": "jira_get_projects", "parameters": {}}'
```

**Search Issues (with JQL)**
```bash
curl -X POST http://localhost:8000/mcp/v1/invoke \
  -H "Content-Type: application/json" \
  -d '{"name": "jira_search_issues", "parameters": {"jql": "ORDER BY created DESC", "max_results": 5}}'
```

**Search Issues (by project)**
```bash
curl -X POST http://localhost:8000/mcp/v1/invoke \
  -H "Content-Type: application/json" \
  -d '{"name": "jira_search_issues", "parameters": {"jql": "project = DEMO AND status = Open", "max_results": 10}}'
```

**Get Specific Issue**
```bash
curl -X POST http://localhost:8000/mcp/v1/invoke \
  -H "Content-Type: application/json" \
  -d '{"name": "jira_get_issue", "parameters": {"issue_key": "PROJ-123"}}'
```

**Create New Issue**
```bash
curl -X POST http://localhost:8000/mcp/v1/invoke \
  -H "Content-Type: application/json" \
  -d '{"name": "jira_create_issue", "parameters": {"project_key": "DEMO", "summary": "Test issue from MCP", "issue_type": "Task", "description": "Created via MCP server"}}'
```

### Confluence Tools

**List All Spaces**
```bash
curl -X POST http://localhost:8000/mcp/v1/invoke \
  -H "Content-Type: application/json" \
  -d '{"name": "confluence_get_spaces", "parameters": {}}'
```

**Search Pages**
```bash
curl -X POST http://localhost:8000/mcp/v1/invoke \
  -H "Content-Type: application/json" \
  -d '{"name": "confluence_search", "parameters": {"query": "Benefits", "max_results": 5}}'
```

**Get Page Content**
```bash
curl -X POST http://localhost:8000/mcp/v1/invoke \
  -H "Content-Type: application/json" \
  -d '{"name": "confluence_get_page", "parameters": {"page_id": "12345678"}}'
```

### Pretty Print JSON Output

Add `| python -m json.tool` to any command for formatted output:

```bash
curl -X POST http://localhost:8000/mcp/v1/invoke \
  -H "Content-Type: application/json" \
  -d '{"name": "jira_get_projects", "parameters": {}}' | python -m json.tool
```

---

## Part 3: Python Client

### Run the Solution

With the MCP server still running, open another terminal:

```bash
python solution.py
```

### Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `jira_get_projects` | List all Jira projects | None |
| `jira_search_issues` | Search issues with JQL | `jql`, `max_results` |
| `jira_get_issue` | Get issue details | `issue_key` (required) |
| `jira_create_issue` | Create a new issue | `project_key`, `summary`, `issue_type`, `description` |
| `confluence_get_spaces` | List all spaces | None |
| `confluence_search` | Search pages | `query` (required), `max_results` |
| `confluence_get_page` | Get page content | `page_id` (required) |

---

## Level 1: Challenge

1. Start the MCP server (`python mcp_server.py`)
2. Test the health endpoint with curl
3. List available tools
4. Search Jira issues via MCP
5. Search Confluence pages via MCP
6. Complete the `starter.py` TODOs

### Success Criteria

- [ ] MCP server is running
- [ ] Can list tools via `/mcp/v1/tools`
- [ ] Can invoke Jira tools
- [ ] Can invoke Confluence tools
- [ ] Understand MCP vs direct API trade-offs

---

## Level 2: Complete starter.py

The starter template has 8 TODOs:

1. **TODO 1-3**: Implement the MCPClient class methods
2. **TODO 4-8**: Implement the demo functions

Compare your implementation with `solution.py`.

---

## Expected Output

```
======================================================================
 Kata 07: Atlassian MCP Server - Solution
======================================================================

1. Connecting to MCP server at http://localhost:8000...
   Connected!

2. Listing MCP tools...

--- Available MCP Tools ---
   - jira_get_projects
     List all Jira projects accessible to the user
   - jira_search_issues
     Search Jira issues using JQL (Jira Query Language)
   ...

3. Testing Jira tools...

--- Jira Projects ---
   - [DEMO] Demo Project
   - [ENG] Engineering

--- Jira Issue Search ---
   JQL: ORDER BY created DESC
   Found 15 issues (showing first 5):
   - [DEMO-5] Update documentation
     Status: Open, Type: Task
   ...

4. Testing Confluence tools...

--- Confluence Spaces ---
   - [DOC] Documentation (global)
   ...
```

---

## MCP vs Direct API Comparison

| Aspect | Direct API (Kata 06) | MCP Server (Kata 07) |
|--------|---------------------|----------------------|
| Setup | Write tools yourself | Use pre-built server |
| Maintenance | You maintain code | Server provider maintains |
| Flexibility | Full control | Limited to MCP spec |
| Tool Discovery | Manual definition | Automatic from server |
| Portability | Tied to your code | Works with any MCP client |

### When to Use Direct API
- Need custom tool behavior
- Performance-critical applications
- Full control over requests

### When to Use MCP
- Rapid prototyping
- Standard CRUD operations
- Using Claude Desktop/IDE integrations
- Want maintained implementations

---

## Extension Challenges (Optional)

### 1. Official Atlassian Remote MCP

For Claude Desktop integration:

```bash
npm install -g mcp-remote
```

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "mcp-remote",
      "args": ["https://mcp.atlassian.com"]
    }
  }
}
```

### 2. Add New Tools

Extend `mcp_server.py` with additional tools:
- `jira_add_comment` - Add comment to an issue
- `confluence_create_page` - Create a new page

### 3. Docker Deployment

Create a Dockerfile for the MCP server for production use.

---

## Troubleshooting

### Server Won't Start

```
Error: Missing Atlassian configuration!
```
- Check your `.env` file has `ATLASSIAN_URL`, `ATLASSIAN_EMAIL`, `ATLASSIAN_API_TOKEN`

### Connection Refused

```
Error: Connection refused
```
- Make sure `mcp_server.py` is running in another terminal
- Check the port (default 8000)

### 401/403 Errors

- Verify your Atlassian API token is correct
- Check the token hasn't expired
- Ensure your user has access to the projects/spaces

---

## Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [Atlassian REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Confluence REST API](https://developer.atlassian.com/cloud/confluence/rest/v1/)
