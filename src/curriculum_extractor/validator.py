"""Data validation for curriculum documents."""

from pydantic import ValidationError

from .models import CurriculumDocument


class ValidationResult:
    """Result of document validation."""

    def __init__(self, is_valid: bool, errors: list[str]):
        self.is_valid = is_valid
        self.errors = errors


class DataValidator:
    """Validates curriculum documents."""

    def validate(self, data: dict) -> ValidationResult:
        """Validate complete curriculum document."""
        try:
            CurriculumDocument(**data)
            return ValidationResult(is_valid=True, errors=[])
        except ValidationError as e:
            errors = []
            for err in e.errors():
                loc = ".".join(str(x) for x in err['loc']) if err['loc'] else "document"
                errors.append(f"{loc}: {err['msg']}")
            return ValidationResult(is_valid=False, errors=errors)

    def validate_metadata(self, subject: str, grade: int, year: int) -> ValidationResult:
        """Validate metadata fields."""
        errors = []
        if not subject or not subject.strip():
            errors.append("subject: field required")
        if not 1 <= grade <= 12:
            errors.append("grade: grade must be between 1 and 12")
        if not 1900 <= year <= 2100:
            errors.append("year: year must be between 1900 and 2100")
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def validate_strands(self, strands: list[dict]) -> ValidationResult:
        """Validate strand structure."""
        errors = []
        if not strands:
            errors.append("strands: field required")
        for i, strand in enumerate(strands):
            if not strand.get("strand_id"):
                errors.append(f"strands[{i}].strand_id: field required")
            if not strand.get("strand_name"):
                errors.append(f"strands[{i}].strand_name: field required")
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def validate_uniqueness(self, data: dict) -> ValidationResult:
        """Check ID uniqueness."""
        errors = []
        strands = data.get("strands", [])
        strand_ids = [s.get("strand_id") for s in strands if s.get("strand_id")]
        if len(strand_ids) != len(set(strand_ids)):
            errors.append("strand_id: values must be unique within a document")
        
        for i, strand in enumerate(strands):
            sub_strands = strand.get("sub_strands", [])
            sub_strand_ids = [ss.get("sub_strand_id") for ss in sub_strands if ss.get("sub_strand_id")]
            if len(sub_strand_ids) != len(set(sub_strand_ids)):
                errors.append(f"strands[{i}].sub_strand_id: values must be unique within a strand")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
