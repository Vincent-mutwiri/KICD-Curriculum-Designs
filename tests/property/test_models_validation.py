"""
Property tests for curriculum data model validation.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from curriculum_extractor.models import CurriculumDocument, GradeRange


def valid_curriculum_data() -> dict[str, Any]:
    """Return a valid curriculum payload that tests can mutate."""
    return {
        "subject": "Mathematics",
        "grade": 4,
        "year": 2024,
        "essence_statement": "Mathematics develops logical thinking.",
        "general_learning_outcomes": ["Apply mathematical ideas in daily life."],
        "strands": [
            {
                "strand_id": "1.0",
                "strand_name": "Numbers",
                "sub_strands": [
                    {
                        "sub_strand_id": "1.1",
                        "sub_strand_name": "Whole Numbers",
                        "topics": ["Counting"],
                        "specific_learning_outcomes": ["Count whole numbers."],
                        "suggested_learning_experiences": ["Use number cards."],
                        "key_inquiry_questions": ["How do we count objects?"],
                        "core_competencies": [
                            {
                                "competency": "Critical thinking",
                                "context": "Solving number problems.",
                            }
                        ],
                        "values": [{"value": "Respect", "context": "Taking turns."}],
                        "pcis": ["Life skills"],
                        "suggested_resources": ["Number cards"],
                        "assessment_methods": ["Observation"],
                    }
                ],
                "assessment_rubric": [
                    {
                        "criterion": "Counts whole numbers",
                        "exceeding_expectations": "Counts accurately and explains patterns.",
                        "meeting_expectations": "Counts accurately.",
                        "approaching_expectations": "Counts with occasional support.",
                        "below_expectations": "Needs support to count.",
                    }
                ],
            }
        ],
    }


def remove_path(data: dict[str, Any], path: tuple[str | int, ...]) -> None:
    """Remove a nested key from a curriculum payload."""
    current: Any = data
    for segment in path[:-1]:
        current = current[segment]
    del current[path[-1]]


required_field_paths = st.sampled_from(
    [
        ("subject",),
        ("grade",),
        ("year",),
        ("essence_statement",),
        ("general_learning_outcomes",),
        ("strands",),
        ("strands", 0, "strand_id"),
        ("strands", 0, "strand_name"),
        ("strands", 0, "sub_strands"),
        ("strands", 0, "assessment_rubric"),
        ("strands", 0, "sub_strands", 0, "sub_strand_id"),
        ("strands", 0, "sub_strands", 0, "sub_strand_name"),
        ("strands", 0, "sub_strands", 0, "topics"),
        ("strands", 0, "sub_strands", 0, "specific_learning_outcomes"),
        ("strands", 0, "sub_strands", 0, "suggested_learning_experiences"),
        ("strands", 0, "sub_strands", 0, "key_inquiry_questions"),
        ("strands", 0, "sub_strands", 0, "core_competencies"),
        ("strands", 0, "sub_strands", 0, "values"),
        ("strands", 0, "sub_strands", 0, "pcis"),
        ("strands", 0, "sub_strands", 0, "suggested_resources"),
        ("strands", 0, "sub_strands", 0, "assessment_methods"),
        ("strands", 0, "sub_strands", 0, "core_competencies", 0, "competency"),
        ("strands", 0, "sub_strands", 0, "core_competencies", 0, "context"),
        ("strands", 0, "sub_strands", 0, "values", 0, "value"),
        ("strands", 0, "sub_strands", 0, "values", 0, "context"),
        ("strands", 0, "assessment_rubric", 0, "criterion"),
        ("strands", 0, "assessment_rubric", 0, "exceeding_expectations"),
        ("strands", 0, "assessment_rubric", 0, "meeting_expectations"),
        ("strands", 0, "assessment_rubric", 0, "approaching_expectations"),
        ("strands", 0, "assessment_rubric", 0, "below_expectations"),
    ]
)


@given(path=required_field_paths)
def test_property_17_validation_detects_missing_required_fields(
    path: tuple[str | int, ...],
) -> None:
    data = valid_curriculum_data()
    remove_path(data, path)

    with pytest.raises(ValidationError):
        CurriculumDocument.model_validate(data)


@given(grade=st.integers().filter(lambda value: value < 1 or value > 12))
def test_property_17_validation_detects_invalid_curriculum_grades(grade: int) -> None:
    data = valid_curriculum_data()
    data["grade"] = grade

    with pytest.raises(ValidationError):
        CurriculumDocument.model_validate(data)


@pytest.mark.parametrize("grade", [0, 13])
def test_property_17_curriculum_grade_boundary_rejects_invalid_edges(grade: int) -> None:
    data = valid_curriculum_data()
    data["grade"] = grade

    with pytest.raises(ValidationError):
        CurriculumDocument.model_validate(data)


@pytest.mark.parametrize("grade", [1, 12])
def test_property_17_curriculum_grade_boundary_accepts_valid_edges(grade: int) -> None:
    data = valid_curriculum_data()
    data["grade"] = grade

    assert CurriculumDocument.model_validate(data).grade == grade


@given(year=st.integers().filter(lambda value: value < 1900 or value > 2100))
def test_property_17_validation_detects_invalid_years(year: int) -> None:
    data = valid_curriculum_data()
    data["year"] = year

    with pytest.raises(ValidationError):
        CurriculumDocument.model_validate(data)


@pytest.mark.parametrize("year", [1899, 2101])
def test_property_17_year_boundary_rejects_invalid_edges(year: int) -> None:
    data = valid_curriculum_data()
    data["year"] = year

    with pytest.raises(ValidationError):
        CurriculumDocument.model_validate(data)


@pytest.mark.parametrize("year", [1900, 2100])
def test_property_17_year_boundary_accepts_valid_edges(year: int) -> None:
    data = valid_curriculum_data()
    data["year"] = year

    assert CurriculumDocument.model_validate(data).year == year


def test_property_17_validation_detects_empty_strands_array() -> None:
    data = valid_curriculum_data()
    data["strands"] = []

    with pytest.raises(ValidationError):
        CurriculumDocument.model_validate(data)


@given(duplicate_id=st.text(min_size=1))
def test_property_17_validation_detects_duplicate_strand_ids(duplicate_id: str) -> None:
    data = valid_curriculum_data()
    duplicate_strand = deepcopy(data["strands"][0])
    data["strands"][0]["strand_id"] = duplicate_id
    duplicate_strand["strand_id"] = duplicate_id
    data["strands"].append(duplicate_strand)

    with pytest.raises(ValidationError):
        CurriculumDocument.model_validate(data)


@given(duplicate_id=st.text(min_size=1))
def test_property_17_validation_detects_duplicate_sub_strand_ids(duplicate_id: str) -> None:
    data = valid_curriculum_data()
    sub_strands = data["strands"][0]["sub_strands"]
    duplicate_sub_strand = deepcopy(sub_strands[0])
    sub_strands[0]["sub_strand_id"] = duplicate_id
    duplicate_sub_strand["sub_strand_id"] = duplicate_id
    sub_strands.append(duplicate_sub_strand)

    with pytest.raises(ValidationError):
        CurriculumDocument.model_validate(data)


@pytest.mark.parametrize(
    ("start", "end"),
    [
        (0, 1),
        (1, 13),
        (12, 1),
    ],
)
def test_property_17_grade_range_rejects_invalid_boundaries(start: int, end: int) -> None:
    with pytest.raises(ValidationError):
        GradeRange.model_validate({"start": start, "end": end})


@pytest.mark.parametrize(
    ("start", "end"),
    [
        (1, 1),
        (1, 12),
        (12, 12),
    ],
)
def test_property_17_grade_range_accepts_valid_boundaries(start: int, end: int) -> None:
    grade_range = GradeRange.model_validate({"start": start, "end": end})

    assert grade_range.start == start
    assert grade_range.end == end
