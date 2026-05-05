"""Pretty-print JSON output for curriculum documents."""

import json
from pathlib import Path
from typing import Any


class PrettyPrinter:
    """Format and write human-readable JSON."""

    def __init__(self, indent_size: int = 2):
        if indent_size < 0:
            raise ValueError("indent_size must be greater than or equal to 0")
        self.indent_size = indent_size

    def format_json(self, data: dict[str, Any] | list[Any]) -> str:
        """Format data as valid JSON using the configured indentation."""
        return json.dumps(
            data,
            ensure_ascii=False,
            indent=self.indent_size,
            sort_keys=False,
        )

    def write_json(self, data: dict[str, Any] | list[Any], output_path: str | Path) -> None:
        """Write formatted JSON data to a UTF-8 encoded file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{self.format_json(data)}\n", encoding="utf-8")
