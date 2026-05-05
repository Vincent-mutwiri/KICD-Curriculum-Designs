#!/usr/bin/env python3
"""Process all curriculum markdown files and generate JSON output."""

from pathlib import Path
from curriculum_extractor import FileProcessor

def main():
    # Find all curriculum markdown files
    base_dir = Path(__file__).parent
    curriculum_files = []
    
    # Collect files from grade directories
    for grade_dir in base_dir.glob("**/Grade_*"):
        curriculum_files.extend(grade_dir.glob("*.md"))
    
    # Collect files from Lower-Primary
    lower_primary = base_dir / "Lower-Primary(G1-G3)"
    if lower_primary.exists():
        curriculum_files.extend(lower_primary.glob("*.md"))
    
    # Create output directory
    output_dir = base_dir / "output_json"
    output_dir.mkdir(exist_ok=True)
    
    # Process all files
    processor = FileProcessor()
    print(f"Processing {len(curriculum_files)} curriculum files...")
    
    result = processor.process_directory(str(base_dir), str(output_dir))
    
    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"{'='*60}")
    print(f"Status: {result.status}")
    print(f"Files processed: {result.files_processed}")
    print(f"Files succeeded: {result.files_succeeded}")
    print(f"Files failed: {result.files_failed}")
    
    if result.errors:
        print(f"\nErrors ({len(result.errors)}):")
        for error in result.errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(result.errors) > 10:
            print(f"  ... and {len(result.errors) - 10} more")
    
    print(f"\nJSON files saved to: {output_dir}")

if __name__ == "__main__":
    main()
