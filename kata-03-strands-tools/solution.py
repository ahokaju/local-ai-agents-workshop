"""
Kata 03: Strands Agent with Custom Tools - Solution

This script demonstrates how to create custom tools and integrate them
with Strands agents, including real API calls.

Prerequisites:
    pip install 'strands-agents[anthropic]' strands-agents-tools httpx
    export ANTHROPIC_API_KEY="your-key-here"
"""

import os
import random
from datetime import datetime, timezone
from dotenv import load_dotenv
from strands import Agent, tool
from strands.models.anthropic import AnthropicModel
import httpx

load_dotenv()


# ANSI color codes for terminal output
class Colors:
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


# City coordinates for weather lookup
CITY_COORDINATES = {
    "london": {"lat": 51.5074, "lon": -0.1278, "country": "UK"},
    "paris": {"lat": 48.8566, "lon": 2.3522, "country": "France"},
    "new york": {"lat": 40.7128, "lon": -74.0060, "country": "USA"},
    "tokyo": {"lat": 35.6762, "lon": 139.6503, "country": "Japan"},
    "helsinki": {"lat": 60.1699, "lon": 24.9384, "country": "Finland"},
    "sydney": {"lat": -33.8688, "lon": 151.2093, "country": "Australia"},
    "berlin": {"lat": 52.5200, "lon": 13.4050, "country": "Germany"},
    "amsterdam": {"lat": 52.3676, "lon": 4.9041, "country": "Netherlands"},
}


# ==============================================================================
# Tool Definitions
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
        # Open-Meteo API - free, no API key required
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

        # Decode weather code to description
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
        expression: A mathematical expression like '2 + 2', '10 * 5', or 'sqrt(16)'.
    """
    import math

    try:
        # Define safe functions and constants
        safe_dict = {
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "pow": pow,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "pi": math.pi,
            "e": math.e,
        }

        # Only allow safe characters
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
def get_current_time(tz_name: str = "UTC") -> str:
    """Get the current date and time.

    Args:
        tz_name: The timezone name (currently supports UTC only).
    """
    now = datetime.now(timezone.utc)
    return f"Current date and time ({tz_name}): {now.strftime('%Y-%m-%d %H:%M:%S')}"


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

    # Convert to Celsius first
    if from_unit == "C":
        celsius = value
    elif from_unit == "F":
        celsius = (value - 32) * 5 / 9
    elif from_unit == "K":
        celsius = value - 273.15
    else:
        return f"Unknown source unit: {from_unit}. Use C, F, or K."

    # Convert from Celsius to target
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
def generate_random_number(min_value: int, max_value: int) -> str:
    """Generate a random integer between min and max (inclusive).

    Args:
        min_value: The minimum value (inclusive).
        max_value: The maximum value (inclusive).
    """
    if min_value > max_value:
        return "Error: min_value must be less than or equal to max_value"
    result = random.randint(min_value, max_value)
    return f"Random number between {min_value} and {max_value}: {result}"


@tool
def get_city_info(city: str) -> str:
    """Get information about a city.

    Args:
        city: The name of the city to get information about.
    """
    city_data = {
        "london": {"country": "UK", "population": "8.8 million", "timezone": "GMT"},
        "paris": {"country": "France", "population": "2.1 million", "timezone": "CET"},
        "new york": {"country": "USA", "population": "8.3 million", "timezone": "EST"},
        "tokyo": {"country": "Japan", "population": "13.9 million", "timezone": "JST"},
        "helsinki": {"country": "Finland", "population": "0.6 million", "timezone": "EET"},
        "sydney": {"country": "Australia", "population": "5.3 million", "timezone": "AEST"},
    }

    city_lower = city.lower()
    if city_lower in city_data:
        data = city_data[city_lower]
        return f"{city}: {data['country']}, Population: {data['population']}, Timezone: {data['timezone']}"
    return f"City information not available for {city}."


@tool
def fetch_webpage(url: str, extract_text: bool = True) -> str:
    """Fetch content from a webpage URL.

    Args:
        url: The URL to fetch content from.
        extract_text: If True, extract just text content. If False, return raw HTML.
    """
    try:
        # Validate URL
        if not url.startswith(("http://", "https://")):
            return "Error: URL must start with http:// or https://"

        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; Workshop-Agent/1.0)"
        }

        response = httpx.get(url, headers=headers, timeout=15.0, follow_redirects=True)
        response.raise_for_status()

        content = response.text

        if extract_text:
            # Simple text extraction - remove HTML tags
            import re
            # Remove script and style elements
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Clean up whitespace
            content = re.sub(r'\s+', ' ', content).strip()
            # Limit length
            if len(content) > 3000:
                content = content[:3000] + "... [truncated]"

        return f"Content from {url}:\n{content}"

    except httpx.TimeoutException:
        return f"Error: Request timed out for {url}"
    except httpx.HTTPError as e:
        return f"Error fetching {url}: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def get_webpage_title(url: str) -> str:
    """Get the title of a webpage.

    Args:
        url: The URL to get the title from.
    """
    try:
        if not url.startswith(("http://", "https://")):
            return "Error: URL must start with http:// or https://"

        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; Workshop-Agent/1.0)"
        }

        response = httpx.get(url, headers=headers, timeout=10.0, follow_redirects=True)
        response.raise_for_status()

        import re
        title_match = re.search(r'<title[^>]*>(.*?)</title>', response.text, re.IGNORECASE | re.DOTALL)

        if title_match:
            title = title_match.group(1).strip()
            # Clean up whitespace
            title = re.sub(r'\s+', ' ', title)
            return f"Page title: {title}"
        return f"No title found for {url}"

    except Exception as e:
        return f"Error: {str(e)}"


# ==============================================================================
# Agent Creation
# ==============================================================================

def create_agent_with_tools():
    """Create a Strands agent with all defined tools."""
    model = AnthropicModel(
        model_id="claude-3-5-haiku-20241022",
        max_tokens=1024
    )

    agent = Agent(
        model=model,
        tools=[
            get_weather,
            calculate,
            get_current_time,
            convert_temperature,
            generate_random_number,
            get_city_info,
            fetch_webpage,
            get_webpage_title,
        ],
        system_prompt="""You are a helpful assistant with access to several tools:
