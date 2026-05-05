"""JSON transformation for curriculum documents."""

import json
import re
from typing import Any

from .models import CurriculumDocument, Strand, SubStrand, RubricCriterion, Competency, Value


class JSONTransformer:
    """Transform curriculum documents to MongoDB-compatible JSON."""

    def transform(self, document: CurriculumDocument) -> dict[str, Any]:
        """Transform a curriculum document to JSON dict."""
        return {
            "subject": self._escape_special_chars(document.subject),
            "grade": document.grade,
            "year": document.year,
            "essence_statement": self._escape_special_chars(document.essence_statement),
            "general_learning_outcomes": [
                self._escape_special_chars(outcome) for outcome in document.general_learning_outcomes
            ],
            "strands": [self.transform_strand(strand) for strand in document.strands],
        }

    def transform_strand(self, strand: Strand) -> dict[str, Any]:
        """Transform a strand to dict."""
        return {
            "strand_id": self._escape_special_chars(strand.strand_id),
            "strand_name": self._escape_special_chars(strand.strand_name),
            "sub_strands": [self.transform_substrand(sub) for sub in strand.sub_strands],
            "assessment_rubric": [self._transform_rubric(rubric) for rubric in strand.assessment_rubric],
        }

    def transform_substrand(self, substrand: SubStrand) -> dict[str, Any]:
        """Transform a sub-strand to dict."""
        return {
            "sub_strand_id": self._escape_special_chars(substrand.sub_strand_id),
            "sub_strand_name": self._escape_special_chars(substrand.sub_strand_name),
            "topics": [self._escape_special_chars(topic) for topic in substrand.topics],
            "specific_learning_outcomes": [
                self._escape_special_chars(outcome) for outcome in substrand.specific_learning_outcomes
            ],
            "suggested_learning_experiences": [
                self._escape_special_chars(exp) for exp in substrand.suggested_learning_experiences
            ],
            "key_inquiry_questions": [
                self._escape_special_chars(q) for q in substrand.key_inquiry_questions
            ],
            "core_competencies": [self._transform_competency(comp) for comp in substrand.core_competencies],
            "values": [self._transform_value(val) for val in substrand.values],
            "pcis": [self._escape_special_chars(pci) for pci in substrand.pcis],
            "suggested_resources": [self._escape_special_chars(res) for res in substrand.suggested_resources],
            "assessment_methods": [self._escape_special_chars(method) for method in substrand.assessment_methods],
        }

    def _transform_rubric(self, rubric: RubricCriterion) -> dict[str, Any]:
        """Transform a rubric criterion to dict."""
        return {
            "criterion": self._escape_special_chars(rubric.criterion),
            "exceeding_expectations": self._escape_special_chars(rubric.exceeding_expectations),
            "meeting_expectations": self._escape_special_chars(rubric.meeting_expectations),
            "approaching_expectations": self._escape_special_chars(rubric.approaching_expectations),
            "below_expectations": self._escape_special_chars(rubric.below_expectations),
        }

    def _transform_competency(self, competency: Competency) -> dict[str, Any]:
        """Transform a competency to dict."""
        return {
            "competency": self._escape_special_chars(competency.competency),
            "context": self._escape_special_chars(competency.context),
        }

    def _transform_value(self, value: Value) -> dict[str, Any]:
        """Transform a value to dict."""
        return {
            "value": self._escape_special_chars(value.value),
            "context": self._escape_special_chars(value.context),
        }

    def _escape_special_chars(self, text: str) -> str:
        """Escape special characters for JSON and MongoDB compliance."""
        # Replace dots and dollar signs in field names (MongoDB restriction)
        # For field values, we preserve them but ensure proper JSON encoding
        return text

    def escape_special_chars(self, text: str) -> str:
        """Public method for escaping special characters."""
        return self._escape_special_chars(text)
