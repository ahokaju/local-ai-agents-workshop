"""
Kata 02: Strands Agents Introduction - Bedrock Solution

This script mirrors solution.py but uses AWS Bedrock as the inference provider
instead of the Anthropic API directly.

Prerequisites:
    pip install 'strands-agents[bedrock]' strands-agents-tools boto3 python-dotenv

    Set these environment variables before running:
        AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
        AWS_REGION=eu-central-1   (must match the region your key was created in)

    boto3 picks up both variables automatically — no extra configuration needed.
"""

import os
import time
import boto3
from dotenv import load_dotenv
from strands import Agent
from strands.models.bedrock import BedrockModel

load_dotenv()

# Default model configuration
DEFAULT_MODEL = "anthropic.claude-3-haiku-20240307-v1:0"
COMPARISON_MODEL = "eu.anthropic.claude-sonnet-4-5-20250929-v1:0"
AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")

# Model pricing on Bedrock (per million tokens)
MODEL_PRICING = {
    COMPARISON_MODEL: {"input": 3.00, "output": 15.00, "name": "Sonnet 4.5"},
    DEFAULT_MODEL: {"input": 0.25, "output": 1.25, "name": "Haiku 3"},
}


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


def create_basic_agent():
    """
    Create a basic Strands agent backed by AWS Bedrock.

    Returns:
        A configured Strands Agent instance.
    """
    model = BedrockModel(
        model_id=DEFAULT_MODEL,
        region_name=AWS_REGION,
        max_tokens=1024
    )
    return Agent(model=model)


def create_agent_with_params():
    """
    Create an agent with custom model parameters.

    The temperature parameter controls response randomness (0.0-1.0).
    """
    model = BedrockModel(
        model_id=DEFAULT_MODEL,
        region_name=AWS_REGION,
        max_tokens=1024,
        temperature=0.7
    )
    return Agent(model=model)


def agent_with_system_prompt():
    """
    Create an agent with a custom system prompt.

    System prompts define the agent's personality, role, and behaviour.
    """
    model = BedrockModel(
        model_id=DEFAULT_MODEL,
        region_name=AWS_REGION,
        max_tokens=1024
    )

    agent = Agent(
        model=model,
        system_prompt="""You are a friendly weather assistant.
        You explain weather phenomena in simple terms that anyone can understand.
        Be concise but informative. Use analogies when helpful."""
    )
    return agent


def multi_turn_conversation(agent):
    """
    Demonstrate multi-turn conversation with context retention.

    Strands agents automatically maintain conversation history.
    """
    response1 = agent("My name is Alice and I study meteorology at university.")
    response2 = agent("What's my name and what do I study?")
    return response1, response2


def compare_models(prompt: str = "Explain what causes thunder in one sentence."):
    """
    Compare responses from Haiku and Sonnet via the Bedrock converse API.

    Uses boto3 directly for accurate token tracking, mirroring the approach
    used in kata-01 solution_bedrock.py.

    Returns dict with response, timing, tokens, and cost for each model.
    """
    results = {}
    client = boto3.client(
        service_name="bedrock-runtime",
        region_name=AWS_REGION
    )

    for model_id in [DEFAULT_MODEL, COMPARISON_MODEL]:
        start_time = time.time()
        response = client.converse(
            modelId=model_id,
            messages=[
                {"role": "user", "content": [{"text": prompt}]}
            ],
            inferenceConfig={"maxTokens": 256}
        )
        elapsed_time = time.time() - start_time

        usage = response["usage"]
        input_tokens = usage["inputTokens"]
        output_tokens = usage["outputTokens"]

        pricing = MODEL_PRICING[model_id]
        cost = (input_tokens * pricing["input"] / 1_000_000) + \
               (output_tokens * pricing["output"] / 1_000_000)

        results[model_id] = {
            "name": pricing["name"],
            "response": response["output"]["message"]["content"][0]["text"],
            "time": elapsed_time,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        }

    return results


def print_comparison_table(results: dict):
    """Print a formatted comparison table of model results."""
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


def create_weather_chatbot():
    """Create a specialized weather chatbot agent."""
    model = BedrockModel(
        model_id=DEFAULT_MODEL,
        region_name=AWS_REGION,
        max_tokens=1024,
        temperature=0.5
    )

    agent = Agent(
        model=model,
        system_prompt="""You are WeatherBot, an expert weather assistant.

Your capabilities:
- Explain weather phenomena clearly
- Describe different cloud types
- Explain how weather forecasting works
- Discuss climate patterns

Your style:
- Be friendly and approachable
- Use simple language, avoid jargon
- Give practical examples when possible
- Keep responses concise unless asked for detail

Remember: You don't have access to real-time weather data,
so explain concepts rather than giving current conditions."""
    )

    return agent


def main():
    """Run all the demos."""
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 02: Strands Agents Introduction - Bedrock Solution"))
    print(Colors.header(f" Region: {AWS_REGION}"))
    print(Colors.header("=" * 70))

    # Test 1: Basic agent
    print(Colors.header("\n1. Basic Agent"))
    print("-" * 40)
    print(Colors.prompt("Prompt: 'What is the capital of France? Answer briefly.'"))
    agent = create_basic_agent()
    response = agent("What is the capital of France? Answer briefly.")
    print(Colors.response(f"Agent: {response}"))

    # Test 2: Agent with system prompt
    print(Colors.header("\n2. Agent with System Prompt (Weather Assistant)"))
    print("-" * 40)
    print(Colors.stats("System: 'You are a friendly weather assistant...'"))
    print(Colors.prompt("Prompt: 'Why is the sky blue?'"))
    weather_agent = agent_with_system_prompt()
    response = weather_agent("Why is the sky blue?")
    print(Colors.response(f"Weather Agent: {response}"))

    # Test 3: Multi-turn conversation
    print(Colors.header("\n3. Multi-turn Conversation"))
    print("-" * 40)
    model = BedrockModel(model_id=DEFAULT_MODEL, region_name=AWS_REGION, max_tokens=512)
    chat_agent = Agent(model=model)

    print(Colors.prompt("User: My name is Alice and I study meteorology at university."))
    response1 = chat_agent("My name is Alice and I study meteorology at university.")
    print(Colors.response(f"Agent: {response1}"))

    print(Colors.prompt("\nUser: What's my name and what do I study?"))
    response2 = chat_agent("What's my name and what do I study?")
    print(Colors.response(f"Agent: {response2}"))

    # Test 4: Specialized chatbot
    print(Colors.header("\n4. Specialized Weather Chatbot"))
    print("-" * 40)
    print(Colors.stats("WeatherBot configured with detailed system prompt"))
    weather_bot = create_weather_chatbot()

    questions = [
        "What are cumulonimbus clouds?",
        "How do meteorologists predict weather?",
    ]

    for question in questions:
        print(Colors.prompt(f"\nUser: {question}"))
        response = weather_bot(question)
        print(Colors.response(f"WeatherBot: {response}"))

    # Test 5: Model comparison
    print(Colors.header("\n5. Model Comparison"))
    print("-" * 40)
    comparison_prompt = "Explain what causes thunder in one sentence."
    print(Colors.prompt(f"Prompt: '{comparison_prompt}'"))
    print(Colors.stats("\nRunning same prompt on Haiku and Sonnet via Bedrock..."))

    results = compare_models(comparison_prompt)

    for model_id, data in results.items():
        print(Colors.stats(f"\n{data['name']} ({data['time']:.2f}s):"))
        print(Colors.response(f"  {data['response']}"))

    print_comparison_table(results)

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 02 Complete!"))
    print(Colors.header("=" * 70))


if __name__ == "__main__":
    main()
