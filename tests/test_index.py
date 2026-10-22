"""The disposable index must preserve authoritative files and all revisions."""

import copy
import hashlib
import importlib
import importlib.util
import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from elvia.storage import save_record


def rebuild(records, db):
    assert importlib.util.find_spec("elvia.index") is not None, "index not implemented"
    return importlib.import_module("elvia.index").rebuild_index(records, db)


def rows(db):
    with closing(sqlite3.connect(db)) as connection:
        return connection.execute(
            "SELECT case_id, revision, case_type, status, repair_status, source_path "
            "FROM records ORDER BY case_id, revision"
        ).fetchall()


def test_index_rebuilds_every_revision_and_recreates(tmp_path, valid_record):
    records = tmp_path / "records"
    save_record(valid_record, records)
    later = copy.deepcopy(valid_record)
    later.update(revision=2, previous_revision=1)
    later["adjudication"]["status"] = "unresolved"
    later["repair"].update(content="Candidate", verification_status="pending")
    save_record(later, records)
    db = tmp_path / "index.sqlite"
    assert rebuild(records, db) == 2
    expected = [
        (
            "synthetic-001",
            1,
            "synthetic_demo",
            "pending",
            "not_proposed",
            str(records / "synthetic-001.r1.json"),
        ),
        (
            "synthetic-001",
            2,
            "synthetic_demo",
            "unresolved",
            "pending",
            str(records / "synthetic-001.r2.json"),
        ),
    ]
    assert rows(db) == expected
    assert rebuild(records, db) == 2
    db.unlink()
    assert rebuild(records, db) == 2
    assert rows(db) == expected
    with closing(sqlite3.connect(db)) as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("INSERT INTO records SELECT * FROM records LIMIT 1")


@pytest.mark.parametrize("input_path", [".", "synthetic-001.r1.json"])
def test_index_relative_to_records_directory(
    tmp_path, valid_record, monkeypatch, input_path
):
    target = save_record(valid_record, tmp_path / "records")
    monkeypatch.chdir(target.parent)
    db = Path("../index.sqlite")
    assert rebuild(Path(input_path), db) == 1
    assert rows(db) == [
        ("synthetic-001", 1, "synthetic_demo", "pending", "not_proposed", str(target))
    ]
    before = (tmp_path / "source.txt").read_bytes()
    with pytest.raises(ValueError, match="overlap"):
        rebuild(Path(input_path), Path("../source.txt"))
    assert (tmp_path / "source.txt").read_bytes() == before


@pytest.mark.parametrize(
    "bad_name,payload",
    [
        ("broken.r1.json", b"{"),
        ("synthetic-001.r2.json", b"{}"),
        ("duplicate.r1.json", None),
    ],
)
def test_index_invalid_input_preserves_existing_db(
    tmp_path, valid_record, bad_name, payload
):
    record_path = save_record(valid_record, tmp_path / "records")
    db = tmp_path / "index.sqlite"
    rebuild(record_path.parent, db)
    before = db.read_bytes()
    (record_path.parent / bad_name).write_bytes(
        record_path.read_bytes() if payload is None else payload
    )
    with pytest.raises(ValueError):
        rebuild(record_path.parent, db)
    assert db.read_bytes() == before


@pytest.mark.parametrize("target", ["record", "source", "evidence"])
def test_index_rejects_authoritative_paths(tmp_path, valid_record, target):
    path = save_record(valid_record, tmp_path / "records")
    db = {
        "record": path,
        "source": tmp_path / "source.txt",
        "evidence": tmp_path / "evidence.txt",
    }[target]
    before = db.read_bytes()
    with pytest.raises(ValueError, match="overlap"):
        rebuild(path.parent, db)
    assert db.read_bytes() == before


def test_index_rejects_non_sqlite_without_replacing(tmp_path, valid_record):
    path = save_record(valid_record, tmp_path / "records")
    db = tmp_path / "notes.txt"
    db.write_bytes(b"unrelated content")
    with pytest.raises(ValueError, match="SQLite"):
        rebuild(path.parent, db)
    assert db.read_bytes() == b"unrelated content"


def test_index_empty_input_does_not_create_output(tmp_path):
    records = tmp_path / "records"
    records.mkdir()
    with pytest.raises(ValueError):
        rebuild(records, tmp_path / "index.sqlite")
    assert not (tmp_path / "index.sqlite").exists()


def test_single_record_index_protects_predecessor_artifacts(tmp_path, valid_record):
    artifact = tmp_path / "historical-evidence.sqlite"
    with closing(sqlite3.connect(artifact)) as connection:
        connection.execute("CREATE TABLE original_evidence (value TEXT)")
        connection.commit()
    old = copy.deepcopy(valid_record)
    old["evidence"][0]["artifact"] = {
        "path": artifact.name,
        "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
    }
    first = save_record(old, tmp_path / "records")
    later = copy.deepcopy(valid_record)
    later.update(revision=2, previous_revision=1)
    second = save_record(later, first.parent)
    before = artifact.read_bytes()
    with pytest.raises(ValueError, match="overlap"):
        rebuild(second, artifact)
    assert artifact.read_bytes() == before


def test_index_resolves_artifact_alias(tmp_path, valid_record):
    path = save_record(valid_record, tmp_path / "records")
    alias = tmp_path / "alias"
    try:
        alias.symlink_to(tmp_path, target_is_directory=True)
    except OSError:
        if __import__("os").name != "nt":
            raise
        import subprocess

        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"New-Item -ItemType Junction -Path '{alias}' -Target '{tmp_path}'",
            ],
            check=True,
            capture_output=True,
        )
    before = (tmp_path / "source.txt").read_bytes()
    with pytest.raises(ValueError, match="overlap"):
        rebuild(path.parent, alias / "source.txt")
    assert (tmp_path / "source.txt").read_bytes() == before
