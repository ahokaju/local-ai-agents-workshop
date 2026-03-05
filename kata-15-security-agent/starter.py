"""
Kata 15: AWS Security Agent — PR Findings Analyzer - Starter Template

Complete the TODOs to build a Strands agent that retrieves security findings
from GitHub PR review comments posted by AWS Security Agent, then generates
a prioritized remediation report.

Why GitHub comments instead of boto3?
    AWS Security Agent is in preview with no public boto3 client or CLI yet.
    Code review findings are accessible via the GitHub PR review comments that
    Security Agent posts automatically — so we use PyGithub (from kata-08).

Prerequisites:
    pip install 'strands-agents[bedrock]' PyGithub boto3 python-dotenv
    export AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
    export AWS_REGION=us-east-1
    export GITHUB_TOKEN=your-github-pat
    export GITHUB_REPO=owner/repo-name
    export PR_NUMBER=42

    Part A (console setup) must be completed first — see README.md.
"""

import json
import os

from dotenv import load_dotenv
from github import Github, GithubException
# TODO 1: Import the following:
#   from strands import Agent, tool
#   from strands.models.bedrock import BedrockModel

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
    TODO = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    @classmethod
    def header(cls, text): return f"{cls.BOLD}{cls.HEADER}{text}{cls.RESET}"
    @classmethod
    def stats(cls, text): return f"{cls.STATS}{text}{cls.RESET}"
    @classmethod
    def todo(cls, text): return f"{cls.TODO}{text}{cls.RESET}"
    @classmethod
    def prompt(cls, text): return f"{cls.PROMPT}{text}{cls.RESET}"
    @classmethod
    def response(cls, text): return f"{cls.RESPONSE}{text}{cls.RESET}"


# ==============================================================================
# TODO 2: Implement get_pr_security_findings as a Strands @tool
# ==============================================================================

# TODO 2: Uncomment and complete this function
# @tool
# def get_pr_security_findings(repo: str, pr_number: int) -> str:
#     """Fetch security findings posted by AWS Security Agent on a GitHub PR.
#
#     Security Agent posts findings as GitHub PR review comments (inline) and
#     as general PR comments for summaries. Retrieve both types.
#
#     Args:
#         repo: GitHub repository in 'owner/repo' format
#         pr_number: Pull request number to fetch findings from
#     """
#     g = Github(GITHUB_TOKEN)
#     repo_obj = g.get_repo(repo)
#     pr = repo_obj.get_pull(pr_number)
#
#     findings = []
#
#     # Inline review comments (bot user type = "Bot")
#     for comment in pr.get_review_comments():
#         if comment.user and comment.user.type == "Bot":
#             findings.append({
#                 "type": "inline_comment",
#                 "body": comment.body,
#                 "file": comment.path,
#                 "line": comment.line,
#                 "author": comment.user.login
#             })
#
#     # General PR comments mentioning security keywords
#     security_keywords = ["security", "vulnerability", "finding", "owasp",
#                          "injection", "xss", "csrf", "critical", "high"]
#     for comment in pr.get_issue_comments():
#         if comment.user and comment.user.type == "Bot":
#             if any(kw in comment.body.lower() for kw in security_keywords):
#                 findings.append({
#                     "type": "pr_comment",
#                     "body": comment.body,
#                     "author": comment.user.login
#                 })
#
#     return json.dumps({
#         "repo": repo, "pr_number": pr_number,
#         "pr_title": pr.title, "findings_count": len(findings),
#         "findings": findings
#     }, indent=2)

def get_pr_security_findings(repo: str, pr_number: int) -> str:
    """Placeholder — complete TODO 2 to implement this."""
    print(Colors.todo("TODO 2: Implement get_pr_security_findings() with @tool decorator"))
    return json.dumps({"error": "Not implemented yet", "repo": repo})


# ==============================================================================
# TODO 3: Implement get_pr_diff as a Strands @tool
# ==============================================================================

# TODO 3: Uncomment and complete this function
# @tool
# def get_pr_diff(repo: str, pr_number: int) -> str:
#     """Get the code diff for a pull request to provide context for security analysis.
#
#     Use this after get_pr_security_findings to see the code changes that triggered
#     the findings. Helps the agent suggest more precise fixes.
#
#     Args:
#         repo: GitHub repository in 'owner/repo' format
#         pr_number: Pull request number
#     """
#     g = Github(GITHUB_TOKEN)
#     repo_obj = g.get_repo(repo)
#     pr = repo_obj.get_pull(pr_number)
#
#     files = []
#     for f in pr.get_files():
#         files.append({
#             "filename": f.filename,
#             "status": f.status,
#             "additions": f.additions,
#             "deletions": f.deletions,
#             "patch": f.patch[:3000] if f.patch else None
#         })
#
#     return json.dumps({
#         "pr_number": pr_number,
#         "files_changed": len(files),
#         "files": files
#     }, indent=2)

