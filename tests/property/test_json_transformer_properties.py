"""Property tests for JSONTransformer."""

import json
import sys

from hypothesis import given, strategies as st

from curriculum_extractor import (
    Competency,
    CurriculumDocument,
    JSONTransformer,
    RubricCriterion,
    Strand,
    SubStrand,
    Value,
)


# Strategy for generating valid text (no control characters)
text_strategy = st.text(
    alphabet=st.characters(
        blacklist_categories=("Cc", "Cs"),  # Exclude control and surrogate characters
        blacklist_characters="\x00",  # Exclude null character
    ),
    min_size=1,
    max_size=100,
)

# Strategy for generating competencies
competency_strategy = st.builds(
    Competency,
    competency=text_strategy,
    context=text_strategy,
)

# Strategy for generating values
value_strategy = st.builds(
    Value,
    value=text_strategy,
    context=text_strategy,
)

# Strategy for generating rubric criteria
rubric_strategy = st.builds(
    RubricCriterion,
    criterion=text_strategy,
    exceeding_expectations=text_strategy,
    meeting_expectations=text_strategy,
    approaching_expectations=text_strategy,
    below_expectations=text_strategy,
)

# Strategy for generating sub-strands
substrand_strategy = st.builds(
    SubStrand,
    sub_strand_id=text_strategy,
    sub_strand_name=text_strategy,
    topics=st.lists(text_strategy, max_size=5),
    specific_learning_outcomes=st.lists(text_strategy, max_size=5),
    suggested_learning_experiences=st.lists(text_strategy, max_size=5),
    key_inquiry_questions=st.lists(text_strategy, max_size=5),
    core_competencies=st.lists(competency_strategy, max_size=3),
    values=st.lists(value_strategy, max_size=3),
    pcis=st.lists(text_strategy, max_size=3),
    suggested_resources=st.lists(text_strategy, max_size=3),
    assessment_methods=st.lists(text_strategy, max_size=3),
)

# Strategy for generating strands
strand_strategy = st.builds(
    Strand,
    strand_id=text_strategy,
    strand_name=text_strategy,
    sub_strands=st.lists(substrand_strategy, max_size=3),
    assessment_rubric=st.lists(rubric_strategy, max_size=3),
)

# Strategy for generating curriculum documents
document_strategy = st.builds(
    CurriculumDocument,
    subject=text_strategy,
    grade=st.integers(min_value=1, max_value=12),
    year=st.integers(min_value=1900, max_value=2100),
    essence_statement=text_strategy,
    general_learning_outcomes=st.lists(text_strategy, min_size=0, max_size=5),
    strands=st.lists(strand_strategy, min_size=1, max_size=3),
)


@given(document_strategy)
def test_property_15_json_validity(document):
    """Property 15: JSON Validity - Validates Requirements 15.1-15.7, 19.1-19.5."""
    transformer = JSONTransformer()
    result = transformer.transform(document)

    # Should be JSON serializable
    json_str = json.dumps(result, ensure_ascii=False)
    assert json_str is not None

    # Should be parseable by standard JSON parser
    parsed = json.loads(json_str)
    assert isinstance(parsed, dict)

    # Should preserve structure
    assert "subject" in parsed
    assert "grade" in parsed
    assert "year" in parsed
    assert "strands" in parsed


@given(
    st.text(
        alphabet=st.characters(
            min_codepoint=0x20,  # Start from space
            max_codepoint=0x10FFFF,  # Full Unicode range
            blacklist_categories=("Cc", "Cs"),  # Exclude control and surrogate
        ),
        min_size=1,
        max_size=100,
    )
)
def test_property_16_special_character_preservation(text):
    """Property 16: Special Character Preservation - Validates Requirements 21.1-21.6."""
    doc = CurriculumDocument(
        subject=text,
        grade=1,
        year=2024,
        essence_statement=text,
        general_learning_outcomes=[text],
        strands=[
            Strand(
                strand_id="1",
                strand_name=text,
                sub_strands=[],
                assessment_rubric=[],
            )
        ],
    )

    transformer = JSONTransformer()
    result = transformer.transform(doc)

    # Should be JSON serializable
    json_str = json.dumps(result, ensure_ascii=False)
    parsed = json.loads(json_str)

    # Characters should be preserved
    assert parsed["subject"] == text
    assert parsed["essence_statement"] == text
    assert parsed["general_learning_outcomes"][0] == text
    assert parsed["strands"][0]["strand_name"] == text


@given(document_strategy)
def test_property_19_mongodb_field_name_compliance(document):
    """Property 19: MongoDB Field Name Compliance - Validates Requirements 25.1-25.4."""
    transformer = JSONTransformer()
    result = transformer.transform(document)

    def check_field_names(obj, path=""):
        """Recursively check that field names don't contain dots or dollar signs."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                # MongoDB field names cannot contain dots or start with dollar signs
                assert "." not in key, f"Field name contains dot: {path}.{key}"
                assert not key.startswith("$"), f"Field name starts with $: {path}.{key}"
                check_field_names(value, f"{path}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_field_names(item, f"{path}[{i}]")

    check_field_names(result)

    # Check document size is reasonable (MongoDB has 16MB limit)
    json_str = json.dumps(result, ensure_ascii=False)
    size_bytes = len(json_str.encode("utf-8"))
    assert size_bytes < 16 * 1024 * 1024, f"Document size {size_bytes} exceeds MongoDB limit"
