"""Unit tests for MongoDB import support."""

import json
import tempfile
from pathlib import Path

import pytest

from curriculum_extractor import MongoDBImporter


class TestMongoDBImporter:
    """Test MongoDB import functionality."""

    @pytest.fixture
    def importer(self):
        """Create MongoDBImporter instance."""
        return MongoDBImporter(database="test_db", collection="test_collection")

    @pytest.fixture
    def sample_json_file(self):
        """Create a sample JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"subject": "Math", "grade": 5}, f)
            return f.name

    def test_generate_import_command(self, importer):
        """Test generating mongoimport command."""
        cmd = importer.generate_import_command("data.json")
        assert "mongoimport" in cmd
        assert "--db test_db" in cmd
        assert "--collection test_collection" in cmd
        assert "--file data.json" in cmd
        assert "--drop" not in cmd

    def test_generate_import_command_with_drop(self, importer):
        """Test generating mongoimport command with drop option."""
        cmd = importer.generate_import_command("data.json", drop=True)
        assert "--drop" in cmd

    def test_generate_batch_script(self, importer, sample_json_file):
        """Test generating batch import script."""
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = Path(tmpdir) / "import.sh"
            result = importer.generate_batch_script(
                [sample_json_file, "file2.json"], str(script_path)
            )
            
            assert result == str(script_path)
            assert script_path.exists()
            
            content = script_path.read_text()
            assert "#!/bin/bash" in content
            assert "set -e" in content
            assert "mongoimport" in content
            assert sample_json_file in content
            assert "file2.json" in content

    def test_generate_batch_script_drop_first_only(self, importer):
        """Test that drop flag only applies to first file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = Path(tmpdir) / "import.sh"
            importer.generate_batch_script(
                ["file1.json", "file2.json"], str(script_path), drop=True
            )
            
            content = script_path.read_text()
            lines = content.split("\n")
            
            # First mongoimport should have --drop
            first_import = [l for l in lines if "file1.json" in l][0]
            assert "--drop" in first_import
            
            # Second should not
            second_import = [l for l in lines if "file2.json" in l][0]
            assert "--drop" not in second_import

    def test_validate_document_size_within_limit(self, importer, sample_json_file):
        """Test document size validation for valid file."""
        valid, size = importer.validate_document_size(sample_json_file)
        assert valid is True
        assert size > 0
        assert size < MongoDBImporter.MAX_DOCUMENT_SIZE

    def test_validate_document_size_exceeds_limit(self, importer):
        """Test document size validation for oversized file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            # Create a file larger than 16MB
            large_data = {"data": "x" * (17 * 1024 * 1024)}
            json.dump(large_data, f)
            large_file = f.name
        
        valid, size = importer.validate_document_size(large_file)
        assert valid is False
        assert size > MongoDBImporter.MAX_DOCUMENT_SIZE
        
        Path(large_file).unlink()

    def test_to_extended_json(self, importer):
        """Test conversion to MongoDB extended JSON format."""
        data = {"subject": "Math", "grade": 5}
        result = importer.to_extended_json(data)
        assert result == data

    def test_default_database_and_collection(self):
        """Test default database and collection names."""
        importer = MongoDBImporter()
        assert importer.database == "curriculum"
        assert importer.collection == "documents"

    def test_script_is_executable(self, importer, sample_json_file):
        """Test that generated script has executable permissions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = Path(tmpdir) / "import.sh"
            importer.generate_batch_script([sample_json_file], str(script_path))
            
            # Check executable bit is set
            assert script_path.stat().st_mode & 0o111
