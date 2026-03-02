"""
Kata 13: AgentCore Gateway - Solution

Register a REST API as MCP-compatible tools using AgentCore Gateway — without
writing an MCP server manually. A Strands agent connects via MCPClient and
automatically discovers and uses the exposed tools.

How credential injection works:
    The Gateway requires credentials for openApiSchema targets. We store a
    placeholder in Secrets Manager; the Gateway injects it as a header.
    Open-Meteo is a public API that ignores unknown headers — in production
    you would store a real API key here.

Prerequisites:
    pip install 'strands-agents[bedrock]' bedrock-agentcore boto3 python-dotenv
    export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
    export AWS_REGION=us-east-1   (must match the region your key was created in)

    To use eu-central-1: set AWS_REGION=eu-central-1 and change DEFAULT_MODEL
    prefix from "us." to "eu.".

    Optional: set GATEWAY_ROLE_ARN to reuse an existing IAM role for the gateway.
    If not set, a minimal role is created automatically and deleted after the run.
"""

import json
import os
import time

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.tools.mcp import MCPClient

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DEFAULT_MODEL = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
GATEWAY_NAME = "kata13-weather-gateway"
GATEWAY_ROLE_NAME = "kata13-agentcore-gateway-role"
SECRET_NAME = "kata13-open-meteo-api-key"
STATE_FILE = os.path.join(os.path.dirname(__file__), "kata13_state.json")

