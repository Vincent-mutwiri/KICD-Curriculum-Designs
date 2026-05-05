"""Unit tests for Configuration Manager."""

import json
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from curriculum_extractor.config import Configuration


class TestConfiguration:
    """Test Configuration class."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = Configuration()
        assert config.preserve_essence_statement is True
        assert config.preserve_general_outcomes is True
        assert config.output_directory == "./output"
        assert config.pretty_print is True
        assert config.indent_size == 2
        assert config.grade_range_strategy == "split"
        assert config.mongodb_format is True

    def test_get_defaults(self) -> None:
        """Test get_defaults classmethod."""
        config = Configuration.get_defaults()
        assert isinstance(config, Configuration)
        assert config.preserve_essence_statement is True
        assert config.output_directory == "./output"

    def test_custom_values(self) -> None:
        """Test configuration with custom values."""
        config = Configuration(
            preserve_essence_statement=False,
            preserve_general_outcomes=False,
            output_directory="/custom/path",
            pretty_print=False,
            indent_size=4,
            grade_range_strategy="single",
            mongodb_format=False,
        )
        assert config.preserve_essence_statement is False
        assert config.preserve_general_outcomes is False
        assert config.output_directory == "/custom/path"
        assert config.pretty_print is False
        assert config.indent_size == 4
        assert config.grade_range_strategy == "single"
        assert config.mongodb_format is False

    def test_load_from_yaml(self, tmp_path: Path) -> None:
        """Test loading configuration from YAML file."""
        config_file = tmp_path / "config.yaml"
        config_data = {
            "preserve_essence_statement": False,
            "output_directory": "/test/output",
            "indent_size": 4,
            "grade_range_strategy": "single",
        }
        config_file.write_text(yaml.dump(config_data))

        config = Configuration.load(config_file)
        assert config.preserve_essence_statement is False
        assert config.output_directory == "/test/output"
        assert config.indent_size == 4
        assert config.grade_range_strategy == "single"
        # Check defaults for unspecified fields
        assert config.preserve_general_outcomes is True
        assert config.pretty_print is True

    def test_load_from_yml(self, tmp_path: Path) -> None:
        """Test loading configuration from .yml file."""
        config_file = tmp_path / "config.yml"
        config_data = {"output_directory": "/yml/test"}
        config_file.write_text(yaml.dump(config_data))

        config = Configuration.load(config_file)
        assert config.output_directory == "/yml/test"

    def test_load_from_json(self, tmp_path: Path) -> None:
        """Test loading configuration from JSON file."""
        config_file = tmp_path / "config.json"
        config_data = {
            "preserve_essence_statement": False,
            "output_directory": "/json/output",
            "indent_size": 3,
        }
        config_file.write_text(json.dumps(config_data))

        config = Configuration.load(config_file)
        assert config.preserve_essence_statement is False
        assert config.output_directory == "/json/output"
        assert config.indent_size == 3

    def test_load_empty_yaml(self, tmp_path: Path) -> None:
        """Test loading empty YAML file uses defaults."""
        config_file = tmp_path / "empty.yaml"
        config_file.write_text("")

        config = Configuration.load(config_file)
        assert config.preserve_essence_statement is True
        assert config.output_directory == "./output"

    def test_load_missing_file(self, tmp_path: Path) -> None:
        """Test loading non-existent file raises FileNotFoundError."""
        config_file = tmp_path / "nonexistent.yaml"
        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            Configuration.load(config_file)

    def test_load_unsupported_format(self, tmp_path: Path) -> None:
        """Test loading unsupported file format raises ValueError."""
        config_file = tmp_path / "config.txt"
        config_file.write_text("some content")

        with pytest.raises(ValueError, match="Unsupported file format"):
            Configuration.load(config_file)

    def test_invalid_indent_size_negative(self) -> None:
        """Test negative indent_size raises ValidationError."""
        with pytest.raises(ValidationError):
            Configuration(indent_size=-1)

    def test_invalid_indent_size_too_large(self) -> None:
        """Test indent_size > 8 raises ValidationError."""
        with pytest.raises(ValidationError):
            Configuration(indent_size=9)

    def test_valid_indent_size_boundary(self) -> None:
        """Test boundary values for indent_size."""
        config_min = Configuration(indent_size=0)
        assert config_min.indent_size == 0

        config_max = Configuration(indent_size=8)
        assert config_max.indent_size == 8

    def test_invalid_grade_range_strategy(self) -> None:
        """Test invalid grade_range_strategy raises ValidationError."""
        with pytest.raises(ValidationError):
            Configuration(grade_range_strategy="invalid")  # type: ignore

    def test_empty_output_directory(self) -> None:
        """Test empty output_directory raises ValidationError."""
        with pytest.raises(ValidationError, match="output_directory cannot be empty"):
            Configuration(output_directory="")

    def test_whitespace_output_directory(self) -> None:
        """Test whitespace-only output_directory raises ValidationError."""
        with pytest.raises(ValidationError, match="output_directory cannot be empty"):
            Configuration(output_directory="   ")

    def test_load_with_invalid_values(self, tmp_path: Path) -> None:
        """Test loading file with invalid values raises ValidationError."""
        config_file = tmp_path / "invalid.yaml"
        config_data = {"indent_size": 10, "grade_range_strategy": "invalid"}
        config_file.write_text(yaml.dump(config_data))

        with pytest.raises(ValidationError):
            Configuration.load(config_file)

    def test_load_with_path_string(self, tmp_path: Path) -> None:
        """Test loading configuration using string path."""
        config_file = tmp_path / "config.yaml"
        config_data = {"output_directory": "/string/path"}
        config_file.write_text(yaml.dump(config_data))

        config = Configuration.load(str(config_file))
        assert config.output_directory == "/string/path"

    def test_load_with_path_object(self, tmp_path: Path) -> None:
        """Test loading configuration using Path object."""
        config_file = tmp_path / "config.yaml"
        config_data = {"output_directory": "/path/object"}
        config_file.write_text(yaml.dump(config_data))

        config = Configuration.load(config_file)
        assert config.output_directory == "/path/object"
