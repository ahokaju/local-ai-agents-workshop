# Kata 01: Anthropic API Basics

## Objective

Learn to use the Anthropic API directly for interacting with Claude models, understanding the fundamentals of API calls, streaming, and token management.

## Learning Goals

- Set up and configure the Anthropic Python client
- Send messages to Claude and process responses
- Implement streaming for real-time output
- Understand token usage and cost management
- Compare with AWS Bedrock API patterns

## Prerequisites

- Python 3.12
- Anthropic API key (get one at https://console.anthropic.com/)
- Basic Python knowledge

## Time Estimate

20-25 minutes

## Difficulty

⭐ (Beginner)

---

## Background

### Why Direct Anthropic API?

While AWS Bedrock provides managed access to Claude models with AWS integration benefits, the direct Anthropic API offers:

- **Simpler setup**: No AWS account or IAM configuration needed
- **Faster iteration**: Direct API calls without AWS middleware
- **Latest features**: New Claude capabilities often available first
- **Lower latency**: Direct connection to Anthropic's infrastructure

### API Structure

The Anthropic API uses a messages-based structure:

```python
from anthropic import Anthropic

client = Anthropic()  # Uses ANTHROPIC_API_KEY env var
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)
```

---

## Level 1: Challenge

Build a Python script that:

1. Initializes the Anthropic client
2. Sends a basic message and prints the response
3. Implements streaming to display response in real-time
4. Tracks and displays token usage
5. Handles errors gracefully

### Success Criteria

- [ ] Successfully connects to Anthropic API
- [ ] Gets a valid response from Claude
- [ ] Streaming output works correctly
- [ ] Token usage is tracked and displayed
- [ ] Errors are handled with helpful messages

---

## Level 2: Step-by-Step Guide

### Step 1: Set Up Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install anthropic python-dotenv

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"
# Or create a .env file with: ANTHROPIC_API_KEY=your-key-here
```

### Step 2: Basic Message

```python
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

# Send a simple message
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

# Extract and print the response
print(response.content[0].text)
```

### Step 3: Add System Prompt

```python
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    system="You are a helpful weather assistant. Be concise.",
    messages=[
        {"role": "user", "content": "What causes rain?"}
    ]
)
```

### Step 4: Implement Streaming

```python
# Streaming for real-time output
with client.messages.stream(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Tell me about clouds."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
print()  # New line at end
```

### Step 5: Track Token Usage

```python
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)

# Access usage information
print(f"Input tokens: {response.usage.input_tokens}")
print(f"Output tokens: {response.usage.output_tokens}")

# Estimate cost (approximate rates)
input_cost = response.usage.input_tokens * 0.003 / 1000  # $3/MTok
output_cost = response.usage.output_tokens * 0.015 / 1000  # $15/MTok
print(f"Estimated cost: ${input_cost + output_cost:.6f}")
```

### Step 6: Error Handling

```python
from anthropic import APIError, AuthenticationError, RateLimitError

try:
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello!"}]
    )
except AuthenticationError:
    print("Invalid API key. Check your ANTHROPIC_API_KEY.")
except RateLimitError:
    print("Rate limit exceeded. Please wait and try again.")
except APIError as e:
    print(f"API error: {e}")
```

---

## Expected Output

```
================================================================================
 Anthropic API Basics - Demo
================================================================================

Testing basic message...
Response: Paris is the capital of France.

Testing streaming...
Response: Clouds form when water vapor in the air condenses...

Token Usage:
  Input tokens: 12
  Output tokens: 45
  Estimated cost: $0.000711
```

---

## Extension Challenges

1. **Multi-turn conversation**: Implement a chat loop that maintains conversation history
2. **Temperature comparison**: Run the same prompt with different temperatures and compare outputs
3. **Model comparison**: Compare responses from Haiku vs Sonnet for the same prompt
4. **Structured output**: Get Claude to respond in JSON format

---

## Comparison: Anthropic API vs AWS Bedrock

| Aspect | Anthropic API | AWS Bedrock |
|--------|---------------|-------------|
| **Setup** | API key only | AWS account + IAM |
| **Authentication** | `ANTHROPIC_API_KEY` | AWS credentials |
| **SDK** | `anthropic` | `boto3` |
| **Request format** | Native Anthropic | AWS-wrapped |
| **Billing** | Anthropic account | AWS account |
| **Best for** | Development, prototyping | Production AWS apps |

---

## Resources

- [Anthropic API Documentation](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- [Claude Model Pricing](https://www.anthropic.com/pricing)
- [Messages API Reference](https://docs.anthropic.com/claude/reference/messages)
