# Implementation Plan: Curriculum Data Extraction and Transformation Tool

## Overview

This implementation plan breaks down the development of the Curriculum Data Extraction and Transformation Tool into discrete, manageable coding tasks. The tool will parse Kenyan curriculum markdown files and transform them into structured JSON documents suitable for MongoDB storage.

**Technology Stack:**
- Python 3.10+
- mistletoe for markdown parsing
- pydantic v2 for data validation
- pytest for unit testing
- hypothesis for property-based testing

**Implementation Approach:**
1. Set up project structure and core dependencies
2. Implement data models with Pydantic v2
3. Build parsing and extraction components
4. Implement transformation and validation
5. Create CLI interface and file processing orchestration
6. Add comprehensive testing (unit, integration, property-based)
7. Generate documentation and examples

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create Python package structure with `src/curriculum_extractor/` directory
  - Create `pyproject.toml` with project metadata and dependencies (mistletoe, pydantic>=2.0, pytest, hypothesis)
  - Create `setup.py` or use modern `pyproject.toml` build system
  - Set up `.gitignore` for Python projects
  - Create `README.md` with project overview
  - Create `tests/` directory structure (unit/, integration/, property/, fixtures/)
  - _Requirements: All requirements depend on proper project setup_

- [ ] 2. Implement Pydantic data models
  - [ ] 2.1 Create core data models with Pydantic v2
    - Implement `Competency` model with `competency` and `context` fields
    - Implement `Value` model with `value` and `context` fields
    - Implement `SubStrand` model with all required fields (sub_strand_id, sub_strand_name, topics, specific_learning_outcomes, suggested_learning_experiences, key_inquiry_questions, core_competencies, values, pcis, suggested_resources, assessment_methods)
    - Implement `RubricCriterion` model with performance level fields
    - Implement `Strand` model with strand_id, strand_name, sub_strands, assessment_rubric
    - Implement `GradeRange` model with start and end fields (1-12 validation)
    - Implement `CurriculumDocument` model with subject, grade, year, essence_statement, general_learning_outcomes, strands
    - Add field validators for grade (1-12), year (1900-2100), and strands non-empty
    - _Requirements: 15.1, 15.2, 15.3, 16.1, 16.4, 16.5, 16.7, 24.1-24.8_

  - [ ] 2.2 Write property test for data model validation
    - **Property 17: Validation Detects Invalid Data**
    - **Validates: Requirements 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7**
    - Use Hypothesis to generate invalid curriculum data (missing fields, invalid grades, invalid years, duplicate IDs)
    - Verify that Pydantic validation catches all invalid cases
    - Test edge cases: grade boundaries (0, 1, 12, 13), year boundaries, empty strands array

- [ ] 3. Implement Configuration Manager
  - [ ] 3.1 Create Configuration class
    - Implement `Configuration` class with fields: preserve_essence_statement, preserve_general_outcomes, output_directory, pretty_print, indent_size, grade_range_strategy, mongodb_format
    - Implement `load()` classmethod to load from YAML/JSON file
    - Implement `get_defaults()` classmethod for default configuration
    - Add validation for configuration values
    - _Requirements: 23.1, 23.2, 23.3, 23.4, 23.5, 23.6, 23.7_

  - [ ] 3.2 Write unit tests for Configuration Manager
    - Test loading from file
    - Test default values
    - Test invalid configuration values
    - Test missing configuration file handling

  - [ ] 3.3 Write property test for configuration loading consistency
    - **Property 22: Configuration Loading Consistency**
    - **Validates: Requirements 23.3, 23.4, 23.5, 23.6, 23.7**
    - Verify that loading the same configuration file multiple times produces identical Configuration objects

- [ ] 4. Implement Markdown Parser
  - [ ] 4.1 Create MarkdownParser class using mistletoe
    - Implement `parse_file()` method to read and parse markdown files
    - Implement `parse_string()` method to parse markdown strings
    - Implement `extract_tables()` method to extract all tables from document
    - Implement `extract_lists()` method to extract all lists from document
    - Handle UTF-8 encoding and encoding errors gracefully
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [ ] 4.2 Write unit tests for MarkdownParser
    - Test parsing valid markdown files
    - Test table extraction with various table structures
    - Test nested list extraction
    - Test encoding error handling
    - Test malformed markdown handling

  - [ ] 4.3 Write property test for table structure preservation
    - **Property 2: Table Structure Preservation**
    - **Validates: Requirements 1.2, 14.1, 14.2, 14.3, 14.4, 14.5**
    - Generate random markdown tables with Hypothesis
    - Verify that parsing preserves all row/column relationships
    - Verify that cell content at position (row, col) is preserved

  - [ ]* 4.4 Write property test for hierarchical structure preservation
    - **Property 3: Hierarchical Structure Preservation**
    - **Validates: Requirements 1.3, 7.4**
    - Generate random nested list structures
    - Verify that parent-child relationships are preserved
    - Verify that nesting depth is maintained

