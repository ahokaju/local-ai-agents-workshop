"""
Kata 05: RAG-Enhanced Strands Agent - Bedrock Solution

This script mirrors solution.py but uses AWS Bedrock as the inference provider
instead of the Anthropic API directly.

Prerequisites:
    pip install 'strands-agents[bedrock]' llama-index llama-index-embeddings-huggingface boto3 python-dotenv

    Set these environment variables before running:
        AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
        AWS_REGION=eu-central-1   (must match the region your key was created in)

    boto3 picks up both variables automatically — no extra configuration needed.
    No extra llama-index LLM package is needed: BedrockLLM wraps boto3 directly.
"""

import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
import boto3
from strands import Agent, tool
from strands.models.bedrock import BedrockModel
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.llms import CustomLLM, CompletionResponse, CompletionResponseGen, LLMMetadata
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DEFAULT_MODEL = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"


class BedrockLLM(CustomLLM):
    """LlamaIndex LLM backed by AWS Bedrock via boto3 — no extra LLM package needed."""

    model_id: str = DEFAULT_MODEL
    region_name: str = AWS_REGION
    max_new_tokens: int = 1024

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=200000,
            num_output=self.max_new_tokens,
            model_name=self.model_id,
        )

    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        client = boto3.client("bedrock-runtime", region_name=self.region_name)
        response = client.converse(
            modelId=self.model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": self.max_new_tokens},
        )
        text = response["output"]["message"]["content"][0]["text"]
        return CompletionResponse(text=text)

    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        client = boto3.client("bedrock-runtime", region_name=self.region_name)
        response = client.converse_stream(
            modelId=self.model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": self.max_new_tokens},
        )

        def gen() -> CompletionResponseGen:
            full_text = ""
            for event in response["stream"]:
                if "contentBlockDelta" in event:
                    delta_text = event["contentBlockDelta"]["delta"].get("text", "")
                    full_text += delta_text
                    yield CompletionResponse(text=full_text, delta=delta_text)

        return gen()


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

    print("   Creating query engine with Bedrock Claude...")
    llm = BedrockLLM(
        model_id=DEFAULT_MODEL,
        region_name=AWS_REGION
    )
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

        result = str(response.response)

        if response.source_nodes:
            sources = []
            for node in response.source_nodes:
                filename = node.node.metadata.get("file_name", "unknown")
                score = node.score if hasattr(node, "score") else 0
                sources.append(f"{filename} (relevance: {score:.2f})")
            unique_sources = list(dict.fromkeys(sources))
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

    return f"{value}°{from_unit} = {result:.1f}°{to_unit}"


@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely.

    Args:
        expression: A mathematical expression like '2 + 2', '10 * 5', or 'sqrt(16)'.
    """
    import math

    try:
        safe_dict = {
            "abs": abs, "round": round, "min": min, "max": max, "sum": sum,
            "sqrt": math.sqrt, "pow": pow, "pi": math.pi,
        }

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
    """Create the RAG-enhanced weather agent backed by AWS Bedrock."""
    model = BedrockModel(
        model_id=DEFAULT_MODEL,
        region_name=AWS_REGION,
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
    print(" Kata 05: RAG-Enhanced Strands Agent - Bedrock Solution")
    print(f" Region: {AWS_REGION}")
    print("=" * 70)

    if not DOCS_PATH.exists():
        print(f"\nError: Documents not found at {DOCS_PATH}")
        print("Please run Kata 04 first to create the sample documents.")
        return

    print("\n1. Setting up knowledge base...")
    setup_knowledge_base()
    print("   Knowledge base ready!")

    print("\n2. Creating RAG-enhanced agent...")
    agent = create_weather_agent()
    print("   Agent ready!")

    print("\n" + "=" * 70)
    print(" Testing the Agent")
    print("=" * 70)

    test_queries = [
        "What are the different types of thunderstorms and their dangers?",
        "What should I do if I'm caught outside during a tornado warning?",
        "It's 95°F outside with 80% humidity. Convert to Celsius and tell me if it's safe to exercise outdoors.",
        "Explain the Enhanced Fujita Scale for tornadoes.",
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