- Real-time weather data for major cities (via Open-Meteo API)
- A calculator for math expressions
- Current time
- Temperature conversion
- Random number generation
- City information
- Web page fetching and title extraction

Use tools when they would help answer the user's question.
When using tool results, incorporate them naturally into your response."""
    )

    return agent


def create_weather_agent():
    """Create a specialized weather-focused agent."""
    model = AnthropicModel(
        model_id="claude-3-5-haiku-20241022",
        max_tokens=1024
    )

    agent = Agent(
        model=model,
        tools=[get_weather, convert_temperature, get_city_info],
        system_prompt="""You are WeatherBot, a specialized weather assistant.
You can check weather conditions and convert temperatures.
Be friendly and provide helpful weather-related advice."""
    )

    return agent


# ==============================================================================
# Main Demo
# ==============================================================================

def main():
    """Run all the demos."""
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 03: Strands Agent with Custom Tools - Solution"))
    print(Colors.header("=" * 70))

    # Create the main agent
    agent = create_agent_with_tools()

    # Test queries that should use different tools
    test_queries = [
        ("1. Real Weather API", "What's the weather like in Paris right now?"),
        ("2. Math Query", "What is 15 * 7 + 23?"),
        ("3. Time Query", "What time is it right now?"),
        ("4. Temperature Conversion", "Convert 25 degrees Celsius to Fahrenheit"),
        ("5. City Info", "Tell me about Tokyo"),
        ("6. Web Page Title", "What is the title of the page at https://example.com?"),
        ("7. Multi-step Query", "What's the weather in London and Helsinki? Which is colder?"),
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

    # Demo the specialized weather agent
    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Specialized Weather Agent Demo"))
    print(Colors.header("=" * 70))

    weather_agent = create_weather_agent()

    weather_queries = [
        "What's the weather in Helsinki? Should I bring a jacket?",
        "Compare the weather in Sydney and London right now.",
    ]

    for query in weather_queries:
        print(Colors.prompt(f"\nUser: {query}"))
        response = weather_agent(query)
        print(Colors.response(f"WeatherBot: {response}"))

    # Demo web fetching
    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Web Fetching Demo"))
    print(Colors.header("=" * 70))

    web_query = "Fetch the content from https://strandsagents.com/latest/ and summarize what you find."
    print(Colors.prompt(f"\nUser: {web_query}"))
    response = agent(web_query)
    print(Colors.response(f"Agent: {response}"))

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 03 Complete!"))
    print(Colors.header("=" * 70))


def web_demo():
    """Run just the web fetching demo."""
    agent = create_agent_with_tools()
    web_query = "Fetch the content from https://strandsagents.com/latest/ and summarize what you find."
    print(f"\nUser: {web_query}")
    response = agent(web_query)
    print(f"Agent: {response}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        web_demo()
    else:
        main()
