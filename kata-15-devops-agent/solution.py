"""
Kata 15: AWS DevOps Agent — Custom MCP Integration - Solution

This script demonstrates the boto3 DevOps Agent API:
  - List AgentSpaces and their associations
  - Register an MCP server programmatically
  - Trigger a test incident via the webhook endpoint

The MCP server itself (mcp_server.py) must be running separately.

Prerequisites:
    # 1. Download the custom service model (preview service, not in boto3 yet)
    curl -o devopsagent.json \
        "https://d1co8nkiwcta1g.cloudfront.net/devopsagent.json"
    aws configure add-model \
        --service-model file://devopsagent.json \
        --service-name devopsagent

    # 2. Set environment variables
    export AWS_REGION=us-east-1   # DevOps Agent preview is us-east-1 only
    export DEVOPS_AGENT_SPACE_ID=<your-agent-space-id>  # from Part A setup

    # 3. Optional (for webhook test)
    export DEVOPS_AGENT_WEBHOOK_ID=<webhook-id>
    export DEVOPS_AGENT_WEBHOOK_SECRET=<webhook-secret>

    # 4. Start the MCP server in a separate terminal
    python mcp_server.py
"""

import base64
import hashlib
import hmac
import json
import os

import boto3
import requests
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AGENT_SPACE_ID = os.getenv("DEVOPS_AGENT_SPACE_ID", "")
WEBHOOK_ID = os.getenv("DEVOPS_AGENT_WEBHOOK_ID", "")
WEBHOOK_SECRET = os.getenv("DEVOPS_AGENT_WEBHOOK_SECRET", "")

