"""Build a new, portable preliminary Atlas from validated authoritative snapshots."""

import hashlib
import json
import shutil
import tempfile
import zipfile
from collections import Counter
from collections.abc import Sequence
from importlib.resources import files
from os import PathLike
from pathlib import Path

from elvia.case_notes import prepare_case_notes
from elvia.export import export_records
from elvia.math_presentation import prepare_presentation
from elvia.reader import prepare_reader, write_reader_bundle
from elvia.research_fields import prepare_research_fields
from elvia.search_pages import write_search_pages
from elvia.storage import load_records

OUTCOMES = (
    "no_issue_found",
    "scope_clarification",
    "candidate_issue",
    "known_issue_reproduced",
    "needs_evidence",
)
# Unmodified Adobe font software and its complete upstream notices. See
# docs/font-sources.md for pinned source URLs, versions and original byte sizes.
FONT_HASHES = {
    "SourceSerif4Variable-Roman.otf.woff2": (
        "f146ee102dddcc5bc7a2cf4af5bcf129832195941b92bd0a512626f390688c1e"
    ),
    "SourceSans3VF-Upright.otf.woff2": (
        "f9e4eac0e8f8ffdae91cf6eff3962b96e81417cba5c728bc1c89efe9510e7653"
    ),
    "LICENSE-SourceSerif4.txt": (
        "c21d7293d87b6d7ab1d0229a2f55b77f33a7613a6a4e66f6693d68d7d8d09464"
    ),
    "LICENSE-SourceSans3.txt": (
        "56af9b9c6715597e458284a474dc118a50a4150e9d547c70f7b4a33c3e6a9328"
    ),
}
MATH_MANIFEST = "vendor/katex/assets.json"
MATH_MANIFEST_SHA256 = (
    "184c1e55ff77ef14bb3d120436cb89bbc0173fe596950b0a92c1ebc6bd38ff46"
)


def _math_hashes():
    content = files("elvia").joinpath("web", MATH_MANIFEST).read_bytes()
    if hashlib.sha256(content).hexdigest() != MATH_MANIFEST_SHA256:
        raise ValueError("bundled math manifest hash mismatch")
    manifest = json.loads(content)
    return {
        MATH_MANIFEST: MATH_MANIFEST_SHA256,
        **{f"vendor/katex/{name}": sha for name, sha in manifest["files"].items()},
    }


MATH_HASHES = _math_hashes()
ASSETS = (
    "index.html",
    "atlas.css",
    "atlas.js",
    "search.js",
    "math.js",
    "case-note.js",
    "assessment.js",
    "case-page.js",
    "case-page.css",
    *FONT_HASHES,
    *MATH_HASHES,
)


def _public(record):
    return (
        record["publication"]["status"] == "preliminary_ai"
        and record["case_type"] != "synthetic_demo"
    )


def _catalog(records, filename, label):
    path = records.parent / filename
    if not path.exists() and not path.is_symlink():
        return None
    if not path.resolve(strict=True).is_relative_to(
        records.parent.resolve(strict=True)
    ):
        raise ValueError(f"{label} catalog escapes dataset root")
    return json.loads(path.read_text("utf-8"))


