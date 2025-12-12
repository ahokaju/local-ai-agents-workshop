"""
Kata 04: Local RAG - Solution

This script demonstrates how to implement RAG (Retrieval-Augmented Generation)
programmatically using LlamaIndex with local embeddings and Claude.

Prerequisites:
    pip install llama-index llama-index-llms-anthropic llama-index-embeddings-huggingface chromadb
    export ANTHROPIC_API_KEY="your-key-here"
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.anthropic import Anthropic

load_dotenv()

# Path to sample documents
DOCS_PATH = Path(__file__).parent / "sample_data" / "weather_docs"


def create_embedding_model():
    """
    Create a local embedding model using HuggingFace.

    We use all-MiniLM-L6-v2 which is:
    - Fast and efficient
    - Good quality embeddings
    - Runs locally (no API costs)
    - 384 dimensions
    """
    embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return embed_model


def load_documents(docs_path: Path):
    """
    Load documents from a directory.

    SimpleDirectoryReader automatically handles:
    - Multiple file formats (MD, TXT, PDF, etc.)
    - Recursive directory scanning
    - Document metadata extraction
    """
    if not docs_path.exists():
        raise FileNotFoundError(f"Documents directory not found: {docs_path}")

    documents = SimpleDirectoryReader(
        str(docs_path),
        recursive=True  # Include subdirectories
    ).load_data()

    return documents


def create_index(documents, embed_model):
    """
    Create a vector index from documents.

    The index:
    - Splits documents into chunks
    - Converts chunks to embeddings
    - Stores embeddings for fast retrieval
    """
    # Configure settings
    Settings.embed_model = embed_model

    # Create the index
    index = VectorStoreIndex.from_documents(
        documents,
        embed_model=embed_model,
        show_progress=True  # Show progress bar during indexing
    )

    return index


def create_query_engine(index, llm=None):
    """
    Create a query engine with Claude as the LLM.

    The query engine:
    - Retrieves relevant document chunks
    - Sends them to the LLM with the user's question
    - Returns the generated answer
    """
    if llm is None:
        llm = Anthropic(model="claude-haiku-4-5-20251001")

    query_engine = index.as_query_engine(
        llm=llm,
        similarity_top_k=3,  # Number of chunks to retrieve
    )

    return query_engine


def query_documents(query_engine, question: str):
    """
    Query the documents and return the answer.

    Returns the response object which includes:
    - response.response: The generated answer
    - response.source_nodes: The source documents used
    """
    response = query_engine.query(question)
    return response


def print_response_with_sources(response):
    """Print the response along with source information."""
    print(f"Answer: {response.response}\n")

    if response.source_nodes:
        print("Sources:")
        for i, node in enumerate(response.source_nodes, 1):
            # Get filename from metadata
            filename = node.node.metadata.get("file_name", "Unknown")
            score = node.score if hasattr(node, "score") else "N/A"
            print(f"  {i}. {filename} (relevance: {score:.3f})")


def interactive_mode(query_engine):
    """Run an interactive query session."""
    print("\nEntering interactive mode. Type 'quit' to exit.\n")

    while True:
        question = input("Your question: ").strip()
        if question.lower() in ["quit", "exit", "q"]:
            break
        if not question:
            continue

        print()
        response = query_documents(query_engine, question)
        print_response_with_sources(response)
        print("-" * 40)


def main():
    """Run the RAG demo."""
    print("=" * 70)
    print(" Kata 04: Local RAG with LlamaIndex - Solution")
    print("=" * 70)

    # Check if documents exist
    if not DOCS_PATH.exists():
        print(f"\nError: Documents not found at {DOCS_PATH}")
        print("Please ensure the sample_data/weather_docs folder exists.")
        return

    # Step 1: Create embedding model
    print("\n1. Creating embedding model...")
    embed_model = create_embedding_model()
    print("   Embedding model: sentence-transformers/all-MiniLM-L6-v2")

    # Step 2: Load documents
    print("\n2. Loading documents...")
    documents = load_documents(DOCS_PATH)
    print(f"   Loaded {len(documents)} document chunks")
    for doc in documents[:3]:  # Show first 3
        filename = doc.metadata.get("file_name", "Unknown")
        print(f"   - {filename}")
    if len(documents) > 3:
        print(f"   ... and {len(documents) - 3} more")

    # Step 3: Create index
    print("\n3. Creating vector index...")
    index = create_index(documents, embed_model)
    print("   Index created successfully!")

    # Step 4: Create query engine
    print("\n4. Creating query engine with Claude...")
    query_engine = create_query_engine(index)
    print("   Query engine ready!")

    # Step 5: Test queries
    print("\n" + "=" * 70)
    print(" Testing Queries")
    print("=" * 70)

    test_questions = [
        "What causes thunder?",
        "What are the four main cloud types?",
        "What should I do during a tornado warning?",
        "How is rainfall measured?",
        "What's the difference between a watch and a warning?",
    ]

    for question in test_questions:
        print(f"\nQ: {question}")
        print("-" * 40)
        response = query_documents(query_engine, question)
        print_response_with_sources(response)

    # Step 6: Interactive mode (optional)
    print("\n" + "=" * 70)
    print(" Interactive Mode")
    print("=" * 70)

    try:
        interactive_mode(query_engine)
    except KeyboardInterrupt:
        print("\n\nExiting...")

    print("\n" + "=" * 70)
    print(" Kata 04 Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
