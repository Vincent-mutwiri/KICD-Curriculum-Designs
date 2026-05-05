"""
Test to verify all dependencies are properly installed and working.
"""
import pytest


def test_pytest_is_working():
    """Verify pytest is working."""
    assert True


def test_mistletoe_import():
    """Verify mistletoe can be imported."""
    import mistletoe
    assert mistletoe.__version__


def test_pydantic_import():
    """Verify pydantic v2 can be imported."""
    import pydantic
    assert pydantic.__version__.startswith("2.")


def test_hypothesis_import():
    """Verify hypothesis can be imported."""
    import hypothesis
    assert hypothesis.__version__


def test_yaml_import():
    """Verify PyYAML can be imported."""
    import yaml
    assert yaml


def test_coverage_import():
    """Verify coverage can be imported."""
    import coverage
    assert coverage


class TestPydanticV2Features:
    """Test that Pydantic v2 features work correctly."""
    
    def test_pydantic_v2_model(self):
        """Test creating a Pydantic v2 model."""
        from pydantic import BaseModel, Field
        
        class TestModel(BaseModel):
            name: str
            value: int = Field(ge=0, le=100)
        
        model = TestModel(name="test", value=50)
        assert model.name == "test"
        assert model.value == 50
    
    def test_pydantic_v2_validation(self):
        """Test Pydantic v2 validation."""
        from pydantic import BaseModel, Field, ValidationError
        
        class TestModel(BaseModel):
            grade: int = Field(ge=1, le=12)
        
        # Valid grade
        model = TestModel(grade=10)
        assert model.grade == 10
        
        # Invalid grade should raise ValidationError
        with pytest.raises(ValidationError):
            TestModel(grade=13)


class TestHypothesisIntegration:
    """Test that Hypothesis property-based testing works."""
    
    def test_hypothesis_basic(self):
        """Test basic hypothesis functionality."""
        from hypothesis import given, strategies as st
        
        @given(st.integers())
        def property_test(x):
            assert isinstance(x, int)
        
        property_test()
    
    def test_hypothesis_with_pydantic(self):
        """Test hypothesis with Pydantic models."""
        from hypothesis import given, strategies as st
        from pydantic import BaseModel
        
        class SimpleModel(BaseModel):
            value: str
        
        @given(st.text())
        def property_test(text):
            model = SimpleModel(value=text)
            assert model.value == text
        
        property_test()
