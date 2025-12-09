"""
Kata 03b: Browser Automation Tools - Starter Template

Complete the TODOs to create browser automation tools for your agent.

Prerequisites:
    pip install 'strands-agents[anthropic]' playwright
    playwright install chromium
    export ANTHROPIC_API_KEY="your-key-here"
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from strands import Agent, tool
from strands.models.anthropic import AnthropicModel
# TODO 1: Import Playwright
# from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

load_dotenv()

# Create screenshots directory
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)


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
    def header(cls, text):
        return f"{cls.BOLD}{cls.HEADER}{text}{cls.RESET}"

    @classmethod
    def prompt(cls, text):
        return f"{cls.PROMPT}{text}{cls.RESET}"

    @classmethod
    def response(cls, text):
        return f"{cls.RESPONSE}{text}{cls.RESET}"

    @classmethod
    def stats(cls, text):
        return f"{cls.STATS}{text}{cls.RESET}"

    @classmethod
    def todo(cls, text):
        return f"{cls.TODO}{text}{cls.RESET}"


# ==============================================================================
# Browser Tools
# ==============================================================================

@tool
def take_screenshot(url: str, filename: str = "screenshot.png", full_page: bool = True) -> str:
    """Take a screenshot of a webpage.

    Args:
        url: The URL to screenshot.
        filename: Output filename (saved in screenshots/ directory).
        full_page: If True, capture the full scrollable page.
    """
    # TODO 2: Implement screenshot functionality
    # Steps:
    #   1. Validate URL starts with http:// or https://
    #   2. Launch headless browser: p.chromium.launch(headless=True)
    #   3. Create new page with viewport size
    #   4. Navigate to URL: page.goto(url, wait_until="networkidle")
    #   5. Take screenshot: page.screenshot(path=filepath, full_page=full_page)
    #   6. Close browser
    #   7. Return success message with filepath

    return "TODO: Implement take_screenshot"


@tool
def get_page_content(url: str, wait_for_js: bool = True) -> str:
    """Get the rendered content of a webpage, including JavaScript-rendered content.

    Args:
        url: The URL to fetch content from.
        wait_for_js: If True, wait for JavaScript to finish rendering.
    """
    # TODO 3: Implement content extraction
    # Steps:
    #   1. Launch headless browser
    #   2. Navigate with appropriate wait_until ("networkidle" for JS, "domcontentloaded" otherwise)
    #   3. Get title: page.title()
    #   4. Get text content: page.inner_text("body")
    #   5. Clean up whitespace and truncate if needed
    #   6. Return formatted result

    return "TODO: Implement get_page_content"


@tool
def extract_links(url: str) -> str:
    """Extract all links from a webpage.

    Args:
        url: The URL to extract links from.
    """
    # TODO 4: Implement link extraction
    # Steps:
    #   1. Launch browser and navigate to URL
    #   2. Use page.eval_on_selector_all() to extract links:
    #      page.eval_on_selector_all(
    #          "a[href]",
    #          "elements => elements.map(e => ({text: e.innerText.trim(), href: e.href}))"
    #      )
    #   3. Format and return results

    return "TODO: Implement extract_links"


@tool
def extract_headings(url: str) -> str:
    """Extract all headings (h1-h6) from a webpage.

    Args:
        url: The URL to extract headings from.
    """
    # TODO 5: Implement heading extraction
    # Similar to extract_links but select "h1, h2, h3, h4, h5, h6"

    return "TODO: Implement extract_headings"


@tool
def get_page_metadata(url: str) -> str:
    """Get metadata from a webpage (title, description, keywords, etc.).

    Args:
        url: The URL to get metadata from.
    """
    # TODO 6: Implement metadata extraction
    # Extract:
    #   - title: page.title()
    #   - meta description: meta[name='description']
    #   - meta keywords: meta[name='keywords']
    #   - og:title, og:description

    return "TODO: Implement get_page_metadata"


@tool
def check_page_status(url: str) -> str:
    """Check if a webpage is accessible and get its status.

    Args:
        url: The URL to check.
    """
    # TODO 7: Implement status check
    # Steps:
    #   1. Navigate and capture response: response = page.goto(url)
    #   2. Check response.status and response.ok
    #   3. Optionally get load timing from performance API

    return "TODO: Implement check_page_status"


# ==============================================================================
# Agent Creation
# ==============================================================================

def create_browser_agent():
    """Create a Strands agent with browser automation tools."""
    model = AnthropicModel(
        model_id="claude-sonnet-4-20250514",
        max_tokens=1024
    )

    agent = Agent(
        model=model,
        tools=[
            take_screenshot,
            get_page_content,
            extract_links,
            extract_headings,
            get_page_metadata,
            check_page_status,
        ],
        system_prompt="""You are a web research assistant with browser automation capabilities.

You can:
- Take screenshots of web pages
- Extract content from JavaScript-rendered pages
- Get links and headings from pages
- Check page metadata and status

Use these tools to help users research and gather information from the web.
When using tool results, summarize the key findings clearly."""
    )

    return agent


# ==============================================================================
# Main Demo
# ==============================================================================

def main():
    """Run all the demos."""
    print(Colors.header("=" * 70))
    print(Colors.header(" Kata 03b: Browser Automation Tools"))
    print(Colors.header("=" * 70))

    # Create the browser agent
    agent = create_browser_agent()

    # Test queries
    test_queries = [
        ("1. Page Status Check", "Check if https://example.com is accessible"),
        ("2. Extract Metadata", "Get the metadata from https://example.com"),
        ("3. Extract Headings", "What are the main headings on https://example.com?"),
        ("4. Take Screenshot", "Take a screenshot of https://example.com"),
    ]

    for title, query in test_queries:
        print(Colors.header(f"\n{title}"))
        print("-" * 40)
        print(Colors.prompt(f"User: {query}"))
        try:
            response = agent(query)
            if "TODO" in str(response):
                print(Colors.todo(f"Agent: {response}"))
            else:
                print(Colors.response(f"Agent: {response}"))
        except Exception as e:
            print(f"Error: {e}")

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 03b Complete!"))
    print(Colors.header("=" * 70))
    print(Colors.stats(f"\nScreenshots directory: {SCREENSHOTS_DIR}"))


if __name__ == "__main__":
    main()
