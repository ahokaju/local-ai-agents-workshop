# Kata 12: AgentCore Memory

## Objective

Give agents persistent long-term memory using AgentCore Memory. Without memory, every conversation starts from scratch. With AgentCore Memory, the agent can recall facts, preferences, and context from previous sessions — enabling personalized, continuity-aware interactions.

## Learning Goals

- Understand the difference between short-term (in-session) and long-term (cross-session) memory
- Use `MemoryManager` + `get_or_create_memory()` to provision a memory store
- Configure `SemanticStrategy` for fact extraction and semantic retrieval
- Use `MemorySessionManager` + `create_memory_session()` for session-scoped state
- Store conversation history with `ConversationalMessage` / `MessageRole`
- Retrieve cross-session memories with `search_long_term_memories()`

## Prerequisites

- Completed Kata 10 (AgentCore Runtime) — understand AgentCore basics
- AWS account with Bedrock + AgentCore Memory enabled
- `AWS_BEARER_TOKEN_BEDROCK` and `AWS_REGION` environment variables set

```bash
pip install bedrock-agentcore bedrock-agentcore-starter-toolkit boto3 python-dotenv
export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
export AWS_REGION=us-east-1
```

## Time Estimate

30–40 minutes

> **First run note:** The memory store takes ~3 minutes to reach `ACTIVE` status on creation (`get_or_create_memory()` polls internally — you will see `[CREATING]` status printed until it becomes `[ACTIVE]`). Subsequent runs reuse the existing store and start instantly.

## Difficulty

⭐⭐⭐ (Advanced — involves async memory extraction with polling)

---

## Background

### Short-term vs Long-term Memory

| Type | Scope | Storage | Retrieval |
|------|-------|---------|-----------|
| Short-term | Current session | In-memory | Automatic (conversation history) |
| Long-term | Cross-session | AgentCore Memory store | Semantic search |

### How AgentCore Memory Works

```
Session 1                          AgentCore Memory
┌──────────────────┐               ┌──────────────────────────┐
│ User: "I'm Alice,│               │  Semantic Strategy        │
│  cloud architect"│──add_turns()──▶  Extracts facts:          │
│ Agent: "Hello!"  │               │  - Name: Alice            │
│ User: "IoT on AWS│               │  - Role: cloud architect  │
│  with Python+CDK"│               │  - Project: IoT pipeline  │
└──────────────────┘               │  - Prefs: Python, CDK     │
                                   └────────────┬─────────────┘
Session 2                                        │
┌──────────────────┐                             │
│ Query: "Who is   │◀──search_long_term_memories()─┘
│  this user?"     │
│ → Alice, cloud   │
│   architect, IoT │
└──────────────────┘
```

### SemanticStrategy

`SemanticStrategy` instructs AgentCore to:
1. **Extract** key facts from conversation turns (name, preferences, topics, tasks)
2. **Embed** them as semantic vectors
3. **Index** them in the memory namespace for the actor
4. **Retrieve** them via cosine similarity when `search_long_term_memories()` is called

### Namespace Template

The namespace `"/strategies/{memoryStrategyId}/actors/{actorId}/"` scopes memories per actor (user). `{memoryStrategyId}` and `{actorId}` are replaced at runtime — memories for "alice" don't mix with memories for "bob".

---

## Level 1: Challenge

Build a Python script that:

1. Provisions an AgentCore Memory store with `SemanticStrategy`
2. Simulates Session 1: stores 4+ conversation turns introducing a user (name, role, project, tech preferences)
3. Waits 30 seconds for async long-term memory extraction
4. Simulates Session 2: uses `search_long_term_memories()` to recall what was learned in Session 1
5. Prints the retrieved memories with confidence scores

### Success Criteria

- [ ] Memory store reaches `ACTIVE` status
- [ ] Session 1 stores a realistic conversation about the user
- [ ] Session 2 retrieves relevant facts (name, role, project, preferences)
- [ ] Results include confidence scores from semantic search

---

## Level 2: Step-by-Step Guide

### Step 1: Import Classes

```python
from bedrock_agentcore_starter_toolkit.operations.memory.manager import MemoryManager
from bedrock_agentcore_starter_toolkit.operations.memory.models.strategies import SemanticStrategy
from bedrock_agentcore.memory.session import MemorySessionManager
from bedrock_agentcore.memory.constants import ConversationalMessage, MessageRole
```

### Step 2: Provision Memory Store

```python
memory_manager = MemoryManager(region_name=AWS_REGION)

memory = memory_manager.get_or_create_memory(
    name="kata12_workshop_memory",
    description="Demo long-term memory",
    strategies=[
        SemanticStrategy(
            name="semanticMemory",
            namespaces=["/strategies/{memoryStrategyId}/actors/{actorId}/"]
        )
    ]
)
memory_id = memory["id"]

# Poll until ACTIVE
while memory_manager.get_memory(memory_id)["status"] != "ACTIVE":
    time.sleep(5)
```

