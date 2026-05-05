"""
Unit tests for StrandExtractor.
"""
import pytest

from curriculum_extractor.parser import MarkdownParser
from curriculum_extractor.strand_extractor import StrandExtractor


class TestStrandExtractor:
    """Test strand extraction functionality."""

    def test_identify_strand_header_standard_format(self):
        """Test identification of standard strand header format."""
        extractor = StrandExtractor()
        assert extractor._is_strand_header("STRAND 1.0: NUMBERS")
        assert extractor._is_strand_header("STRAND 2.0: MEASUREMENT")

    def test_identify_strand_header_case_insensitive(self):
        """Test strand header identification is case insensitive."""
        extractor = StrandExtractor()
        assert extractor._is_strand_header("Strand 1.0: Numbers")
        assert extractor._is_strand_header("strand 3.0: geometry")

    def test_identify_strand_header_with_whitespace(self):
        """Test strand header with extra whitespace."""
        extractor = StrandExtractor()
        assert extractor._is_strand_header("  STRAND 1.0: NUMBERS  ")
        assert extractor._is_strand_header("STRAND  2.0:  MEASUREMENT")

    def test_identify_strand_header_single_digit(self):
        """Test strand header with single digit ID."""
        extractor = StrandExtractor()
        assert extractor._is_strand_header("STRAND 1: NUMBERS")

    def test_identify_strand_header_rejects_invalid(self):
        """Test rejection of non-strand headers."""
        extractor = StrandExtractor()
        assert not extractor._is_strand_header("SUMMARY OF STRANDS")
        assert not extractor._is_strand_header("Sub-Strand 1.1")
        assert not extractor._is_strand_header("STRAND: NUMBERS")
        assert not extractor._is_strand_header("1.0: NUMBERS")

    def test_parse_strand_id_and_name_standard(self):
        """Test parsing strand ID and name from standard format."""
        extractor = StrandExtractor()
        strand_id, name = extractor._parse_strand_header("STRAND 1.0: NUMBERS")
        assert strand_id == "1.0"
        assert name == "NUMBERS"

    def test_parse_strand_id_and_name_single_digit(self):
        """Test parsing strand with single digit ID."""
        extractor = StrandExtractor()
        strand_id, name = extractor._parse_strand_header("STRAND 2: MEASUREMENT")
        assert strand_id == "2"
        assert name == "MEASUREMENT"

    def test_parse_strand_id_and_name_multi_word(self):
        """Test parsing strand with multi-word name."""
        extractor = StrandExtractor()
        strand_id, name = extractor._parse_strand_header(
            "STRAND 3.0: ALGEBRAIC EXPRESSIONS"
        )
        assert strand_id == "3.0"
        assert name == "ALGEBRAIC EXPRESSIONS"

    def test_parse_strand_id_and_name_case_insensitive(self):
        """Test parsing is case insensitive."""
        extractor = StrandExtractor()
        strand_id, name = extractor._parse_strand_header("Strand 1.0: Numbers")
        assert strand_id == "1.0"
        assert name == "Numbers"

    def test_parse_strand_invalid_format(self):
        """Test parsing returns empty strings for invalid format."""
        extractor = StrandExtractor()
        strand_id, name = extractor._parse_strand_header("INVALID HEADER")
        assert strand_id == ""
        assert name == ""

    def test_extract_strands_sequential_order(self):
        """Test strands are extracted in sequential order."""
        markdown = """
# STRAND 1.0: NUMBERS

Content for strand 1

# STRAND 2.0: MEASUREMENT

Content for strand 2

# STRAND 3.0: GEOMETRY

Content for strand 3
"""
        parser = MarkdownParser()
        document = parser.parse_string(markdown)
        extractor = StrandExtractor(parser)

        strands = extractor.extract_strands(document)

        assert len(strands) == 3
        assert strands[0].strand_id == "1.0"
        assert strands[0].strand_name == "NUMBERS"
        assert strands[1].strand_id == "2.0"
        assert strands[1].strand_name == "MEASUREMENT"
        assert strands[2].strand_id == "3.0"
        assert strands[2].strand_name == "GEOMETRY"

    def test_extract_strands_empty_document(self):
        """Test extraction from document with no strands."""
        markdown = """
# Introduction

This is a curriculum document.

## Some Section

No strands here.
"""
        parser = MarkdownParser()
        document = parser.parse_string(markdown)
        extractor = StrandExtractor(parser)

        strands = extractor.extract_strands(document)

        assert len(strands) == 0

    def test_extract_strands_with_sub_strands(self):
        """Test extraction ignores sub-strand headers."""
        markdown = """
# STRAND 1.0: NUMBERS

## Sub-Strand 1.1: Whole Numbers

Content

# STRAND 2.0: MEASUREMENT

## Sub-Strand 2.1: Length

Content
"""
        parser = MarkdownParser()
        document = parser.parse_string(markdown)
        extractor = StrandExtractor(parser)

        strands = extractor.extract_strands(document)

        assert len(strands) == 2
        assert strands[0].strand_id == "1.0"
        assert strands[1].strand_id == "2.0"

    def test_extract_strands_content_boundaries(self):
        """Test content start and end line tracking."""
        markdown = """
# STRAND 1.0: NUMBERS

Content for strand 1

# STRAND 2.0: MEASUREMENT

Content for strand 2
"""
        parser = MarkdownParser()
        document = parser.parse_string(markdown)
        extractor = StrandExtractor(parser)

        strands = extractor.extract_strands(document)

        assert strands[0].content_start_line is not None
        assert strands[0].content_end_line == strands[1].content_start_line
        assert strands[1].content_end_line is None
