"""
Kata 05: RAG-Enhanced Strands Agent - Solution

This script combines RAG retrieval with a Strands agent to create an intelligent
weather assistant that can search a knowledge base and use other tools.

Prerequisites:
    pip install 'strands-agents[anthropic]' llama-index llama-index-embeddings-huggingface
    export ANTHROPIC_API_KEY="your-key-here"
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from strands import Agent, tool
from strands.models.anthropic import AnthropicModel
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.anthropic import Anthropic

load_dotenv()

# Path to sample documents (reuse from Kata 04)
DOCS_PATH = Path(__file__).parent.parent / "kata-04-local-rag" / "sample_data" / "weather_docs"

# Global query engine (initialized in setup)
query_engine = None


def setup_knowledge_base():
    """Initialize the knowledge base and query engine."""
    global query_engine

    print("   Loading embedding model...")
    embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("   Loading documents...")
    documents = SimpleDirectoryReader(str(DOCS_PATH)).load_data()
    print(f"   Loaded {len(documents)} document chunks")

    print("   Creating vector index...")
    Settings.embed_model = embed_model
    index = VectorStoreIndex.from_documents(
        documents,
        embed_model=embed_model,
        show_progress=True
    )

    print("   Creating query engine with Claude...")
    llm = Anthropic(model="claude-3-5-haiku-20241022")
    query_engine = index.as_query_engine(
        llm=llm,
        similarity_top_k=3
    )

    return query_engine


# ==============================================================================
# Tool Definitions
# ==============================================================================

@tool
def search_weather_knowledge(query: str) -> str:
    """Search the weather knowledge base for information about weather
    phenomena, forecasting, safety procedures, and meteorology.

    Use this tool when you need factual information about:
    - Weather phenomena (clouds, rain, storms, etc.)
    - Weather safety procedures
    - Forecast interpretation
    - Meteorological concepts

    Args:
        query: The search query describing what information you need.
    """
    if query_engine is None:
        return "Error: Knowledge base not initialized"

    try:
        response = query_engine.query(query)

        # Format response with source information
        result = str(response.response)

        # Add source citations
        if response.source_nodes:
            sources = []
            for node in response.source_nodes:
                filename = node.node.metadata.get("file_name", "unknown")
                score = node.score if hasattr(node, "score") else 0
                sources.append(f"{filename} (relevance: {score:.2f})")
            unique_sources = list(dict.fromkeys(sources))  # Remove duplicates preserving order
            result += f"\n\n[Sources: {', '.join(unique_sources)}]"

        return result

    except Exception as e:
        return f"Error searching knowledge base: {e}"


@tool
def convert_temperature(value: float, from_unit: str, to_unit: str) -> str:
    """Convert temperature between Celsius (C), Fahrenheit (F), and Kelvin (K).

    Args:
        value: The temperature value to convert.
        from_unit: Source unit (C, F, or K).
        to_unit: Target unit (C, F, or K).
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

    return f"{value}°{from_unit} = {result:.1f}°{to_unit}"


