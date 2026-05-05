# Examples

This directory contains example files and usage patterns for the Curriculum Data Extractor.

## Configuration

- `config.example.yaml` - Example configuration file showing all available options

## Usage Examples

### Basic Usage

Process a single curriculum file:

```bash
curriculum-extractor "Grade_10/English Grade 10 - July 2025.md" -o output/english_grade_10.json
```

### Batch Processing

Process all files in a directory:

```bash
curriculum-extractor Grade_10/ -o output/
```

### With Configuration File

Use a custom configuration:

```bash
curriculum-extractor input.md -c config.yaml -o output.json
```

### Python API Usage

```python
from curriculum_extractor import FileProcessor, Configuration
from pathlib import Path

# Load configuration
config = Configuration.load("config.yaml")

# Process a single file
processor = FileProcessor(config)
result = processor.process_file(Path("input.md"))

if result.success:
    print(f"Successfully processed: {result.output_path}")
    print(f"Extracted {result.strand_count} strands")
else:
    print(f"Processing failed: {result.error}")

# Process a directory
batch_result = processor.process_directory(Path("Grade_10/"))
print(f"Processed {batch_result.success_count}/{batch_result.total_count} files")
```

## Sample Data

Sample curriculum files and expected outputs will be added here for testing and demonstration purposes.

### Directory Structure

```
examples/
├── README.md                    # This file
├── config.example.yaml          # Example configuration
├── sample_input/                # Sample curriculum markdown files
│   └── (to be added)
├── expected_output/             # Expected JSON outputs
│   └── (to be added)
└── scripts/                     # Example scripts
    └── (to be added)
```

## Adding Examples

When adding new examples:

1. Place sample input files in `sample_input/`
2. Place expected outputs in `expected_output/`
3. Document the example in this README
4. Include any special notes or considerations
