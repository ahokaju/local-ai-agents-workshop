"""
Kata 02: Strands Agents Introduction - Solution

This script demonstrates how to build AI agents using the Strands SDK
with Anthropic as the model provider.

Prerequisites:
    pip install 'strands-agents[anthropic]' strands-agents-tools
    export ANTHROPIC_API_KEY="your-key-here"
"""

import os
import time
from dotenv import load_dotenv
from strands import Agent
from strands.models.anthropic import AnthropicModel
from anthropic import Anthropic

load_dotenv()

# Default model configuration
DEFAULT_MODEL = "claude-3-5-haiku-20241022"  # Fast, cost-effective for workshop
COMPARISON_MODEL = "claude-sonnet-4-20250514"  # For model comparison demo

# Model pricing (per million tokens) - as of 2024
MODEL_PRICING = {
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00, "name": "Sonnet 4"},
    "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00, "name": "Haiku 3.5"},
}


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for pretty terminal output."""
    HEADER = '\033[96m'      # Cyan - step headers
    PROMPT = '\033[93m'      # Yellow - user prompts
    RESPONSE = '\033[92m'    # Green - AI responses
    STATS = '\033[95m'       # Magenta - statistics/model info
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
    Create a basic Strands agent with Anthropic.

    Returns:
        A configured Strands Agent instance.
    """
    # Create the model provider
    model = AnthropicModel(
        model_id=DEFAULT_MODEL,
        max_tokens=1024
    )

    # Create and return the agent
    agent = Agent(model=model)

    return agent


def create_agent_with_params():
    """
    Create an agent with custom model parameters.

    The params dict allows you to configure:
    - temperature: Controls randomness (0.0-1.0)
    - top_p: Nucleus sampling parameter
    """
    model = AnthropicModel(
        model_id=DEFAULT_MODEL,
        max_tokens=1024,
        params={
            "temperature": 0.7,
        }
    )

    agent = Agent(model=model)
    return agent


def agent_with_system_prompt():
    """
    Create an agent with a custom system prompt.

    System prompts define the agent's personality, role, and behavior.
    """
    model = AnthropicModel(
        model_id=DEFAULT_MODEL,
        max_tokens=1024
    )

    # Create agent with a weather-focused system prompt
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

    Strands agents automatically maintain conversation history,
    allowing for natural back-and-forth dialogue.
    """
    # First message - introduce context
    response1 = agent("My name is Alice and I study meteorology at university.")

    # Second message - agent should remember the context
    response2 = agent("What's my name and what do I study?")

    return response1, response2


def compare_models(prompt: str = "Explain what causes thunder in one sentence."):
    """
    Compare responses from different Claude models with detailed stats.

    This demonstrates how to switch between models for different use cases:
    - Haiku: Fast, cost-effective for simple tasks
    - Sonnet: Balanced performance for most tasks

    Uses direct Anthropic API for accurate token tracking.
    Returns dict with response, timing, tokens, and cost for each model.
    """
    results = {}
    client = Anthropic()

    for model_id in [DEFAULT_MODEL, COMPARISON_MODEL]:
        # Time the response using direct Anthropic API for accurate token counts
        start_time = time.time()
        response = client.messages.create(
            model=model_id,
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}]
        )
        elapsed_time = time.time() - start_time

        # Get token usage directly from response
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        # Calculate cost
        pricing = MODEL_PRICING[model_id]
        cost = (input_tokens * pricing["input"] / 1_000_000) + \
               (output_tokens * pricing["output"] / 1_000_000)

        results[model_id] = {
            "name": pricing["name"],
            "response": response.content[0].text,
            "time": elapsed_time,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        }

    return results


def print_comparison_table(results: dict):
    """Print a formatted comparison table of model results."""
    # Table header
    print(Colors.header("\n┌" + "─" * 58 + "┐"))
    print(Colors.header("│" + " MODEL COMPARISON SUMMARY".center(58) + "│"))
    print(Colors.header("├" + "─" * 12 + "┬" + "─" * 10 + "┬" + "─" * 10 + "┬" + "─" * 10 + "┬" + "─" * 12 + "┤"))
    print(Colors.header("│" + " Model".center(12) + "│" + " Time".center(10) + "│" + " In Tok".center(10) + "│" + " Out Tok".center(10) + "│" + " Cost".center(12) + "│"))
    print(Colors.header("├" + "─" * 12 + "┼" + "─" * 10 + "┼" + "─" * 10 + "┼" + "─" * 10 + "┼" + "─" * 12 + "┤"))

    # Table rows
    for model_id, data in results.items():
        name = data["name"][:10].center(12)
        time_str = f"{data['time']:.2f}s".center(10)
        in_tok = str(data["input_tokens"]).center(10)
        out_tok = str(data["output_tokens"]).center(10)
        cost_str = f"${data['cost']:.6f}".center(12)
        print(Colors.stats(f"│{name}│{time_str}│{in_tok}│{out_tok}│{cost_str}│"))

    print(Colors.header("└" + "─" * 12 + "┴" + "─" * 10 + "┴" + "─" * 10 + "┴" + "─" * 10 + "┴" + "─" * 12 + "┘"))

    # Calculate and show comparisons
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
    """
    Create a specialized weather chatbot agent.

    This demonstrates a more complete agent configuration
    for a specific use case.
    """
    model = AnthropicModel(
        model_id=DEFAULT_MODEL,
        max_tokens=1024,
        params={
            "temperature": 0.5,  # Slightly lower for more focused responses
        }
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
    print(Colors.header(" Kata 02: Strands Agents Introduction - Solution"))
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
    # Create a fresh agent for this test
    model = AnthropicModel(model_id=DEFAULT_MODEL, max_tokens=512)
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

    # Test 5: Model comparison (moved to end as capstone)
    print(Colors.header("\n5. Model Comparison"))
    print("-" * 40)
    comparison_prompt = "Explain what causes thunder in one sentence."
    print(Colors.prompt(f"Prompt: '{comparison_prompt}'"))
    print(Colors.stats("\nRunning same prompt on Haiku and Sonnet..."))

    results = compare_models(comparison_prompt)

    # Show individual responses
    for model_id, data in results.items():
        print(Colors.stats(f"\n{data['name']} ({data['time']:.2f}s):"))
        print(Colors.response(f"  {data['response']}"))

    # Show comparison table
    print_comparison_table(results)

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 02 Complete!"))
    print(Colors.header("=" * 70))


if __name__ == "__main__":
    main()
