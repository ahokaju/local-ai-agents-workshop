"""
Kata 05: RAG-Enhanced Strands Agent - Bedrock Starter Template

Complete the TODOs to combine RAG retrieval with a Strands agent backed by
AWS Bedrock instead of the Anthropic API directly.

Two Bedrock-specific changes vs starter.py:
  1. BedrockLLM (same custom wrapper as kata-04) for LlamaIndex query engine
  2. BedrockModel for the Strands agent

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

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")
DEFAULT_MODEL = "eu.anthropic.claude-sonnet-4-5-20250929-v1:0"

# Path to sample documents (reuse from Kata 04)
DOCS_PATH = Path(__file__).parent.parent / "kata-04-local-rag" / "sample_data" / "weather_docs"

# Global query engine (will be initialized in setup)
query_engine = None


# ==============================================================================
# TODO 1-4: Implement BedrockLLM (same as kata-04 — copy your solution here)
# ==============================================================================
#
# Imports you'll need:
#   import boto3
#   from llama_index.core.llms import CustomLLM, CompletionResponse, CompletionResponseGen, LLMMetadata
#
# TODO 1: Define BedrockLLM(CustomLLM) with model_id, region_name, max_new_tokens fields
# TODO 2: Implement metadata property → LLMMetadata(context_window=200000, ...)
# TODO 3: Implement complete(prompt, **kwargs) → boto3 converse() → CompletionResponse
# TODO 4: Implement stream_complete(prompt, **kwargs) → boto3 converse_stream() → generator


def setup_knowledge_base():
    """Initialize the knowledge base and query engine using BedrockLLM."""
    global query_engine

    # TODO 5: Import required LlamaIndex modules
    # from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
    # from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    # TODO 6: Create HuggingFace embedding model (unchanged from starter.py)
    # embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # TODO 7: Load documents and create vector index (unchanged from starter.py)
    # documents = SimpleDirectoryReader(str(DOCS_PATH)).load_data()
    # Settings.embed_model = embed_model
    # index = VectorStoreIndex.from_documents(documents, embed_model=embed_model, show_progress=True)

    # TODO 8: Create query engine using BedrockLLM instead of the Anthropic LLM package
    # llm = BedrockLLM(model_id=DEFAULT_MODEL, region_name=AWS_REGION)
    # query_engine = index.as_query_engine(llm=llm, similarity_top_k=3)

    pass


# ==============================================================================
# Tool Definitions (identical to starter.py — add @tool decorator and implement)
# ==============================================================================

# TODO 9: Add @tool decorator
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
    # TODO: Implement using the global query_engine
    # response = query_engine.query(query)
    # Include source citations in the return value
    pass


# TODO 10: Add @tool decorator
def convert_temperature(value: float, from_unit: str, to_unit: str) -> str:
    """Convert temperature between Celsius (C), Fahrenheit (F), and Kelvin (K).

    Args:
        value: The temperature value to convert.
        from_unit: Source unit (C, F, or K).
        to_unit: Target unit (C, F, or K).
    """
    # TODO: Implement temperature conversion
    pass


# TODO 11: Add @tool decorator
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely.

    Args:
        expression: A mathematical expression like '2 + 2', '10 * 5', or 'sqrt(16)'.
    """
    # TODO: Implement safe calculation
    pass


def create_weather_agent():
    """Create the RAG-enhanced weather agent backed by AWS Bedrock."""
    # TODO 12: Import Agent from strands and BedrockModel from strands.models.bedrock
    # from strands import Agent
    # from strands.models.bedrock import BedrockModel

    # TODO 13: Create BedrockModel and Agent with all tools
    # model = BedrockModel(model_id=DEFAULT_MODEL, region_name=AWS_REGION, max_tokens=1024)
    # agent = Agent(model=model, tools=[search_weather_knowledge, convert_temperature, calculate], system_prompt="...")
    # Key difference from starter.py: BedrockModel replaces AnthropicModel

    return None


def main():
    """Run the RAG agent demo."""
    print("=" * 70)
    print(" Kata 05: RAG-Enhanced Strands Agent - Bedrock Starter")
    print(f" Region: {AWS_REGION}")
    print("=" * 70)

    if not DOCS_PATH.exists():
        print(f"\nError: Documents not found at {DOCS_PATH}")
        print("Please run Kata 04 first to create the sample documents.")
        return

    print("\n1. Setting up knowledge base...")
    setup_knowledge_base()
    if query_engine is None:
        print("TODO: Implement setup_knowledge_base() with BedrockLLM")
        return
    print("   Knowledge base ready!")

    print("\n2. Creating RAG-enhanced agent...")
    agent = create_weather_agent()
    if agent is None:
        print("TODO: Implement create_weather_agent() with BedrockModel")
        return
    print("   Agent ready!")

    print("\n" + "=" * 70)
    print(" Testing the Agent")
    print("=" * 70)

    test_queries = [
        "What are the different types of thunderstorms?",
        "What should I do during a tornado warning?",
        "Convert 86°F to Celsius and tell me if that's considered hot weather",
        "What's the difference between a weather watch and warning?",
    ]

    for query in test_queries:
        print(f"\nUser: {query}")
        print("-" * 40)
        try:
            response = agent(query)
            print(f"Agent: {response}")
        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "=" * 70)
    print(" Kata 05 Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
