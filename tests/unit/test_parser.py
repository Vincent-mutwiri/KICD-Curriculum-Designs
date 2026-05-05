"""Unit tests for MarkdownParser."""
from __future__ import annotations

from pathlib import Path

from mistletoe.block_token import Document

from curriculum_extractor.parser import MarkdownParser


class TestMarkdownParser:
    """Test MarkdownParser behavior."""

    def test_parse_valid_markdown_file(self, tmp_path: Path) -> None:
        markdown_file = tmp_path / "curriculum.md"
        markdown_file.write_text("# Mathematics\n\nLearning outcomes.", encoding="utf-8")

        document = MarkdownParser().parse_file(markdown_file)

        assert isinstance(document, Document)
        assert len(document.children) == 2

    def test_parse_string(self) -> None:
        document = MarkdownParser().parse_string("## Strand\n\nContent")

        assert isinstance(document, Document)
        assert len(document.children) == 2

    def test_extract_tables_with_multiple_structures(self) -> None:
        markdown = """
| Strand | Outcome |
| --- | --- |
| Numbers | Count objects |
| Geometry | Identify shapes |

| Level | Description | Evidence |
| :--- | :---: | ---: |
| Exceeding | Explains ideas | Portfolio |
""".strip()

        tables = MarkdownParser().extract_tables(MarkdownParser().parse_string(markdown))

        assert len(tables) == 2
        assert tables[0].headers == ["Strand", "Outcome"]
        assert tables[0].rows == [
            ["Numbers", "Count objects"],
            ["Geometry", "Identify shapes"],
        ]
        assert tables[1].headers == ["Level", "Description", "Evidence"]
        assert tables[1].alignments == [None, 0, 1]
        assert tables[1].rows[0][2] == "Portfolio"

    def test_extract_nested_lists(self) -> None:
        markdown = """
- Strand 1
  - Sub-strand 1.1
    - Topic A
  - Sub-strand 1.2
- Strand 2
""".strip()

        lists = MarkdownParser().extract_lists(MarkdownParser().parse_string(markdown))

        assert len(lists) == 1
        assert lists[0].ordered is False
        assert [item.text for item in lists[0].items] == ["Strand 1", "Strand 2"]
        first_child_list = lists[0].items[0].children[0]
        assert [item.text for item in first_child_list.items] == ["Sub-strand 1.1", "Sub-strand 1.2"]
        assert first_child_list.items[0].children[0].items[0].text == "Topic A"

    def test_extract_ordered_list(self) -> None:
        markdown = "3. First\n4. Second"

        lists = MarkdownParser().extract_lists(MarkdownParser().parse_string(markdown))

        assert len(lists) == 1
        assert lists[0].ordered is True
        assert lists[0].start == 3
        assert [item.text for item in lists[0].items] == ["First", "Second"]

    def test_parse_file_replaces_invalid_utf8(self, tmp_path: Path) -> None:
        markdown_file = tmp_path / "invalid.md"
        markdown_file.write_bytes(b"# Valid\n\nBroken byte: \xff")

        document = MarkdownParser().parse_file(markdown_file)

        assert isinstance(document, Document)
        assert "Broken byte: \ufffd" in MarkdownParser()._node_text(document)

    def test_malformed_markdown_is_parsed_tolerantly(self) -> None:
        markdown = "# Unclosed [link\n\n| Header | Missing delimiter\n| value"

        document = MarkdownParser().parse_string(markdown)

        assert isinstance(document, Document)
        assert MarkdownParser().extract_tables(document) == []
