# Kata 05: RAG-Enhanced Strands Agent

## Objective

Combine the power of RAG (Retrieval-Augmented Generation) with Strands agents to create an intelligent assistant that can search a knowledge base and use other tools to provide comprehensive answers.

## Learning Goals

- Integrate RAG retrieval as a Strands tool
- Build a knowledge-augmented agent
- Combine multiple tools (RAG + other capabilities)
- Handle context injection effectively
- Understand production patterns for RAG agents

## Prerequisites

- Completed Kata 03 (Strands Tools)
- Completed Kata 04 (Local RAG)
- Anthropic API key configured
- LlamaIndex dependencies installed

## Time Estimate

40-50 minutes

## Difficulty

⭐⭐⭐ (Advanced)

---

## Background

### Why Combine RAG with Agents?

RAG alone is powerful, but combining it with an agent provides:
- **Tool selection**: Agent decides when to search knowledge base
- **Multi-step reasoning**: Can combine KB search with other tools
- **Better answers**: Agent can synthesize information from multiple sources
- **Conversation flow**: Maintains context across queries

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Strands Agent                        │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  RAG Tool   │  │ Calculator  │  │ Other Tools │     │
│  │  (Search)   │  │             │  │             │     │
│  └──────┬──────┘  └─────────────┘  └─────────────┘     │
│         │                                               │
│         ▼                                               │
│  ┌─────────────────────────────────────┐               │
│  │     Vector Index (LlamaIndex)        │               │
│  │  ┌─────┐  ┌─────┐  ┌─────┐          │               │
│  │  │Doc 1│  │Doc 2│  │Doc 3│  ...     │               │
│  │  └─────┘  └─────┘  └─────┘          │               │
│  └─────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────┘
```

### Key Pattern

The RAG retrieval becomes a tool that the agent can call:

```python
@tool
def search_knowledge_base(query: str) -> str:
    """Search the weather knowledge base for information."""
    response = query_engine.query(query)
    return str(response)
```

---

## Level 1: Challenge

Build a weather assistant agent that:

1. Has access to a RAG-powered knowledge base tool
2. Can search weather documentation
3. Has additional utility tools (calculator, etc.)
4. Provides comprehensive answers using multiple sources
5. Cites sources when using knowledge base

### Success Criteria

- [ ] RAG is integrated as a Strands tool
- [ ] Agent correctly identifies when to search KB
- [ ] Agent can combine KB info with reasoning
- [ ] Sources are cited in responses
- [ ] Other tools work alongside RAG

---

## Level 2: Step-by-Step Guide

### Step 1: Set Up the Knowledge Base

```python
from pathlib import Path
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Create embedding model
embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load and index documents
docs_path = Path("./sample_data/weather_docs")
documents = SimpleDirectoryReader(str(docs_path)).load_data()
index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)

# Create query engine (we'll use this in our tool)
query_engine = index.as_query_engine(similarity_top_k=3)
```

### Step 2: Create the RAG Tool

```python
from strands import tool

@tool
def search_weather_knowledge(query: str) -> str:
    """Search the weather knowledge base for information about weather
    phenomena, forecasting, safety procedures, and meteorology.

    Args:
        query: The search query describing what information you need.
    """
    response = query_engine.query(query)

    # Format response with source information
    result = str(response.response)

    # Add source citations
    if response.source_nodes:
        sources = [node.node.metadata.get("file_name", "unknown")
                   for node in response.source_nodes]
        unique_sources = list(set(sources))
        result += f"\n\n[Sources: {', '.join(unique_sources)}]"

    return result
```

### Step 3: Add Complementary Tools

```python
@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expression: A mathematical expression like '32 * 9/5 + 32'.
    """
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"

@tool
def convert_temperature(value: float, from_unit: str, to_unit: str) -> str:
    """Convert temperature between Celsius and Fahrenheit.

    Args:
        value: The temperature value to convert.
        from_unit: Source unit (C or F).
        to_unit: Target unit (C or F).
    """
    if from_unit.upper() == "C" and to_unit.upper() == "F":
        result = value * 9/5 + 32
    elif from_unit.upper() == "F" and to_unit.upper() == "C":
        result = (value - 32) * 5/9
    else:
        return f"Unknown conversion: {from_unit} to {to_unit}"
    return f"{value}°{from_unit} = {result:.1f}°{to_unit}"
```

### Step 4: Create the Agent

```python
from strands import Agent
from strands.models.anthropic import AnthropicModel

model = AnthropicModel(
    model_id="claude-3-5-haiku-20241022",
    max_tokens=1024
)

agent = Agent(
    model=model,
    tools=[search_weather_knowledge, calculate, convert_temperature],
    system_prompt="""You are WeatherBot, an expert weather assistant.

