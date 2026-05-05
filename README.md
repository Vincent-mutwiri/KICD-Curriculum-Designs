# Curriculum Data Extraction and Transformation Tool

A Python-based system designed to parse Kenyan curriculum markdown files and transform them into structured JSON documents suitable for MongoDB storage.

## Overview

This tool processes curriculum files organized by grade level (Grades 1-12) and subject, extracting essential curriculum elements while filtering extraneous content. It transforms markdown curriculum documents into structured JSON format that can be imported into MongoDB.

## Features

- **Markdown Parsing**: Parse complex markdown structures including tables, nested lists, and hierarchical content
- **Content Extraction**: Extract strands, sub-strands, learning outcomes, competencies, values, and assessment data
- **Data Transformation**: Convert extracted data into MongoDB-compatible JSON format
- **Data Validation**: Ensure completeness and correctness of extracted data using Pydantic v2
- **Batch Processing**: Process multiple curriculum files efficiently
- **Configurable**: Support for various configuration options to customize extraction behavior
- **Reporting**: Generate detailed processing logs and statistics

## Requirements

- Python 3.10 or higher
- Dependencies (automatically installed):
  - mistletoe >= 1.3.0 (markdown parsing)
  - pydantic >= 2.0.0 (data validation)
  - pyyaml >= 6.0 (configuration)

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd curriculum-extractor

# Install in development mode
pip install -e ".[dev]"
```

### For Production

```bash
pip install .
```

## Usage

### Command Line Interface

Process a single curriculum file:

```bash
curriculum-extractor input.md -o output.json
```

Process a directory of curriculum files:

```bash
curriculum-extractor input_directory/ -o output_directory/
```

With configuration file:

```bash
curriculum-extractor input.md -c config.yaml -o output.json
```

### Python API

```python
from curriculum_extractor import FileProcessor, Configuration

# Load configuration
config = Configuration.load("config.yaml")

# Process a single file
processor = FileProcessor(config)
result = processor.process_file("input.md")

# Process a directory
batch_result = processor.process_directory("input_directory/")
```

## Configuration

Create a `config.yaml` file to customize extraction behavior:

```yaml
preserve_essence_statement: true
preserve_general_outcomes: true
output_directory: "./output"
pretty_print: true
indent_size: 2
grade_range_strategy: "split"  # or "single"
mongodb_format: true
```

## Project Structure

```
curriculum-extractor/
├── src/
│   └── curriculum_extractor/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── parser.py
│       ├── extractors/
│       ├── transformers/
│       └── validators/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── property/
│   └── fixtures/
├── examples/
├── pyproject.toml
├── README.md
└── LICENSE
```

## Development

### Setup Development Environment

```bash
# Install with development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=curriculum_extractor --cov-report=html

# Run specific test types
pytest tests/unit/
pytest tests/integration/
pytest tests/property/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

## Architecture

The system follows a pipeline architecture with four main stages:

1. **Parse**: Read and parse markdown files using mistletoe
2. **Extract**: Identify and extract curriculum elements
3. **Transform**: Convert to JSON structure
4. **Validate**: Verify data quality and completeness

### Key Components

- **MarkdownParser**: Parse markdown files into AST
- **ContentFilter**: Remove extraneous content
- **MetadataExtractor**: Extract subject, grade, and year
- **StrandExtractor**: Extract strand information
- **SubStrandExtractor**: Extract sub-strand details
- **RubricExtractor**: Extract assessment rubrics
- **JSONTransformer**: Transform to JSON format
- **DataValidator**: Validate extracted data
- **FileProcessor**: Orchestrate the complete pipeline

## Testing Strategy

The project uses three types of tests:

1. **Unit Tests**: Test individual components and functions
2. **Integration Tests**: Test the complete pipeline end-to-end
3. **Property-Based Tests**: Verify universal correctness properties using Hypothesis

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please ensure:

- All tests pass
- Code is formatted with Black
- Type hints are included
- Documentation is updated

## Support

For issues, questions, or contributions, please open an issue on the project repository.
