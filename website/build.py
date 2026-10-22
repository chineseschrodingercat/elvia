"""Build the validated collection and maintained website presentation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from elvia.site import build_site

ROOT = Path(__file__).resolve().parents[1]


def build(output: Path, reader_library: Path | None = None) -> int:
    count = build_site(
        ROOT / "studies/neurips2025/records", output, reader_library=reader_library
    )
    for source in (ROOT / "website/atlas-assets").iterdir():
        if source.name not in {"atlas.css", "atlas.js", "index.html"}:
            raise ValueError("Unexpected presentation asset")
        (output / source.name).write_bytes(source.read_bytes())
    files = [
        {
            "path": p.relative_to(output).as_posix(),
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        }
        for p in sorted(output.rglob("*"))
        if p.is_file() and p.name not in {"manifest.json", "integration-files.json"}
    ]
    (output / "manifest.json").write_text(
        json.dumps(
            {"format_version": "1", "case_count": count, "files": files}, indent=2
        )
        + "\n",
        encoding="utf-8",
    )
    files.append(
        {
            "path": "manifest.json",
            "sha256": hashlib.sha256(
                (output / "manifest.json").read_bytes()
            ).hexdigest(),
        }
    )
    (output / "integration-files.json").write_text(
        json.dumps({"schema_version": 1, "files": files}, indent=2) + "\n",
        encoding="utf-8",
    )
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "website/preview/site/atlas"
    )
    parser.add_argument(
        "--reader-library",
        type=Path,
        help="Verified public PDFs and published revision manifest",
    )
    args = parser.parse_args()
    print(f"Built {build(args.output, args.reader_library)} records into {args.output}")
