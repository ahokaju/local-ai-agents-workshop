"""
Kata 13: AgentCore Gateway - Starter Template

Complete the TODOs to register a REST API as MCP-compatible tools using
AgentCore Gateway — without writing an MCP server manually. Then connect a
Strands agent via MCPClient to use those tools.

How credential injection works:
    Gateway's openApiSchema targets require credentials (OAUTH or API_KEY).
    We store a placeholder in Secrets Manager; the Gateway injects it as a
    request header. Open-Meteo is a public API that ignores unknown headers —
    in production you would store a real API key here.

Prerequisites:
    pip install 'strands-agents[bedrock]' bedrock-agentcore boto3 python-dotenv
    export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
    export AWS_REGION=us-east-1   (must match the region your key was created in)

    Optional: set GATEWAY_ROLE_ARN to reuse an existing IAM role for the gateway.
    If not set, a minimal role is created automatically and deleted after the run.
"""

import json
import os
import time

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
# TODO 1: Import the following:
#   from mcp.client.streamable_http import streamablehttp_client
#   from strands import Agent
#   from strands.models.bedrock import BedrockModel
#   from strands.tools.mcp import MCPClient

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DEFAULT_MODEL = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
GATEWAY_NAME = "kata13-weather-gateway"
GATEWAY_ROLE_NAME = "kata13-agentcore-gateway-role"
SECRET_NAME = "kata13-open-meteo-api-key"
STATE_FILE = os.path.join(os.path.dirname(__file__), "kata13_state.json")

