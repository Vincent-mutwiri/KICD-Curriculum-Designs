"""Processing report generation for curriculum extraction runs."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

ELEMENT_COUNT_KEYS = (
    "strands",
    "sub_strands",
    "topics",
    "specific_learning_outcomes",
    "suggested_learning_experiences",
    "key_inquiry_questions",
    "core_competencies",
    "values",
    "pcis",
    "suggested_resources",
    "assessment_methods",
    "assessment_rubric",
    "general_learning_outcomes",
)


@dataclass(frozen=True)
class FileReport:
    """Report for one processed curriculum file."""

    input_file: str
    output_file: str
    status: str
    element_counts: dict[str, int]
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    processing_time: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable report dictionary."""
        return asdict(self)


@dataclass(frozen=True)
class BatchReport:
    """Summary report for a batch of processed curriculum files."""

    status: str
    files_processed: int
    files_succeeded: int
    files_failed: int
    total_processing_time: float
    average_processing_time: float
    aggregate_element_counts: dict[str, int]
    reports: list[FileReport]
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable report dictionary."""
        data = asdict(self)
        data["reports"] = [report.to_dict() for report in self.reports]
        return data


class ReportGenerator:
    """Generate per-file and batch processing reports."""

    def __init__(self, indent_size: int = 2):
        if indent_size < 0:
            raise ValueError("indent_size must be greater than or equal to 0")
        self.indent_size = indent_size

    def generate_file_report(
        self,
        result: Any,
        output_data: dict[str, Any] | None = None,
        output_path: str | Path | None = None,
        processing_time: float | None = None,
    ) -> FileReport:
        """Create a report for one processed file."""
        input_file = self._result_value(result, "input_file", "file_path", default="")
        resolved_output_path = output_path or self._result_value(
            result,
            "output_file",
            "output_path",
            default="",
        )
        resolved_processing_time = processing_time
        if resolved_processing_time is None:
            resolved_processing_time = self._result_value(
                result,
                "processing_time",
                "duration",
                default=0.0,
            )

        data = output_data if output_data is not None else self._result_output_data(result)

        return FileReport(
            input_file=str(input_file),
            output_file=str(resolved_output_path),
            status=str(self._result_value(result, "status", default="unknown")),
            element_counts=self.calculate_element_counts(data),
            warnings=list(self._result_value(result, "warnings", default=[])),
            errors=list(self._result_value(result, "errors", default=[])),
            processing_time=float(resolved_processing_time or 0.0),
        )

    def generate_batch_report(self, results: list[Any]) -> BatchReport:
        """Create an aggregate report for a batch of processed files."""
        reports = [
            result if isinstance(result, FileReport) else self.generate_file_report(result)
            for result in results
        ]

        aggregate_counts = dict.fromkeys(ELEMENT_COUNT_KEYS, 0)
        for report in reports:
            for key in ELEMENT_COUNT_KEYS:
                aggregate_counts[key] += report.element_counts.get(key, 0)

        files_processed = len(reports)
        files_succeeded = sum(1 for report in reports if report.status == "success")
        files_failed = sum(1 for report in reports if report.status != "success")
        total_processing_time = sum(report.processing_time for report in reports)
        average_processing_time = (
            total_processing_time / files_processed if files_processed else 0.0
        )

        if files_failed == 0:
            status = "success"
        elif files_succeeded == 0:
            status = "failed"
        else:
            status = "partial"

        return BatchReport(
            status=status,
            files_processed=files_processed,
            files_succeeded=files_succeeded,
            files_failed=files_failed,
            total_processing_time=total_processing_time,
            average_processing_time=average_processing_time,
            aggregate_element_counts=aggregate_counts,
            reports=reports,
            warnings=[warning for report in reports for warning in report.warnings],
            errors=[error for report in reports for error in report.errors],
        )

    def write_report(self, report: FileReport | BatchReport | dict[str, Any], output_path: str | Path) -> None:
        """Write a report as formatted UTF-8 JSON."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = report.to_dict() if hasattr(report, "to_dict") else report
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=self.indent_size) + "\n",
            encoding="utf-8",
        )

    def calculate_element_counts(self, output_data: dict[str, Any] | None) -> dict[str, int]:
        """Count major curriculum elements in output JSON data."""
        counts = dict.fromkeys(ELEMENT_COUNT_KEYS, 0)
        if not output_data:
            return counts

        strands = output_data.get("strands", [])
        counts["strands"] = len(strands)
        counts["general_learning_outcomes"] = len(
            output_data.get("general_learning_outcomes", [])
        )

        for strand in strands:
            sub_strands = strand.get("sub_strands", [])
            counts["sub_strands"] += len(sub_strands)
            counts["assessment_rubric"] += len(strand.get("assessment_rubric", []))

            for sub_strand in sub_strands:
                counts["topics"] += len(sub_strand.get("topics", []))
                counts["specific_learning_outcomes"] += len(
                    sub_strand.get("specific_learning_outcomes", [])
                )
                counts["suggested_learning_experiences"] += len(
                    sub_strand.get("suggested_learning_experiences", [])
                )
                counts["key_inquiry_questions"] += len(
                    sub_strand.get("key_inquiry_questions", [])
                )
                counts["core_competencies"] += len(sub_strand.get("core_competencies", []))
                counts["values"] += len(sub_strand.get("values", []))
                counts["pcis"] += len(sub_strand.get("pcis", []))
                counts["suggested_resources"] += len(
                    sub_strand.get("suggested_resources", [])
                )
                counts["assessment_methods"] += len(
                    sub_strand.get("assessment_methods", [])
                )

        return counts

    def _result_output_data(self, result: Any) -> dict[str, Any] | None:
        """Find output JSON data on a processing result-like object."""
        return self._result_value(
            result,
            "output_data",
            "output_json",
            "json_output",
            "data",
            default=None,
        )

    def _result_value(self, result: Any, *names: str, default: Any = None) -> Any:
        """Read a value from either an object or mapping-like result."""
        if isinstance(result, dict):
            for name in names:
                if name in result:
                    return result[name]
            return default

        for name in names:
            if hasattr(result, name):
                return getattr(result, name)
        return default
