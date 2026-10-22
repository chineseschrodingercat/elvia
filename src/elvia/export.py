"""Lossless portable datasets with Markdown and JSONL views."""

import hashlib
import json
import shutil
from pathlib import Path, PurePosixPath

from elvia.records import _artifacts
from elvia.storage import load_records


def _json(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)


def _markdown(record):
    lines = [
        f"# {record['case_id']} — revision {record['revision']}",
        "",
        f"Case type: `{record['case_type']}`. "
        f"Issue decision: `{record['adjudication']['status']}`. "
        f"Repair verification: `{record['repair']['verification_status']}`. "
        f"Author adoption: `{record['repair']['adoption_status']}`.",
        "",
        "Synthetic demonstration."
        if record["case_type"] == "synthetic_demo"
        else "Scientific record export.",
        "Tool computation, human adjudication, repair verification, and author "
        "adoption are separate. This export preserves process declarations; "
        "software does not certify reviewer identity, expertise, or judgments.",
        "",
    ]
    # Every schema field is rendered without summarizing away adverse evidence,
    # unknowns, histories, run metadata, or human declarations.
    for key, value in record.items():
        lines.extend([f"## {key}", "", "```json", _json(value), "```", ""])
    return "\n".join(lines).encode("utf-8")


def _entries_with_predecessors(input_path):
    entries = load_records(input_path)
    if input_path.is_file():
        path, record = entries[0]
        entries = [
            load_records(path.parent / f"{record['case_id']}.r{revision}.json")[0]
            for revision in range(1, record["revision"])
        ] + entries
    return entries


def export_records(input_path: Path, output: Path) -> int:
    """Export unchanged snapshots and all artifacts to a new directory.

    Return the number of snapshots actually exported. A single-file request
    includes its complete predecessor chain for portability, but no unrelated
    cases. JSONL and Markdown contain those same snapshots. manifest.json hashes
    every exported file except the manifest itself. No output is overwritten.
    Callers must not replace input or output paths concurrently.
    """
    input_path, output = Path(input_path), Path(output)
    entries = _entries_with_predecessors(input_path)
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"{output}: export requires a new directory")
    files = {}
    keys = set()

    def add(relative, payload):
        relative = PurePosixPath(relative).as_posix()
        key = relative.casefold()
        if any(
            key == other or key.startswith(other + "/") or other.startswith(key + "/")
            for other in keys
        ):
            raise ValueError(f"{relative}: export path collision")
        keys.add(key)
        files[relative] = payload

    for path, record in entries:
        add(f"records/{path.name}", path.read_bytes())
        add(f"markdown/{path.stem}.md", _markdown(record))
    add(
        "records.jsonl",
        "".join(
            json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n"
            for _, record in entries
        ).encode("utf-8"),
    )
    artifact_paths = {}
    for path, record in entries:
        for _, artifact in _artifacts(record):
            relative = PurePosixPath(artifact["path"]).as_posix()
            key = relative.casefold()
            if (
                key.split("/")[0] in {"records", "markdown"}
                or key == "manifest.json"
                or key.startswith("manifest.json/")
            ):
                raise ValueError(f"{relative}: export path collision")
            if relative in artifact_paths:
                continue
            payload = (path.parent.parent / artifact["path"]).read_bytes()
            if hashlib.sha256(payload).hexdigest() != artifact["sha256"]:
                raise ValueError(f"{path}: artifact hash changed before export")
            add(relative, payload)
            artifact_paths[relative] = artifact["sha256"]
    manifest = {
        "format_version": "1",
        "snapshot_count": len(entries),
        "files": [
            {"path": relative, "sha256": hashlib.sha256(payload).hexdigest()}
            for relative, payload in sorted(files.items())
        ],
    }
    add("manifest.json", (_json(manifest) + "\n").encode("utf-8"))
    output.mkdir(parents=True, exist_ok=False)
    try:
        for relative, payload in files.items():
            target = output / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(payload)
    except BaseException:
        shutil.rmtree(output)
        raise
    return len(entries)
