"""Property tests for JSONTransformer."""

import json

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


"""Property tests for JSONTransformer."""

import json

from hypothesis import given, settings, strategies as st, HealthCheck

from curriculum_extractor import (
    Competency,
    CurriculumDocument,
    JSONTransformer,
    RubricCriterion,
    Strand,
    SubStrand,
    Value,
)


# Strategy for generating valid text (alphanumeric + common punctuation)
text_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd", "Zs", "Po"),  # Letters, digits, spaces, punctuation
    ),
    min_size=1,
    max_size=50,
).filter(lambda s: s.strip())  # Ensure not whitespace-only

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


# Strategy for generating sub-strands with unique IDs
@st.composite
def substrand_with_id_strategy(draw, sub_strand_id):
    """Generate a sub-strand with a specific ID."""
    return SubStrand(
        sub_strand_id=sub_strand_id,
        sub_strand_name=draw(text_strategy),
        topics=draw(st.lists(text_strategy, max_size=5)),
        specific_learning_outcomes=draw(st.lists(text_strategy, max_size=5)),
        suggested_learning_experiences=draw(st.lists(text_strategy, max_size=5)),
        key_inquiry_questions=draw(st.lists(text_strategy, max_size=5)),
        core_competencies=draw(st.lists(competency_strategy, max_size=3)),
        values=draw(st.lists(value_strategy, max_size=3)),
        pcis=draw(st.lists(text_strategy, max_size=3)),
        suggested_resources=draw(st.lists(text_strategy, max_size=3)),
        assessment_methods=draw(st.lists(text_strategy, max_size=3)),
    )


# Strategy for generating strands with unique IDs
@st.composite
def strand_with_id_strategy(draw, strand_id):
    """Generate a strand with a specific ID and unique sub-strand IDs."""
    num_substrands = draw(st.integers(min_value=0, max_value=3))
    sub_strands = [
        draw(substrand_with_id_strategy(f"{strand_id}.{i+1}"))
        for i in range(num_substrands)
    ]
    
    return Strand(
        strand_id=strand_id,
        strand_name=draw(text_strategy),
        sub_strands=sub_strands,
        assessment_rubric=draw(st.lists(rubric_strategy, max_size=3)),
    )


# Strategy for generating curriculum documents with unique strand IDs
@st.composite
def document_strategy(draw):
    """Generate a curriculum document with unique strand IDs."""
    num_strands = draw(st.integers(min_value=1, max_value=3))
    strands = [
        draw(strand_with_id_strategy(str(i+1)))
        for i in range(num_strands)
    ]
    
    return CurriculumDocument(
        subject=draw(text_strategy),
        grade=draw(st.integers(min_value=1, max_value=12)),
        year=draw(st.integers(min_value=1900, max_value=2100)),
        essence_statement=draw(text_strategy),
        general_learning_outcomes=draw(st.lists(text_strategy, min_size=0, max_size=5)),
        strands=strands,
    )


@given(document_strategy())
@settings(suppress_health_check=[HealthCheck.too_slow], max_examples=50)
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


@given(text_strategy)
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

    # Characters should be preserved (note: Pydantic strips whitespace)
    assert parsed["subject"] == text.strip()
    assert parsed["essence_statement"] == text.strip()
    assert parsed["general_learning_outcomes"][0] == text.strip()
    assert parsed["strands"][0]["strand_name"] == text.strip()


@given(document_strategy())
@settings(suppress_health_check=[HealthCheck.too_slow], max_examples=50)
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