def get_pr_diff(repo: str, pr_number: int) -> str:
    """Placeholder — complete TODO 3 to implement this."""
    print(Colors.todo("TODO 3: Implement get_pr_diff() with @tool decorator"))
    return json.dumps({"error": "Not implemented yet"})


# ==============================================================================
# Step 2 (provided): Direct PR inspection without Strands
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

        bot_comments = [c for c in pr.get_review_comments()
                        if c.user and c.user.type == "Bot"]
        if bot_comments:
            print(Colors.stats(f"  Found {len(bot_comments)} Security Agent review comment(s)"))
        else:
            print(Colors.stats("  No bot review comments found yet."))
            print(Colors.stats("  Ensure Security Agent has reviewed this PR (check console)."))
        return len(bot_comments)
    except GithubException as e:
        print(f"  GitHub error: {e}")
        return 0


# ==============================================================================
# TODO 4: Build and run the remediation agent
# ==============================================================================

def run_remediation_agent(repo: str, pr_number: int) -> None:
    """Run a Strands agent that retrieves PR findings and generates a remediation report.

    Steps:
        1. Create a BedrockModel with DEFAULT_MODEL and AWS_REGION, max_tokens=4096
        2. Create an Agent with:
               model=model
               tools=[get_pr_security_findings, get_pr_diff]
               system_prompt=(
                   "You are a senior security engineer reviewing findings from AWS Security Agent. "
                   "For each finding: explain the vulnerability + OWASP category, "
                   "why it's dangerous, and a concrete before/after code fix. "
                   "Organize by severity. Format as Markdown."
               )
        3. Call agent() asking it to:
               - Fetch findings from PR #{pr_number} in {repo}
               - Get the code diff for context
               - Generate a complete remediation report
        4. Print the response
    """
    # TODO 4: Implement run_remediation_agent()
    # model = BedrockModel(model_id=DEFAULT_MODEL, region_name=AWS_REGION, max_tokens=4096)
    # agent = Agent(
    #     model=model,
    #     tools=[get_pr_security_findings, get_pr_diff],
    #     system_prompt=(
    #         "You are a senior security engineer reviewing findings from AWS Security Agent. "
    #         "For each finding, provide: "
    #         "1) The vulnerability type and OWASP category, "
    #         "2) Why it is dangerous, "
    #         "3) A concrete before/after code fix. "
    #         "Organize by severity (CRITICAL first). Format as Markdown."
    #     )
    # )
    # response = agent(
    #     f"Analyze security findings on PR #{pr_number} in {repo}. "
    #     "Get the code diff for context. Generate a complete remediation report."
    # )
    # print(response)

    print(Colors.todo("TODO 4: Implement run_remediation_agent()"))


# ==============================================================================
# Main
# ==============================================================================

def main():
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 15: AWS Security Agent - PR Findings Analyzer"))
    print(Colors.header(f" Region: {AWS_REGION}  |  Model: {DEFAULT_MODEL}"))
    print(Colors.header("=" * 70))

    if not GITHUB_TOKEN:
        print("\nError: GITHUB_TOKEN not set.")
        print("  export GITHUB_TOKEN=your-github-pat")
        return

    if not GITHUB_REPO or not PR_NUMBER:
        print("\nError: GITHUB_REPO and PR_NUMBER are required.")
        print("  export GITHUB_REPO=owner/repo-name")
        print("  export PR_NUMBER=42")
        return

    # Step 1: Inspect PR findings
    print(Colors.header("\n1. Fetching Security Agent findings from PR"))
    print("-" * 40)
    print(Colors.stats(f"  Repo: {GITHUB_REPO}  |  PR: #{PR_NUMBER}"))
    inspect_pr_findings(GITHUB_REPO, PR_NUMBER)

    # TODO 2-4: Remediation agent
    print(Colors.header("\n2. Remediation agent"))
    print("-" * 40)
    run_remediation_agent(GITHUB_REPO, PR_NUMBER)

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 15 Complete!"))
    print(Colors.header("=" * 70))


if __name__ == "__main__":
    main()
