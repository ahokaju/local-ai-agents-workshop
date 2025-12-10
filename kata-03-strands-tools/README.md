# Kata 03: Strands Agent with Custom Tools

## Objective

Learn to extend Strands agents with custom tools, enabling them to perform actions beyond text generation. This is a key capability for building useful AI assistants.

## Learning Goals

- Understand the concept of tools/function calling in LLMs
- Create custom tools using the `@tool` decorator
- Build an agent that uses multiple tools
- Handle tool execution and responses
- Understand when and how the agent decides to use tools

## Prerequisites

- Completed Kata 02 (Strands Introduction)
- Anthropic API key configured
- Python 3.12

```bash
pip install 'strands-agents[anthropic]' strands-agents-tools httpx
```

## Time Estimate

30-40 minutes

## Difficulty

⭐⭐ (Intermediate)

---

## Background

### What are Tools?

Tools (also called "functions" or "actions") allow AI agents to:
- **Retrieve data**: Get current weather, search databases, call APIs
- **Take actions**: Send emails, create files, update records
- **Perform calculations**: Math operations, data processing
- **Access external systems**: Jira, Confluence, Slack, etc.

### How Tool Calling Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   User      │────▶│   Agent     │────▶│    Tool     │
│   Query     │     │   (LLM)     │     │  Execution  │
└─────────────┘     └──────┬──────┘     └──────┬──────┘
                           │                    │
                           │◀───────────────────┘
                           │    Tool Result
                           ▼
                   ┌─────────────┐
                   │   Final     │
                   │  Response   │
                   └─────────────┘
```

1. User sends a query
2. Agent decides if a tool is needed
3. Agent calls the tool with parameters
4. Tool returns result
5. Agent formulates final response

### Strands Tool Definition

```python
from strands import tool
import httpx

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city using Open-Meteo API.

    Args:
        city: The name of the city to get weather for.
    """
    # Real API call to Open-Meteo (free, no API key needed)
    coords = {"lat": 48.8566, "lon": 2.3522}  # Paris
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "current": "temperature_2m,weather_code",
    }
    response = httpx.get(url, params=params, timeout=10.0)
    data = response.json()
    temp = data["current"]["temperature_2m"]
    return f"Weather in {city}: {temp}°C"
```

---

## Level 1: Challenge

Build a Python script that:

1. Creates custom tools including:
   - **Real weather API** (Open-Meteo - free, no key needed)
   - **Calculator** (safe math evaluation)
   - **Web page fetcher** (using httpx)
   - **Temperature converter**
2. Builds an agent with access to these tools
3. Demonstrates the agent using tools to answer questions
4. Shows the agent choosing the right tool for different queries

### Success Criteria

- [ ] Weather tool fetches real data from Open-Meteo API
- [ ] Web fetcher can retrieve content from URLs
- [ ] Tools have typed parameters and proper docstrings
- [ ] Agent correctly identifies when to use tools
- [ ] Agent correctly chooses the right tool for each query
- [ ] Final responses incorporate tool results naturally

---

## Level 2: Step-by-Step Guide

### Step 1: Define a Real Weather Tool

```python
from strands import tool
import httpx

# City coordinates for weather lookup
CITY_COORDINATES = {
    "london": {"lat": 51.5074, "lon": -0.1278},
    "paris": {"lat": 48.8566, "lon": 2.3522},
    "helsinki": {"lat": 60.1699, "lon": 24.9384},
    "tokyo": {"lat": 35.6762, "lon": 139.6503},
}

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city using Open-Meteo API.

    Args:
        city: The name of the city to get weather for.
    """
    city_lower = city.lower()
    if city_lower not in CITY_COORDINATES:
        return f"City not found. Available: {list(CITY_COORDINATES.keys())}"

    coords = CITY_COORDINATES[city_lower]
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "current": "temperature_2m,relative_humidity_2m,weather_code",
    }

    response = httpx.get(url, params=params, timeout=10.0)
    data = response.json()
    current = data["current"]

    return f"Weather in {city}: {current['temperature_2m']}°C, Humidity: {current['relative_humidity_2m']}%"
