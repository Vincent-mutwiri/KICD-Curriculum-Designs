# Requirements Document

## Introduction

This document specifies the requirements for a Curriculum Data Extraction and Transformation Tool designed to process Kenyan curriculum markdown files and transform them into a structured JSON format suitable for MongoDB storage. The tool will extract curriculum content from markdown files organized by grade level (Grades 1-12) and subject, removing extraneous information while preserving the essential curriculum structure including strands, sub-strands, learning outcomes, competencies, values, and assessment methods.

## Glossary

- **System**: The Curriculum Data Extraction and Transformation Tool
- **Parser**: The component that reads and interprets markdown curriculum files
- **Transformer**: The component that converts parsed data into JSON format
- **Extractor**: The component that identifies and extracts specific curriculum elements
- **Validator**: The component that verifies the correctness of extracted and transformed data
- **Curriculum_File**: A markdown file containing curriculum design for a specific subject and grade
- **Strand**: A major thematic area within a curriculum subject
- **Sub_Strand**: A subdivision of a strand focusing on specific topics
- **Learning_Outcome**: A specific skill or knowledge the learner should acquire
- **Core_Competency**: A cross-cutting skill developed through learning experiences
- **PCI**: Pertinent and Contemporary Issues addressed in the curriculum
- **Assessment_Rubric**: A table defining performance levels and criteria
- **MongoDB_Document**: A JSON object structured for MongoDB storage
- **Pretty_Printer**: A component that formats JSON output in human-readable form

## Requirements

### Requirement 1: Parse Curriculum Markdown Files

**User Story:** As a curriculum data manager, I want to parse markdown curriculum files, so that I can extract structured curriculum data.

#### Acceptance Criteria

1. WHEN a valid curriculum markdown file is provided, THE Parser SHALL read the file and identify its structure
2. WHEN a curriculum file contains tables, THE Parser SHALL extract table data preserving row and column relationships
3. WHEN a curriculum file contains nested lists, THE Parser SHALL preserve the hierarchical structure
4. IF a file cannot be read or is corrupted, THEN THE Parser SHALL return a descriptive error message
5. THE Parser SHALL identify the subject name from the file name or content
6. THE Parser SHALL identify the grade level from the file name or content
7. THE Parser SHALL identify the year from the file name or content

### Requirement 2: Extract Subject and Grade Metadata

**User Story:** As a curriculum data manager, I want to extract subject and grade metadata, so that I can properly categorize curriculum documents.

#### Acceptance Criteria

1. WHEN parsing a curriculum file, THE Extractor SHALL extract the subject name
2. WHEN parsing a curriculum file, THE Extractor SHALL extract the grade level as an integer
3. WHEN parsing a curriculum file, THE Extractor SHALL extract the year as an integer
4. IF the subject name contains special characters or multiple words, THE Extractor SHALL normalize it to a consistent format
5. IF the grade level is specified as "Grade X" or "Gredi X" or "G X", THE Extractor SHALL extract the numeric value X
6. THE Extractor SHALL handle both "Grade 1-3" range formats and single grade formats

### Requirement 3: Filter Extraneous Content

**User Story:** As a curriculum data manager, I want to remove unnecessary content from curriculum files, so that I can focus on essential curriculum data.

#### Acceptance Criteria

1. WHEN processing a curriculum file, THE System SHALL remove copyright and ISBN information
2. WHEN processing a curriculum file, THE System SHALL remove table of contents sections
3. WHEN processing a curriculum file, THE System SHALL remove "National Goals of Education" sections
4. WHEN processing a curriculum file, THE System SHALL remove foreword and preface sections
5. WHEN processing a curriculum file, THE System SHALL remove acknowledgement sections
6. WHEN processing a curriculum file, THE System SHALL remove "Senior School in the CBC" or "Junior School" descriptive sections
7. WHEN processing a curriculum file, THE System SHALL remove lesson allocation tables
8. WHERE the user configures it, THE System SHALL optionally preserve essence statements
9. WHERE the user configures it, THE System SHALL optionally preserve general learning outcomes

### Requirement 4: Extract Strand Information

**User Story:** As a curriculum data manager, I want to extract strand information, so that I can organize curriculum content by major themes.

#### Acceptance Criteria

1. WHEN processing curriculum content, THE Extractor SHALL identify all strands
2. FOR ALL strands, THE Extractor SHALL extract the strand ID (e.g., "1.0", "2.0")
3. FOR ALL strands, THE Extractor SHALL extract the strand name
4. THE Extractor SHALL maintain the sequential order of strands as they appear in the source document
5. IF a strand has no sub-strands, THE Extractor SHALL record it with an empty sub-strands array

### Requirement 5: Extract Sub-Strand Information