# Minimal OpenAPI spec for the Open-Meteo forecast endpoint
OPEN_METEO_SPEC = json.dumps({
    "openapi": "3.0.0",
    "info": {"title": "Open-Meteo Weather API", "version": "1.0.0"},
    "servers": [{"url": "https://api.open-meteo.com"}],
    "paths": {
        "/v1/forecast": {
            "get": {
                "operationId": "GetWeatherForecast",
                "summary": "Get weather forecast for a location",
                "description": (
                    "Get current weather and short-term forecast. "
                    "Required: latitude and longitude coordinates."
                ),
                "parameters": [
                    {
                        "name": "latitude",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "number"},
                        "description": "Latitude of the location (e.g., 60.1699 for Helsinki)"
                    },
                    {
                        "name": "longitude",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "number"},
                        "description": "Longitude of the location (e.g., 24.9384 for Helsinki)"
                    },
                    {
                        "name": "current_weather",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "boolean"},
                        "description": "Include current weather conditions"
                    },
                    {
                        "name": "hourly",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "string"},
                        "description": "Comma-separated hourly variables (e.g., temperature_2m)"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Weather forecast data",
                        "content": {"application/json": {"schema": {"type": "object"}}}
                    }
                }
            }
        }
    }
})


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for pretty terminal output."""
    HEADER = '\033[96m'
    PROMPT = '\033[93m'
    RESPONSE = '\033[92m'
    STATS = '\033[95m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    @classmethod
    def header(cls, text): return f"{cls.BOLD}{cls.HEADER}{text}{cls.RESET}"
    @classmethod
    def prompt(cls, text): return f"{cls.PROMPT}{text}{cls.RESET}"
    @classmethod
    def response(cls, text): return f"{cls.RESPONSE}{text}{cls.RESET}"
    @classmethod
    def stats(cls, text): return f"{cls.STATS}{text}{cls.RESET}"


# ==============================================================================
# Step 0a: IAM role for the Gateway
# ==============================================================================

def get_or_create_gateway_role() -> tuple[str, str | None]:
    """Return (role_arn, role_name_if_created_else_None).

    Checks GATEWAY_ROLE_ARN env var first; otherwise creates a minimal role.
    """
    env_arn = os.getenv("GATEWAY_ROLE_ARN")
    if env_arn:
        print(Colors.stats(f"Using existing role from GATEWAY_ROLE_ARN: {env_arn}"))
        return env_arn, None

    iam = boto3.client("iam")
    trust_policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    })

    try:
        resp = iam.create_role(
            RoleName=GATEWAY_ROLE_NAME,
            AssumeRolePolicyDocument=trust_policy,
            Description="Auto-created IAM role for kata-13 AgentCore Gateway"
        )
        role_arn = resp["Role"]["Arn"]
        print(Colors.stats(f"Created IAM role: {role_arn}"))
        return role_arn, GATEWAY_ROLE_NAME
    except iam.exceptions.EntityAlreadyExistsException:
        resp = iam.get_role(RoleName=GATEWAY_ROLE_NAME)
        role_arn = resp["Role"]["Arn"]
        print(Colors.stats(f"Reusing existing role: {role_arn}"))
        return role_arn, GATEWAY_ROLE_NAME


# ==============================================================================
# Step 0b: Secrets Manager secret for API key credential injection
# ==============================================================================

def create_api_key_secret(role_name: str | None) -> tuple[str, bool]:
    """Create a Secrets Manager secret and grant the gateway role read access.

    The openApiSchema target type requires OAUTH or API_KEY credentials.
    We store a placeholder here; the Gateway injects it as a header.
    Open-Meteo is public and ignores unknown headers — in production you
    would store a real API key.

    Returns:
        (secret_arn, created: bool)
    """
    sm = boto3.client("secretsmanager", region_name=AWS_REGION)

    try:
        resp = sm.create_secret(
            Name=SECRET_NAME,
            SecretString="open-meteo-no-auth-needed",
            Description="Placeholder API key for kata-13 AgentCore Gateway (Open-Meteo is public)"
        )
        secret_arn = resp["ARN"]
        print(Colors.stats(f"Created secret: {secret_arn}"))
        created = True
    except sm.exceptions.ResourceExistsException:
        resp = sm.describe_secret(SecretId=SECRET_NAME)
        secret_arn = resp["ARN"]
        print(Colors.stats(f"Reusing existing secret: {secret_arn}"))
        created = False

    # Allow the gateway role to read the secret
    if role_name:
        iam = boto3.client("iam")
        policy = json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": "secretsmanager:GetSecretValue",
                "Resource": secret_arn
            }]
        })
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName="kata13-secret-read",
            PolicyDocument=policy
        )
        print(Colors.stats(f"Granted role {role_name} access to secret"))

    return secret_arn, created


# ==============================================================================
# Step 1: Create Gateway and wait for READY
# ==============================================================================

def create_gateway(control_client, role_arn: str) -> tuple[str, str]:
    """Create an AgentCore Gateway with MCP protocol and wait until READY.

    Returns:
        (gateway_id, gateway_url)
    """
    print(Colors.stats(f"Creating Gateway: {GATEWAY_NAME}"))
    response = control_client.create_gateway(
        name=GATEWAY_NAME,
        description="Exposes the Open-Meteo weather API as MCP-compatible tools",
        protocolType="MCP",
        authorizerType="NONE",
        roleArn=role_arn,
    )
    gateway_id = response["gatewayId"]
    gateway_url = response["gatewayUrl"]
    print(Colors.stats(f"Gateway ID:  {gateway_id}"))
    print(Colors.stats(f"Gateway URL: {gateway_url}"))

    # Poll until READY
    print(Colors.stats("Waiting for gateway to become READY "), end="", flush=True)
    while True:
        status = control_client.get_gateway(gatewayIdentifier=gateway_id)["status"]
        print(Colors.stats(f"[{status}]"), end=" ", flush=True)
        if status == "READY":
            break
        if status == "FAILED":
            raise RuntimeError("Gateway entered FAILED state")
        time.sleep(5)
    print()

    return gateway_id, gateway_url


# ==============================================================================
# Step 2: Register API target using OpenAPI schema + API key credentials
# ==============================================================================

def register_weather_target(control_client, gateway_id: str, secret_arn: str) -> str:
    """Register the Open-Meteo forecast API as a gateway target.

    Uses openApiSchema with API_KEY credential injection (required by the API).

    Returns:
        target_id
    """
    print(Colors.stats("Registering Open-Meteo weather API as gateway target..."))
    response = control_client.create_gateway_target(
        gatewayIdentifier=gateway_id,
        name="OpenMeteoWeather",
        description="Open-Meteo public weather forecast API",
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
    print(Colors.stats(f"Target ID: {target_id}"))
    return target_id


# ==============================================================================
# Step 3: Connect agent via MCPClient and run queries
# ==============================================================================

def run_weather_agent(gateway_url: str) -> None:
    """Connect a Strands agent to the Gateway via MCPClient and answer weather questions."""
    print(Colors.stats("\nConnecting to Gateway via MCPClient..."))

    with MCPClient(lambda: streamablehttp_client(gateway_url)) as mcp:
        tools = mcp.list_tools_sync()
        print(Colors.stats(f"Gateway exposed {len(tools)} tool(s): {[t.tool_name for t in tools]}"))

        model = BedrockModel(
            model_id=DEFAULT_MODEL,
            region_name=AWS_REGION,
            max_tokens=1024,
        )
        agent = Agent(
            model=model,
            tools=tools,
            system_prompt=(
                "You are a weather assistant. Use the available tools to get "
                "real weather data. Provide helpful, conversational answers. "
                "Helsinki coordinates: lat=60.1699, lon=24.9384. "
                "Berlin coordinates: lat=52.5200, lon=13.4050."
            )
        )

        questions = [
            "What's the current temperature in Helsinki, Finland?",
            "How does the weather in Berlin compare to Helsinki right now?",
        ]

        for question in questions:
            print(Colors.prompt(f"\nUser: {question}"))
            response = agent(question)
            print(Colors.response(f"Agent: {response}"))


# ==============================================================================
# Step 4: Cleanup
# ==============================================================================

def cleanup_gateway(control_client, gateway_id: str) -> bool:
    """Delete the gateway and its targets. Returns True on success."""
    print(Colors.stats(f"Cleaning up gateway {gateway_id}..."))

    # Poll until deletable
    for _ in range(12):
        status = control_client.get_gateway(gatewayIdentifier=gateway_id).get("status")
        if status in ("READY", "FAILED"):
            break
        print(Colors.stats(f"  Gateway status: {status} — waiting..."))
        time.sleep(5)

    try:
        targets = control_client.list_gateway_targets(gatewayIdentifier=gateway_id)
        for target in targets.get("items", []):
            control_client.delete_gateway_target(
                gatewayIdentifier=gateway_id,
                targetId=target["targetId"]
            )
            print(Colors.stats(f"  Deleted target: {target['targetId']}"))
        time.sleep(3)  # allow target deletion to propagate before deleting gateway

        control_client.delete_gateway(gatewayIdentifier=gateway_id)
        print(Colors.stats(f"  Deleted gateway: {gateway_id}"))
        return True
    except ClientError as e:
        print(f"  Warning during gateway cleanup: {e}")
        return False


def cleanup_iam_role(role_name: str) -> None:
    """Delete the auto-created IAM role."""
    iam = boto3.client("iam")
    try:
        for policy_name in iam.list_role_policies(RoleName=role_name).get("PolicyNames", []):
            iam.delete_role_policy(RoleName=role_name, PolicyName=policy_name)
        iam.delete_role(RoleName=role_name)
        print(Colors.stats(f"  Deleted IAM role: {role_name}"))
    except ClientError as e:
        print(f"  Warning during role cleanup: {e}")


def cleanup_secret(secret_arn: str) -> None:
    """Delete the Secrets Manager secret (no recovery window for workshop use)."""
    sm = boto3.client("secretsmanager", region_name=AWS_REGION)
    try:
        sm.delete_secret(SecretId=secret_arn, ForceDeleteWithoutRecovery=True)
        print(Colors.stats(f"  Deleted secret: {SECRET_NAME}"))
    except ClientError as e:
        print(f"  Warning during secret cleanup: {e}")


# ==============================================================================
# Main
# ==============================================================================

def main():
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 13: AgentCore Gateway - Solution"))
    print(Colors.header(f" Region: {AWS_REGION}  |  Model: {DEFAULT_MODEL}"))
    print(Colors.header("=" * 70))
    print(Colors.stats("\nCompare with kata-07: Gateway auto-generates the MCP server;"))
    print(Colors.stats("kata-07 required manually writing mcp_server.py.\n"))

    control_client = boto3.client("bedrock-agentcore-control", region_name=AWS_REGION)
    gateway_id = None
    role_name_created = None
    secret_arn = None
    secret_created = False
    gateway_cleanup_ok = False

    try:
        # Step 0a: IAM role
        print(Colors.header("0a. IAM role for Gateway"))
        print("-" * 40)
        role_arn, role_name_created = get_or_create_gateway_role()

        # Step 0b: Secrets Manager secret for API key credential injection
        print(Colors.header("\n0b. Secrets Manager secret (API key placeholder)"))
        print("-" * 40)
        secret_arn, secret_created = create_api_key_secret(role_name_created)

        # Step 1: Create Gateway
        print(Colors.header("\n1. Creating AgentCore Gateway (MCP protocol)"))
        print("-" * 40)
        gateway_id, gateway_url = create_gateway(control_client, role_arn)

        # Persist state immediately so cleanup.py can recover if the script crashes
        state = {
            "gateway_id": gateway_id,
            "gateway_name": GATEWAY_NAME,
            "region": AWS_REGION,
            "role_name": role_name_created,
            "secret_arn": secret_arn if secret_created else None,
        }
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
        print(Colors.stats(f"State saved to {os.path.basename(STATE_FILE)}"))

        # Step 2: Register Open-Meteo API
        print(Colors.header("\n2. Registering weather API as gateway target"))
        print("-" * 40)
        target_id = register_weather_target(control_client, gateway_id, secret_arn)

        # Update state with target ID
        with open(STATE_FILE) as f:
            state = json.load(f)
        state["target_id"] = target_id
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)

        # Step 3: Agent + MCPClient
        print(Colors.header("\n3. Connecting agent via MCPClient"))
        print("-" * 40)
        run_weather_agent(gateway_url)

    except NoCredentialsError:
        print("\nError: AWS credentials not configured.")
        print("Set AWS_BEARER_TOKEN_BEDROCK and AWS_REGION environment variables.")
    except ClientError as e:
        print(f"\nAWS error: {e}")
        raise
    finally:
        # Step 4: Cleanup
        print(Colors.header("\n4. Cleanup"))
        print("-" * 40)
        if gateway_id:
            gateway_cleanup_ok = cleanup_gateway(control_client, gateway_id)
        if role_name_created:
            cleanup_iam_role(role_name_created)
        if secret_arn and secret_created:
            cleanup_secret(secret_arn)
        if gateway_cleanup_ok and os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
            print(Colors.stats(f"  Removed {os.path.basename(STATE_FILE)}"))
        elif os.path.exists(STATE_FILE):
            print(Colors.stats(f"  State file kept — run cleanup.py to finish"))

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 13 Complete!"))
    print(Colors.header("=" * 70))
    print(Colors.stats("\nKey takeaway: Gateway exposed the Open-Meteo REST API as MCP tools"))
    print(Colors.stats("with zero MCP server code — compare with kata-07's mcp_server.py."))


if __name__ == "__main__":
    main()
