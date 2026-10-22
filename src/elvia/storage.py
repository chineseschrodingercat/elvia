"""Validated immutable JSON snapshots, with exclusive atomic publication."""

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

from elvia.records import validate_record

_CANONICAL = re.compile(r"[a-z0-9][a-z0-9_-]{0,79}\.r[1-9][0-9]*\.json\Z")
_SOURCE_IDENTITY = ("title", "version", "doi", "arxiv_id", "artifact")
_AUDIT_IDENTITY = (
    "venue",
    "year",
    "authors",
    "landing_url",
    "pdf_url",
    "pdf_sha256",
    "retrieved_at",
)


def _filename(record):
    return f"{record['case_id']}.r{record['revision']}.json"


def _check_records_directory(records_dir):
    """Reject a pre-existing records symlink/junction outside its dataset root."""
    root = records_dir.parent.resolve(strict=True)
    try:
        resolved = records_dir.resolve()
    except RuntimeError as exc:
        raise ValueError(f"{records_dir}: cannot resolve records directory") from exc
    if not resolved.is_relative_to(root):
        raise ValueError(f"{records_dir}: records directory escapes dataset root")


def _read(path):
    if not _CANONICAL.fullmatch(path.name):
        raise ValueError(f"{path}: noncanonical record filename")
    if not path.resolve().is_relative_to(path.parent.resolve()):
        raise ValueError(f"{path}: record symlink escapes records directory")
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ValueError(f"{path}: malformed JSON ({exc})") from exc
    errors = validate_record(record, root=path.parent.parent)
    if errors:
        raise ValueError(f"{path}: " + "; ".join(errors))
    if path.name != _filename(record):
        raise ValueError(f"{path}: filename does not match case_id/revision")
    return record


def _check_predecessor(record, previous):
    if record["case_type"] != previous["case_type"]:
        raise ValueError("$.case_type: cannot change between revisions")
    transition = record.get("source_update")
    if transition is not None:
        canonical = json.dumps(
            previous, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode()
        if (
            hashlib.sha256(canonical).hexdigest()
            != transition["previous_record_sha256"]
        ):
            raise ValueError("$.source_update: predecessor record hash mismatch")
        if "audit" in previous and (
            "audit" not in record
            or any(
                record["audit"][k] != previous["audit"][k] for k in ("venue", "year")
            )
        ):
            raise ValueError(
                "$.source_update: venue/year correspondence must be retained"
            )
        return
    if any(
        record["source"][key] != previous["source"][key] for key in _SOURCE_IDENTITY
    ):
        raise ValueError("$.source: source identity cannot change between revisions")
    if "audit" in previous and (
        "audit" not in record
        or any(
            record["audit"][key] != previous["audit"][key] for key in _AUDIT_IDENTITY
        )
    ):
        raise ValueError(
            "$.audit: upstream source identity cannot change between revisions"
        )


def _check_history(entries):
    snapshots = {
        (record["case_id"], record["revision"]): record for _, record in entries
    }
    for path, record in entries:
        if record["revision"] == 1:
            continue
        previous = snapshots.get((record["case_id"], record["revision"] - 1))
        if previous is None:
            raise ValueError(f"{path}: missing predecessor revision")
        _check_predecessor(record, previous)


def load_records(path: Path) -> list[tuple[Path, dict]]:
    """Load a canonical file or all directory snapshots, validating history.

    A single-file request checks its preceding sibling snapshots but returns only
    the requested revision. Directory requests retain every revision.
    """
    # Anchor before deriving parents, retaining links for the containment check.
    path = Path(path).absolute()
    if path.is_dir():
        _check_records_directory(path)
        candidates = sorted(path.glob("*.json"))
        if not candidates:
            raise ValueError(f"{path}: No canonical records (empty input)")
        entries = [(candidate, _read(candidate)) for candidate in candidates]
        _check_history(entries)
        return sorted(
            entries, key=lambda item: (item[1]["case_id"], item[1]["revision"])
        )
    _check_records_directory(path.parent)
    record = _read(path)
    history = [(path, record)]
    for revision in range(record["revision"] - 1, 0, -1):
        predecessor = path.parent / f"{record['case_id']}.r{revision}.json"
        if not predecessor.is_file():
            raise ValueError(f"{path}: missing predecessor revision {revision}")
        history.append((predecessor, _read(predecessor)))
    _check_history(history)
    return [(path, record)]


def save_record(record: dict, records_dir: Path) -> Path:
    """Validate and publish a complete snapshot without replacing any path.

    A flushed temporary file is hard-linked to its final name exclusively on the
    same filesystem. Unsupported hard links raise OSError; there is no unsafe
    overwrite or partial-file fallback.
    """
    records_dir = Path(records_dir).absolute()
    _check_records_directory(records_dir)
    errors = validate_record(record, root=records_dir.parent)
    if errors:
        raise ValueError("; ".join(errors))
    if record["revision"] > 1:
        predecessor = records_dir / (
            f"{record['case_id']}.r{record['previous_revision']}.json"
        )
        if not predecessor.is_file():
            raise ValueError("$.previous_revision: missing predecessor snapshot")
        previous = load_records(predecessor)[0][1]
        _check_predecessor(record, previous)
    payload = (
        json.dumps(record, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")
    records_dir.mkdir(parents=True, exist_ok=True)
    target = records_dir / _filename(record)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=".elvia-", suffix=".tmp", dir=records_dir, delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return target
