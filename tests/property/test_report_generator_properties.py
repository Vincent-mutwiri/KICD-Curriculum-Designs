"""Property tests for processing report generation."""

from hypothesis import given
from hypothesis import strategies as st

from curriculum_extractor.report_generator import ReportGenerator


def list_of_strings(max_size: int = 5) -> st.SearchStrategy[list[str]]:
    """Generate small JSON-safe string lists."""
    return st.lists(st.text(min_size=1, max_size=12), max_size=max_size)


sub_strand_strategy = st.fixed_dictionaries(
    {
        "sub_strand_id": st.text(min_size=1, max_size=8),
        "sub_strand_name": st.text(min_size=1, max_size=20),
        "topics": list_of_strings(),
        "specific_learning_outcomes": list_of_strings(),
        "suggested_learning_experiences": list_of_strings(),
        "key_inquiry_questions": list_of_strings(),
        "core_competencies": st.lists(
            st.fixed_dictionaries(
                {
                    "competency": st.text(min_size=1, max_size=12),
                    "context": st.text(min_size=1, max_size=20),
                }
            ),
            max_size=5,
        ),
        "values": st.lists(
            st.fixed_dictionaries(
                {
                    "value": st.text(min_size=1, max_size=12),
                    "context": st.text(min_size=1, max_size=20),
                }
            ),
            max_size=5,
        ),
        "pcis": list_of_strings(),
        "suggested_resources": list_of_strings(),
        "assessment_methods": list_of_strings(),
    }
)


strand_strategy = st.fixed_dictionaries(
    {
        "strand_id": st.text(min_size=1, max_size=8),
        "strand_name": st.text(min_size=1, max_size=20),
        "sub_strands": st.lists(sub_strand_strategy, max_size=5),
        "assessment_rubric": st.lists(
            st.fixed_dictionaries(
                {
                    "criterion": st.text(min_size=1, max_size=12),
                    "exceeding_expectations": st.text(min_size=1, max_size=20),
                    "meeting_expectations": st.text(min_size=1, max_size=20),
                    "approaching_expectations": st.text(min_size=1, max_size=20),
                    "below_expectations": st.text(min_size=1, max_size=20),
                }
            ),
            max_size=5,
        ),
    }
)


curriculum_output_strategy = st.fixed_dictionaries(
    {
        "subject": st.text(min_size=1, max_size=20),
        "grade": st.integers(min_value=1, max_value=12),
        "year": st.integers(min_value=1900, max_value=2100),
        "essence_statement": st.text(min_size=1, max_size=40),
        "general_learning_outcomes": list_of_strings(),
        "strands": st.lists(strand_strategy, max_size=5),
    }
)


def expected_counts(output_data: dict) -> dict[str, int]:
    """Calculate expected element counts directly from output JSON."""
    strands = output_data["strands"]
    sub_strands = [
        sub_strand for strand in strands for sub_strand in strand["sub_strands"]
    ]
    return {
        "strands": len(strands),
        "sub_strands": len(sub_strands),
        "topics": sum(len(item["topics"]) for item in sub_strands),
        "specific_learning_outcomes": sum(
            len(item["specific_learning_outcomes"]) for item in sub_strands
        ),
        "suggested_learning_experiences": sum(
            len(item["suggested_learning_experiences"]) for item in sub_strands
        ),
        "key_inquiry_questions": sum(
            len(item["key_inquiry_questions"]) for item in sub_strands
        ),
        "core_competencies": sum(
            len(item["core_competencies"]) for item in sub_strands
        ),
        "values": sum(len(item["values"]) for item in sub_strands),
        "pcis": sum(len(item["pcis"]) for item in sub_strands),
        "suggested_resources": sum(
            len(item["suggested_resources"]) for item in sub_strands
        ),
        "assessment_methods": sum(
            len(item["assessment_methods"]) for item in sub_strands
        ),
        "assessment_rubric": sum(len(strand["assessment_rubric"]) for strand in strands),
        "general_learning_outcomes": len(output_data["general_learning_outcomes"]),
    }


@given(output_data=curriculum_output_strategy)
def test_property_20_processing_report_accuracy(output_data: dict) -> None:
    """
    Property 20: Processing Report Accuracy
    Validates: Requirements 22.1-22.6

    Given output JSON for a processed curriculum file,
    verify report counts match actual output JSON counts.
    """
    report = ReportGenerator().generate_file_report(
        {
            "status": "success",
            "input_file": "curriculum.md",
            "output_file": "curriculum.json",
            "output_data": output_data,
        }
    )

    assert report.element_counts == expected_counts(output_data)
