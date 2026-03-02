# Kata 13: AgentCore Gateway

## Objective

Use AgentCore Gateway to register an existing REST API as MCP-compatible tools — without writing an MCP server manually. Contrast this with kata-07 where you hand-coded `mcp_server.py`. The Gateway auto-generates the MCP infrastructure from an API endpoint declaration.

## Learning Goals

- Understand what AgentCore Gateway does and when to use it
- Create a Gateway with `protocolType="MCP"` using the `bedrock-agentcore-control` boto3 client
- Register a REST API as a gateway target with `create_gateway_target()`
- Connect a Strands agent via `MCPClient` using the Gateway URL
- Discover available tools with `mcp.list_tools_sync()`
- Compare: hand-written MCP server (kata-07) vs Gateway auto-generation (kata-13)

## Prerequisites

- Completed Kata 07 (MCP Server) — understand MCP concepts
- AWS account with Bedrock + AgentCore enabled
- `AWS_BEARER_TOKEN_BEDROCK` and `AWS_REGION` environment variables set

```bash
pip install 'strands-agents[bedrock]' bedrock-agentcore boto3 python-dotenv
export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
export AWS_REGION=us-east-1
```

## Time Estimate

25–35 minutes

## Difficulty

⭐⭐⭐ (Advanced — involves AWS API management infrastructure)

---

## Background

### Kata-07 vs Kata-13: Building MCP Servers

In kata-07, you built a hand-crafted MCP server:

```python
# kata-07: mcp_server.py (manual MCP server)
@mcp.tool()
async def search_confluence(query: str) -> str:
    """Search Confluence pages."""
    # Custom implementation...
```

In kata-13, Gateway handles the MCP server layer automatically:

```python
# kata-13: declare the API via an OpenAPI spec — no server code needed
control_client.create_gateway_target(
    gatewayIdentifier=gateway_id,
    name="OpenMeteoWeather",
    targetConfiguration={
        "mcp": {"openApiSchema": {"inlinePayload": OPEN_METEO_SPEC}}
    },
    credentialProviderConfigurations=[...]  # required even for public APIs
)
# Gateway auto-generates the MCP tool from the spec
```

### Architecture

```
                    ┌─────────────────────────────────────────────┐
                    │          AgentCore Gateway (AWS managed)     │
REST API            │                                             │
(Open-Meteo) ◀──── │  Gateway Target: GetWeatherForecast          │
                    │  → wraps REST endpoint as MCP tool          │
                    │  → handles protocol translation             │
                    └──────────────┬──────────────────────────────┘
                                   │ MCP protocol (streamable HTTP)
                    ┌──────────────▼──────────────────────────────┐
                    │  MCPClient (Strands)                         │
                    │  → list_tools_sync() discovers tools         │
                    │  → Agent uses tools just like kata-07        │
                    └─────────────────────────────────────────────┘
```

### When to Use Gateway vs Hand-Written MCP Server

| Scenario | Use Gateway | Use Hand-Written Server |
|----------|-------------|------------------------|
| Existing REST API | ✓ | |
| Custom business logic | | ✓ |
| Authentication transformation | ✓ (Gateway handles auth) | ✓ |
| Data processing/transformation | | ✓ |
| Rapid prototyping | ✓ | |
| Production with complex flows | | ✓ |

### Gateway Authentication Options

- `authorizerType="NONE"` — public endpoint (good for demos, open APIs)
- `authorizerType="IAM"` — IAM-signed requests (production)
- `authorizerType="API_KEY"` — API key header forwarding

---

## Level 1: Challenge

Build a Python script that:

1. Creates a `bedrock-agentcore-control` boto3 client
2. Creates a Gateway with `protocolType="MCP"` and extracts the gateway URL
3. Registers the Open-Meteo weather API as a gateway target
4. Connects a Strands agent via `MCPClient` to the gateway URL
5. Discovers tools with `list_tools_sync()` and prints their names
6. Asks the agent weather questions using the Gateway-proxied tool
7. Cleans up (deletes gateway + targets)

### Success Criteria

