"""
Kata 08: Strands GitHub PR Agent - Solution

This script demonstrates how to create a GitHub PR agent using Strands,
designed for integration with OSS Risk Mitigation workflows.

Prerequisites:
    pip install 'strands-agents[anthropic]' PyGithub python-dotenv
    export ANTHROPIC_API_KEY="your-key-here"
    export GITHUB_TOKEN="your-github-token"

Usage:
    python solution.py              # Run interactive demo
    python solution.py --mock       # Run with mock tools (no GitHub API)
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from strands import Agent, tool
from strands.models.anthropic import AnthropicModel

from github_tools import (
    create_github_pr_agent,
    github_create_branch,
    github_commit_file,
    github_create_pr,
    github_list_prs,
    github_get_pr,
    github_get_file,
)

load_dotenv()


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[96m'
    PROMPT = '\033[93m'
    RESPONSE = '\033[92m'
    ERROR = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    @classmethod
    def header(cls, text):
        return f"{cls.BOLD}{cls.HEADER}{text}{cls.RESET}"

    @classmethod
    def prompt(cls, text):
        return f"{cls.PROMPT}{text}{cls.RESET}"

    @classmethod
    def response(cls, text):
        return f"{cls.RESPONSE}{text}{cls.RESET}"

    @classmethod
    def error(cls, text):
        return f"{cls.ERROR}{text}{cls.RESET}"


# ==============================================================================
# Mock Tools for Testing Without GitHub API
# ==============================================================================

@tool
def mock_github_create_branch(
    repo_full_name: str,
    branch_name: str,
    base_branch: str = "main"
) -> str:
    """[MOCK] Create a new branch from a base branch.

    Args:
        repo_full_name: Repository in 'owner/repo' format.
        branch_name: Name for the new branch.
        base_branch: Branch to create from (default: main).
    """
    return (
        f"[MOCK] Branch created successfully!\n"
        f"Repository: {repo_full_name}\n"
        f"Branch: {branch_name}\n"
        f"Based on: {base_branch} (SHA: abc12345)"
    )


@tool
def mock_github_commit_file(
    repo_full_name: str,
    file_path: str,
    content: str,
    commit_message: str,
    branch: str
) -> str:
    """[MOCK] Commit a file to a branch in a GitHub repository.

    Args:
        repo_full_name: Repository in 'owner/repo' format.
        file_path: Path to the file in the repository.
        content: The file content to commit.
        commit_message: Git commit message.
        branch: Target branch for the commit.
    """
    return (
        f"[MOCK] File created successfully!\n"
        f"Repository: {repo_full_name}\n"
        f"Path: {file_path}\n"
        f"Branch: {branch}\n"
        f"Commit: def67890\n"
        f"Message: {commit_message}"
    )


@tool
def mock_github_create_pr(
    repo_full_name: str,
    title: str,
    body: str,
    head_branch: str,
    base_branch: str = "main"
) -> str:
    """[MOCK] Create a pull request.

    Args:
        repo_full_name: Repository in 'owner/repo' format.
        title: Pull request title.
        body: Pull request description (markdown supported).
        head_branch: Branch containing changes.
        base_branch: Branch to merge into (default: main).
    """
    return (
        f"[MOCK] Pull request created successfully!\n"
        f"PR #42: {title}\n"
        f"URL: https://github.com/{repo_full_name}/pull/42\n"
        f"State: open\n"
        f"Head: {head_branch} → Base: {base_branch}"
    )


@tool
def mock_github_list_prs(
    repo_full_name: str,
    state: str = "open",
    max_results: int = 10
) -> str:
    """[MOCK] List pull requests in a repository.

    Args:
        repo_full_name: Repository in 'owner/repo' format.
        state: PR state filter ('open', 'closed', 'all').
        max_results: Maximum number of PRs to return.
    """
    return (
        f"[MOCK] Pull requests in {repo_full_name} (state: {state}):\n\n"
        f"#42: Update OSS RMP: openssl vulnerability\n"
        f"   State: open | Branch: rmp/openssl-2024-01 → main\n"
        f"   Created: 2024-01-15 | URL: https://github.com/{repo_full_name}/pull/42\n\n"
        f"#41: Update OSS RMP: zlib patch\n"
        f"   State: open | Branch: rmp/zlib-2024-01 → main\n"
        f"   Created: 2024-01-10 | URL: https://github.com/{repo_full_name}/pull/41"
    )


@tool
def mock_github_get_pr(
    repo_full_name: str,
    pr_number: int
) -> str:
    """[MOCK] Get details of a specific pull request.

    Args:
        repo_full_name: Repository in 'owner/repo' format.
        pr_number: The pull request number.
    """
    return (
        f"[MOCK] Pull Request #{pr_number}: Update OSS RMP: openssl vulnerability\n"
        f"State: open | Mergeable: True\n"
        f"Branch: rmp/openssl-2024-01 → main\n"
        f"Author: oss-bot\n"
        f"Created: 2024-01-15 10:30\n"
        f"Updated: 2024-01-15 14:22\n"
        f"Reviews: 0 approved, 0 changes requested\n"
        f"URL: https://github.com/{repo_full_name}/pull/{pr_number}\n\n"
        f"Description:\n"
        f"## Summary\n"
        f"Updated Risk Mitigation Plan for openssl CVE-2024-XXXX\n\n"
        f"## Changes\n"
        f"- Risk level: HIGH → MEDIUM (patch available)\n"
        f"- Mitigation: Upgrade to openssl 3.0.13"
    )


@tool
def mock_github_get_file(
    repo_full_name: str,
    file_path: str,
    branch: str = "main"
) -> str:
    """[MOCK] Get contents of a file from a repository.

    Args:
        repo_full_name: Repository in 'owner/repo' format.
        file_path: Path to the file.
        branch: Branch to read from (default: main).
    """
    return (
        f"[MOCK] File: {file_path} (branch: {branch})\n"
        f"Size: 1234 bytes\n"
        f"SHA: abc12345\n"
        f"---\n"
        f"# OSS Risk Mitigation Plan\n\n"
        f"## Component: openssl\n"
        f"- Version: 3.0.12\n"
        f"- License: Apache-2.0\n"
        f"- Risk Level: HIGH\n"
        f"- CVEs: CVE-2024-XXXX\n\n"
        f"## Mitigation\n"
        f"Awaiting patch release."
    )


def create_mock_agent(
    model_id: str = "claude-haiku-4-5-20251001",
    max_tokens: int = 2048
) -> Agent:
    """Create a mock GitHub PR agent for testing without API calls."""
    model = AnthropicModel(
        model_id=model_id,
        max_tokens=max_tokens
    )

    agent = Agent(
        model=model,
        tools=[
            mock_github_create_branch,
            mock_github_commit_file,
            mock_github_create_pr,
            mock_github_list_prs,
            mock_github_get_pr,
            mock_github_get_file,
        ],
        system_prompt="""You are a GitHub PR assistant specializing in OSS Risk Mitigation.

