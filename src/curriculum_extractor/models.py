"""
Pydantic models for structured curriculum documents.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CurriculumBaseModel(BaseModel):
    """Base model configuration shared by curriculum models."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Competency(CurriculumBaseModel):
    """Core competency with curriculum-specific context."""

    competency: str = Field(..., min_length=1)
    context: str = Field(..., min_length=1)


class Value(CurriculumBaseModel):
    """Curriculum value with curriculum-specific context."""

    value: str = Field(..., min_length=1)
    context: str = Field(..., min_length=1)


class SubStrand(CurriculumBaseModel):
    """A sub-strand in a curriculum strand."""

    sub_strand_id: str = Field(..., min_length=1)
    sub_strand_name: str = Field(..., min_length=1)
    topics: list[str]
    specific_learning_outcomes: list[str]
    suggested_learning_experiences: list[str]
    key_inquiry_questions: list[str]
    core_competencies: list[Competency]
    values: list[Value]
    pcis: list[str]
    suggested_resources: list[str]
    assessment_methods: list[str]


class RubricCriterion(CurriculumBaseModel):
    """Assessment rubric criterion with performance level descriptors."""

    criterion: str = Field(..., min_length=1)
    exceeding_expectations: str = Field(..., min_length=1)
    meeting_expectations: str = Field(..., min_length=1)
    approaching_expectations: str = Field(..., min_length=1)
    below_expectations: str = Field(..., min_length=1)


class Strand(CurriculumBaseModel):
    """A curriculum strand with sub-strands and assessment rubric entries."""

    strand_id: str = Field(..., min_length=1)
    strand_name: str = Field(..., min_length=1)
    sub_strands: list[SubStrand]
    assessment_rubric: list[RubricCriterion]

    @model_validator(mode="after")
    def validate_unique_sub_strand_ids(self) -> Strand:
        """Ensure sub-strand IDs are unique within a strand."""
        sub_strand_ids = [sub_strand.sub_strand_id for sub_strand in self.sub_strands]
        if len(sub_strand_ids) != len(set(sub_strand_ids)):
            raise ValueError("sub_strand_id values must be unique within a strand")
        return self


class GradeRange(CurriculumBaseModel):
    """Inclusive grade range for curriculum applicability."""

    start: int
    end: int

    @field_validator("start", "end")
    @classmethod
    def validate_grade_boundary(cls, grade: int) -> int:
        """Validate grades are in the Kenyan basic education range."""
        if not 1 <= grade <= 12:
            raise ValueError("grade must be between 1 and 12")
        return grade

    @model_validator(mode="after")
    def validate_range_order(self) -> GradeRange:
        """Ensure the grade range is ordered."""
        if self.start > self.end:
            raise ValueError("start grade must be less than or equal to end grade")
        return self


class CurriculumDocument(CurriculumBaseModel):
    """A complete extracted curriculum document."""

    subject: str = Field(..., min_length=1)
    grade: int
    year: int
    essence_statement: str = Field(..., min_length=1)
    general_learning_outcomes: list[str]
    strands: list[Strand] = Field(..., min_length=1)

    @field_validator("grade")
    @classmethod
    def validate_grade(cls, grade: int) -> int:
        """Validate document grade is in the supported range."""
        if not 1 <= grade <= 12:
            raise ValueError("grade must be between 1 and 12")
        return grade

    @field_validator("year")
    @classmethod
    def validate_year(cls, year: int) -> int:
        """Validate document year is in the supported range."""
        if not 1900 <= year <= 2100:
            raise ValueError("year must be between 1900 and 2100")
        return year

    @field_validator("strands")
    @classmethod
    def validate_strands_non_empty(cls, strands: list[Strand]) -> list[Strand]:
        """Ensure every curriculum document contains at least one strand."""
        if not strands:
            raise ValueError("strands must not be empty")
        return strands

    @model_validator(mode="after")
    def validate_unique_strand_ids(self) -> CurriculumDocument:
        """Ensure strand IDs are unique within a document."""
        strand_ids = [strand.strand_id for strand in self.strands]
        if len(strand_ids) != len(set(strand_ids)):
            raise ValueError("strand_id values must be unique within a document")
        return self
