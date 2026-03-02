# Local AI Agents Workshop

## Overview

This workshop teaches you to build AI agents locally using:
- **Anthropic API** directly (no AWS required)
- **Strands Agents SDK** (open-source agent framework)
- **Local RAG** with LlamaIndex and HuggingFace embeddings
- **Atlassian Integration** (Jira/Confluence)
- **GitHub Integration** (PR workflows with PyGithub)
- **MCP Protocol** for standardized tool integration
- **AWS AgentCore** (Runtime, Memory, Code Interpreter, Gateway)
- **Bedrock Knowledge Bases** with S3 Vectors

**Duration**: ~7-9 hours (all katas) or pick the track you need
**Level**: Beginner to Advanced
**Format**: 13 hands-on katas with progressive difficulty

---

## Why This Session?

This session complements the main AWS Bedrock workshop by:

| Aspect | AWS Bedrock Workshop | This Session |
|--------|---------------------|--------------|
| **API** | AWS Bedrock Runtime | Anthropic API directly |
| **Authentication** | AWS IAM / credentials | Simple API key |
| **Agents** | Bedrock Agents | Strands Agents SDK |
| **RAG** | OpenSearch Serverless | LlamaIndex (local) |
| **Embeddings** | Titan Embeddings | HuggingFace (free, local) |
| **External Tools** | Lambda functions | Atlassian API, MCP |
| **Infrastructure** | AWS managed | Local machine |
| **Best for** | Production AWS apps | Prototyping, local dev |

---

