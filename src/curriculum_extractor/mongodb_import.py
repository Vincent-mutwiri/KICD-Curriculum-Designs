"""MongoDB import support for curriculum documents."""

import json
from pathlib import Path
from typing import Optional


class MongoDBImporter:
    """Generate MongoDB import commands and scripts."""

    MAX_DOCUMENT_SIZE = 16 * 1024 * 1024  # 16MB in bytes

    def __init__(self, database: str = "curriculum", collection: str = "documents"):
        self.database = database
        self.collection = collection

    def generate_import_command(self, json_file: str, drop: bool = False) -> str:
        """Generate mongoimport command for a single file."""
        cmd = f"mongoimport --db {self.database} --collection {self.collection}"
        if drop:
            cmd += " --drop"
        cmd += f" --file {json_file}"
        return cmd

    def generate_batch_script(
        self, json_files: list[str], output_path: str, drop: bool = False
    ) -> str:
        """Generate shell script for batch import."""
        script_lines = ["#!/bin/bash", "set -e", ""]
        
        for json_file in json_files:
            cmd = self.generate_import_command(json_file, drop and json_files.index(json_file) == 0)
            script_lines.append(cmd)
        
        script_lines.append("")
        script = "\n".join(script_lines)
        
        Path(output_path).write_text(script)
        Path(output_path).chmod(0o755)
        
        return output_path

    def validate_document_size(self, json_file: str) -> tuple[bool, int]:
        """Check if document is within MongoDB size limit."""
        size = Path(json_file).stat().st_size
        return size <= self.MAX_DOCUMENT_SIZE, size

    def to_extended_json(self, data: dict) -> dict:
        """Convert to MongoDB extended JSON format."""
        # For now, just return as-is since we don't have special types
        # In future, could handle dates, ObjectIds, etc.
        return data
