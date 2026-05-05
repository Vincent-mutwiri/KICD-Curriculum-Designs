"""Unit tests for DataValidator."""

import pytest

from curriculum_extractor import DataValidator


class TestDataValidator:
    """Test suite for DataValidator."""

    @pytest.fixture
    def validator(self):
        """Create a DataValidator instance."""
        return DataValidator()

    @pytest.fixture
    def valid_document(self):
        """Create a valid curriculum document."""
        return {
            "subject": "Mathematics",
            "grade": 5,
            "year": 2024,
            "essence_statement": "Mathematics develops logical thinking",
            "general_learning_outcomes": ["Outcome 1"],
            "strands": [
                {
                    "strand_id": "S1",
                    "strand_name": "Numbers",
                    "sub_strands": [
                        {
                            "sub_strand_id": "SS1",
                            "sub_strand_name": "Counting",
                            "topics": ["Topic 1"],
                            "specific_learning_outcomes": ["Outcome 1"],
                            "suggested_learning_experiences": ["Experience 1"],
                            "key_inquiry_questions": ["Question 1"],
                            "core_competencies": [{"competency": "Critical thinking", "context": "Context"}],
                            "values": [{"value": "Respect", "context": "Context"}],
                            "pcis": ["PCI 1"],
                            "suggested_resources": ["Resource 1"],
                            "assessment_methods": ["Method 1"],
                        }
                    ],
                    "assessment_rubric": [
                        {
                            "criterion": "Criterion 1",
                            "exceeding_expectations": "Exceeds",
                            "meeting_expectations": "Meets",
                            "approaching_expectations": "Approaches",
                            "below_expectations": "Below",
                        }
                    ],
                }
            ],
        }

    def test_validate_valid_document(self, validator, valid_document):
        """Test validation of a valid document."""
        result = validator.validate(valid_document)
        assert result.is_valid
        assert result.errors == []

    def test_validate_missing_subject(self, validator, valid_document):
        """Test detection of missing subject."""
        del valid_document["subject"]
        result = validator.validate(valid_document)
        assert not result.is_valid
        assert any("subject" in err for err in result.errors)

    def test_validate_missing_grade(self, validator, valid_document):
        """Test detection of missing grade."""
        del valid_document["grade"]
        result = validator.validate(valid_document)
        assert not result.is_valid
        assert any("grade" in err for err in result.errors)

    def test_validate_invalid_grade_low(self, validator, valid_document):
        """Test detection of grade below valid range."""
        valid_document["grade"] = 0
        result = validator.validate(valid_document)
        assert not result.is_valid
        assert any("grade" in err and "between 1 and 12" in err for err in result.errors)

    def test_validate_invalid_grade_high(self, validator, valid_document):
        """Test detection of grade above valid range."""
        valid_document["grade"] = 13
        result = validator.validate(valid_document)
        assert not result.is_valid
        assert any("grade" in err and "between 1 and 12" in err for err in result.errors)

    def test_validate_invalid_year_low(self, validator, valid_document):
        """Test detection of year below valid range."""
        valid_document["year"] = 1899
        result = validator.validate(valid_document)
        assert not result.is_valid
        assert any("year" in err and "between 1900 and 2100" in err for err in result.errors)

    def test_validate_invalid_year_high(self, validator, valid_document):
        """Test detection of year above valid range."""
        valid_document["year"] = 2101
        result = validator.validate(valid_document)
        assert not result.is_valid
        assert any("year" in err and "between 1900 and 2100" in err for err in result.errors)

    def test_validate_duplicate_strand_ids(self, validator, valid_document):
        """Test detection of duplicate strand IDs."""
        valid_document["strands"].append(valid_document["strands"][0].copy())
        result = validator.validate(valid_document)
        assert not result.is_valid
        assert any("strand_id" in err and "unique" in err for err in result.errors)

    def test_validate_duplicate_substrand_ids(self, validator, valid_document):
        """Test detection of duplicate sub-strand IDs within a strand."""
        valid_document["strands"][0]["sub_strands"].append(
            valid_document["strands"][0]["sub_strands"][0].copy()
        )
        result = validator.validate(valid_document)
        assert not result.is_valid
        assert any("sub_strand_id" in err and "unique" in err for err in result.errors)

    def test_validate_metadata_valid(self, validator):
        """Test validation of valid metadata."""
        result = validator.validate_metadata("Mathematics", 5, 2024)
        assert result.is_valid
        assert result.errors == []

    def test_validate_metadata_empty_subject(self, validator):
        """Test detection of empty subject."""
        result = validator.validate_metadata("", 5, 2024)
        assert not result.is_valid
        assert any("subject" in err for err in result.errors)

    def test_validate_metadata_invalid_grade(self, validator):
        """Test detection of invalid grade in metadata."""
        result = validator.validate_metadata("Mathematics", 0, 2024)
        assert not result.is_valid
        assert any("grade" in err for err in result.errors)

    def test_validate_metadata_invalid_year(self, validator):
        """Test detection of invalid year in metadata."""
        result = validator.validate_metadata("Mathematics", 5, 1800)
        assert not result.is_valid
        assert any("year" in err for err in result.errors)

    def test_validate_strands_valid(self, validator):
        """Test validation of valid strands."""
        strands = [{"strand_id": "S1", "strand_name": "Numbers"}]
        result = validator.validate_strands(strands)
        assert result.is_valid
        assert result.errors == []

    def test_validate_strands_empty(self, validator):
        """Test detection of empty strands list."""
        result = validator.validate_strands([])
        assert not result.is_valid
        assert any("strands" in err for err in result.errors)

    def test_validate_strands_missing_id(self, validator):
        """Test detection of missing strand ID."""
        strands = [{"strand_name": "Numbers"}]
        result = validator.validate_strands(strands)
        assert not result.is_valid
        assert any("strand_id" in err for err in result.errors)

    def test_validate_strands_missing_name(self, validator):
        """Test detection of missing strand name."""
        strands = [{"strand_id": "S1"}]
        result = validator.validate_strands(strands)
        assert not result.is_valid
        assert any("strand_name" in err for err in result.errors)

    def test_validate_uniqueness_valid(self, validator, valid_document):
        """Test validation of unique IDs."""
        result = validator.validate_uniqueness(valid_document)
        assert result.is_valid
        assert result.errors == []

    def test_validate_uniqueness_duplicate_strands(self, validator, valid_document):
        """Test detection of duplicate strand IDs."""
        valid_document["strands"].append(
            {"strand_id": "S1", "strand_name": "Duplicate", "sub_strands": []}
        )
        result = validator.validate_uniqueness(valid_document)
        assert not result.is_valid
        assert any("strand_id" in err and "unique" in err for err in result.errors)

    def test_validate_uniqueness_duplicate_substrands(self, validator, valid_document):
        """Test detection of duplicate sub-strand IDs."""
        valid_document["strands"][0]["sub_strands"].append(
            {"sub_strand_id": "SS1", "sub_strand_name": "Duplicate"}
        )
        result = validator.validate_uniqueness(valid_document)
        assert not result.is_valid
        assert any("sub_strand_id" in err and "unique" in err for err in result.errors)
