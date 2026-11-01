#!/usr/bin/env python3
"""Merge immutable reader libraries into a new, hash-verified library.

Only manifest-referenced files are published. Sources must remain immutable:
same-volume hard links share their bytes with the source. Use --copy-only when
the caller cannot guarantee that. This tool never changes a source library.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
from pathlib import Path, PurePosixPath
from typing import Any

MANIFEST = "reader-files.json"
HASH_RE = re.compile(r"[0-9a-fA-F]{64}\Z")
RESERVED = {"con", "prn", "aux", "nul"} | {
    f"{prefix}{number}" for prefix in ("com", "lpt") for number in range(1, 10)
}


class MergeError(ValueError):
    """An input cannot safely be published."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _plain_path(root: Path, relative: str) -> Path:
    """Require canonical portable paths and regular files, without redirects."""
    if not isinstance(relative, str) or not relative:
        raise MergeError("A file path must be a nonempty string")
    parts = relative.split("/")
    for part in parts:
        if (
            part in ("", ".", "..")
            or part.endswith((".", " "))
            or part.split(".")[0].casefold() in RESERVED
            or any(ord(char) < 32 or char in '<>:"\\|?*' for char in part)
        ):
            raise MergeError(f"Nonportable or escaping file path: {relative!r}")
    if PurePosixPath(relative).is_absolute():
        raise MergeError(f"Absolute file path: {relative!r}")
    path = root
    for index, part in enumerate(parts):
        path = path / part
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(path, "is_junction", lambda: False)():
            raise MergeError(f"Symlink or junction is not allowed: {path}")
        expected = stat.S_ISREG if index == len(parts) - 1 else stat.S_ISDIR
        if not expected(info.st_mode):
            raise MergeError(f"Expected a regular file or directory: {path}")
    if not path.resolve().is_relative_to(root):
        raise MergeError(f"File escapes its library: {relative!r}")
    return path


def _references(case: dict[str, Any]):
    for name in ("article", "report"):
        if case.get(name) is not None:
            yield case[name]
    revisions = case.get("revisions", [])
    evidence = case.get("evidence", [])
    if not isinstance(revisions, list) or not isinstance(evidence, list):
        raise MergeError("revisions and evidence must be lists")
    for revision in revisions:
        if not isinstance(revision, dict) or not isinstance(
            revision.get("files", []), list
        ):
            raise MergeError("Each revision must contain a files list")
        yield from revision.get("files", [])
    yield from evidence


def merge_libraries(
    libraries: list[Path], output: Path, *, copy_only: bool = False
) -> dict[str, Any]:
    """Validate all inputs first, then publish an explicit, disjoint case union."""
    if not libraries:
        raise MergeError("At least one input library is required")
    output = output.absolute()
    if output.exists() or output.is_symlink():
        raise MergeError(f"Output must not already exist: {output}")
    cases: dict[str, Any] = {}
    case_names: set[str] = set()
    files: dict[str, tuple[Path, str]] = {}
    portable_paths: dict[str, str] = {}
    inputs = []
    for supplied_root in libraries:
        supplied_root = supplied_root.absolute()
        if (
            supplied_root.is_symlink()
            or getattr(supplied_root, "is_junction", lambda: False)()
        ):
            raise MergeError(
                f"Library root must not be a symlink or junction: {supplied_root}"
            )
        root = supplied_root.resolve(strict=True)
        if output.resolve().is_relative_to(root):
            raise MergeError("Output must be outside every source library")
        manifest_path = _plain_path(root, MANIFEST)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        if (
            not isinstance(manifest, dict)
            or type(manifest.get("format_version")) is not int
            or manifest["format_version"] != 1
            or not isinstance(manifest.get("cases"), dict)
        ):
            raise MergeError(f"Unsupported reader manifest: {manifest_path}")
        inputs.append({"library": str(root), "manifest_sha256": _sha256(manifest_path)})
        for case_id, case in manifest["cases"].items():
            if (
                not isinstance(case_id, str)
                or not case_id
                or not isinstance(case, dict)
            ):
                raise MergeError(
                    "Case identifiers must be nonempty strings with object values"
                )
            if case_id.casefold() in case_names:
                raise MergeError(f"Case IDs must be disjoint: {case_id}")
            case_names.add(case_id.casefold())
            cases[case_id] = case
            for reference in _references(case):
                if not isinstance(reference, dict):
                    raise MergeError(f"Invalid file reference in {case_id}")
                relative, expected = reference.get("path"), reference.get("sha256")
                if not isinstance(expected, str) or not HASH_RE.fullmatch(expected):
                    raise MergeError(
                        f"Missing or invalid SHA-256 in {case_id}: {relative!r}"
                    )
                source = _plain_path(root, relative)
                expected = expected.lower()
                if _sha256(source) != expected:
                    raise MergeError(f"SHA-256 mismatch: {source}")
                folded = relative.casefold()
                if folded == MANIFEST:
                    raise MergeError(
                        "A referenced file conflicts with the output manifest"
                    )
                if folded in portable_paths and portable_paths[folded] != relative:
                    raise MergeError(
                        f"Case-insensitive file path collision: {relative}"
                    )
                portable_paths[folded] = relative
                if relative in files and files[relative][1] != expected:
                    raise MergeError(
                        f"Conflicting bytes at shared file path: {relative}"
                    )
                files.setdefault(relative, (source, expected))
    for relative in portable_paths:
        for parent in PurePosixPath(relative).parents:
            if str(parent) != "." and str(parent) in portable_paths:
                raise MergeError(f"File/directory path collision: {relative}")
    linked = copied = total_bytes = 0
    output.mkdir(parents=True, exist_ok=False)
    try:
        for relative, (source, expected) in sorted(files.items()):
            destination = output / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            used_link = False
            if not copy_only:
                try:
                    os.link(source, destination, follow_symlinks=False)
                    used_link = True
                except OSError:
                    if destination.exists() or destination.is_symlink():
                        raise
            if used_link:
                linked += 1
            else:
                with source.open("rb") as src, destination.open("xb") as dst:
                    shutil.copyfileobj(src, dst, 1024 * 1024)
                copied += 1
            if _sha256(destination) != expected:
                raise MergeError(f"File changed during publication: {source}")
            total_bytes += destination.stat().st_size
        manifest = {"format_version": 1, "cases": cases}
        with (output / MANIFEST).open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(manifest, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.write("\n")
    except BaseException:
        shutil.rmtree(output)
        raise
    return {
        "output": str(output),
        "cases": len(cases),
        "files": len(files),
        "linked": linked,
        "copied": copied,
        "logical_bytes": total_bytes,
        "manifest_sha256": _sha256(output / MANIFEST),
        "inputs": inputs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--copy-only", action="store_true")
    args = parser.parse_args()
    try:
        result = merge_libraries(args.library, args.output, copy_only=args.copy_only)
    except (MergeError, OSError, json.JSONDecodeError) as exc:
        parser.exit(1, f"Library merge failed: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
