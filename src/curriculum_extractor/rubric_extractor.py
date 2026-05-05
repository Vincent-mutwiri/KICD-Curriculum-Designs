"""Rubric extraction from curriculum documents."""

from mistletoe.block_token import Table

from .models import RubricCriterion
from .parser import MarkdownParser


class RubricExtractor:
    """Extract assessment rubrics from curriculum documents."""

    def __init__(self, parser: MarkdownParser):
        self.parser = parser

    def extract_rubrics(self, document) -> list[RubricCriterion]:
        """Extract all rubric criteria from document."""
        rubrics = []
        for table in self._walk_tables(document):
            if self.identify_rubric_table(table):
                rubrics.extend(self._parse_rubric_table(table))
        return rubrics

    def identify_rubric_table(self, table: Table) -> bool:
        """Check if table is a rubric table."""
        if not table.header or not table.header.children:
            return False
        
        headers = [self._get_cell_text(cell).strip().lower() for cell in table.header.children]
        
        # Must have indicator/criterion column
        has_indicator = any('indicator' in h or 'criterion' in h for h in headers)
        
        # Must have at least 2 performance levels
        performance_keywords = ['exceed', 'meet', 'approach', 'below']
        performance_count = sum(1 for h in headers if any(kw in h for kw in performance_keywords))
        
        return has_indicator and performance_count >= 2

    def parse_rubric_row(self, row_cells: list, col_map: dict[str, int]) -> RubricCriterion | None:
        """Extract criterion and performance descriptions from a row."""
        criterion = self._get_cell_text(row_cells[col_map['criterion']]).strip()
        if not criterion:
            return None
        
        return RubricCriterion(
            criterion=criterion,
            exceeding_expectations=self._get_cell_text(row_cells[col_map['exceeding']]).strip(),
            meeting_expectations=self._get_cell_text(row_cells[col_map['meeting']]).strip(),
            approaching_expectations=self._get_cell_text(row_cells[col_map['approaching']]).strip(),
            below_expectations=self._get_cell_text(row_cells[col_map['below']]).strip(),
        )

    def _walk_tables(self, node):
        """Walk document tree to find all Table nodes."""
        if isinstance(node, Table):
            yield node
        if hasattr(node, 'children') and node.children is not None:
            for child in node.children:
                yield from self._walk_tables(child)

    def _parse_rubric_table(self, table: Table) -> list[RubricCriterion]:
        """Parse rubric table and extract criteria."""
        if not table.header or not table.children:
            return []
        
        headers = [self._get_cell_text(cell).strip().lower() for cell in table.header.children]
        col_map = self._map_columns(headers)
        
        if not col_map:
            return []
        
        rubrics = []
        for row in table.children:
            if not row.children:
                continue
            
            criterion = self.parse_rubric_row(row.children, col_map)
            if criterion:
                rubrics.append(criterion)
        
        return rubrics

    def _map_columns(self, headers: list[str]) -> dict[str, int]:
        """Map rubric column names to indices."""
        col_map = {}
        
        for i, h in enumerate(headers):
            if 'indicator' in h or 'criterion' in h:
                col_map['criterion'] = i
            elif 'exceed' in h:
                col_map['exceeding'] = i
            elif 'meet' in h and 'exceed' not in h:
                col_map['meeting'] = i
            elif 'approach' in h:
                col_map['approaching'] = i
            elif 'below' in h:
                col_map['below'] = i
        
        # Must have all required columns
        required = ['criterion', 'exceeding', 'meeting', 'approaching', 'below']
        if all(k in col_map for k in required):
            return col_map
        return {}

    def _get_cell_text(self, cell) -> str:
        """Extract text from table cell."""
        if not cell or not hasattr(cell, 'children'):
            return ''
        
        text_parts = []
        for child in cell.children:
            text_parts.append(self._extract_text(child))
        
        return ' '.join(text_parts).strip()

    def _extract_text(self, node) -> str:
        """Recursively extract text from node."""
        from mistletoe.span_token import RawText, Strong, Emphasis
        
        if isinstance(node, RawText):
            return node.content
        
        if isinstance(node, (Strong, Emphasis)):
            return ''.join(self._extract_text(child) for child in node.children)
        
        if hasattr(node, 'children') and node.children:
            return ''.join(self._extract_text(child) for child in node.children)
        
        return ''
