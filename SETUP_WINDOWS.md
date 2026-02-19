# Windows Setup Guide - Local AI Agents Workshop

This guide covers Windows-specific setup steps and fixes for common issues encountered in previous workshops.

> **Prerequisite**: Complete the main [SETUP.md](SETUP.md) alongside this guide. This document covers Windows-specific differences and known problem areas.

---

## Use the Right Terminal

**Using the wrong terminal is the most common source of problems on Windows.**

| Terminal | Supported | Notes |
|----------|-----------|-------|
| **PowerShell** | ✅ Recommended | Use Windows Terminal or the built-in PowerShell app. |
| **WSL2 (Ubuntu/Debian)** | ✅ Best compatibility | Behaves identically to Linux/macOS instructions. |
| **Command Prompt (CMD)** | ⚠️ Works with adjustments | See table below — do not copy `export` or `source` commands literally. |

**How to open PowerShell:**
- Press `Win + X` → select **Windows PowerShell** or **Terminal**
- Or search for **PowerShell** in the Start menu

### CMD users: command translation

The Python scripts themselves are terminal-agnostic. The only differences are the shell commands you type to set up and run them:

| Instruction in README | CMD equivalent |
|-----------------------|----------------|
| `export VAR=value` | `set VAR=value` |
| `source venv/bin/activate` | `venv\Scripts\activate.bat` |
| `venv\Scripts\Activate.ps1` | `venv\Scripts\activate.bat` |

> **Tip**: Use a `.env` file instead of `set` — it works in any terminal and persists across sessions. See [section 4](#4-setting-environment-variables).

---

## 1. Python 3.12 Installation & PATH

### Install Python 3.12

1. Download from [python.org/downloads](https://www.python.org/downloads/) — select **Python 3.12.x**
2. Run the installer and **check both boxes**:
   - ✅ **Add Python 3.12 to PATH**
   - ✅ **Install for all users** (recommended)
3. Click **Install Now**

### Verify Python is on PATH

Open a new PowerShell window after installation:

```powershell
python --version
# Expected: Python 3.12.x

py --list
# Expected: -3.12 (active) ...
```

If `python` is not recognized, Python was installed without being added to PATH. Fix it:

1. Search for **"Edit the system environment variables"** in Start
2. Click **Environment Variables**
3. Under **System variables**, find `Path` → click **Edit**
4. Add the path to your Python 3.12 installation, e.g.:
   ```
   C:\Users\YourName\AppData\Local\Programs\Python\Python312\
   C:\Users\YourName\AppData\Local\Programs\Python\Python312\Scripts\
   ```
5. Click OK, then **open a new PowerShell window** and retry

---

## 2. Microsoft C++ Build Tools (Required for pip installs)

Several workshop packages (`chromadb`, `sentence-transformers`, `tokenizers`) require compiled C extensions. Without build tools, `pip install` will fail with errors like:

```
error: Microsoft Visual C++ 14.0 or greater is required
```

### Install Build Tools

1. Download [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Run the installer and select **"Desktop development with C++"**
3. Ensure these components are checked:
   - MSVC v143 (or latest) C++ build tools
   - Windows 10/11 SDK
4. Click **Install** (~5–7 GB, may take a while)
5. **Restart your computer** after installation

### Verify Build Tools

```powershell
# Should print the MSVC compiler version
cl
```

After installing build tools, retry:

```powershell
pip install -r requirements.txt
```

---

## 3. Create and Activate the Virtual Environment

```powershell
# Navigate to the workshop directory
cd C:\path\to\local-ai-agents-workshop

# Create virtual environment using Python 3.12
py -3.12 -m venv venv

# Activate in PowerShell
venv\Scripts\Activate.ps1

# Verify - prompt should show (venv) prefix
python --version   # Should show 3.12.x
```

### PowerShell Execution Policy Error

If activation fails with a message about scripts being disabled:

```powershell
# Allow scripts for the current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again.

---

## 4. Setting Environment Variables

### Temporary (current PowerShell session only)

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-api03-your-key-here"
$env:ATLASSIAN_URL = "https://your-domain.atlassian.net"
$env:ATLASSIAN_EMAIL = "your-email@example.com"
$env:ATLASSIAN_API_TOKEN = "your-token"
$env:GITHUB_TOKEN = "your-github-token"
```

> Variables set this way are lost when you close PowerShell.

### Temporary (CMD session only)

```cmd
set ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
set ATLASSIAN_URL=https://your-domain.atlassian.net
set ATLASSIAN_EMAIL=your-email@example.com
set ATLASSIAN_API_TOKEN=your-token
set GITHUB_TOKEN=your-github-token
```

> **CMD warning**: Do NOT add quotes around values. CMD includes the quotes as part of the value, which breaks authentication. Use `set VAR=value`, not `set VAR="value"`.

### Persistent (recommended)

Use a `.env` file in the workshop root — `python-dotenv` loads it automatically in each kata:

```
# .env
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
ATLASSIAN_URL=https://your-domain.atlassian.net
ATLASSIAN_EMAIL=your-email@example.com
ATLASSIAN_API_TOKEN=your-token
GITHUB_TOKEN=your-github-token
```

---

## 5. Running Katas

```powershell
# Activate virtual environment first (every new terminal session)
venv\Scripts\Activate.ps1

# Run a kata
cd kata-01-anthropic-basics
python solution.py
```

---

## Windows-Specific Troubleshooting

### `pip install` fails on `chromadb` or `sentence-transformers`

Install [Microsoft C++ Build Tools](#2-microsoft-c-build-tools-required-for-pip-installs) (section 2 above).

### `python` command not found

Add Python 3.12 to PATH as described in [section 1](#1-python-312-installation--path).

### Unicode / emoji errors in terminal output

Some workshop scripts print emoji characters. If you see garbled output or errors, set UTF-8 encoding:

```powershell
# Set UTF-8 for the current session
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
```

To make this permanent, add it to your PowerShell profile (`$PROFILE`).

### MCP server port check

```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill the process using that port (replace <PID> with the actual PID)
taskkill /PID <PID> /F
```

### Curl not available

PowerShell has a built-in `curl` alias that behaves differently from Unix curl. Use `Invoke-RestMethod` instead:

```powershell
# Health check
Invoke-RestMethod http://localhost:8000/health

# List MCP tools
Invoke-RestMethod http://localhost:8000/mcp/v1/tools | ConvertTo-Json -Depth 5
```