```

### Step 2: Define a Calculator Tool

```python
@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expression: A mathematical expression like '2 + 2' or '10 * 5'.
    """
    try:
        # Safe evaluation of mathematical expressions
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression"
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating: {e}"
```

### Step 3: Define a Time Tool

```python
from datetime import datetime, timezone

@tool
def get_current_time(tz_name: str = "UTC") -> str:
    """Get the current time.

    Args:
        tz_name: The timezone (currently only supports UTC).
    """
    now = datetime.now(timezone.utc)
    return f"Current time (UTC): {now.strftime('%Y-%m-%d %H:%M:%S')}"
```

### Step 4: Define a Web Fetching Tool

```python
@tool
def fetch_webpage(url: str) -> str:
    """Fetch content from a webpage URL.

    Args:
        url: The URL to fetch content from.
    """
    import re

    if not url.startswith(("http://", "https://")):
        return "Error: URL must start with http:// or https://"

    response = httpx.get(url, timeout=15.0, follow_redirects=True)
    content = response.text

    # Strip HTML tags for cleaner output
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
    content = re.sub(r'<[^>]+>', ' ', content)
    content = ' '.join(content.split())[:2000]  # Limit length

    return f"Content from {url}:\n{content}"
```

### Step 5: Create Agent with Tools

```python
from strands import Agent
from strands.models.anthropic import AnthropicModel

model = AnthropicModel(
    model_id="claude-3-5-haiku-20241022",
    max_tokens=1024
)

agent = Agent(
    model=model,
    tools=[get_weather, calculate, get_current_time, fetch_webpage],
    system_prompt="""You are a helpful assistant with access to:
- Real-time weather data (via Open-Meteo API)
- A calculator for math expressions
- Current time
- Web page fetching

Use tools when they would help answer the user's question."""
)
```

### Step 6: Test the Agent

```python
# Real weather query - fetches live data from Open-Meteo
response = agent("What's the weather in Paris right now?")
print(response)

# Math query - uses calculator tool
response = agent("What is 15 * 7 + 23?")
print(response)

# Web fetch query - fetches page content
response = agent("What is the title of the page at https://example.com?")
print(response)

# Multi-step query - uses multiple tools
response = agent("What's the weather in London and Helsinki? Which is colder?")
print(response)
```

---

## Running the Solution

```bash
# Run all demos
python solution.py

# Run only the web fetching demo (faster for testing)
python solution.py web
```

---

## Expected Output

```
======================================================================
 Kata 03: Strands Agent with Custom Tools - Solution
======================================================================

1. Real Weather API
----------------------------------------
User: What's the weather like in Paris right now?
Agent: The current weather in Paris is 12.5°C with 78% humidity and overcast skies.

2. Math Query
----------------------------------------
User: What is 15 * 7 + 23?
Agent: Let me calculate that for you. 15 × 7 + 23 = 128

3. Web Page Title
----------------------------------------
User: What is the title of the page at https://example.com?
Agent: The page title is "Example Domain".

4. Multi-step Query
----------------------------------------
User: What's the weather in London and Helsinki? Which is colder?
Agent: London is currently 8°C while Helsinki is -2°C. Helsinki is significantly colder!
```

Note: Weather data will vary as it's fetched live from the Open-Meteo API.

---

## Extension Challenges

1. **Add more cities**: Extend `CITY_COORDINATES` with more cities
2. **Weather forecast**: Modify the weather tool to get multi-day forecasts
3. **Browser automation**: See **Kata 03b** for Playwright-based browser tools
4. **Error handling**: Add robust error handling for network failures
5. **Caching**: Add caching to avoid repeated API calls for the same city

---

## Key Concepts

### Tool Docstrings Are Important

The docstring is what the LLM sees to understand the tool:

```python
@tool
def search_database(query: str, limit: int = 10) -> str:
    """Search the product database.

    Args:
        query: The search query string.
        limit: Maximum number of results to return (default: 10).
    """
```

### When Tools Are Called

The agent decides to use a tool when:
1. The query matches the tool's purpose (from docstring)
2. The required information isn't in the agent's knowledge
3. An action needs to be performed

### Tools Can Fail

Always handle errors gracefully:

```python
@tool
def risky_operation(param: str) -> str:
    """Perform an operation that might fail."""
    try:
        # Do something
        return "Success"
    except Exception as e:
        return f"Error: {e}"
```

---

## Comparison with AWS Bedrock

| Aspect | Strands Tools | Bedrock Action Groups |
|--------|---------------|----------------------|
| Definition | Python `@tool` decorator | Lambda + OpenAPI schema |
| Execution | Local Python | AWS Lambda |
| Complexity | Simple | More setup required |
| Scalability | Local resources | AWS managed |

---

## Resources

- [Strands Tools Documentation](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/tools/)
- [Claude Tool Use Guide](https://docs.anthropic.com/claude/docs/tool-use)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
