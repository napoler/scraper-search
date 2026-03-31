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
        self.text_maker.body_width = False  # Don't wrap text

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
