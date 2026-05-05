# CLI Quick Reference

## Installation

```bash
pip install -e .
```

## Basic Usage

```bash
# Process single file
python -m curriculum_extractor.cli input.md -o output.json

# Process directory
python -m curriculum_extractor.cli input_dir/ -o output_dir/

# Show help
python -m curriculum_extractor.cli --help
```

## Options

| Option | Description |
|--------|-------------|
| `-o, --output` | Output file or directory path |
| `-c, --config` | Configuration file (YAML or JSON) |
| `-v, --verbose` | Show detailed processing information |
| `--mongodb-script` | Generate MongoDB import script |
| `--pretty-print` | Format JSON output with indentation |
| `--preserve-essence` | Keep essence statement in output |
| `--preserve-outcomes` | Keep general learning outcomes in output |

## Examples

### Process with verbose output
```bash
python -m curriculum_extractor.cli input.md -o output.json -v
```

### Use configuration file
```bash
python -m curriculum_extractor.cli input.md -c config.yaml -o output.json
```

### Pretty print with preserved content
```bash
python -m curriculum_extractor.cli input.md -o output.json \
  --pretty-print --preserve-essence --preserve-outcomes
```

### Process directory with MongoDB format
```bash
python -m curriculum_extractor.cli curriculum_files/ -o json_output/ \
  --mongodb-script --pretty-print
```

## Return Codes

- `0` - Success (all files processed)
- `1` - Failure or partial success (some files failed)

## Output Messages

- `✓ Success: N file(s) processed` - All files processed successfully
- `⚠ Partial: N succeeded, M failed` - Some files failed
- `✗ Failed: error message` - Processing failed

## Configuration File Format

### YAML
```yaml
preserve_essence_statement: true
preserve_general_outcomes: true
output_directory: "./output"
pretty_print: true
indent_size: 2
grade_range_strategy: "split"
mongodb_format: true
```

### JSON
```json
{
  "preserve_essence_statement": true,
  "preserve_general_outcomes": true,
  "output_directory": "./output",
  "pretty_print": true,
  "indent_size": 2,
  "grade_range_strategy": "split",
  "mongodb_format": true
}
```

## Error Handling

Errors are written to stderr, results to stdout. Use verbose mode (`-v`) for detailed error information including stack traces.

## Input File Format

The CLI expects markdown files with the following structure:

```markdown
# Subject Grade X Year

## Essence Statement
...

## General Learning Outcomes
- Outcome 1
- Outcome 2

## STRAND 1: Strand Name

### 1.1 Sub-strand Name

**Specific Learning Outcomes:**
- Outcome 1

**Suggested Learning Experiences:**
- Experience 1

**Key Inquiry Questions:**
- Question 1?

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

## Assessment Rubric

| Criterion | Exceeding | Meeting | Approaching | Below |
|-----------|-----------|---------|-------------|-------|
| ...       | ...       | ...     | ...         | ...   |
```
