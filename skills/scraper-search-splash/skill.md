---
name: scraper-search-splash
description: 通过 Splash 渲染执行搜索并整理资料 - 使用 scraper-search CLI 工具，支持 Splash JS 渲染、代理配置，用于获取搜索结果正文内容。
version: 1.0.0
tags:
  - search
  - scraping
  - splash
  - content-extraction
  - research
---

# Scraper Search Splash Skill

## When to Activate

当以下任一条件满足时激活：

- 用户需要**搜索并整理**多个来源的资料
- 用户需要获取搜索结果的**详细内容**（不只是摘要）
- 用户提到"调研"、"资料收集"、"多来源"、"搜索结果详情"
- 用户需要抓取需要 JavaScript 渲染的页面内容
- 上下文包含 search、scrape、research、survey、collect、Splash 等关键词

## Installation

```bash
cd /mnt/data/dev/scraper-search
pip install -e .
```

## Core Components

### 1. CLI Entry Point (cli.py)

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI entry point for scraper-search
"""

import os
import sys
import json
from pathlib import Path

import click
from dotenv import load_dotenv

from scraper_search.search import SearchEngine
from scraper_search.fetcher import fetch_html
from scraper_search.readability import ContentExtractor
from scraper_search.formatter import OutputFormatter

# Load .env file
load_dotenv()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """scraper-search: Search and extract web content to markdown"""
    pass


@main.command()
@click.option("-q", "--query", required=True, help="Search query")
@click.option("-n", "--num", default=5, help="Number of results to fetch")
@click.option("-o", "--output", type=click.Path(), help="Output file (default: stdout)")
@click.option("-f", "--format", "output_format", type=click.Choice(["json", "markdown"]), default="markdown", help="Output format")
@click.option("--no-save-content", is_flag=True, help="Skip fetching full content")
@click.option("--no-splash", "use_splash", is_flag=True, flag_value=False, default=True, help="Disable Splash JavaScript renderer (default: enabled)")
@click.option("--splash-url", default=None, help="Splash server URL")
@click.option("--proxy", "proxy_url", default=None, help="Proxy URL (http/https/socks)")
def search(query, num, output, output_format, no_save_content, use_splash, splash_url, proxy_url):
    """Search and extract content from web pages"""
    click.echo(f"🔍 Searching for: {query}")

    # Initialize components
    extractor = ContentExtractor()
    formatter = OutputFormatter(format_type=output_format)

    try:
        # Perform search
        search_engine = SearchEngine()
        results, status = search_engine.search(query, num_results=num)

        if status != 200:
            click.echo(f"❌ Search failed with status: {status}", err=True)
            sys.exit(1)

        links = results.links()
        click.echo(f"📋 Found {len(links)} links")

        # Prepare proxies dict if proxy URL provided
        proxies = None
        if proxy_url:
            proxies = {"http": proxy_url, "https": proxy_url}

        # Process each link
        processed_results = []
        for i, link in enumerate(links, 1):
            click.echo(f"  [{i}/{len(links)}] Fetching: {link}")

            html, response = fetch_html(link, proxies=proxies, use_splash=use_splash, splash_url=splash_url)
            if not html:
                click.echo(f"    ⚠️  Failed to fetch")
                continue

            # Extract title and content
            title = extractor.extract_title(html)
            content = extractor.extract_content(html)

            result_item = {
                "title": title,
                "url": link,
                "content": content,
                "status": response.status_code if response else None,
            }
            processed_results.append(result_item)

            # Show preview
            preview = content[:200].replace("\n", " ") if content else "No content"
            click.echo(f"    ✅ {title[:60]}...")
            click.echo(f"       {preview}...")

        # Output results
        if output:
            output_path = Path(output)
            output_path.write_text(formatter.format_results(processed_results), encoding="utf-8")
            click.echo(f"\n💾 Results saved to: {output}")
        else:
            click.echo("\n" + formatter.format_results(processed_results))

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("url")
@click.option("-o", "--output", type=click.Path(), help="Output file")
@click.option("-f", "--format", "output_format", type=click.Choice(["json", "markdown"]), default="markdown")
@click.option("--no-splash", "use_splash", is_flag=True, flag_value=False, default=True, help="Disable Splash JavaScript renderer (default: enabled)")
@click.option("--splash-url", default=None, help="Splash server URL")
@click.option("--proxy", "proxy_url", default=None, help="Proxy URL (http/https/socks)")
def fetch(url, output, output_format, use_splash, splash_url, proxy_url):
    """Fetch and extract content from a single URL"""
    click.echo(f"📥 Fetching: {url}")

    # Prepare proxies dict if proxy URL provided
    proxies = None
    if proxy_url:
        proxies = {"http": proxy_url, "https": proxy_url}

    try:
        html, response = fetch_html(url, proxies=proxies, use_splash=use_splash, splash_url=splash_url)
        if not html:
            click.echo("❌ Failed to fetch content", err=True)
            sys.exit(1)

        extractor = ContentExtractor()
        title = extractor.extract_title(html)
        content = extractor.extract_content(html)
        formatter = OutputFormatter(format_type=output_format)

        result = {
            "title": title,
            "url": url,
            "content": content,
            "status": response.status_code if response else None,
        }

        if output:
            Path(output).write_text(formatter.format_single(result), encoding="utf-8")
            click.echo(f"💾 Saved to: {output}")
        else:
            click.echo(formatter.format_single(result))

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### 2. Fetcher with Splash Support (fetcher.py)

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP fetcher with retry logic, user-agent rotation, proxy support and Splash rendering
"""

