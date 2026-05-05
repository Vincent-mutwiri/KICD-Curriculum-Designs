"""Integration tests for FileProcessor."""

import json
import tempfile
from pathlib import Path

import pytest

from curriculum_extractor import FileProcessor, Configuration


class TestFileProcessor:
    """Test suite for FileProcessor."""

    @pytest.fixture
    def processor(self):
        """Create a FileProcessor instance."""
        return FileProcessor()

    @pytest.fixture
    def sample_file(self):
        """Path to sample curriculum file."""
        return "tests/fixtures/sample_curriculum.md"

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_process_file_success(self, processor, sample_file, temp_dir):
        """Test successful processing of a single file."""
        output_file = Path(temp_dir) / "output.json"
        result = processor.process_file(sample_file, str(output_file))

        if result.status != "success":
            print(f"Errors: {result.errors}")
        assert result.status == "success"
        assert result.files_processed == 1
        assert result.files_succeeded == 1
        assert result.files_failed == 0
        assert len(result.errors) == 0
        assert output_file.exists()

        # Verify JSON structure
        with open(output_file) as f:
            data = json.load(f)
        assert data["subject"] == "Mathematics"
        assert data["grade"] == 5
        assert data["year"] == 2024
        assert len(data["strands"]) > 0

    def test_process_file_without_output(self, processor, sample_file):
        """Test processing without writing output."""
        result = processor.process_file(sample_file)

        assert result.status == "success"
        assert result.files_processed == 1
        assert result.files_succeeded == 1

    def test_process_file_invalid_path(self, processor):
        """Test processing with invalid file path."""
        result = processor.process_file("nonexistent.md")

        assert result.status == "failed"
        assert len(result.errors) > 0

    def test_process_directory_success(self, processor, temp_dir):
        """Test batch processing of directory."""
        # Create test files
        input_dir = Path(temp_dir) / "input"
        output_dir = Path(temp_dir) / "output"
        input_dir.mkdir()

        file1 = input_dir / "file1.md"
        file2 = input_dir / "file2.md"

        sample_content = """# Subject: Mathematics

# Grade 5

# Year: 2024

## Essence Statement
Test content

## General Learning Outcomes
- Outcome 1

## Strand 1: Numbers

### Sub-strand 1.1: Test

**Topics:** Topic 1
**Specific Learning Outcomes:** Outcome 1
**Suggested Learning Experiences:** Experience 1
**Key Inquiry Questions:** Question 1
**Core Competencies:** Critical thinking: Context
**Values:** Respect: Context
**PCIs:** PCI 1
**Suggested Resources:** Resource 1
**Assessment Methods:** Method 1

### Assessment Rubric

| Indicator | Exceeds Expectation | Meets Expectation | Approaches Expectation | Below Expectation |
|-----------|---------------------|-------------------|------------------------|-------------------|
| Test | Exceeds | Meets | Approaches | Below |
"""

        file1.write_text(sample_content)
        file2.write_text(sample_content)

        result = processor.process_directory(str(input_dir), str(output_dir))

        assert result.status == "success"
        assert result.files_processed == 2
        assert result.files_succeeded == 2
        assert result.files_failed == 0
        assert (output_dir / "file1.json").exists()
        assert (output_dir / "file2.json").exists()

    def test_process_directory_partial_failure(self, processor, temp_dir):
        """Test batch processing with some failures."""
        input_dir = Path(temp_dir) / "input"
        output_dir = Path(temp_dir) / "output"
        input_dir.mkdir()

        # Valid file
        valid_file = input_dir / "valid.md"
        valid_file.write_text("""# Subject: Mathematics

# Grade 5

# Year: 2024

## Essence Statement
Test

## General Learning Outcomes
- Outcome 1

## Strand 1: Numbers

### Sub-strand 1.1: Test

**Topics:** Topic 1
**Specific Learning Outcomes:** Outcome 1
**Suggested Learning Experiences:** Experience 1
**Key Inquiry Questions:** Question 1
**Core Competencies:** Critical thinking: Context
**Values:** Respect: Context
**PCIs:** PCI 1
**Suggested Resources:** Resource 1
**Assessment Methods:** Method 1

### Assessment Rubric

| Indicator | Exceeds Expectation | Meets Expectation | Approaches Expectation | Below Expectation |
|-----------|---------------------|-------------------|------------------------|-------------------|
| Test | Exceeds | Meets | Approaches | Below |
""")

        # Invalid file (missing required fields)
        invalid_file = input_dir / "invalid.md"
        invalid_file.write_text("# Invalid Content")

        result = processor.process_directory(str(input_dir), str(output_dir))

        assert result.status == "partial"
        assert result.files_processed == 2
        assert result.files_succeeded == 1
        assert result.files_failed == 1
        assert len(result.errors) > 0

    def test_generate_output_filename(self, processor):
        """Test output filename generation."""
        assert processor.generate_output_filename("test.md") == "test.json"
        assert processor.generate_output_filename("path/to/file.md") == "file.json"
        assert processor.generate_output_filename("grade5_math.md") == "grade5_math.json"

    def test_process_directory_without_output(self, processor, temp_dir):
        """Test batch processing without output directory."""
        input_dir = Path(temp_dir) / "input"
        input_dir.mkdir()

        file1 = input_dir / "file1.md"
        file1.write_text("""# Subject: Mathematics

# Grade 5

# Year: 2024

## Essence Statement
Test

## General Learning Outcomes
- Outcome 1

## Strand 1: Numbers

### Sub-strand 1.1: Test

**Topics:** Topic 1
**Specific Learning Outcomes:** Outcome 1
**Suggested Learning Experiences:** Experience 1
**Key Inquiry Questions:** Question 1
**Core Competencies:** Critical thinking: Context
**Values:** Respect: Context
**PCIs:** PCI 1
**Suggested Resources:** Resource 1
**Assessment Methods:** Method 1

### Assessment Rubric

| Indicator | Exceeds Expectation | Meets Expectation | Approaches Expectation | Below Expectation |
|-----------|---------------------|-------------------|------------------------|-------------------|
| Test | Exceeds | Meets | Approaches | Below |
""")

        result = processor.process_directory(str(input_dir))

        assert result.status == "success"
        assert result.files_processed == 1
        assert result.files_succeeded == 1
