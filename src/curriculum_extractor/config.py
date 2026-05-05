"""Configuration management for curriculum extractor."""

import json
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, field_validator


class Configuration(BaseModel):
    """Configuration for curriculum extraction and transformation."""

    preserve_essence_statement: bool = True
    preserve_general_outcomes: bool = True
    output_directory: str = "./output"
    pretty_print: bool = True
    indent_size: int = Field(default=2, ge=0, le=8)
    grade_range_strategy: Literal["split", "single"] = "split"
    mongodb_format: bool = True

    @field_validator("output_directory")
    @classmethod
    def validate_output_directory(cls, v: str) -> str:
        """Validate output directory path."""
        if not v or not v.strip():
            raise ValueError("output_directory cannot be empty")
        return v

    @classmethod
    def load(cls, path: str | Path) -> "Configuration":
        """Load configuration from YAML or JSON file."""
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        content = file_path.read_text()
        suffix = file_path.suffix.lower()

        data: dict[str, Any]
        if suffix in (".yaml", ".yml"):
            data = yaml.safe_load(content) or {}
        elif suffix == ".json":
            data = json.loads(content)
        else:
            raise ValueError(f"Unsupported file format: {suffix}. Use .yaml, .yml, or .json")

        return cls(**data)

    @classmethod
    def get_defaults(cls) -> "Configuration":
        """Get default configuration."""
        return cls()