import os
import random
import time
from typing import Optional, Tuple, Dict, Any

import requests


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]


def get_proxy_dict() -> Optional[Dict[str, str]]:
    """
    Get proxy configuration from environment variables.
    Supports HTTP, HTTPS, and SOCKS proxies.

    Returns:
        Proxy dict for requests library, or None if no proxy configured
    """
    http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
    https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy") or os.getenv("HTTP_PROXY")
    socks_proxy = os.getenv("SOCKS_PROXY") or os.getenv("socks_proxy")

    proxies: Dict[str, str] = {}
    if http_proxy:
        proxies["http"] = http_proxy
    if https_proxy:
        proxies["https"] = https_proxy
    if socks_proxy:
        proxies["http"] = socks_proxy
        proxies["https"] = socks_proxy

    return proxies if proxies else None


class SplashResponse:
    """Mock response object for Splash rendering"""
    status_code: int = 200

    def __repr__(self) -> str:
        return f"<SplashResponse status_code={self.status_code}>"


def fetch_with_splash(url: str, splash_url: str, timeout: int = 30) -> Tuple[Optional[str], Optional[SplashResponse]]:
    """
    Fetch HTML content using Splash JavaScript renderer.

    Args:
        url: Target URL to render
        splash_url: Splash server URL
        timeout: Request timeout in seconds

    Returns:
        Tuple of (html_content, SplashResponse) or (None, None) on failure
    """
    render_endpoint = f"{splash_url}/render.json"

    try:
        splash_proxy: Optional[str] = os.getenv("SPLASH_PROXY")
        payload: Dict[str, Any] = {
            "url": url,
            "wait": 2,
            "timeout": timeout,
            "resource_timeout": 10,
            "proxy": splash_proxy,
        }
        response = requests.post(render_endpoint, json=payload, timeout=timeout + 5)

        if response.status_code == 200:
            data = response.json()
            if "html" in data:
                return data["html"], SplashResponse()
            elif "info" in data and "error" in data["info"]:
                print(f"Splash error: {data['info']['error']}")
        else:
            print(f"Splash request failed with status: {response.status_code}")

    except Exception as e:
        print(f"Splash rendering error: {e}")

    return None, None


def fetch_html(
    url: str,
    proxies: Optional[Dict[str, str]] = None,
    max_retries: Optional[int] = None,
    use_splash: bool = False,
    splash_url: Optional[str] = None
) -> Tuple[Optional[str], Optional[Any]]:
    """
    Fetch HTML content from a URL with retry logic.

    Args:
        url: Target URL
        proxies: Proxy configuration dict (optional)
        max_retries: Maximum retry attempts (default from env MAX_RETRIES=3)
        use_splash: Whether to use Splash for JavaScript rendering
        splash_url: Splash server URL (default: http://127.0.0.1:8050)

    Returns:
        Tuple of (html_content, response_object) or (None, None) on failure
    """
    if use_splash:
        if splash_url is None:
            splash_url = os.getenv("SPLASH_URL", "http://127.0.0.1:8050")
        return fetch_with_splash(url, splash_url)

    if max_retries is None:
        max_retries = int(os.getenv("MAX_RETRIES", "3"))

    delay_min = float(os.getenv("REQUEST_DELAY_MIN", "1"))
    delay_max = float(os.getenv("REQUEST_DELAY_MAX", "3"))
    timeout = int(os.getenv("REQUEST_TIMEOUT", "10"))

    env_proxies = get_proxy_dict()
    if proxies and env_proxies:
        merged = env_proxies.copy()
        merged.update(proxies)
        proxies = merged
    elif env_proxies:
        proxies = env_proxies

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    for _ in range(max_retries):
        try:
            time.sleep(random.uniform(delay_min, delay_max))
            response = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)

            if response.status_code == 200:
                if response.encoding is None or response.encoding == "ISO-8859-1":
                    response.encoding = response.apparent_encoding
                return response.text, response
            else:
                print(f"Status code: {response.status_code}")
        except Exception as e:
            print(f"Request error: {e}")

    return None, None
```

### 3. Search Engine (search.py)

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Search engine integration
"""

from search_engines_kit import Bing


class SearchEngine:
    """Wrapper for search engine operations"""

    def __init__(self, engine: str = "bing"):
        self.engine_name = engine
        self.engine = Bing()

    def search(self, query: str, num_results: int = 10) -> tuple:
        """
        Perform a search query

        Args:
            query: Search query string
            num_results: Number of results to return

        Returns:
            Tuple of (results, status_code)
        """
        return self.engine.search(query, num_results)
```

