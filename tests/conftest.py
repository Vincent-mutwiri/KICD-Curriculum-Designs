"""
Pytest configuration and shared fixtures.
"""
import pytest
from pathlib import Path


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_curriculum_dir(fixtures_dir: Path) -> Path:
    """Return the path to sample curriculum files."""
    return fixtures_dir / "sample_curriculum_files"


@pytest.fixture
def expected_outputs_dir(fixtures_dir: Path) -> Path:
    """Return the path to expected output files."""
    return fixtures_dir / "expected_outputs"


@pytest.fixture
def edge_cases_dir(fixtures_dir: Path) -> Path:
    """Return the path to edge case test files."""
    return fixtures_dir / "edge_cases"


@pytest.fixture
def invalid_files_dir(fixtures_dir: Path) -> Path:
    """Return the path to invalid test files."""
    return fixtures_dir / "invalid_files"
