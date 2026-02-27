"""
Kata 04: Local RAG - Bedrock Starter Template

Complete the TODOs to implement RAG (Retrieval-Augmented Generation) using
LlamaIndex with AWS Bedrock as the LLM backend.

The key difference from starter.py: LlamaIndex has no built-in Bedrock LLM
package, so you must implement a custom BedrockLLM(CustomLLM) wrapper around
boto3.  Embeddings stay HuggingFace (free, local — no change needed).

Prerequisites:
    pip install llama-index llama-index-embeddings-huggingface chromadb boto3 python-dotenv

    Set these environment variables before running:
        AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
        AWS_REGION=us-east-1   (must match the region your key was created in)

    boto3 picks up both variables automatically — no extra configuration needed.
    No extra llama-index LLM package is needed: BedrockLLM wraps boto3 directly.

    To use eu-central-1: set AWS_REGION=eu-central-1 and change the model ID
    prefix from "us." to "eu." (e.g. "eu.anthropic.claude-sonnet-4-5-20250929-v1:0").
"""

import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DEFAULT_MODEL = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

# Path to sample documents
DOCS_PATH = Path(__file__).parent / "sample_data" / "weather_docs"


# ==============================================================================
# TODO 1-4: Implement BedrockLLM — a custom LlamaIndex LLM backed by boto3
# ==============================================================================
#
# LlamaIndex requires an LLM object to generate answers from retrieved chunks.
# Since there's no official Bedrock package for llama-index, we subclass CustomLLM.
#
# Imports you'll need:
#   import boto3
#   from llama_index.core.llms import CustomLLM, CompletionResponse, CompletionResponseGen, LLMMetadata

# TODO 1: Define BedrockLLM class that extends CustomLLM
# Hint:
#   class BedrockLLM(CustomLLM):
#       model_id: str = DEFAULT_MODEL
#       region_name: str = AWS_REGION
#       max_new_tokens: int = 1024
#
#       @property
#       def metadata(self) -> LLMMetadata:
#           ...
#
#       def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
#           ...
#
#       def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
#           ...

# TODO 2: Implement the metadata property
# Return LLMMetadata with:
#   context_window=200000, num_output=self.max_new_tokens, model_name=self.model_id
# Hint: from llama_index.core.llms import LLMMetadata

# TODO 3: Implement complete(prompt, **kwargs)
# Steps:
#   1. Create boto3 client: boto3.client("bedrock-runtime", region_name=self.region_name)
#   2. Call client.converse(modelId=self.model_id,
#                           messages=[{"role": "user", "content": [{"text": prompt}]}],
#                           inferenceConfig={"maxTokens": self.max_new_tokens})
#   3. Extract text: response["output"]["message"]["content"][0]["text"]
#   4. Return CompletionResponse(text=text)

# TODO 4: Implement stream_complete(prompt, **kwargs)
# Steps:
#   1. Call client.converse_stream() with the same params as complete()
#   2. Define a generator that iterates response["stream"]
#   3. Yield CompletionResponse(text=accumulated, delta=chunk) for "contentBlockDelta" events
#   4. Return the generator


def create_embedding_model():
    """Create a local embedding model using HuggingFace (unchanged from starter.py)."""
    # TODO 5: Import HuggingFaceEmbedding and create the model
    # Hint: from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    # Hint: embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    embed_model = None

    return embed_model


def load_documents(docs_path: Path):
    """Load documents from a directory (unchanged from starter.py)."""
    # TODO 6: Import SimpleDirectoryReader and load documents
    # Hint: from llama_index.core import SimpleDirectoryReader
    # Hint: documents = SimpleDirectoryReader(str(docs_path), recursive=True).load_data()
    documents = []

    return documents


def create_index(documents, embed_model):
    """Create a vector index from documents (unchanged from starter.py)."""
    # TODO 7: Import VectorStoreIndex and Settings, then create the index
    # Hint: from llama_index.core import VectorStoreIndex, Settings
    # Hint: Settings.embed_model = embed_model
    # Hint: index = VectorStoreIndex.from_documents(documents, embed_model=embed_model, show_progress=True)
    index = None

    return index


def create_query_engine(index):
    """Create a query engine using BedrockLLM instead of the Anthropic LLM package."""
    # TODO 8: Instantiate BedrockLLM and pass it to the query engine
    # Hint: llm = BedrockLLM(model_id=DEFAULT_MODEL, region_name=AWS_REGION)
    # Hint: query_engine = index.as_query_engine(llm=llm, similarity_top_k=3)
    # Note: No llama-index-llms-anthropic import needed — BedrockLLM wraps boto3 directly
    query_engine = None

    return query_engine


def query_documents(query_engine, question: str):
    """Query the documents and return the answer (unchanged from starter.py)."""
    # TODO 9: Execute the query
    # Hint: response = query_engine.query(question)
    response = None

    return response


def main():
    """Run the RAG demo."""
    print("=" * 70)
    print(" Kata 04: Local RAG with LlamaIndex - Bedrock Starter")
    print(f" Region: {AWS_REGION}")
    print("=" * 70)

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
    print("\n4. Creating query engine with Bedrock Claude...")
    query_engine = create_query_engine(index)
    if not query_engine:
        print("TODO: Implement create_query_engine() with BedrockLLM")
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