def build_site(
    records: Path | Sequence[Path],
    output: Path,
    *,
    reader_library: Path | None = None,
    public_base_url: str | None = None,
) -> int:
    """Validate all datasets, then publish latest public cases to NEW output.

    Case exports retain full immutable history. A non-public predecessor fails
    closed: publishing a later revision never implicitly publishes a draft.
    Draft latest revisions hide the case even if earlier revisions were public.
    Publication eligibility does not grant access or deploy a public website.
    The client runs no evidence code; serve bundled assets over loopback HTTP.
    A path or sequence of paths preserves each collection's artifact root and
    presentation catalogs. Case identities must be unique across collections.
    """
    directories = (
        [Path(records)]
        if isinstance(records, (str, PathLike))
        else [Path(path) for path in records]
    )
    if not directories:
        raise ValueError("site build requires at least one records directory")
    collections, entries, owners = [], [], {}
    for directory in directories:
        if not directory.is_dir():
            raise ValueError(
                "site build requires a records directory, not one revision"
            )
        loaded = load_records(directory)
        for case in {record["case_id"] for _, record in loaded}:
            if case in owners:
                raise ValueError(f"{case}: duplicate case across collections")
            owners[case] = directory
        collections.append((directory, loaded))
        entries.extend(loaded)
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"{output}: site build requires a new directory")
    latest = {}
    for path, record in entries:
        latest[record["case_id"]] = (path, record)
    selected = [latest[case] for case in sorted(latest) if _public(latest[case][1])]
    ids = {record["case_id"] for _, record in selected}
    for _, record in entries:
        if record["case_id"] in ids and not _public(record):
            raise ValueError(
                f"{record['case_id']}: non-public predecessor cannot be published; "
                "site requires an entirely public revision chain"
            )
    counts = Counter(record["audit"]["outcome"] for _, record in selected)
    payload = {
        "format_version": "1",
        "case_count": len(selected),
        "counts": {outcome: counts[outcome] for outcome in OUTCOMES},
        "records": [record for _, record in selected],
        "presentation": {},
        "case_notes": {},
        "research_fields": {},
    }
    for directory, _ in collections:
        members = [
            record for _, record in selected if owners[record["case_id"]] == directory
        ]
        payload["presentation"].update(
            prepare_presentation(
                members,
                catalog=_catalog(directory, "math-notation.json", "math presentation"),
            )
        )
        payload["case_notes"].update(
            prepare_case_notes(
                members, catalog=_catalog(directory, "case-notes.json", "case note")
            )
        )
        payload["research_fields"].update(
            prepare_research_fields(
                members,
                _catalog(directory, "research-fields.json", "research field"),
            )
        )
        reader_catalog = _catalog(directory, "reader-catalog.json", "reader")
        if reader_catalog is not None:
            payload.setdefault("reader", {}).update(
                prepare_reader(members, reader_catalog)
            )
    reader_files = None
    if reader_library is not None:
        reader_library = Path(reader_library)
        reader_files = json.loads(
            (reader_library / "reader-files.json").read_text("utf-8")
        )
        if reader_files.get("format_version") != 1:
            raise ValueError("unsupported reader library")
        payload["reader_bundles"] = {
            record["case_id"]: f"evidence/{record['case_id']}.zip"
            for _, record in selected
        }
    serialized = json.dumps(payload, ensure_ascii=True, indent=2, allow_nan=False)
    # Preflight exports and all file bytes in private staging before output exists.
    with tempfile.TemporaryDirectory(prefix="elvia-atlas-") as temporary:
        staging = Path(temporary)
        for path, record in selected:
            case_root = staging / "evidence" / record["case_id"]
            export_records(path, case_root)
            if reader_files is not None:
                row = reader_files.get("cases", {}).get(record["case_id"])
                if row is None:
                    raise ValueError(f"missing reader files: {record['case_id']}")
                write_reader_bundle(
                    record,
                    row,
                    reader_library,
                    owners[record["case_id"]].parent,
                    case_root.with_suffix(".zip"),
                )
                continue
            with zipfile.ZipFile(case_root.with_suffix(".zip"), "x") as bundle:
                for artifact in sorted(case_root.rglob("*")):
                    if artifact.is_file():
                        # Fixed ZIP metadata makes identical evidence reproducible.
                        info = zipfile.ZipInfo(
                            artifact.relative_to(case_root).as_posix()
                        )
                        info.compress_type = zipfile.ZIP_DEFLATED
                        bundle.writestr(info, artifact.read_bytes())
        for asset in ASSETS:
            content = files("elvia").joinpath("web", asset).read_bytes()
            if asset in FONT_HASHES:
                if hashlib.sha256(content).hexdigest() != FONT_HASHES[asset]:
                    raise ValueError(f"{asset}: bundled font or license hash mismatch")
            if asset in MATH_HASHES:
                if hashlib.sha256(content).hexdigest() != MATH_HASHES[asset]:
                    raise ValueError(f"{asset}: bundled math asset hash mismatch")
            target = staging / asset
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        (staging / "data.json").write_text(serialized + "\n", encoding="utf-8")
        # External script avoids file:// fetch restrictions; escaped JSON is data,
        # never HTML or a template literal. Prose uses textContent; only explicit
        # equations are handed to the bundled renderer with trust disabled.
        safe = (
            serialized.replace("<", "\\u003c")
            .replace(">", "\\u003e")
            .replace("&", "\\u0026")
        )
        (staging / "data.js").write_text(
            "window.ELVIA_DATA = " + safe + ";\n", encoding="utf-8"
        )
        write_search_pages(staging, payload, public_base_url)
        manifest = {
            "format_version": "1",
            "case_count": len(selected),
            "files": [
                {
                    "path": p.relative_to(staging).as_posix(),
                    "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                }
                for p in sorted(staging.rglob("*"))
                if p.is_file()
            ],
        }
        (staging / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        output.mkdir(parents=True, exist_ok=False)
        try:
            for source in staging.rglob("*"):
                if source.is_file():
                    target = output / source.relative_to(staging)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with target.open("xb") as stream:
                        stream.write(source.read_bytes())
        except BaseException:
            shutil.rmtree(output)
            raise
    return len(selected)
