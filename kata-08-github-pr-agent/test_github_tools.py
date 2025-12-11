"""
Unit tests for GitHub PR Tools

Run with: pytest test_github_tools.py -v

These tests use mocking to avoid actual GitHub API calls.
For integration tests against real GitHub, use a test repository.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestGetGitHubClient:
    """Tests for get_github_client function."""

    def test_missing_token_raises_error(self):
        """Test that missing token raises clear error."""
        with patch.dict(os.environ, {'GITHUB_TOKEN': ''}, clear=False):
            # Need to reimport to pick up new env
            import github_tools
            github_tools._github_client = None
            github_tools.GITHUB_TOKEN = ''

            with pytest.raises(ValueError) as excinfo:
                github_tools.get_github_client()
            assert "GITHUB_TOKEN" in str(excinfo.value)

    @patch('github_tools.Github')
    def test_client_created_with_token(self, mock_github_class):
        """Test that client is created when token is present."""
        import github_tools
        github_tools._github_client = None
        github_tools.GITHUB_TOKEN = 'test-token'
        github_tools.GITHUB_BASE_URL = 'https://api.github.com'

        client = github_tools.get_github_client()

        mock_github_class.assert_called_once_with(login_or_token='test-token')


class TestGitHubCreateBranch:
    """Tests for github_create_branch tool."""

    @patch('github_tools.get_github_client')
    def test_create_branch_success(self, mock_get_client):
        """Test successful branch creation."""
        from github_tools import github_create_branch

        # Setup mock
        mock_repo = Mock()
        mock_ref = Mock()
        mock_ref.object.sha = "abc123456789"
        mock_repo.get_git_ref.return_value = mock_ref

        mock_client = Mock()
        mock_client.get_repo.return_value = mock_repo
        mock_get_client.return_value = mock_client

        # Call the tool
        result = github_create_branch("owner/repo", "new-branch", "main")

        # Assertions
        assert "successfully" in result.lower()
        assert "new-branch" in result
        mock_repo.create_git_ref.assert_called_once()

    @patch('github_tools.get_github_client')
    def test_create_branch_already_exists(self, mock_get_client):
        """Test handling of duplicate branch error."""
        from github import GithubException
        from github_tools import github_create_branch

        mock_repo = Mock()
        mock_ref = Mock()
        mock_ref.object.sha = "abc123"
        mock_repo.get_git_ref.return_value = mock_ref
        mock_repo.create_git_ref.side_effect = GithubException(
            422, {"message": "Reference already exists"}
        )

        mock_client = Mock()
        mock_client.get_repo.return_value = mock_repo
        mock_get_client.return_value = mock_client

        result = github_create_branch("owner/repo", "existing-branch")

        assert "already exist" in result.lower() or "error" in result.lower()


class TestGitHubCommitFile:
    """Tests for github_commit_file tool."""

    @patch('github_tools.get_github_client')
    def test_commit_new_file_success(self, mock_get_client):
        """Test creating a new file."""
        from github import GithubException
        from github_tools import github_commit_file

        mock_repo = Mock()
        # File doesn't exist
        mock_repo.get_contents.side_effect = GithubException(404, {})
        mock_repo.create_file.return_value = {
            "commit": Mock(sha="def456789")
        }

        mock_client = Mock()
        mock_client.get_repo.return_value = mock_repo
        mock_get_client.return_value = mock_client

        result = github_commit_file(
            "owner/repo",
            "docs/test.md",
            "# Test content",
            "Add test file",
            "feature-branch"
        )

        assert "created" in result.lower()
        mock_repo.create_file.assert_called_once()

    @patch('github_tools.get_github_client')
    def test_update_existing_file_success(self, mock_get_client):
        """Test updating an existing file."""
        from github_tools import github_commit_file

        mock_repo = Mock()
        mock_existing = Mock()
        mock_existing.sha = "old-sha-123"
        mock_repo.get_contents.return_value = mock_existing
        mock_repo.update_file.return_value = {
            "commit": Mock(sha="new-sha-456")
        }

        mock_client = Mock()
        mock_client.get_repo.return_value = mock_repo
        mock_get_client.return_value = mock_client

        result = github_commit_file(
            "owner/repo",
            "docs/existing.md",
            "# Updated content",
            "Update file",
            "main"
        )

        assert "updated" in result.lower()
        mock_repo.update_file.assert_called_once()


class TestGitHubCreatePR:
    """Tests for github_create_pr tool."""

    @patch('github_tools.get_github_client')
    def test_create_pr_success(self, mock_get_client):
        """Test successful PR creation."""
        from github_tools import github_create_pr

        mock_pr = Mock()
        mock_pr.number = 42
        mock_pr.title = "Test PR"
        mock_pr.html_url = "https://github.com/owner/repo/pull/42"
        mock_pr.state = "open"

        mock_repo = Mock()
        mock_repo.create_pull.return_value = mock_pr

        mock_client = Mock()
        mock_client.get_repo.return_value = mock_repo
        mock_get_client.return_value = mock_client

        result = github_create_pr(
            "owner/repo",
            "Test PR",
            "Description",
            "feature-branch"
        )

        assert "successfully" in result.lower()
        assert "#42" in result
        assert "https://github.com" in result

    @patch('github_tools.get_github_client')
    def test_create_pr_duplicate(self, mock_get_client):
        """Test handling of duplicate PR error."""
        from github import GithubException
        from github_tools import github_create_pr

        mock_repo = Mock()
        mock_repo.create_pull.side_effect = GithubException(
            422, {"message": "A pull request already exists"}
        )

        mock_client = Mock()
        mock_client.get_repo.return_value = mock_repo
        mock_get_client.return_value = mock_client

        result = github_create_pr(
            "owner/repo",
            "Test PR",
            "Description",
            "existing-branch"
        )

        assert "already exist" in result.lower()


class TestGitHubListPRs:
    """Tests for github_list_prs tool."""

    @patch('github_tools.get_github_client')
    def test_list_prs_success(self, mock_get_client):
        """Test listing PRs."""
        from github_tools import github_list_prs

        mock_pr1 = Mock()
        mock_pr1.number = 1
        mock_pr1.title = "First PR"
        mock_pr1.state = "open"
        mock_pr1.head.ref = "feature-1"
        mock_pr1.base.ref = "main"
        mock_pr1.created_at = Mock()
        mock_pr1.created_at.strftime.return_value = "2024-01-15"
        mock_pr1.html_url = "https://github.com/owner/repo/pull/1"

        mock_repo = Mock()
        mock_repo.get_pulls.return_value = [mock_pr1]

        mock_client = Mock()
        mock_client.get_repo.return_value = mock_repo
        mock_get_client.return_value = mock_client

        result = github_list_prs("owner/repo")

        assert "#1" in result
        assert "First PR" in result

    @patch('github_tools.get_github_client')
    def test_list_prs_empty(self, mock_get_client):
        """Test listing PRs when none exist."""
        from github_tools import github_list_prs

        mock_repo = Mock()
        mock_repo.get_pulls.return_value = []

        mock_client = Mock()
        mock_client.get_repo.return_value = mock_repo
        mock_get_client.return_value = mock_client

        result = github_list_prs("owner/repo")

        assert "no" in result.lower() or "not found" in result.lower()


class TestGitHubGetPR:
    """Tests for github_get_pr tool."""

    @patch('github_tools.get_github_client')
    def test_get_pr_success(self, mock_get_client):
        """Test getting PR details."""
        from github_tools import github_get_pr

        mock_pr = Mock()
        mock_pr.number = 42
        mock_pr.title = "Test PR"
        mock_pr.state = "open"
        mock_pr.mergeable = True
        mock_pr.head.ref = "feature-branch"
        mock_pr.base.ref = "main"
        mock_pr.user.login = "testuser"
        mock_pr.created_at = Mock()
        mock_pr.created_at.strftime.return_value = "2024-01-15 10:00"
        mock_pr.updated_at = Mock()
        mock_pr.updated_at.strftime.return_value = "2024-01-15 12:00"
        mock_pr.html_url = "https://github.com/owner/repo/pull/42"
        mock_pr.body = "PR Description"
        mock_pr.get_reviews.return_value = []

        mock_repo = Mock()
        mock_repo.get_pull.return_value = mock_pr

        mock_client = Mock()
        mock_client.get_repo.return_value = mock_repo
        mock_get_client.return_value = mock_client

        result = github_get_pr("owner/repo", 42)

        assert "#42" in result
        assert "Test PR" in result
        assert "testuser" in result


class TestGitHubGetFile:
    """Tests for github_get_file tool."""

    @patch('github_tools.get_github_client')
    def test_get_file_success(self, mock_get_client):
        """Test getting file contents."""
        import base64
        from github_tools import github_get_file

        content = "# Test File\nThis is content."
        mock_file = Mock()
        mock_file.content = base64.b64encode(content.encode()).decode()
        mock_file.encoding = "base64"
        mock_file.size = len(content)
        mock_file.sha = "abc123456"

        mock_repo = Mock()
        mock_repo.get_contents.return_value = mock_file

        mock_client = Mock()
        mock_client.get_repo.return_value = mock_repo
        mock_get_client.return_value = mock_client

        result = github_get_file("owner/repo", "docs/test.md")

        assert "Test File" in result
        assert "This is content" in result

    @patch('github_tools.get_github_client')
    def test_get_file_not_found(self, mock_get_client):
        """Test handling of file not found."""
        from github import GithubException
        from github_tools import github_get_file

        mock_repo = Mock()
        mock_repo.get_contents.side_effect = GithubException(404, {})

        mock_client = Mock()
        mock_client.get_repo.return_value = mock_repo
        mock_get_client.return_value = mock_client

        result = github_get_file("owner/repo", "nonexistent.md")

        assert "not found" in result.lower()


class TestCreateGitHubPRAgent:
    """Tests for agent factory function."""

    @patch('github_tools.AnthropicModel')
    @patch('github_tools.Agent')
    def test_create_agent_with_tools(self, mock_agent_class, mock_model_class):
        """Test agent creation with all tools."""
        from github_tools import create_github_pr_agent

        mock_model = Mock()
        mock_model_class.return_value = mock_model

        agent = create_github_pr_agent()

        # Verify model was created
        mock_model_class.assert_called_once()

        # Verify agent was created with tools
        mock_agent_class.assert_called_once()
        call_kwargs = mock_agent_class.call_args[1]
        assert 'tools' in call_kwargs
        assert len(call_kwargs['tools']) == 6  # All 6 tools
        assert 'system_prompt' in call_kwargs


# ==============================================================================
# Integration Tests (require real GitHub access)
# ==============================================================================

@pytest.mark.integration
class TestGitHubIntegration:
    """
    Integration tests against real GitHub.

    Run with: pytest test_github_tools.py -v -m integration

    Requires:
    - GITHUB_TOKEN environment variable
    - A test repository with write access
    """

    TEST_REPO = os.getenv("TEST_GITHUB_REPO", "your-org/test-repo")

    @pytest.fixture(autouse=True)
    def skip_without_token(self):
        """Skip integration tests if no token is configured."""
        if not os.getenv("GITHUB_TOKEN"):
            pytest.skip("GITHUB_TOKEN not configured")

    def test_list_prs_real(self):
        """Test listing PRs against real GitHub."""
        from github_tools import github_list_prs

        result = github_list_prs(self.TEST_REPO, state="all", max_results=5)

        # Should return something (even if "no PRs found")
        assert result is not None
        assert len(result) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
