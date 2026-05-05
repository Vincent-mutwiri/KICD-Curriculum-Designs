"""Property-based tests for RubricExtractor."""

import html

from hypothesis import given
from hypothesis import strategies as st
from mistletoe import Document

from curriculum_extractor import MarkdownParser, RubricExtractor


@given(
    indicators=st.lists(
        st.text(min_size=1, max_size=50, alphabet=st.characters(min_codepoint=32, max_codepoint=126, blacklist_characters='|\\#*_[]()<>+`')).filter(lambda x: x.strip()),
        min_size=1,
        max_size=10
    ),
    exceeding=st.lists(
        st.text(min_size=1, max_size=30, alphabet=st.characters(min_codepoint=32, max_codepoint=126, blacklist_characters='|\\#*_[]()<>+`')).filter(lambda x: x.strip()),
        min_size=1,
        max_size=10
    ),
    meeting=st.lists(
        st.text(min_size=1, max_size=30, alphabet=st.characters(min_codepoint=32, max_codepoint=126, blacklist_characters='|\\#*_[]()<>+`')).filter(lambda x: x.strip()),
        min_size=1,
        max_size=10
    ),
    approaching=st.lists(
        st.text(min_size=1, max_size=30, alphabet=st.characters(min_codepoint=32, max_codepoint=126, blacklist_characters='|\\#*_[]()<>+`')).filter(lambda x: x.strip()),
        min_size=1,
        max_size=10
    ),
    below=st.lists(
        st.text(min_size=1, max_size=30, alphabet=st.characters(min_codepoint=32, max_codepoint=126, blacklist_characters='|\\#*_[]()<>+`')).filter(lambda x: x.strip()),
        min_size=1,
        max_size=10
    ),
)
def test_property_14_rubric_structure_correctness(
    indicators: list[str],
    exceeding: list[str],
    meeting: list[str],
    approaching: list[str],
    below: list[str],
) -> None:
    """
    Property 14: Rubric Structure Correctness.

    Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5, 14.6

    Verify that each indicator maps to all performance level descriptions
    and that the rubric structure is preserved correctly.
    """
    # Ensure all lists have same length
    min_len = min(len(indicators), len(exceeding), len(meeting), len(approaching), len(below))
    indicators = indicators[:min_len]
    exceeding = exceeding[:min_len]
    meeting = meeting[:min_len]
    approaching = approaching[:min_len]
    below = below[:min_len]

    # Build rubric table
    header = "| Indicator | Exceeds Expectation | Meets Expectation | Approaches Expectation | Below Expectation |"
    separator = "|-----------|---------------------|-------------------|------------------------|-------------------|"
    rows = []
    for i in range(len(indicators)):
        rows.append(f"| {indicators[i]} | {exceeding[i]} | {meeting[i]} | {approaching[i]} | {below[i]} |")

    markdown = "\n".join([header, separator] + rows)
    doc = Document(markdown)

    parser = MarkdownParser()
    extractor = RubricExtractor(parser)
    rubrics = extractor.extract_rubrics(doc)

    # All indicators must be extracted
    assert len(rubrics) == len(indicators)

    # Each rubric must have all performance levels
    for i, rubric in enumerate(rubrics):
        assert rubric.criterion.strip() == html.unescape(indicators[i].strip())
        assert rubric.exceeding_expectations.strip() == html.unescape(exceeding[i].strip())
        assert rubric.meeting_expectations.strip() == html.unescape(meeting[i].strip())
        assert rubric.approaching_expectations.strip() == html.unescape(approaching[i].strip())
        assert rubric.below_expectations.strip() == html.unescape(below[i].strip())
