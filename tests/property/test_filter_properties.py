"""Property-based tests for ContentFilter."""

from mistletoe import Document
from hypothesis import given
from hypothesis import strategies as st

from curriculum_extractor.config import Configuration
from curriculum_extractor.filter import ContentFilter


@given(
    has_copyright=st.booleans(),
    has_toc=st.booleans(),
    has_foreword=st.booleans(),
    has_acknowledgements=st.booleans(),
)
def test_property_7_content_filtering_preserves_essential_data(
    has_copyright: bool,
    has_toc: bool,
    has_foreword: bool,
    has_acknowledgements: bool,
) -> None:
    """
    Property 7: Content Filtering Preserves Essential Data.

    Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7

    Verify that filtering removes only extraneous sections and preserves
    all strand and sub-strand content.
    """
    # Build document with optional extraneous sections
    sections = []
    
    if has_copyright:
        sections.append("# Copyright\n© 2024 KICD\n")
    
    if has_toc:
        sections.append("# Table of Contents\n1. Introduction\n")
    
    if has_foreword:
        sections.append("# Foreword\nThis is the foreword.\n")
    
    if has_acknowledgements:
        sections.append("# Acknowledgements\nThanks to everyone.\n")
    
    # Always include essential content
    sections.append("# Strand 1: Numbers\nStrand content here\n")
    sections.append("## Sub-strand 1.1: Counting\nSub-strand content here\n")
    
    markdown = "\n".join(sections)
    
    doc = Document(markdown)
    config = Configuration()
    filter = ContentFilter(config)
    
    # Filter the document
    filtered = filter.filter_document(doc)
    filtered_headings = [child for child in filtered.children if hasattr(child, "level")]
    
    # Verify correct number of headings remain (2 essential ones)
    assert len(filtered_headings) == 2
    
    # Verify essential content is preserved
    heading_texts = [filter._get_heading_text(h) for h in filtered_headings]
    assert any("Strand 1" in text for text in heading_texts)
    assert any("Sub-strand 1.1" in text for text in heading_texts)
    
    # Verify no extraneous sections remain
    for heading in filtered_headings:
        text = filter._get_heading_text(heading).lower()
        assert "copyright" not in text
        assert "table of contents" not in text
        assert "foreword" not in text
        assert "acknowledgement" not in text


@given(
    preserve_essence=st.booleans(),
    preserve_outcomes=st.booleans(),
)
def test_property_8_configuration_based_preservation(
    preserve_essence: bool, preserve_outcomes: bool
) -> None:
    """
    Property 8: Configuration-Based Preservation.

    Validates: Requirements 3.8, 3.9, 23.1, 23.2

    Verify that configuration deterministically controls preservation
    of essence statements and general outcomes.
    """
    markdown = """# Essence Statement
This is the essence of the subject.

# General Learning Outcomes
Students will learn these outcomes.

# Strand 1
Content here
"""
    
    config = Configuration(
        preserve_essence_statement=preserve_essence,
        preserve_general_outcomes=preserve_outcomes,
    )
    filter = ContentFilter(config)
    
    # Filter document multiple times
    doc1 = Document(markdown)
    doc2 = Document(markdown)
    doc3 = Document(markdown)
    
    filtered1 = filter.filter_document(doc1)
    filtered2 = filter.filter_document(doc2)
    filtered3 = filter.filter_document(doc3)
    
    # Extract heading texts
    headings1 = [filter._get_heading_text(h) for h in filtered1.children if hasattr(h, "level")]
    headings2 = [filter._get_heading_text(h) for h in filtered2.children if hasattr(h, "level")]
    headings3 = [filter._get_heading_text(h) for h in filtered3.children if hasattr(h, "level")]
    
    # Verify deterministic behavior
    assert headings1 == headings2 == headings3
    
    # Verify essence statement preservation matches config
    has_essence = any("Essence" in h for h in headings1)
    assert has_essence == preserve_essence
    
    # Verify general outcomes preservation matches config
    has_outcomes = any("General" in h and "Outcomes" in h for h in headings1)
    assert has_outcomes == preserve_outcomes
    
    # Verify strand is always preserved
    assert any("Strand" in h for h in headings1)
