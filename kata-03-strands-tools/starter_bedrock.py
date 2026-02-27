"""
Kata 03: Strands Agent with Custom Tools - Bedrock Starter Template

Complete the TODO to learn how to build agents with custom tools backed by
AWS Bedrock.  All tools are identical to starter.py — only the model provider
changes in create_agent_with_tools().

Prerequisites:
    pip install 'strands-agents[bedrock]' strands-agents-tools boto3 httpx python-dotenv

    Set these environment variables before running:
        AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
        AWS_REGION=us-east-1   (must match the region your key was created in)

    boto3 picks up both variables automatically — no extra configuration needed.

    To use eu-central-1: set AWS_REGION=eu-central-1. The Haiku 3 model ID has
    no region prefix and works in all regions as-is.
"""

import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from strands import Agent, tool
# TODO 1: Import BedrockModel instead of AnthropicModel
# Hint: from strands.models.bedrock import BedrockModel
import httpx

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DEFAULT_MODEL = "anthropic.claude-3-haiku-20240307-v1:0"


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[96m'
    PROMPT = '\033[93m'
    RESPONSE = '\033[92m'
    STATS = '\033[95m'
    TODO = '\033[91m'
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


# City coordinates for weather lookup
CITY_COORDINATES = {
    "london": {"lat": 51.5074, "lon": -0.1278, "country": "UK"},
    "paris": {"lat": 48.8566, "lon": 2.3522, "country": "France"},
    "new york": {"lat": 40.7128, "lon": -74.0060, "country": "USA"},
    "tokyo": {"lat": 35.6762, "lon": 139.6503, "country": "Japan"},
    "helsinki": {"lat": 60.1699, "lon": 24.9384, "country": "Finland"},
    "sydney": {"lat": -33.8688, "lon": 151.2093, "country": "Australia"},
}


# ==============================================================================
# Tool Definitions  (identical to starter.py — copy implementations here)
# ==============================================================================

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city using Open-Meteo API (real data).

    Args:
        city: The name of the city to get weather for.
    """
    city_lower = city.lower()

    if city_lower not in CITY_COORDINATES:
        available = ", ".join(CITY_COORDINATES.keys())
        return f"City '{city}' not found. Available cities: {available}"

    coords = CITY_COORDINATES[city_lower]

    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "timezone": "auto"
        }

        response = httpx.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        current = data["current"]
        temp = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        wind = current["wind_speed_10m"]
        weather_code = current["weather_code"]

        weather_descriptions = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
            80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
            95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
        }
        condition = weather_descriptions.get(weather_code, f"Weather code {weather_code}")

        return (f"Weather in {city.title()} ({coords['country']}): "
                f"{temp}°C, {condition}, Humidity: {humidity}%, Wind: {wind} km/h")

    except httpx.TimeoutException:
        return f"Error: Weather API request timed out for {city}"
    except httpx.HTTPError as e:
        return f"Error fetching weather for {city}: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely.

    Args:
        expression: A mathematical expression like '2 + 2' or 'sqrt(16)'.
    """
    import math

    try:
        safe_dict = {
            "abs": abs, "round": round, "min": min, "max": max, "sum": sum,
            "pow": pow, "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
            "tan": math.tan, "pi": math.pi, "e": math.e,
        }

        allowed_chars = set("0123456789+-*/.() ,")
        expression_check = expression
        for func in safe_dict.keys():
            expression_check = expression_check.replace(func, "")

        if not all(c in allowed_chars for c in expression_check):
            return "Error: Expression contains invalid characters"

        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return f"Result: {result}"
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"


@tool
def get_current_time(timezone: str = "UTC") -> str:
    """Get the current date and time.

    Args:
        timezone: The timezone name (currently supports UTC only).
    """
    from datetime import datetime, timezone as tz
    now = datetime.now(tz.utc)
    return f"Current date and time ({timezone}): {now.strftime('%Y-%m-%d %H:%M:%S')}"


@tool
def convert_temperature(value: float, from_unit: str, to_unit: str) -> str:
    """Convert temperature between Celsius, Fahrenheit, and Kelvin.

    Args:
        value: The temperature value to convert.
        from_unit: The source unit (C, F, or K).
        to_unit: The target unit (C, F, or K).
    """
    from_unit = from_unit.upper()
    to_unit = to_unit.upper()

    if from_unit == "C":
        celsius = value
    elif from_unit == "F":
        celsius = (value - 32) * 5 / 9
    elif from_unit == "K":
        celsius = value - 273.15
    else:
        return f"Unknown source unit: {from_unit}. Use C, F, or K."

    if to_unit == "C":
        result = celsius
    elif to_unit == "F":
        result = celsius * 9 / 5 + 32
    elif to_unit == "K":
        result = celsius + 273.15
    else:
        return f"Unknown target unit: {to_unit}. Use C, F, or K."

    return f"{value}°{from_unit} = {result:.2f}°{to_unit}"


@tool
def fetch_webpage(url: str, extract_text: bool = True) -> str:
    """Fetch content from a webpage URL.

    Args:
        url: The URL to fetch content from.
        extract_text: If True, extract just text content. If False, return raw HTML.
    """
    try:
        if not url.startswith(("http://", "https://")):
            return "Error: URL must start with http:// or https://"

        headers = {"User-Agent": "Mozilla/5.0 (compatible; Workshop-Agent/1.0)"}
        response = httpx.get(url, headers=headers, timeout=15.0, follow_redirects=True)
        response.raise_for_status()

        content = response.text

        if extract_text:
            import re
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<[^>]+>', ' ', content)
            content = re.sub(r'\s+', ' ', content).strip()
            if len(content) > 3000:
                content = content[:3000] + "... [truncated]"

        return f"Content from {url}:\n{content}"

    except httpx.TimeoutException:
        return f"Error: Request timed out for {url}"
    except httpx.HTTPError as e:
        return f"Error fetching {url}: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


# ==============================================================================
# Agent Creation
# ==============================================================================

def create_agent_with_tools():
    """Create a Strands agent with all defined tools."""
    # TODO 2: Create a BedrockModel instead of AnthropicModel
    # Hint: from strands.models.bedrock import BedrockModel
    # Hint: model = BedrockModel(model_id=DEFAULT_MODEL, region_name=AWS_REGION, max_tokens=1024)
    # Everything else (tools list, system_prompt) is identical to starter.py
    model = None

    if model is None:
        return None

    agent = Agent(
        model=model,
        tools=[get_weather, calculate, get_current_time, convert_temperature, fetch_webpage],
        system_prompt="""You are a helpful assistant with access to several tools:
- Real-time weather data for major cities (via Open-Meteo API)
- A calculator for math expressions
- Current time
- Temperature conversion
- Web page fetching

Use tools when they would help answer the user's question.
When using tool results, incorporate them naturally into your response."""
    )

    return agent


# ==============================================================================
# Main Demo
# ==============================================================================

def main():
    """Run all the demos."""
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 03: Strands Agent with Custom Tools - Bedrock Starter"))
    print(Colors.header(f" Region: {AWS_REGION}"))
    print(Colors.header("=" * 70))

    agent = create_agent_with_tools()

    if not agent:
        print(Colors.todo("\nTODO: Implement create_agent_with_tools() using BedrockModel"))
        print(Colors.stats("\nComplete the TODO in this file to enable the agent."))
        return

    test_queries = [
        ("1. Real Weather API", "What's the weather like in Paris right now?"),
        ("2. Math Query", "What is 15 * 7 + 23?"),
        ("3. Time Query", "What time is it right now?"),
        ("4. Temperature Conversion", "Convert 25 degrees Celsius to Fahrenheit"),
        ("5. Web Page Title", "What is the title of the page at https://example.com?"),
        ("6. Multi-step Query", "What's the weather in London and Helsinki? Which is colder?"),
    ]

    for title, query in test_queries:
        print(Colors.header(f"\n{title}"))
        print("-" * 40)
        print(Colors.prompt(f"User: {query}"))
        try:
            response = agent(query)
            print(Colors.response(f"Agent: {response}"))
        except Exception as e:
            print(f"Error: {e}")

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 03 Complete!"))
    print(Colors.header("=" * 70))


if __name__ == "__main__":
    main()