# OpenAPI spec describing the Open-Meteo forecast endpoint
OPEN_METEO_SPEC = json.dumps({
    "openapi": "3.0.0",
    "info": {"title": "Open-Meteo Weather API", "version": "1.0.0"},
    "servers": [{"url": "https://api.open-meteo.com"}],
    "paths": {
        "/v1/forecast": {
            "get": {
                "operationId": "GetWeatherForecast",
                "summary": "Get weather forecast for a location",
                "description": "Get current weather and forecast. Required: latitude and longitude.",
                "parameters": [
                    {"name": "latitude", "in": "query", "required": True,
                     "schema": {"type": "number"}, "description": "Latitude (e.g., 60.1699 for Helsinki)"},
                    {"name": "longitude", "in": "query", "required": True,
                     "schema": {"type": "number"}, "description": "Longitude (e.g., 24.9384 for Helsinki)"},
                    {"name": "current_weather", "in": "query", "required": False,
                     "schema": {"type": "boolean"}, "description": "Include current weather conditions"},
                    {"name": "hourly", "in": "query", "required": False,
                     "schema": {"type": "string"}, "description": "Comma-separated hourly variables"},
                ],
                "responses": {
                    "200": {"description": "Weather data",
                            "content": {"application/json": {"schema": {"type": "object"}}}}
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
    TODO = '\033[91m'
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
    @classmethod
    def todo(cls, text): return f"{cls.TODO}{text}{cls.RESET}"


# ==============================================================================
# TODO 2: Get or create the IAM role for the Gateway
# ==============================================================================

def get_or_create_gateway_role() -> tuple[str, str | None]:
    """Return (role_arn, role_name_if_created_else_None).

    Steps:
        1. Check os.getenv("GATEWAY_ROLE_ARN") — if set, return (arn, None)
        2. Otherwise use boto3.client("iam") to create a role named GATEWAY_ROLE_NAME
           with trust policy allowing bedrock-agentcore.amazonaws.com to assume it
        3. Handle EntityAlreadyExistsException by fetching the existing role ARN
        4. Return (role_arn, GATEWAY_ROLE_NAME)
    """
    # TODO 2: Implement get_or_create_gateway_role()
    # env_arn = os.getenv("GATEWAY_ROLE_ARN")
    # if env_arn:
    #     return env_arn, None
    #
    # iam = boto3.client("iam")
    # trust_policy = json.dumps({
    #     "Version": "2012-10-17",
    #     "Statement": [{"Effect": "Allow",
    #                    "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
    #                    "Action": "sts:AssumeRole"}]
    # })
    # try:
    #     resp = iam.create_role(RoleName=GATEWAY_ROLE_NAME,
    #                            AssumeRolePolicyDocument=trust_policy,
    #                            Description="Auto-created IAM role for kata-13 gateway")
    #     return resp["Role"]["Arn"], GATEWAY_ROLE_NAME
    # except iam.exceptions.EntityAlreadyExistsException:
    #     resp = iam.get_role(RoleName=GATEWAY_ROLE_NAME)
    #     return resp["Role"]["Arn"], GATEWAY_ROLE_NAME

    print(Colors.todo("TODO 2: Implement get_or_create_gateway_role()"))
    return "TODO-role-arn", None


# ==============================================================================
# TODO 3: Create Secrets Manager secret for API key credential injection
# ==============================================================================

def create_api_key_secret(role_name: str | None) -> tuple[str, bool]:
    """Store a placeholder API key in Secrets Manager and grant the gateway role read access.

    Gateway's openApiSchema targets require API_KEY or OAUTH credentials.
    We store a placeholder here; the Gateway injects it as a header.

    Steps:
        1. Use boto3.client("secretsmanager") to create_secret with:
               Name=SECRET_NAME, SecretString="open-meteo-no-auth-needed"
           Handle ResourceExistsException by calling describe_secret instead.
        2. If role_name is set, use boto3.client("iam") to put_role_policy granting
               secretsmanager:GetSecretValue on the secret ARN
        3. Return (secret_arn, created: bool)
    """
    # TODO 3: Implement create_api_key_secret()
    # sm = boto3.client("secretsmanager", region_name=AWS_REGION)
    # try:
    #     resp = sm.create_secret(Name=SECRET_NAME,
    #                             SecretString="open-meteo-no-auth-needed",
    #                             Description="Placeholder for kata-13 gateway")
    #     secret_arn, created = resp["ARN"], True
    # except sm.exceptions.ResourceExistsException:
    #     resp = sm.describe_secret(SecretId=SECRET_NAME)
    #     secret_arn, created = resp["ARN"], False
    #
    # if role_name:
    #     iam = boto3.client("iam")
    #     iam.put_role_policy(
    #         RoleName=role_name,
    #         PolicyName="kata13-secret-read",
    #         PolicyDocument=json.dumps({
    #             "Version": "2012-10-17",
    #             "Statement": [{"Effect": "Allow",
    #                            "Action": "secretsmanager:GetSecretValue",
    #                            "Resource": secret_arn}]
    #         })
    #     )
    # return secret_arn, created

    print(Colors.todo("TODO 3: Implement create_api_key_secret()"))
    return "TODO-secret-arn", False


# ==============================================================================
# TODO 4: Create Gateway with MCP protocol and wait for READY
# ==============================================================================

def create_gateway(control_client, role_arn: str) -> tuple[str, str]:
    """Create an AgentCore Gateway and poll until status is READY.

    Steps:
        1. Call control_client.create_gateway() with:
               name=GATEWAY_NAME, protocolType="MCP",
               authorizerType="NONE", roleArn=role_arn
        2. Extract gateway_id from response["gatewayId"]
        3. Extract gateway_url from response["gatewayUrl"]   ← note: top-level key, NOT response["mcp"]["url"]
        4. Poll control_client.get_gateway(gatewayIdentifier=gateway_id)["status"]
           until "READY" (sleep 5 s between polls)
        5. Return (gateway_id, gateway_url)
    """
    # TODO 4: Implement create_gateway()
    # response = control_client.create_gateway(
    #     name=GATEWAY_NAME,
    #     description="Exposes Open-Meteo weather API as MCP tools",
    #     protocolType="MCP",
    #     authorizerType="NONE",
    #     roleArn=role_arn,
    # )
    # gateway_id = response["gatewayId"]
    # gateway_url = response["gatewayUrl"]   # top-level key
    # while True:
    #     status = control_client.get_gateway(gatewayIdentifier=gateway_id)["status"]
    #     if status == "READY":
    #         break
    #     if status == "FAILED":
    #         raise RuntimeError("Gateway entered FAILED state")
    #     time.sleep(5)
    # return gateway_id, gateway_url

    print(Colors.todo("TODO 4: Implement create_gateway()"))
    return "TODO-gateway-id", "http://TODO-gateway-url"


# ==============================================================================
# TODO 5: Register the Open-Meteo API as a gateway target
# ==============================================================================

def register_weather_target(control_client, gateway_id: str, secret_arn: str) -> str:
    """Register the Open-Meteo API using an OpenAPI schema + API_KEY credentials.

    Steps:
        1. Call control_client.create_gateway_target() with:
               gatewayIdentifier=gateway_id
               name="OpenMeteoWeather"
               targetConfiguration={"mcp": {"openApiSchema": {"inlinePayload": OPEN_METEO_SPEC}}}
               credentialProviderConfigurations=[{
                   "credentialProviderType": "API_KEY",
                   "credentialProvider": {
                       "apiKeyCredentialProvider": {
                           "providerArn": secret_arn,
                           "credentialParameterName": "X-Api-Key",
                           "credentialLocation": "HEADER"
                       }
                   }
               }]
        2. Return response["targetId"]

    Note: openApiSchema targets require OAUTH or API_KEY credentials — GATEWAY_IAM_ROLE
    is NOT supported for this target type.
    """
    # TODO 5: Implement register_weather_target()
    # response = control_client.create_gateway_target(
    #     gatewayIdentifier=gateway_id,
    #     name="OpenMeteoWeather",
    #     description="Open-Meteo public weather forecast API",
    #     targetConfiguration={
    #         "mcp": {"openApiSchema": {"inlinePayload": OPEN_METEO_SPEC}}
    #     },
    #     credentialProviderConfigurations=[{
    #         "credentialProviderType": "API_KEY",
    #         "credentialProvider": {
    #             "apiKeyCredentialProvider": {
    #                 "providerArn": secret_arn,
    #                 "credentialParameterName": "X-Api-Key",
    #                 "credentialLocation": "HEADER"
    #             }
    #         }
    #     }],
    # )
    # return response["targetId"]

    print(Colors.todo("TODO 5: Implement register_weather_target()"))
    return "TODO-target-id"


# ==============================================================================
# TODO 6: Connect Strands agent to Gateway via MCPClient
# ==============================================================================

def run_weather_agent(gateway_url: str) -> None:
    """Connect a Strands agent to the Gateway via MCPClient and answer weather questions.

    Steps:
        1. Open MCPClient(lambda: streamablehttp_client(gateway_url)) as context manager
           Note: MCPClient expects a CALLABLE, not a dict config.
        2. Call mcp.list_tools_sync() — returns MCPAgentTool objects
        3. Print tool names using t.tool_name (NOT t.name)
        4. Create BedrockModel and Agent with the discovered tools
        5. Ask at least one weather question
    """
    # TODO 6: Implement run_weather_agent()
    # with MCPClient(lambda: streamablehttp_client(gateway_url)) as mcp:
    #     tools = mcp.list_tools_sync()
    #     print(f"Gateway exposed {len(tools)} tool(s): {[t.tool_name for t in tools]}")
    #     model = BedrockModel(model_id=DEFAULT_MODEL, region_name=AWS_REGION, max_tokens=1024)
    #     agent = Agent(model=model, tools=tools,
    #                   system_prompt="You are a weather assistant. Use tools for real data. "
    #                                 "Helsinki: lat=60.1699, lon=24.9384.")
    #     response = agent("What's the current temperature in Helsinki, Finland?")
    #     print(response)

    print(Colors.todo("TODO 6: Implement run_weather_agent()"))


# ==============================================================================
# Helper: Cleanup (provided — no need to modify)
# ==============================================================================

def cleanup_gateway(control_client, gateway_id: str) -> None:
    """Delete the gateway and its targets, polling for READY state first."""
    print(Colors.stats(f"Cleaning up gateway {gateway_id}..."))
    # Poll until deletable
    for _ in range(12):
        status = control_client.get_gateway(gatewayIdentifier=gateway_id).get("status")
        if status in ("READY", "FAILED"):
            break
        print(Colors.stats(f"  Status: {status} — waiting..."))
        time.sleep(5)
    try:
        targets = control_client.list_gateway_targets(gatewayIdentifier=gateway_id)
        for target in targets.get("items", []):
            control_client.delete_gateway_target(
                gatewayIdentifier=gateway_id,
                targetId=target["targetId"]   # use targetId, NOT targetIdentifier
            )
        time.sleep(3)  # allow target deletion to propagate
        control_client.delete_gateway(gatewayIdentifier=gateway_id)
        print(Colors.stats(f"  Gateway deleted: {gateway_id}"))
    except ClientError as e:
        print(f"  Warning during cleanup: {e}")


def cleanup_iam_role(role_name: str) -> None:
    """Delete the auto-created IAM role."""
    if not role_name:
        return
    iam = boto3.client("iam")
    try:
        for policy_name in iam.list_role_policies(RoleName=role_name).get("PolicyNames", []):
            iam.delete_role_policy(RoleName=role_name, PolicyName=policy_name)
        iam.delete_role(RoleName=role_name)
        print(Colors.stats(f"  Deleted IAM role: {role_name}"))
    except ClientError as e:
        print(f"  Warning during role cleanup: {e}")


def cleanup_secret(secret_arn: str) -> None:
    """Delete the auto-created Secrets Manager secret."""
    if not secret_arn:
        return
    sm = boto3.client("secretsmanager", region_name=AWS_REGION)
    try:
        sm.delete_secret(SecretId=secret_arn, ForceDeleteWithoutRecovery=True)
        print(Colors.stats(f"  Deleted secret"))
    except ClientError as e:
        print(f"  Warning during secret cleanup: {e}")


# ==============================================================================
# Main
# ==============================================================================

def main():
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 13: AgentCore Gateway"))
    print(Colors.header(f" Region: {AWS_REGION}  |  Model: {DEFAULT_MODEL}"))
    print(Colors.header("=" * 70))
    print(Colors.stats("\nCompare with kata-07: Gateway auto-generates the MCP server;"))
    print(Colors.stats("kata-07 required manually writing mcp_server.py.\n"))

    # TODO 7: Create boto3 'bedrock-agentcore-control' client
    # control_client = boto3.client("bedrock-agentcore-control", region_name=AWS_REGION)
    print(Colors.todo("TODO 7: Create the bedrock-agentcore-control boto3 client"))
    control_client = None

    gateway_id = None
    role_name_created = None
    secret_arn = None
    secret_created = False

    try:
        print(Colors.header("0a. IAM role for Gateway"))
        print("-" * 40)
        role_arn, role_name_created = get_or_create_gateway_role()

        print(Colors.header("\n0b. Secrets Manager secret (API key placeholder)"))
        print("-" * 40)
        secret_arn, secret_created = create_api_key_secret(role_name_created)

        print(Colors.header("\n1. Creating AgentCore Gateway (MCP protocol)"))
        print("-" * 40)
        if control_client and role_arn != "TODO-role-arn":
            gateway_id, gateway_url = create_gateway(control_client, role_arn)
        else:
            gateway_id, gateway_url = create_gateway(None, role_arn)

        # Save state so cleanup.py can recover if the script crashes
        if gateway_id and gateway_id != "TODO-gateway-id":
            state = {
                "gateway_id": gateway_id, "gateway_name": GATEWAY_NAME,
                "region": AWS_REGION, "role_name": role_name_created,
                "secret_arn": secret_arn if secret_created else None,
            }
            with open(STATE_FILE, "w") as f:
                json.dump(state, f, indent=2)

        print(Colors.header("\n2. Registering weather API as gateway target"))
        print("-" * 40)
        if control_client and gateway_id != "TODO-gateway-id" and secret_arn != "TODO-secret-arn":
            target_id = register_weather_target(control_client, gateway_id, secret_arn)
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE) as f:
                    state = json.load(f)
                state["target_id"] = target_id
                with open(STATE_FILE, "w") as f:
                    json.dump(state, f, indent=2)
        else:
            register_weather_target(None, gateway_id, secret_arn)

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
        print(Colors.header("\n4. Cleanup"))
        print("-" * 40)
        if control_client and gateway_id and gateway_id != "TODO-gateway-id":
            cleanup_gateway(control_client, gateway_id)
        if role_name_created:
            cleanup_iam_role(role_name_created)
        if secret_created and secret_arn:
            cleanup_secret(secret_arn)
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 13 Complete!"))
    print(Colors.header("=" * 70))


if __name__ == "__main__":
    main()