You have access to a knowledge base with detailed weather information.
Use the search_weather_knowledge tool to find accurate information.

When answering questions:
1. Search the knowledge base for relevant information
2. Synthesize the information into a clear answer
3. Cite your sources when using knowledge base content
4. Use other tools (calculator, converter) when helpful

Be helpful, accurate, and cite your sources."""
)
```

### Step 5: Test the Agent

```python
# Questions that should use the knowledge base
response = agent("What are the different types of thunderstorms and their dangers?")
print(response)

# Questions combining KB + other tools
response = agent("If it's 68°F in New York, what is that in Celsius? And what should I wear?")
print(response)

# Multi-step question
response = agent("Explain the Enhanced Fujita Scale and calculate the average wind speed of EF3-EF5 tornadoes")
print(response)
```

---

## Expected Output

```
================================================================================
 Kata 05: RAG-Enhanced Strands Agent
================================================================================

Question: What causes lightning and thunder?

Agent: Based on the weather knowledge base, lightning and thunder are related
phenomena during thunderstorms.

**Lightning** forms when electrical charges build up in clouds due to colliding
ice particles. When the charge difference becomes large enough, electricity
discharges as lightning.

**Thunder** is caused by the rapid expansion of air heated by lightning.
The lightning heats air to around 30,000°C, creating a shock wave that we
hear as thunder.

Fun fact: You can estimate how far away lightning is by counting seconds
between the flash and thunder, then dividing by 3 (for km) or 5 (for miles).

[Sources: weather_faq.md, severe_weather.md]

Question: Convert 100°F to Celsius and tell me what weather conditions I should expect

Agent: Let me convert that temperature and check the weather guidance.

100°F = 37.8°C

At this temperature, you should expect hot weather conditions. According to
the weather safety guidelines, when heat index is above 32°C (90°F):
- Stay hydrated
- Limit outdoor activities
- Watch for signs of heat exhaustion
- Seek air-conditioned spaces

[Sources: weather_faq.md]
```

---

## Extension Challenges

1. **Add web search**: Integrate a web search tool for current conditions
2. **Conversation memory**: Remember user preferences across queries
3. **Source ranking**: Show confidence scores for KB results
4. **Streaming responses**: Implement streaming for long answers
5. **Error handling**: Gracefully handle KB unavailability

---

## Production Patterns

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query: str) -> str:
    return query_engine.query(query)
```

### Fallback Handling

```python
@tool
def search_weather_knowledge(query: str) -> str:
    """Search the weather knowledge base."""
    try:
        response = query_engine.query(query)
        if not response.response:
            return "No relevant information found in knowledge base."
        return str(response)
    except Exception as e:
        return f"Knowledge base temporarily unavailable. Error: {e}"
```

### Relevance Filtering

```python
@tool
def search_weather_knowledge(query: str, min_relevance: float = 0.5) -> str:
    """Search with relevance filtering."""
    response = query_engine.query(query)

    # Filter low-relevance results
    relevant_nodes = [
        node for node in response.source_nodes
        if node.score >= min_relevance
    ]

    if not relevant_nodes:
        return "No sufficiently relevant information found."

    return str(response)
```

---

## Troubleshooting

### Agent Doesn't Use KB Tool

- Check tool docstring is descriptive
- Ensure system prompt mentions the KB
- Try more explicit questions ("search the knowledge base for...")

### Slow Responses

- Use smaller embedding model
- Reduce `similarity_top_k`
- Cache frequent queries

### Poor Answer Quality

- Improve chunking strategy
- Add more documents
- Fine-tune similarity threshold

---

## Resources

- [Strands Agents Documentation](https://strandsagents.com/)
- [LlamaIndex Query Engine](https://docs.llamaindex.ai/en/stable/module_guides/querying/)
- [RAG Best Practices](https://www.anthropic.com/research/rag-best-practices)
