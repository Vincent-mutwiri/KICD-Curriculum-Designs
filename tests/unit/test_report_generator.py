"""Unit tests for ReportGenerator."""

import json
from pathlib import Path

from curriculum_extractor import FileReport, ReportGenerator
from curriculum_extractor.file_processor import ProcessingResult


def sample_output(strand_count: int = 1, sub_strand_count: int = 1) -> dict:
    """Build representative curriculum output JSON."""
    return {
        "subject": "Mathematics",
        "grade": 4,
        "year": 2024,
        "essence_statement": "Learn mathematics",
        "general_learning_outcomes": ["count", "measure"],
        "strands": [
            {
                "strand_id": f"{strand_index + 1}.0",
                "strand_name": f"Strand {strand_index + 1}",
                "assessment_rubric": [
                    {
                        "criterion": "Accuracy",
                        "exceeding_expectations": "Excellent",
                        "meeting_expectations": "Good",
                        "approaching_expectations": "Fair",
                        "below_expectations": "Needs support",
                    }
                ],
                "sub_strands": [
                    {
                        "sub_strand_id": f"{strand_index + 1}.{sub_index + 1}",
                        "sub_strand_name": f"Sub {sub_index + 1}",
                        "topics": ["topic a", "topic b"],
                        "specific_learning_outcomes": ["outcome"],
                        "suggested_learning_experiences": ["experience"],
                        "key_inquiry_questions": ["question"],
                        "core_competencies": [
                            {"competency": "Communication", "context": "discussion"}
                        ],
                        "values": [{"value": "Respect", "context": "turn taking"}],
                        "pcis": ["Safety"],
                        "suggested_resources": ["Counters", "Charts"],
                        "assessment_methods": ["Observation"],
                    }
                    for sub_index in range(sub_strand_count)
                ],
            }
            for strand_index in range(strand_count)
        ],
    }


def test_generate_file_report_from_processing_result() -> None:
    """Test file report generation from a ProcessingResult object."""
    result = ProcessingResult(
        "success",
        "input.md",
        warnings=["minor warning"],
        errors=[],
    )
    result.output_path = "output.json"
    result.output_data = sample_output(strand_count=2, sub_strand_count=3)
    result.processing_time = 1.25

    report = ReportGenerator().generate_file_report(result)

    assert report.input_file == "input.md"
    assert report.output_file == "output.json"
    assert report.status == "success"
    assert report.warnings == ["minor warning"]
    assert report.errors == []
    assert report.processing_time == 1.25
    assert report.element_counts["strands"] == 2
    assert report.element_counts["sub_strands"] == 6
    assert report.element_counts["topics"] == 12
    assert report.element_counts["assessment_rubric"] == 2


def test_generate_file_report_from_mapping_with_explicit_output_data() -> None:
    """Test file report generation from dict-like processing data."""
    result = {
        "status": "failed",
        "input_file": "bad.md",
        "output_file": "bad.json",
        "warnings": [],
        "errors": ["validation failed"],
        "processing_time": 0.5,
    }

    report = ReportGenerator().generate_file_report(result, output_data=sample_output())

    assert report.status == "failed"
    assert report.input_file == "bad.md"
    assert report.output_file == "bad.json"
    assert report.errors == ["validation failed"]
    assert report.element_counts["strands"] == 1
    assert report.element_counts["sub_strands"] == 1


def test_generate_batch_report_calculates_aggregate_statistics() -> None:
    """Test batch report generation and aggregate statistics."""
    generator = ReportGenerator()
    success = generator.generate_file_report(
        {
            "status": "success",
            "input_file": "one.md",
            "output_file": "one.json",
            "processing_time": 1.0,
            "output_data": sample_output(strand_count=1, sub_strand_count=2),
        }
    )
    failure = FileReport(
        input_file="two.md",
        output_file="",
        status="failed",
        element_counts=generator.calculate_element_counts(None),
        errors=["parse failed"],
        processing_time=3.0,
    )

    report = generator.generate_batch_report([success, failure])

    assert report.status == "partial"
    assert report.files_processed == 2
    assert report.files_succeeded == 1
    assert report.files_failed == 1
    assert report.total_processing_time == 4.0
    assert report.average_processing_time == 2.0
    assert report.aggregate_element_counts["strands"] == 1
    assert report.aggregate_element_counts["sub_strands"] == 2
    assert report.errors == ["parse failed"]


def test_generate_empty_batch_report() -> None:
    """Test aggregate values for an empty batch."""
    report = ReportGenerator().generate_batch_report([])

    assert report.status == "success"
    assert report.files_processed == 0
    assert report.files_succeeded == 0
    assert report.files_failed == 0
    assert report.total_processing_time == 0.0
    assert report.average_processing_time == 0.0


def test_write_report_writes_valid_json(tmp_path: Path) -> None:
    """Test writing formatted JSON reports to disk."""
    generator = ReportGenerator(indent_size=4)
    report = generator.generate_file_report(
        {"status": "success", "input_file": "input.md", "output_data": sample_output()}
    )
    output_path = tmp_path / "reports" / "report.json"

    generator.write_report(report, output_path)

    content = output_path.read_text(encoding="utf-8")
    loaded = json.loads(content)
    assert content.endswith("\n")
    assert '\n    "input_file"' in content
    assert loaded["input_file"] == "input.md"
    assert loaded["element_counts"]["strands"] == 1