- [ ] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement Content Filter
  - [ ] 6.1 Create ContentFilter class
    - Implement `filter_document()` method to remove extraneous sections
    - Implement `remove_section()` method to remove specific sections by name
    - Implement `should_preserve()` method to check configuration for preservation rules
    - Add logic to remove: copyright/ISBN, TOC, National Goals, foreword/preface, acknowledgements, lesson allocation tables
    - Add logic to conditionally preserve essence statements and general outcomes based on configuration
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9_

  - [ ] 6.2 Write unit tests for ContentFilter
    - Test removal of each extraneous section type
    - Test preservation of strand/sub-strand content
    - Test configuration-based preservation of essence statements
    - Test configuration-based preservation of general outcomes

  - [ ] 6.3 Write property test for content filtering preservation
    - **Property 7: Content Filtering Preserves Essential Data**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**
    - Generate curriculum documents with both essential and extraneous content
    - Verify that filtering removes only extraneous sections
    - Verify that all strand and sub-strand content is preserved

  - [ ] 6.4 Write property test for configuration-based preservation
    - **Property 8: Configuration-Based Preservation**
    - **Validates: Requirements 3.8, 3.9, 23.1, 23.2**
    - Test with preserve_essence_statement=True and False
    - Test with preserve_general_outcomes=True and False
    - Verify that configuration deterministically controls output

- [ ] 7. Implement Metadata Extractor
  - [ ] 7.1 Create MetadataExtractor class
    - Implement `extract_from_filename()` method to parse filename patterns
    - Implement `extract_from_content()` method to extract from document headers
    - Implement `normalize_subject()` method to normalize subject names
    - Implement `parse_grade()` method to handle various grade formats ("Grade 10", "Gredi 10", "G 10", "Grade 1-3")
    - Handle special characters and multi-word subject names
    - _Requirements: 1.5, 1.6, 1.7, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 18.1, 18.2_

  - [ ] 7.2 Write unit tests for MetadataExtractor
    - Test filename parsing with various formats
    - Test content extraction from headers
    - Test subject name normalization with special characters
    - Test grade parsing for single grades and ranges
    - Test alternative grade formats (Gredi, G)

  - [ ] 7.3 Write property test for metadata extraction completeness
    - **Property 4: Metadata Extraction Completeness**
    - **Validates: Requirements 1.5, 1.6, 1.7, 2.1, 2.2, 2.3**
    - Generate valid curriculum filenames with subject, grade, year
    - Verify that all three metadata fields are extracted correctly

  - [ ] 7.4 Write property test for grade format normalization
    - **Property 5: Grade Format Normalization**
    - **Validates: Requirements 2.5, 2.6, 18.1, 18.2**
    - Generate various grade format strings
    - Verify correct extraction of numeric values or range objects

  - [ ] 7.5 Write property test for subject name normalization idempotence
    - **Property 6: Subject Name Normalization Idempotence**
    - **Validates: Requirements 2.4**
    - Generate random subject names
    - Verify that normalize(normalize(name)) == normalize(name)

- [ ] 8. Implement Strand Extractor
  - [ ] 8.1 Create StrandExtractor class
    - Implement `extract_strands()` method to identify and extract all strands
    - Implement `identify_strand_header()` method to recognize strand headers (e.g., "STRAND 1.0: NAME")
    - Implement `extract_strand_content()` method to extract content between strand headers
    - Parse strand ID and strand name from headers
    - Maintain sequential order of strands
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [ ] 8.2 Write unit tests for StrandExtractor
    - Test strand header identification with various formats
    - Test strand ID and name parsing
    - Test sequential order preservation
    - Test handling of strands with no sub-strands

  - [ ] 8.3 Write property test for element extraction completeness
    - **Property 9: Element Extraction Completeness**
    - **Validates: Requirements 4.1, 4.2, 4.3, 5.1, 5.2, 5.3**
    - Generate curriculum documents with N strands
    - Verify that exactly N strands are extracted
    - Verify that each strand's M sub-strands are all extracted

  - [ ] 8.4 Write property test for sequential order preservation
    - **Property 10: Sequential Order Preservation**
    - **Validates: Requirements 4.4, 5.5**
    - Generate curriculum documents with multiple strands and sub-strands
    - Verify that output order matches input order for both strands and sub-strands

  - [ ] 8.5 Write property test for empty collection representation
    - **Property 11: Empty Collection Representation**
    - **Validates: Requirements 4.5, 24.1-24.8**
    - Generate strands with no sub-strands
    - Generate sub-strands with missing optional fields
    - Verify that empty arrays are used (not null or missing fields)