Your responsibilities:
1. Create branches for Risk Mitigation Plan (RMP) updates
2. Commit updated RMP files to branches
3. Create pull requests with clear descriptions of changes
4. Check for existing PRs to avoid duplicates
5. Provide summaries of PR status

Note: You are running in MOCK mode. All GitHub operations are simulated.

When creating PRs for RMP updates:
- Use descriptive branch names like 'rmp/update-<component>-<date>'
- Include a clear summary of risk findings in the PR body
- List the affected components and their risk levels"""
    )

    return agent


# ==============================================================================
# Demo Scenarios
# ==============================================================================

def demo_oss_risk_mitigation_workflow(agent: Agent, repo: str):
    """Demonstrate a complete OSS Risk Mitigation workflow."""
    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" OSS Risk Mitigation Workflow Demo"))
    print(Colors.header("=" * 70))

    # Simulate an RMP update scenario
    rmp_content = """# OSS Risk Mitigation Plan

## Component: log4j
- **Version**: 2.17.1
- **License**: Apache-2.0
- **Risk Level**: LOW (previously CRITICAL)
- **CVEs**: CVE-2021-44228 (Log4Shell) - RESOLVED

## Analysis Date
{date}

## Mitigation Status
- [x] Identified vulnerability
- [x] Assessed impact
- [x] Applied patch (upgrade to 2.17.1)
- [x] Verified fix