**User Story:** As a curriculum data manager, I want to extract sub-strand information, so that I can organize curriculum content by specific topics within strands.

#### Acceptance Criteria

1. WHEN processing a strand, THE Extractor SHALL identify all sub-strands within that strand
2. FOR ALL sub-strands, THE Extractor SHALL extract the sub-strand ID (e.g., "1.1", "1.2")
3. FOR ALL sub-strands, THE Extractor SHALL extract the sub-strand name
4. FOR ALL sub-strands, THE Extractor SHALL extract the list of topics
5. THE Extractor SHALL maintain the sequential order of sub-strands within each strand

### Requirement 6: Extract Learning Outcomes

**User Story:** As a curriculum data manager, I want to extract specific learning outcomes, so that I can document what learners should achieve.

#### Acceptance Criteria

1. WHEN processing a sub-strand, THE Extractor SHALL identify the "Specific Learning Outcomes" section
2. THE Extractor SHALL extract all learning outcomes as a list of strings
3. THE Extractor SHALL preserve the lettered or numbered ordering of learning outcomes (e.g., "a)", "b)", "1.", "2.")
4. THE Extractor SHALL remove the ordering prefix and store only the outcome text
5. IF learning outcomes contain formatting (bold, italic), THE Extractor SHALL preserve the text content without formatting

### Requirement 7: Extract Learning Experiences

**User Story:** As a curriculum data manager, I want to extract suggested learning experiences, so that I can document recommended teaching activities.

#### Acceptance Criteria

1. WHEN processing a sub-strand, THE Extractor SHALL identify the "Suggested Learning Experiences" section
2. THE Extractor SHALL extract all learning experiences as a list of strings
3. THE Extractor SHALL preserve bullet points or numbered items as separate list entries
4. THE Extractor SHALL preserve nested sub-items within learning experiences
5. IF learning experiences contain formatting (bold, italic), THE Extractor SHALL preserve the text content without formatting

### Requirement 8: Extract Key Inquiry Questions

**User Story:** As a curriculum data manager, I want to extract key inquiry questions, so that I can document essential questions for learners.

#### Acceptance Criteria

1. WHEN processing a sub-strand, THE Extractor SHALL identify the "Suggested Key Inquiry Question(s)" section
2. THE Extractor SHALL extract all inquiry questions as a list of strings
3. THE Extractor SHALL preserve numbered or bulleted question formatting
4. THE Extractor SHALL remove numbering prefixes and store only the question text
5. IF no inquiry questions are present, THE Extractor SHALL record an empty array

### Requirement 9: Extract Core Competencies

**User Story:** As a curriculum data manager, I want to extract core competencies with context, so that I can document cross-cutting skills developed.

#### Acceptance Criteria

1. WHEN processing a sub-strand, THE Extractor SHALL identify the "Core Competencies to be developed" section
2. FOR ALL competencies, THE Extractor SHALL extract the competency name
3. FOR ALL competencies, THE Extractor SHALL extract the context or description
4. THE Extractor SHALL structure each competency as an object with "competency" and "context" fields
5. THE Extractor SHALL handle competencies separated by bullet points or commas
6. IF a competency name appears before a colon or dash, THE Extractor SHALL treat the text before as the name and after as the context

### Requirement 10: Extract Values

**User Story:** As a curriculum data manager, I want to extract values with context, so that I can document character development aspects.

#### Acceptance Criteria

1. WHEN processing a sub-strand, THE Extractor SHALL identify the "Values" section
2. FOR ALL values, THE Extractor SHALL extract the value name
3. FOR ALL values, THE Extractor SHALL extract the context or description
4. THE Extractor SHALL structure each value as an object with "value" and "context" fields
5. THE Extractor SHALL handle values separated by bullet points or commas
6. IF a value name appears before a colon or dash, THE Extractor SHALL treat the text before as the name and after as the context

### Requirement 11: Extract Pertinent and Contemporary Issues (PCIs)

**User Story:** As a curriculum data manager, I want to extract PCIs, so that I can document contemporary issues addressed in the curriculum.

#### Acceptance Criteria

1. WHEN processing a sub-strand, THE Extractor SHALL identify the "Pertinent and Contemporary Issues (PCIs)" section
2. THE Extractor SHALL extract all PCIs as a list of strings
3. THE Extractor SHALL handle PCIs separated by bullet points or commas
4. IF a PCI has a description after a colon or dash, THE Extractor SHALL include both the PCI name and description
5. IF no PCIs are present, THE Extractor SHALL record an empty array

### Requirement 12: Extract Suggested Resources

**User Story:** As a curriculum data manager, I want to extract suggested learning resources, so that I can document recommended materials.

#### Acceptance Criteria

