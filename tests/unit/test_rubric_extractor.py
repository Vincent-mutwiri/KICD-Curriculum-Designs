"""Unit tests for RubricExtractor."""

import pytest
from mistletoe import Document

from curriculum_extractor import RubricExtractor, MarkdownParser


class TestRubricExtractor:
    """Test suite for RubricExtractor class."""

    @pytest.fixture
    def parser(self):
        """Create MarkdownParser instance."""
        return MarkdownParser()

    @pytest.fixture
    def extractor(self, parser):
        """Create RubricExtractor instance."""
        return RubricExtractor(parser)

    def test_identify_rubric_table_valid(self, extractor):
        """Test identification of valid rubric table."""
        markdown = """
| Indicator | Exceeds Expectation | Meets Expectation | Approaches Expectation | Below Expectation |
|-----------|---------------------|-------------------|------------------------|-------------------|
| Test      | Excellent           | Good              | Fair                   | Poor              |
"""
        doc = Document(markdown)
        tables = list(extractor._walk_tables(doc))
        assert len(tables) == 1
        assert extractor.identify_rubric_table(tables[0])

    def test_identify_rubric_table_with_criterion_header(self, extractor):
        """Test identification with 'Criterion' instead of 'Indicator'."""
        markdown = """
| Criterion | Exceeding | Meeting | Approaching | Below |
|-----------|-----------|---------|-------------|-------|
| Test      | A         | B       | C           | D     |
"""
        doc = Document(markdown)
        tables = list(extractor._walk_tables(doc))
        assert extractor.identify_rubric_table(tables[0])

    def test_identify_rubric_table_invalid_no_indicator(self, extractor):
        """Test rejection of table without indicator column."""
        markdown = """
| Column1 | Column2 | Column3 |
|---------|---------|---------|
| A       | B       | C       |
"""
        doc = Document(markdown)
        tables = list(extractor._walk_tables(doc))
        assert not extractor.identify_rubric_table(tables[0])

    def test_identify_rubric_table_invalid_insufficient_levels(self, extractor):
        """Test rejection of table with insufficient performance levels."""
        markdown = """
| Indicator | Exceeds |
|-----------|---------|
| Test      | Good    |
"""
        doc = Document(markdown)
        tables = list(extractor._walk_tables(doc))
        assert not extractor.identify_rubric_table(tables[0])

    def test_extract_rubrics_single_criterion(self, extractor):
        """Test extraction of single rubric criterion."""
        markdown = """
| Indicator | Exceeds Expectation | Meets Expectation | Approaches Expectation | Below Expectation |
|-----------|---------------------|-------------------|------------------------|-------------------|
| Accuracy  | Highly accurate     | Mostly accurate   | Somewhat accurate      | Inaccurate        |
"""
        doc = Document(markdown)
        rubrics = extractor.extract_rubrics(doc)
        
        assert len(rubrics) == 1
        assert rubrics[0].criterion == "Accuracy"
        assert rubrics[0].exceeding_expectations == "Highly accurate"
        assert rubrics[0].meeting_expectations == "Mostly accurate"
        assert rubrics[0].approaching_expectations == "Somewhat accurate"
        assert rubrics[0].below_expectations == "Inaccurate"

    def test_extract_rubrics_multiple_criteria(self, extractor):
        """Test extraction of multiple rubric criteria."""
        markdown = """
| Indicator | Exceeds Expectation | Meets Expectation | Approaches Expectation | Below Expectation |
|-----------|---------------------|-------------------|------------------------|-------------------|
| Accuracy  | Highly accurate     | Mostly accurate   | Somewhat accurate      | Inaccurate        |
| Clarity   | Very clear          | Clear             | Somewhat clear         | Unclear           |
"""
        doc = Document(markdown)
        rubrics = extractor.extract_rubrics(doc)
        
        assert len(rubrics) == 2
        assert rubrics[0].criterion == "Accuracy"
        assert rubrics[1].criterion == "Clarity"

    def test_extract_rubrics_empty_rows_skipped(self, extractor):
        """Test that rows with empty criterion are skipped."""
        markdown = """
| Indicator | Exceeds Expectation | Meets Expectation | Approaches Expectation | Below Expectation |
|-----------|---------------------|-------------------|------------------------|-------------------|
| Accuracy  | Highly accurate     | Mostly accurate   | Somewhat accurate      | Inaccurate        |
|           | Empty               | Empty             | Empty                  | Empty             |
| Clarity   | Very clear          | Clear             | Somewhat clear         | Unclear           |
"""
        doc = Document(markdown)
        rubrics = extractor.extract_rubrics(doc)
        
        assert len(rubrics) == 2
        assert rubrics[0].criterion == "Accuracy"
        assert rubrics[1].criterion == "Clarity"

    def test_extract_rubrics_no_rubric_tables(self, extractor):
        """Test extraction when no rubric tables exist."""
        markdown = """
# Heading

Some text content.

| Not | A | Rubric |
|-----|---|--------|
| X   | Y | Z      |
"""
        doc = Document(markdown)
        rubrics = extractor.extract_rubrics(doc)
        assert len(rubrics) == 0

    def test_parse_rubric_row_valid(self, extractor):
        """Test parsing of valid rubric row."""
        markdown = """
| Indicator | Exceeds | Meets | Approaches | Below |
|-----------|---------|-------|------------|-------|
| Test      | A       | B     | C          | D     |
"""
        doc = Document(markdown)
        tables = list(extractor._walk_tables(doc))
        table = tables[0]
        
        headers = [extractor._get_cell_text(cell).strip().lower() for cell in table.header.children]
        col_map = extractor._map_columns(headers)
        
        row = table.children[0]
        criterion = extractor.parse_rubric_row(row.children, col_map)
        
        assert criterion is not None
        assert criterion.criterion == "Test"
        assert criterion.exceeding_expectations == "A"
        assert criterion.meeting_expectations == "B"
        assert criterion.approaching_expectations == "C"
        assert criterion.below_expectations == "D"

    def test_parse_rubric_row_empty_criterion(self, extractor):
        """Test parsing returns None for empty criterion."""
        markdown = """
| Indicator | Exceeds | Meets | Approaches | Below |
|-----------|---------|-------|------------|-------|
|           | A       | B     | C          | D     |
"""
        doc = Document(markdown)
        tables = list(extractor._walk_tables(doc))
        table = tables[0]
        
        headers = [extractor._get_cell_text(cell).strip().lower() for cell in table.header.children]
        col_map = extractor._map_columns(headers)
        
        row = table.children[0]
        criterion = extractor.parse_rubric_row(row.children, col_map)
        
        assert criterion is None

    def test_extract_rubrics_with_formatted_text(self, extractor):
        """Test extraction with bold and italic text in cells."""
        markdown = """
| Indicator | Exceeds Expectation | Meets Expectation | Approaches Expectation | Below Expectation |
|-----------|---------------------|-------------------|------------------------|-------------------|
| **Bold**  | *Italic*            | Normal            | **Bold** text          | *Italic* text     |
"""
        doc = Document(markdown)
        rubrics = extractor.extract_rubrics(doc)
        
        assert len(rubrics) == 1
        assert rubrics[0].criterion == "Bold"
        assert rubrics[0].exceeding_expectations == "Italic"

    def test_extract_rubrics_multiple_tables(self, extractor):
        """Test extraction from document with multiple rubric tables."""
        markdown = """
| Indicator | Exceeds | Meets | Approaches | Below |
|-----------|---------|-------|------------|-------|
| Test1     | A1      | B1    | C1         | D1    |

Some text between tables.

| Indicator | Exceeds | Meets | Approaches | Below |
|-----------|---------|-------|------------|-------|
| Test2     | A2      | B2    | C2         | D2    |
"""
        doc = Document(markdown)
        rubrics = extractor.extract_rubrics(doc)
        
        assert len(rubrics) == 2
        assert rubrics[0].criterion == "Test1"
        assert rubrics[1].criterion == "Test2"

    def test_map_columns_all_present(self, extractor):
        """Test column mapping with all required columns."""
        headers = ['indicator', 'exceeds expectation', 'meets expectation', 'approaches expectation', 'below expectation']
        col_map = extractor._map_columns(headers)
        
        assert col_map == {
            'criterion': 0,
            'exceeding': 1,
            'meeting': 2,
            'approaching': 3,
            'below': 4
        }

    def test_map_columns_missing_column(self, extractor):
        """Test column mapping returns empty dict when column missing."""
        headers = ['indicator', 'exceeds', 'meets']
        col_map = extractor._map_columns(headers)
        assert col_map == {}

    def test_get_cell_text_empty_cell(self, extractor):
        """Test text extraction from empty cell."""
        markdown = """
| A |   |
|---|---|
| X | Y |
"""
        doc = Document(markdown)
        tables = list(extractor._walk_tables(doc))
        table = tables[0]
        
        cell = table.header.children[1]
        text = extractor._get_cell_text(cell)
        assert text == ""