- [ ] 9. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Implement SubStrand Extractor
  - [ ] 10.1 Create SubStrandExtractor class
    - Implement `extract_substrands()` method to extract sub-strands from strand content
    - Implement `extract_table_content()` method to parse sub-strand tables
    - Implement `parse_learning_outcomes()` method to extract and clean learning outcomes
    - Implement `parse_learning_experiences()` method to extract learning experiences
    - Implement `parse_inquiry_questions()` method to extract inquiry questions
    - Handle multi-row sub-strands in tables
    - Parse nested lists within table cells
    - Extract sub-strand ID, name, and topics
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4_

  - [ ] 10.2 Write unit tests for SubStrandExtractor
    - Test sub-strand table identification
    - Test extraction of each field type
    - Test multi-row sub-strand handling
    - Test nested list parsing in cells
    - Test removal of formatting markers (bullets, numbering)

  - [ ] 10.3 Write property test for list element extraction
    - **Property 12: List Element Extraction Preserves Content**
    - **Validates: Requirements 6.1-6.5, 7.1-7.5, 8.1-8.4, 11.1-11.4, 12.1-12.4, 13.1-13.4**
    - Generate lists with various formatting (bullets, numbers, bold, italic)
    - Verify that text content is preserved while formatting is removed

- [ ] 11. Implement structured data extractors (Competencies, Values, PCIs, Resources, Assessment)
  - [ ] 11.1 Add methods to SubStrandExtractor for structured data
    - Implement `parse_competencies()` method to extract competencies with context
    - Implement `parse_values()` method to extract values with context
    - Implement `parse_pcis()` method to extract PCIs
    - Implement `parse_resources()` method to extract suggested resources
    - Implement `parse_assessment_methods()` method to extract assessment methods
    - Handle various separator formats (colon, dash, comma)
    - Parse "Name: Context" and "Name - Context" patterns
    - _Requirements: 9.1-9.6, 10.1-10.6, 11.1-11.4, 12.1-12.4, 13.1-13.4_

  - [ ] 11.2 Write unit tests for structured data extraction
    - Test competency parsing with various formats
    - Test value parsing with various formats
    - Test PCI extraction with and without descriptions
    - Test resource extraction with parenthetical details
    - Test assessment method extraction

  - [ ] 11.3 Write property test for structured data extraction correctness
    - **Property 13: Structured Data Extraction Correctness**
    - **Validates: Requirements 9.1-9.6, 10.1-10.6**
    - Generate competencies and values with "Name: Context" format
    - Verify correct separation into name and context fields

- [ ] 12. Implement Rubric Extractor
  - [ ] 12.1 Create RubricExtractor class
    - Implement `extract_rubrics()` method to identify and extract rubric tables
    - Implement `identify_rubric_table()` method to recognize rubric table structure
    - Implement `parse_rubric_row()` method to extract criterion and performance descriptions
    - Handle rubric headers: Indicators, Exceeds Expectation, Meets Expectation, Approaches Expectation, Below Expectation
    - Handle split rubrics across pages
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6_

  - [ ] 12.2 Write unit tests for RubricExtractor
    - Test rubric table identification
    - Test extraction of performance levels
    - Test extraction of indicators and descriptions
    - Test handling of split rubrics

  - [ ] 12.3 Write property test for rubric structure correctness
    - **Property 14: Rubric Structure Correctness**
    - **Validates: Requirements 14.1-14.6**
    - Generate rubric tables with indicators and performance levels
    - Verify that each indicator maps to all performance level descriptions

