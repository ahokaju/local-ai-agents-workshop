"""
Kata 15: AWS Security Agent — PR Findings Analyzer - Solution

AWS Security Agent posts code review findings as GitHub PR review comments.
This script uses PyGithub to retrieve those findings and a Strands agent to
generate a prioritized remediation report with explanations and code fixes.

Why GitHub comments instead of boto3?
    AWS Security Agent is in preview and has no public boto3 client or CLI yet.
    The IAM action namespace `securityagent:` exists (ListFindings, BatchGetFindings,
    etc.) but is not exposed via a published SDK. Code review findings ARE accessible
    via the GitHub PR comments that Security Agent posts automatically.

Prerequisites:
    pip install 'strands-agents[bedrock]' PyGithub boto3 python-dotenv
    export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
    export AWS_REGION=us-east-1
    export GITHUB_TOKEN=your-github-pat
    export GITHUB_REPO=owner/repo-name    # repository Security Agent is connected to
    export PR_NUMBER=42                   # PR that Security Agent reviewed

    To use eu-central-1: set AWS_REGION=eu-central-1 and change DEFAULT_MODEL
    prefix from "us." to "eu.".

    Part A (console setup) must be completed first — see README.md.
"""

import json
import os

from dotenv import load_dotenv
from github import Github, GithubException
from strands import Agent, tool
from strands.models.bedrock import BedrockModel

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DEFAULT_MODEL = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "")
PR_NUMBER = int(os.getenv("PR_NUMBER", "0"))


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[96m'
    PROMPT = '\033[93m'
    RESPONSE = '\033[92m'
    STATS = '\033[95m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    @classmethod
    def header(cls, text): return f"{cls.BOLD}{cls.HEADER}{text}{cls.RESET}"
    @classmethod
    def prompt(cls, text): return f"{cls.PROMPT}{text}{cls.RESET}"
    @classmethod
    def response(cls, text): return f"{cls.RESPONSE}{text}{cls.RESET}"
    @classmethod
    def stats(cls, text): return f"{cls.STATS}{text}{cls.RESET}"


# ==============================================================================
# Step 1: Strands @tool — fetch Security Agent findings from a GitHub PR
# ==============================================================================

@tool
def get_pr_security_findings(repo: str, pr_number: int) -> str:
    """Fetch security findings posted by AWS Security Agent on a GitHub PR.

    Security Agent posts findings as GitHub PR review comments (inline on specific
    lines) and as general PR comments for summaries. This tool retrieves both types
    so the agent can analyze each finding.

    Args:
        repo: GitHub repository in 'owner/repo' format (e.g., 'myorg/myapp')
        pr_number: Pull request number to fetch findings from
    """
    if not GITHUB_TOKEN:
        return json.dumps({"error": "GITHUB_TOKEN environment variable not set"})

    try:
        g = Github(GITHUB_TOKEN)
        repo_obj = g.get_repo(repo)
        pr = repo_obj.get_pull(pr_number)
    except GithubException as e:
        return json.dumps({"error": str(e), "repo": repo, "pr_number": pr_number})

    findings = []

    # Inline review comments (Security Agent posts findings as code-level comments)
    try:
        for comment in pr.get_review_comments():
            if comment.user and comment.user.type == "Bot":
                findings.append({
                    "type": "inline_comment",
                    "body": comment.body,
                    "file": comment.path,
                    "line": comment.line,
                    "author": comment.user.login,
                    "created_at": comment.created_at.isoformat()
                })
    except GithubException:
        pass

    # General PR comments — Security Agent may post a summary here too
    security_keywords = ["security", "vulnerability", "finding", "owasp",
                         "injection", "xss", "csrf", "ssrf", "critical", "high"]
    try:
        for comment in pr.get_issue_comments():
            if comment.user and comment.user.type == "Bot":
                body_lower = comment.body.lower()
                if any(kw in body_lower for kw in security_keywords):
                    findings.append({
                        "type": "pr_comment",
                        "body": comment.body,
                        "author": comment.user.login,
                        "created_at": comment.created_at.isoformat()
                    })
    except GithubException:
        pass

    return json.dumps({
        "repo": repo,
        "pr_number": pr_number,
        "pr_title": pr.title,
        "pr_state": pr.state,
        "findings_count": len(findings),
        "findings": findings,
        "note": (
            "If findings_count is 0: ensure Security Agent is connected to this repo "
            "and has reviewed the PR. Check the Agent Space console."
        )
    }, indent=2)


# ==============================================================================
# Step 2: Strands @tool — fetch the PR diff for code context
# ==============================================================================

@tool
def get_pr_diff(repo: str, pr_number: int) -> str:
    """Get the code diff for a pull request to provide context for security analysis.

    Use this after get_pr_security_findings to see the actual code changes that
    triggered the findings. Helps the agent suggest more precise fixes.

    Args:
        repo: GitHub repository in 'owner/repo' format
        pr_number: Pull request number
    """
    if not GITHUB_TOKEN:
        return json.dumps({"error": "GITHUB_TOKEN environment variable not set"})

    try:
        g = Github(GITHUB_TOKEN)
        repo_obj = g.get_repo(repo)
        pr = repo_obj.get_pull(pr_number)
    except GithubException as e:
        return json.dumps({"error": str(e)})

    files = []
    try:
        for f in pr.get_files():
            files.append({
                "filename": f.filename,
                "status": f.status,
                "additions": f.additions,
                "deletions": f.deletions,
                "patch": f.patch[:3000] if f.patch else None  # truncate large diffs
            })
    except GithubException as e:
        return json.dumps({"error": str(e)})

    return json.dumps({
        "pr_number": pr_number,
        "base_branch": pr.base.ref,
        "head_branch": pr.head.ref,
        "files_changed": len(files),
        "total_additions": sum(f["additions"] for f in files),
        "total_deletions": sum(f["deletions"] for f in files),
        "files": files
    }, indent=2)


# ==============================================================================
# Step 3: Check for Security Agent findings (direct inspection, no Strands)
# ==============================================================================

def inspect_pr_findings(repo: str, pr_number: int) -> int:
    """Print a summary of Security Agent findings found on the PR."""
    if not GITHUB_TOKEN:
        print(Colors.stats("  Error: GITHUB_TOKEN not set"))
        return 0

    try:
        g = Github(GITHUB_TOKEN)
        repo_obj = g.get_repo(repo)
        pr = repo_obj.get_pull(pr_number)
        print(Colors.stats(f"  PR #{pr_number}: {pr.title}"))
        print(Colors.stats(f"  State: {pr.state}"))

        bot_comments = []
        for comment in pr.get_review_comments():
            if comment.user and comment.user.type == "Bot":
                bot_comments.append(comment.user.login)

        if bot_comments:
            print(Colors.stats(f"  Found {len(bot_comments)} Security Agent review comment(s)"))
            print(Colors.stats(f"  Bot accounts: {set(bot_comments)}"))
        else:
            print(Colors.stats("  No bot review comments found yet."))
            print(Colors.stats("  Ensure Security Agent has reviewed this PR (check console)."))

        return len(bot_comments)
    except GithubException as e:
        print(f"  GitHub error: {e}")
        return 0


# ==============================================================================
# Step 4: Remediation agent
# ==============================================================================

def run_remediation_agent(repo: str, pr_number: int) -> None:
    """Run the Strands remediation agent for the given PR."""
    print(Colors.stats("\nInitializing remediation agent..."))

    model = BedrockModel(
        model_id=DEFAULT_MODEL,
        region_name=AWS_REGION,
        max_tokens=4096,
    )
    agent = Agent(
        model=model,
        tools=[get_pr_security_findings, get_pr_diff],
        system_prompt=(
            "You are a senior security engineer reviewing findings from AWS Security Agent. "
            "Security Agent automatically reviews GitHub pull requests for vulnerabilities. "
            "Use the available tools to:\n"
            "1. Retrieve security findings from the PR review comments\n"
            "2. Get the code diff for context\n\n"
            "For each finding, provide:\n"
            "- The vulnerability type and OWASP category (e.g., A03:2021 Injection)\n"
            "- Why it is dangerous (potential attack scenario and impact)\n"
            "- A concrete before/after code fix\n"
            "- Estimated fix effort (Low/Medium/High)\n\n"
            "Organize by severity (CRITICAL first, then HIGH, MEDIUM, LOW). "
            "Format as Markdown suitable for developers."
        )
    )

    prompt = (
        f"Analyze the security findings on PR #{pr_number} in repository {repo}. "
        "First fetch the Security Agent findings, then get the code diff for context. "
        "Generate a complete remediation report that developers can act on immediately."
    )

    print(Colors.prompt(f"\nUser: {prompt[:100]}...\n"))
    response = agent(prompt)
    print(Colors.response(f"\n{response}"))


# ==============================================================================
# Main
# ==============================================================================

def main():
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 15: AWS Security Agent - PR Findings Analyzer"))
    print(Colors.header(f" Region: {AWS_REGION}  |  Model: {DEFAULT_MODEL}"))
    print(Colors.header("=" * 70))

    if not GITHUB_TOKEN:
        print("\nError: GITHUB_TOKEN environment variable is not set.")
        print("  export GITHUB_TOKEN=your-github-personal-access-token")
        return

    if not GITHUB_REPO or not PR_NUMBER:
        print("\nError: GITHUB_REPO and PR_NUMBER environment variables are required.")
        print("  export GITHUB_REPO=owner/repo-name")
        print("  export PR_NUMBER=42")
        return

    # Step 1: Inspect PR for Security Agent findings
    print(Colors.header("\n1. Fetching Security Agent findings from PR"))
    print("-" * 40)
    print(Colors.stats(f"  Repo: {GITHUB_REPO}  |  PR: #{PR_NUMBER}"))
    findings_count = inspect_pr_findings(GITHUB_REPO, PR_NUMBER)

    if findings_count == 0:
        print(Colors.stats("\n  Note: Proceeding anyway — agent will attempt to retrieve findings."))
        print(Colors.stats("  If none are found, check Part A setup in README.md."))

    # Step 2: Run remediation agent
    print(Colors.header("\n2. Remediation agent"))
    print("-" * 40)
    run_remediation_agent(GITHUB_REPO, PR_NUMBER)

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 15 Complete!"))
    print(Colors.header("=" * 70))
    print(Colors.stats("\nKey takeaway: Security Agent has no public boto3 API (preview)."))
    print(Colors.stats("Its findings ARE accessible via GitHub PR comments, giving you"))
    print(Colors.stats("a real integration path using PyGithub + Strands + Claude."))


if __name__ == "__main__":
    main()
