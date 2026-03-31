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