## Learning Path

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     LOCAL AI AGENTS WORKSHOP                             │
├─────────────────────────────────────────────────────────────────────────┤
│  Track 1: Anthropic + Strands (no AWS required)                         │
│                                                                          │
│  Kata 01          Kata 02          Kata 03                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                          │
│  │Anthropic │───▶│ Strands  │───▶│ Strands  │                          │
│  │   API    │    │  Intro   │    │  Tools   │                          │
│  └──────────┘    └──────────┘    └──────────┘                          │
│      ⭐              ⭐             ⭐⭐                                  │
│    20 min          25 min         35 min                                │
│                                                                          │
│  Kata 04          Kata 05                                               │
│  ┌──────────┐    ┌──────────┐                                          │
│  │  Local   │───▶│   RAG    │                                          │
│  │   RAG    │    │  Agent   │                                          │
│  └──────────┘    └──────────┘                                          │
│     ⭐⭐            ⭐⭐⭐                                                 │
│    40 min          45 min                                               │
│                                                                          │
│  Kata 06          Kata 07          Kata 08                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                          │
│  │Atlassian │───▶│Atlassian │    │ GitHub   │                          │
│  │  Agent   │    │   MCP    │    │ PR Agent │                          │
│  └──────────┘    └──────────┘    └──────────┘                          │
│     ⭐⭐            ⭐⭐⭐            ⭐⭐                                  │
│    40 min          45 min         35 min                                │
│                                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│  Track 2: AWS Bedrock + AgentCore (AWS credentials required)            │
│                                                                          │
│  Kata 09          Kata 10          Kata 11                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                          │
│  │ Bedrock  │───▶│AgentCore │───▶│AgentCore │                          │
│  │Knowledge │    │ Runtime  │    │  Memory  │                          │
│  │   Base   │    │          │    │          │                          │
│  └──────────┘    └──────────┘    └──────────┘                          │
│     ⭐⭐⭐           ⭐⭐             ⭐⭐⭐                                 │
│    45-60 min       20 min         30-40 min                             │
│                                                                          │
│  Kata 12          Kata 13                                               │
│  ┌──────────┐    ┌──────────┐                                          │
│  │AgentCore │───▶│AgentCore │                                          │
│  │  Code    │    │ Gateway  │                                          │
│  │Interpret.│    │ (MCP)    │                                          │
│  └──────────┘    └──────────┘                                          │
│     ⭐⭐            ⭐⭐⭐                                                 │
│    20-30 min       25-35 min                                            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Required
- Python 3.12
- **One** of:
  - Anthropic API key ([get one here](https://console.anthropic.com/)), **or**
  - AWS Bedrock bearer token (runs `*_bedrock.py` variants instead)
- Basic Python knowledge

### For Atlassian Katas (06-07)
- Atlassian Cloud account ([free tier available](https://www.atlassian.com/try))
- Atlassian API token ([create here](https://id.atlassian.com/manage-profile/security/api-tokens))

### For MCP Kata (07)
- Uses the included `mcp_server.py` (no additional setup required)
- Optional: Node.js v18+ (for official Atlassian MCP)

### For GitHub Kata (08)
- GitHub account
- GitHub Personal Access Token with `repo` scope ([create here](https://github.com/settings/tokens))

### For AWS AgentCore Katas (09–13)
- AWS account with Bedrock and AgentCore enabled
- `AWS_BEARER_TOKEN_BEDROCK` and `AWS_REGION` environment variables set
- Katas 09–13 run **only** the `solution.py` / `starter.py` variants (Bedrock-native)

---

## Setup

For detailed setup instructions see [SETUP.md](SETUP.md).
**Windows users**: see [SETUP_WINDOWS.md](SETUP_WINDOWS.md) for terminal requirements, PATH setup, and pip install fixes.
**Prefer Docker?** Skip Python setup entirely — see [`docker/DOCKER.md`](docker/DOCKER.md).
**Using AWS Bedrock?** See the [Bedrock setup in SETUP.md](SETUP.md#2b-aws-bedrock-bearer-token).

## Quick Start

> **Pick your path before you begin:**
>
> | Path | When to use |
> |------|-------------|
> | **[A — Anthropic API](#path-a--anthropic-api)** | You have an Anthropic API key (simplest) |
> | **[B — AWS Bedrock](#path-b--aws-bedrock)** | You have an AWS Bedrock bearer token |
> | **[C — Docker](#path-c--docker)** | You want to skip Python/pip setup entirely |
>
> Paths A and B use the same venv setup — A runs `solution.py`, B runs `solution_bedrock.py`.

---

### Path A — Anthropic API

```bash
# 1. Enter the workshop directory
cd local-ai-agents-workshop

# 2. Create virtual environment (Python 3.12 required)
# macOS (Homebrew):
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv venv
# Linux: python3.12 -m venv venv
# Windows: py -3.12 -m venv venv

source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set API key
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# 5. Start Kata 01
cd kata-01-anthropic-basics
python solution.py
```

---

### Path B — AWS Bedrock

```bash
# 1-3. Same venv setup as Path A
source venv/bin/activate
pip install -r requirements.txt

# 4. Set Bedrock credentials
export AWS_BEARER_TOKEN_BEDROCK="your-bedrock-token"
export AWS_REGION="us-east-1"
# For eu-central-1: set AWS_REGION=eu-central-1 and change the model ID
# prefix from "us." to "eu." in each *_bedrock.py file you run.

# 5. Start Kata 01 (Bedrock variant)
cd kata-01-anthropic-basics
python solution_bedrock.py
```

---

### Path C — Docker

```bash
# 1. Enter the docker directory
cd local-ai-agents-workshop/docker

# 2. Copy env file and fill in your key
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY (Path A) or AWS_BEARER_TOKEN_BEDROCK (Path B)

# 3. Start the container
docker compose up -d

# 4. Enter the container and run
docker exec -it workshop bash
python kata-01-anthropic-basics/solution.py          # Anthropic API
# python kata-01-anthropic-basics/solution_bedrock.py  # AWS Bedrock
```

See [`docker/DOCKER.md`](docker/DOCKER.md) for full Docker instructions including image variants.

---

## Kata Summary

### Track 1 — Anthropic + Strands (no AWS required)

| Kata | Topic | Skills | Time | Difficulty |
|------|-------|--------|------|------------|
| 01 | Anthropic API Basics | Messages API, streaming, tokens | 20-25 min | ⭐ |
| 02 | Strands Introduction | Agent class, model providers | 25-30 min | ⭐ |
| 03 | Strands with Tools | @tool decorator, custom tools | 30-40 min | ⭐⭐ |
| 04 | Local RAG | LlamaIndex, embeddings, indexing | 30-40 min | ⭐⭐ |
| 05 | RAG Agent | RAG as tool, knowledge-augmented agent | 40-50 min | ⭐⭐⭐ |
| 06 | Atlassian Agent | Jira/Confluence API, productivity tools | 35-45 min | ⭐⭐ |
| 07 | Atlassian MCP | MCP protocol, standardized tools | 40-50 min | ⭐⭐⭐ |
| 08 | GitHub PR Agent | GitHub API, PR workflows, PyGithub | 30-40 min | ⭐⭐ |

### Track 2 — AWS Bedrock + AgentCore (AWS credentials required)

| Kata | Topic | Skills | Time | Difficulty |
|------|-------|--------|------|------------|
| 09 | Bedrock Knowledge Base | S3 Vectors, KB ingestion, RAG agent | 45-60 min | ⭐⭐⭐ |
| 10 | AgentCore Runtime | BedrockAgentCoreApp, HTTP server, health checks | 20-30 min | ⭐⭐ |
| 11 | AgentCore Memory | Persistent memory, SemanticStrategy, cross-session recall | 30-40 min | ⭐⭐⭐ |
| 12 | AgentCore Code Interpreter | Sandboxed code execution, autonomous coding agent | 20-30 min | ⭐⭐ |
| 13 | AgentCore Gateway | REST→MCP auto-generation, OpenAPI schema, credential injection | 25-35 min | ⭐⭐⭐ |

---

## Folder Structure

```
local-ai-agents-workshop/
├── README.md               # This file
├── SETUP.md               # Detailed setup instructions
├── requirements.txt       # Python dependencies
│
│  Track 1 — Anthropic + Strands
│
├── kata-01-anthropic-basics/
│   ├── README.md          # Kata instructions
│   ├── starter.py         # Template with TODOs
│   └── solution.py        # Complete solution
│
├── kata-02-strands-intro/
│   ├── README.md
│   ├── starter.py
│   └── solution.py
│
├── kata-03-strands-tools/
│   ├── README.md
│   ├── starter.py
│   └── solution.py
│
├── kata-04-local-rag/
│   ├── README.md
│   ├── starter.py
│   ├── solution.py
│   └── sample_data/weather_docs/  # Sample documents
│
├── kata-05-rag-agent/
│   ├── README.md
│   ├── starter.py
│   ├── solution.py
│   └── sample_data/
│
├── kata-06-atlassian-agent/
│   ├── README.md
│   ├── starter.py
│   └── solution.py
│
├── kata-07-atlassian-mcp/
│   ├── README.md
│   ├── mcp_server.py        # Simple HTTP MCP server
│   ├── starter.py
│   └── solution.py
│
├── kata-08-github-pr-agent/
│   ├── README.md
│   ├── github_tools.py      # Reusable GitHub tools module
│   ├── starter.py
│   ├── solution.py
│   └── test_github_tools.py # Unit tests
│
│  Track 2 — AWS Bedrock + AgentCore
│
├── kata-09-bedrock-knowledge-base/
│   ├── README.md
│   ├── starter.py
│   ├── solution.py
│   ├── chat.py              # Interactive chat with the KB agent
│   ├── cleanup.py           # Deletes AWS resources (reads kata09_state.json)
│   └── sample_data/
│
├── kata-10-agentcore-runtime/
│   ├── README.md
│   ├── starter.py
│   └── solution.py
│
├── kata-11-agentcore-memory/
│   ├── README.md
│   ├── starter.py
│   ├── solution.py
│   └── cleanup.py           # Deletes AgentCore Memory store
│
├── kata-12-agentcore-code-interpreter/
│   ├── README.md
│   ├── starter.py
│   └── solution.py
│
└── kata-13-agentcore-gateway/
    ├── README.md
    ├── starter.py
    ├── solution.py
    └── cleanup.py           # Deletes Gateway, IAM role, and Secrets Manager secret
```

---

## How to Use This Workshop

### Self-Paced Learning

1. **Read the README** for each kata to understand the objectives
2. **Try the starter.py** first - complete the TODOs yourself
3. **Check solution.py** when stuck or to compare your approach
4. **Run and experiment** - modify code to deepen understanding

### Instructor-Led

1. **Instructor demos** solution.py with explanations
2. **Participants follow** along or code independently
3. **Discussion** of concepts and real-world applications
4. **Q&A** and extension challenges

---

## Cost Considerations

| Component | Cost |
|-----------|------|
| Anthropic API (Claude Sonnet) | ~$3 input / $15 output per MTok |
| Local embeddings (HuggingFace) | Free |
| LlamaIndex | Free |
| Atlassian Cloud (free tier) | Free |

**Estimated workshop cost**: $5-10 total for API calls

**Tips to minimize costs**:
- Use Claude Haiku for testing ($0.25/$1.25 per MTok)
- Limit `max_tokens` during development
- Reuse indexed documents

---

## Comparison with AWS Bedrock Workshop

This session teaches the same concepts as the AWS workshop but with:

**Simpler Setup**
- No AWS account needed
- Single API key authentication
- Local resources (no cloud costs beyond API)

**Same Patterns**
- Agent architecture (Strands works with both Bedrock and Anthropic)
- Tool definition and execution
- RAG concepts and implementation
- Conversation management

**Different Focus**
- Direct API access vs managed service
- Local RAG vs cloud-hosted
- Enterprise tool integration (Atlassian)
- MCP protocol for portability

---

## Next Steps After Workshop

1. **Build a real project** using these patterns
2. **Try AWS Bedrock** workshop for production deployment
3. **Explore other MCP servers** (GitHub, Slack, etc.)
4. **Contribute to Strands** (open-source)
5. **Join communities**:
   - [Strands Discord](https://strandsagents.com/)
   - [Anthropic Discord](https://discord.gg/anthropic)

---

## Troubleshooting

### API Key Issues
```
AuthenticationError: Invalid API key
```
- Verify `ANTHROPIC_API_KEY` is set correctly
- Check key hasn't expired
- Ensure no extra whitespace in key

### Import Errors
```
ModuleNotFoundError: No module named 'strands'
```
- Run `pip install -r requirements.txt`
- Ensure virtual environment is activated

### Atlassian Connection
```
401 Unauthorized
```
- Check API token is correct
- Verify email matches account
- Ensure URL includes `https://`

### MCP Server
```
Connection refused
```
- Check Docker container is running
- Verify port mapping
- Try `curl localhost:8000/health`

---

## Resources

### Documentation
- [Anthropic API Docs](https://docs.anthropic.com/)
- [Strands Agents](https://strandsagents.com/)
- [LlamaIndex](https://docs.llamaindex.ai/)
- [Atlassian Python API](https://atlassian-python-api.readthedocs.io/)
- [MCP Specification](https://modelcontextprotocol.io/)

### Tutorials
- [Strands + Anthropic Guide](https://dev.to/aws/using-strands-agents-with-anthropic-20jn)
- [RAG Best Practices](https://www.anthropic.com/research/rag-best-practices)

---

## Feedback

We'd love your feedback!
- What worked well?
- What was confusing?
- What would you add?

---

**Happy Building!**
