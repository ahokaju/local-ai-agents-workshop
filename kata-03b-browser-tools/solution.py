"""
Kata 03b: Browser Automation Tools - Solution

This script demonstrates how to create browser automation tools using
Playwright and integrate them with Strands agents.

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
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

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
    if not url.startswith(("http://", "https://")):
        return "Error: URL must start with http:// or https://"

    filepath = SCREENSHOTS_DIR / filename

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 720})

            page.goto(url, wait_until="networkidle", timeout=30000)
            page.screenshot(path=str(filepath), full_page=full_page)

            browser.close()

        return f"Screenshot saved to {filepath}"

    except PlaywrightTimeout:
        return f"Error: Page load timed out for {url}"
    except Exception as e:
        return f"Error taking screenshot: {str(e)}"


@tool
def get_page_content(url: str, wait_for_js: bool = True) -> str:
    """Get the rendered content of a webpage, including JavaScript-rendered content.

    Args:
        url: The URL to fetch content from.
        wait_for_js: If True, wait for JavaScript to finish rendering.
    """
    if not url.startswith(("http://", "https://")):
        return "Error: URL must start with http:// or https://"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            wait_until = "networkidle" if wait_for_js else "domcontentloaded"
            page.goto(url, wait_until=wait_until, timeout=30000)

            # Get page title
            title = page.title()

            # Get text content
            content = page.inner_text("body")

            # Clean up whitespace
            content = " ".join(content.split())

            # Limit length
            if len(content) > 3000:
                content = content[:3000] + "... [truncated]"

            browser.close()

        return f"Title: {title}\n\nContent:\n{content}"

    except PlaywrightTimeout:
        return f"Error: Page load timed out for {url}"
    except Exception as e:
        return f"Error fetching page: {str(e)}"


@tool
def extract_links(url: str) -> str:
    """Extract all links from a webpage.

    Args:
        url: The URL to extract links from.
    """
    if not url.startswith(("http://", "https://")):
        return "Error: URL must start with http:// or https://"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Extract all links
            links = page.eval_on_selector_all(
                "a[href]",
                "elements => elements.map(e => ({text: e.innerText.trim(), href: e.href})).filter(l => l.href && l.text)"
            )

            browser.close()

        if not links:
            return f"No links found on {url}"

        # Format links (limit to first 20)
        links = links[:20]
        result = f"Links found on {url}:\n\n"
        for link in links:
            text = link["text"][:50] + "..." if len(link["text"]) > 50 else link["text"]
            result += f"- {text}: {link['href']}\n"

        if len(links) == 20:
            result += "\n... (showing first 20 links)"

        return result

    except Exception as e:
        return f"Error extracting links: {str(e)}"


@tool
def extract_headings(url: str) -> str:
    """Extract all headings (h1-h6) from a webpage.

    Args:
        url: The URL to extract headings from.
    """
    if not url.startswith(("http://", "https://")):
        return "Error: URL must start with http:// or https://"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Extract headings
            headings = page.eval_on_selector_all(
                "h1, h2, h3, h4, h5, h6",
                "elements => elements.map(e => ({level: e.tagName, text: e.innerText.trim()}))"
            )

            browser.close()

        if not headings:
            return f"No headings found on {url}"

        result = f"Headings on {url}:\n\n"
        for h in headings:
            result += f"[{h['level']}] {h['text']}\n"

        return result

    except Exception as e:
        return f"Error extracting headings: {str(e)}"


@tool
def get_page_metadata(url: str) -> str:
    """Get metadata from a webpage (title, description, keywords, etc.).

    Args:
        url: The URL to get metadata from.
    """
    if not url.startswith(("http://", "https://")):
        return "Error: URL must start with http:// or https://"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Extract metadata
            title = page.title()

            meta_desc = page.eval_on_selector(
                "meta[name='description']",
                "el => el ? el.content : null"
            ) if page.query_selector("meta[name='description']") else None

            meta_keywords = page.eval_on_selector(
                "meta[name='keywords']",
                "el => el ? el.content : null"
            ) if page.query_selector("meta[name='keywords']") else None

            og_title = page.eval_on_selector(
                "meta[property='og:title']",
                "el => el ? el.content : null"
            ) if page.query_selector("meta[property='og:title']") else None

            og_desc = page.eval_on_selector(
                "meta[property='og:description']",
                "el => el ? el.content : null"
            ) if page.query_selector("meta[property='og:description']") else None

            browser.close()

        result = f"Metadata for {url}:\n\n"
        result += f"Title: {title}\n"
        if meta_desc:
            result += f"Description: {meta_desc}\n"
        if meta_keywords:
            result += f"Keywords: {meta_keywords}\n"
        if og_title:
            result += f"OG Title: {og_title}\n"
        if og_desc:
            result += f"OG Description: {og_desc}\n"

        return result

    except Exception as e:
        return f"Error getting metadata: {str(e)}"


@tool
def check_page_status(url: str) -> str:
    """Check if a webpage is accessible and get its status.

    Args:
        url: The URL to check.
    """
    if not url.startswith(("http://", "https://")):
        return "Error: URL must start with http:// or https://"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            response = page.goto(url, timeout=30000)

            status = response.status if response else "Unknown"
            ok = response.ok if response else False

            # Get page load timing
            timing = page.evaluate("() => performance.timing.loadEventEnd - performance.timing.navigationStart")

            browser.close()

        status_text = "accessible" if ok else "not accessible"
        return f"URL: {url}\nStatus: {status} ({status_text})\nLoad time: {timing}ms"

    except PlaywrightTimeout:
        return f"URL: {url}\nStatus: Timeout - page took too long to load"
    except Exception as e:
        return f"URL: {url}\nStatus: Error - {str(e)}"


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
    print(Colors.header(" Kata 03b: Browser Automation Tools - Solution"))
    print(Colors.header("=" * 70))

    # Create the browser agent
    agent = create_browser_agent()

    # Test queries
    test_queries = [
        ("1. Page Status Check", "Check if https://example.com is accessible"),
        ("2. Extract Metadata", "Get the metadata from https://news.ycombinator.com"),
        ("3. Extract Headings", "What are the main headings on https://example.com?"),
        ("4. Take Screenshot", "Take a screenshot of https://example.com and save it as example.png"),
        ("5. JavaScript Content", "Get the content from https://quotes.toscrape.com/js/ (it uses JavaScript)"),
    ]

    for title, query in test_queries:
        print(Colors.header(f"\n{title}"))
        print("-" * 40)
        print(Colors.prompt(f"User: {query}"))
        try:
            response = agent(query)
            print(Colors.response(f"Agent: {response}"))
        except Exception as e:
            print(f"Error: {e}")

    # Demo multi-step research
    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Multi-step Web Research Demo"))
    print(Colors.header("=" * 70))

    research_query = """Research the Hacker News homepage:
    1. Check if it's accessible
    2. Get its metadata
    3. Extract the main headings
    Give me a summary of what this site is about."""

    print(Colors.prompt(f"\nUser: {research_query}"))
    response = agent(research_query)
    print(Colors.response(f"Agent: {response}"))

    print(Colors.header("\n" + "=" * 70))
    print(Colors.header(" Kata 03b Complete!"))
    print(Colors.header("=" * 70))
    print(Colors.stats(f"\nScreenshots saved to: {SCREENSHOTS_DIR}"))


def test_url(url: str):
    """Test browser tools with a custom URL."""
    print(Colors.header("=" * 70))
    print(Colors.header(f" Testing: {url}"))
    print(Colors.header("=" * 70))

    agent = create_browser_agent()

    queries = [
        f"Check if {url} is accessible and get its status",
        f"Get the metadata from {url}",
        f"What are the main headings on {url}?",
        f"Take a screenshot of {url}",
    ]

    for query in queries:
        print(Colors.prompt(f"\nUser: {query}"))
        try:
            response = agent(query)
            print(Colors.response(f"Agent: {response}"))
        except Exception as e:
            print(f"Error: {e}")

    print(Colors.stats(f"\nScreenshots saved to: {SCREENSHOTS_DIR}"))


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # Custom URL provided
        test_url(sys.argv[1])
    else:
        main()
