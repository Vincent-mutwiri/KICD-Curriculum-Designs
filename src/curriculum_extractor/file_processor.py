"""File processing orchestration."""

import json
from pathlib import Path

from .config import Configuration
from .filter import ContentFilter
from .json_transformer import JSONTransformer
from .metadata import MetadataExtractor
from .models import CurriculumDocument
from .parser import MarkdownParser
from .rubric_extractor import RubricExtractor
from .strand_extractor import StrandExtractor
from .substrand_extractor import SubStrandExtractor
from .validator import DataValidator


class ProcessingResult:
    """Result of file processing."""

    def __init__(self, status: str, file_path: str = "", errors: list[str] = None, warnings: list[str] = None):
        self.status = status
        self.file_path = file_path
        self.errors = errors or []
        self.warnings = warnings or []
        self.files_processed = 0
        self.files_succeeded = 0
        self.files_failed = 0


class FileProcessor:
    """Orchestrates the complete curriculum extraction pipeline."""

    def __init__(self, config: Configuration = None):
        self.config = config or Configuration()
        self.parser = MarkdownParser()
        self.filter = ContentFilter(self.config)
        self.metadata_extractor = MetadataExtractor()
        self.strand_extractor = StrandExtractor(self.parser)
        self.substrand_extractor = SubStrandExtractor(self.parser)
        self.rubric_extractor = RubricExtractor(self.parser)
        self.transformer = JSONTransformer()
        self.validator = DataValidator()

    def process_file(self, input_path: str, output_path: str = None) -> ProcessingResult:
        """Process a single curriculum file."""
        try:
            # Parse
            with open(input_path, "r", encoding="utf-8") as f:
                content = f.read()
            doc = self.parser.parse_string(content)

            # Filter
            filtered = self.filter.filter_document(doc)

            # Extract metadata
            metadata_dict = self.metadata_extractor.extract_from_content(filtered)
            if not metadata_dict.get("subject") or not metadata_dict.get("grade") or not metadata_dict.get("year"):
                return ProcessingResult("failed", input_path, errors=["Missing required metadata fields"])

            # Extract essence statement and general outcomes from document
            essence_statement = ""
            general_outcomes = []
            
            for i, child in enumerate(filtered.children):
                if hasattr(child, "level") and child.level == 2:
                    heading_text = "".join(c.content if hasattr(c, "content") else "" for c in child.children).strip()
                    if "essence" in heading_text.lower():
                        # Get next paragraph
                        if i + 1 < len(filtered.children) and hasattr(filtered.children[i + 1], "children"):
                            essence_statement = "".join(c.content if hasattr(c, "content") else "" for c in filtered.children[i + 1].children).strip()
                    elif "general" in heading_text.lower() and "outcome" in heading_text.lower():
                        # Get next list
                        if i + 1 < len(filtered.children) and hasattr(filtered.children[i + 1], "children"):
                            for item in filtered.children[i + 1].children:
                                if hasattr(item, "children"):
                                    text = "".join(c.content if hasattr(c, "content") else "" for c in item.children).strip()
                                    if text:
                                        general_outcomes.append(text)

            # Extract strands
            strand_data_list = self.strand_extractor.extract_strands(filtered)

            # Extract all sub-strands and rubrics from the document
            all_sub_strands = self.substrand_extractor.extract_substrands(filtered)
            all_rubrics = self.rubric_extractor.extract_rubrics(filtered)

            # Build document - for now, put all sub-strands and rubrics in first strand
            # TODO: Properly associate sub-strands and rubrics with their strands
            strands = []
            for i, strand_data in enumerate(strand_data_list):
                strands.append({
                    "strand_id": strand_data.strand_id,
                    "strand_name": strand_data.strand_name,
                    "sub_strands": [ss.model_dump() for ss in all_sub_strands] if i == 0 else [],
                    "assessment_rubric": [r.model_dump() for r in all_rubrics] if i == 0 else [],
                })

            doc_dict = {
                "subject": metadata_dict["subject"],
                "grade": metadata_dict["grade"],
                "year": metadata_dict["year"],
                "essence_statement": essence_statement or "Not specified",
                "general_learning_outcomes": general_outcomes if general_outcomes else ["Not specified"],
                "strands": strands,
            }

            # Validate
            validation = self.validator.validate(doc_dict)
            if not validation.is_valid:
                return ProcessingResult("failed", input_path, errors=validation.errors)

            # Transform
            curriculum_doc = CurriculumDocument(**doc_dict)
            json_output = self.transformer.transform(curriculum_doc)

            # Write
            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(json_output, f, ensure_ascii=False, indent=2)

            result = ProcessingResult("success", input_path)
            result.files_processed = 1
            result.files_succeeded = 1
            return result

        except Exception as e:
            return ProcessingResult("failed", input_path, errors=[str(e)])

    def process_directory(self, input_dir: str, output_dir: str = None) -> ProcessingResult:
        """Process all markdown files in a directory."""
        input_path = Path(input_dir)
        output_path = Path(output_dir) if output_dir else None

        result = ProcessingResult("success")
        md_files = list(input_path.glob("**/*.md"))

        for md_file in md_files:
            result.files_processed += 1
            output_file = None
            if output_path:
                output_file = output_path / self.generate_output_filename(md_file.name)

            file_result = self.process_file(str(md_file), str(output_file) if output_file else None)

            if file_result.status == "success":
                result.files_succeeded += 1
            else:
                result.files_failed += 1
                result.errors.extend([f"{md_file.name}: {err}" for err in file_result.errors])

        if result.files_failed > 0:
            result.status = "partial"
        return result

    def generate_output_filename(self, input_filename: str) -> str:
        """Generate output filename from input filename."""
        return Path(input_filename).stem + ".json"
