"""Private ELVIA snapshots; restore only into a new directory, never in place."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

DB = "elvia.sqlite3"
CONFIG = ("email-settings.json", "email-verification.key", "google-oauth.json")
ALLOWED = {DB, *CONFIG}
FORMAL = Path(__file__).resolve().parents[2]


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def plain(path):
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        raise ValueError("Linked state is unsupported.")


def checked(path):
    path = Path(path).absolute()
    for part in (path, *path.parents):
        plain(part)
    path = path.resolve()
    if path == FORMAL or FORMAL in path.parents:
        raise ValueError("Formal repository is outside scope.")
    return path


def private_new(path):
    path = checked(path)
    path.mkdir(parents=False, exist_ok=False)
    if os.name == "nt":
        value = subprocess.run(
            ["whoami", "/user", "/fo", "csv", "/nh"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        sid = next(csv.reader([value.strip()]))[1]
        subprocess.run(
            [
                "icacls",
                str(path),
                "/inheritance:r",
                "/grant:r",
                f"*{sid}:(OI)(CI)F",
                "*S-1-5-18:(OI)(CI)F",
            ],
            check=True,
            capture_output=True,
        )
    else:
        path.chmod(0o700)
    return path


def ro(path):
    return sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=15)


def integrity(path):
    with closing(ro(path)) as db:
        if db.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise ValueError("SQLite integrity failed.")
        if db.execute("PRAGMA foreign_key_check").fetchone() is not None:
            raise ValueError("Foreign-key check failed.")


def verify(snapshot_path):
    root = checked(snapshot_path)
    plain(root / "manifest.json")
    manifest = json.loads((root / "manifest.json").read_text("utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("Snapshot manifest must be an object.")
    entries = manifest.get("files", {})
    if manifest.get("format") != "elvia-private-state-v1" or not isinstance(
        entries, dict
    ):
        raise ValueError("Unsupported manifest.")
    if DB not in entries or not set(entries) <= ALLOWED:
        raise ValueError("Invalid file allowlist.")
    if {p.name for p in root.iterdir()} != set(entries) | {"manifest.json"}:
        raise ValueError("Unexpected/missing snapshot members.")
    for name, info in entries.items():
        path = root / name
        plain(path)
        if (
            not path.is_file()
            or path.stat().st_size != info["bytes"]
            or digest(path) != info["sha256"]
        ):
            raise ValueError("Member hash/size mismatch.")
    integrity(root / DB)
    return manifest


def snapshot(data, destination, offline):
    if not offline:
        raise ValueError("Stop service and assert --offline first.")
    data, destination = checked(data), checked(destination)
    if (
        data == destination
        or data in destination.parents
        or destination in data.parents
    ):
        raise ValueError("Source/destination must be separate.")
    unknown = (
        {p.name for p in data.iterdir()}
        - ALLOWED
        - {DB + "-wal", DB + "-shm", "MAINTAINER-LOGIN.txt"}
    )
    if unknown:
        raise ValueError("Unrecognized private state; review allowlist locally.")
    for name in ALLOWED | {DB + "-wal", DB + "-shm"}:
        plain(data / name)
    if not (data / DB).is_file():
        raise ValueError("Missing source database.")
    before = {name: digest(data / name) for name in CONFIG if (data / name).is_file()}
    destination = private_new(destination)
    with (
        closing(ro(data / DB)) as source,
        closing(sqlite3.connect(destination / DB)) as target,
    ):
        source.backup(target)
        target.execute("PRAGMA journal_mode=DELETE")
    for name in before:
        shutil.copyfile(data / name, destination / name)
    after = {name: digest(data / name) for name in CONFIG if (data / name).is_file()}
    if before != after or any(
        digest(destination / name) != sha for name, sha in before.items()
    ):
        raise ValueError("Configuration changed during backup; output is incomplete.")
    manifest = {
        "format": "elvia-private-state-v1",
        "created_utc": datetime.now(UTC).isoformat(),
        "offline_asserted": True,
        "excluded_bootstrap_password": True,
        "files": {
            p.name: {"bytes": p.stat().st_size, "sha256": digest(p)}
            for p in destination.iterdir()
        },
    }
    (destination / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", "utf-8"
    )
    verify(destination)
    return {"action": "snapshot", "verified": True, "files": len(manifest["files"])}


def restore(snapshot_path, destination):
    snapshot_path, destination = checked(snapshot_path), checked(destination)
    if destination == snapshot_path or snapshot_path in destination.parents:
        raise ValueError("Restore must be outside snapshot.")
    manifest = verify(snapshot_path)
    destination = private_new(destination)
    for name in manifest["files"]:
        shutil.copyfile(snapshot_path / name, destination / name)
        if digest(destination / name) != manifest["files"][name]["sha256"]:
            raise ValueError("Source changed during restore; discard partial output.")
    with closing(sqlite3.connect(destination / DB)) as db:
        tables = {
            r[0]
            for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        for table in (
            "sessions",
            "email_challenges",
            "oauth_states",
            "password_reset_tokens",
        ):
            if table in tables:
                db.execute('DELETE FROM "' + table + '"')
        db.commit()
        db.execute("PRAGMA journal_mode=DELETE")
    integrity(destination / DB)
    return {
        "action": "restore-copy",
        "verified": True,
        "transient_auth_invalidated": True,
        "existing_state_overwritten": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="action", required=True)
    snap = subs.add_parser(
        "snapshot", help="Private plaintext snapshot after stopping service"
    )
    snap.add_argument("--data-dir", required=True)
    snap.add_argument("--destination", required=True)
    snap.add_argument(
        "--offline", action="store_true", help="Assert service is already stopped"
    )
    check = subs.add_parser("verify")
    check.add_argument("--snapshot", required=True)
    copy = subs.add_parser(
        "restore-copy", help="Restore into a new directory and expire transient auth"
    )
    copy.add_argument("--snapshot", required=True)
    copy.add_argument("--destination", required=True)
    args = parser.parse_args()
    try:
        if args.action == "snapshot":
            result = snapshot(args.data_dir, args.destination, args.offline)
        elif args.action == "verify":
            result = {"action": "verify", "verified": bool(verify(args.snapshot))}
        else:
            result = restore(args.snapshot, args.destination)
    except (
        OSError,
        ValueError,
        sqlite3.Error,
        subprocess.SubprocessError,
        KeyError,
        TypeError,
    ):
        parser.exit(
            1,
            "Operation failed. Inspect paths, permissions and private manifest "
            "locally; do not use partial output.\n",
        )
    print(json.dumps(result))


if __name__ == "__main__":
    main()
