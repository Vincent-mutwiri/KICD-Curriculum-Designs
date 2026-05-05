"""Property tests for round-trip curriculum transformation."""

import json

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from curriculum_extractor import (
    Competency,
    CurriculumDocument,
    JSONTransformer,
    RubricCriterion,
    Strand,
    SubStrand,
    Value,
    verify_round_trip,
)

text_strategy = st.text(
    alphabet=st.characters(
        blacklist_categories=("Cc", "Cs"),
    ),
    min_size=1,
    max_size=50,
).filter(lambda value: bool(value.strip()))


competency_strategy = st.builds(
    Competency,
    competency=text_strategy,
    context=text_strategy,
)

value_strategy = st.builds(
    Value,
    value=text_strategy,
    context=text_strategy,
)

rubric_strategy = st.builds(
    RubricCriterion,
    criterion=text_strategy,
    exceeding_expectations=text_strategy,
    meeting_expectations=text_strategy,
    approaching_expectations=text_strategy,
    below_expectations=text_strategy,
)


@st.composite
def substrand_strategy(draw: st.DrawFn, sub_strand_id: str) -> SubStrand:
    """Generate a valid sub-strand with a deterministic unique ID."""
    return SubStrand(
        sub_strand_id=sub_strand_id,
        sub_strand_name=draw(text_strategy),
        topics=draw(st.lists(text_strategy, max_size=4)),
        specific_learning_outcomes=draw(st.lists(text_strategy, max_size=4)),
        suggested_learning_experiences=draw(st.lists(text_strategy, max_size=4)),
        key_inquiry_questions=draw(st.lists(text_strategy, max_size=4)),
        core_competencies=draw(st.lists(competency_strategy, max_size=3)),
        values=draw(st.lists(value_strategy, max_size=3)),
        pcis=draw(st.lists(text_strategy, max_size=3)),
        suggested_resources=draw(st.lists(text_strategy, max_size=3)),
        assessment_methods=draw(st.lists(text_strategy, max_size=3)),
    )


@st.composite
def strand_strategy(draw: st.DrawFn, strand_id: str) -> Strand:
    """Generate a valid strand with unique sub-strand IDs."""
    sub_strands = [
        draw(substrand_strategy(f"{strand_id}.{index + 1}"))
        for index in range(draw(st.integers(min_value=0, max_value=3)))
    ]

    return Strand(
        strand_id=strand_id,
        strand_name=draw(text_strategy),
        sub_strands=sub_strands,
        assessment_rubric=draw(st.lists(rubric_strategy, max_size=3)),
    )


@st.composite
def curriculum_document_strategy(draw: st.DrawFn) -> CurriculumDocument:
    """Generate valid curriculum documents with unique strand IDs."""
    strands = [
        draw(strand_strategy(str(index + 1)))
        for index in range(draw(st.integers(min_value=1, max_value=3)))
    ]

    return CurriculumDocument(
        subject=draw(text_strategy),
        grade=draw(st.integers(min_value=1, max_value=12)),
        year=draw(st.integers(min_value=1900, max_value=2100)),
        essence_statement=draw(text_strategy),
        general_learning_outcomes=draw(st.lists(text_strategy, max_size=5)),
        strands=strands,
    )


@given(curriculum_document_strategy())
@settings(suppress_health_check=[HealthCheck.too_slow], max_examples=50)
def test_property_1_round_trip_transformation_preserves_data(
    document: CurriculumDocument,
) -> None:
    """Property 1: Round-Trip Transformation Preserves Data."""
    transformed = JSONTransformer().transform(document)
    formatted_json = json.dumps(transformed, ensure_ascii=False, indent=4)

    result = verify_round_trip(document, formatted_json)

    assert result.is_equivalent is True
    assert result.differences == []
    assert result.parsed_document == document
