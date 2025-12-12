# Kata 02: Introduction to Strands Agents

## Objective

Learn to build AI agents using the Strands Agents SDK with Anthropic as the model provider. Understand the agent architecture and how it differs from direct API calls.

## Learning Goals

- Understand what Strands Agents are and why to use them
- Set up Strands with the Anthropic provider
- Create a basic agent that can hold conversations
- Configure agent parameters (model, temperature, max_tokens)
- Compare agent-based approach vs direct API calls

## Prerequisites

- Completed Kata 01 (Anthropic API Basics)
- Anthropic API key configured
- Python 3.12

## Time Estimate

25-30 minutes

## Difficulty

⭐ (Beginner)

---

## Background

### What are Strands Agents?

Strands Agents is an open-source SDK that provides a model-driven approach to building AI agents. Key features:

- **Model-agnostic**: Works with Anthropic, AWS Bedrock, OpenAI, Ollama, and more
- **Simple agent loop**: Clean abstraction over LLM interactions
- **Tool support**: Easy integration of custom tools (covered in Kata 03)
- **Production-ready**: Used in production by multiple companies

### Why Use Strands?

| Direct API | Strands Agents |
|------------|----------------|
| Manual conversation management | Automatic conversation handling |
| Build your own tool calling | Built-in tool execution |
| Custom retry/error handling | Production patterns included |
| Good for simple use cases | Better for complex agents |

### Architecture

```
┌─────────────────┐
│  Your Code      │
├─────────────────┤
│  Strands Agent  │  ← Agent loop, tool execution
├─────────────────┤
│  Model Provider │  ← Anthropic, Bedrock, OpenAI...
├─────────────────┤
│  LLM API        │  ← Claude, GPT, etc.
└─────────────────┘
```

---

## Level 1: Challenge

Build a Python script that:

1. Sets up Strands with the Anthropic model provider
2. Creates a basic agent
3. Sends messages and receives responses
4. Configures model parameters
5. Demonstrates multi-turn conversation

### Success Criteria

- [ ] Strands is properly installed with Anthropic support
- [ ] Agent responds to queries correctly
- [ ] Multi-turn conversation maintains context
- [ ] Custom model parameters are applied
- [ ] Code is clean and well-documented

---

## Level 2: Step-by-Step Guide

### Step 1: Install Strands with Anthropic Provider

```bash
pip install 'strands-agents[anthropic]' strands-agents-tools
```

### Step 2: Create a Basic Agent

```python
from strands import Agent
from strands.models.anthropic import AnthropicModel

# Create the model provider
model = AnthropicModel(
    model_id="claude-haiku-4-5-20251001",
    max_tokens=1024
)

# Create the agent
agent = Agent(model=model)

# Send a message
response = agent("What is the weather like in Paris?")
print(response)
```

### Step 3: Configure Model Parameters

```python
model = AnthropicModel(
    model_id="claude-haiku-4-5-20251001",
    max_tokens=1024,
    params={
        "temperature": 0.7,  # Control randomness
    }
)
```

### Step 4: Add a System Prompt

```python
agent = Agent(
    model=model,
    system_prompt="You are a helpful weather assistant. Be concise and accurate."
)
```

### Step 5: Multi-turn Conversation

```python
# Strands maintains conversation history automatically
agent = Agent(model=model)

# First message
response1 = agent("My name is Alice")
print(f"Agent: {response1}")

# Follow-up (agent remembers context)
response2 = agent("What's my name?")
print(f"Agent: {response2}")
```

### Step 6: Access the Full Response Object

```python
# Get detailed response information
result = agent("Tell me about rain")

# The response includes the full message
print(f"Response text: {result}")

# You can also access the agent's message history
# (This is managed internally by Strands)
```

---

## Expected Output

```
================================================================================
 Kata 02: Strands Agents Introduction
================================================================================

1. Basic Agent
-----------------------------------------
Agent: I don't have access to real-time weather data...

2. Agent with System Prompt
-----------------------------------------
Agent: Currently, I cannot check live weather, but Paris typically...

3. Multi-turn Conversation
-----------------------------------------
User: My name is Alice and I work in meteorology.
Agent: Nice to meet you, Alice! It's great to meet someone who works...
User: What's my profession?
Agent: You work in meteorology!

4. Different Models Comparison
-----------------------------------------
Haiku (fast): [quick response]
Sonnet (balanced): [balanced response]
```

---

## Extension Challenges

1. **Weather chatbot**: Create a weather-focused agent with a detailed system prompt
2. **Conversation logger**: Track all messages and responses
3. **Model comparison**: Compare response quality between Haiku and Sonnet
4. **Custom persona**: Create an agent with a specific personality

---

## Key Concepts

### Agent vs Direct API

```python
# Direct API (from Kata 01)
client = Anthropic()
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    messages=[{"role": "user", "content": "Hello"}]
)

# Strands Agent (this kata)
agent = Agent(model=AnthropicModel(...))
response = agent("Hello")  # Much simpler!
```

### When to Use Each

**Use Direct API when:**
- Simple one-off queries
- Maximum control needed
- Learning the fundamentals

**Use Strands Agent when:**
- Building conversational agents
- Need tool integration (Kata 03)
- Want production-ready patterns
- Multi-turn conversations

---

## Resources

- [Strands Agents Documentation](https://strandsagents.com/)
- [Strands + Anthropic Guide](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/anthropic/)
- [Strands GitHub Repository](https://github.com/strands-agents/sdk-python)
- [Agent Architecture Overview](https://aws.amazon.com/blogs/opensource/introducing-strands-agents-an-open-source-ai-agents-sdk/)
