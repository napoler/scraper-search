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
            "wait": 2,  # Wait for JavaScript execution
            "timeout": timeout,
            "resource_timeout": 10,
            "proxy": splash_proxy,  # Optional proxy for Splash itself
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
    # Use Splash if requested
    if use_splash:
        if splash_url is None:
            splash_url = os.getenv("SPLASH_URL", "http://127.0.0.1:8050")
        return fetch_with_splash(url, splash_url)

    # Fall back to regular HTTP request
    if max_retries is None:
        max_retries = int(os.getenv("MAX_RETRIES", "3"))

    delay_min = float(os.getenv("REQUEST_DELAY_MIN", "1"))
    delay_max = float(os.getenv("REQUEST_DELAY_MAX", "3"))
    timeout = int(os.getenv("REQUEST_TIMEOUT", "10"))

    # Merge environment proxies with provided proxies
    env_proxies = get_proxy_dict()
    if proxies and env_proxies:
        # Combine both, with explicit proxies taking precedence
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
            # Random delay between requests
            time.sleep(random.uniform(delay_min, delay_max))

            response = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)

            if response.status_code == 200:
                # Auto-detect encoding
                if response.encoding is None or response.encoding == "ISO-8859-1":
                    response.encoding = response.apparent_encoding
                return response.text, response
            else:
                print(f"Status code: {response.status_code}")
        except Exception as e:
            print(f"Request error: {e}")

    return None, None