### Step 3: Session 1 — Store Turns

```python
session_mgr = MemorySessionManager(memory_id=memory_id, region_name=AWS_REGION)
session1 = session_mgr.create_memory_session(actor_id="alice", session_id="session-001")

session1.add_turns(messages=[
    ConversationalMessage("Hi! My name is Alice and I'm a cloud architect at Acme.", MessageRole.USER),
    ConversationalMessage("Hello Alice! Great to meet you.", MessageRole.ASSISTANT),
    ConversationalMessage("I'm building a real-time data pipeline for IoT sensor data on AWS.", MessageRole.USER),
    ConversationalMessage("AWS IoT Core and Kinesis work well for that.", MessageRole.ASSISTANT),
    ConversationalMessage("I prefer Python and use CDK for infrastructure as code.", MessageRole.USER),
    ConversationalMessage("Python + CDK is a great combination for IoT pipelines.", MessageRole.ASSISTANT),
])

# Allow time for async long-term memory extraction
time.sleep(30)
```

### Step 4: Session 2 — Semantic Recall

```python
session2 = session_mgr.create_memory_session(actor_id="alice", session_id="session-002")

results = session2.search_long_term_memories(
    query="Who is this user and what are they working on?",
    namespace_prefix="/",
    top_k=3
)

for r in results:
    score = r.get("score", "n/a")
    text = r["content"]["text"]
    print(f"[{score:.3f}] {text}")
```

---

## Running the Solution

> **Run the script twice to see full memory retrieval.**
> Long-term memory extraction is asynchronous — after the first run stores session-001 turns and waits 30 s, Bedrock may still be extracting facts in the background. The second run reuses the existing (ACTIVE) memory store and session-002 will find the fully extracted facts.

```bash
# First run: creates memory store (~3 min), stores turns, waits 30 s, attempts recall
python solution.py

# Second run: reuses store instantly, session-002 retrieves richer extracted facts
python solution.py
```

Expected output:
```
1. Provisioning memory store
Provisioning memory store: 'kata12_workshop_memory'
Memory ID: mem-abc123
[CREATING] [CREATING] [ACTIVE]
Memory store is ACTIVE.

2. Simulating Session 1 (storing turns)
Stored 6 conversation turns in session-001.
  User: Hi! My name is Alice and I'm a cloud architect at Acme.
  Agent: Hello Alice! Great to meet you.
  ...
Waiting for long-term memory extraction (30 s)...

3. Simulating Session 2 (semantic recall)
Query: Who is this user and what is their job role?
  [1] (score=0.923) Alice is a cloud architect at Acme.
  [2] (score=0.871) The user is building an IoT data pipeline on AWS.

Query: What programming language and IaC tool does the user prefer?
  [1] (score=0.945) Alice prefers Python and uses AWS CDK for infrastructure.
```

> **Tip:** Run the script twice. The second run will find richer memories because extraction has had more time after the first run.

---

## Cleanup

When you are done with the kata, delete the AgentCore Memory store to avoid ongoing costs:

```bash
python cleanup.py
```

This reads the memory ID from `kata12_state.json` (written by `solution.py` / `starter.py`) and deletes the memory store. The state file is gitignored — each participant manages their own resources.

---

## Extension Challenges

1. **Multiple actors**: Add memories for "bob" and verify alice's search doesn't return bob's data
2. **Integrate with agent**: Pass retrieved memories as context in a Strands agent's system prompt
3. **Memory update**: Store new facts in session-003 and verify session-004 gets updated information
4. **Summary strategy**: Explore `SummaryStrategy` — extracts session summaries instead of individual facts

---

## Key Concepts

### Why Not Just Use a Database?

You could store conversation history in DynamoDB or Redis. AgentCore Memory adds:
- **Automatic fact extraction** — no need to parse transcripts manually
- **Semantic search** — retrieve memories by meaning, not keyword matching
- **Actor isolation** — automatic scoping per user/session
- **Managed service** — no vector DB to operate

### Memory Extraction Latency

Long-term memory extraction is asynchronous. After `add_turns()`, Bedrock processes the conversation and extracts facts in the background. This typically takes 10–60 seconds. The `time.sleep(30)` in the solution approximates this wait — in production, you'd poll or use event notifications.

---

## Resources

- [AgentCore Memory Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html)
- [bedrock-agentcore-starter-toolkit](https://pypi.org/project/bedrock-agentcore-starter-toolkit/)
- [SemanticStrategy Reference](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory-strategies.html)
