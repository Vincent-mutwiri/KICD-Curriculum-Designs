#!/bin/bash
# Comprehensive setup verification script

echo "=========================================="
echo "Curriculum Extractor - Setup Verification"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found${NC}"
    echo "  Run: python3 -m venv venv"
    exit 1
fi
echo -e "${GREEN}✓ Virtual environment exists${NC}"

# Check Python version
PYTHON_VERSION=$(./venv/bin/python --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python version: $PYTHON_VERSION${NC}"

# Check if package is installed
if ./venv/bin/pip show curriculum-extractor > /dev/null 2>&1; then
    echo -e "${GREEN}✓ curriculum-extractor package installed${NC}"
else
    echo -e "${RED}✗ curriculum-extractor package not installed${NC}"
    echo "  Run: ./venv/bin/pip install -e \".[dev]\""
    exit 1
fi

echo ""
echo "Core Dependencies:"
echo "------------------"

# Check each core dependency
for package in mistletoe pydantic pytest hypothesis black ruff mypy pyyaml pytest-cov; do
    if ./venv/bin/pip show $package > /dev/null 2>&1; then
        VERSION=$(./venv/bin/pip show $package | grep Version | awk '{print $2}')
        echo -e "${GREEN}✓ $package ($VERSION)${NC}"
    else
        echo -e "${RED}✗ $package not installed${NC}"
    fi
done

echo ""
echo "Import Tests:"
echo "-------------"

# Test imports
./venv/bin/python -c "import mistletoe" 2>/dev/null && echo -e "${GREEN}✓ mistletoe imports successfully${NC}" || echo -e "${RED}✗ mistletoe import failed${NC}"
./venv/bin/python -c "import pydantic" 2>/dev/null && echo -e "${GREEN}✓ pydantic imports successfully${NC}" || echo -e "${RED}✗ pydantic import failed${NC}"
./venv/bin/python -c "import pytest" 2>/dev/null && echo -e "${GREEN}✓ pytest imports successfully${NC}" || echo -e "${RED}✗ pytest import failed${NC}"
./venv/bin/python -c "import hypothesis" 2>/dev/null && echo -e "${GREEN}✓ hypothesis imports successfully${NC}" || echo -e "${RED}✗ hypothesis import failed${NC}"
./venv/bin/python -c "import yaml" 2>/dev/null && echo -e "${GREEN}✓ yaml imports successfully${NC}" || echo -e "${RED}✗ yaml import failed${NC}"

echo ""
echo "CLI Tests:"
echo "----------"

# Test CLI
if ./venv/bin/curriculum-extractor > /dev/null 2>&1; then
    echo -e "${GREEN}✓ CLI entry point works${NC}"
else
    echo -e "${RED}✗ CLI entry point failed${NC}"
fi

# Test pytest
if ./venv/bin/pytest --version > /dev/null 2>&1; then
    PYTEST_VERSION=$(./venv/bin/pytest --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓ pytest command works ($PYTEST_VERSION)${NC}"
else
    echo -e "${RED}✗ pytest command failed${NC}"
fi

echo ""
echo "Running Verification Tests:"
echo "---------------------------"

# Run verification tests
if [ -f "tests/test_installation.py" ]; then
    ./venv/bin/pytest tests/test_installation.py -v --tb=short 2>&1 | grep -E "(PASSED|FAILED|ERROR)" | head -10
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo -e "${GREEN}✓ All verification tests passed${NC}"
    else
        echo -e "${YELLOW}⚠ Some verification tests failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Verification test file not found${NC}"
fi

echo ""
echo "Project Structure:"
echo "------------------"

# Check key directories and files
for item in "src/curriculum_extractor" "tests/unit" "tests/integration" "tests/property" "tests/fixtures" "pyproject.toml" "README.md"; do
    if [ -e "$item" ]; then
        echo -e "${GREEN}✓ $item${NC}"
    else
        echo -e "${RED}✗ $item missing${NC}"
    fi
done

echo ""
echo "=========================================="
echo "Setup Verification Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start implementing Task 2: Pydantic data models"
echo "3. Run tests: pytest"
echo ""
