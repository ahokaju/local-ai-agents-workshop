# Kata 14: AWS Security Agent — PR Findings Analyzer

> **Preview service**: AWS Security Agent is currently in Preview in **us-east-1 only**.
> Request access at [aws.amazon.com/security-agent](https://aws.amazon.com/security-agent).
>
> **No public API**: Unlike most AWS services, Security Agent has no boto3 client or
> AWS CLI at this time. Findings are consumed through the web application or via the
> GitHub PR comments that Security Agent posts automatically. This kata uses the GitHub
> integration — building on kata-07 — to retrieve and analyze those findings.

## Objective

AWS Security Agent posts security findings directly to GitHub pull requests as review
comments. This kata uses PyGithub (from kata-07) to fetch those comments, then passes
them to a Strands agent that generates a prioritized remediation report with explanations
and concrete code fixes.

## Learning Goals

- Understand AWS Security Agent's architecture and capabilities (code review, design review, pentest)
- Configure the GitHub integration so Security Agent reviews pull requests automatically
- Use PyGithub to retrieve Security Agent findings from PR review comments
- Build a Strands agent that analyzes security findings and generates actionable remediation guidance
- See how multiple katas compose: kata-07 (GitHub) + Strands agent = security workflow

## Prerequisites

- Completed Kata 03 (custom tools) and Kata 07 (GitHub integration)
- AWS account with Security Agent Preview access (us-east-1)
- GitHub account with a repository connected to Security Agent
- GitHub Personal Access Token with `repo` scope

```bash
pip install 'strands-agents[bedrock]' PyGithub boto3 python-dotenv
export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
export AWS_REGION=us-east-1
export GITHUB_TOKEN=your-github-pat
export GITHUB_REPO=owner/repo-name        # e.g., myorg/myapp
export PR_NUMBER=42                        # PR that Security Agent reviewed
```

## Time Estimate

25–35 minutes

## Difficulty

⭐⭐ (Intermediate — familiar Strands @tool pattern, builds on kata-07)

---

## Background

### What AWS Security Agent Does

Security Agent continuously secures applications across the development lifecycle:

| Capability | Trigger | Output |
|---|---|---|
| **Code Review** | Pull request opened/updated | GitHub PR review comments |
| **Design Review** | Manual upload of architecture doc | Compliance assessment (console) |
| **Penetration Testing** | Manual trigger (console) | Vulnerability findings (console) |

Code Review is the only capability with a programmatic output you can consume — findings
appear as GitHub PR review comments, making them accessible via the GitHub API.

### Why No boto3 Client?

Security Agent is in preview and the underlying API exists (IAM actions like
`securityagent:ListFindings` confirm this), but AWS has not published a boto3 client,
CLI, or public API reference yet. The web application calls the backend API, but that
endpoint is not documented for external use.

This is similar to early DevOps Agent, which required a custom service model download.
Security Agent may gain a public API as it moves toward GA.

### Architecture for This Kata

```
Developer opens PR on GitHub
    ↓
AWS Security Agent (managed) detects the PR
    ↓ [reviews code against OWASP Top 10 + org security requirements]
Security Agent posts findings as GitHub PR review comments
    ↓
Python: PyGithub → fetch PR review comments
    ↓
Strands agent: Claude analyzes findings
    ↓
Output: Prioritized Markdown remediation report
```

---

## Part A: Console Setup (~10 min)

### Step 1: Enable Security Agent

1. Sign in to the [AWS Console](https://us-east-1.console.aws.amazon.com/securityagent/)
2. Click **Get started** and follow the activation wizard
3. Create an **Agent Space** (name it after your application, e.g., `kata-14-app`)

### Step 2: Connect GitHub

1. In your Agent Space, click **Integrations** → **Connect GitHub**
2. Install the Security Agent GitHub App on your repository
3. Select the repository you want to scan

> **Tip**: Use a repository with known vulnerabilities for a richer demo. Fork a
> vulnerability-by-design app, or open a PR that introduces a simple SQL injection.

### Step 3: Trigger a Code Review

1. Open a pull request in your connected repository
2. Security Agent automatically detects the PR and begins reviewing
3. Wait 2–5 minutes for findings to appear as PR review comments
4. Note the **PR number** — you'll need it for Part B

> If Security Agent doesn't trigger automatically, check the GitHub App installation
> and repository permissions in the Agent Space console.

---

## Part B: Code (~25-35 min)

### What You'll Build

A Strands agent with two `@tool` functions:

1. `get_pr_security_findings(repo, pr_number)` — fetches Security Agent review comments via PyGithub
2. `get_pr_diff(repo, pr_number)` — fetches the code diff for context

The agent uses these to retrieve findings and generate a structured remediation report.

### Running the Solution

```bash
cd kata-14-security-agent
export GITHUB_TOKEN=your-pat
export GITHUB_REPO=owner/repo
export PR_NUMBER=42
python solution.py
```

Expected output:
```
===========================================================
 Kata 14: AWS Security Agent - PR Findings Analyzer
 Region: us-east-1
===========================================================

1. Fetching Security Agent findings from PR #42
----------------------------------------
Found 3 Security Agent review comment(s)

2. Remediation agent
----------------------------------------

User: Analyze security findings on PR #42 and generate a remediation report

# Security Remediation Report — PR #42

## CRITICAL: SQL Injection (OWASP A03:2021)

**Location**: `src/db/queries.py` (from PR comment)

**What it is**: User input is passed directly into a SQL query without
parameterization, allowing an attacker to manipulate the query.

**Why it's dangerous**: An attacker can read, modify, or delete arbitrary
database records, or execute system commands if `xp_cmdshell` is enabled.

**Fix**:
```python
# BEFORE (vulnerable):
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

# AFTER (safe):
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```
...
```

---

## Level 1: Challenge

1. Implement `get_pr_security_findings()` using the `github` library to fetch PR review comments
2. Filter comments to only those posted by the Security Agent GitHub App bot
3. Implement `get_pr_diff()` to provide code context to the agent
4. Build a Strands agent that produces a severity-organized remediation report

### Success Criteria

- [ ] `get_pr_security_findings` returns at least one Security Agent comment
- [ ] Agent generates a report organized by severity
- [ ] Each finding includes: what it is, why it's dangerous, how to fix it
- [ ] (Bonus) Post the remediation report back to the PR as a comment (kata-07 pattern)

---

## Level 2: Step-by-Step Guide

### Step 1: Identify Security Agent Comments

Security Agent posts comments as a GitHub App bot. The bot username typically contains
`aws-security-agent` or similar. You can also filter by comment body patterns (e.g.,
comments that start with a severity indicator).

```python
from github import Github

def get_security_agent_comments(repo_name: str, pr_number: int, token: str) -> list[dict]:
    g = Github(token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    security_comments = []
    for review in pr.get_reviews():
        # Filter for Security Agent bot reviews
        if review.user and (
            "aws" in review.user.login.lower() or
            "security" in review.user.login.lower() or
            review.user.type == "Bot"
        ):
            for comment in pr.get_review_comments():
                if comment.pull_request_review_id == review.id:
                    security_comments.append({
                        "body": comment.body,
                        "path": comment.path,
                        "line": comment.line,
                        "position": comment.position
                    })

    return security_comments
```

### Step 2: list_security_findings Tool

```python
from strands import tool

@tool
def get_pr_security_findings(repo: str, pr_number: int) -> str:
    """Fetch security findings posted by AWS Security Agent on a GitHub PR.

    Security Agent posts findings as GitHub PR review comments. This tool
    retrieves those comments so the agent can analyze and explain each finding.

    Args:
        repo: GitHub repository in 'owner/repo' format
        pr_number: Pull request number to fetch findings from
    """
    g = Github(GITHUB_TOKEN)
    repo_obj = g.get_repo(repo)
    pr = repo_obj.get_pull(pr_number)

    findings = []

    # Fetch PR review comments (inline code comments)
    for comment in pr.get_review_comments():
        if comment.user and comment.user.type == "Bot":
            findings.append({
                "type": "review_comment",
                "body": comment.body,
                "file": comment.path,
                "line": comment.line,
                "author": comment.user.login
            })

    # Also check general PR comments for summary findings
    for comment in pr.get_issue_comments():
        if comment.user and comment.user.type == "Bot":
            if any(kw in comment.body.lower() for kw in
                   ["security", "vulnerability", "finding", "owasp", "injection"]):
                findings.append({
                    "type": "pr_comment",
                    "body": comment.body,
                    "author": comment.user.login
                })

    return json.dumps({
        "repo": repo,
        "pr_number": pr_number,
        "pr_title": pr.title,
        "findings_count": len(findings),
        "findings": findings
    }, indent=2)
```

### Step 3: get_pr_diff Tool

```python
@tool
def get_pr_diff(repo: str, pr_number: int) -> str:
    """Get the code diff for a pull request to provide context for security analysis.

    Use this after get_pr_security_findings to understand the code changes
    that triggered the security findings.

    Args:
        repo: GitHub repository in 'owner/repo' format
        pr_number: Pull request number
    """
    g = Github(GITHUB_TOKEN)
    repo_obj = g.get_repo(repo)
    pr = repo_obj.get_pull(pr_number)

    files = []
    for f in pr.get_files():
        files.append({
            "filename": f.filename,
            "status": f.status,
            "additions": f.additions,
            "deletions": f.deletions,
            "patch": f.patch[:2000] if f.patch else None  # truncate large diffs
        })

    return json.dumps({
        "pr_number": pr_number,
        "files_changed": len(files),
        "files": files
    }, indent=2)
```

### Step 4: Build the Remediation Agent

```python
from strands import Agent
from strands.models.bedrock import BedrockModel

model = BedrockModel(model_id=DEFAULT_MODEL, region_name=AWS_REGION, max_tokens=4096)
agent = Agent(
    model=model,
    tools=[get_pr_security_findings, get_pr_diff],
    system_prompt=(
        "You are a senior security engineer reviewing findings from AWS Security Agent. "
        "Use the available tools to retrieve security findings from a GitHub PR. "
        "For each finding, provide:\n"
        "1. What the vulnerability is and its OWASP category\n"
        "2. Why it is dangerous (potential impact)\n"
        "3. A concrete code fix\n\n"
        "Organize by severity (CRITICAL first). Format as Markdown."
    )
)

response = agent(
    f"Analyze security findings on PR #{PR_NUMBER} in {GITHUB_REPO}. "
    "Get the code diff for context. Generate a complete remediation report."
)
print(response)
```

---

## Extension Challenges

1. **Post report as PR comment**: Use kata-07's `github_create_pr_comment` pattern to
   post the remediation report directly on the PR so developers see it immediately
2. **Severity filter**: Only report on findings that include specific OWASP categories
   (e.g., only injection-type vulnerabilities)
3. **Design review**: Use the console to run a design review on an architecture document,
   then manually paste the findings into the agent to analyze compliance gaps
4. **Trend tracking**: Run the agent on multiple PRs and track which vulnerability types
   recur most often across your codebase

---

## Note on Future API Access

As Security Agent moves toward GA, AWS may publish a boto3 client similar to DevOps
Agent's custom service model. The IAM actions (`securityagent:ListFindings`,
`securityagent:BatchGetFindings`, etc.) already exist — they just aren't exposed via a
public SDK yet. When that changes, this kata can be updated to use direct API calls
instead of the GitHub PR comments approach.

---

## Resources

- [AWS Security Agent Documentation](https://docs.aws.amazon.com/securityagent/latest/userguide/)
- [AWS Security Agent Preview](https://aws.amazon.com/security-agent/)
- [Inside AWS Security Agent — multi-agent architecture](https://aws.amazon.com/blogs/security/inside-aws-security-agent-a-multi-agent-architecture-for-automated-penetration-testing/)
- [PyGithub Documentation](https://pygithub.readthedocs.io/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
