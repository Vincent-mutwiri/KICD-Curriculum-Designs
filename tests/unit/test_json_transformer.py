"""Unit tests for JSONTransformer."""

import json

import pytest

from curriculum_extractor import (
    Competency,
    CurriculumDocument,
    JSONTransformer,
    RubricCriterion,
    Strand,
    SubStrand,
    Value,
)


class TestJSONTransformer:
    """Test JSONTransformer class."""

    def test_transform_complete_document(self):
        """Test transformation of a complete curriculum document."""
        doc = CurriculumDocument(
            subject="Mathematics",
            grade=1,
            year=2024,
            essence_statement="Learn math",
            general_learning_outcomes=["Count", "Add"],
            strands=[
                Strand(
                    strand_id="1",
                    strand_name="Numbers",
                    sub_strands=[
                        SubStrand(
                            sub_strand_id="1.1",
                            sub_strand_name="Counting",
                            topics=["Numbers 1-10"],
                            specific_learning_outcomes=["Count to 10"],
                            suggested_learning_experiences=["Use counters"],
                            key_inquiry_questions=["How many?"],
                            core_competencies=[Competency(competency="Critical thinking", context="Counting")],
                            values=[Value(value="Respect", context="Sharing")],
                            pcis=["Numeracy"],
                            suggested_resources=["Counters"],
                            assessment_methods=["Observation"],
                        )
                    ],
                    assessment_rubric=[
                        RubricCriterion(
                            criterion="Counting",
                            exceeding_expectations="Counts beyond 10",
                            meeting_expectations="Counts to 10",
                            approaching_expectations="Counts to 5",
                            below_expectations="Cannot count",
                        )
                    ],
                )
            ],
        )

        transformer = JSONTransformer()
        result = transformer.transform(doc)

        assert result["subject"] == "Mathematics"
        assert result["grade"] == 1
        assert result["year"] == 2024
        assert result["essence_statement"] == "Learn math"
        assert result["general_learning_outcomes"] == ["Count", "Add"]
        assert len(result["strands"]) == 1

    def test_transform_strand(self):
        """Test transformation of a strand."""
        strand = Strand(
            strand_id="1",
            strand_name="Numbers",
            sub_strands=[],
            assessment_rubric=[],
        )

        transformer = JSONTransformer()
        result = transformer.transform_strand(strand)

        assert result["strand_id"] == "1"
        assert result["strand_name"] == "Numbers"
        assert result["sub_strands"] == []
        assert result["assessment_rubric"] == []

    def test_transform_substrand(self):
        """Test transformation of a sub-strand."""
        substrand = SubStrand(
            sub_strand_id="1.1",
            sub_strand_name="Counting",
            topics=["Numbers"],
            specific_learning_outcomes=["Count"],
            suggested_learning_experiences=["Practice"],
            key_inquiry_questions=["How?"],
            core_competencies=[],
            values=[],
            pcis=[],
            suggested_resources=[],
            assessment_methods=[],
        )

        transformer = JSONTransformer()
        result = transformer.transform_substrand(substrand)

        assert result["sub_strand_id"] == "1.1"
        assert result["sub_strand_name"] == "Counting"
        assert result["topics"] == ["Numbers"]
        assert result["specific_learning_outcomes"] == ["Count"]

    def test_special_character_escaping(self):
        """Test that special characters are handled correctly."""
        doc = CurriculumDocument(
            subject="Math & Science",
            grade=1,
            year=2024,
            essence_statement="Learn \"math\" & 'science'",
            general_learning_outcomes=["Count 1-10", "Add 2+2"],
            strands=[
                Strand(
                    strand_id="1",
                    strand_name="Numbers",
                    sub_strands=[],
                    assessment_rubric=[],
                )
            ],
        )

        transformer = JSONTransformer()
        result = transformer.transform(doc)

        # Verify special characters are preserved
        assert result["subject"] == "Math & Science"
        assert result["essence_statement"] == "Learn \"math\" & 'science'"
        assert result["general_learning_outcomes"][0] == "Count 1-10"

    def test_unicode_character_preservation(self):
        """Test that Unicode characters are preserved."""
        doc = CurriculumDocument(
            subject="Kiswahili",
            grade=1,
            year=2024,
            essence_statement="Kujifunza Kiswahili 🎓",
            general_learning_outcomes=["Soma", "Andika"],
            strands=[
                Strand(
                    strand_id="1",
                    strand_name="Kusoma",
                    sub_strands=[],
                    assessment_rubric=[],
                )
            ],
        )

        transformer = JSONTransformer()
        result = transformer.transform(doc)

        assert result["subject"] == "Kiswahili"
        assert result["essence_statement"] == "Kujifunza Kiswahili 🎓"
        assert result["general_learning_outcomes"] == ["Soma", "Andika"]

    def test_json_serializable(self):
        """Test that transformed output is JSON serializable."""
        doc = CurriculumDocument(
            subject="Mathematics",
            grade=1,
            year=2024,
            essence_statement="Learn math",
            general_learning_outcomes=["Count"],
            strands=[
                Strand(
                    strand_id="1",
                    strand_name="Numbers",
                    sub_strands=[],
                    assessment_rubric=[],
                )
            ],
        )

        transformer = JSONTransformer()
        result = transformer.transform(doc)

        # Should not raise an exception
        json_str = json.dumps(result, ensure_ascii=False)
        assert json_str is not None

        # Should be parseable
        parsed = json.loads(json_str)
        assert parsed["subject"] == "Mathematics"

    def test_mongodb_field_name_compliance(self):
        """Test that field names don't contain dots or dollar signs."""
        doc = CurriculumDocument(
            subject="Mathematics",
            grade=1,
            year=2024,
            essence_statement="Learn math",
            general_learning_outcomes=["Count"],
            strands=[
                Strand(
                    strand_id="1",
                    strand_name="Numbers",
                    sub_strands=[
                        SubStrand(
                            sub_strand_id="1.1",
                            sub_strand_name="Counting",
                            topics=[],
                            specific_learning_outcomes=[],
                            suggested_learning_experiences=[],
                            key_inquiry_questions=[],
                            core_competencies=[],
                            values=[],
                            pcis=[],
                            suggested_resources=[],
                            assessment_methods=[],
                        )
                    ],
                    assessment_rubric=[],
                )
            ],
        )

        transformer = JSONTransformer()
        result = transformer.transform(doc)

        # Check all field names recursively
        def check_field_names(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    assert "." not in key, f"Field name contains dot: {path}.{key}"
                    assert "$" not in key, f"Field name contains dollar sign: {path}.{key}"
                    check_field_names(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_field_names(item, f"{path}[{i}]")

        check_field_names(result)

    def test_empty_lists(self):
        """Test transformation with empty lists."""
        doc = CurriculumDocument(
            subject="Mathematics",
            grade=1,
            year=2024,
            essence_statement="Learn math",
            general_learning_outcomes=[],
            strands=[
                Strand(
                    strand_id="1",
                    strand_name="Numbers",
                    sub_strands=[],
                    assessment_rubric=[],
                )
            ],
        )

        transformer = JSONTransformer()
        result = transformer.transform(doc)

        assert result["general_learning_outcomes"] == []
        assert result["strands"][0]["sub_strands"] == []
        assert result["strands"][0]["assessment_rubric"] == []

    def test_transform_rubric_criterion(self):
        """Test transformation of rubric criterion."""
        rubric = RubricCriterion(
            criterion="Counting",
            exceeding_expectations="Counts beyond 10",
            meeting_expectations="Counts to 10",
            approaching_expectations="Counts to 5",
            below_expectations="Cannot count",
        )

        transformer = JSONTransformer()
        result = transformer._transform_rubric(rubric)

        assert result["criterion"] == "Counting"
        assert result["exceeding_expectations"] == "Counts beyond 10"
        assert result["meeting_expectations"] == "Counts to 10"
        assert result["approaching_expectations"] == "Counts to 5"
        assert result["below_expectations"] == "Cannot count"

    def test_transform_competency(self):
        """Test transformation of competency."""
        competency = Competency(competency="Critical thinking", context="Problem solving")

        transformer = JSONTransformer()
        result = transformer._transform_competency(competency)

        assert result["competency"] == "Critical thinking"
        assert result["context"] == "Problem solving"

    def test_transform_value(self):
        """Test transformation of value."""
        value = Value(value="Respect", context="Working together")

        transformer = JSONTransformer()
        result = transformer._transform_value(value)

        assert result["value"] == "Respect"
        assert result["context"] == "Working together"