- [ ] Gateway created and reaches `READY` status
- [ ] Gateway URL returned and usable
- [ ] At least 1 tool discovered via `list_tools_sync()`
- [ ] Agent answers a weather question using the Gateway tool (not from memory)
- [ ] Gateway deleted after use (no lingering infrastructure)

---

## Level 2: Step-by-Step Guide

### Step 0a: IAM Role for the Gateway

The Gateway requires an IAM role with a trust policy for `bedrock-agentcore.amazonaws.com`:

```python
import json
import boto3

iam = boto3.client("iam")
trust_policy = json.dumps({
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
})
resp = iam.create_role(
    RoleName="kata13-agentcore-gateway-role",
    AssumeRolePolicyDocument=trust_policy,
)
role_arn = resp["Role"]["Arn"]
```

### Step 0b: Secrets Manager Secret (Required for OpenAPI Targets)

The `openApiSchema` target type only supports `OAUTH` or `API_KEY` credentials — not `GATEWAY_IAM_ROLE`. You must create a Secrets Manager secret even for public APIs:

```python
sm = boto3.client("secretsmanager", region_name=AWS_REGION)
resp = sm.create_secret(
    Name="kata13-open-meteo-api-key",
    SecretString="open-meteo-no-auth-needed",
)
secret_arn = resp["ARN"]

# Grant the gateway role read access to the secret
policy = json.dumps({
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": "secretsmanager:GetSecretValue",
        "Resource": secret_arn
    }]
})
iam.put_role_policy(
    RoleName="kata13-agentcore-gateway-role",
    PolicyName="kata13-secret-read",
    PolicyDocument=policy,
)
```

### Step 1: Create the boto3 Client

```python
control_client = boto3.client("bedrock-agentcore-control", region_name=AWS_REGION)
```

### Step 2: Create the Gateway and Wait for READY

`roleArn` is required. The gateway URL is returned at the top level as `gatewayUrl`. Poll until status is `READY` before registering targets:

```python
response = control_client.create_gateway(
    name="kata13-weather-gateway",
    description="Exposes Open-Meteo weather API as MCP tools",
    protocolType="MCP",
    authorizerType="NONE",
    roleArn=role_arn,          # required
)
gateway_id = response["gatewayId"]
gateway_url = response["gatewayUrl"]   # top-level key, NOT response["mcp"]["url"]
print(f"Gateway URL: {gateway_url}")

# Poll until READY
import time
while True:
    status = control_client.get_gateway(gatewayIdentifier=gateway_id)["status"]
    print(f"[{status}]", end=" ", flush=True)
    if status == "READY":
        break
    time.sleep(5)
```

### Step 3: Register the API Target

Targets use `targetConfiguration` (not `endpoint`). The `openApiSchema` type requires an inline OpenAPI spec and `credentialProviderConfigurations`:

```python
OPEN_METEO_SPEC = json.dumps({
    "openapi": "3.0.0",
    "info": {"title": "Open-Meteo Weather API", "version": "1.0.0"},
    "servers": [{"url": "https://api.open-meteo.com"}],
    "paths": {
        "/v1/forecast": {
            "get": {
                "operationId": "GetWeatherForecast",
                "summary": "Get weather forecast for a location",
                "parameters": [
                    {"name": "latitude", "in": "query", "required": True, "schema": {"type": "number"}},
                    {"name": "longitude", "in": "query", "required": True, "schema": {"type": "number"}},
                    {"name": "current_weather", "in": "query", "schema": {"type": "boolean"}},
                ]
            }
        }
    }
})

response = control_client.create_gateway_target(
    gatewayIdentifier=gateway_id,
    name="OpenMeteoWeather",
    targetConfiguration={
        "mcp": {
            "openApiSchema": {
                "inlinePayload": OPEN_METEO_SPEC
            }
        }
    },
    credentialProviderConfigurations=[{
        "credentialProviderType": "API_KEY",
        "credentialProvider": {
            "apiKeyCredentialProvider": {
                "providerArn": secret_arn,
                "credentialParameterName": "X-Api-Key",
                "credentialLocation": "HEADER"
            }
        }
    }],
)
target_id = response["targetId"]
```