# DevOps Agent preview service endpoint — required because the service
# uses a custom endpoint not in the standard AWS regional endpoint list
DEVOPS_AGENT_ENDPOINT = "https://api.prod.cp.aidevops.us-east-1.api.aws"


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[96m'
    PROMPT = '\033[93m'
    RESPONSE = '\033[92m'
    STATS = '\033[95m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    @classmethod
    def header(cls, text): return f"{cls.BOLD}{cls.HEADER}{text}{cls.RESET}"
    @classmethod
    def stats(cls, text): return f"{cls.STATS}{text}{cls.RESET}"
    @classmethod
    def response(cls, text): return f"{cls.RESPONSE}{text}{cls.RESET}"


def make_client() -> object:
    """Create the devopsagent boto3 client with the custom endpoint URL.

    Note: The devopsagent service model is not built into boto3 yet (preview).
    You must add it via:
        aws configure add-model --service-model file://devopsagent.json \
                                --service-name devopsagent
    """
    return boto3.client(
        "devopsagent",
        region_name=AWS_REGION,
        endpoint_url=DEVOPS_AGENT_ENDPOINT
    )


# ==============================================================================
# Step 1: List AgentSpaces
# ==============================================================================

def list_agent_spaces(client) -> list[dict]:
    """List all DevOps Agent spaces in the account."""
    response = client.list_agent_spaces()
    spaces = response.get("agentSpaces", [])

    if not spaces:
        print(Colors.stats("  No AgentSpaces found."))
        print(Colors.stats("  Create one in the console or with:"))
        print(Colors.stats(f'    aws devopsagent create-agent-space --name "kata-15-agent-space" \\'))
        print(Colors.stats(f'      --endpoint-url "{DEVOPS_AGENT_ENDPOINT}" --region {AWS_REGION}'))
        return []

    print(Colors.stats(f"  Found {len(spaces)} AgentSpace(s):"))
    for space in spaces:
        print(Colors.stats(f"    - {space.get('name', 'N/A')} (ID: {space.get('agentSpaceId', 'N/A')})"))

    return spaces


# ==============================================================================
# Step 2: Get AgentSpace details and associations
# ==============================================================================

def inspect_agent_space(client, space_id: str) -> None:
    """Get details and associated services for an AgentSpace."""
    # Get AgentSpace details
    details = client.get_agent_space(agentSpaceId=space_id)
    print(Colors.stats(f"  Name:   {details.get('name', 'N/A')}"))
    print(Colors.stats(f"  Status: {details.get('status', 'N/A')}"))

    # List associations (AWS account, GitHub, MCP servers, etc.)
    assocs = client.list_associations(agentSpaceId=space_id)
    associations = assocs.get("associations", [])

    if not associations:
        print(Colors.stats("  No associations found."))
        return

    print(Colors.stats(f"\n  Associated services ({len(associations)}):"))
    for a in associations:
        service_id = a.get("serviceId", "N/A")
        service_type = a.get("serviceType", "N/A")
        print(Colors.stats(f"    - {service_type}: {service_id}"))

        # Show MCP server endpoint if present
        config = a.get("configuration", {})
        if "mcpserver" in config:
            endpoint = config["mcpserver"].get("endpoint", "N/A")
            print(Colors.stats(f"      MCP endpoint: {endpoint}"))


# ==============================================================================
# Step 3: Register MCP server (if not already registered via console/CLI)
# ==============================================================================

def register_mcp_server(client, endpoint_url: str, api_key: str) -> str | None:
    """Register the MCP server with DevOps Agent at the account level.

    Returns the serviceId, or None if registration fails.
    Note: After registration, you must also call associate-service to link
    the server to a specific AgentSpace.
    """
    print(Colors.stats(f"  Registering MCP server: {endpoint_url}"))

    response = client.register_service(
        service="mcpserver",
        serviceDetails={
            "mcpserver": {
                "name": "kata15-ops-tools",
                "endpoint": endpoint_url,
                "description": "Internal ops tools: deployments, runbooks, on-call",
                "authorizationConfig": {
                    "apiKey": {
                        "apiKeyHeader": "X-Api-Key",
                        "apiKeyName": "kata15-mcp-key",
                        "apiKeyValue": api_key
                    }
                }
            }
        }
    )

    service_id = response.get("serviceId")
    if service_id:
        print(Colors.stats(f"  Registered. Service ID: {service_id}"))
        print(Colors.stats("  Now associate with your AgentSpace:"))
        print(Colors.stats(f'    aws devopsagent associate-service \\'))
        print(Colors.stats(f'      --agent-space-id {AGENT_SPACE_ID} \\'))
        print(Colors.stats(f'      --service-id {service_id} \\'))
        print(Colors.stats(f'      --configuration \'{{"mcpserver": {{"name": "kata15-ops-tools", "endpoint": "{endpoint_url}"}}}}\'\\'))
        print(Colors.stats(f'      --endpoint-url "{DEVOPS_AGENT_ENDPOINT}" --region {AWS_REGION}'))
    return service_id


# ==============================================================================
# Step 4: Trigger a test incident via webhook (optional)
# ==============================================================================

def trigger_test_incident(webhook_id: str, webhook_secret: str) -> None:
    """Send a test incident payload to the DevOps Agent webhook endpoint.

    DevOps Agent receives the alert and starts an autonomous investigation,
    which may call your MCP tools (get_deployment_history, etc.).

    The webhook uses HMAC-SHA256 signing for authentication.
    """
    webhook_url = f"https://event-ai.us-east-1.api.aws/webhook/generic/{webhook_id}"

    payload = {
        "eventType": "incident",
        "incidentId": "kata15-test-001",
        "action": "created",
        "priority": "HIGH",
        "title": "High latency on payment-api",
        "description": (
            "P99 latency exceeded 5s for 10+ minutes on payment-api. "
            "Error rate is 2.3%. Deployed v2.4.1 two hours ago."
        ),
        "timestamp": "2025-01-01T12:00:00Z",
        "service": "payment-api",
        "data": {
            "metadata": {
                "region": "us-east-1",
                "environment": "production"
            }
        }
    }

    body = json.dumps(payload).encode()

    # HMAC-SHA256 signature (required for HMAC-authenticated webhooks)
    sig = hmac.new(webhook_secret.encode(), body, hashlib.sha256).digest()
    signature = base64.b64encode(sig).decode()

    print(Colors.stats(f"  POST {webhook_url}"))
    response = requests.post(
        webhook_url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-amzn-event-signature": signature
        },
        timeout=10
    )
    print(Colors.stats(f"  Status: {response.status_code}"))

    if response.status_code in (200, 202):
        print(Colors.response("  Incident investigation initiated."))
        print(Colors.response("  DevOps Agent will now investigate and may call your MCP tools."))
        print(Colors.response("  Check the Agent Space console for investigation progress."))
    else:
        print(f"  Response: {response.text[:200]}")


