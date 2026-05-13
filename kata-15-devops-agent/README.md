# Kata 15: AWS DevOps Agent — Custom MCP Integration

> **Preview service**: AWS DevOps Agent is currently in Public Preview in **us-east-1 only**.
> You need an AWS account with DevOps Agent access. Request access at
> [aws.amazon.com/devops-agent](https://aws.amazon.com/devops-agent) if needed.
> Follow the console setup in Part A, then run the code in Part B.

## Objective

Build a custom MCP server that AWS DevOps Agent calls when investigating incidents. This
kata shows how a managed AWS agent can *consume* your MCP server to access internal tools
— the reverse of kata-08 (your agent → MCP server) and kata-13 (your agent → Gateway).

Here, **DevOps Agent is the agent** and **you provide the tools**.

## Learning Goals

- Understand the AWS DevOps Agent architecture (managed agent + your MCP server)
- Build a correct Streamable HTTP MCP server using FastMCP (the protocol DevOps Agent requires)
- Register your MCP server with DevOps Agent using the CLI (`register-service` + `associate-service`)
- Use the `devopsagent` boto3 client to inspect AgentSpaces programmatically
- Trigger incident investigations programmatically via the webhook API

## Prerequisites

- Completed Kata 08 (MCP server) and Kata 13 (MCP + AgentCore Gateway)
- AWS account with DevOps Agent access (us-east-1)
- AWS CLI configured with appropriate permissions
- `AWS_REGION=us-east-1` (DevOps Agent Preview is us-east-1 only)

```bash
pip install boto3 mcp python-dotenv
export AWS_REGION=us-east-1
```

## Time Estimate

35–45 minutes

## Difficulty

⭐⭐⭐ (Advanced — combines AWS service setup with proper MCP server development)

---

## Background

### How DevOps Agent Uses Your MCP Server

```
CloudWatch Alarm / webhook trigger
    ↓
AWS DevOps Agent (managed service, us-east-1 only)
    ↓ [Streamable HTTP MCP protocol + API key]
Your MCP server (kata-15/mcp_server.py)
    → tool: get_deployment_history(service, hours)
    → tool: query_runbook(incident_type)
    → tool: get_team_oncall(service)
    ↓
DevOps Agent reads your tool results and generates
an investigation report with root cause + next steps
```

### Architecture

```
┌────────────────────────────────────────────────────────────────┐
│  AWS Cloud (us-east-1)                                          │
│                                                                 │
│  CloudWatch Alarm ──────────┐                                  │
│  Webhook trigger ───────────┼──▶  AWS DevOps Agent             │
│                              │    AgentSpace                    │
│                              │         │                        │
│                              │         │ Streamable HTTP MCP    │
│                              │         │ (HTTPS + API key)      │
└──────────────────────────────┼─────────┼────────────────────────┘
                               │         │
                               │         ▼
                    ┌──────────┴──────────────────────────┐
                    │  Your MCP server (mcp_server.py)    │
                    │  FastMCP — Streamable HTTP transport │
                    │                                     │
                    │  get_deployment_history()           │
                    │  query_runbook()                    │
                    │  get_team_oncall()                  │
                    └─────────────────────────────────────┘
```

### Key Concept: MCP Transport Protocol

DevOps Agent **requires Streamable HTTP transport** for MCP servers. This is different
from the plain REST server in kata-08:

| Kata 08 (plain HTTP) | Kata 15 (Streamable HTTP MCP) |
|----------------------|-------------------------------|
| Custom `HTTPServer` class | FastMCP (`mcp` library) |
| REST endpoints (`/mcp/v1/tools`, `/mcp/v1/invoke`) | Standard MCP protocol |
| Works with your own agent | Required by AWS DevOps Agent |
| No protocol negotiation | MCP protocol handshake |

### Key Concept: DevOps Agent as MCP Consumer

In katas 08 and 13, *you* built an agent that consumed an MCP server.
In kata 15, *AWS DevOps Agent* is the consumer. Your job is to expose your
internal tools (deployments, runbooks, on-call) so the managed agent can use them.

### Service Identity

The DevOps Agent IAM service principal is `aidevops.amazonaws.com`. The IAM action
namespace is `aidevops:` (not `devopsagent:` — different from the CLI service name).

---

## boto3 Setup — Custom Service Model Required

AWS DevOps Agent is in preview and uses a **custom service model** not yet in the
standard boto3. You must add it before using `boto3.client("devopsagent")`:

```bash
# 1. Download the service model
curl -o devopsagent.json \
  "https://d1co8nkiwcta1g.cloudfront.net/devopsagent.json"

# 2. Register it with AWS CLI / boto3
aws configure add-model \
  --service-model "file://devopsagent.json" \
  --service-name devopsagent

# 3. Verify
aws devopsagent help \
  --endpoint-url "https://api.prod.cp.aidevops.us-east-1.api.aws"
```

Then in Python:

```python
import boto3

client = boto3.client(
    "devopsagent",
    region_name="us-east-1",
    endpoint_url="https://api.prod.cp.aidevops.us-east-1.api.aws"
)
```

---

## Part A: Console Setup (~10 min)

### Step 1: Create an AgentSpace

**Option A — Console:**
1. Sign in to [AWS Console](https://console.aws.amazon.com/devopsagent/)
2. Click **Create agent space**, enter a name (e.g., `kata-15-agent-space`)
3. Complete the wizard and note the **AgentSpace ID**

**Option B — CLI:**
```bash
aws devopsagent create-agent-space \
  --name "kata-15-agent-space" \
  --description "Kata 15 workshop agent space" \
  --endpoint-url "https://api.prod.cp.aidevops.us-east-1.api.aws" \
  --region us-east-1
# Response includes agentSpaceId — save it
export DEVOPS_AGENT_SPACE_ID=<agentSpaceId from response>
```

### Step 2: Associate Your AWS Account

```bash
aws devopsagent associate-service \
  --agent-space-id $DEVOPS_AGENT_SPACE_ID \
  --service-id aws \
  --configuration '{
    "aws": {
      "assumableRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/DevOpsAgentRole-AgentSpace",
      "accountId": "<ACCOUNT_ID>",
      "accountType": "monitor",
      "resources": []
    }
  }' \
  --endpoint-url "https://api.prod.cp.aidevops.us-east-1.api.aws" \
  --region us-east-1
```

> **Note**: The IAM role `DevOpsAgentRole-AgentSpace` is created automatically
> by the console wizard. For CLI-only setup, see the DevOps Agent IAM guide.

### Step 3: Register Your MCP Server

This is a two-step process: register the server globally, then associate it with
your AgentSpace.

```bash
# Step 3a: Start your MCP server and get a public URL
python mcp_server.py &   # starts on localhost:8001
ngrok http 8001           # in a separate terminal — note the https URL

# Step 3b: Register the MCP server (account level)
aws devopsagent register-service \
  --service mcpserver \
  --service-details '{
    "mcpserver": {
      "name": "kata15-ops-tools",
      "endpoint": "https://your-ngrok-url.ngrok.io/mcp",
      "description": "Internal ops tools: deployments, runbooks, on-call",
      "authorizationConfig": {
        "apiKey": {
          "apiKeyHeader": "X-Api-Key",
          "apiKeyName": "kata15-mcp-key",
          "apiKeyValue": "kata15-dev-key"
        }
      }
    }
  }' \
  --endpoint-url "https://api.prod.cp.aidevops.us-east-1.api.aws" \
  --region us-east-1
# Response includes serviceId — save it
export MCP_SERVICE_ID=<serviceId from response>

# Step 3c: Associate the MCP server with your AgentSpace
aws devopsagent associate-service \
  --agent-space-id $DEVOPS_AGENT_SPACE_ID \
  --service-id $MCP_SERVICE_ID \
  --configuration '{
    "mcpserver": {
      "name": "kata15-ops-tools",
      "endpoint": "https://your-ngrok-url.ngrok.io/mcp"
    }
  }' \
  --endpoint-url "https://api.prod.cp.aidevops.us-east-1.api.aws" \
  --region us-east-1
```

### Step 4: Set Up a Webhook (optional — for incident triggering)

In the Console: **AgentSpace → Event Channel → Create webhook**. Save the
webhook ID from the response URL.

```bash
export DEVOPS_AGENT_WEBHOOK_ID=<webhookId>
```

---

## Part B: Code (~25-35 min)

### Running the MCP Server

```bash
cd kata-15-devops-agent
export MCP_API_KEY=kata15-dev-key
python mcp_server.py
# Starts on http://localhost:8001/mcp (Streamable HTTP transport)
```

### Running the boto3 Inspector

```bash
cd kata-15-devops-agent
export DEVOPS_AGENT_SPACE_ID=<your-agent-space-id>
python solution.py
```

Expected output:
```
===========================================================
 Kata 15: AWS DevOps Agent - Solution
 Region: us-east-1
===========================================================

1. Listing AgentSpaces
----------------------------------------
Found 1 AgentSpace(s):
  - kata-15-agent-space (ID: as-abc123)

2. AgentSpace associations
----------------------------------------
  - service: aws (ID: svc-111)
  - service: mcpserver (ID: svc-222)
    Endpoint: https://your-ngrok-url.ngrok.io/mcp

3. Triggering test incident via webhook
----------------------------------------
POST https://event-ai.us-east-1.api.aws/webhook/generic/<id>
Status: 200 - Incident investigation initiated
```

---

## Level 1: Challenge

1. Implement the three `@mcp.tool()` functions in `mcp_server.py` (already done in solution)
2. Add the custom service model to boto3 (download + `aws configure add-model`)
3. Use `boto3.client("devopsagent")` to list agent spaces and their associations
4. Trigger a test incident via the webhook endpoint

### Success Criteria

- [ ] MCP server starts on port 8001 using Streamable HTTP transport
- [ ] `list_agent_spaces()` returns your AgentSpace via boto3
- [ ] `list_associations()` shows your MCP server is associated
- [ ] (Bonus) Trigger a test incident via webhook and watch DevOps Agent call your tools

---

## Level 2: Step-by-Step Guide

### MCP Tools with FastMCP

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("devops-agent-tools")

@mcp.tool()
def get_deployment_history(service: str, hours: int = 24) -> str:
    """Return recent deployments for a service within the last N hours.

    Args:
        service: Service name (e.g., "payment-api")
        hours: Look-back window in hours (default: 24)
    """
    # ... implementation
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    # Streamable HTTP transport — required by DevOps Agent
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8001)
```

### boto3 AgentSpace Inspector

```python
import boto3

ENDPOINT = "https://api.prod.cp.aidevops.us-east-1.api.aws"
client = boto3.client("devopsagent", region_name="us-east-1", endpoint_url=ENDPOINT)

# List all AgentSpaces
response = client.list_agent_spaces()
for space in response.get("agentSpaces", []):
    print(f"  - {space['name']} (ID: {space['agentSpaceId']})")

# List associations for a specific space
assocs = client.list_associations(agentSpaceId=AGENT_SPACE_ID)
for a in assocs.get("associations", []):
    print(f"  - service: {a.get('serviceId')}")
```

### Webhook Incident Trigger

```python
import requests
import hmac, hashlib, base64

WEBHOOK_ID = os.getenv("DEVOPS_AGENT_WEBHOOK_ID", "")
WEBHOOK_SECRET = os.getenv("DEVOPS_AGENT_WEBHOOK_SECRET", "")
WEBHOOK_URL = f"https://event-ai.us-east-1.api.aws/webhook/generic/{WEBHOOK_ID}"

payload = {
    "eventType": "incident",
    "incidentId": "test-incident-001",
    "action": "created",
    "priority": "HIGH",
    "title": "High latency on payment-api",
    "description": "P99 latency exceeded 5s for 10 minutes on payment-api",
    "timestamp": "2025-01-01T12:00:00Z",
    "service": "payment-api"
}
body = json.dumps(payload).encode()

# HMAC-SHA256 signature
sig = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).digest()
signature = base64.b64encode(sig).decode()

