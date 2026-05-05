#!/usr/bin/env python3
"""
Example: Custom processing with individual extractors.
"""
from curriculum_extractor import (
    MarkdownParser,
    MetadataExtractor,
    StrandExtractor,
    SubStrandExtractor,
    RubricExtractor,
    JSONTransformer,
    CurriculumDocument
)

# Read file
with open("examples/curriculum_files/comprehensive.md", "r") as f:
    content = f.read()

# Parse markdown
parser = MarkdownParser()
doc = parser.parse_string(content)

# Extract metadata
metadata_extractor = MetadataExtractor()
metadata = metadata_extractor.extract_from_content(doc)

print(f"Subject: {metadata['subject']}")
print(f"Grade: {metadata['grade']}")
print(f"Year: {metadata['year']}")

# Extract strands
strand_extractor = StrandExtractor(parser)
strands = strand_extractor.extract_strands(doc)

print(f"\nFound {len(strands)} strand(s):")
for strand in strands:
    print(f"  - {strand.strand_id}: {strand.strand_name}")

# Extract sub-strands from first strand
if strands:
    substrand_extractor = SubStrandExtractor(parser)
    substrands = substrand_extractor.extract_substrands(strands[0].content)
    print(f"\nFound {len(substrands)} sub-strand(s) in strand 1")

# Extract rubrics
rubric_extractor = RubricExtractor(parser)
rubrics = rubric_extractor.extract_rubrics(doc)
print(f"\nFound {len(rubrics)} rubric criteria")
