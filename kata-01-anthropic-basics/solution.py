"""
Kata 01: Anthropic API Basics - Solution

This script demonstrates the fundamentals of using the Anthropic API
to interact with Claude models.

Prerequisites:
    pip install anthropic python-dotenv
    export ANTHROPIC_API_KEY="your-key-here"
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic, APIError, AuthenticationError, RateLimitError

# Load environment variables from .env file
load_dotenv()

# Default model - Claude Haiku for fast, cost-effective responses
DEFAULT_MODEL = "claude-3-5-haiku-20241022"


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for pretty terminal output."""
    HEADER = '\033[96m'      # Cyan - step headers
    PROMPT = '\033[93m'      # Yellow - user prompts
    RESPONSE = '\033[92m'    # Green - AI responses
    STATS = '\033[95m'       # Magenta - statistics
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

# Token tracking for cumulative usage
class TokenTracker:
    """Track cumulative token usage across multiple API calls."""
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.call_count = 0

    def add(self, response):
        """Add tokens from a response to the running total."""
        self.total_input_tokens += response.usage.input_tokens
        self.total_output_tokens += response.usage.output_tokens
        self.call_count += 1

    def get_summary(self):
        """Get summary of all token usage."""
        # Sonnet pricing: $3 input / $15 output per MTok
        input_cost = self.total_input_tokens * 0.003 / 1000
        output_cost = self.total_output_tokens * 0.015 / 1000
        total_cost = input_cost + output_cost
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "api_calls": self.call_count,
            "estimated_cost": total_cost
        }

# Global tracker instance
tracker = TokenTracker()


def basic_message():
    """Send a basic message to Claude and get a response."""
    # Initialize the Anthropic client (uses ANTHROPIC_API_KEY env var)
    client = Anthropic()

    # Create a message request
    response = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "What is the capital of France? Answer in one sentence."}
        ]
    )

    # Track token usage
    tracker.add(response)

    # Extract and return the text response
    return response.content[0].text


def message_with_system_prompt(user_message: str, system_prompt: str):
    """
    Send a message with a system prompt.

    Args:
        user_message: The user's question or request.
        system_prompt: Instructions for how Claude should behave.

    Returns:
        The model's text response.
    """
    client = Anthropic()

    response = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=1024,
        system=system_prompt,  # System prompt sets the context/behavior
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    # Track token usage
    tracker.add(response)

    return response.content[0].text


def streaming_response(prompt: str):
    """
    Stream a response from Claude in real-time.

    This is useful for long responses where you want to show
    output as it's generated rather than waiting for the complete response.
    """
    client = Anthropic()

    # Use context manager for streaming
    with client.messages.stream(
        model=DEFAULT_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        # Iterate over text chunks as they arrive
        for text in stream.text_stream:
            print(text, end="", flush=True)

    # Track token usage from the final message
    tracker.add(stream.get_final_message())


def get_token_usage(prompt: str):
    """
    Get token usage statistics for a request.

    Token usage helps you:
    - Estimate costs
    - Stay within rate limits
    - Optimize prompt length

    Returns:
        Dict with input_tokens and output_tokens counts.
    """
    client = Anthropic()

    response = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    )

    # Track token usage
    tracker.add(response)

    return {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens
    }


def multi_turn_conversation():
    """
    Demonstrate a multi-turn conversation with message history.

    The messages list maintains conversation context.
    """
    client = Anthropic()

    # Conversation history
    messages = [
        {"role": "user", "content": "My name is Alice and I like weather."},
        {"role": "assistant", "content": "Nice to meet you, Alice! It's great that you're interested in weather. Is there anything specific about weather you'd like to discuss?"},
        {"role": "user", "content": "What's my name and what do I like?"},
    ]

    response = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=256,
        messages=messages
    )

    # Track token usage
    tracker.add(response)

    return response.content[0].text


def handle_errors():
    """
    Demonstrate proper error handling with the Anthropic API.

    Always handle these common errors:
    - AuthenticationError: Invalid or missing API key
    - RateLimitError: Too many requests
    - APIError: General API errors
    """
    client = Anthropic()

    try:
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=256,
            messages=[{"role": "user", "content": "Hello!"}]
        )
        # Track token usage
        tracker.add(response)
        return f"Success: {response.content[0].text}"

    except AuthenticationError:
        return "Error: Invalid API key. Check your ANTHROPIC_API_KEY."

    except RateLimitError:
        return "Error: Rate limit exceeded. Please wait and try again."

    except APIError as e:
        return f"Error: API error - {e}"


def main():
    """Run all the demos."""
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 01: Anthropic API Basics - Solution"))
    print(Colors.header("=" * 70))

    # Test 1: Basic message
    print(Colors.header("\n1. Basic Message"))
    print("-" * 40)
    print(Colors.prompt("Prompt: 'What is the capital of France? Answer in one sentence.'"))
    response = basic_message()
    print(Colors.response(f"Response: {response}"))

    # Test 2: System prompt
    print(Colors.header("\n2. Message with System Prompt"))
    print("-" * 40)
    print(Colors.prompt("System: 'You are a weather expert. Be concise and use simple language.'"))
    print(Colors.prompt("Prompt: 'What causes rain?'"))
    response = message_with_system_prompt(
        user_message="What causes rain?",
        system_prompt="You are a weather expert. Be concise and use simple language."
    )
    print(Colors.response(f"Response: {response}"))

    # Test 3: Streaming
    print(Colors.header("\n3. Streaming Response"))
    print("-" * 40)
    print(Colors.prompt("Prompt: 'Count from 1 to 5, with a brief pause description between each number.'"))
    print(f"{Colors.RESPONSE}Response: ", end="")
    streaming_response("Count from 1 to 5, with a brief pause description between each number.")
    print(Colors.RESET)

    # Test 4: Token usage
    print(Colors.header("\n4. Token Usage"))
    print("-" * 40)
    print(Colors.prompt("Prompt: 'Hello, how are you today?'"))
    usage = get_token_usage("Hello, how are you today?")
    print(Colors.stats(f"Input tokens: {usage['input_tokens']}"))
    print(Colors.stats(f"Output tokens: {usage['output_tokens']}"))

    # Estimate cost (Sonnet pricing: $3 input / $15 output per MTok)
    input_cost = usage['input_tokens'] * 0.003 / 1000
    output_cost = usage['output_tokens'] * 0.015 / 1000
    total_cost = input_cost + output_cost
    print(Colors.stats(f"Estimated cost: ${total_cost:.6f}"))

    # Test 5: Multi-turn conversation
    print(Colors.header("\n5. Multi-turn Conversation"))
    print("-" * 40)
    print(Colors.prompt("Turn 1 - User: 'My name is Alice and I like weather.'"))
    print(Colors.response("Turn 1 - Assistant: 'Nice to meet you, Alice! ...'"))
    print(Colors.prompt("Turn 2 - User: 'What's my name and what do I like?'"))
    response = multi_turn_conversation()
    print(Colors.response(f"Turn 2 - Response: {response}"))

    # Test 6: Error handling
    print(Colors.header("\n6. Error Handling"))
    print("-" * 40)
    print(Colors.prompt("Testing error handling with a simple 'Hello!' message..."))
    result = handle_errors()
    print(Colors.response(f"Result: {result}"))

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
