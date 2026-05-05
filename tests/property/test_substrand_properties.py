"""Property-based tests for SubStrandExtractor."""

from hypothesis import given, strategies as st
from curriculum_extractor import MarkdownParser, SubStrandExtractor


# Property 12: List Element Extraction Preserves Content
@given(
    items=st.lists(
        st.text(
            alphabet=st.characters(
                blacklist_categories=("Cs",),
                blacklist_characters="*_●○•"
            ),
            min_size=5,
            max_size=50
        ).filter(lambda x: x.strip()),  # Ensure non-empty
        min_size=1,
        max_size=10
    ),
    marker=st.sampled_from(["●", "a)", "1.", "**", "*", "_"])
)
def test_property_12_list_element_extraction_preserves_content(items, marker):
    """
    Property 12: List Element Extraction Preserves Content
    
    Validates Requirements: 6.1-6.5, 7.1-7.5, 8.1-8.4, 11.1-11.4, 12.1-12.4, 13.1-13.4
    
    Given a list of text items with various formatting markers,
    when the list is parsed,
    then all text content is preserved while formatting is removed.
    """
    parser = MarkdownParser()
    extractor = SubStrandExtractor(parser)
    
    # Build formatted text based on marker type
    if marker in ["●"]:
        # Bullet list
        formatted_text = " ".join(f"{marker} {item}" for item in items)
    elif marker == "a)":
        # Letter list
        letters = "abcdefghij"
        formatted_text = " ".join(f"{letters[i]}) {item}" for i, item in enumerate(items))
    elif marker == "1.":
        # Numbered list
        formatted_text = "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
    elif marker == "**":
        # Bold formatting
        formatted_text = " ● ".join(f"**{item}**" for item in items)
    elif marker == "*":
        # Italic formatting
        formatted_text = " ● ".join(f"*{item}*" for item in items)
    elif marker == "_":
        # Underline formatting
        formatted_text = " ● ".join(f"_{item}_" for item in items)
    else:
        formatted_text = " ● ".join(items)
    
    # Parse the list
    parsed_items = extractor._parse_list_items(formatted_text)
    
    # Verify content is preserved (allowing for whitespace normalization)
    assert len(parsed_items) == len(items), f"Expected {len(items)} items, got {len(parsed_items)}"
    
    for original, parsed in zip(items, parsed_items):
        # Normalize whitespace for comparison
        original_normalized = " ".join(original.split())
        parsed_normalized = " ".join(parsed.split())
        
        # Check that content is preserved (allowing for trailing punctuation removal)
        # The parser intentionally removes trailing commas and periods
        original_stripped = original_normalized.rstrip('.,')
        assert original_stripped == parsed_normalized or original_normalized == parsed_normalized, \
            f"Content mismatch: '{original_normalized}' != '{parsed_normalized}'"
        
        # Verify formatting markers are removed
        assert "**" not in parsed, "Bold markers not removed"
        assert not (parsed.startswith("*") and parsed.endswith("*")), "Italic markers not removed"
        assert not (parsed.startswith("_") and parsed.endswith("_")), "Underline markers not removed"
        assert not parsed.startswith("●"), "Bullet markers not removed"
        assert not parsed.startswith(tuple(f"{i}." for i in range(10))), "Number markers not removed"


# Additional property test for nested formatting
@given(
    items=st.lists(
        st.text(
            alphabet=st.characters(blacklist_categories=("Cs",), blacklist_characters="*_"),
            min_size=3,
            max_size=30
        ).filter(lambda x: x.strip()),  # Ensure non-empty after stripping
        min_size=1,
        max_size=5
    )
)
def test_property_12_nested_formatting_removal(items):
    """
    Property 12 Extension: Nested formatting is properly removed.
    
    Tests that nested bold/italic combinations are handled correctly.
    """
    parser = MarkdownParser()
    extractor = SubStrandExtractor(parser)
    
    # Create text with nested formatting
    formatted_items = [f"**_{item}_**" for item in items]
    formatted_text = " ● ".join(formatted_items)
    
    # Parse the list
    parsed_items = extractor._parse_list_items(formatted_text)
    
    # Verify all formatting is removed
    assert len(parsed_items) == len(items)
    
    for original, parsed in zip(items, parsed_items):
        original_normalized = " ".join(original.split())
        parsed_normalized = " ".join(parsed.split())
        
        # Content should be preserved
        assert original_normalized in parsed_normalized or parsed_normalized in original_normalized
        
        # No formatting markers should remain (since we excluded them from content)
        assert "**" not in parsed
        assert "_" not in parsed


# Property test for empty and whitespace handling
@given(
    num_items=st.integers(min_value=0, max_value=10),
    include_empty=st.booleans()
)
def test_property_12_empty_and_whitespace_handling(num_items, include_empty):
    """
    Property 12 Extension: Empty items and whitespace are handled correctly.
    
    Tests that empty list items are filtered out and whitespace is normalized.
    """
    parser = MarkdownParser()
    extractor = SubStrandExtractor(parser)
    
    # Create list with potential empty items
    items = []
    for i in range(num_items):
        if include_empty and i % 3 == 0:
            items.append("")
        else:
            items.append(f"item {i}")
    
    formatted_text = " ● ".join(items)
    
    # Parse the list
    parsed_items = extractor._parse_list_items(formatted_text)
    
    # Verify empty items are filtered out
    expected_count = sum(1 for item in items if item.strip())
    assert len(parsed_items) == expected_count
    
    # Verify no empty items in result
    assert all(item.strip() for item in parsed_items)
