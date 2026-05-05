"""Integration tests for CLI interface."""
import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def sample_markdown(tmp_path):
    """Create a sample markdown file."""
    content = """# Mathematics Grade 3 2024

## Essence Statement
Learn basic mathematics concepts.

## General Learning Outcomes
- Count numbers
- Add and subtract

## STRAND 1: NUMBERS

### 1.1 Whole Numbers

**Specific Learning Outcomes:**
- Count from 1 to 100

**Suggested Learning Experiences:**
- Use counters

**Key Inquiry Questions:**
- How do we count?

**Core Competencies:**
- Critical thinking: Problem solving

**Values:**
- Respect: Working together

**PCIs:**
- Numeracy

**Suggested Resources:**
- Number charts

**Assessment Methods:**
- Observation

## Assessment Rubric

| Criterion | Exceeding | Meeting | Approaching | Below |
|-----------|-----------|---------|-------------|-------|
| Counting  | 1-200     | 1-100   | 1-50        | 1-10  |
"""
    md_file = tmp_path / "test.md"
    md_file.write_text(content)
    return md_file


@pytest.fixture
def sample_config(tmp_path):
    """Create a sample config file."""
    config = {
        "preserve_essence_statement": True,
        "preserve_general_outcomes": True,
        "pretty_print": True,
        "indent_size": 2,
    }
    config_file = tmp_path / "config.yaml"
    import yaml
    config_file.write_text(yaml.dump(config))
    return config_file


def run_cli(*args):
    """Run CLI and return result."""
    result = subprocess.run(
        [sys.executable, "-m", "curriculum_extractor.cli", *args],
        capture_output=True,
        text=True,
    )
    return result


class TestCLI:
    """Test CLI interface."""

    def test_cli_single_file(self, sample_markdown, tmp_path):
        """Test CLI with single file input."""
        output = tmp_path / "output.json"
        result = run_cli(str(sample_markdown), "-o", str(output))

        assert result.returncode == 0
        assert "Success" in result.stdout
        assert output.exists()

        # Verify JSON content
        data = json.loads(output.read_text())
        assert data["subject"] == "Mathematics"
        assert data["grade"] == 3
        assert data["year"] == 2024

    def test_cli_directory_input(self, tmp_path):
        """Test CLI with directory input."""
        # Create multiple markdown files
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"

        for i in range(2):
            md_file = input_dir / f"test{i}.md"
            md_file.write_text(f"""# Subject{i} Grade {i+1} 2024

## STRAND 1: TEST STRAND

### 1.1 Sub-strand

**Specific Learning Outcomes:**
- Outcome {i}

**Suggested Learning Experiences:**
- Experience {i}

**Key Inquiry Questions:**
- Question {i}?

**Core Competencies:**
- Competency: Context

**Values:**
- Value: Context

**PCIs:**
- PCI

**Suggested Resources:**
- Resource

**Assessment Methods:**
- Method
""")

        result = run_cli(str(input_dir), "-o", str(output_dir))

        assert result.returncode == 0
        assert "Success" in result.stdout or "Partial" in result.stdout
        assert output_dir.exists()

    def test_cli_with_config_file(self, sample_markdown, sample_config, tmp_path):
        """Test CLI with configuration file."""
        output = tmp_path / "output.json"
        result = run_cli(
            str(sample_markdown),
            "-o", str(output),
            "-c", str(sample_config)
        )

        assert result.returncode == 0
        assert output.exists()

    def test_cli_with_verbose_option(self, sample_markdown, tmp_path):
        """Test CLI with verbose mode."""
        output = tmp_path / "output.json"
        result = run_cli(str(sample_markdown), "-o", str(output), "-v")

        assert result.returncode == 0
        assert "Processing file" in result.stdout

    def test_cli_with_pretty_print_option(self, sample_markdown, tmp_path):
        """Test CLI with pretty print option."""
        output = tmp_path / "output.json"
        result = run_cli(str(sample_markdown), "-o", str(output), "--pretty-print")

        assert result.returncode == 0
        assert output.exists()

    def test_cli_with_preserve_options(self, sample_markdown, tmp_path):
        """Test CLI with preserve options."""
        output = tmp_path / "output.json"
        result = run_cli(
            str(sample_markdown),
            "-o", str(output),
            "--preserve-essence",
            "--preserve-outcomes"
        )

        assert result.returncode == 0
        assert output.exists()

        data = json.loads(output.read_text())
        assert data["essence_statement"]
        assert data["general_learning_outcomes"]

    def test_cli_with_mongodb_script_option(self, sample_markdown, tmp_path):
        """Test CLI with MongoDB script option."""
        output = tmp_path / "output.json"
        result = run_cli(str(sample_markdown), "-o", str(output), "--mongodb-script")

        assert result.returncode == 0
        assert output.exists()

    def test_cli_missing_input_file(self):
        """Test CLI with missing input file."""
        result = run_cli("nonexistent.md")

        assert result.returncode == 1
        assert "does not exist" in result.stderr

    def test_cli_invalid_config_file(self, sample_markdown):
        """Test CLI with invalid config file."""
        result = run_cli(str(sample_markdown), "-c", "nonexistent.yaml")

        assert result.returncode == 1
        assert "Error loading config" in result.stderr

    def test_cli_help_message(self):
        """Test CLI help message."""
        result = run_cli("--help")

        assert result.returncode == 0
        assert "Extract and transform curriculum" in result.stdout
        assert "--output" in result.stdout
        assert "--config" in result.stdout
        assert "--verbose" in result.stdout

    def test_cli_no_output_specified(self, sample_markdown):
        """Test CLI without output path."""
        result = run_cli(str(sample_markdown))

        # Should succeed but not write file
        assert result.returncode == 0
        assert "Success" in result.stdout
