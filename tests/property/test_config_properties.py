"""Property-based tests for Configuration Manager."""

import tempfile
from pathlib import Path

import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

from curriculum_extractor.config import Configuration


@given(
    preserve_essence=st.booleans(),
    preserve_outcomes=st.booleans(),
    output_dir=st.text(
        min_size=1, alphabet=st.characters(blacklist_categories=("Cc", "Cs"))
    ).filter(lambda x: x.strip()),
    pretty=st.booleans(),
    indent=st.integers(min_value=0, max_value=8),
    strategy=st.sampled_from(["split", "single"]),
    mongodb=st.booleans(),
)
@settings(deadline=None)
def test_configuration_loading_consistency(
    preserve_essence: bool,
    preserve_outcomes: bool,
    output_dir: str,
    pretty: bool,
    indent: int,
    strategy: str,
    mongodb: bool,
) -> None:
    """
    Property 22: Configuration Loading Consistency.

    Validates: Requirements 23.3, 23.4, 23.5, 23.6, 23.7

    Verify that loading the same configuration file multiple times
    produces identical Configuration objects.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_file = Path(tmp_dir) / "test_config.yaml"

        # Use YAML dump to properly escape values
        config_data = {
            "preserve_essence_statement": preserve_essence,
            "preserve_general_outcomes": preserve_outcomes,
            "output_directory": output_dir,
            "pretty_print": pretty,
            "indent_size": indent,
            "grade_range_strategy": strategy,
            "mongodb_format": mongodb,
        }
        config_file.write_text(yaml.dump(config_data))

        # Load the same configuration file multiple times
        config1 = Configuration.load(config_file)
        config2 = Configuration.load(config_file)
        config3 = Configuration.load(config_file)

        # All loaded configurations should be identical
        assert config1 == config2
        assert config2 == config3
        assert config1 == config3

        # Verify all fields match
        assert config1.preserve_essence_statement == config2.preserve_essence_statement
        assert config1.preserve_general_outcomes == config2.preserve_general_outcomes
        assert config1.output_directory == config2.output_directory
        assert config1.pretty_print == config2.pretty_print
        assert config1.indent_size == config2.indent_size
        assert config1.grade_range_strategy == config2.grade_range_strategy
        assert config1.mongodb_format == config2.mongodb_format
