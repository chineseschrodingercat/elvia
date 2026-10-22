"""Offline command-line workflow with located, concise user errors."""

import argparse
import sqlite3
import sys
from pathlib import Path

from elvia.demo import create_demo
from elvia.export import export_records
from elvia.index import rebuild_index
from elvia.site import build_site
from elvia.storage import load_records


def main(argv: list[str] | None = None) -> int:
    """Run a local command; routine data/path errors return a failure status."""
    parser = argparse.ArgumentParser(
        prog="elvia", description="Offline proposition evidence records"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="create an original synthetic dataset")
    demo.add_argument("--output", type=Path, required=True, help="new output directory")
    validate = commands.add_parser("validate", help="validate a record or directory")
    validate.add_argument("input", type=Path)
    index = commands.add_parser("index", help="manage the disposable SQLite index")
    index_commands = index.add_subparsers(dest="index_command", required=True)
    rebuild = index_commands.add_parser("rebuild", help="rebuild from validated JSON")
    rebuild.add_argument("--records", type=Path, required=True)
    rebuild.add_argument("--db", type=Path, required=True)
    export = commands.add_parser(
        "export",
        help="export portable JSON, Markdown, JSONL and artifacts",
        description=(
            "Export to a new directory. A single revision includes its needed "
            "predecessors; the reported count includes all exported snapshots."
        ),
    )
    export.add_argument("input", type=Path)
    export.add_argument("--output", type=Path, required=True)
    site = commands.add_parser("site", help="build the preliminary evidence Atlas")
    site_commands = site.add_subparsers(dest="site_command", required=True)
    build = site_commands.add_parser("build", help="build into a new output directory")
    build.add_argument("--records", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            path = create_demo(args.output)
            print(f"Created pending synthetic demonstration: {path}")
        elif args.command == "validate":
            count = len(load_records(args.input))
            print(f"Validated {count} requested snapshot(s): {args.input}")
        elif args.command == "index":
            count = rebuild_index(args.records, args.db)
            print(f"Indexed {count} snapshot(s): {args.db}")
        elif args.command == "export":
            count = export_records(args.input, args.output)
            print(
                f"Exported {count} snapshot(s), including predecessors: {args.output}"
            )
        elif args.command == "site":
            count = build_site(args.records, args.output)
            print(f"Built Atlas with {count} preliminary case(s): {args.output}")
        return 0
    except (OSError, ValueError, RuntimeError, sqlite3.DatabaseError) as exc:
        print(f"elvia: {exc}", file=sys.stderr)
        return 1