1. WHEN processing a sub-strand, THE Extractor SHALL identify the "Suggested Learning Resources" section
2. THE Extractor SHALL extract all resources as a list of strings
3. THE Extractor SHALL handle resources separated by commas or bullet points
4. THE Extractor SHALL preserve resource descriptions including parenthetical details
5. IF no resources are present, THE Extractor SHALL record an empty array

### Requirement 13: Extract Assessment Methods

**User Story:** As a curriculum data manager, I want to extract assessment methods, so that I can document how learning is evaluated.

#### Acceptance Criteria

1. WHEN processing a sub-strand, THE Extractor SHALL identify assessment methods if present in the sub-strand section
2. THE Extractor SHALL extract all assessment methods as a list of strings
3. THE Extractor SHALL handle assessment methods separated by commas or bullet points
4. IF no assessment methods are present in the sub-strand, THE Extractor SHALL record an empty array
5. THE Extractor SHALL distinguish between sub-strand level assessment methods and strand level assessment rubrics

### Requirement 14: Extract Assessment Rubrics

**User Story:** As a curriculum data manager, I want to extract assessment rubrics, so that I can document performance criteria and levels.

#### Acceptance Criteria

1. WHEN processing a strand, THE Extractor SHALL identify assessment rubric tables
2. FOR ALL rubric tables, THE Extractor SHALL extract the table headers (performance levels)
3. FOR ALL rubric rows, THE Extractor SHALL extract the indicator/criteria
4. FOR ALL rubric cells, THE Extractor SHALL extract the performance description
5. THE Extractor SHALL structure rubrics as an array of objects with "indicator", "exceeds_expectation", "meets_expectation", "approaches_expectation", and "below_expectation" fields
6. WHERE a rubric spans multiple pages or is split, THE Extractor SHALL combine the parts into a single rubric structure

### Requirement 15: Transform Data to JSON Structure

**User Story:** As a curriculum data manager, I want to transform extracted data into JSON format, so that I can store it in MongoDB.

#### Acceptance Criteria

1. WHEN all data is extracted, THE Transformer SHALL create a JSON object with "subject", "grade", "year", and "strands" fields
2. FOR ALL strands, THE Transformer SHALL create a strand object with "strand_id", "strand_name", and "sub_strands" fields
3. FOR ALL sub-strands, THE Transformer SHALL create a sub-strand object with all extracted fields
4. THE Transformer SHALL ensure all arrays are properly formatted as JSON arrays
5. THE Transformer SHALL ensure all objects are properly formatted as JSON objects
6. THE Transformer SHALL escape special characters in strings according to JSON specification
7. THE Transformer SHALL produce valid JSON that can be parsed by standard JSON parsers

### Requirement 16: Validate Extracted Data

**User Story:** As a curriculum data manager, I want to validate extracted data, so that I can ensure data quality and completeness.

#### Acceptance Criteria

1. WHEN data extraction is complete, THE Validator SHALL verify that required fields are present
2. THE Validator SHALL verify that strand IDs are unique within a document
3. THE Validator SHALL verify that sub-strand IDs are unique within a strand
4. THE Validator SHALL verify that grade is a valid integer between 1 and 12
5. THE Validator SHALL verify that year is a valid four-digit integer
6. IF validation fails, THE Validator SHALL return a list of validation errors with specific details
7. THE Validator SHALL verify that all arrays contain at least one element where logically required (e.g., strands array)

### Requirement 17: Process Multiple Files in Batch

**User Story:** As a curriculum data manager, I want to process multiple curriculum files in batch, so that I can efficiently transform all curriculum data.

#### Acceptance Criteria

1. WHEN provided with a directory path, THE System SHALL identify all markdown files in the directory
2. THE System SHALL process each markdown file independently
3. THE System SHALL generate a separate JSON output file for each input markdown file
4. THE System SHALL maintain a processing log showing success or failure for each file
5. IF a file fails to process, THE System SHALL continue processing remaining files
6. THE System SHALL report a summary of processed files including success count and failure count

### Requirement 18: Handle Grade Range Files

**User Story:** As a curriculum data manager, I want to handle files covering multiple grades, so that I can process lower primary (Grade 1-3) curriculum files.

#### Acceptance Criteria

1. WHEN processing a file with grade range "Grade 1-3", THE System SHALL extract the grade range
2. WHERE the user configures it, THE System SHALL create separate JSON documents for each grade in the range
3. WHERE the user configures it, THE System SHALL create a single JSON document with a grade range field
4. THE System SHALL clearly indicate in the output whether the document covers a single grade or a range

### Requirement 19: Generate Pretty-Printed JSON Output

**User Story:** As a curriculum data manager, I want to generate human-readable JSON output, so that I can review and verify the transformed data.

