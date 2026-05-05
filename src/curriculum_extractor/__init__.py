"""
Curriculum Data Extraction and Transformation Tool

A Python-based system designed to parse Kenyan curriculum markdown files
and transform them into structured JSON documents suitable for MongoDB storage.
"""

from curriculum_extractor.config import Configuration
from curriculum_extractor.models import (
    Competency,
    CurriculumDocument,
    GradeRange,
    RubricCriterion,
    Strand,
    SubStrand,
    Value,
)
from curriculum_extractor.parser import MarkdownList, MarkdownListItem, MarkdownParser, MarkdownTable

__version__ = "0.1.0"

__all__ = [
    "Competency",
    "Configuration",
    "CurriculumDocument",
    "GradeRange",
    "MarkdownList",
    "MarkdownListItem",
    "MarkdownParser",
    "MarkdownTable",
    "RubricCriterion",
    "Strand",
    "SubStrand",
    "Value",
]
