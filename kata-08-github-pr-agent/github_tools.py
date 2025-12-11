"""
GitHub PR Tools for Strands Agents

This module provides GitHub tools for creating and managing pull requests,
designed for integration with the OSS Risk Mitigation system.

Prerequisites:
    pip install 'strands-agents[anthropic]' PyGithub python-dotenv
    export GITHUB_TOKEN="your-github-token"
"""

import os
import base64
from typing import Optional
from dotenv import load_dotenv
from strands import Agent, tool
from strands.models.anthropic import AnthropicModel
from github import Github, GithubException

load_dotenv()

# GitHub configuration via environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_BASE_URL = os.getenv("GITHUB_BASE_URL", "https://api.github.com")

# Global client (initialized on demand)
_github_client: Optional[Github] = None


def get_github_client() -> Github:
    """Get or create the GitHub client singleton.

    Raises:
        ValueError: If GITHUB_TOKEN is not configured.
    """
    global _github_client

    if _github_client is None:
        if not GITHUB_TOKEN:
            raise ValueError(
                "GITHUB_TOKEN environment variable is required. "
                "Create a token at https://github.com/settings/tokens with 'repo' scope."
            )

        # Support GitHub Enterprise with custom base URL
        if GITHUB_BASE_URL != "https://api.github.com":
            _github_client = Github(
                login_or_token=GITHUB_TOKEN,
                base_url=GITHUB_BASE_URL
            )
        else:
            _github_client = Github(login_or_token=GITHUB_TOKEN)

    return _github_client


# ==============================================================================
# GitHub Tool Definitions
# ==============================================================================

@tool
def github_create_branch(
    repo_full_name: str,
    branch_name: str,
    base_branch: str = "main"
) -> str:
    """Create a new branch from a base branch in a GitHub repository.

    Args:
        repo_full_name: Repository in 'owner/repo' format (e.g., 'acme-corp/oss-policies').
        branch_name: Name for the new branch (e.g., 'rmp/update-log4j-2024-01').
        base_branch: Branch to create from (default: main).
    """
    try:
        gh = get_github_client()
        repo = gh.get_repo(repo_full_name)

        # Get the SHA of the base branch
        base_ref = repo.get_git_ref(f"heads/{base_branch}")
        base_sha = base_ref.object.sha

        # Create new branch
        repo.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=base_sha
        )

        return (
            f"Branch created successfully!\n"
            f"Repository: {repo_full_name}\n"
            f"Branch: {branch_name}\n"
            f"Based on: {base_branch} (SHA: {base_sha[:8]})"
        )

    except GithubException as e:
        if e.status == 401:
            return "Error: Invalid GitHub token. Check your GITHUB_TOKEN."
        elif e.status == 403:
            return f"Error: Permission denied. Token may lack 'repo' scope. {e.data.get('message', '')}"
        elif e.status == 404:
            return f"Error: Repository '{repo_full_name}' or branch '{base_branch}' not found."
        elif e.status == 422:
            return f"Error: Branch '{branch_name}' may already exist. {e.data.get('message', '')}"
        else:
            return f"GitHub API error ({e.status}): {e.data.get('message', str(e))}"
    except ValueError as e:
        return f"Configuration error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {type(e).__name__}: {str(e)}"


