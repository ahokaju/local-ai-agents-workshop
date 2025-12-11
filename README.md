# Local AI Agents Workshop

## Overview

This workshop teaches you to build AI agents locally using:
- **Anthropic API** directly (no AWS required)
- **Strands Agents SDK** (open-source agent framework)
- **Local RAG** with LlamaIndex and HuggingFace embeddings
- **Atlassian Integration** (Jira/Confluence)
- **GitHub Integration** (PR workflows with PyGithub)
- **MCP Protocol** for standardized tool integration

**Duration**: ~4.5-5 hours
**Level**: Beginner to Intermediate
**Format**: 8 hands-on katas with progressive difficulty

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
│  Kata 06          Kata 07                                               │
│  ┌──────────┐    ┌──────────┐                                          │
│  │Atlassian │───▶│Atlassian │                                          │
│  │  Agent   │    │   MCP    │                                          │
│  └──────────┘    └──────────┘                                          │
│     ⭐⭐            ⭐⭐⭐                                                 │
│    40 min          45 min                                               │
│                                                                          │
│  Kata 08                                                                │
│  ┌──────────┐                                                          │
│  │ GitHub   │                                                          │
│  │ PR Agent │                                                          │
│  └──────────┘                                                          │
│     ⭐⭐                                                                 │
│    35 min                                                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Required
- Python 3.12
- Anthropic API key ([get one here](https://console.anthropic.com/))
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

---

## Quick Start

```bash
# 1. Clone and navigate to this directory
cd local-agents

# 2. Create virtual environment with Python 3.12
# macOS (Homebrew):
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv venv
# Linux: python3.12 -m venv venv
# Windows: py -3.12 -m venv venv

source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Verify Python version
python --version  # Should be 3.12.x

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up API key
export ANTHROPIC_API_KEY="your-key-here"

# 6. Start with Kata 01
cd kata-01-anthropic-basics
python solution.py
```

---

## Kata Summary

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

---

## Folder Structure

```
local-agents/
├── README.md               # This file
├── SETUP.md               # Detailed setup instructions
├── requirements.txt       # Python dependencies
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
└── kata-08-github-pr-agent/
    ├── README.md
    ├── github_tools.py      # Reusable GitHub tools module
    ├── starter.py
    ├── solution.py
    └── test_github_tools.py # Unit tests
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
