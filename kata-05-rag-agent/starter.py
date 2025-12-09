"""
Kata 05: RAG-Enhanced Strands Agent - Starter Template

Combine RAG retrieval with a Strands agent to create an intelligent
weather assistant.

Prerequisites:
    pip install 'strands-agents[anthropic]' llama-index llama-index-embeddings-huggingface
    export ANTHROPIC_API_KEY="your-key-here"
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Path to sample documents (reuse from Kata 04)
DOCS_PATH = Path(__file__).parent.parent / "kata-04-local-rag" / "sample_data" / "weather_docs"

# Global query engine (will be initialized in setup)
query_engine = None


def setup_knowledge_base():
    """Initialize the knowledge base and query engine."""
    global query_engine

    # TODO 1: Import required modules
    # Hint: from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    # Hint: from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    # TODO 2: Create embedding model
    # Hint: embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # TODO 3: Load documents and create index
    # Hint: documents = SimpleDirectoryReader(str(DOCS_PATH)).load_data()
    # Hint: index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)

    # TODO 4: Create query engine
    # Hint: query_engine = index.as_query_engine(similarity_top_k=3)

    pass


# TODO 5: Create the RAG tool using @tool decorator
# Hint: from strands import tool
def search_weather_knowledge(query: str) -> str:
    """Search the weather knowledge base for information.

    Args:
        query: The search query describing what information you need.
    """
    # TODO: Implement the search using query_engine
    # Hint: response = query_engine.query(query)
    # Hint: Return the response with source citations
    pass


# TODO 6: Create additional utility tools
def convert_temperature(value: float, from_unit: str, to_unit: str) -> str:
    """Convert temperature between Celsius and Fahrenheit.

    Args:
        value: The temperature value to convert.
        from_unit: Source unit (C or F).
        to_unit: Target unit (C or F).
    """
    # TODO: Implement temperature conversion
    pass


def calculate(expression: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expression: A mathematical expression.
    """
    # TODO: Implement safe calculation
    pass


def create_weather_agent():
    """Create the RAG-enhanced weather agent."""
    # TODO 7: Import Agent and AnthropicModel
    # Hint: from strands import Agent
    # Hint: from strands.models.anthropic import AnthropicModel

    # TODO 8: Create model and agent with all tools
    # Hint: Agent(model=model, tools=[...], system_prompt="...")

    return None


def main():
    """Run the RAG agent demo."""
    print("=" * 70)
    print(" Kata 05: RAG-Enhanced Strands Agent")
    print("=" * 70)

    # Check if documents exist
    if not DOCS_PATH.exists():
        print(f"\nError: Documents not found at {DOCS_PATH}")
        print("Please run Kata 04 first to create the sample documents.")
        return

    # Setup knowledge base
    print("\n1. Setting up knowledge base...")
    setup_knowledge_base()
    if query_engine is None:
        print("TODO: Implement setup_knowledge_base()")
        return
    print("   Knowledge base ready!")

    # Create agent
    print("\n2. Creating RAG-enhanced agent...")
    agent = create_weather_agent()
    if agent is None:
        print("TODO: Implement create_weather_agent()")
        return
    print("   Agent ready!")

    # Test queries
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