#### Acceptance Criteria

1. WHEN generating JSON output, THE Pretty_Printer SHALL format the JSON with proper indentation
2. THE Pretty_Printer SHALL use 2 spaces for each indentation level
3. THE Pretty_Printer SHALL place opening braces on the same line as the key
4. THE Pretty_Printer SHALL place closing braces on a new line at the appropriate indentation level
5. THE Pretty_Printer SHALL ensure the output is valid JSON that can be parsed

### Requirement 20: Verify Round-Trip Transformation

**User Story:** As a curriculum data manager, I want to verify round-trip transformation, so that I can ensure no data is lost during processing.

#### Acceptance Criteria

1. FOR ALL valid curriculum files, parsing then pretty-printing then parsing SHALL produce an equivalent JSON structure
2. THE System SHALL provide a round-trip verification function that compares original parsed data with re-parsed data
3. IF round-trip verification fails, THE System SHALL report the specific differences
4. THE round-trip verification SHALL compare all fields including nested objects and arrays
5. THE round-trip verification SHALL ignore formatting differences (whitespace, indentation) and compare only data content

### Requirement 21: Handle Special Characters and Formatting

**User Story:** As a curriculum data manager, I want to handle special characters and formatting, so that I can preserve curriculum content accurately.

#### Acceptance Criteria

1. WHEN extracting text, THE System SHALL preserve Unicode characters (e.g., bullets, dashes, special symbols)
2. WHEN extracting text, THE System SHALL convert markdown formatting to plain text
3. WHEN extracting text, THE System SHALL preserve line breaks within multi-line content
4. THE System SHALL handle italic text markers (asterisks, underscores) by removing them and keeping the text
5. THE System SHALL handle bold text markers (double asterisks) by removing them and keeping the text
6. THE System SHALL handle parenthetical content by preserving it as part of the text

### Requirement 22: Generate Processing Reports

**User Story:** As a curriculum data manager, I want to generate processing reports, so that I can track the extraction and transformation process.

#### Acceptance Criteria

1. WHEN processing files, THE System SHALL generate a report for each file processed
2. THE report SHALL include the input file name, output file name, and processing status
3. THE report SHALL include counts of extracted strands, sub-strands, and other major elements
4. THE report SHALL include any warnings or errors encountered during processing
5. THE report SHALL include processing time for each file
6. THE System SHALL generate a summary report for batch processing showing aggregate statistics

### Requirement 23: Support Configuration Options

**User Story:** As a curriculum data manager, I want to configure processing options, so that I can customize the extraction and transformation behavior.

#### Acceptance Criteria

1. THE System SHALL support a configuration option to preserve or remove essence statements
2. THE System SHALL support a configuration option to preserve or remove general learning outcomes
3. THE System SHALL support a configuration option to specify output directory for JSON files
4. THE System SHALL support a configuration option to enable or disable pretty-printing
5. THE System SHALL support a configuration option to specify indentation size for pretty-printing
6. THE System SHALL load configuration from a configuration file if present
7. THE System SHALL use default values for any configuration options not specified

### Requirement 24: Handle Missing or Optional Fields

**User Story:** As a curriculum data manager, I want to handle missing or optional fields gracefully, so that I can process curriculum files with varying structures.

#### Acceptance Criteria

1. WHEN a sub-strand lacks specific learning outcomes, THE System SHALL record an empty array
2. WHEN a sub-strand lacks learning experiences, THE System SHALL record an empty array
3. WHEN a sub-strand lacks inquiry questions, THE System SHALL record an empty array
4. WHEN a sub-strand lacks core competencies, THE System SHALL record an empty array
5. WHEN a sub-strand lacks values, THE System SHALL record an empty array
6. WHEN a sub-strand lacks PCIs, THE System SHALL record an empty array
7. WHEN a sub-strand lacks resources, THE System SHALL record an empty array
8. WHEN a sub-strand lacks assessment methods, THE System SHALL record an empty array
9. THE System SHALL distinguish between missing fields and empty fields in validation reports

### Requirement 25: Support MongoDB Import Format

**User Story:** As a curriculum data manager, I want to generate MongoDB-compatible JSON, so that I can import the data directly into MongoDB.

#### Acceptance Criteria

1. THE System SHALL generate JSON documents that conform to MongoDB document structure requirements
2. THE System SHALL ensure field names do not contain dots or dollar signs (MongoDB reserved characters)
3. THE System SHALL ensure document size does not exceed MongoDB's 16MB document size limit
4. WHERE a document would exceed size limits, THE System SHALL provide a warning
5. THE System SHALL support generating JSON in MongoDB extended JSON format where needed
6. THE System SHALL provide an option to generate a MongoDB import script alongside JSON files
