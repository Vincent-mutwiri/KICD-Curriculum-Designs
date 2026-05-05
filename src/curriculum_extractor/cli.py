"""Command-line interface for the curriculum extractor."""
import argparse
import sys
from pathlib import Path

from .config import Configuration
from .file_processor import FileProcessor


def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Extract and transform curriculum markdown files to JSON"
    )
    parser.add_argument("input", help="Input file or directory")
    parser.add_argument("-o", "--output", help="Output file or directory")
    parser.add_argument("-c", "--config", help="Configuration file (YAML or JSON)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--mongodb-script", action="store_true", help="Generate MongoDB import script")
    parser.add_argument("--pretty-print", action="store_true", help="Pretty print JSON output")
    parser.add_argument("--preserve-essence", action="store_true", help="Preserve essence statement")
    parser.add_argument("--preserve-outcomes", action="store_true", help="Preserve general learning outcomes")

    args = parser.parse_args()

    # Load configuration
    if args.config:
        try:
            config = Configuration.load(args.config)
        except Exception as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            return 1
    else:
        config = Configuration()

    # Override config with CLI options
    if args.pretty_print:
        config.pretty_print = True
    if args.preserve_essence:
        config.preserve_essence_statement = True
    if args.preserve_outcomes:
        config.preserve_general_outcomes = True
    if args.mongodb_script:
        config.mongodb_format = True

    # Process input
    processor = FileProcessor(config)
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Error: Input path does not exist: {args.input}", file=sys.stderr)
        return 1

    try:
        if input_path.is_file():
            if args.verbose:
                print(f"Processing file: {input_path}")
            result = processor.process_file(str(input_path), args.output)
        else:
            if args.verbose:
                print(f"Processing directory: {input_path}")
            result = processor.process_directory(str(input_path), args.output)

        # Display results
        if result.status == "success":
            print(f"✓ Success: {result.files_succeeded} file(s) processed")
            return 0
        elif result.status == "partial":
            print(f"⚠ Partial: {result.files_succeeded} succeeded, {result.files_failed} failed")
            if args.verbose and result.errors:
                for error in result.errors:
                    print(f"  - {error}")
            return 1
        else:
            print(f"✗ Failed: {result.errors[0] if result.errors else 'Unknown error'}")
            if args.verbose and len(result.errors) > 1:
                for error in result.errors[1:]:
                    print(f"  - {error}")
            return 1

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