## Recommendation
Continue monitoring for new CVEs. Current version is safe.
""".format(date=datetime.now().strftime("%Y-%m-%d"))

    queries = [
        (
            "Step 1: Check existing PRs",
            f"List any open pull requests in {repo} related to risk mitigation."
        ),
        (
            "Step 2: Create PR workflow",
            f"""Create a complete PR workflow for an OSS Risk Mitigation Plan update:

Repository: {repo}
Component: log4j
Previous Risk: CRITICAL (CVE-2021-44228)
New Risk: LOW (patched to 2.17.1)

Please:
1. Create a branch named 'rmp/log4j-{datetime.now().strftime("%Y%m%d")}'
2. Commit the RMP file to 'docs/rmp/log4j.md'
3. Create a PR with a clear description of the risk changes

RMP Content to commit:
{rmp_content}"""
        ),
    ]

    for title, query in queries:
        print(Colors.header(f"\n{title}"))
        print("-" * 50)
        print(Colors.prompt(f"Query: {query[:200]}..."))
        print()

        try:
            response = agent(query)
            print(Colors.response(f"Agent:\n{response}"))
        except Exception as e:
            print(Colors.error(f"Error: {e}"))


def demo_interactive(agent: Agent):
    """Run an interactive session with the agent."""
    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Interactive GitHub PR Agent"))
    print(Colors.header("=" * 70))
    print("\nType your queries or commands. Type 'quit' to exit.\n")
    print("Example queries:")
    print("  - List open PRs in owner/repo")
    print("  - Get details of PR #42 in owner/repo")
    print("  - Create a branch 'feature/test' in owner/repo")
    print()

    while True:
        try:
            query = input(Colors.prompt("You: ")).strip()
            if query.lower() in ('quit', 'exit', 'q'):
                print("Goodbye!")
                break
            if not query:
                continue

            response = agent(query)
            print(Colors.response(f"Agent: {response}\n"))

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(Colors.error(f"Error: {e}\n"))


# ==============================================================================
# Main Entry Point
# ==============================================================================

def main():
    """Run the GitHub PR Agent demo."""
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 08: Strands GitHub PR Agent"))
    print(Colors.header("=" * 70))

    # Check for mock mode
    use_mock = "--mock" in sys.argv or not os.getenv("GITHUB_TOKEN")

    if use_mock:
        print(Colors.prompt("\nRunning in MOCK mode (no GitHub API calls)"))
        print("To use real GitHub API, set GITHUB_TOKEN environment variable.\n")
        agent = create_mock_agent()
    else:
        print(Colors.prompt("\nRunning with real GitHub API"))
        print("GITHUB_TOKEN is configured.\n")
        agent = create_github_pr_agent()

    # Demo repository (use a test repo for real mode)
    demo_repo = "acme-corp/oss-policies"

    # Run workflow demo
    demo_oss_risk_mitigation_workflow(agent, demo_repo)

    # Offer interactive mode
    print(Colors.header("\n" + "=" * 70))
    response = input("\nWould you like to enter interactive mode? (y/n): ").strip().lower()
    if response in ('y', 'yes'):
        demo_interactive(agent)

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 08 Complete!"))
    print(Colors.header("=" * 70))


if __name__ == "__main__":
    main()
