# Kata 04: Local RAG with LlamaIndex

## Objective

Learn to implement Retrieval-Augmented Generation (RAG) programmatically using LlamaIndex with local embeddings and Claude.

## Learning Goals

- Understand RAG architecture and why it's useful
- Use LlamaIndex for document loading and indexing
- Configure local embeddings (HuggingFace)
- Create a searchable vector index
- Query documents using natural language with Claude

## Prerequisites

- Completed Kata 01-03
- Anthropic API key configured
- Sample documents (provided in `sample_data/`)

## Time Estimate

30-40 minutes

## Difficulty

**Intermediate**

---

## Background

### What is RAG?

Retrieval-Augmented Generation combines:
1. **Retrieval**: Search relevant documents based on user query
2. **Generation**: Use retrieved context to generate accurate answers

```

   Query        Search        Retrieved
      |          Index         Context
      v            |              |
+----------+  +----------+  +----------+
|  "What   |->| Vector   |->| Relevant |
|  causes  |  | Search   |  |  Chunks  |
| thunder?"|  +----------+  +----+-----+
+----------+                     |
                                 v
                    +------------------------+
                    |   LLM (Claude)         |
                    |   Query + Context      |
                    |          |             |
                    |   Accurate Answer      |
                    +------------------------+
```

### Why Use RAG?

| Without RAG | With RAG |
|-------------|----------|
| Limited to training data | Access to your documents |
| May hallucinate facts | Grounded in actual content |
| No source attribution | Can cite sources |
| Can't update knowledge | Easy to update documents |

### RAG Components

1. **Document Loader**: Reads files (PDF, MD, TXT, etc.)
2. **Text Splitter**: Chunks documents into manageable pieces
3. **Embedding Model**: Converts text to vectors
4. **Vector Store**: Stores and searches embeddings
5. **LLM**: Generates responses using retrieved context

---

## Setup

```bash
pip install llama-index llama-index-llms-anthropic llama-index-embeddings-huggingface chromadb
```

---

## Level 1: Challenge

Implement a RAG system that:

1. Loads the weather documents from `sample_data/weather_docs/`
2. Creates embeddings using a local HuggingFace model
3. Builds a searchable vector index
4. Queries the index and generates answers with Claude
5. Shows source attribution for answers

### Success Criteria

- [ ] Documents are loaded successfully
- [ ] Local embeddings are generated (no API costs)
- [ ] Vector index is created
- [ ] Queries return relevant, accurate answers
- [ ] Source documents are shown with answers

---

## Level 2: Step-by-Step Guide

### Step 1: Create the Embedding Model

```python
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Use local embeddings - free, no API costs!
embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
```

**Why this model?**
- Fast and efficient
- Good quality embeddings
- Runs locally (free)
- 384 dimensions (compact)

### Step 2: Load Documents

```python
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader(
    "./sample_data/weather_docs",
    recursive=True
).load_data()

print(f"Loaded {len(documents)} document chunks")
```

### Step 3: Create the Vector Index

```python
from llama_index.core import VectorStoreIndex, Settings

# Set the embedding model globally
Settings.embed_model = embed_model

# Create index from documents
index = VectorStoreIndex.from_documents(
    documents,
    embed_model=embed_model,
    show_progress=True
)
```

### Step 4: Create Query Engine with Claude

```python
from llama_index.llms.anthropic import Anthropic

llm = Anthropic(model="claude-haiku-4-5-20251001")

query_engine = index.as_query_engine(
    llm=llm,
    similarity_top_k=3  # Retrieve top 3 most relevant chunks
)
```

### Step 5: Query and Display Results

```python
question = "What causes thunder?"
response = query_engine.query(question)

print(f"Answer: {response.response}")
print("\nSources:")
for node in response.source_nodes:
    filename = node.node.metadata.get("file_name", "Unknown")
    print(f"  - {filename}")
```

---

## Testing Your RAG

Test with these questions:

**Factual Questions (should find in documents)**
```
Q: What are the main cloud types?
Expected: Should mention cumulus, stratus, cirrus, cumulonimbus

Q: What does METAR stand for?
Expected: Should describe airport weather format

Q: What's the Enhanced Fujita Scale?
Expected: Should describe tornado rating system EF0-EF5
```

**Questions Requiring Synthesis**
```
Q: I'm planning an outdoor event. What weather factors should I monitor?
Expected: Should mention precipitation, wind, severe weather watches/warnings

Q: Compare thunderstorm types and their dangers.
Expected: Should contrast ordinary, multi-cell, and supercell storms
```

**Questions Outside Document Scope**
```
Q: What's the weather in Paris today?
Expected: Should acknowledge it doesn't have real-time data
```

---

## Expected Output

```
======================================================================
 Kata 04: Local RAG with LlamaIndex - Solution
======================================================================

1. Creating embedding model...
   Embedding model: sentence-transformers/all-MiniLM-L6-v2

2. Loading documents...
   Loaded 3 document chunks
   - weather_faq.md
   - forecast_guide.md
   - severe_weather.md

3. Creating vector index...
   Index created successfully!

4. Creating query engine with Claude...
   Query engine ready!

======================================================================
 Testing Queries
======================================================================

Q: What causes thunder?
----------------------------------------
Answer: Thunder is caused by the rapid expansion of air heated by
lightning. When lightning strikes, it heats the air to around 30,000K,
causing the air to expand rapidly and create a shock wave that we
hear as thunder.

Sources:
  1. weather_faq.md (relevance: 0.812)
```

---

## Key Concepts

### Embedding Models

Embeddings convert text to numerical vectors that capture meaning:
- Similar concepts have similar vectors
- Enables semantic search (not just keyword matching)

Popular local models:
- `all-MiniLM-L6-v2` - Fast, good quality, 384 dimensions
- `all-mpnet-base-v2` - Better quality, slower, 768 dimensions

### Chunking Strategy

How documents are split affects retrieval quality:
- **Too small**: Loses context
- **Too large**: Includes irrelevant information
- **Typical**: 256-1024 tokens with some overlap

### Vector Stores

- **In-memory** (default) - Simple, good for small datasets
- **ChromaDB** - Local, persistent, easy to use
- **FAISS** - Fast, good for large datasets

---

## Extension Challenges

1. **Add persistence**: Save the index to disk with ChromaDB
2. **Compare embedding models**: Try different HuggingFace models
3. **Implement chat history**: Allow follow-up questions
4. **Add metadata filtering**: Filter by document type
5. **Tune retrieval**: Experiment with chunk size and top_k

---

## Troubleshooting

### Import Errors

```bash
pip install llama-index llama-index-llms-anthropic llama-index-embeddings-huggingface
```

### Memory Issues with Embeddings

```python
# Use smaller batch size
embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    embed_batch_size=10  # Smaller batches
)
```

### First Run is Slow

First run downloads the embedding model (~100MB). Pre-download with:

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### Poor Answer Quality

- Increase `similarity_top_k` to retrieve more context
- Check documents were loaded correctly
- Try rephrasing your question

---

## Resources

- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [RAG Explained (AWS)](https://aws.amazon.com/what-is/retrieval-augmented-generation/)
- [HuggingFace Sentence Transformers](https://www.sbert.net/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