# ==============================================================================
# Main
# ==============================================================================

def main():
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 15: AWS DevOps Agent - Solution"))
    print(Colors.header(f" Region: {AWS_REGION}"))
    print(Colors.header(f" Endpoint: {DEVOPS_AGENT_ENDPOINT}"))
    print(Colors.header("=" * 70))
    print(Colors.stats("\nNote: DevOps Agent uses a custom service model (preview)."))
    print(Colors.stats("If you get 'Unknown service', add the model with:"))
    print(Colors.stats("  curl -o devopsagent.json https://d1co8nkiwcta1g.cloudfront.net/devopsagent.json"))
    print(Colors.stats("  aws configure add-model --service-model file://devopsagent.json \\"))
    print(Colors.stats("                          --service-name devopsagent\n"))

    try:
        client = make_client()

        # Step 1: List AgentSpaces
        print(Colors.header("1. Listing AgentSpaces"))
        print("-" * 40)
        spaces = list_agent_spaces(client)

        # Step 2: Inspect the configured space
        space_id = AGENT_SPACE_ID or (spaces[0]["agentSpaceId"] if spaces else None)
        if space_id:
            print(Colors.header(f"\n2. AgentSpace details: {space_id}"))
            print("-" * 40)
            inspect_agent_space(client, space_id)
        else:
            print(Colors.header("\n2. Skipping — no AgentSpace ID available"))
            print(Colors.stats("  Set DEVOPS_AGENT_SPACE_ID to inspect a specific space"))

        # Step 3: MCP server is running — no registration needed if set up via Part A CLI steps
        print(Colors.header("\n3. MCP Server Status"))
        print("-" * 40)
        mcp_port = int(os.getenv("MCP_PORT", 8001))
        try:
            import urllib.request
            req = urllib.request.urlopen(f"http://localhost:{mcp_port}/health", timeout=2)
            print(Colors.stats(f"  MCP server is running on port {mcp_port}"))
        except Exception:
            print(Colors.stats(f"  MCP server not detected on port {mcp_port}"))
            print(Colors.stats("  Start it with: python mcp_server.py"))

        # Step 4: Trigger test incident (if webhook is configured)
        print(Colors.header("\n4. Webhook Incident Trigger"))
        print("-" * 40)
        if WEBHOOK_ID and WEBHOOK_SECRET:
            trigger_test_incident(WEBHOOK_ID, WEBHOOK_SECRET)
        else:
            print(Colors.stats("  Skipping — DEVOPS_AGENT_WEBHOOK_ID / DEVOPS_AGENT_WEBHOOK_SECRET not set"))
            print(Colors.stats("  To enable: create a webhook in the AgentSpace console, then:"))
            print(Colors.stats("    export DEVOPS_AGENT_WEBHOOK_ID=<id>"))
            print(Colors.stats("    export DEVOPS_AGENT_WEBHOOK_SECRET=<secret>"))

    except NoCredentialsError:
        print("\nError: AWS credentials not configured.")
        print("Set AWS access key, or use AWS_BEARER_TOKEN_BEDROCK + AWS_REGION.")
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "")
        if "UnknownServiceError" in str(e) or code == "UnknownService":
            print("\nError: devopsagent service model not found.")
            print("Add it with:")
            print("  curl -o devopsagent.json https://d1co8nkiwcta1g.cloudfront.net/devopsagent.json")
            print("  aws configure add-model --service-model file://devopsagent.json \\")
            print("                          --service-name devopsagent")
        else:
            print(f"\nAWS error: {e}")

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 15 Complete!"))
    print(Colors.header("=" * 70))
    print(Colors.stats("\nKey takeaway: DevOps Agent calls your MCP tools (not the other way around."))
    print(Colors.stats("The Streamable HTTP transport is what makes this interoperability possible."))


if __name__ == "__main__":
    main()
