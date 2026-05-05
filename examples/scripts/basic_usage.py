#!/usr/bin/env python3
"""
Example: Basic API usage for processing a single curriculum file.
"""
from curriculum_extractor import FileProcessor, Configuration

# Create processor with default configuration
processor = FileProcessor()

# Process a single file
result = processor.process_file(
    "examples/curriculum_files/minimal_valid.md",
    "output/minimal_valid.json"
)

# Check result
if result.status == "success":
    print(f"✓ Successfully processed {result.files_succeeded} file(s)")
else:
    print(f"✗ Processing failed: {result.errors}")
