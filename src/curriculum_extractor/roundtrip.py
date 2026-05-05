"""Round-trip verification for transformed curriculum JSON."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from pydantic import ValidationError

from .json_transformer import JSONTransformer
from .models import CurriculumDocument

JsonInput = str | bytes | bytearray | Mapping[str, Any]


@dataclass(frozen=True)
class RoundTripResult:
    """Result of comparing an original document with re-parsed JSON."""

    is_equivalent: bool
    differences: list[str] = field(default_factory=list)
    parsed_document: CurriculumDocument | None = None


class RoundTripVerifier:
    """Verify that transformed JSON can be parsed back without data loss."""

    def __init__(self, transformer: JSONTransformer | None = None) -> None:
        self.transformer = transformer or JSONTransformer()

    def parse_json(self, json_data: JsonInput) -> CurriculumDocument:
        """Parse JSON data back into a CurriculumDocument."""
        if isinstance(json_data, str | bytes | bytearray):
            data = json.loads(json_data)
        else:
            data = dict(json_data)

        return CurriculumDocument.model_validate(data)

    def compare(
        self,
        original: CurriculumDocument | Mapping[str, Any],
        parsed: CurriculumDocument | Mapping[str, Any],
    ) -> RoundTripResult:
        """Compare two curriculum documents and report path-level differences."""
        try:
            original_doc = self._as_document(original)
            parsed_doc = self._as_document(parsed)
        except ValidationError as exc:
            return RoundTripResult(
                is_equivalent=False,
                differences=[f"validation error: {exc}"],
            )

        differences = list(
            _diff_values(
                original_doc.model_dump(mode="json"),
                parsed_doc.model_dump(mode="json"),
            )
        )
        return RoundTripResult(
            is_equivalent=not differences,
            differences=differences,
            parsed_document=parsed_doc,
        )

    def verify(
        self,
        original: CurriculumDocument | Mapping[str, Any],
        json_data: JsonInput | None = None,
    ) -> RoundTripResult:
        """Transform or parse JSON, then compare with the original document."""
        try:
            original_doc = self._as_document(original)
            parsed_doc = (
                self.parse_json(json_data)
                if json_data is not None
                else self.parse_json(self.transformer.transform(original_doc))
            )
        except (TypeError, json.JSONDecodeError, ValidationError) as exc:
            return RoundTripResult(
                is_equivalent=False,
                differences=[f"parse error: {exc}"],
            )

        return self.compare(original_doc, parsed_doc)

    def _as_document(
        self,
        document: CurriculumDocument | Mapping[str, Any],
    ) -> CurriculumDocument:
        if isinstance(document, CurriculumDocument):
            return document
        return CurriculumDocument.model_validate(document)


def parse_json_to_curriculum(json_data: JsonInput) -> CurriculumDocument:
    """Parse transformed JSON back into a CurriculumDocument."""
    return RoundTripVerifier().parse_json(json_data)


def compare_curriculum_documents(
    original: CurriculumDocument | Mapping[str, Any],
    parsed: CurriculumDocument | Mapping[str, Any],
) -> RoundTripResult:
    """Compare two curriculum documents for data equivalence."""
    return RoundTripVerifier().compare(original, parsed)


def verify_round_trip(
    original: CurriculumDocument | Mapping[str, Any],
    json_data: JsonInput | None = None,
) -> RoundTripResult:
    """Verify that curriculum data survives JSON transformation and parsing."""
    return RoundTripVerifier().verify(original, json_data)


def _diff_values(left: Any, right: Any, path: str = "$") -> list[str]:
    if isinstance(left, dict) and isinstance(right, dict):
        differences: list[str] = []
        for key in sorted(left.keys() | right.keys()):
            child_path = f"{path}.{key}"
            if key not in left:
                differences.append(f"{child_path}: missing from original")
            elif key not in right:
                differences.append(f"{child_path}: missing from parsed")
            else:
                differences.extend(_diff_values(left[key], right[key], child_path))
        return differences

    if isinstance(left, list) and isinstance(right, list):
        differences = []
        if len(left) != len(right):
            differences.append(
                f"{path}: length differs, original={len(left)} parsed={len(right)}"
            )

        for index, (left_item, right_item) in enumerate(zip(left, right, strict=False)):
            differences.extend(_diff_values(left_item, right_item, f"{path}[{index}]"))
        return differences

    if left != right:
        return [f"{path}: original={left!r} parsed={right!r}"]

    return []
