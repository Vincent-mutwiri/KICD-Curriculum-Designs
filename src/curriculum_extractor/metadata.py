"""Metadata extraction from curriculum filenames and content."""

import re
from pathlib import Path
from typing import Optional

from mistletoe import Document

from curriculum_extractor.models import GradeRange


class MetadataExtractor:
    """Extract subject, grade, and year metadata from filenames and content."""

    YEAR_PATTERN = r"(?:19\d{2}|20\d{2}|2100)"

    def __init__(self) -> None:
        """Initialize the metadata extractor."""
        pass

    def extract_from_filename(self, filename: str) -> dict[str, Optional[str | int | GradeRange]]:
        """
        Extract metadata from filename patterns.

        Expected patterns:
        - Subject_Grade_Year.md
        - Subject Grade Year.md
        - Subject-Grade-Year.md
        """
        path = Path(filename)
        stem = path.stem
        
        # First find the year to avoid confusion with grade ranges
        year_match = re.search(rf"[\s_-]({self.YEAR_PATTERN})(?:[\s_-]|$)", stem)
        
        if year_match:
            # Only search for grade before the year
            stem_before_year = stem[:year_match.start()]
            grade_match = re.search(r"(?:Grade|Gredi|G)[\s_-]+(\d{1,2}(?:[\s_-]*(?:to|-)[\s_-]*\d{1,2})?)", stem_before_year, re.IGNORECASE)
            
            if grade_match:
                # Extract subject as everything before the grade pattern
                subject_end = grade_match.start()
                subject = stem_before_year[:subject_end].rstrip("_- ")
                
                return {
                    "subject": self.normalize_subject(subject),
                    "grade": self.parse_grade(grade_match.group(0)),
                    "year": int(year_match.group(1)),
                }
        
        return {"subject": None, "grade": None, "year": None}

    def extract_from_content(self, document: Document) -> dict[str, Optional[str | int | GradeRange]]:
        """Extract metadata from document headers."""
        metadata = {"subject": None, "grade": None, "year": None}
        
        for child in document.children:
            if hasattr(child, "level") and child.level == 1:
                text = self._get_heading_text(child)
                
                # Look for subject
                if "subject" in text.lower():
                    subject_match = re.search(r"subject[:\s]+(.+)", text, re.IGNORECASE)
                    if subject_match:
                        metadata["subject"] = self.normalize_subject(subject_match.group(1))
                
                # Look for grade
                if "grade" in text.lower() or "gredi" in text.lower():
                    grade = self.parse_grade(text)
                    if grade:
                        metadata["grade"] = grade
                
                # Look for year
                year_match = re.search(rf"\b({self.YEAR_PATTERN})\b", text)
                if year_match:
                    metadata["year"] = int(year_match.group(1))
        
        return metadata

    def normalize_subject(self, subject: str) -> str:
        """Normalize subject names to consistent format."""
        # Strip whitespace
        normalized = subject.strip()
        
        # Replace multiple spaces with single space
        normalized = re.sub(r"\s+", " ", normalized)
        
        # Title case
        normalized = normalized.title()
        
        return normalized

    def parse_grade(self, grade_str: str) -> Optional[int | GradeRange]:
        """
        Parse grade from various formats.

        Supports:
        - "Grade 10", "Gredi 10", "G 10"
        - "Grade 1-3", "Grade 1 to 3"
        - "10", "1-3"
        """
        # Extract numeric parts
        numbers = re.findall(r"\d+", grade_str)
        
        if not numbers:
            return None
        
        if len(numbers) == 1:
            return int(numbers[0])
        
        # Check if it's a valid grade range (both numbers should be 1-12)
        if len(numbers) >= 2:
            first = int(numbers[0])
            second = int(numbers[1])
            
            # If second number looks like a year, treat first as single grade
            if second >= 1900:
                return first if 1 <= first <= 12 else None
            
            # Otherwise try to create a range
            try:
                return GradeRange(start=first, end=second)
            except ValueError:
                return None
        
        return None

    def _parse_year(self, year_str: str) -> Optional[int]:
        """Parse year from string."""
        match = re.search(rf"\b({self.YEAR_PATTERN})\b", year_str)
        if match:
            return int(match.group(1))
        return None

    def _get_heading_text(self, heading) -> str:
        """Extract text content from a heading node."""
        if hasattr(heading, "children"):
            return "".join(
                child.content if hasattr(child, "content") else str(child)
                for child in heading.children
            )
        return ""
