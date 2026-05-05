"""
Extract strands from parsed curriculum documents.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from mistletoe.block_token import Document, Heading

from curriculum_extractor.parser import MarkdownParser


@dataclass(frozen=True)
class StrandData:
    """Raw extracted strand data before transformation."""

    strand_id: str
    strand_name: str
    content_start_line: int | None
    content_end_line: int | None


class StrandExtractor:
    """Extract strand information from curriculum documents."""

    def __init__(self, parser: MarkdownParser | None = None):
        self.parser = parser or MarkdownParser()

    def extract_strands(self, document: Document) -> list[StrandData]:
        """Extract all strands from a parsed document in sequential order."""
        strands: list[StrandData] = []
        strand_headers = self._find_strand_headers(document)

        for i, (header, line_num) in enumerate(strand_headers):
            strand_id, strand_name = self._parse_strand_header(header)
            if strand_id and strand_name:
                content_end = (
                    strand_headers[i + 1][1] if i + 1 < len(strand_headers) else None
                )
                strands.append(
                    StrandData(
                        strand_id=strand_id,
                        strand_name=strand_name,
                        content_start_line=line_num,
                        content_end_line=content_end,
                    )
                )

        return strands

    def _find_strand_headers(self, document: Document) -> list[tuple[str, int | None]]:
        """Find all strand headers in the document."""
        headers: list[tuple[str, int | None]] = []

        # Check headings
        for node in self._walk_headings(document):
            text = self._get_heading_text(node)
            if self._is_strand_header(text):
                line_num = getattr(node, "line_number", None)
                headers.append((text, line_num))

        # Check paragraphs for bold strand text
        for node in self._walk_paragraphs(document):
            text = self._get_paragraph_text(node)
            if self._is_strand_header(text):
                line_num = getattr(node, "line_number", None)
                headers.append((text, line_num))

        # Sort by line number to maintain order
        headers.sort(key=lambda x: x[1] if x[1] is not None else float("inf"))
        return headers

    def _is_strand_header(self, text: str) -> bool:
        """Check if text matches strand header pattern."""
        # Strip markdown bold markers
        text = text.strip().strip("*").strip()
        pattern = r"^STRAND\s+\d+(\.\d+)?\s*:?"
        return bool(re.match(pattern, text, re.IGNORECASE))

    def _parse_strand_header(self, header: str) -> tuple[str, str]:
        """Parse strand ID and name from header text."""
        # Strip markdown bold markers
        header = header.strip().strip("*").strip()
        # Try with colon first
        match = re.match(
            r"^STRAND\s+(\d+(?:\.\d+)?)\s*:\s*(.+)$", header, re.IGNORECASE
        )
        if match:
            return match.group(1), match.group(2).strip()
        # Try without colon
        match = re.match(
            r"^STRAND\s+(\d+(?:\.\d+)?)\s+(.+)$", header, re.IGNORECASE
        )
        if match:
            return match.group(1), match.group(2).strip()
        return "", ""

    def _get_heading_text(self, node: Heading) -> str:
        """Extract text content from a heading node."""
        children = getattr(node, "children", None) or []
        parts = []
        for child in children:
            content = getattr(child, "content", None)
            if content:
                parts.append(str(content))
        return "".join(parts).strip()

    def _get_paragraph_text(self, node) -> str:
        """Extract text content from a paragraph node, including bold text."""
        from mistletoe.span_token import Strong

        children = getattr(node, "children", None) or []
        parts = []
        for child in children:
            # Check if it's a Strong (bold) token
            if isinstance(child, Strong):
                for subchild in getattr(child, "children", None) or []:
                    content = getattr(subchild, "content", None)
                    if content:
                        parts.append(str(content))
            else:
                content = getattr(child, "content", None)
                if content:
                    parts.append(str(content))
        return "".join(parts).strip()

    def _walk_headings(self, node: object):
        """Walk the document tree and yield all heading nodes."""
        if isinstance(node, Heading):
            yield node

        for child in getattr(node, "children", None) or []:
            yield from self._walk_headings(child)

    def _walk_paragraphs(self, node: object):
        """Walk the document tree and yield all paragraph nodes."""
        from mistletoe.block_token import Paragraph

        if isinstance(node, Paragraph):
            yield node

        for child in getattr(node, "children", None) or []:
            yield from self._walk_paragraphs(child)