@tool
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
        file_path: Path to the file in the repository (e.g., 'docs/rmp/log4j.md').
        content: The file content to commit.
        commit_message: Git commit message describing the change.
        branch: Target branch for the commit.
    """
    try:
        gh = get_github_client()
        repo = gh.get_repo(repo_full_name)

        # Check if file already exists (for update vs create)
        try:
            existing_file = repo.get_contents(file_path, ref=branch)
            sha = existing_file.sha
            result = repo.update_file(
                path=file_path,
                message=commit_message,
                content=content,
                sha=sha,
                branch=branch
            )
            action = "updated"
        except GithubException as e:
            if e.status == 404:
                # File doesn't exist, create it
                result = repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    branch=branch
                )
                action = "created"
            else:
                raise

        commit_sha = result["commit"].sha

        return (
            f"File {action} successfully!\n"
            f"Repository: {repo_full_name}\n"
            f"Path: {file_path}\n"
            f"Branch: {branch}\n"
            f"Commit: {commit_sha[:8]}\n"
            f"Message: {commit_message}"
        )

    except GithubException as e:
        if e.status == 401:
            return "Error: Invalid GitHub token. Check your GITHUB_TOKEN."
        elif e.status == 403:
            return f"Error: Permission denied. {e.data.get('message', '')}"
        elif e.status == 404:
            return f"Error: Repository '{repo_full_name}' or branch '{branch}' not found."
        elif e.status == 409:
            return f"Error: Conflict - file may have been modified. {e.data.get('message', '')}"
        else:
            return f"GitHub API error ({e.status}): {e.data.get('message', str(e))}"
    except ValueError as e:
        return f"Configuration error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {type(e).__name__}: {str(e)}"


@tool
def github_create_pr(
    repo_full_name: str,
    title: str,
    body: str,
    head_branch: str,
    base_branch: str = "main"
) -> str:
    """Create a pull request in a GitHub repository.

    Args:
        repo_full_name: Repository in 'owner/repo' format.
        title: Pull request title (e.g., 'Update OSS RMP: log4j vulnerability').
        body: Pull request description/body (markdown supported).
        head_branch: Branch containing changes (e.g., 'rmp/update-log4j').
        base_branch: Branch to merge into (default: main).
    """
    try:
        gh = get_github_client()
        repo = gh.get_repo(repo_full_name)

        pr = repo.create_pull(
            title=title,
            body=body,
            head=head_branch,
            base=base_branch
        )

        return (
            f"Pull request created successfully!\n"
            f"PR #{pr.number}: {pr.title}\n"
            f"URL: {pr.html_url}\n"
            f"State: {pr.state}\n"
            f"Head: {head_branch} → Base: {base_branch}"
        )

    except GithubException as e:
        if e.status == 401:
            return "Error: Invalid GitHub token. Check your GITHUB_TOKEN."
        elif e.status == 403:
            return f"Error: Permission denied. {e.data.get('message', '')}"
        elif e.status == 404:
            return f"Error: Repository '{repo_full_name}' not found or not accessible."
        elif e.status == 422:
            msg = e.data.get('message', '')
            if 'already exists' in str(e.data).lower():
                return f"Error: A pull request already exists for branch '{head_branch}'. {msg}"
            return f"Error: Could not create PR. {msg}"
        else:
            return f"GitHub API error ({e.status}): {e.data.get('message', str(e))}"
    except ValueError as e:
        return f"Configuration error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {type(e).__name__}: {str(e)}"


@tool
def github_list_prs(
    repo_full_name: str,
    state: str = "open",
    max_results: int = 10
) -> str:
    """List pull requests in a GitHub repository.

    Args:
        repo_full_name: Repository in 'owner/repo' format.
        state: PR state filter ('open', 'closed', or 'all').
        max_results: Maximum number of PRs to return (default: 10).
    """
    try:
        gh = get_github_client()
        repo = gh.get_repo(repo_full_name)

        prs = repo.get_pulls(state=state, sort="updated", direction="desc")

        results = []
        count = 0
        for pr in prs:
            if count >= max_results:
                break
            results.append(
                f"#{pr.number}: {pr.title}\n"
                f"   State: {pr.state} | Branch: {pr.head.ref} → {pr.base.ref}\n"
                f"   Created: {pr.created_at.strftime('%Y-%m-%d')} | URL: {pr.html_url}"
            )
            count += 1

        if not results:
            return f"No {state} pull requests found in {repo_full_name}."

        header = f"Pull requests in {repo_full_name} (state: {state}):\n"
        return header + "\n\n".join(results)

    except GithubException as e:
        if e.status == 401:
            return "Error: Invalid GitHub token. Check your GITHUB_TOKEN."
        elif e.status == 404:
            return f"Error: Repository '{repo_full_name}' not found."
        else:
            return f"GitHub API error ({e.status}): {e.data.get('message', str(e))}"
    except ValueError as e:
        return f"Configuration error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {type(e).__name__}: {str(e)}"


@tool
def github_get_pr(
    repo_full_name: str,
    pr_number: int
) -> str:
    """Get details of a specific pull request.

    Args:
        repo_full_name: Repository in 'owner/repo' format.
        pr_number: The pull request number.
    """
    try:
        gh = get_github_client()
        repo = gh.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)

        # Get review state
        reviews = list(pr.get_reviews())
        review_summary = "No reviews yet"
        if reviews:
            approved = sum(1 for r in reviews if r.state == "APPROVED")
            changes_requested = sum(1 for r in reviews if r.state == "CHANGES_REQUESTED")
            review_summary = f"{approved} approved, {changes_requested} changes requested"

        return (
            f"Pull Request #{pr.number}: {pr.title}\n"
            f"State: {pr.state} | Mergeable: {pr.mergeable}\n"
            f"Branch: {pr.head.ref} → {pr.base.ref}\n"
            f"Author: {pr.user.login}\n"
            f"Created: {pr.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"Updated: {pr.updated_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"Reviews: {review_summary}\n"
            f"URL: {pr.html_url}\n\n"
            f"Description:\n{pr.body or '(No description)'}"
        )

    except GithubException as e:
        if e.status == 401:
            return "Error: Invalid GitHub token. Check your GITHUB_TOKEN."
        elif e.status == 404:
            return f"Error: PR #{pr_number} not found in '{repo_full_name}'."
        else:
            return f"GitHub API error ({e.status}): {e.data.get('message', str(e))}"
    except ValueError as e:
        return f"Configuration error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {type(e).__name__}: {str(e)}"


@tool
def github_get_file(
    repo_full_name: str,
    file_path: str,
    branch: str = "main"
) -> str:
    """Get contents of a file from a GitHub repository.

    Args:
        repo_full_name: Repository in 'owner/repo' format.
        file_path: Path to the file in the repository.
        branch: Branch to read from (default: main).
    """
    try:
        gh = get_github_client()
        repo = gh.get_repo(repo_full_name)

        file_content = repo.get_contents(file_path, ref=branch)

        # Decode content
        if file_content.encoding == "base64":
            content = base64.b64decode(file_content.content).decode("utf-8")
        else:
            content = file_content.content

        # Truncate if very long
        if len(content) > 10000:
            content = content[:10000] + "\n\n... [truncated, file too large]"

        return (
            f"File: {file_path} (branch: {branch})\n"
            f"Size: {file_content.size} bytes\n"
            f"SHA: {file_content.sha[:8]}\n"
            f"---\n{content}"
        )

    except GithubException as e:
        if e.status == 401:
            return "Error: Invalid GitHub token. Check your GITHUB_TOKEN."
        elif e.status == 404:
            return f"Error: File '{file_path}' not found in '{repo_full_name}' on branch '{branch}'."
        else:
            return f"GitHub API error ({e.status}): {e.data.get('message', str(e))}"
    except ValueError as e:
        return f"Configuration error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {type(e).__name__}: {str(e)}"


# ==============================================================================
# Agent Factory
# ==============================================================================

def create_github_pr_agent(
    model_id: str = "claude-haiku-4-5-20251001",
    max_tokens: int = 2048
) -> Agent:
    """Create a GitHub PR agent with all GitHub tools.

    Args:
        model_id: The Anthropic model to use.
        max_tokens: Maximum tokens for responses.

    Returns:
        A Strands Agent configured with GitHub tools.
    """
    model = AnthropicModel(
        model_id=model_id,
        max_tokens=max_tokens
    )

    agent = Agent(
        model=model,
        tools=[
            github_create_branch,
            github_commit_file,
            github_create_pr,
            github_list_prs,
            github_get_pr,
            github_get_file,
        ],
        system_prompt="""You are a GitHub PR assistant specializing in OSS Risk Mitigation.

