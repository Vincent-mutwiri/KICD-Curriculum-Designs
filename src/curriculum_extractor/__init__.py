"""
Curriculum Data Extraction and Transformation Tool

A Python-based system designed to parse Kenyan curriculum markdown files
and transform them into structured JSON documents suitable for MongoDB storage.
"""

from curriculum_extractor.config import Configuration
from curriculum_extractor.file_processor import FileProcessor, ProcessingResult
from curriculum_extractor.filter import ContentFilter
from curriculum_extractor.json_transformer import JSONTransformer
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
from curriculum_extractor.mongodb_import import MongoDBImporter
from curriculum_extractor.parser import (
    MarkdownList,
    MarkdownListItem,
    MarkdownParser,
    MarkdownTable,
)
from curriculum_extractor.pretty_printer import PrettyPrinter
from curriculum_extractor.report_generator import BatchReport, FileReport, ReportGenerator
from curriculum_extractor.roundtrip import (
    RoundTripResult,
    RoundTripVerifier,
    compare_curriculum_documents,
    parse_json_to_curriculum,
    verify_round_trip,
)
from curriculum_extractor.rubric_extractor import RubricExtractor
from curriculum_extractor.strand_extractor import StrandData, StrandExtractor
from curriculum_extractor.substrand_extractor import SubStrandData, SubStrandExtractor
from curriculum_extractor.validator import DataValidator, ValidationResult

__version__ = "0.1.0"

__all__ = [
    "Competency",
    "Configuration",
    "ContentFilter",
    "CurriculumDocument",
    "DataValidator",
    "BatchReport",
    "FileProcessor",
    "FileReport",
    "GradeRange",
    "JSONTransformer",
    "MarkdownList",
    "MarkdownListItem",
    "MarkdownParser",
    "MarkdownTable",
    "MetadataExtractor",
    "MongoDBImporter",
    "PrettyPrinter",
    "ProcessingResult",
    "ReportGenerator",
    "RubricCriterion",
    "RubricExtractor",
    "RoundTripResult",
    "RoundTripVerifier",
    "Strand",
    "StrandData",
    "StrandExtractor",
    "SubStrand",
    "SubStrandData",
    "SubStrandExtractor",
    "ValidationResult",
    "Value",
    "compare_curriculum_documents",
    "parse_json_to_curriculum",
    "verify_round_trip",
]
