"""
Kata 01: Anthropic API Basics - Bedrock Solution

This script mirrors solution.py but uses AWS Bedrock as the inference provider
instead of the Anthropic API directly.

Prerequisites:
    pip install boto3 python-dotenv

    Set these environment variables before running:
        AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
        AWS_REGION=us-east-1   (must match the region your key was created in)

    boto3 picks up both variables automatically — no extra configuration needed.

    To use eu-central-1: set AWS_REGION=eu-central-1 and change the model ID
    prefix from "us." to "eu." (e.g. "eu.anthropic.claude-sonnet-4-5-20250929-v1:0").
"""

import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"


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


def get_client():
    """Create a Bedrock runtime client using env-var credentials."""
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )


# Token tracking for cumulative usage
class TokenTracker:
    """Track cumulative token usage across multiple API calls."""
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.call_count = 0

    def add(self, usage: dict):
        """Add tokens from a Bedrock usage dict to the running total."""
        self.total_input_tokens += usage.get("inputTokens", 0)
        self.total_output_tokens += usage.get("outputTokens", 0)
        self.call_count += 1

    def get_summary(self):
        """Get summary of all token usage."""
        # Claude Sonnet on Bedrock pricing: ~$3 input / $15 output per MTok
        input_cost = self.total_input_tokens * 0.003 / 1000
        output_cost = self.total_output_tokens * 0.015 / 1000
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "api_calls": self.call_count,
            "estimated_cost": input_cost + output_cost
        }


tracker = TokenTracker()


def basic_message():
    """Send a basic message via Bedrock and get a response."""
    client = get_client()

    response = client.converse(
        modelId=DEFAULT_MODEL,
        messages=[
            {"role": "user", "content": [{"text": "What is the capital of France? Answer in one sentence."}]}
        ],
        inferenceConfig={"maxTokens": 1024}
    )

    tracker.add(response["usage"])
    return response["output"]["message"]["content"][0]["text"]


def message_with_system_prompt(user_message: str, system_prompt: str):
    """Send a message with a system prompt via Bedrock."""
    client = get_client()

    response = client.converse(
        modelId=DEFAULT_MODEL,
        system=[{"text": system_prompt}],
        messages=[
            {"role": "user", "content": [{"text": user_message}]}
        ],
        inferenceConfig={"maxTokens": 1024}
    )

    tracker.add(response["usage"])
    return response["output"]["message"]["content"][0]["text"]


def streaming_response(prompt: str):
    """Stream a response from Bedrock in real-time."""
    client = get_client()

    response = client.converse_stream(
        modelId=DEFAULT_MODEL,
        messages=[
            {"role": "user", "content": [{"text": prompt}]}
        ],
        inferenceConfig={"maxTokens": 1024}
    )

    for event in response["stream"]:
        if "contentBlockDelta" in event:
            delta = event["contentBlockDelta"]["delta"]
            if "text" in delta:
                print(delta["text"], end="", flush=True)
        elif "metadata" in event:
            # Usage is reported in the final metadata event
            tracker.add(event["metadata"].get("usage", {}))


def get_token_usage(prompt: str):
    """Get token usage statistics for a request."""
    client = get_client()

    response = client.converse(
        modelId=DEFAULT_MODEL,
        messages=[
            {"role": "user", "content": [{"text": prompt}]}
        ],
        inferenceConfig={"maxTokens": 256}
    )

    usage = response["usage"]
    tracker.add(usage)
    return {
        "input_tokens": usage["inputTokens"],
        "output_tokens": usage["outputTokens"]
    }


def multi_turn_conversation():
    """Demonstrate a multi-turn conversation with message history."""
    client = get_client()

    messages = [
        {"role": "user", "content": [{"text": "My name is Alice and I like weather."}]},
        {"role": "assistant", "content": [{"text": "Nice to meet you, Alice! It's great that you're interested in weather. Is there anything specific about weather you'd like to discuss?"}]},
        {"role": "user", "content": [{"text": "What's my name and what do I like?"}]},
    ]

    response = client.converse(
        modelId=DEFAULT_MODEL,
        messages=messages,
        inferenceConfig={"maxTokens": 256}
    )

    tracker.add(response["usage"])
    return response["output"]["message"]["content"][0]["text"]


def handle_errors():
    """Demonstrate error handling with the Bedrock API."""
    client = get_client()

    try:
        response = client.converse(
            modelId=DEFAULT_MODEL,
            messages=[
                {"role": "user", "content": [{"text": "Hello!"}]}
            ],
            inferenceConfig={"maxTokens": 256}
        )
        tracker.add(response["usage"])
        return f"Success: {response['output']['message']['content'][0]['text']}"

    except NoCredentialsError:
        return "Error: No credentials found. Ensure AWS_BEARER_TOKEN_BEDROCK and AWS_REGION are set."

    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "AccessDeniedException":
            return "Error: Access denied. Check your AWS_BEARER_TOKEN_BEDROCK key and model access in the console."
        elif code == "ThrottlingException":
            return "Error: Rate limit exceeded. Please wait and try again."
        else:
            return f"Error: {code} - {e.response['Error']['Message']}"


def main():
    """Run all the demos."""
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 01: Anthropic API Basics - Bedrock Solution"))
    print(Colors.header(f" Model: {DEFAULT_MODEL}"))
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
    input_cost = usage['input_tokens'] * 0.003 / 1000
    output_cost = usage['output_tokens'] * 0.015 / 1000
    print(Colors.stats(f"Estimated cost: ${input_cost + output_cost:.6f}"))

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

    # Summary
    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" SESSION SUMMARY"))
    print(Colors.header("=" * 70))
    summary = tracker.get_summary()
    print(Colors.stats(f"Total API calls:     {summary['api_calls']}"))
    print(Colors.stats(f"Total input tokens:  {summary['total_input_tokens']}"))
    print(Colors.stats(f"Total output tokens: {summary['total_output_tokens']}"))
    print(Colors.stats(f"Total tokens:        {summary['total_tokens']}"))
    print(Colors.stats(f"Estimated cost:      ${summary['estimated_cost']:.6f}"))

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 01 Complete!"))
    print(Colors.header("=" * 70))


if __name__ == "__main__":
    main()