Your responsibilities:
1. Create branches for Risk Mitigation Plan (RMP) updates
2. Commit updated RMP files to branches
3. Create pull requests with clear descriptions of changes
4. Check for existing PRs to avoid duplicates
5. Provide summaries of PR status

When creating PRs for RMP updates:
- Use descriptive branch names like 'rmp/update-<component>-<date>'
- Include a clear summary of risk findings in the PR body
- List the affected components and their risk levels
- Reference any related SBOM data when available

Always verify operations completed successfully before proceeding to the next step.
When errors occur, explain them clearly and suggest fixes."""
    )

    return agent


# ==============================================================================
# Standalone Usage
# ==============================================================================

if __name__ == "__main__":
    # Simple test to verify tools are defined correctly
    print("GitHub PR Tools for Strands Agents")
    print("=" * 50)
    print("\nAvailable tools:")
    print("  - github_create_branch")
    print("  - github_commit_file")
    print("  - github_create_pr")
    print("  - github_list_prs")
    print("  - github_get_pr")
    print("  - github_get_file")
    print("\nUsage:")
    print("  from github_tools import create_github_pr_agent")
    print("  agent = create_github_pr_agent()")
    print("  response = agent('List open PRs in owner/repo')")
    print("\nRequired environment variables:")
    print(f"  GITHUB_TOKEN: {'Set' if GITHUB_TOKEN else 'NOT SET'}")
    print(f"  GITHUB_BASE_URL: {GITHUB_BASE_URL}")