### Step 4: Connect Agent via MCPClient

Pass a callable (lambda) to `MCPClient`, not a dict. Tool names are accessed via `.tool_name`, not `.name`:

```python
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.tools.mcp import MCPClient

with MCPClient(lambda: streamablehttp_client(gateway_url)) as mcp:
    tools = mcp.list_tools_sync()
    print(f"Tools: {[t.tool_name for t in tools]}")   # .tool_name, not .name

    agent = Agent(
        model=BedrockModel(model_id=DEFAULT_MODEL, region_name=AWS_REGION),
        tools=tools,
        system_prompt=(
            "You are a weather assistant. Use tools for real data. "
            "Helsinki: lat=60.1699, lon=24.9384."
        )
    )
    response = agent("What's the current temperature in Helsinki?")
    print(response)
```

### Step 5: Cleanup

Use `targetId` (not `targetIdentifier`) in `delete_gateway_target`. Wait briefly after deleting targets before deleting the gateway:

```python
# Delete targets first, then gateway
targets = control_client.list_gateway_targets(gatewayIdentifier=gateway_id)
for t in targets.get("items", []):
    control_client.delete_gateway_target(
        gatewayIdentifier=gateway_id,
        targetId=t["targetId"]          # targetId, NOT targetIdentifier
    )
time.sleep(3)                           # allow propagation before gateway deletion
control_client.delete_gateway(gatewayIdentifier=gateway_id)
```

---

## Running the Solution

```bash
python solution.py
```

Expected output:
```
0a. IAM role for Gateway
Created IAM role: arn:aws:iam::123456789012:role/kata13-agentcore-gateway-role

0b. Secrets Manager secret (API key placeholder)
Created secret: arn:aws:secretsmanager:us-east-1:123456789012:secret:kata13-open-meteo-api-key-...
Granted role kata13-agentcore-gateway-role access to secret

1. Creating AgentCore Gateway (MCP protocol)
Creating Gateway: kata13-weather-gateway
Gateway ID:  gw-abc123
Gateway URL: https://...agentcore.aws/mcp/v1
Waiting for gateway to become READY [CREATING] [CREATING] [READY]

2. Registering weather API as gateway target
Registering Open-Meteo weather API as gateway target...
Target ID: tgt-def456

3. Connecting agent via MCPClient
Gateway exposed 1 tool(s): ['GetWeatherForecast']

User: What's the current temperature in Helsinki, Finland?
Agent: Based on the weather data from the API, Helsinki is currently...

4. Cleanup
  Deleted target: tgt-def456
  Deleted gateway: gw-abc123
  Deleted IAM role: kata13-agentcore-gateway-role
  Deleted secret: kata13-open-meteo-api-key
```

---

## Extension Challenges

1. **Add a second API**: Register a second target (e.g., a currency exchange API) and build an agent that uses both
2. **IAM authentication**: Change `authorizerType` to `"IAM"` and configure IAM-signed requests
3. **Existing internal API**: Register your own REST API (or a mock at `localhost`) as a Gateway target
4. **Persistent gateway**: Remove the cleanup step, save the gateway URL, and reuse it across script runs

---

## Comparison: Kata-07 vs Kata-13

| Aspect | Kata-07 (Manual MCP) | Kata-13 (Gateway) |
|--------|---------------------|-------------------|
| Server code | ~100 lines Python | 0 lines |
| Deployment | Manual (`python mcp_server.py`) | AWS managed |
| APIs supported | Hand-coded only | Any REST API |
| Flexibility | Full control | Limited to REST→MCP mapping |
| Auth | Custom | IAM, API key, None |
| Cost | Free (local) | AWS Gateway pricing |
| MCPClient usage | Identical | Identical |

**Key insight:** The agent code in step 4 is identical to kata-07 — `MCPClient` doesn't care whether the MCP server was hand-written or auto-generated by Gateway. The protocol is the same.

---

## Resources

- [AgentCore Gateway Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)
- [Open-Meteo API](https://open-meteo.com/en/docs)
- [MCPClient (Strands)](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/tools/mcp-client/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
