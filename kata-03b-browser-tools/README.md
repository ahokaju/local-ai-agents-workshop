# Kata 03b: Browser Automation Tools

## Overview

This kata extends agent capabilities with **browser automation** using Playwright. You'll learn to create tools that can:
- Navigate to web pages
- Take screenshots
- Extract structured data from pages
- Interact with dynamic content (click, fill forms)

## Prerequisites

```bash
# Install dependencies
pip install playwright httpx

# Install browser binaries (required once)
playwright install chromium
```

### Windows WSL Users

If you're running on Windows WSL with a virtual environment, you'll need to install additional system libraries for Chromium to work:

```bash
sudo apt update
sudo apt install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0t64 \
    libatk-bridge2.0-0t64 \
    libcups2t64 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2t64 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libgtk-3-0t64
```

**Symptom**: Error mentioning missing `libnspr4.so` or similar library errors when the agent tries to launch the browser.

## Learning Objectives

1. Understand when browser automation is needed vs simple HTTP requests
2. Create Playwright-based tools for Strands agents
3. Handle dynamic/JavaScript-rendered content
4. Implement screenshot capabilities
5. Extract structured data from web pages

## When to Use Browser Tools

| Use Case | HTTP (httpx) | Browser (Playwright) |
|----------|--------------|----------------------|
| Static HTML pages | ✅ Fast | Overkill |
| REST APIs | ✅ Best | Not needed |
| JavaScript-rendered content | ❌ Won't work | ✅ Required |
| Screenshots | ❌ Not possible | ✅ Yes |
| Form interactions | Limited | ✅ Full support |
| Login-protected pages | Complex | ✅ Easier |

## Exercises

### Exercise 1: Screenshot Tool
Create a tool that takes a screenshot of any URL and saves it locally.

### Exercise 2: Content Extraction
Extract specific elements from a page (headings, links, tables).

### Exercise 3: Dynamic Content
Handle pages that load content via JavaScript.

### Exercise 4: Form Interaction
Fill out and submit a form programmatically.

## Files

- `solution.py` - Complete implementation with all browser tools
- `starter.py` - Template with TODOs to complete
- `screenshots/` - Directory for saved screenshots (created automatically)

## Running the Solution

```bash
cd kata-03b-browser-tools

# Run all demos
python solution.py

# Test a custom URL
python solution.py https://www.vaisala.com
python solution.py https://strandsagents.com/latest/
```

When testing a custom URL, the agent will:
1. Check if the site is accessible
2. Extract metadata (title, description)
3. Extract main headings
4. Take a screenshot

## Key Concepts

### Playwright Basics

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://example.com")

    # Take screenshot
    page.screenshot(path="screenshot.png")

    # Extract content
    title = page.title()
    content = page.content()

    browser.close()
```

### As a Strands Tool

```python
@tool
def take_screenshot(url: str, filename: str = "screenshot.png") -> str:
    """Take a screenshot of a webpage."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        page.screenshot(path=filename, full_page=True)
        browser.close()
    return f"Screenshot saved to {filename}"
```

## Tips

- Always use `headless=True` for server/agent use
- Use `wait_until="networkidle"` for JavaScript-heavy pages
- Set reasonable timeouts to avoid hanging
- Clean up browser instances properly
- Consider screenshot size/quality for storage

## Estimated Time

45-60 minutes
