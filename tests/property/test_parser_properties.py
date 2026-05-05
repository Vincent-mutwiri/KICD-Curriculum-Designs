"""Property tests for markdown parser structure preservation."""

import string
from typing import Any

from hypothesis import given, settings
from hypothesis import strategies as st

from curriculum_extractor.parser import MarkdownList, MarkdownParser

cell_text = st.text(
    alphabet=string.ascii_letters + string.digits + " ",
    min_size=1,
    max_size=20,
).map(str.strip).filter(bool)


@st.composite
def markdown_tables(draw: st.DrawFn) -> tuple[list[str], list[list[str]], str]:
    column_count = draw(st.integers(min_value=1, max_value=6))
    row_count = draw(st.integers(min_value=1, max_value=8))
    headers = draw(st.lists(cell_text, min_size=column_count, max_size=column_count))
    rows = [
        draw(st.lists(cell_text, min_size=column_count, max_size=column_count))
        for _ in range(row_count)
    ]

    markdown_lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in range(column_count)) + " |",
    ]
    markdown_lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return headers, rows, "\n".join(markdown_lines)


@given(table_data=markdown_tables())
@settings(deadline=None)
def test_property_2_table_structure_preservation(
    table_data: tuple[list[str], list[list[str]], str],
) -> None:
    headers, rows, markdown = table_data

    tables = MarkdownParser().extract_tables(MarkdownParser().parse_string(markdown))

    assert len(tables) == 1
    assert tables[0].headers == headers
    assert len(tables[0].rows) == len(rows)
    for row_index, row in enumerate(rows):
        assert len(tables[0].rows[row_index]) == len(row)
        for column_index, expected_cell in enumerate(row):
            assert tables[0].rows[row_index][column_index] == expected_cell


list_node_strategy = st.recursive(
    st.builds(lambda text: {"text": text, "children": []}, cell_text),
    lambda children: st.builds(
        lambda text, nested: {"text": text, "children": nested},
        cell_text,
        st.lists(children, min_size=0, max_size=3),
    ),
    max_leaves=12,
)


@st.composite
def nested_list_documents(draw: st.DrawFn) -> tuple[list[dict[str, Any]], str]:
    nodes = draw(st.lists(list_node_strategy, min_size=1, max_size=5))
    lines: list[str] = []
    _render_list_nodes(nodes, lines, depth=0)
    return nodes, "\n".join(lines)


def _render_list_nodes(nodes: list[dict[str, Any]], lines: list[str], depth: int) -> None:
    indent = "  " * depth
    for node in nodes:
        lines.append(f"{indent}- {node['text']}")
        _render_list_nodes(node["children"], lines, depth + 1)


@given(list_data=nested_list_documents())
@settings(deadline=None)
def test_property_3_hierarchical_structure_preservation(
    list_data: tuple[list[dict[str, Any]], str],
) -> None:
    expected_nodes, markdown = list_data

    lists = MarkdownParser().extract_lists(MarkdownParser().parse_string(markdown))

    assert len(lists) == 1
    _assert_list_matches_nodes(lists[0], expected_nodes)


def _assert_list_matches_nodes(markdown_list: MarkdownList, nodes: list[dict[str, Any]]) -> None:
    assert len(markdown_list.items) == len(nodes)
    for item, node in zip(markdown_list.items, nodes, strict=True):
        assert item.text == node["text"]
        assert len(item.children) == (1 if node["children"] else 0)
        if node["children"]:
            _assert_list_matches_nodes(item.children[0], node["children"])
