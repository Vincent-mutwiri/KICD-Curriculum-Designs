"""Unit tests for round-trip verification."""

import json

from curriculum_extractor import (
    Competency,
    CurriculumDocument,
    JSONTransformer,
    RoundTripVerifier,
    RubricCriterion,
    Strand,
    SubStrand,
    Value,
    compare_curriculum_documents,
    parse_json_to_curriculum,
    verify_round_trip,
)


def sample_document() -> CurriculumDocument:
    """Build a complete curriculum document for round-trip tests."""
    return CurriculumDocument(
        subject="Science",
        grade=4,
        year=2024,
        essence_statement="Learners explore scientific ideas.",
        general_learning_outcomes=["Observe natural phenomena"],
        strands=[
            Strand(
                strand_id="1",
                strand_name="Living Things",
                sub_strands=[
                    SubStrand(
                        sub_strand_id="1.1",
                        sub_strand_name="Plants",
                        topics=["Roots", "Leaves"],
                        specific_learning_outcomes=["Identify plant parts"],
                        suggested_learning_experiences=["Observe a seedling"],
                        key_inquiry_questions=["What do roots do?"],
                        core_competencies=[
                            Competency(
                                competency="Critical thinking",
                                context="Classifying plant parts",
                            )
                        ],
                        values=[
                            Value(
                                value="Responsibility",
                                context="Caring for classroom plants",
                            )
                        ],
                        pcis=["Environmental awareness"],
                        suggested_resources=["Seedlings"],
                        assessment_methods=["Observation checklist"],
                    )
                ],
                assessment_rubric=[
                    RubricCriterion(
                        criterion="Identifies parts",
                        exceeding_expectations="Explains functions",
                        meeting_expectations="Names all parts",
                        approaching_expectations="Names some parts",
                        below_expectations="Needs support",
                    )
                ],
            )
        ],
    )


def test_parse_json_to_curriculum_ignores_formatting() -> None:
    """Formatted JSON parses back to the original model shape."""
    document = sample_document()
    json_data = JSONTransformer().transform(document)
    formatted_json = json.dumps(json_data, indent=4)

    parsed = parse_json_to_curriculum(formatted_json)

    assert parsed == document


def test_verify_round_trip_returns_equivalent_result() -> None:
    """Round-trip verification succeeds for transformed curriculum JSON."""
    result = verify_round_trip(sample_document())

    assert result.is_equivalent is True
    assert result.differences == []
    assert result.parsed_document == sample_document()


def test_compare_reports_specific_nested_difference() -> None:
    """Comparison reports the path and values for nested changes."""
    original = sample_document()
    changed = original.model_copy(
        update={
            "strands": [
                original.strands[0].model_copy(
                    update={"strand_name": "Physical Science"}
                )
            ]
        },
        deep=True,
    )

    result = compare_curriculum_documents(original, changed)

    assert result.is_equivalent is False
    assert result.differences == [
        "$.strands[0].strand_name: original='Living Things' parsed='Physical Science'"
    ]


def test_verify_round_trip_reports_parse_errors() -> None:
    """Malformed JSON produces a failed verification result."""
    result = RoundTripVerifier().verify(sample_document(), "{not json")

    assert result.is_equivalent is False
    assert result.differences
    assert result.differences[0].startswith("parse error:")
