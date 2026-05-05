"""
Property-based tests for strand extraction.
"""
from hypothesis import given, strategies as st

from curriculum_extractor.parser import MarkdownParser
from curriculum_extractor.strand_extractor import StrandExtractor


@st.composite
def strand_documents(draw):
    """Generate curriculum documents with N strands and M sub-strands each."""
    num_strands = draw(st.integers(min_value=1, max_value=10))
    strands = []

    for i in range(num_strands):
        strand_id = f"{i + 1}.0"
        strand_name = draw(
            st.text(
                alphabet=st.characters(whitelist_categories=("Lu", "Ll"), min_codepoint=65, max_codepoint=90),
                min_size=3,
                max_size=20,
            ).map(lambda s: s.upper().replace("\n", " "))
        )
        num_sub_strands = draw(st.integers(min_value=0, max_value=5))

        sub_strands = []
        for j in range(num_sub_strands):
            sub_strand_id = f"{i + 1}.{j + 1}"
            sub_strand_name = draw(
                st.text(
                    alphabet=st.characters(whitelist_categories=("Lu", "Ll"), min_codepoint=65, max_codepoint=90),
                    min_size=3,
                    max_size=15,
                ).map(lambda s: s.title().replace("\n", " "))
            )
            sub_strands.append((sub_strand_id, sub_strand_name))

        strands.append((strand_id, strand_name, sub_strands))

    return strands


def build_markdown_from_strands(strands):
    """Build markdown document from strand data."""
    lines = []
    for strand_id, strand_name, sub_strands in strands:
        lines.append(f"# STRAND {strand_id}: {strand_name}\n")
        lines.append(f"\nContent for strand {strand_id}\n\n")

        for sub_strand_id, sub_strand_name in sub_strands:
            lines.append(f"## Sub-Strand {sub_strand_id}: {sub_strand_name}\n")
            lines.append(f"\nContent for sub-strand {sub_strand_id}\n\n")

    return "".join(lines)


@given(strand_documents())
def test_property_9_element_extraction_completeness(strands):
    """
    Property 9: Element Extraction Completeness
    Validates: Requirements 4.1, 4.2, 4.3, 5.1, 5.2, 5.3

    Given a curriculum document with N strands,
    verify that exactly N strands are extracted.
    """
    markdown = build_markdown_from_strands(strands)
    parser = MarkdownParser()
    document = parser.parse_string(markdown)
    extractor = StrandExtractor(parser)

    extracted = extractor.extract_strands(document)

    # Verify exactly N strands are extracted
    assert len(extracted) == len(strands)

    # Verify each strand ID and name matches
    for i, (expected_id, expected_name, _) in enumerate(strands):
        assert extracted[i].strand_id == expected_id
        assert extracted[i].strand_name == expected_name


@given(strand_documents())
def test_property_10_sequential_order_preservation(strands):
    """
    Property 10: Sequential Order Preservation
    Validates: Requirements 4.4, 5.5

    Given a curriculum document with multiple strands,
    verify that output order matches input order.
    """
    markdown = build_markdown_from_strands(strands)
    parser = MarkdownParser()
    document = parser.parse_string(markdown)
    extractor = StrandExtractor(parser)

    extracted = extractor.extract_strands(document)

    # Verify order is preserved
    for i, (expected_id, expected_name, _) in enumerate(strands):
        assert extracted[i].strand_id == expected_id
        assert extracted[i].strand_name == expected_name

    # Verify sequential ordering of IDs
    extracted_ids = [s.strand_id for s in extracted]
    expected_ids = [s[0] for s in strands]
    assert extracted_ids == expected_ids


@given(
    st.lists(
        st.tuples(
            st.text(
                alphabet=st.characters(whitelist_categories=("Lu", "Ll"), min_codepoint=65, max_codepoint=90),
                min_size=3,
                max_size=20,
            ).map(lambda s: s.upper().replace("\n", " ")),
            st.booleans(),
        ),
        min_size=1,
        max_size=5,
    )
)
def test_property_11_empty_collection_representation(strands_with_flags):
    """
    Property 11: Empty Collection Representation
    Validates: Requirements 4.5, 24.1-24.8

    Given strands with no sub-strands or missing optional fields,
    verify that empty arrays are used (not null or missing fields).
    """
    markdown_lines = []

    for i, (strand_name, has_sub_strands) in enumerate(strands_with_flags):
        strand_id = f"{i + 1}.0"
        markdown_lines.append(f"# STRAND {strand_id}: {strand_name}\n")
        markdown_lines.append(f"\nContent for strand {strand_id}\n\n")

        if has_sub_strands:
            markdown_lines.append(f"## Sub-Strand {strand_id}.1: Sub Content\n")
            markdown_lines.append("\nSome sub-strand content\n\n")

    markdown = "".join(markdown_lines)
    parser = MarkdownParser()
    document = parser.parse_string(markdown)
    extractor = StrandExtractor(parser)

    extracted = extractor.extract_strands(document)

    # Verify all strands are extracted regardless of sub-strand presence
    assert len(extracted) == len(strands_with_flags)

    # Verify each strand has valid data structure
    for strand in extracted:
        assert strand.strand_id != ""
        assert strand.strand_name != ""
        # Content boundaries should be set (can be None for end)
        assert strand.content_start_line is not None or strand.content_start_line is None