- [ ] 13. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Implement JSON Transformer
  - [ ] 14.1 Create JSONTransformer class
    - Implement `transform()` method to convert CurriculumDocument to JSON dict
    - Implement `transform_strand()` method to convert Strand to dict
    - Implement `transform_substrand()` method to convert SubStrand to dict
    - Implement `escape_special_chars()` method for JSON string escaping
    - Ensure MongoDB field name compliance (no dots or dollar signs)
    - Handle Unicode characters correctly
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7, 19.1-19.5, 21.1-21.6, 25.1, 25.2_

  - [ ] 14.2 Write unit tests for JSONTransformer
    - Test transformation of complete curriculum document
    - Test transformation of individual components
    - Test special character escaping
    - Test MongoDB field name compliance
    - Test Unicode character preservation

  - [ ] 14.3 Write property test for JSON validity
    - **Property 15: JSON Validity**
    - **Validates: Requirements 15.1-15.7, 19.1-19.5**
    - Generate random curriculum documents
    - Transform to JSON
    - Verify that output is valid JSON parseable by standard parsers

  - [ ] 14.4 Write property test for special character preservation
    - **Property 16: Special Character Preservation**
    - **Validates: Requirements 21.1-21.6**
    - Generate text with Unicode, special symbols, formatting characters
    - Verify that characters are preserved correctly in JSON output

  - [ ] 14.5 Write property test for MongoDB field name compliance
    - **Property 19: MongoDB Field Name Compliance**
    - **Validates: Requirements 25.1-25.4**
    - Generate curriculum documents
    - Verify that no field names contain dots or dollar signs
    - Verify document size is within MongoDB limits

- [ ] 15. Implement Data Validator
  - [ ] 15.1 Create DataValidator class
    - Implement `validate()` method to validate complete CurriculumDocument
    - Implement `validate_metadata()` method to validate subject, grade, year
    - Implement `validate_strands()` method to validate strand structure
    - Implement `validate_uniqueness()` method to check ID uniqueness
    - Return detailed ValidationResult with list of errors
    - Validate required fields, grade range (1-12), year range (1900-2100)
    - Validate strand ID uniqueness and sub-strand ID uniqueness within strands
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7_

  - [ ] 15.2 Write unit tests for DataValidator
    - Test validation of valid documents
    - Test detection of missing required fields
    - Test detection of invalid grade values
    - Test detection of invalid year values
    - Test detection of duplicate IDs
    - Test validation error messages

- [ ] 16. Implement Pretty Printer
  - [ ] 16.1 Create PrettyPrinter class
    - Implement `format_json()` method to format JSON with indentation
    - Implement `write_json()` method to write formatted JSON to file
    - Support configurable indentation size (default 2 spaces)
    - Ensure valid JSON output
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5_

  - [ ] 16.2 Write unit tests for PrettyPrinter
    - Test JSON formatting with various indentation sizes
    - Test file writing
    - Test output validity

- [ ] 17. Implement File Processor (orchestration)
  - [ ] 17.1 Create FileProcessor class
    - Implement `process_file()` method to orchestrate complete pipeline for single file
    - Implement `process_directory()` method for batch processing
    - Implement `generate_output_filename()` method to create output filenames
    - Coordinate: parse → filter → extract metadata → extract strands → extract sub-strands → transform → validate → write
    - Handle errors gracefully and continue processing on failures
    - Return ProcessingResult with status, counts, errors, warnings
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6_

  - [ ] 17.2 Write integration tests for FileProcessor
    - Test end-to-end processing of sample curriculum files
    - Test batch processing of multiple files
    - Test error recovery (continue on individual file failures)
    - Test output filename generation

  - [ ] 17.3 Write property test for batch processing independence
    - **Property 18: Batch Processing Independence**
    - **Validates: Requirements 17.1-17.6**
    - Generate multiple curriculum files
    - Verify that batch processing produces same output as individual processing
    - Verify that failure of one file doesn't affect others

- [ ] 18. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 19. Implement Report Generator
  - [ ] 19.1 Create ReportGenerator class
    - Implement `generate_file_report()` method to create per-file reports
    - Implement `generate_batch_report()` method to create batch summary reports
    - Implement `write_report()` method to write reports to files
    - Include: file names, status, element counts, warnings, errors, processing time
    - Calculate aggregate statistics for batch reports
    - _Requirements: 22.1, 22.2, 22.3, 22.4, 22.5, 22.6_

  - [ ] 19.2 Write unit tests for ReportGenerator
    - Test file report generation
    - Test batch report generation
    - Test report writing
    - Test aggregate statistics calculation

  - [ ] 19.3 Write property test for processing report accuracy
    - **Property 20: Processing Report Accuracy**
    - **Validates: Requirements 22.1-22.6**
    - Process curriculum files
    - Verify that report counts match actual output JSON counts

