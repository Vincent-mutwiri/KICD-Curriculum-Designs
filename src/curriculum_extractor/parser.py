"""
Markdown parsing utilities for curriculum source documents.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import mistletoe
from mistletoe.block_token import Document, List, ListItem, Paragraph, Table, TableCell


@dataclass(frozen=True)
class MarkdownTable:
    """Extracted markdown table with positional cell data preserved."""

    headers: list[str]
    rows: list[list[str]]
    alignments: list[str | None]
    line_number: int | None = None


@dataclass(frozen=True)
class MarkdownListItem:
    """Extracted markdown list item with nested children preserved."""

    text: str
    children: list["MarkdownList"] = field(default_factory=list)
    line_number: int | None = None


@dataclass(frozen=True)
class MarkdownList:
    """Extracted markdown list preserving order and nesting."""

    ordered: bool
    items: list[MarkdownListItem]
    start: int | None = None
    line_number: int | None = None


class MarkdownParser:
    """Parse markdown documents and extract common block structures."""

    def parse_file(self, file_path: str | Path) -> Document:
        """Read a UTF-8 markdown file and parse it into a mistletoe document.

        Invalid UTF-8 bytes are replaced so a damaged source file can still be
        parsed and reported on by later pipeline stages.
        """
        path = Path(file_path)
        content = path.read_bytes().decode("utf-8", errors="replace")
        return self.parse_string(content)

    def parse_string(self, markdown: str) -> Document:
        """Parse a markdown string into a mistletoe document."""
        return mistletoe.Document(markdown)

    def extract_tables(self, document: Document) -> list[MarkdownTable]:
        """Extract all tables from a parsed markdown document."""
        tables: list[MarkdownTable] = []
        for table in self._walk(document, Table):
            headers = [self._node_text(cell) for cell in table.header.children or []]
            rows = [
                [self._node_text(cell) for cell in row.children or []]
                for row in table.children or []
            ]
            tables.append(
                MarkdownTable(
                    headers=headers,
                    rows=rows,
                    alignments=list(table.column_align),
                    line_number=getattr(table, "line_number", None),
                )
            )
        return tables

    def extract_lists(self, document: Document) -> list[MarkdownList]:
        """Extract top-level lists from a parsed markdown document.

        Nested lists are preserved on their parent list items rather than being
        duplicated at the top level.
        """
        lists: list[MarkdownList] = []
        for markdown_list in self._walk(document, List):
            if not isinstance(getattr(markdown_list, "_parent", None), ListItem):
                lists.append(self._extract_list(markdown_list))
        return lists

    def _extract_list(self, markdown_list: List) -> MarkdownList:
        items = [self._extract_list_item(item) for item in markdown_list.children or []]
        return MarkdownList(
            ordered=markdown_list.start is not None,
            items=items,
            start=markdown_list.start,
            line_number=getattr(markdown_list, "line_number", None),
        )

    def _extract_list_item(self, item: ListItem) -> MarkdownListItem:
        text_parts: list[str] = []
        child_lists: list[MarkdownList] = []

        for child in item.children or []:
            if isinstance(child, List):
                child_lists.append(self._extract_list(child))
            elif isinstance(child, Paragraph):
                text_parts.append(self._node_text(child))

        return MarkdownListItem(
            text=" ".join(part for part in text_parts if part).strip(),
            children=child_lists,
            line_number=getattr(item, "line_number", None),
        )

    def _node_text(self, node: object) -> str:
        content = getattr(node, "content", None)
        if content is not None:
            return str(content)

        children = getattr(node, "children", None) or []
        return "".join(self._node_text(child) for child in children).strip()

    def _walk(self, node: object, token_type: type) -> Iterable:
        if isinstance(node, token_type):
            yield node

        header = getattr(node, "header", None)
        if header is not None:
            yield from self._walk(header, token_type)

        for child in getattr(node, "children", None) or []:
            yield from self._walk(child, token_type)