### 4. Content Extractor (readability.py)

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Content extraction using readability-lxml and html2text
"""

from readability import Document
import html2text
from bs4 import BeautifulSoup


class ContentExtractor:
    """Extract readable content from HTML"""

    def __init__(self):
        self.text_maker = html2text.HTML2Text()
        self.text_maker.ignore_links = True
        self.text_maker.bypass_tables = True
        self.text_maker.ignore_images = True
        self.text_maker.images_to_alt = True
        self.text_maker.google_doc = True
        self.text_maker.single_line_break = False
        self.text_maker.ignore_emphasis = True
        self.text_maker.body_width = False

    def extract_title(self, html: str) -> str:
        """Extract page title from HTML"""
        soup = BeautifulSoup(html, "html.parser")
        return soup.title.string if soup.title and soup.title.string else "No title"

    def extract_content(self, html: str) -> str:
        """
        Extract readable content from HTML and convert to markdown

        Args:
            html: Raw HTML content

        Returns:
            Markdown-formatted text content
        """
        try:
            doc = Document(html)
            clean_html = doc.summary(True)
            text = self.text_maker.handle(clean_html)
            return text.strip()
        except Exception as e:
            print(f"Content extraction error: {e}")
            return ""

    def extract_raw_text(self, html: str) -> str:
        """Extract raw text without markdown formatting"""
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator="\n", strip=True)
```

### 5. Output Formatter (formatter.py)

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Output formatters for different formats
"""

import json
from typing import List, Dict


class OutputFormatter:
    """Format search results for output"""

    def __init__(self, format_type: str = "markdown"):
        self.format_type = format_type

    def format_results(self, results: List[Dict]) -> str:
        """Format multiple search results"""
        if self.format_type == "json":
            return self._format_json(results)
        return self._format_markdown(results)

    def format_single(self, result: Dict) -> str:
        """Format a single result"""
        if self.format_type == "json":
            return json.dumps(result, ensure_ascii=False, indent=2)
        return self._format_markdown_single(result)

    def _format_json(self, results: List[Dict]) -> str:
        return json.dumps(results, ensure_ascii=False, indent=2)

    def _format_markdown(self, results: List[Dict]) -> str:
        """Format results as markdown"""
        output = []
        for i, item in enumerate(results, 1):
            output.append(self._format_markdown_single(item, index=i))
        return "\n\n".join(output)

    def _format_markdown_single(self, item: Dict, index: int = None) -> str:
        """Format a single item as markdown"""
        lines = []
        if index is not None:
            lines.append(f"## [{index}] {item.get('title', 'No title')}")
        else:
            lines.append(f"## {item.get('title', 'No title')}")

        lines.append(f"**URL**: {item.get('url', 'N/A')}")

        if item.get("status"):
            lines.append(f"**Status**: {item.get('status')}")

        lines.append("")
        lines.append("### Content")
        lines.append("")
        lines.append(item.get("content", "No content available"))

        return "\n".join(lines)
```

## Usage

### Search Command (Default: Splash Enabled)

```bash
scraper-search search -q "关键词" -n 5
```

### Fetch Single URL

```bash
scraper-search fetch "https://example.com/article"
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-q, --query` | Search query | Required |
| `-n, --num` | Number of results | 5 |
| `-o, --output` | Output file path | stdout |
| `-f, --format` | Output format (json/markdown) | markdown |
| `--no-splash` | Disable Splash rendering | Enabled by default |
| `--splash-url` | Splash server URL | http://127.0.0.1:8050 |
| `--proxy` | Proxy URL (http/https/socks) | None |

### Environment Variables

```bash
# Splash
SPLASH_URL=http://127.0.0.1:8050
SPLASH_PROXY=http://your-proxy:8080

# Proxy
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
SOCKS_PROXY=socks5://127.0.0.1:7891

# Request
MAX_RETRIES=3
REQUEST_DELAY_MIN=1
REQUEST_DELAY_MAX=3
REQUEST_TIMEOUT=10
```

## Fallback Strategy

```
Splash (default) → HTTP fallback (--no-splash)
     ↓                  ↓
  Failure          Try proxy
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Splash connection failed | Splash not running | Start Splash or use --no-splash |
| 403 Forbidden | Anti-bot detection | Try proxy or --no-splash |
| Timeout | Slow network/large page | Increase REQUEST_TIMEOUT |
| Parse failed | Unusual page structure | Manual inspection needed |

## Limitations

1. **Legal compliance**: Use only for lawful purposes, respect website ToS
2. **Splash service**: Requires local Splash running (Docker or source)
3. **Proxy limits**: Proxy services may have rate/traffic limits
4. **Anti-bot**: Frequent requests may trigger restrictions
5. **Copyright**: Collected content for personal research only

---

**Created**: 2026-04-01
