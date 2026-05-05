# Examples Directory

This directory contains sample curriculum files, example scripts, and configuration files to help you get started with the curriculum extractor.

## Directory Structure

```
examples/
├── curriculum_files/     # Sample curriculum markdown files
├── scripts/             # Example Python scripts
├── configs/             # Example configuration files
└── README.md           # This file
```

## Sample Curriculum Files

### minimal_valid.md
A minimal valid curriculum file with the bare minimum required elements:
- Subject, grade, and year in heading
- One strand with one sub-strand
- All required sub-strand fields

### comprehensive.md
A comprehensive curriculum file demonstrating all features:
- Essence statement and general learning outcomes
- Multiple strands and sub-strands
- Complete assessment rubric
- All optional fields populated

### special_characters.md
Demonstrates handling of special characters:
- Unicode characters (Kiswahili text)
- Emoji symbols
- Special punctuation
- Non-ASCII characters

### empty_sections.md
Edge case file with empty sections to test robustness:
- Empty essence statement
- Empty learning outcomes
- Empty sub-strand fields
- Empty rubric cells

## Example Scripts

### basic_usage.py
Demonstrates basic API usage:
```python
from curriculum_extractor import FileProcessor

processor = FileProcessor()
result = processor.process_file("input.md", "output.json")
```

### batch_processing.py
Shows how to process multiple files:
```python
from curriculum_extractor import FileProcessor, Configuration

config = Configuration.load("config.yaml")
processor = FileProcessor(config)
result = processor.process_directory("input_dir", "output_dir")
```

### custom_extraction.py
Demonstrates using individual extractors:
```python
from curriculum_extractor import (
    MarkdownParser,
    MetadataExtractor,
    StrandExtractor,
    SubStrandExtractor
)

parser = MarkdownParser()
doc = parser.parse_string(content)
metadata = MetadataExtractor().extract_from_content(doc)
strands = StrandExtractor(parser).extract_strands(doc)
```

## Configuration Files

### batch_config.yaml
YAML configuration for batch processing with all features enabled.

### minimal_config.json
JSON configuration with minimal settings for compact output.

### production_config.json
Production-ready configuration with recommended settings.

## Usage Examples

### Process a single file
```bash
python -m curriculum_extractor.cli examples/curriculum_files/minimal_valid.md -o output.json
```

### Process with configuration
```bash
python -m curriculum_extractor.cli examples/curriculum_files/comprehensive.md \
  -c examples/configs/batch_config.yaml -o output.json
```

### Batch process all examples
```bash
python -m curriculum_extractor.cli examples/curriculum_files/ \
  -o output/ --pretty-print -v
```

### Run example scripts
```bash
# Basic usage
python examples/scripts/basic_usage.py

# Batch processing
python examples/scripts/batch_processing.py

# Custom extraction
python examples/scripts/custom_extraction.py
```

## Testing the Examples

You can use these files to test the curriculum extractor:

```bash
# Test minimal file
python -m curriculum_extractor.cli examples/curriculum_files/minimal_valid.md -o /tmp/test1.json -v

# Test comprehensive file
python -m curriculum_extractor.cli examples/curriculum_files/comprehensive.md -o /tmp/test2.json -v

# Test special characters
python -m curriculum_extractor.cli examples/curriculum_files/special_characters.md -o /tmp/test3.json -v

# Test edge cases
python -m curriculum_extractor.cli examples/curriculum_files/empty_sections.md -o /tmp/test4.json -v
```

## Expected Outputs

All example files should process successfully and produce valid JSON output. The empty_sections.md file may produce warnings but should still generate valid output with default values for empty fields.

## Modifying Examples

Feel free to modify these examples to suit your needs:
- Add more strands and sub-strands
- Change subject, grade, or year
- Add or remove optional fields
- Test different configurations

## Contributing

If you create useful example files or scripts, consider contributing them back to the project!
