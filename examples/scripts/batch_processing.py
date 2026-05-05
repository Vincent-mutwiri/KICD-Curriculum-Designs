#!/usr/bin/env python3
"""
Example: Batch processing with custom configuration.
"""
from pathlib import Path
from curriculum_extractor import FileProcessor, Configuration

# Load configuration from file
config = Configuration.load("examples/configs/batch_config.yaml")

# Or create configuration programmatically
config = Configuration(
    preserve_essence_statement=True,
    preserve_general_outcomes=True,
    pretty_print=True,
    indent_size=2,
    mongodb_format=True
)

# Create processor
processor = FileProcessor(config)

# Process entire directory
result = processor.process_directory(
    "examples/curriculum_files",
    "output/batch_results"
)

# Display results
print(f"Processed: {result.files_processed}")
print(f"Succeeded: {result.files_succeeded}")
print(f"Failed: {result.files_failed}")

if result.errors:
    print("\nErrors:")
    for error in result.errors:
        print(f"  - {error}")
