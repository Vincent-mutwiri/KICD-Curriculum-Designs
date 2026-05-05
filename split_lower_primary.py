#!/usr/bin/env python3
"""Split Lower-Primary (G1-G3) files into separate grade files."""

import re
from pathlib import Path

def extract_subject(filename):
    """Extract subject name from filename."""
    name = filename.replace("Grade 1-3 ", "").replace(".md", "")
    name = re.sub(r" - Revised.*", "", name)
    name = re.sub(r",? IL G1-3", "", name)
    name = re.sub(r" \(\d+\)", "", name)
    return name.strip()

def split_file(input_path, output_dir):
    """Split a multi-grade file into separate grade files."""
    content = input_path.read_text()
    subject = extract_subject(input_path.name)
    
    # Find grade section markers (e.g., "MATHEMATICAL ACTIVITIES GRADE 1")
    pattern = re.compile(r'\*\*([A-Z\s]+)\s+GRADE\s+([123])\*\*', re.IGNORECASE)
    matches = list(pattern.finditer(content))
    
    if not matches:
        print(f"  Warning: No grade sections found in {input_path.name}")
        return
    
    # Extract content for each grade
    for i, match in enumerate(matches):
        grade = int(match.group(2))
        start_pos = match.end()
        
        # Find end position (start of next grade or end of file)
        if i < len(matches) - 1:
            end_pos = matches[i + 1].start()
        else:
            # Look for APPENDIX or end of file
            appendix_match = re.search(r'\*\*APPENDIX', content[start_pos:], re.IGNORECASE)
            end_pos = start_pos + appendix_match.start() if appendix_match else len(content)
        
        grade_content = content[start_pos:end_pos].strip()
        
        # Create output file
        output_file = output_dir / f"{subject} Grade {grade}.md"
        grade_doc = f"""# Subject: {subject}

# Grade {grade}

# Year: 2024

{grade_content}
"""
        output_file.write_text(grade_doc)
        print(f"  Created: {output_file.name}")

def main():
    base_dir = Path(__file__).parent
    input_dir = base_dir / "Lower-Primary(G1-G3)"
    output_dir = base_dir / "Lower-Primary-Split"
    output_dir.mkdir(exist_ok=True)
    
    print("Splitting Lower-Primary files...")
    
    for md_file in input_dir.glob("*.md"):
        print(f"\nProcessing: {md_file.name}")
        split_file(md_file, output_dir)
    
    print(f"\n{'='*60}")
    print(f"Split files saved to: {output_dir}")
    print(f"Total files created: {len(list(output_dir.glob('*.md')))}")

if __name__ == "__main__":
    main()
