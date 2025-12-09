"""
Kata 04: Local RAG - Starter Template

This script demonstrates how to implement RAG (Retrieval-Augmented Generation)
programmatically using LlamaIndex with local embeddings.

Prerequisites:
    pip install llama-index llama-index-llms-anthropic llama-index-embeddings-huggingface chromadb
    export ANTHROPIC_API_KEY="your-key-here"
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Path to sample documents
DOCS_PATH = Path(__file__).parent / "sample_data" / "weather_docs"


def create_embedding_model():
    """Create a local embedding model using HuggingFace."""
    # TODO 1: Import HuggingFaceEmbedding
    # Hint: from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    # TODO 2: Create the embedding model
    # Hint: Use model_name="sentence-transformers/all-MiniLM-L6-v2"
    embed_model = None

    return embed_model


def load_documents(docs_path: Path):
    """Load documents from a directory."""
    # TODO 3: Import SimpleDirectoryReader
    # Hint: from llama_index.core import SimpleDirectoryReader

    # TODO 4: Load documents from the path
    # Hint: documents = SimpleDirectoryReader(str(docs_path)).load_data()
    documents = []

    return documents


def create_index(documents, embed_model):
    """Create a vector index from documents."""
    # TODO 5: Import VectorStoreIndex
    # Hint: from llama_index.core import VectorStoreIndex

    # TODO 6: Create the index
    # Hint: index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
    index = None

    return index


def create_query_engine(index):
    """Create a query engine with Claude as the LLM."""
    # TODO 7: Import Anthropic from llama_index
    # Hint: from llama_index.llms.anthropic import Anthropic

    # TODO 8: Create LLM and query engine
    # Hint: llm = Anthropic(model="claude-3-5-haiku-20241022")
    # Hint: query_engine = index.as_query_engine(llm=llm)
    query_engine = None

    return query_engine


def query_documents(query_engine, question: str):
    """Query the documents and return the answer."""
    # TODO 9: Execute the query
    # Hint: response = query_engine.query(question)
    response = None

    return response


def main():
    """Run the RAG demo."""
    print("=" * 70)
    print(" Kata 04: Local RAG with LlamaIndex")
    print("=" * 70)

    # Check if documents exist
    if not DOCS_PATH.exists():
        print(f"\nError: Documents not found at {DOCS_PATH}")
        print("Please ensure the sample_data/weather_docs folder exists.")
        return

    # Step 1: Create embedding model
    print("\n1. Creating embedding model...")
    embed_model = create_embedding_model()
    if not embed_model:
        print("TODO: Implement create_embedding_model()")
        return
    print("   Embedding model created!")

    # Step 2: Load documents
    print("\n2. Loading documents...")
    documents = load_documents(DOCS_PATH)
    if not documents:
        print("TODO: Implement load_documents()")
        return
    print(f"   Loaded {len(documents)} documents")

    # Step 3: Create index
    print("\n3. Creating vector index (this may take a moment)...")
    index = create_index(documents, embed_model)
    if not index:
        print("TODO: Implement create_index()")
        return
    print("   Index created!")

    # Step 4: Create query engine
    print("\n4. Creating query engine...")
    query_engine = create_query_engine(index)
    if not query_engine:
        print("TODO: Implement create_query_engine()")
        return
    print("   Query engine ready!")

    # Step 5: Test queries
    print("\n5. Testing queries...")
    print("-" * 40)

    test_questions = [
        "What causes thunder?",
        "What are the main cloud types?",
        "What should I do during a tornado warning?",
    ]

    for question in test_questions:
        print(f"\nQ: {question}")
        response = query_documents(query_engine, question)
        if response:
            print(f"A: {response}")
        else:
            print("TODO: Implement query_documents()")
            break

    print("\n" + "=" * 70)
    print(" Kata 04 Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