response = requests.post(
    WEBHOOK_URL,
    data=body,
    headers={
        "Content-Type": "application/json",
        "x-amzn-event-signature": signature
    }
)
print(f"Status: {response.status_code}")
```

---

## Extension Challenges

1. **Real data sources**: Replace mock data with calls to your deployment pipeline
   (GitHub Actions API, AWS CodeDeploy, etc.)
2. **OAuth authentication**: Register the MCP server with `oAuthClientCredentials`
   instead of API key
3. **Knowledge items**: Use `aidevops:CreateKnowledgeItem` to add runbook content
   directly to DevOps Agent's knowledge base
4. **Multiple services**: Register a second MCP server for a different team's tools
   (e.g., database ops, infrastructure)

---

## Resources

- [AWS DevOps Agent Documentation](https://docs.aws.amazon.com/devopsagent/latest/userguide/)
- [Connecting MCP Servers to DevOps Agent](https://docs.aws.amazon.com/devopsagent/latest/userguide/configuring-capabilities-for-aws-devops-agent-connecting-mcp-servers.html)
- [Invoking DevOps Agent via Webhook](https://docs.aws.amazon.com/devopsagent/latest/userguide/configuring-capabilities-for-aws-devops-agent-invoking-devops-agent-through-webhook.html)
- [CLI Onboarding Guide](https://docs.aws.amazon.com/devopsagent/latest/userguide/getting-started-with-aws-devops-agent-cli-onboarding-guide.html)
- [FastMCP (MCP Python library)](https://github.com/modelcontextprotocol/python-sdk)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [ngrok for local development](https://ngrok.com/docs)
