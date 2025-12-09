"""
Kata 03: Strands Agent with Custom Tools - Starter Template

Complete the TODOs to learn how to build agents with custom tools,
including real API calls.

Prerequisites:
    pip install 'strands-agents[anthropic]' strands-agents-tools httpx
    export ANTHROPIC_API_KEY="your-key-here"
"""

import os
from datetime import datetime
from dotenv import load_dotenv
# TODO 1: Import required modules
# from strands import Agent, tool
# from strands.models.anthropic import AnthropicModel
# import httpx

load_dotenv()


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
# Tool Definitions
# ==============================================================================

# TODO 2: Add @tool decorator and implement real weather API
def get_weather(city: str) -> str:
    """Get the current weather for a city using Open-Meteo API (real data).

    Args:
        city: The name of the city to get weather for.
    """
    # TODO: Implement using Open-Meteo API
    # Steps:
    #   1. Look up city in CITY_COORDINATES
    #   2. Call https://api.open-meteo.com/v1/forecast with lat/lon
    #   3. Parse response for temperature, humidity, weather_code
    #   4. Return formatted weather string

    # Example API call (uncomment and complete):
    # url = "https://api.open-meteo.com/v1/forecast"
    # params = {
    #     "latitude": coords["lat"],
    #     "longitude": coords["lon"],
    #     "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
    # }
    # response = httpx.get(url, params=params, timeout=10.0)

    return "TODO: Implement get_weather with Open-Meteo API"


# TODO 3: Add @tool decorator and implement calculator
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely.

    Args:
        expression: A mathematical expression like '2 + 2' or 'sqrt(16)'.
    """
    # TODO: Implement safe calculation
    # Steps:
    #   1. Define allowed functions (abs, round, sqrt, sin, cos, etc.)
    #   2. Validate expression contains only safe characters
    #   3. Use eval() with restricted builtins

    return "TODO: Implement calculate"


# TODO 4: Add @tool decorator and implement time tool
def get_current_time(timezone: str = "UTC") -> str:
    """Get the current date and time.

    Args:
        timezone: The timezone name (currently supports UTC only).
    """
    # TODO: Return formatted current time

    return "TODO: Implement get_current_time"


# TODO 5: Add @tool decorator and implement temperature converter
def convert_temperature(value: float, from_unit: str, to_unit: str) -> str:
    """Convert temperature between Celsius, Fahrenheit, and Kelvin.

    Args:
        value: The temperature value to convert.
        from_unit: The source unit (C, F, or K).
        to_unit: The target unit (C, F, or K).
    """
    # TODO: Implement temperature conversion
    # Formulas:
    #   C to F: (C * 9/5) + 32
    #   C to K: C + 273.15
    #   F to C: (F - 32) * 5/9

    return "TODO: Implement convert_temperature"


# TODO 6: Add @tool decorator and implement web page fetching
def fetch_webpage(url: str, extract_text: bool = True) -> str:
    """Fetch content from a webpage URL.

    Args:
        url: The URL to fetch content from.
        extract_text: If True, extract just text content. If False, return raw HTML.
    """
    # TODO: Implement using httpx
    # Steps:
    #   1. Validate URL starts with http:// or https://
    #   2. Make GET request with httpx
    #   3. If extract_text, strip HTML tags using regex
    #   4. Truncate if too long
    #   5. Return content

    return "TODO: Implement fetch_webpage"


# ==============================================================================
# Agent Creation
# ==============================================================================

def create_agent_with_tools():
    """Create a Strands agent with all defined tools."""
    # TODO 7: Create model and agent with tools
    # model = AnthropicModel(model_id="claude-3-5-haiku-20241022", max_tokens=1024)
    # agent = Agent(
    #     model=model,
    #     tools=[get_weather, calculate, get_current_time, convert_temperature, fetch_webpage],
    #     system_prompt="..."
    # )

    return None


# ==============================================================================
# Main Demo
# ==============================================================================

def main():
    """Run all the demos."""
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 03: Strands Agent with Custom Tools"))
    print(Colors.header("=" * 70))

    agent = create_agent_with_tools()

    if not agent:
        print(Colors.todo("\nTODO: Implement create_agent_with_tools()"))
        print(Colors.stats("\nComplete the TODOs in this file to enable the agent."))
        return

    # Test queries
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
            if "TODO" in str(response):
                print(Colors.todo(f"Agent: {response}"))
            else:
                print(Colors.response(f"Agent: {response}"))
        except Exception as e:
            print(f"Error: {e}")

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 03 Complete!"))
    print(Colors.header("=" * 70))


if __name__ == "__main__":
    main()
