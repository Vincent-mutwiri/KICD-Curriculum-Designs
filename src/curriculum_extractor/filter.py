"""Content filtering to remove extraneous sections from curriculum documents."""

from mistletoe import Document
from mistletoe.block_token import Heading

from curriculum_extractor.config import Configuration


class ContentFilter:
    """Filter extraneous content from parsed curriculum documents."""

    EXTRANEOUS_SECTIONS = {
        "copyright",
        "isbn",
        "table of contents",
        "national goals of education",
        "foreword",
        "preface",
        "acknowledgement",
        "acknowledgements",
        "lesson allocation",
        "time allocation",
    }

    def __init__(self, config: Configuration):
        self.config = config

    def filter_document(self, document: Document) -> Document:
        """Remove extraneous sections from document."""
        children = list(document.children or [])
        filtered = []
        skip_until_next_heading = False

        for i, child in enumerate(children):
            if isinstance(child, Heading):
                heading_text = self._get_heading_text(child).lower()
                
                if self._is_extraneous_section(heading_text):
                    skip_until_next_heading = True
                    continue
                elif not self.should_preserve(heading_text):
                    skip_until_next_heading = True
                    continue
                else:
                    skip_until_next_heading = False
                    filtered.append(child)
            elif not skip_until_next_heading:
                filtered.append(child)

        document.children = filtered
        return document

    def remove_section(self, document: Document, section_name: str) -> Document:
        """Remove a specific section by name."""
        children = list(document.children or [])
        filtered = []
        skip_until_next_heading = False
        target = section_name.lower()

        for child in children:
            if isinstance(child, Heading):
                heading_text = self._get_heading_text(child).lower()
                if target in heading_text:
                    skip_until_next_heading = True
                    continue
                else:
                    skip_until_next_heading = False
                    filtered.append(child)
            elif not skip_until_next_heading:
                filtered.append(child)

        document.children = filtered
        return document

    def should_preserve(self, heading_text: str) -> bool:
        """Check if section should be preserved based on configuration."""
        heading_lower = heading_text.lower()
        
        if "essence statement" in heading_lower:
            return self.config.preserve_essence_statement
        
        if "general" in heading_lower and "outcome" in heading_lower:
            return self.config.preserve_general_outcomes
        
        return True

    def _is_extraneous_section(self, heading_text: str) -> bool:
        """Check if heading matches extraneous section patterns."""
        return any(pattern in heading_text for pattern in self.EXTRANEOUS_SECTIONS)

    def _get_heading_text(self, heading: Heading) -> str:
        """Extract text content from heading node."""
        children = getattr(heading, "children", None) or []
        parts = []
        for child in children:
            content = getattr(child, "content", None)
            if content:
                parts.append(str(content))
        return "".join(parts).strip()
