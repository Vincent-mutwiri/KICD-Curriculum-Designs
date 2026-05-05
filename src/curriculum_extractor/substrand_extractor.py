"""SubStrand extraction from curriculum documents."""

import re
from dataclasses import dataclass
from mistletoe.block_token import Table
from mistletoe.span_token import RawText, Strong, Emphasis

from .parser import MarkdownParser


@dataclass(frozen=True)
class SubStrandData:
    """Data extracted from a sub-strand."""

    sub_strand_id: str
    sub_strand_name: str
    topics: list[str]
    specific_learning_outcomes: list[str]
    suggested_learning_experiences: list[str]
    key_inquiry_questions: list[str]


class SubStrandExtractor:
    """Extract sub-strands from curriculum documents."""

    def __init__(self, parser: MarkdownParser):
        self.parser = parser

    def extract_substrands(
        self, document, start_line: int | None = None, end_line: int | None = None
    ) -> list[SubStrandData]:
        """Extract all sub-strands from document or within line range."""
        substrands = []
        for table in self._walk_tables(document):
            if self._is_substrand_table(table):
                substrands.extend(self._extract_table_content(table))
        
        # Filter by line range if specified
        if start_line is not None or end_line is not None:
            filtered = []
            for substrand in substrands:
                line_num = getattr(substrand, '_line_number', None)
                if line_num is not None:
                    if start_line is not None and line_num < start_line:
                        continue
                    if end_line is not None and line_num > end_line:
                        continue
                filtered.append(substrand)
            return filtered
        
        return substrands

    def _walk_tables(self, node):
        """Walk document tree to find all Table nodes."""
        if isinstance(node, Table):
            yield node
        if hasattr(node, 'children') and node.children is not None:
            for child in node.children:
                yield from self._walk_tables(child)

    def _is_substrand_table(self, table: Table) -> bool:
        """Check if table is a sub-strand table."""
        if not table.header or not table.header.children:
            return False
        
        headers = [self._get_cell_text(cell).strip().lower() for cell in table.header.children]
        required = ['sub-strand', 'specific learning', 'suggested learning experience']
        return all(any(req in h for h in headers) for req in required)

    def _extract_table_content(self, table: Table) -> list[SubStrandData]:
        """Extract sub-strands from table."""
        if not table.header or not table.children:
            return []
        
        headers = [self._get_cell_text(cell).strip().lower() for cell in table.header.children]
        col_map = self._map_columns(headers)
        
        substrands = []
        current_substrand = None
        
        for row in table.children:
            if not row.children:
                continue
            
            cells = [self._get_cell_text(cell) for cell in row.children]
            
            # Check if this row starts a new sub-strand
            substrand_cell = cells[col_map['substrand']] if col_map['substrand'] < len(cells) else ''
            if self._is_substrand_header(substrand_cell):
                if current_substrand:
                    substrands.append(self._build_substrand(current_substrand))
                current_substrand = {
                    'id': '',
                    'name': '',
                    'topics': [],
                    'outcomes': [],
                    'experiences': [],
                    'questions': []
                }
                self._parse_substrand_header(substrand_cell, current_substrand)
            
            # Accumulate data for current sub-strand
            if current_substrand:
                if col_map['outcomes'] < len(cells):
                    outcomes = self.parse_learning_outcomes(cells[col_map['outcomes']])
                    current_substrand['outcomes'].extend(outcomes)
                
                if col_map['experiences'] < len(cells):
                    experiences = self.parse_learning_experiences(cells[col_map['experiences']])
                    current_substrand['experiences'].extend(experiences)
                
                if col_map['questions'] < len(cells):
                    questions = self.parse_inquiry_questions(cells[col_map['questions']])
                    current_substrand['questions'].extend(questions)
        
        if current_substrand:
            substrands.append(self._build_substrand(current_substrand))
        
        return substrands

    def _map_columns(self, headers: list[str]) -> dict[str, int]:
        """Map column names to indices."""
        col_map = {'substrand': -1, 'outcomes': -1, 'experiences': -1, 'questions': -1}
        
        for i, header in enumerate(headers):
            if 'sub-strand' in header or 'sub strand' in header:
                col_map['substrand'] = i
            elif 'specific learning' in header and 'outcome' in header:
                col_map['outcomes'] = i
            elif 'suggested learning experience' in header:
                col_map['experiences'] = i
            elif 'inquiry question' in header or 'key inquiry' in header:
                col_map['questions'] = i
        
        return col_map

    def _is_substrand_header(self, text: str) -> bool:
        """Check if text is a sub-strand header."""
        text = text.strip()
        pattern = r'^\*?\*?\d+\.\d+\s+'
        return bool(re.match(pattern, text))

    def _parse_substrand_header(self, text: str, data: dict):
        """Parse sub-strand ID and name from header."""
        text = text.strip().strip('*')
        match = re.match(r'^(\d+\.\d+)\s+(.+)', text)
        if match:
            data['id'] = match.group(1)
            data['name'] = match.group(2).strip()
            # Extract topics from name (text in parentheses or after bullets)
            topics = self._extract_topics(data['name'])
            data['topics'] = topics

    def _extract_topics(self, name: str) -> list[str]:
        """Extract topics from sub-strand name."""
        topics = []
        # Extract text in parentheses (lesson count and topics)
        paren_match = re.search(r'\(([^)]+)\)', name)
        if paren_match:
            content = paren_match.group(1)
            # Split by bullets or newlines
            items = re.split(r'[•●○]\s*|\n', content)
            for item in items:
                item = item.strip().strip('*').strip()
                # Skip lesson count
                if 'lesson' not in item.lower() and item:
                    topics.append(item)
        return topics

    def _build_substrand(self, data: dict) -> SubStrandData:
        """Build SubStrandData from accumulated data."""
        return SubStrandData(
            sub_strand_id=data['id'],
            sub_strand_name=data['name'],
            topics=data['topics'],
            specific_learning_outcomes=data['outcomes'],
            suggested_learning_experiences=data['experiences'],
            key_inquiry_questions=data['questions']
        )

    def parse_learning_outcomes(self, text: str) -> list[str]:
        """Extract and clean learning outcomes from text."""
        if not text or not text.strip():
            return []
        
        # Remove the preamble (simpler approach)
        if text.lower().startswith('by the end'):
            idx = text.lower().find('able to:')
            if idx != -1:
                text = text[idx + 8:].strip()
        
        return self._parse_list_items(text)

    def parse_learning_experiences(self, text: str) -> list[str]:
        """Extract learning experiences from text."""
        if not text or not text.strip():
            return []
        
        # Remove the preamble (simpler approach)
        if text.lower().startswith('the learner is guided'):
            idx = text.lower().find('guided to:')
            if idx != -1:
                text = text[idx + 10:].strip()
        
        return self._parse_list_items(text)

    def parse_inquiry_questions(self, text: str) -> list[str]:
        """Extract inquiry questions from text."""
        items = self._parse_list_items(text)
        # Further split on numbered questions like "1. " or "2. "
        result = []
        for item in items:
            # Split on question numbers
            parts = re.split(r'\s+\d+\.\s+', item)
            for part in parts:
                part = part.strip()
                if part:
                    result.append(part)
        return result

    def _parse_list_items(self, text: str) -> list[str]:
        """Parse list items from text, removing formatting."""
        if not text or not text.strip():
            return []
        
        # Split by common list markers (don't require newline before letter markers)
        items = re.split(r'[•●○]\s*|(?:^|\s+)[a-z]\)\s*|(?:^|\n)\s*\d+\.\s*|(?:^|\n)\s*\d+\)\s*', text)
        
        # Clean each item
        cleaned = []
        for item in items:
            item = item.strip()
            if not item:
                continue
            # Remove bold/italic markers
            item = re.sub(r'\*\*([^*]+)\*\*', r'\1', item)
            item = re.sub(r'\*([^*]+)\*', r'\1', item)
            item = re.sub(r'_([^_]+)_', r'\1', item)
            # Remove trailing commas and periods
            item = item.rstrip('.,')
            item = item.strip()
            if item:
                cleaned.append(item)
        
        return cleaned

    def _get_cell_text(self, cell) -> str:
        """Extract text from table cell."""
        if hasattr(cell, 'children') and cell.children:
            return ''.join(self._extract_text(child) for child in cell.children)
        return ''

    def _extract_text(self, node) -> str:
        """Recursively extract text from node."""
        if isinstance(node, RawText):
            return node.content
        if isinstance(node, str):
            return node
        if isinstance(node, (Strong, Emphasis)):
            return ''.join(self._extract_text(child) for child in node.children)
        if hasattr(node, 'children') and node.children:
            return ''.join(self._extract_text(child) for child in node.children)
        return ''
