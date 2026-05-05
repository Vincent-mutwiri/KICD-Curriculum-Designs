"""Unit tests for SubStrandExtractor."""

import pytest

from curriculum_extractor import MarkdownParser, SubStrandExtractor


class TestSubStrandExtractor:
    """Test SubStrandExtractor functionality."""

    @pytest.fixture
    def parser(self):
        return MarkdownParser()

    @pytest.fixture
    def extractor(self, parser):
        return SubStrandExtractor(parser)

    def test_extract_substrands_from_table(self, parser, extractor):
        """Test extraction of sub-strands from a table."""
        markdown = """
| Strand | Sub-Strand | Specific Learning Outcomes | Suggested Learning Experiences | Suggested Key Inquiry Question(s) |
|--------|------------|----------------------------|--------------------------------|-----------------------------------|
| 1.0 Numbers | **1.1 Pre-number activities** (20 lessons) | By the end of the sub strand, the learner should be able to: a) sort objects, b) match objects | The learner is guided to: ● collect objects, ● group objects | 1. How can we group? 2. How can we arrange? |
"""
        document = parser.parse_string(markdown)
        substrands = extractor.extract_substrands(document)

        assert len(substrands) == 1
        assert substrands[0].sub_strand_id == "1.1"
        assert "Pre-number activities" in substrands[0].sub_strand_name

    def test_parse_learning_outcomes(self, extractor):
        """Test parsing of learning outcomes."""
        text = "By the end of the sub strand, the learner should be able to: a) sort objects, b) match objects, c) order objects"
        outcomes = extractor.parse_learning_outcomes(text)

        assert len(outcomes) == 3
        assert "sort objects" in outcomes[0]
        assert "match objects" in outcomes[1]
        assert "order objects" in outcomes[2]

    def test_parse_learning_outcomes_removes_preamble(self, extractor):
        """Test that preamble is removed from outcomes."""
        text = "By the end of the sub strand, the learner should be able to: a) sort objects"
        outcomes = extractor.parse_learning_outcomes(text)

        assert len(outcomes) == 1
        assert outcomes[0] == "sort objects"
        assert "By the end" not in outcomes[0]

    def test_parse_learning_experiences(self, extractor):
        """Test parsing of learning experiences."""
        text = "The learner is guided to: ● collect objects, ● group objects, ● arrange objects"
        experiences = extractor.parse_learning_experiences(text)

        assert len(experiences) == 3
        assert "collect objects" in experiences[0]
        assert "group objects" in experiences[1]

    def test_parse_learning_experiences_removes_preamble(self, extractor):
        """Test that preamble is removed from experiences."""
        text = "The learner is guided to: ● collect objects"
        experiences = extractor.parse_learning_experiences(text)

        assert len(experiences) == 1
        assert experiences[0] == "collect objects"
        assert "guided to" not in experiences[0]

    def test_parse_inquiry_questions(self, extractor):
        """Test parsing of inquiry questions."""
        text = "1. How can we group objects? 2. How can we arrange objects?"
        questions = extractor.parse_inquiry_questions(text)

        assert len(questions) == 2
        assert "How can we group objects?" in questions[0]
        assert "How can we arrange objects?" in questions[1]

    def test_parse_list_items_with_bullets(self, extractor):
        """Test parsing list items with bullet markers."""
        text = "● item one ● item two ● item three"
        items = extractor._parse_list_items(text)

        assert len(items) == 3
        assert "item one" in items[0]
        assert "item two" in items[1]

    def test_parse_list_items_with_letters(self, extractor):
        """Test parsing list items with letter markers."""
        text = "a) first item b) second item c) third item"
        items = extractor._parse_list_items(text)

        assert len(items) == 3
        assert "first item" in items[0]
        assert "second item" in items[1]

    def test_parse_list_items_with_numbers(self, extractor):
        """Test parsing list items with number markers."""
        text = "1. first item\n2. second item\n3. third item"
        items = extractor._parse_list_items(text)

        assert len(items) == 3
        assert "first item" in items[0]

    def test_parse_list_items_removes_bold(self, extractor):
        """Test that bold markers are removed."""
        text = "● **bold item** ● normal item"
        items = extractor._parse_list_items(text)

        assert len(items) == 2
        assert items[0] == "bold item"
        assert "**" not in items[0]

    def test_parse_list_items_removes_italic(self, extractor):
        """Test that italic markers are removed."""
        text = "● *italic item* ● _underline item_"
        items = extractor._parse_list_items(text)

        assert len(items) == 2
        assert items[0] == "italic item"
        assert items[1] == "underline item"
        assert "*" not in items[0]
        assert "_" not in items[1]

    def test_parse_list_items_removes_trailing_punctuation(self, extractor):
        """Test that trailing commas and periods are removed."""
        text = "a) first item, b) second item."
        items = extractor._parse_list_items(text)

        assert len(items) == 2
        assert items[0] == "first item"
        assert items[1] == "second item"
        assert not items[0].endswith(",")
        assert not items[1].endswith(".")

    def test_extract_topics_from_substrand_name(self, extractor):
        """Test extraction of topics from sub-strand name."""
        name = "Pre-number activities (20 lessons • Sorting • Matching • Ordering)"
        topics = extractor._extract_topics(name)

        assert len(topics) == 3
        assert "Sorting" in topics
        assert "Matching" in topics
        assert "Ordering" in topics
        assert "20 lessons" not in " ".join(topics)

    def test_is_substrand_header(self, extractor):
        """Test identification of sub-strand headers."""
        assert extractor._is_substrand_header("1.1 Pre-number activities")
        assert extractor._is_substrand_header("**1.2 Whole Numbers**")
        assert extractor._is_substrand_header("2.1 Length")
        assert not extractor._is_substrand_header("Not a substrand")
        # Note: 1.0 matches the pattern, but context determines if it's a strand or sub-strand

    def test_extract_substrands_empty_document(self, parser, extractor):
        """Test extraction from empty document."""
        markdown = "# Empty Document\n\nNo tables here."
        document = parser.parse_string(markdown)
        substrands = extractor.extract_substrands(document)

        assert len(substrands) == 0

    def test_multi_row_substrand(self, parser, extractor):
        """Test handling of multi-row sub-strands in tables."""
        markdown = """
| Strand | Sub-Strand | Specific Learning Outcomes | Suggested Learning Experiences | Suggested Key Inquiry Question(s) |
|--------|------------|----------------------------|--------------------------------|-----------------------------------|
| 1.0 Numbers | **1.1 Activities** | By the end of the sub strand, the learner should be able to: a) sort objects | The learner is guided to: ● collect objects | How can we group? |
|  |  | b) match objects | ● group objects | How can we arrange? |
"""
        document = parser.parse_string(markdown)
        substrands = extractor.extract_substrands(document)

        assert len(substrands) == 1
        # Should accumulate outcomes and experiences from multiple rows
        assert len(substrands[0].specific_learning_outcomes) >= 2
        assert len(substrands[0].suggested_learning_experiences) >= 2
