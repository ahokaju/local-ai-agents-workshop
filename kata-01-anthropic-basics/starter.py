"""
Kata 01: Anthropic API Basics - Starter Template

Complete the TODOs to learn how to interact with the Anthropic API.

Prerequisites:
    pip install anthropic python-dotenv
    export ANTHROPIC_API_KEY="your-key-here"
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Default model - Claude Haiku for fast, cost-effective responses
DEFAULT_MODEL = "claude-haiku-4-5-20251001"


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for pretty terminal output."""
    HEADER = '\033[96m'      # Cyan - step headers
    PROMPT = '\033[93m'      # Yellow - user prompts
    RESPONSE = '\033[92m'    # Green - AI responses
    STATS = '\033[95m'       # Magenta - statistics
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


# TODO 0: Create a TokenTracker class to track cumulative token usage
# Hint: Track total_input_tokens, total_output_tokens, and call_count
# Hint: Add an add(response) method to accumulate usage from each API call
# Hint: Add a get_summary() method to return totals and estimated cost
class TokenTracker:
    """Track cumulative token usage across multiple API calls."""
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.call_count = 0

    def add(self, response):
        # TODO: Implement token tracking
        pass

    def get_summary(self):
        # TODO: Return dict with totals and estimated cost
        # Sonnet pricing: $3 input / $15 output per MTok
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": 0,
            "api_calls": self.call_count,
            "estimated_cost": 0.0
        }

# Global tracker instance
tracker = TokenTracker()


def basic_message():
    """Send a basic message to Claude and get a response."""
    # TODO 1: Import the Anthropic client
    # Hint: from anthropic import Anthropic

    # TODO 2: Initialize the Anthropic client
    # Hint: The client automatically uses ANTHROPIC_API_KEY from environment
    client = None

    # TODO 3: Create a message request
    # Hint: Use client.messages.create() with model, max_tokens, and messages
    response = None

    # TODO 4: Extract and return the text response
    # Hint: response.content[0].text
    return None


def message_with_system_prompt(user_message: str, system_prompt: str):
    """Send a message with a system prompt."""
    # TODO 5: Initialize client and create message with system prompt
    # Hint: Add system="..." parameter to messages.create()

    return None


def streaming_response(prompt: str):
    """Stream a response from Claude in real-time."""
    # TODO 6: Import and initialize client

    # TODO 7: Use client.messages.stream() to get streaming response
    # Hint: Use "with client.messages.stream(...) as stream:"
    # Hint: Then iterate over stream.text_stream

    pass


def get_token_usage(prompt: str):
    """Get token usage statistics for a request."""
    # TODO 8: Make a request and return token usage
    # Hint: response.usage.input_tokens and response.usage.output_tokens

    return {"input_tokens": 0, "output_tokens": 0}


def handle_errors():
    """Demonstrate error handling with the Anthropic API."""
    # TODO 9: Import error types and handle them appropriately
    # Hint: from anthropic import APIError, AuthenticationError, RateLimitError

    try:
        # This should work if API key is valid
        pass
    except Exception as e:
        print(f"Error: {e}")


def multi_turn_conversation():
    """Demonstrate a multi-turn conversation with message history."""
    # TODO 10: Create a conversation with multiple turns
    # Hint: messages list should contain alternating user/assistant messages
    # Hint: Previous messages provide context for the model

    return None


def main():
    """Run all the demos."""
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 01: Anthropic API Basics"))
    print(Colors.header("=" * 70))

    # Test 1: Basic message
    print(Colors.header("\n1. Basic Message"))
    print("-" * 40)
    print(Colors.prompt("Prompt: 'What is the capital of France? Answer in one sentence.'"))
    response = basic_message()
    if response:
        print(Colors.response(f"Response: {response}"))
    else:
        print(Colors.todo("TODO: Implement basic_message()"))

    # Test 2: System prompt
    print(Colors.header("\n2. Message with System Prompt"))
    print("-" * 40)
    print(Colors.prompt("System: 'You are a weather expert. Be concise and use simple language.'"))
    print(Colors.prompt("Prompt: 'What causes rain?'"))
    response = message_with_system_prompt(
        user_message="What causes rain?",
        system_prompt="You are a weather expert. Be concise and use simple language."
    )
    if response:
        print(Colors.response(f"Response: {response}"))
    else:
        print(Colors.todo("TODO: Implement message_with_system_prompt()"))

    # Test 3: Streaming
    print(Colors.header("\n3. Streaming Response"))
    print("-" * 40)
    print(Colors.prompt("Prompt: 'Count from 1 to 5 slowly.'"))
    print(f"{Colors.RESPONSE}Response: ", end="")
    streaming_response("Count from 1 to 5 slowly.")
    print(Colors.RESET)

    # Test 4: Token usage
    print(Colors.header("\n4. Token Usage"))
    print("-" * 40)
    print(Colors.prompt("Prompt: 'Hello, how are you?'"))
    usage = get_token_usage("Hello, how are you?")
    print(Colors.stats(f"Input tokens: {usage['input_tokens']}"))
    print(Colors.stats(f"Output tokens: {usage['output_tokens']}"))

    # Estimate cost (Sonnet pricing: $3/$15 per MTok)
    if usage['input_tokens'] > 0:
        input_cost = usage['input_tokens'] * 0.003 / 1000
        output_cost = usage['output_tokens'] * 0.015 / 1000
        print(Colors.stats(f"Estimated cost: ${input_cost + output_cost:.6f}"))

    # Test 5: Multi-turn conversation
    print(Colors.header("\n5. Multi-turn Conversation"))
    print("-" * 40)
    print(Colors.prompt("Turn 1 - User: 'My name is Alice and I like weather.'"))
    print(Colors.prompt("Turn 2 - User: 'What's my name and what do I like?'"))
    response = multi_turn_conversation()
    if response:
        print(Colors.response(f"Response: {response}"))
    else:
        print(Colors.todo("TODO: Implement multi_turn_conversation()"))

    # Test 6: Error handling
    print(Colors.header("\n6. Error Handling"))
    print("-" * 40)
    print(Colors.prompt("Testing error handling with a simple 'Hello!' message..."))
    handle_errors()

    # Summary: Total token usage across all demos
    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" SESSION SUMMARY"))
    print(Colors.header("=" * 70))
    summary = tracker.get_summary()
    print(Colors.stats(f"Total API calls:    {summary['api_calls']}"))
    print(Colors.stats(f"Total input tokens: {summary['total_input_tokens']}"))
    print(Colors.stats(f"Total output tokens:{summary['total_output_tokens']}"))
    print(Colors.stats(f"Total tokens:       {summary['total_tokens']}"))
    print(Colors.stats(f"Estimated cost:     ${summary['estimated_cost']:.6f}"))

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 01 Complete!"))
    print(Colors.header("=" * 70))


if __name__ == "__main__":
    main()