@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely.

    Args:
        expression: A mathematical expression like '2 + 2', '10 * 5', or 'sqrt(16)'.
    """
    import math

    try:
        # Define safe functions
        safe_dict = {
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "sqrt": math.sqrt,
            "pow": pow,
            "pi": math.pi,
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
    except Exception as e:
        return f"Error calculating: {e}"


@tool
def get_weather_comfort_level(temperature_c: float, humidity: float) -> str:
    """Determine comfort level based on temperature and humidity.

    Args:
        temperature_c: Temperature in Celsius.
        humidity: Relative humidity percentage (0-100).
    """
    # Calculate heat index approximation
    if temperature_c >= 27 and humidity >= 40:
        heat_index = temperature_c + 0.33 * humidity - 0.7
        if heat_index > 40:
            comfort = "Dangerous - risk of heat stroke"
        elif heat_index > 32:
            comfort = "Very uncomfortable - caution advised"
        elif heat_index > 27:
            comfort = "Uncomfortable - stay hydrated"
        else:
            comfort = "Moderate discomfort"
        return f"Heat index: {heat_index:.1f}°C. Comfort level: {comfort}"
    elif temperature_c < 0:
        if temperature_c < -10:
            comfort = "Very cold - frostbite risk"
        else:
            comfort = "Cold - dress warmly"
        return f"Temperature: {temperature_c}°C. Comfort level: {comfort}"
    else:
        return f"Temperature: {temperature_c}°C. Comfort level: Comfortable"


# ==============================================================================
# Agent Creation
# ==============================================================================

def create_weather_agent():
    """Create the RAG-enhanced weather agent."""
    model = AnthropicModel(
        model_id="claude-3-5-haiku-20241022",
        max_tokens=1024
    )

    agent = Agent(
        model=model,
        tools=[
            search_weather_knowledge,
            convert_temperature,
            calculate,
            get_weather_comfort_level,
        ],
        system_prompt="""You are WeatherBot, an expert weather assistant with access to a comprehensive weather knowledge base.

Your capabilities:
1. **Knowledge Base Search**: Use search_weather_knowledge to find accurate information about weather phenomena, forecasting, safety procedures, and meteorology.
2. **Temperature Conversion**: Convert between Celsius, Fahrenheit, and Kelvin.
3. **Calculations**: Perform mathematical calculations.
4. **Comfort Assessment**: Evaluate weather comfort levels.

Guidelines:
- Always search the knowledge base for factual weather information
- Cite your sources when using information from the knowledge base
- Combine tools when helpful (e.g., convert temperature then assess comfort)
- Be accurate, helpful, and safety-conscious
- If the knowledge base doesn't have information, say so clearly

When responding:
- Start with the most relevant information
- Provide practical advice when appropriate
- Keep responses clear and well-organized"""
    )

    return agent


# ==============================================================================
# Main Demo
# ==============================================================================

def main():
    """Run the RAG agent demo."""
    print("=" * 70)
    print(" Kata 05: RAG-Enhanced Strands Agent - Solution")
    print("=" * 70)

    # Check if documents exist
    if not DOCS_PATH.exists():
        print(f"\nError: Documents not found at {DOCS_PATH}")
        print("Please run Kata 04 first to create the sample documents.")
        return

    # Setup knowledge base
    print("\n1. Setting up knowledge base...")
    setup_knowledge_base()
    print("   Knowledge base ready!")

    # Create agent
    print("\n2. Creating RAG-enhanced agent...")
    agent = create_weather_agent()
    print("   Agent ready!")

    # Test queries
    print("\n" + "=" * 70)
    print(" Testing the Agent")
    print("=" * 70)

    test_queries = [
        # Basic KB query
        "What are the different types of thunderstorms and their dangers?",

        # Safety information
        "What should I do if I'm caught outside during a tornado warning?",

        # Combining KB + tools
        "It's 95°F outside with 80% humidity. Convert to Celsius and tell me if it's safe to exercise outdoors.",

        # Multi-step reasoning
        "Explain the Enhanced Fujita Scale for tornadoes.",

        # Question that might not be in KB
        "What's the current weather in Paris?",
    ]

    for query in test_queries:
        print(f"\nUser: {query}")
        print("-" * 40)
        try:
            response = agent(query)
            print(f"WeatherBot: {response}")
        except Exception as e:
            print(f"Error: {e}")

    # Interactive mode
    print("\n" + "=" * 70)
    print(" Interactive Mode (type 'quit' to exit)")
    print("=" * 70)

    while True:
        try:
            query = input("\nYour question: ").strip()
            if query.lower() in ["quit", "exit", "q"]:
                break
            if not query:
                continue

            response = agent(query)
            print(f"\nWeatherBot: {response}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "=" * 70)
    print(" Kata 05 Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
