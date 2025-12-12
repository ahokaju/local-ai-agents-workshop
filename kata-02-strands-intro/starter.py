"""
Kata 02: Strands Agents Introduction - Starter Template

Complete the TODOs to learn how to build AI agents with Strands.

Prerequisites:
    pip install 'strands-agents[anthropic]' strands-agents-tools
    export ANTHROPIC_API_KEY="your-key-here"
"""

import os
import time
from dotenv import load_dotenv

load_dotenv()

# Default model configuration
DEFAULT_MODEL = "claude-haiku-4-5-20251001"  # Fast, cost-effective for workshop
COMPARISON_MODEL = "claude-sonnet-4-20250514"  # For model comparison demo

# Model pricing (per million tokens)
MODEL_PRICING = {
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00, "name": "Sonnet 4"},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00, "name": "Haiku 4.5"},
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
    """Create a basic Strands agent with Anthropic."""
    # TODO 1: Import Agent from strands
    # Hint: from strands import Agent

    # TODO 2: Import AnthropicModel from strands.models.anthropic
    # Hint: from strands.models.anthropic import AnthropicModel

    # TODO 3: Create an AnthropicModel instance
    # Hint: model = AnthropicModel(model_id="claude-sonnet-4-20250514", max_tokens=1024)
    model = None

    # TODO 4: Create an Agent with the model
    # Hint: agent = Agent(model=model)
    agent = None

    return agent


def agent_with_system_prompt():
    """Create an agent with a custom system prompt."""
    # TODO 5: Create model and agent with a system prompt
    # Hint: Agent(model=model, system_prompt="Your system prompt here")

    return None


def multi_turn_conversation(agent):
    """Demonstrate multi-turn conversation with context retention."""
    # TODO 6: Send multiple messages to the same agent
    # The agent should remember context from previous messages

    # First message
    response1 = None  # agent("My name is Alice and I study weather.")

    # Second message (agent should remember the context)
    response2 = None  # agent("What's my name and what do I study?")

    return response1, response2


def compare_models(prompt: str = "Explain what causes thunder in one sentence."):
    """
    Compare responses from different Claude models with timing and cost.

    TODO 7: Implement model comparison with stats tracking
    Uses direct Anthropic API for accurate token counts.

    Returns dict with model_id -> {name, response, time, input_tokens, output_tokens, cost}
    """
    # TODO: Import Anthropic client
    # from anthropic import Anthropic
    # client = Anthropic()

    results = {}

    # TODO: Loop through [DEFAULT_MODEL, COMPARISON_MODEL]
    # For each model:
    #   1. Time the API call: start = time.time()
    #   2. Call: response = client.messages.create(model=model_id, max_tokens=256, messages=[...])
    #   3. elapsed = time.time() - start
    #   4. Get tokens: response.usage.input_tokens, response.usage.output_tokens
    #   5. Calculate cost using MODEL_PRICING
    #   6. Store in results dict with keys: name, response, time, input_tokens, output_tokens, cost

    # Placeholder return - replace with actual implementation
    return results


def print_comparison_table(results: dict):
    """Print a formatted comparison table of model results."""
    if not results:
        print(Colors.todo("No comparison results to display"))
        return

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


def main():
    """Run all the demos."""
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 02: Strands Agents Introduction"))
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
        # Create a fresh agent for this test
        from strands import Agent
        from strands.models.anthropic import AnthropicModel

        model = AnthropicModel(model_id=DEFAULT_MODEL, max_tokens=512)
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

    # Test 4: Specialized chatbot (placeholder - add your own!)
    print(Colors.header("\n4. Specialized Chatbot (Bonus)"))
    print("-" * 40)
    print(Colors.stats("Create your own specialized chatbot with a detailed system prompt"))
    print(Colors.todo("TODO (Bonus): Create a specialized chatbot agent"))

    # Test 5: Model comparison (capstone - moved to end)
    print(Colors.header("\n5. Model Comparison"))
    print("-" * 40)
    comparison_prompt = "Explain what causes thunder in one sentence."
    print(Colors.prompt(f"Prompt: '{comparison_prompt}'"))
    print(Colors.stats("\nRunning same prompt on Haiku and Sonnet..."))

    results = compare_models(comparison_prompt)

    if results:
        # Show individual responses
        for model_id, data in results.items():
            print(Colors.stats(f"\n{data['name']} ({data['time']:.2f}s):"))
            print(Colors.response(f"  {data['response']}"))

        # Show comparison table
        print_comparison_table(results)
    else:
        print(Colors.todo("TODO: Implement compare_models()"))

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 02 Complete!"))
    print(Colors.header("=" * 70))


if __name__ == "__main__":
    main()
