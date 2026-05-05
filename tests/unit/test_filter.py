"""Unit tests for ContentFilter."""

import pytest
from mistletoe import Document

from curriculum_extractor.config import Configuration
from curriculum_extractor.filter import ContentFilter


class TestContentFilter:
    """Test ContentFilter class."""

    def test_remove_copyright_section(self):
        """Test removal of copyright section."""
        markdown = """# Copyright
© 2024 KICD

# Strand 1
Content here"""
        doc = Document(markdown)
        config = Configuration()
        filter = ContentFilter(config)
        
        filtered = filter.filter_document(doc)
        headings = [child for child in filtered.children if hasattr(child, "level")]
        assert len(headings) == 1
        assert "Strand" in filter._get_heading_text(headings[0])

    def test_remove_isbn_section(self):
        """Test removal of ISBN section."""
        markdown = """# ISBN
978-1234567890

# Strand 1
Content"""
        doc = Document(markdown)
        config = Configuration()
        filter = ContentFilter(config)
        
        filtered = filter.filter_document(doc)
        headings = [child for child in filtered.children if hasattr(child, "level")]
        assert len(headings) == 1

    def test_remove_table_of_contents(self):
        """Test removal of table of contents."""
        markdown = """# Table of Contents
1. Introduction
2. Strands

# Strand 1
Content"""
        doc = Document(markdown)
        config = Configuration()
        filter = ContentFilter(config)
        
        filtered = filter.filter_document(doc)
        headings = [child for child in filtered.children if hasattr(child, "level")]
        assert len(headings) == 1

    def test_remove_national_goals(self):
        """Test removal of national goals section."""
        markdown = """# National Goals of Education
Goal 1
Goal 2

# Strand 1
Content"""
        doc = Document(markdown)
        config = Configuration()
        filter = ContentFilter(config)
        
        filtered = filter.filter_document(doc)
        headings = [child for child in filtered.children if hasattr(child, "level")]
        assert len(headings) == 1

    def test_remove_foreword(self):
        """Test removal of foreword section."""
        markdown = """# Foreword
This is the foreword.

# Strand 1
Content"""
        doc = Document(markdown)
        config = Configuration()
        filter = ContentFilter(config)
        
        filtered = filter.filter_document(doc)
        headings = [child for child in filtered.children if hasattr(child, "level")]
        assert len(headings) == 1

    def test_remove_preface(self):
        """Test removal of preface section."""
        markdown = """# Preface
This is the preface.

# Strand 1
Content"""
        doc = Document(markdown)
        config = Configuration()
        filter = ContentFilter(config)
        
        filtered = filter.filter_document(doc)
        headings = [child for child in filtered.children if hasattr(child, "level")]
        assert len(headings) == 1

    def test_remove_acknowledgements(self):
        """Test removal of acknowledgements section."""
        markdown = """# Acknowledgements
Thanks to everyone.

# Strand 1
Content"""
        doc = Document(markdown)
        config = Configuration()
        filter = ContentFilter(config)
        
        filtered = filter.filter_document(doc)
        headings = [child for child in filtered.children if hasattr(child, "level")]
        assert len(headings) == 1

    def test_remove_lesson_allocation(self):
        """Test removal of lesson allocation table."""
        markdown = """# Lesson Allocation
| Grade | Lessons |
|-------|---------|
| 1     | 5       |

# Strand 1
Content"""
        doc = Document(markdown)
        config = Configuration()
        filter = ContentFilter(config)
        
        filtered = filter.filter_document(doc)
        headings = [child for child in filtered.children if hasattr(child, "level")]
        assert len(headings) == 1

    def test_preserve_strand_content(self):
        """Test that strand content is preserved."""
        markdown = """# Strand 1: Numbers
## Sub-strand 1.1
Content here"""
        doc = Document(markdown)
        config = Configuration()
        filter = ContentFilter(config)
        
        filtered = filter.filter_document(doc)
        headings = [child for child in filtered.children if hasattr(child, "level")]
        assert len(headings) == 2

    def test_preserve_essence_statement_when_enabled(self):
        """Test essence statement preservation when config is True."""
        markdown = """# Essence Statement
This is the essence.

# Strand 1
Content"""
        doc = Document(markdown)
        config = Configuration(preserve_essence_statement=True)
        filter = ContentFilter(config)
        
        filtered = filter.filter_document(doc)
        headings = [child for child in filtered.children if hasattr(child, "level")]
        assert len(headings) == 2

    def test_remove_essence_statement_when_disabled(self):
        """Test essence statement removal when config is False."""
        markdown = """# Essence Statement
This is the essence.

# Strand 1
Content"""
        doc = Document(markdown)
        config = Configuration(preserve_essence_statement=False)
        filter = ContentFilter(config)
        
        filtered = filter.filter_document(doc)
        headings = [child for child in filtered.children if hasattr(child, "level")]
        assert len(headings) == 1

    def test_preserve_general_outcomes_when_enabled(self):
        """Test general outcomes preservation when config is True."""
        markdown = """# General Learning Outcomes
Outcome 1

# Strand 1
Content"""
        doc = Document(markdown)
        config = Configuration(preserve_general_outcomes=True)
        filter = ContentFilter(config)
        
        filtered = filter.filter_document(doc)
        headings = [child for child in filtered.children if hasattr(child, "level")]
        assert len(headings) == 2

    def test_remove_general_outcomes_when_disabled(self):
        """Test general outcomes removal when config is False."""
        markdown = """# General Learning Outcomes
Outcome 1

# Strand 1
Content"""
        doc = Document(markdown)
        config = Configuration(preserve_general_outcomes=False)
        filter = ContentFilter(config)
        
        filtered = filter.filter_document(doc)
        headings = [child for child in filtered.children if hasattr(child, "level")]
        assert len(headings) == 1

    def test_remove_section_by_name(self):
        """Test remove_section method."""
        markdown = """# Introduction
Some intro text.

# Strand 1
Content"""
        doc = Document(markdown)
        config = Configuration()
        filter = ContentFilter(config)
        
        filtered = filter.remove_section(doc, "Introduction")
        headings = [child for child in filtered.children if hasattr(child, "level")]
        assert len(headings) == 1
        assert "Strand" in filter._get_heading_text(headings[0])

    def test_should_preserve_essence_statement(self):
        """Test should_preserve for essence statement."""
        config_true = Configuration(preserve_essence_statement=True)
        config_false = Configuration(preserve_essence_statement=False)
        
        filter_true = ContentFilter(config_true)
        filter_false = ContentFilter(config_false)
        
        assert filter_true.should_preserve("Essence Statement") is True
        assert filter_false.should_preserve("Essence Statement") is False

    def test_should_preserve_general_outcomes(self):
        """Test should_preserve for general outcomes."""
        config_true = Configuration(preserve_general_outcomes=True)
        config_false = Configuration(preserve_general_outcomes=False)
        
        filter_true = ContentFilter(config_true)
        filter_false = ContentFilter(config_false)
        
        assert filter_true.should_preserve("General Learning Outcomes") is True
        assert filter_false.should_preserve("General Learning Outcomes") is False

    def test_should_preserve_other_sections(self):
        """Test should_preserve returns True for non-special sections."""
        config = Configuration()
        filter = ContentFilter(config)
        
        assert filter.should_preserve("Strand 1") is True
        assert filter.should_preserve("Sub-strand 1.1") is True
