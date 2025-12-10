# Setup Guide - Local AI Agents Workshop

This guide provides detailed setup instructions for all workshop prerequisites.

---

## Table of Contents

1. [Python Environment](#1-python-environment)
2. [Anthropic API Key](#2-anthropic-api-key)
3. [Installing Dependencies](#3-installing-dependencies)
4. [Atlassian Setup (Katas 06-07)](#4-atlassian-setup)
5. [MCP Server Setup (Kata 07)](#5-mcp-server-setup)
6. [Verifying Your Setup](#6-verifying-your-setup)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Python Environment

### Requirements
- **Python 3.12** (required)
- pip (Python package manager)
- Virtual environment (recommended)

> **Important**: Python 3.13+ is too new and lacks pre-built wheels for many ML packages. Python 3.10/3.11 may have compatibility issues with some dependencies. Python 3.12 is required for this workshop.

### Check Available Python Versions

```bash
# macOS (Homebrew):
ls /opt/homebrew/opt/python@*/bin/python3*
# or
brew list | grep python

# Linux:
ls /usr/bin/python3* 2>/dev/null
# or check specific versions:
which python3.10 python3.11 python3.12

# Windows (Python launcher):
py --list

# Any system - check specific version:
python3.12 --version
```

### Install Python 3.12 (if needed)

```bash
# macOS with Homebrew
brew install python@3.12

# Ubuntu/Debian
sudo apt update && sudo apt install python3.12 python3.12-venv

# Windows
# 1. Download Python 3.12 from https://www.python.org/downloads/
# 2. During installation, CHECK "Add Python to PATH"
# 3. Verify: py --list (should show 3.12)
```

### Create Virtual Environment

```bash
# Navigate to workshop directory
cd local-agents

# Create virtual environment with specific Python version
# macOS with Homebrew:
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv venv

# Linux (if python3.12 is in PATH):
python3.12 -m venv venv

# Windows (adjust path to your Python 3.12 installation):
py -3.12 -m venv venv

# Activate the virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Verify Python version (should be 3.12.x)
python --version
```

---

## 2. Anthropic API Key

### Get Your API Key

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Sign in or create an account
3. Navigate to **API Keys**
4. Click **Create Key**
5. Copy the key (you won't see it again!)

### Set the API Key

**Option A: Environment Variable (Recommended)**

```bash
# macOS/Linux - add to ~/.bashrc or ~/.zshrc
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"

# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"

# Windows CMD
set ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

> **Windows Note**: Environment variables set with `$env:` or `set` are temporary (only for current session). For persistence, use Option B (.env file) or set via System Properties > Environment Variables.

**Option B: .env File (Recommended for Windows)**

Create a `.env` file in the `local-agents` directory:

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

> **Security Note**: Never commit API keys to version control. The `.env` file is in `.gitignore`.

### Verify API Key

```python
from anthropic import Anthropic

client = Anthropic()
response = client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=10,
    messages=[{"role": "user", "content": "Hi"}]
)
print("API key is valid!")
```

---

## 3. Installing Dependencies

### Install All Dependencies

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Install all requirements
pip install -r requirements.txt
```

### What Gets Installed

| Package | Purpose |
|---------|---------|
| `anthropic` | Anthropic API client |
| `strands-agents[anthropic]` | Strands SDK with Anthropic provider |
| `llama-index` | RAG framework |
| `llama-index-embeddings-huggingface` | Local embeddings |
| `chromadb` | Vector database |
| `sentence-transformers` | Embedding models |
| `atlassian-python-api` | Jira/Confluence API |
| `mcp` | Model Context Protocol |
| `python-dotenv` | Environment variables |

### Verify Installation

```bash
# Check key packages
python -c "import anthropic; print('anthropic:', anthropic.__version__)"
python -c "import strands; print('strands: OK')"
python -c "import llama_index; print('llama_index: OK')"
```

---

## 4. Atlassian Setup

Required for Katas 06-07 (Atlassian agent and MCP).

### Get Atlassian Account

1. Go to [atlassian.com/try](https://www.atlassian.com/try)
2. Sign up for a free cloud account
3. You'll get a site like `your-domain.atlassian.net`

### Create API Token

1. Go to [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Name it (e.g., "AI Agent Workshop")
4. Copy the token immediately (shown only once)

### Set Environment Variables

```bash
# Add to your shell profile or .env file
export ATLASSIAN_URL="https://your-domain.atlassian.net"
export ATLASSIAN_EMAIL="your-email@example.com"
export ATLASSIAN_API_TOKEN="your-api-token-here"
```

### Create Test Data (Optional)

For the best experience, create some test data in your Atlassian instance:

**Jira**:
1. Create a project (e.g., "DEMO")
2. Add a few issues of different types (Task, Bug, Story)

**Confluence**:
1. Create a space (e.g., "DOC")
2. Add a few pages with sample content

### Verify Atlassian Connection

```python
from atlassian import Jira
import os

jira = Jira(
    url=os.getenv("ATLASSIAN_URL"),
    username=os.getenv("ATLASSIAN_EMAIL"),
    password=os.getenv("ATLASSIAN_API_TOKEN"),
    cloud=True
)

# Should list your projects
projects = jira.projects()
print(f"Connected! Found {len(projects)} projects")
```

---

## 5. MCP Server Setup

For Kata 07, the workshop includes a simple HTTP MCP server (`mcp_server.py`).

### Primary Option: Included MCP Server

The workshop includes `kata-07-atlassian-mcp/mcp_server.py` - a simple HTTP-based MCP server.

**No additional setup required** - just ensure your Atlassian credentials are configured (step 4).

```bash
# Start the MCP server
cd kata-07-atlassian-mcp
python mcp_server.py
```

**Verify**:

```bash
# Test health endpoint (use curl, or open in browser)
curl http://localhost:8000/health

# List available tools
curl http://localhost:8000/mcp/v1/tools | python -m json.tool

# Windows PowerShell alternative (if curl not available):
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/mcp/v1/tools | ConvertTo-Json
```

### Optional: Official Atlassian Remote MCP

For Claude Desktop integration:

**Requirements**: Node.js v18+

```bash
# Install mcp-remote
npm install -g mcp-remote
```

**Configure Claude Desktop**:

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac):

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "mcp-remote",
      "args": ["https://mcp.atlassian.com"]
    }
  }
}
```

---

## 6. Verifying Your Setup

Run this verification script to check everything is set up correctly:

```python
#!/usr/bin/env python3
"""Setup verification script for Local AI Agents Workshop."""

import sys

def check_python():
    print("1. Python Version")
    print(f"   Version: {sys.version}")
    if sys.version_info >= (3, 13):
        print("   ❌ Python 3.13+ detected - too new, may have install issues")
        print("      Required: Python 3.12")
        return False
    elif sys.version_info[:2] == (3, 12):
        print("   ✅ Python 3.12 detected")
        return True
    else:
        print("   ❌ Python 3.12 required")
        return False

def check_anthropic():
    print("\n2. Anthropic API")
    try:
        from anthropic import Anthropic
        client = Anthropic()
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        print("   ✅ Anthropic API connected")
        return True
    except Exception as e:
        print(f"   ❌ Anthropic error: {e}")
        return False

def check_strands():
    print("\n3. Strands Agents")
    try:
        from strands import Agent
        from strands.models.anthropic import AnthropicModel
        print("   ✅ Strands imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Strands error: {e}")
        return False

def check_embeddings():
    print("\n4. Local Embeddings")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        embedding = model.encode("test")
        print(f"   ✅ Embeddings working (dim: {len(embedding)})")
        return True
    except Exception as e:
        print(f"   ❌ Embeddings error: {e}")
        return False

def check_atlassian():
    print("\n5. Atlassian API")
    import os
    url = os.getenv("ATLASSIAN_URL")
    email = os.getenv("ATLASSIAN_EMAIL")
    token = os.getenv("ATLASSIAN_API_TOKEN")

    if not all([url, email, token]):
        print("   ⚠️  Atlassian not configured (optional for Kata 06-07)")
        return None

    try:
        from atlassian import Jira
        jira = Jira(url=url, username=email, password=token, cloud=True)
        projects = jira.projects()
        print(f"   ✅ Connected to Atlassian ({len(projects)} projects)")
        return True
    except Exception as e:
        print(f"   ❌ Atlassian error: {e}")
        return False

def main():
    print("=" * 60)
    print(" Local AI Agents Workshop - Setup Verification")
    print("=" * 60)

    results = [
        check_python(),
        check_anthropic(),
        check_strands(),
        check_embeddings(),
        check_atlassian(),
    ]

    print("\n" + "=" * 60)
    passed = sum(1 for r in results if r is True)
    optional = sum(1 for r in results if r is None)
    total = len(results) - optional

    print(f" Results: {passed}/{total} required checks passed")
    if optional:
        print(f"          {optional} optional check(s) skipped")

    if passed == total:
        print(" ✅ You're ready for the workshop!")
    else:
        print(" ⚠️  Please resolve the issues above before starting")

    print("=" * 60)

if __name__ == "__main__":
    main()
```

Save as `verify_setup.py` and run:

```bash
python verify_setup.py
```

---

## 7. Troubleshooting

### "ModuleNotFoundError: No module named 'xyz'"

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### "AuthenticationError: Invalid API key"

- Check API key is set correctly
- Verify no extra whitespace
- Try regenerating the key

### "Connection refused" (Atlassian)

- Check URL includes `https://`
- Verify email matches your Atlassian account
- Ensure API token is correct (not password)

### "429 Too Many Requests"

- Rate limit hit - wait a minute and retry
- Use Claude Haiku model for testing
- Reduce `max_tokens`

### MCP Server Issues

```bash
# Check MCP server is running
curl http://localhost:8000/health

# If port 8000 is in use:
# macOS/Linux:
lsof -i :8000
# Windows (PowerShell):
netstat -ano | findstr :8000

# Restart the server if needed (Ctrl+C and run again)
python mcp_server.py
```

### Embedding Model Download Issues

First run downloads embedding models (~100MB):

```bash
# Pre-download the model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

---

## Need Help?

- Check the README.md in each kata folder
- Review the troubleshooting section above
- Ask your instructor (if in-person)

---

## Quick Reference

### Environment Variables

```bash
# Required
export ANTHROPIC_API_KEY="sk-ant-..."

# For Atlassian katas (optional)
export ATLASSIAN_URL="https://your-domain.atlassian.net"
export ATLASSIAN_EMAIL="your-email@example.com"
export ATLASSIAN_API_TOKEN="your-token"

# For MCP kata (optional)
export MCP_SERVER_URL="http://localhost:8000"
```

### Key Commands

```bash
# Activate environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run a kata solution
cd kata-01-anthropic-basics
python solution.py

# Verify setup
python verify_setup.py
```
