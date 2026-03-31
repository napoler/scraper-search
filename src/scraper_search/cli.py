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
