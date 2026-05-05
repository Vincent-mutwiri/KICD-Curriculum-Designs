"""
Curriculum Data Extraction and Transformation Tool

A Python-based system designed to parse Kenyan curriculum markdown files
and transform them into structured JSON documents suitable for MongoDB storage.
"""

from curriculum_extractor.config import Configuration
from curriculum_extractor.filter import ContentFilter
from curriculum_extractor.metadata import MetadataExtractor
from curriculum_extractor.models import (
    Competency,
    CurriculumDocument,
    GradeRange,
    RubricCriterion,
    Strand,
    SubStrand,
    Value,
)
from curriculum_extractor.parser import (
    MarkdownList,
    MarkdownListItem,
    MarkdownParser,
    MarkdownTable,
)
from curriculum_extractor.rubric_extractor import RubricExtractor
from curriculum_extractor.strand_extractor import StrandData, StrandExtractor
from curriculum_extractor.substrand_extractor import SubStrandData, SubStrandExtractor

__version__ = "0.1.0"

__all__ = [
    "Competency",
    "Configuration",
    "ContentFilter",
    "CurriculumDocument",
    "GradeRange",
    "MarkdownList",
    "MarkdownListItem",
    "MarkdownParser",
    "MarkdownTable",
    "MetadataExtractor",
    "RubricCriterion",
    "RubricExtractor",
    "Strand",
    "StrandData",
    "StrandExtractor",
    "SubStrand",
    "SubStrandData",
    "SubStrandExtractor",
    "Value",
]
