"""Build the validated collection and maintained website presentation."""

from __future__ import annotations

import argparse
import hashlib
import json
from html import escape
from pathlib import Path

from elvia.search_pages import prepare_index, write_sitemap
from elvia.site import build_site

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ORIGIN = "https://elvia-atlas.org"
COLLECTIONS = ("neurips2025", "icml2025")
PUBLIC_PAGES = (
    "/",
    "/project.html",
    "/contact.html",
    "/participate.html",
    "/research-review-platforms.html",
    "/report-templates.html",
    "/exemplary-cases.html",
    "/privacy.html",
    "/terms.html",
)


def build(output: Path, reader_library: Path | None = None) -> int:
    count = build_site(
        [ROOT / "studies" / name / "records" for name in COLLECTIONS],
        output,
        reader_library=reader_library,
        public_base_url=PUBLIC_ORIGIN + "/atlas/",
    )
    for source in (ROOT / "website/atlas-assets").iterdir():
        if source.name not in {"atlas.css", "atlas.js", "index.html"}:
            raise ValueError("Unexpected presentation asset")
        (output / source.name).write_bytes(source.read_bytes())
    payload = json.loads((output / "data.json").read_text("utf-8"))
    for record in payload["records"]:
        page = output / "cases" / (record["case_id"] + ".html")
        html = page.read_text("utf-8")
        html = html.replace("</nav>", '<a href="/contact.html">Contact</a></nav>', 1)
        html = html.replace("base-uri 'none';", "connect-src 'self'; base-uri 'none';")
        html = html.replace(
            "</head>",
            '<link rel="stylesheet" href="/paper-availability.css">'
            '<script defer src="/paper-availability.js"></script></head>',
        )
        html = html.replace(
            '<p class="detail-citation">',
            '<section class="paper-availability" data-paper-availability="'
            + escape(record["case_id"])
            + '"><h2>Contribution availability</h2>'
            '<p role="status">Checking whether this paper is available… '
            "The editor verifies availability before reserving it.</p></section>"
            '<p class="detail-citation">',
        )
        page.write_text(html, "utf-8")
    prepare_index(output, payload, PUBLIC_ORIGIN + "/atlas/")
    write_sitemap(
        output,
        [PUBLIC_ORIGIN + path for path in PUBLIC_PAGES]
        + [PUBLIC_ORIGIN + "/atlas/"]
        + [
            PUBLIC_ORIGIN + "/atlas/cases/" + r["case_id"] + ".html"
            for r in payload["records"]
        ],
        last_modified={
            PUBLIC_ORIGIN + "/atlas/cases/" + r["case_id"] + ".html": r["created_at"]
            for r in payload["records"]
        },
    )
    files = [
        {
            "path": p.relative_to(output).as_posix(),
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        }
        for p in sorted(output.rglob("*"))
        if p.is_file()
        and p.relative_to(output).as_posix()
        not in {"manifest.json", "integration-files.json"}
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
