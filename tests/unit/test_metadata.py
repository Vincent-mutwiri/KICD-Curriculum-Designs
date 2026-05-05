"""Unit tests for MetadataExtractor."""

from mistletoe import Document

from curriculum_extractor.metadata import MetadataExtractor
from curriculum_extractor.models import GradeRange


class TestMetadataExtractor:
    """Test suite for MetadataExtractor class."""

    def test_extract_from_filename_underscore_separator(self) -> None:
        """Test filename parsing with underscore separator."""
        extractor = MetadataExtractor()
        result = extractor.extract_from_filename("Mathematics_Grade_10_2024.md")

        assert result["subject"] == "Mathematics"
        assert result["grade"] == 10
        assert result["year"] == 2024

    def test_extract_from_filename_space_separator(self) -> None:
        """Test filename parsing with space separator."""
        extractor = MetadataExtractor()
        result = extractor.extract_from_filename("English Language Grade 5 2023.md")

        assert result["subject"] == "English Language"
        assert result["grade"] == 5
        assert result["year"] == 2023

    def test_extract_from_filename_hyphen_separator(self) -> None:
        """Test filename parsing with hyphen separator."""
        extractor = MetadataExtractor()
        result = extractor.extract_from_filename("Science-Grade-7-2022.md")

        assert result["subject"] == "Science"
        assert result["grade"] == 7
        assert result["year"] == 2022

    def test_extract_from_filename_multi_word_subject(self) -> None:
        """Test filename parsing with multi-word subject names."""
        extractor = MetadataExtractor()
        result = extractor.extract_from_filename("Social Studies_Grade_4_2024.md")

        assert result["subject"] == "Social Studies"
        assert result["grade"] == 4
        assert result["year"] == 2024

    def test_extract_from_filename_grade_first_subject(self) -> None:
        """Test filename parsing when grade appears before the subject."""
        extractor = MetadataExtractor()
        result = extractor.extract_from_filename("Grade 4 Science and Technology.md")

        assert result["subject"] == "Science And Technology"
        assert result["grade"] == 4
        assert result["year"] is None

    def test_extract_from_filename_invalid_format(self) -> None:
        """Test filename parsing with invalid format."""
        extractor = MetadataExtractor()
        result = extractor.extract_from_filename("InvalidFilename.md")

        assert result["subject"] is None
        assert result["grade"] is None
        assert result["year"] is None

    def test_extract_from_content_subject_header(self) -> None:
        """Test content extraction with subject header."""
        markdown = "# Subject: Mathematics\n\nContent here"
        doc = Document(markdown)
        extractor = MetadataExtractor()

        result = extractor.extract_from_content(doc)
        assert result["subject"] == "Mathematics"

    def test_extract_from_content_grade_header(self) -> None:
        """Test content extraction with grade header."""
        markdown = "# Grade 10\n\nContent here"
        doc = Document(markdown)
        extractor = MetadataExtractor()

        result = extractor.extract_from_content(doc)
        assert result["grade"] == 10

    def test_extract_from_content_year_in_header(self) -> None:
        """Test content extraction with year in header."""
        markdown = "# Curriculum 2024\n\nContent here"
        doc = Document(markdown)
        extractor = MetadataExtractor()

        result = extractor.extract_from_content(doc)
        assert result["year"] == 2024

    def test_extract_from_content_real_title_block(self) -> None:
        """Test title-block metadata used by real KICD files."""
        markdown = """**PRIMARY SCHOOL EDUCATION CURRICULUM DESIGN SCIENCE AND TECHNOLOGY**

**GRADE 4**

First Published 2017

Revised 2024
"""
        doc = Document(markdown)
        extractor = MetadataExtractor()

        result = extractor.extract_from_content(doc)

        assert result["subject"] == "Science And Technology"
        assert result["grade"] == 4
        assert result["year"] == 2024

    def test_normalize_subject_strips_whitespace(self) -> None:
        """Test subject normalization strips whitespace."""
        extractor = MetadataExtractor()
        assert extractor.normalize_subject("  Mathematics  ") == "Mathematics"

    def test_normalize_subject_title_case(self) -> None:
        """Test subject normalization converts to title case."""
        extractor = MetadataExtractor()
        assert extractor.normalize_subject("english language") == "English Language"

    def test_normalize_subject_multiple_spaces(self) -> None:
        """Test subject normalization collapses multiple spaces."""
        extractor = MetadataExtractor()
        assert extractor.normalize_subject("Social   Studies") == "Social Studies"

    def test_normalize_subject_special_characters(self) -> None:
        """Test subject normalization preserves special characters."""
        extractor = MetadataExtractor()
        assert extractor.normalize_subject("art & design") == "Art & Design"

    def test_parse_grade_standard_format(self) -> None:
        """Test grade parsing with 'Grade N' format."""
        extractor = MetadataExtractor()
        assert extractor.parse_grade("Grade 10") == 10

    def test_parse_grade_gredi_format(self) -> None:
        """Test grade parsing with 'Gredi N' format."""
        extractor = MetadataExtractor()
        assert extractor.parse_grade("Gredi 5") == 5

    def test_parse_grade_g_format(self) -> None:
        """Test grade parsing with 'G N' format."""
        extractor = MetadataExtractor()
        assert extractor.parse_grade("G 7") == 7

    def test_parse_grade_numeric_only(self) -> None:
        """Test grade parsing with numeric only."""
        extractor = MetadataExtractor()
        assert extractor.parse_grade("12") == 12

    def test_parse_grade_range_hyphen(self) -> None:
        """Test grade parsing with range using hyphen."""
        extractor = MetadataExtractor()
        result = extractor.parse_grade("Grade 1-3")

        assert isinstance(result, GradeRange)
        assert result.start == 1
        assert result.end == 3

    def test_parse_grade_range_to(self) -> None:
        """Test grade parsing with range using 'to'."""
        extractor = MetadataExtractor()
        result = extractor.parse_grade("Grade 4 to 6")

        assert isinstance(result, GradeRange)
        assert result.start == 4
        assert result.end == 6

    def test_parse_grade_invalid(self) -> None:
        """Test grade parsing with invalid input."""
        extractor = MetadataExtractor()
        assert extractor.parse_grade("Invalid") is None

    def test_parse_grade_invalid_range(self) -> None:
        """Test grade parsing with invalid range."""
        extractor = MetadataExtractor()
        result = extractor.parse_grade("Grade 10-5")
        assert result is None