- [ ] 20. Implement CLI interface
  - [ ] 20.1 Create command-line interface using argparse or click
    - Implement main CLI entry point
    - Add arguments: input file/directory, output path, config file, verbose mode
    - Add options: --mongodb-script, --pretty-print, --preserve-essence, --preserve-outcomes
    - Integrate with FileProcessor for processing
    - Display progress and results
    - Handle errors and display user-friendly messages
    - _Requirements: All requirements - CLI is the user interface_

  - [ ] 20.2 Write integration tests for CLI
    - Test CLI with single file input
    - Test CLI with directory input
    - Test CLI with configuration file
    - Test CLI with various options
    - Test error handling and messages

  - [ ]* 20.3 Write property test for error messages
    - **Property 21: Error Messages Are Descriptive**
    - **Validates: Requirements 1.4**
    - Generate various error conditions
    - Verify that error messages include error type, file path, and context

- [ ] 21. Implement round-trip verification
  - [ ] 21.1 Add round-trip verification functionality
    - Implement function to parse JSON back to CurriculumDocument
    - Implement comparison function to check equivalence
    - Report specific differences if verification fails
    - Ignore formatting differences (whitespace, indentation)
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5_

  - [ ] 21.2 Write property test for round-trip transformation
    - **Property 1: Round-Trip Transformation Preserves Data**
    - **Validates: Requirements 20.1-20.5**
    - Generate valid curriculum documents
    - Transform to JSON and parse back
    - Verify that result is equivalent to original

- [ ] 22. Add MongoDB import support
  - [ ] 22.1 Implement MongoDB import script generation
    - Create function to generate mongoimport commands
    - Create shell script for batch import
    - Add option to generate MongoDB extended JSON format
    - Verify document size limits (16MB)
    - _Requirements: 25.1, 25.2, 25.3, 25.4, 25.5, 25.6_

  - [ ] 22.2 Write unit tests for MongoDB import support
    - Test import script generation
    - Test extended JSON format
    - Test document size validation

- [ ] 23. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 24. Create comprehensive documentation
  - [ ] 24.1 Write user documentation
    - Create comprehensive README.md with installation, usage, examples
    - Document CLI options and arguments
    - Document configuration file format
    - Provide example curriculum files and expected outputs
    - Document common issues and troubleshooting

  - [ ] 24.2 Write developer documentation
    - Document architecture and component design
    - Document how to add new extractors
    - Document how to extend for new markdown structures
    - Create API documentation for Python usage
    - Document testing strategy and how to run tests

  - [ ] 24.3 Add inline code documentation
    - Add docstrings to all classes and methods
    - Add type hints throughout codebase
    - Add comments for complex logic
    - Ensure docstrings follow standard format (Google or NumPy style)

- [ ] 25. Create example usage and sample data
  - [ ] 25.1 Create sample curriculum files
    - Create minimal valid curriculum file
    - Create comprehensive curriculum file with all elements
    - Create edge case files (empty sections, special characters, etc.)
    - Place in `examples/` directory

  - [ ] 25.2 Create example scripts
    - Create example Python script using the API
    - Create example configuration files
    - Create example batch processing script
    - Place in `examples/` directory

- [ ] 26. Final integration and testing
  - [ ] 26.1 Run complete test suite
    - Run all unit tests with coverage report
    - Run all integration tests
    - Run all property-based tests
    - Verify coverage goals (≥90% unit, ≥80% integration)

  - [ ] 26.2 Test with real curriculum files
    - Process sample curriculum files from Grade_4, Grade_7, Grade_10
    - Verify output correctness manually
    - Check for any edge cases not covered by tests
    - Fix any issues discovered

  - [ ] 26.3 Performance testing
    - Test processing time for typical files
    - Test memory usage
    - Test batch processing performance
    - Verify performance meets goals (<1s per file)

- [ ] 27. Final checkpoint - Ensure all tests pass and documentation is complete
  - Ensure all tests pass, ask the user if questions arise.
  - Verify that documentation is complete and accurate.
  - Confirm that the tool is ready for use.

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation throughout development
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- The implementation follows the pipeline architecture: Parse → Filter → Extract → Transform → Validate → Output
- All 22 correctness properties from the design document are covered by property-based tests
- Python 3.10+ is required for modern type hints and Pydantic v2 compatibility
