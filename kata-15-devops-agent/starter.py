"""
Kata 15: AWS DevOps Agent — Custom MCP Integration - Starter Template

Complete the TODOs to:
  1. Add the MCP tools to mcp_server.py (open that file and complete the @mcp.tool() functions)
  2. Inspect DevOps Agent AgentSpaces using the boto3 client
  3. Trigger a test incident via the webhook endpoint

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

    # 4. In a separate terminal: start your MCP server
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

# DevOps Agent preview service endpoint
DEVOPS_AGENT_ENDPOINT = "https://api.prod.cp.aidevops.us-east-1.api.aws"


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[96m'
    STATS = '\033[95m'
    TODO = '\033[91m'
    RESPONSE = '\033[92m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    @classmethod
    def header(cls, text): return f"{cls.BOLD}{cls.HEADER}{text}{cls.RESET}"
    @classmethod
    def stats(cls, text): return f"{cls.STATS}{text}{cls.RESET}"
    @classmethod
    def todo(cls, text): return f"{cls.TODO}{text}{cls.RESET}"
    @classmethod
    def response(cls, text): return f"{cls.RESPONSE}{text}{cls.RESET}"


# ==============================================================================
# TODO 1: Create the devopsagent boto3 client
# ==============================================================================

def make_client() -> object:
    """Create the devopsagent boto3 client with the custom endpoint URL.

    Steps:
        1. Call boto3.client() with:
               service_name="devopsagent"
               region_name=AWS_REGION
               endpoint_url=DEVOPS_AGENT_ENDPOINT
        2. Return the client

    Note: If you get "Unknown service", add the service model with:
        aws configure add-model --service-model file://devopsagent.json \
                                --service-name devopsagent
    """
    # TODO 1: Implement make_client()
    # return boto3.client(
    #     "devopsagent",
    #     region_name=AWS_REGION,
    #     endpoint_url=DEVOPS_AGENT_ENDPOINT
    # )

    print(Colors.todo("TODO 1: Implement make_client()"))
    return None


# ==============================================================================
# TODO 2: List AgentSpaces
# ==============================================================================

def list_agent_spaces(client) -> list[dict]:
    """List all DevOps Agent spaces in the account.

    Steps:
        1. Call client.list_agent_spaces()
        2. Extract the "agentSpaces" list from the response
        3. Print each space's name and agentSpaceId
        4. Return the list

    AgentSpace fields: agentSpaceId, name, status, createdAt, updatedAt
    """
    # TODO 2: Implement list_agent_spaces()
    # response = client.list_agent_spaces()
    # spaces = response.get("agentSpaces", [])
    # for space in spaces:
    #     print(Colors.stats(f"  - {space['name']} (ID: {space['agentSpaceId']})"))
    # return spaces

    print(Colors.todo("TODO 2: Implement list_agent_spaces()"))
    return []


# ==============================================================================
# TODO 3: Inspect an AgentSpace and its associations
# ==============================================================================

def inspect_agent_space(client, space_id: str) -> None:
    """Get details and associated services for an AgentSpace.

    Steps:
        1. Call client.get_agent_space(agentSpaceId=space_id)
           Print: name, status
        2. Call client.list_associations(agentSpaceId=space_id)
           Print: each association's serviceType and serviceId
        3. For MCP server associations, print the endpoint URL from
           association["configuration"]["mcpserver"]["endpoint"]
    """
    # TODO 3: Implement inspect_agent_space()
    # details = client.get_agent_space(agentSpaceId=space_id)
    # print(Colors.stats(f"  Name:   {details.get('name')}"))
    # print(Colors.stats(f"  Status: {details.get('status')}"))
    #
    # assocs = client.list_associations(agentSpaceId=space_id)
    # for a in assocs.get("associations", []):
    #     print(Colors.stats(f"  - {a.get('serviceType')}: {a.get('serviceId')}"))
    #     if "mcpserver" in a.get("configuration", {}):
    #         endpoint = a["configuration"]["mcpserver"].get("endpoint")
    #         print(Colors.stats(f"    MCP endpoint: {endpoint}"))

    print(Colors.todo("TODO 3: Implement inspect_agent_space()"))


# ==============================================================================
# TODO 4: Trigger a test incident via webhook
# ==============================================================================

def trigger_test_incident(webhook_id: str, webhook_secret: str) -> None:
    """Send a test incident payload to the DevOps Agent webhook endpoint.

    Steps:
        1. Build the webhook URL:
               f"https://event-ai.us-east-1.api.aws/webhook/generic/{webhook_id}"
        2. Create a payload dict with:
               eventType="incident", incidentId="kata15-test-001",
               action="created", priority="HIGH",
               title="High latency on payment-api",
               description="P99 latency exceeded 5s for 10+ minutes.",
               timestamp="2025-01-01T12:00:00Z", service="payment-api"
        3. HMAC-SHA256 sign the JSON body:
               body = json.dumps(payload).encode()
               sig = hmac.new(webhook_secret.encode(), body, hashlib.sha256).digest()
               signature = base64.b64encode(sig).decode()
        4. POST with headers:
               "Content-Type": "application/json"
               "x-amzn-event-signature": signature
        5. Print the response status code
    """
    # TODO 4: Implement trigger_test_incident()
    # webhook_url = f"https://event-ai.us-east-1.api.aws/webhook/generic/{webhook_id}"
    # payload = {
    #     "eventType": "incident",
    #     "incidentId": "kata15-test-001",
    #     "action": "created",
    #     "priority": "HIGH",
    #     "title": "High latency on payment-api",
    #     "description": "P99 latency exceeded 5s for 10+ minutes on payment-api.",
    #     "timestamp": "2025-01-01T12:00:00Z",
    #     "service": "payment-api"
    # }
    # body = json.dumps(payload).encode()
    # sig = hmac.new(webhook_secret.encode(), body, hashlib.sha256).digest()
    # signature = base64.b64encode(sig).decode()
    # response = requests.post(
    #     webhook_url, data=body,
    #     headers={"Content-Type": "application/json",
    #              "x-amzn-event-signature": signature},
    #     timeout=10
    # )
    # print(Colors.stats(f"  Status: {response.status_code}"))

    print(Colors.todo("TODO 4: Implement trigger_test_incident()"))


# ==============================================================================
# Main
# ==============================================================================

def main():
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 15: AWS DevOps Agent"))
    print(Colors.header(f" Region: {AWS_REGION}"))
    print(Colors.header("=" * 70))

    try:
        # TODO 1: Create the devopsagent client
        client = make_client()

        # TODO 2: List AgentSpaces
        print(Colors.header("1. Listing AgentSpaces"))
        print("-" * 40)
        if client:
            spaces = list_agent_spaces(client)
        else:
            spaces = []
            print(Colors.stats("  (Skipping — client not created)"))

        # TODO 3: Inspect the configured AgentSpace
        space_id = AGENT_SPACE_ID or (spaces[0]["agentSpaceId"] if spaces else None)
        if client and space_id:
            print(Colors.header(f"\n2. AgentSpace details: {space_id}"))
            print("-" * 40)
            inspect_agent_space(client, space_id)
        else:
            print(Colors.header("\n2. Skipping — no AgentSpace ID"))
            print(Colors.stats("  Set DEVOPS_AGENT_SPACE_ID to inspect a space"))

        # Step 3: Check MCP server is running
        print(Colors.header("\n3. MCP Server Status"))
        print("-" * 40)
        mcp_port = int(os.getenv("MCP_PORT", 8001))
        try:
            import urllib.request
            urllib.request.urlopen(f"http://localhost:{mcp_port}/health", timeout=2)
            print(Colors.stats(f"  MCP server is running on port {mcp_port}"))
        except Exception:
            print(Colors.stats(f"  MCP server not detected on port {mcp_port}"))
            print(Colors.stats("  Start it with: python mcp_server.py"))

        # TODO 4: Trigger test incident
        print(Colors.header("\n4. Webhook Incident Trigger"))
        print("-" * 40)
        if WEBHOOK_ID and WEBHOOK_SECRET:
            trigger_test_incident(WEBHOOK_ID, WEBHOOK_SECRET)
        else:
            print(Colors.stats("  Skipping — DEVOPS_AGENT_WEBHOOK_ID / DEVOPS_AGENT_WEBHOOK_SECRET not set"))
            print(Colors.stats("  Create a webhook in the AgentSpace console to enable this."))

    except NoCredentialsError:
        print("\nError: AWS credentials not configured.")
    except ClientError as e:
        if "UnknownServiceError" in str(e):
            print("\nError: devopsagent service model not found.")
            print("  curl -o devopsagent.json https://d1co8nkiwcta1g.cloudfront.net/devopsagent.json")
            print("  aws configure add-model --service-model file://devopsagent.json \\")
            print("                          --service-name devopsagent")
        else:
            print(f"\nAWS error: {e}")

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 15 Complete!"))
    print(Colors.header("=" * 70))


if __name__ == "__main__":
    main()
