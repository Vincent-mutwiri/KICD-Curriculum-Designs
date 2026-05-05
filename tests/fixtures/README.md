# Test Fixtures

This directory contains test fixtures for the curriculum extractor test suite.

## Structure

- `sample_curriculum_files/` - Sample markdown curriculum files for testing
- `expected_outputs/` - Expected JSON outputs for integration tests
- `edge_cases/` - Edge case test files (empty sections, special characters, etc.)
- `invalid_files/` - Invalid files for error handling tests

## Usage

Test fixtures are used by:
- Unit tests to test individual extractors
- Integration tests to verify end-to-end processing
- Property-based tests to generate test data

## Adding New Fixtures

When adding new test fixtures:
1. Place markdown files in appropriate subdirectory
2. Add corresponding expected output JSON if needed
3. Document any special characteristics in comments
4. Update test cases to use the new fixtures
