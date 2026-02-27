"""
Kata 02: Strands Agents Introduction - Bedrock Starter Template

Complete the TODOs to learn how to build AI agents with Strands backed by
AWS Bedrock instead of the Anthropic API directly.  The demo flow is identical
to starter.py — only the model provider changes.

Prerequisites:
    pip install 'strands-agents[bedrock]' strands-agents-tools boto3 python-dotenv

    Set these environment variables before running:
        AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
        AWS_REGION=eu-central-1   (must match the region your key was created in)

    boto3 picks up both variables automatically — no extra configuration needed.
"""

import os
import time
from dotenv import load_dotenv

load_dotenv()

# Bedrock model IDs
DEFAULT_MODEL = "anthropic.claude-3-haiku-20240307-v1:0"   # Fast, cost-effective
COMPARISON_MODEL = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"  # Higher quality
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Model pricing on Bedrock (per million tokens)
MODEL_PRICING = {
    COMPARISON_MODEL: {"input": 3.00, "output": 15.00, "name": "Sonnet 4.5"},
    DEFAULT_MODEL:    {"input": 0.25, "output": 1.25,  "name": "Haiku 3"},
}


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for pretty terminal output."""
    HEADER = '\033[96m'      # Cyan - step headers
    PROMPT = '\033[93m'      # Yellow - user prompts
    RESPONSE = '\033[92m'    # Green - AI responses
    STATS = '\033[95m'       # Magenta - statistics/model info
    TODO = '\033[91m'        # Red - TODO items
    BOLD = '\033[1m'
    RESET = '\033[0m'

    @classmethod
    def header(cls, text):
        return f"{cls.BOLD}{cls.HEADER}{text}{cls.RESET}"

    @classmethod
    def prompt(cls, text):
        return f"{cls.PROMPT}{text}{cls.RESET}"

    @classmethod
    def response(cls, text):
        return f"{cls.RESPONSE}{text}{cls.RESET}"

    @classmethod
    def stats(cls, text):
        return f"{cls.STATS}{text}{cls.RESET}"

    @classmethod
    def todo(cls, text):
        return f"{cls.TODO}{text}{cls.RESET}"


def create_basic_agent():
    """Create a basic Strands agent backed by AWS Bedrock."""
    # TODO 1: Import Agent from strands
    # Hint: from strands import Agent

    # TODO 2: Import BedrockModel from strands.models.bedrock
    # Hint: from strands.models.bedrock import BedrockModel
    # Key difference from starter.py: BedrockModel replaces AnthropicModel

    # TODO 3: Create a BedrockModel instance
    # Hint: model = BedrockModel(model_id=DEFAULT_MODEL, region_name=AWS_REGION, max_tokens=1024)
    model = None

    # TODO 4: Create an Agent with the model
    # Hint: agent = Agent(model=model)
    agent = None

    return agent


def agent_with_system_prompt():
    """Create an agent with a custom system prompt."""
    # TODO 5: Create BedrockModel and Agent with a system prompt
    # Hint: Agent(model=model, system_prompt="Your system prompt here")
    # Same pattern as starter.py — only AnthropicModel → BedrockModel changes

    return None


def multi_turn_conversation(agent):
    """Demonstrate multi-turn conversation with context retention."""
    # TODO 6: Send multiple messages to the same agent
    # Strands agents automatically maintain conversation history — no change needed here
    # Just call agent("message") twice with the same agent instance

    response1 = None  # agent("My name is Alice and I study weather.")
    response2 = None  # agent("What's my name and what do I study?")

    return response1, response2


def compare_models(prompt: str = "Explain what causes thunder in one sentence."):
    """
    Compare responses from Haiku 3 and Sonnet 4.5 via the Bedrock converse API.

    TODO 7: Implement model comparison using boto3 directly (same approach as kata-01)
    Uses direct boto3 calls for accurate token counts — no Strands wrapper here.

    Returns dict with model_id -> {name, response, time, input_tokens, output_tokens, cost}
    """
    # TODO: import boto3
    # client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

    results = {}

    # TODO: Loop through [DEFAULT_MODEL, COMPARISON_MODEL]
    # For each model:
    #   1. Time the call: start = time.time()
    #   2. response = client.converse(modelId=model_id, messages=[...], inferenceConfig={"maxTokens": 256})
    #   3. elapsed = time.time() - start
    #   4. usage = response["usage"]  →  "inputTokens" / "outputTokens"
    #   5. Calculate cost using MODEL_PRICING
    #   6. Store in results dict with keys: name, response, time, input_tokens, output_tokens, cost

    return results


def print_comparison_table(results: dict):
    """Print a formatted comparison table of model results."""
    if not results:
        print(Colors.todo("No comparison results to display"))
        return

    print(Colors.header("\n┌" + "─" * 58 + "┐"))
    print(Colors.header("│" + " MODEL COMPARISON SUMMARY".center(58) + "│"))
    print(Colors.header("├" + "─" * 12 + "┬" + "─" * 10 + "┬" + "─" * 10 + "┬" + "─" * 10 + "┬" + "─" * 12 + "┤"))
    print(Colors.header("│" + " Model".center(12) + "│" + " Time".center(10) + "│" + " In Tok".center(10) + "│" + " Out Tok".center(10) + "│" + " Cost".center(12) + "│"))
    print(Colors.header("├" + "─" * 12 + "┼" + "─" * 10 + "┼" + "─" * 10 + "┼" + "─" * 10 + "┼" + "─" * 12 + "┤"))

    for model_id, data in results.items():
        name = data["name"][:10].center(12)
        time_str = f"{data['time']:.2f}s".center(10)
        in_tok = str(data["input_tokens"]).center(10)
        out_tok = str(data["output_tokens"]).center(10)
        cost_str = f"${data['cost']:.6f}".center(12)
        print(Colors.stats(f"│{name}│{time_str}│{in_tok}│{out_tok}│{cost_str}│"))

    print(Colors.header("└" + "─" * 12 + "┴" + "─" * 10 + "┴" + "─" * 10 + "┴" + "─" * 10 + "┴" + "─" * 12 + "┘"))

    haiku = results.get(DEFAULT_MODEL, {})
    sonnet = results.get(COMPARISON_MODEL, {})

    if haiku.get("time") and sonnet.get("time") and haiku["time"] > 0:
        speed_ratio = sonnet["time"] / haiku["time"]
        print(Colors.stats(f"\n  Haiku is ~{speed_ratio:.1f}x faster than Sonnet"))

    if haiku.get("cost") and sonnet.get("cost") and haiku["cost"] > 0:
        cost_ratio = sonnet["cost"] / haiku["cost"]
        print(Colors.stats(f"  Haiku is ~{cost_ratio:.1f}x cheaper than Sonnet"))

    print(Colors.stats("\n  Note: Faster/cheaper doesn't mean better for complex tasks!"))


def main():
    """Run all the demos."""
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 02: Strands Agents Introduction - Bedrock Starter"))
    print(Colors.header(f" Region: {AWS_REGION}"))
    print(Colors.header("=" * 70))

    # Test 1: Basic agent
    print(Colors.header("\n1. Basic Agent"))
    print("-" * 40)
    print(Colors.prompt("Prompt: 'What is the capital of France? Answer briefly.'"))
    agent = create_basic_agent()
    if agent:
        response = agent("What is the capital of France? Answer briefly.")
        print(Colors.response(f"Agent: {response}"))
    else:
        print(Colors.todo("TODO: Implement create_basic_agent()"))

    # Test 2: Agent with system prompt
    print(Colors.header("\n2. Agent with System Prompt"))
    print("-" * 40)
    print(Colors.stats("System: 'You are a friendly weather assistant...'"))
    print(Colors.prompt("Prompt: 'Why is the sky blue?'"))
    weather_agent = agent_with_system_prompt()
    if weather_agent:
        response = weather_agent("Why is the sky blue?")
        print(Colors.response(f"Weather Agent: {response}"))
    else:
        print(Colors.todo("TODO: Implement agent_with_system_prompt()"))

    # Test 3: Multi-turn conversation
    print(Colors.header("\n3. Multi-turn Conversation"))
    print("-" * 40)
    if agent:
        from strands import Agent
        from strands.models.bedrock import BedrockModel

        model = BedrockModel(model_id=DEFAULT_MODEL, region_name=AWS_REGION, max_tokens=512)
        chat_agent = Agent(model=model)

        print(Colors.prompt("User: My name is Alice and I study weather."))
        print(Colors.prompt("User: What's my name and what do I study?"))
        response1, response2 = multi_turn_conversation(chat_agent)
        if response1 and response2:
            print(Colors.response(f"Response 1: {response1}"))
            print(Colors.response(f"Response 2: {response2}"))
        else:
            print(Colors.todo("TODO: Implement multi_turn_conversation()"))
    else:
        print(Colors.todo("TODO: Complete previous steps first"))

    # Test 4: Specialized chatbot (bonus)
    print(Colors.header("\n4. Specialized Chatbot (Bonus)"))
    print("-" * 40)
    print(Colors.stats("Create your own specialized chatbot with a detailed system prompt"))
    print(Colors.todo("TODO (Bonus): Create a specialized chatbot agent using BedrockModel"))

    # Test 5: Model comparison
    print(Colors.header("\n5. Model Comparison"))
    print("-" * 40)
    comparison_prompt = "Explain what causes thunder in one sentence."
    print(Colors.prompt(f"Prompt: '{comparison_prompt}'"))
    print(Colors.stats("\nRunning same prompt on Haiku and Sonnet via Bedrock..."))

    results = compare_models(comparison_prompt)

    if results:
        for model_id, data in results.items():
            print(Colors.stats(f"\n{data['name']} ({data['time']:.2f}s):"))
            print(Colors.response(f"  {data['response']}"))
        print_comparison_table(results)
    else:
        print(Colors.todo("TODO: Implement compare_models()"))

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 02 Complete!"))
    print(Colors.header("=" * 70))


if __name__ == "__main__":
    main()
