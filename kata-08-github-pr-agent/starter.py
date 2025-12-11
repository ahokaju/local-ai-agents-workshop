"""
Kata 08: Strands GitHub PR Agent - Starter Template

In this kata, you'll build a GitHub PR agent using Strands that can:
- Create branches
- Commit files
- Create pull requests
- List and view PRs

This is designed for integration with OSS Risk Mitigation workflows.

Prerequisites:
    pip install 'strands-agents[anthropic]' PyGithub python-dotenv
    export ANTHROPIC_API_KEY="your-key-here"
    export GITHUB_TOKEN="your-github-token"

Learning Objectives:
    1. Define tools using the @tool decorator
    2. Handle API errors gracefully
    3. Create an agent with multiple tools
    4. Build tools that work together in workflows
"""

import os
from typing import Optional
from dotenv import load_dotenv

# TODO 1: Import the required modules from strands and github
# Hint: You need Agent, tool from strands
#       AnthropicModel from strands.models.anthropic
#       Github, GithubException from github


load_dotenv()

# GitHub configuration via environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
_github_client = None


def get_github_client():
    """Get or create the GitHub client singleton.

    TODO 2: Implement this function
    - Check if _github_client is None
    - If GITHUB_TOKEN is not set, raise ValueError
    - Create and cache a Github client
    - Return the client

    Hint: Use the global keyword to modify _github_client
    """
    global _github_client

    # Your implementation here
    pass


# ==============================================================================
# TODO 3: Implement the github_create_branch tool
# ==============================================================================

# @tool
def github_create_branch(
    repo_full_name: str,
    branch_name: str,
    base_branch: str = "main"
) -> str:
    """Create a new branch from a base branch.

    Args:
        repo_full_name: Repository in 'owner/repo' format.
        branch_name: Name for the new branch.
        base_branch: Branch to create from (default: main).

    TODO: Implement this function
    - Get the GitHub client
    - Get the repository using gh.get_repo()
    - Get the base branch's SHA using repo.get_git_ref()
    - Create the new branch using repo.create_git_ref()
    - Handle GithubException errors (401, 403, 404, 422)
    - Return a success message with branch details
    """
    pass


# ==============================================================================
# TODO 4: Implement the github_commit_file tool
# ==============================================================================

# @tool
def github_commit_file(
    repo_full_name: str,
    file_path: str,
    content: str,
    commit_message: str,
    branch: str
) -> str:
    """Commit a file to a branch in a GitHub repository.

    Args:
        repo_full_name: Repository in 'owner/repo' format.
        file_path: Path to the file in the repository.
        content: The file content to commit.
        commit_message: Git commit message.
        branch: Target branch for the commit.

    TODO: Implement this function
    - Get the GitHub client
    - Get the repository
    - Try to get existing file with repo.get_contents()
    - If file exists, use repo.update_file() with the SHA
    - If file doesn't exist (404), use repo.create_file()
    - Handle errors appropriately
    - Return a success message
    """
    pass


# ==============================================================================
# TODO 5: Implement the github_create_pr tool
# ==============================================================================

# @tool
def github_create_pr(
    repo_full_name: str,
    title: str,
    body: str,
    head_branch: str,
    base_branch: str = "main"
) -> str:
    """Create a pull request.

    Args:
        repo_full_name: Repository in 'owner/repo' format.
        title: Pull request title.
        body: Pull request description (markdown supported).
        head_branch: Branch containing changes.
        base_branch: Branch to merge into (default: main).

    TODO: Implement this function
    - Get the GitHub client
    - Get the repository
    - Create a PR using repo.create_pull()
    - Handle 422 error for duplicate PRs
    - Return PR number, title, and URL
    """
    pass


# ==============================================================================
# TODO 6: Implement the github_list_prs tool
# ==============================================================================

# @tool
def github_list_prs(
    repo_full_name: str,
    state: str = "open",
    max_results: int = 10
) -> str:
    """List pull requests in a repository.

    Args:
        repo_full_name: Repository in 'owner/repo' format.
        state: PR state filter ('open', 'closed', 'all').
        max_results: Maximum number of PRs to return.

    TODO: Implement this function
    - Get the GitHub client
    - Get the repository
    - Get PRs using repo.get_pulls(state=state)
    - Iterate through PRs (up to max_results)
    - Format each PR with number, title, state, branches
    - Return formatted list
    """
    pass


# ==============================================================================
# TODO 7: Implement the github_get_pr tool
# ==============================================================================

# @tool
def github_get_pr(
    repo_full_name: str,
    pr_number: int
) -> str:
    """Get details of a specific pull request.

    Args:
        repo_full_name: Repository in 'owner/repo' format.
        pr_number: The pull request number.

    TODO: Implement this function
    - Get the GitHub client
    - Get the repository
    - Get the PR using repo.get_pull(pr_number)
    - Get review info using pr.get_reviews()
    - Return detailed PR info (title, state, author, dates, etc.)
    """
    pass


# ==============================================================================
# TODO 8: Create the agent factory function
# ==============================================================================

def create_github_pr_agent(
    model_id: str = "claude-haiku-4-5-20251001",
    max_tokens: int = 2048
):
    """Create a GitHub PR agent with all GitHub tools.

    TODO: Implement this function
    - Create an AnthropicModel with the given model_id
    - Create an Agent with:
      - The model
      - All your GitHub tools in a list
      - A system prompt describing the agent's purpose

    Hint: The system prompt should explain:
    - That the agent handles GitHub PRs for OSS Risk Mitigation
    - How to name branches (e.g., 'rmp/update-<component>-<date>')
    - What to include in PR descriptions
    """
    pass


# ==============================================================================
# Main Demo
# ==============================================================================

def main():
    """Run a demo of the GitHub PR agent."""
    print("=" * 60)
    print(" Kata 08: GitHub PR Agent - Starter")
    print("=" * 60)

    # Check configuration
    if not GITHUB_TOKEN:
        print("\nWarning: GITHUB_TOKEN not set.")
        print("Set it to use real GitHub API, or run solution.py --mock")
        return

    # TODO 9: Create the agent and test it
    # Uncomment and complete:
    #
    # agent = create_github_pr_agent()
    #
    # # Test query
    # response = agent("List open PRs in owner/repo")
    # print(f"Agent: {response}")

    print("\nImplement the TODOs and run again!")


if __name__ == "__main__":
    main()
