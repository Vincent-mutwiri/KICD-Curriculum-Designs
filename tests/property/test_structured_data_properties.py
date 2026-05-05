"""
Property tests for structured sub-strand data extraction.
"""

from hypothesis import given
from hypothesis import strategies as st

from curriculum_extractor.parser import MarkdownParser
from curriculum_extractor.substrand_extractor import SubStrandExtractor

simple_word = st.text(
    alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd"),
        min_codepoint=48,
        max_codepoint=122,
    ),
    min_size=1,
    max_size=10,
)

simple_text = st.lists(simple_word, min_size=1, max_size=4).map(" ".join)


structured_items = st.lists(
    st.tuples(simple_text, simple_text),
    min_size=1,
    max_size=8,
    unique_by=lambda item: item[0].casefold(),
)


@given(items=structured_items)
def test_property_13_competency_extraction_correctness(
    items: list[tuple[str, str]],
) -> None:
    """
    Property 13: Structured Data Extraction Correctness
    Validates: Requirements 9.1-9.6, 10.1-10.6

    Given competencies with Name: Context format,
    verify correct separation into name and context fields.
    """
    markdown = "\n".join(f"• {name}: {context}" for name, context in items)
    extractor = SubStrandExtractor(MarkdownParser())

    competencies = extractor.parse_competencies(markdown)

    assert [(item.competency, item.context) for item in competencies] == items


@given(items=structured_items)
def test_property_13_value_extraction_correctness(
    items: list[tuple[str, str]],
) -> None:
    """
    Property 13: Structured Data Extraction Correctness
    Validates: Requirements 9.1-9.6, 10.1-10.6

    Given values with Name: Context format,
    verify correct separation into name and context fields.
    """
    markdown = "\n".join(f"• {name}: {context}" for name, context in items)
    extractor = SubStrandExtractor(MarkdownParser())

    values = extractor.parse_values(markdown)

    assert [(item.value, item.context) for item in values] == items
