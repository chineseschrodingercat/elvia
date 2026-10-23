import sqlite3

import pytest

from website.storage import TABLES, install_limits


def database():
    db = sqlite3.connect(":memory:")
    for table in TABLES:
        db.execute(f"CREATE TABLE {table}(id TEXT PRIMARY KEY, body BLOB)")
    db.create_function("elvia_storage_ok", 1, lambda _size: 1)
    install_limits(db, quota=20)
    return db


def test_quota_counts_all_tables_and_preserves_old_bytes():
    db = database()
    for table in TABLES:
        db.execute(f"INSERT INTO {table} VALUES(?,?)", ("a", b"1234"))
    with pytest.raises(sqlite3.IntegrityError, match="ELVIA_STORAGE_QUOTA"):
        db.execute("INSERT INTO packages VALUES(?,?)", ("b", b"x"))
    assert db.execute("SELECT body FROM packages").fetchone()[0] == b"1234"


def test_replace_counts_delta_and_low_disk_denies_before_mutation():
    db = database()
    db.execute("INSERT INTO packages VALUES(?,?)", ("a", b"x" * 20))
    db.execute(
        "INSERT INTO packages VALUES(?,?) "
        "ON CONFLICT(id) DO UPDATE SET body=excluded.body",
        ("a", b"y" * 20),
    )
    db.create_function("elvia_storage_ok", 1, lambda _size: 0)
    with pytest.raises(sqlite3.IntegrityError, match="ELVIA_STORAGE_QUOTA"):
        db.execute("UPDATE packages SET body=? WHERE id=?", (b"z", "a"))
    assert db.execute("SELECT body FROM packages").fetchone()[0] == b"y" * 20
