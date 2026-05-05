# Quick Start Guide

## ✅ Installation Complete!

All dependencies are installed and verified. You're ready to start development!

## Verify Installation

Run the verification script:

```bash
./verify_setup.sh
```

Expected output: All checks should show ✓ (green checkmarks)

## Activate Virtual Environment

```bash
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate     # On Windows
```

## Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=curriculum_extractor --cov-report=html

# Run specific test types
pytest tests/unit/
pytest tests/integration/
pytest tests/property/

# Run verification tests
pytest tests/test_installation.py -v
```

## Development Commands

### Code Formatting

```bash
# Format code with Black
black src/ tests/

# Check formatting without changes
black --check src/ tests/
```

### Linting

```bash
# Lint with Ruff
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/
```

### Type Checking

```bash
# Type check with MyPy
mypy src/
```

### Run All Quality Checks

```bash
# Format, lint, type check, and test
black src/ tests/ && \
ruff check src/ tests/ && \
mypy src/ && \
pytest
```

## CLI Usage

```bash
# Run the CLI (placeholder for now)
curriculum-extractor

# Or with Python
python -m curriculum_extractor.cli
```

## Project Structure

```
curriculum-extractor/
├── src/
│   └── curriculum_extractor/     # Main package
│       ├── __init__.py
│       └── cli.py
├── tests/
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── property/                 # Property-based tests
│   ├── fixtures/                 # Test data
│   ├── conftest.py              # Pytest config
│   └── test_installation.py     # Verification tests
├── examples/
│   ├── config.example.yaml      # Example config
│   └── README.md
├── venv/                        # Virtual environment
├── pyproject.toml              # Project config
├── README.md                   # User docs
├── CONTRIBUTING.md             # Dev docs
├── INSTALLATION_VERIFIED.md    # Installation report
├── QUICK_START.md             # This file
└── verify_setup.sh            # Verification script
```

## Installed Dependencies

### Core Dependencies
- ✅ **mistletoe 1.5.1** - Markdown parsing
- ✅ **pydantic 2.13.3** - Data validation
- ✅ **pyyaml 6.0.3** - Configuration files

### Development Dependencies
- ✅ **pytest 9.0.3** - Testing framework
- ✅ **pytest-cov 7.1.0** - Coverage reporting
- ✅ **hypothesis 6.152.4** - Property-based testing
- ✅ **black 26.3.1** - Code formatting
- ✅ **ruff 0.15.12** - Fast linting
- ✅ **mypy 1.20.2** - Type checking

## Next Steps

### Task 2: Implement Pydantic Data Models

Start implementing the data models as specified in the tasks:

1. Open `src/curriculum_extractor/models.py` (create it)
2. Implement the Pydantic models:
   - `Competency`
   - `Value`
   - `SubStrand`
   - `RubricCriterion`
   - `Strand`
   - `GradeRange`
   - `CurriculumDocument`
3. Add field validators
4. Write unit tests in `tests/unit/test_models.py`
5. Write property tests in `tests/property/test_models_validation.py`

### Reference Documents

- **Requirements:** `.kiro/specs/curriculum-data-extractor/requirements.md`
- **Design:** `.kiro/specs/curriculum-data-extractor/design.md`
- **Tasks:** `.kiro/specs/curriculum-data-extractor/tasks.md`

## Troubleshooting

### If dependencies are missing:

```bash
./venv/bin/pip install -e ".[dev]"
```

### If tests fail:

```bash
# Check what's installed
./venv/bin/pip list

# Verify imports
./venv/bin/python -c "import mistletoe, pydantic, pytest, hypothesis"

# Run verification tests
pytest tests/test_installation.py -v
```

### If virtual environment is broken:

```bash
# Remove and recreate
rm -rf venv
python3 -m venv venv
./venv/bin/pip install -e ".[dev]"
```

## Getting Help

- Check `CONTRIBUTING.md` for development guidelines
- Check `README.md` for project overview
- Check `INSTALLATION_VERIFIED.md` for detailed verification report
- Run `./verify_setup.sh` to check your setup

## Ready to Code! 🚀

Your development environment is fully configured and all dependencies are verified. Start implementing Task 2!
