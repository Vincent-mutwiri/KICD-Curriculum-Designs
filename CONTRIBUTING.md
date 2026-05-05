# Contributing to Curriculum Data Extractor

Thank you for your interest in contributing to the Curriculum Data Extractor project!

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git

### Setting Up Your Development Environment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd curriculum-extractor
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the package in development mode**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Verify the installation**
   ```bash
   curriculum-extractor
   pytest --version
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=curriculum_extractor --cov-report=html

# Run specific test types
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/property/      # Property-based tests only

# Run a specific test file
pytest tests/unit/test_parser.py

# Run tests matching a pattern
pytest -k "test_metadata"
```

### Code Quality

#### Format Code with Black

```bash
black src/ tests/
```

#### Lint Code with Ruff

```bash
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/
```

#### Type Checking with MyPy

```bash
mypy src/
```

#### Run All Quality Checks

```bash
# Format
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/

# Test
pytest
```

## Project Structure

```
curriculum-extractor/
├── src/
│   └── curriculum_extractor/     # Main package
│       ├── __init__.py
│       ├── cli.py               # Command-line interface
│       ├── config.py            # Configuration management
│       ├── parser.py            # Markdown parsing
│       ├── extractors/          # Data extraction components
│       ├── transformers/        # Data transformation components
│       └── validators/          # Data validation components
├── tests/
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   ├── property/                # Property-based tests
│   ├── fixtures/                # Test data
│   └── conftest.py              # Pytest configuration
├── examples/                    # Example usage
├── pyproject.toml              # Project configuration
├── README.md                   # User documentation
└── CONTRIBUTING.md             # This file
```

## Coding Standards

### Python Style

- Follow PEP 8 style guide
- Use Black for code formatting (line length: 100)
- Use type hints for all function signatures
- Write docstrings for all public classes and functions

### Docstring Format

Use Google-style docstrings:

```python
def extract_metadata(filename: str) -> Metadata:
    """Extract metadata from curriculum filename.
    
    Args:
        filename: The curriculum file name to parse.
        
    Returns:
        A Metadata object containing subject, grade, and year.
        
    Raises:
        ValueError: If the filename format is invalid.
    """
    pass
```

### Type Hints

Always include type hints:

```python
from typing import List, Optional
from pathlib import Path

def process_file(
    input_path: Path,
    output_path: Optional[Path] = None
) -> ProcessingResult:
    """Process a curriculum file."""
    pass
```

## Testing Guidelines

### Unit Tests

- Test individual functions and methods
- Mock external dependencies
- Use descriptive test names: `test_<function>_<scenario>_<expected_result>`
- Include edge cases and error conditions

Example:
```python
def test_parse_grade_single_grade_returns_integer():
    """Test that parsing 'Grade 10' returns integer 10."""
    result = parse_grade("Grade 10")
    assert result == 10
```

### Integration Tests

- Test complete workflows end-to-end
- Use real test fixtures
- Verify output correctness

### Property-Based Tests

- Use Hypothesis to generate test data
- Test universal properties that should hold for all inputs
- Tag tests with property references from design document

Example:
```python
from hypothesis import given, strategies as st

# Feature: curriculum-data-extractor, Property 6: Subject Name Normalization Idempotence
@given(st.text())
def test_subject_normalization_is_idempotent(subject: str):
    """Normalizing twice should produce same result as normalizing once."""
    normalized_once = normalize_subject(subject)
    normalized_twice = normalize_subject(normalized_once)
    assert normalized_once == normalized_twice
```

## Adding New Features

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write tests first** (TDD approach)
   - Write unit tests for new functionality
   - Write integration tests if needed
   - Write property tests for universal properties

3. **Implement the feature**
   - Follow coding standards
   - Add type hints
   - Write docstrings

4. **Run quality checks**
   ```bash
   black src/ tests/
   ruff check src/ tests/
   mypy src/
   pytest
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

6. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Pull Request Guidelines

- Ensure all tests pass
- Maintain or improve code coverage
- Update documentation if needed
- Write clear commit messages
- Reference related issues

## Questions or Issues?

- Open an issue on the project repository
- Provide detailed information about the problem
- Include steps to reproduce if reporting a bug

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
