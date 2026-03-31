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
