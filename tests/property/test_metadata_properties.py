"""Property-based tests for MetadataExtractor."""

from hypothesis import given
from hypothesis import strategies as st
from mistletoe import Document

from curriculum_extractor.metadata import MetadataExtractor
from curriculum_extractor.models import GradeRange


@given(
    subject=st.text(min_size=1, max_size=50, alphabet="abcdefghijklmnopqrstuvwxyz ").filter(lambda x: x.strip()),
    grade=st.integers(min_value=1, max_value=12),
    year=st.integers(min_value=1900, max_value=2100),
)
def test_property_4_metadata_extraction_completeness(
    subject: str, grade: int, year: int
) -> None:
    """
    Property 4: Metadata Extraction Completeness.

    Validates: Requirements 1.5, 1.6, 1.7, 2.1, 2.2, 2.3

    Verify that all three metadata fields (subject, grade, year) are
    extracted correctly from valid curriculum filenames.
    """
    extractor = MetadataExtractor()
    subject_clean = extractor.normalize_subject(subject)
    filename = f"{subject_clean}_Grade_{grade}_{year}.md"

    result = extractor.extract_from_filename(filename)
    
    # All three fields must be extracted
    assert result["subject"] is not None
    assert result["grade"] is not None
    assert result["year"] is not None
    
    # Values must match input
    assert result["subject"] == subject_clean
    assert result["grade"] == grade
    assert result["year"] == year


@given(
    grade_num=st.integers(min_value=1, max_value=12),
    format_choice=st.sampled_from(["Grade {}", "Gredi {}", "G {}", "{}"]),
)
def test_property_5_grade_format_normalization_single(
    grade_num: int, format_choice: str
) -> None:
    """
    Property 5: Grade Format Normalization (single grades).

    Validates: Requirements 2.5, 2.6, 18.1, 18.2

    Verify correct extraction of numeric values from various grade formats.
    """
    grade_str = format_choice.format(grade_num)
    
    extractor = MetadataExtractor()
    result = extractor.parse_grade(grade_str)
    
    assert result == grade_num


@given(
    start=st.integers(min_value=1, max_value=11),
    end=st.integers(min_value=2, max_value=12),
    separator=st.sampled_from(["-", " to "]),
)
def test_property_5_grade_format_normalization_range(
    start: int, end: int, separator: str
) -> None:
    """
    Property 5: Grade Format Normalization (ranges).

    Validates: Requirements 2.5, 2.6, 18.1, 18.2

    Verify correct extraction of range objects from various grade formats.
    """
    if start > end:
        start, end = end, start
    
    grade_str = f"Grade {start}{separator}{end}"
    
    extractor = MetadataExtractor()
    result = extractor.parse_grade(grade_str)
    
    assert isinstance(result, GradeRange)
    assert result.start == start
    assert result.end == end


@given(
    subject=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
)
def test_property_6_subject_name_normalization_idempotence(subject: str) -> None:
    """
    Property 6: Subject Name Normalization Idempotence.

    Validates: Requirements 2.4

    Verify that normalize(normalize(name)) == normalize(name).
    """
    extractor = MetadataExtractor()
    
    normalized_once = extractor.normalize_subject(subject)
    normalized_twice = extractor.normalize_subject(normalized_once)
    
    assert normalized_once == normalized_twice
