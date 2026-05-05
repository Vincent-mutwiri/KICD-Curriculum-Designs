"""Unit tests for PrettyPrinter."""

import json

import pytest

from curriculum_extractor import PrettyPrinter


class TestPrettyPrinter:
    """Test JSON pretty-printing and file writing."""

    def test_format_json_default_indentation(self):
        """Test default two-space indentation."""
        data = {"subject": "Mathematics", "grade": 1, "outcomes": ["Count", "Add"]}
        printer = PrettyPrinter()

        formatted = printer.format_json(data)

        assert json.loads(formatted) == data
        assert '\n  "subject": "Mathematics"' in formatted
        assert '\n    "Count"' in formatted

    @pytest.mark.parametrize("indent_size", [0, 2, 4, 8])
    def test_format_json_with_configurable_indentation(self, indent_size):
        """Test formatting with various indentation sizes."""
        data = {"strand": {"id": "1.0", "name": "Numbers"}}
        printer = PrettyPrinter(indent_size=indent_size)

        formatted = printer.format_json(data)

        assert json.loads(formatted) == data
        if indent_size > 0:
            assert f'\n{" " * indent_size}"strand"' in formatted

    def test_format_json_preserves_unicode(self):
        """Test Unicode characters are emitted directly and remain valid JSON."""
        data = {"subject": "Kiswahili", "outcome": "Kusoma na kuandika"}
        printer = PrettyPrinter()

        formatted = printer.format_json(data)

        assert "Kiswahili" in formatted
        assert json.loads(formatted) == data

    def test_write_json_writes_valid_utf8_file(self, tmp_path):
        """Test writing formatted JSON to a file."""
        data = {"subject": "Science", "resources": ["charts", "models"]}
        output_path = tmp_path / "nested" / "curriculum.json"
        printer = PrettyPrinter(indent_size=4)

        printer.write_json(data, output_path)

        written = output_path.read_text(encoding="utf-8")
        assert json.loads(written) == data
        assert '\n    "subject": "Science"' in written
        assert written.endswith("\n")

    def test_invalid_indent_size_raises_value_error(self):
        """Test negative indentation is rejected."""
        with pytest.raises(ValueError, match="indent_size"):
            PrettyPrinter(indent_size=-1)
