# Kata 08: Strands GitHub PR Agent

Build a Strands agent that can create and manage GitHub pull requests for OSS Risk Mitigation workflows.

## Learning Objectives

- Create tools using the `@tool` decorator for external API integration
- Handle API authentication via environment variables
- Implement comprehensive error handling for REST APIs
- Build an agent that orchestrates multiple tools in workflows

## Scenario: OSS Risk Mitigation

Your organization needs to automate the process of updating Open Source Software (OSS) Risk Mitigation Plans. When security vulnerabilities are found in dependencies, an agent should:

1. Create a feature branch for the update
2. Commit the updated RMP document
3. Create a pull request for human review
4. Track existing PRs to avoid duplicates

## Prerequisites

```bash
# Install dependencies
pip install 'strands-agents[anthropic]' PyGithub python-dotenv

# Set environment variables
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export GITHUB_TOKEN="your-github-token"  # Needs 'repo' scope
```

### Creating a GitHub Token

1. Go to [GitHub Settings > Developer Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Generate a new token (classic) with `repo` scope
3. Copy and set as `GITHUB_TOKEN` environment variable

## Files

| File | Description |
|------|-------------|
| `README.md` | This file - kata instructions |
| `starter.py` | Template with TODOs for you to implement |
| `solution.py` | Complete working implementation |
| `github_tools.py` | Reusable GitHub tools module |
| `test_github_tools.py` | Unit tests with mocking |

## Difficulty Levels

### Level 1: Independent Implementation
Try implementing the GitHub tools yourself using only the docstrings in `starter.py`.

### Level 2: Guided Implementation
Follow the TODO comments in `starter.py` step by step.

### Level 3: Study Solution
Review `solution.py` and `github_tools.py` to understand the patterns.

## Tools to Implement

| Tool | Purpose |
|------|---------|
| `github_create_branch` | Create a new branch from base |
| `github_commit_file` | Commit a file to a branch |
| `github_create_pr` | Create a pull request |
| `github_list_prs` | List pull requests |
| `github_get_pr` | Get PR details |
| `github_get_file` | Read file from repository |

## Running the Solution

```bash
# With real GitHub API (requires GITHUB_TOKEN)
python solution.py

# With mock tools (no API calls - for testing)
python solution.py --mock
```

## Example Usage

```python
from github_tools import create_github_pr_agent

agent = create_github_pr_agent()

# List open PRs
response = agent("List open PRs in owner/repo")

# Create complete PR workflow
response = agent("""
Create a PR for an OSS Risk Mitigation Plan update:
- Repository: acme-corp/oss-policies
- Component: log4j
- Risk Level: LOW (patched)
- Create branch 'rmp/log4j-update'
- Commit RMP file to 'docs/rmp/log4j.md'
- Create PR with summary
""")
```

## Integration with OSS Risk Mitigation System

This agent is designed to work as part of a larger system:

```
Jenkins Pipeline
    │
    ├── Extract SBOM from firmware
    ├── Compare with previous analysis
    ├── Run AI analysis (risk assessment)
    │
    └── GitHub PR Agent ← This kata
        ├── Create branch
        ├── Commit RMP files
        └── Create PR for review
```

## Running Tests

```bash
# Run all unit tests
pytest test_github_tools.py -v

# Run with coverage
pytest test_github_tools.py -v --cov=github_tools

# Run integration tests (requires GITHUB_TOKEN)
pytest test_github_tools.py -v -m integration
```

## Error Handling

The tools handle common GitHub API errors:

| Status | Meaning | Handling |
|--------|---------|----------|
| 401 | Invalid token | Clear error message |
| 403 | Permission denied / Rate limited | Suggest checking scopes |
| 404 | Not found | Indicate what's missing |
| 422 | Validation error | Handle duplicate PRs |

## Key Patterns

### Tool Definition
```python
@tool
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
        body: PR description (markdown supported).
        head_branch: Branch containing changes.
        base_branch: Branch to merge into.
    """
    try:
        # Implementation
        ...
    except GithubException as e:
        # Error handling
        ...
```

### Agent Creation
```python
agent = Agent(
    model=model,
    tools=[tool1, tool2, tool3],
    system_prompt="Describe the agent's purpose and capabilities"
)
```

## Success Criteria

You've completed this kata when:

- [ ] All 6 GitHub tools are implemented
- [ ] Tools handle errors gracefully
- [ ] Agent can orchestrate a complete PR workflow
- [ ] Unit tests pass

## Next Steps

After completing this kata:

1. Integrate with OSS analysis tools (SBOM parsing, vulnerability scanning)
2. Add tools for PR comments and reviews
3. Connect to Jenkins pipeline for automation
4. Add Confluence integration for documentation
