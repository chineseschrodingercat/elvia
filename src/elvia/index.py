"""Disposable SQLite queries built from validated authoritative snapshots."""

import os
import sqlite3
import tempfile
from pathlib import Path

from elvia.records import _artifacts
from elvia.storage import load_records


def _check_target(db, protected):
    if db in protected:
        raise ValueError(f"{db}: database path overlaps a record or artifact")
    if db.exists():
        if not db.is_file():
            raise ValueError(f"{db}: existing target is not a SQLite file")
        with db.open("rb") as stream:
            header = stream.read(16)
        if header != b"SQLite format 3\x00":
            raise ValueError(f"{db}: refusing to replace a non-SQLite file")
        try:
            connection = sqlite3.connect(db.as_uri() + "?mode=ro", uri=True)
            try:
                if connection.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
                    raise ValueError(f"{db}: existing SQLite file is corrupt")
            finally:
                connection.close()
        except sqlite3.DatabaseError as exc:
            raise ValueError(f"{db}: invalid SQLite file ({exc})") from exc


def rebuild_index(records: Path, db: Path) -> int:
    """Validate first, stage transactionally, then atomically replace the index.

    Return the number of indexed snapshots, including historical revisions.
    SQLite stores query fields only; all scientific declarations remain in JSON.
    As with record storage, callers must not replace paths concurrently.
    """
    records = Path(records)
    entries = load_records(records)
    protected_entries = list(entries)
    if records.is_file():
        path, record = entries[0]
        for revision in range(1, record["revision"]):
            protected_entries.extend(
                load_records(path.parent / f"{record['case_id']}.r{revision}.json")
            )
    protected = set()
    for path, record in protected_entries:
        protected.add(path.resolve())
        protected.update(
            (path.parent.parent / artifact["path"]).resolve()
            for _, artifact in _artifacts(record)
        )
    db = Path(db).resolve()
    _check_target(db, protected)
    db.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=".elvia-index-", dir=db.parent)
    os.close(descriptor)
    temporary = Path(name)
    try:
        connection = sqlite3.connect(temporary)
        try:
            with connection:
                connection.execute(
                    "CREATE TABLE records (case_id TEXT NOT NULL, "
                    "revision INTEGER NOT NULL, case_type TEXT NOT NULL, "
                    "status TEXT NOT NULL, repair_status TEXT NOT NULL, "
                    "source_path TEXT NOT NULL, PRIMARY KEY (case_id, revision))"
                )
                connection.executemany(
                    "INSERT INTO records VALUES (?, ?, ?, ?, ?, ?)",
                    [
                        (
                            record["case_id"],
                            record["revision"],
                            record["case_type"],
                            record["adjudication"]["status"],
                            record["repair"]["verification_status"],
                            str(path),
                        )
                        for path, record in entries
                    ],
                )
        finally:
            connection.close()
        _check_target(db, protected)
        os.replace(temporary, db)
    finally:
        temporary.unlink(missing_ok=True)
    return len(entries)
