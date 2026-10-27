"""Prepare explicit public scientific evidence beside an accepted PDF library.

Only paths/members selected in the private index are read. No directories are
searched, no programs are imported or executed, and no author data is fetched.
Sanitized copies must be supplied and described explicitly by the maintainer.
"""

import argparse
import copy
import hashlib
import json
import re
import shutil
import stat
import zipfile
from pathlib import Path, PurePosixPath

from elvia.reader import (
    _archive_name,
    _bytes,
    _file,
    _reader_evidence,
    record_digest,
    report_source,
)
from elvia.storage import load_records

_SECRET = re.compile(
    rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    rb"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{24,}|"
    rb"AIza[A-Za-z0-9_-]{30,}|xox[baprs]-[A-Za-z0-9-]{20,})\b"
)
_PRIVATE_HOST = re.compile(
    r"C:[/\\]+Users[/\\]+liumi\b|D:[/\\]+ELVIA report raw\b|"
    r"/mnt/data/|/home/oai/|https://chatgpt\.com/c/",
    re.I,
)


def _sha(content):
    return hashlib.sha256(content).hexdigest()


def _local_file(name):
    path = Path(name)
    if not path.is_absolute():
        raise ValueError("scientific source paths must be explicitly absolute")
    for item in (path, *path.parents):
        if item.is_symlink() or item.is_junction():
            raise ValueError("scientific source links are not allowed")
    path = path.resolve(strict=True)
    if not path.is_file():
        raise ValueError("scientific source is not a file")
    return path


def _zip_member_name(name):
    if (
        not isinstance(name, str)
        or not name
        or any(c in name for c in '\\:%?#"<>|*')
        or any(ord(c) < 32 for c in name)
        or PurePosixPath(name).is_absolute()
        or any(p in {"", ".", ".."} or p.endswith((".", " ")) for p in name.split("/"))
    ):
        raise ValueError("invalid scientific archive member")
    return name


def _source_bytes(item):
    if "source_path" in item and "source_archive" not in item:
        return _local_file(item["source_path"]).read_bytes()
    if "source_archive" in item and "source_path" not in item:
        archive = _local_file(item["source_archive"])
        member = _zip_member_name(item.get("source_member"))
        with zipfile.ZipFile(archive) as source:
            entries = [entry for entry in source.infolist() if entry.filename == member]
            if (
                len(entries) != 1
                or entries[0].is_dir()
                or stat.S_ISLNK(entries[0].external_attr >> 16)
            ):
                raise ValueError("scientific archive member must be one ordinary file")
            return source.read(entries[0])
    raise ValueError("select exactly one retained source file or archive member")


def _check_public_content(content, archive_name, *, nested=False):
    if _SECRET.search(content):
        raise ValueError("credential-like content in selected public evidence")
    extension = PurePosixPath(archive_name).suffix.lower()
    if extension in {
        ".json",
        ".jsonl",
        ".ipynb",
        ".py",
        ".pyi",
        ".gin",
        ".bif",
        ".pyx",
        ".in",
        ".txt",
        ".md",
        ".tex",
        ".csv",
        ".tsv",
        ".yaml",
        ".yml",
        ".toml",
        ".sh",
        ".js",
        ".rs",
        ".c",
        ".cpp",
        ".h",
        ".cu",
        ".html",
        ".xml",
        ".ini",
        ".cfg",
    }:
        if _PRIVATE_HOST.search(content.decode("utf-8", errors="replace")):
            raise ValueError(
                "private host or conversation path remains in public evidence"
            )
    if extension == ".zip":
        if nested:
            raise ValueError(
                "nested scientific archives require an explicitly flattened copy"
            )
        import io

        with zipfile.ZipFile(io.BytesIO(content)) as bundle:
            names = set()
            for entry in bundle.infolist():
                if entry.is_dir():
                    continue
                name = _zip_member_name(entry.filename)
                if name.casefold() in names or stat.S_ISLNK(entry.external_attr >> 16):
                    raise ValueError(
                        "duplicate or linked public scientific archive member"
                    )
                names.add(name.casefold())
                if PurePosixPath(name).name.casefold() in {
                    ".env",
                    "credentials.json",
                    "cookies.json",
                    "sessions.json",
                }:
                    raise ValueError("private files remain in a scientific archive")
                _check_public_content(bundle.read(entry), name, nested=True)


def _prepared_file(item):
    if item.get("published") is not True:
        raise ValueError(
            "scientific publication requires an explicit approved selection"
        )
    name = _archive_name(item.get("archive_name"))
    original = _source_bytes(item)
    if _sha(original) != item.get("source_sha256"):
        raise ValueError("retained scientific source hash mismatch")
    public = (
        _local_file(item["public_source_path"]).read_bytes()
        if item.get("public_source_path")
        else original
    )
    public_sha = _sha(public)
    if item.get("sha256") is not None and item["sha256"] != public_sha:
        raise ValueError("approved public scientific copy hash mismatch")
    transformation = item.get("transformation", {})
    if transformation.get("kind") == "verbatim" and public != original:
        raise ValueError("verbatim publication changed retained evidence bytes")
    if transformation.get("kind") == "sanitized-scientific-copy" and not item.get(
        "public_source_path"
    ):
        raise ValueError("a sanitized scientific copy must be explicitly supplied")
    _check_public_content(public, name)
    selected = {
        key: copy.deepcopy(item[key])
        for key in (
            "archive_name",
            "source_sha256",
            "references",
            "published",
            "transformation",
            "source_version",
            "license",
        )
        if key in item
    }
    selected.update(path=f"evidence/sha256/{public_sha}", sha256=public_sha)
    return selected, public


def _latest(records):
    latest = {}
    for directory in map(Path, records):
        for _, record in load_records(directory):
            case = record["case_id"]
            if case in latest and latest[case][1] != directory.parent:
                raise ValueError("a reader case occurs in multiple datasets")
            if case not in latest or record["revision"] > latest[case][0]["revision"]:
                latest[case] = (record, directory.parent)
    return latest


def prepare_evidence_library(
    records, pdf_library, evidence_index, output, *, receipt=None
):
    """Reuse exact accepted PDFs and add only explicit hash-checked scientific files."""
    pdf_library, output = Path(pdf_library), Path(output)
    index = json.loads(Path(evidence_index).read_text("utf-8"))
    previous = json.loads((pdf_library / "reader-files.json").read_text("utf-8"))
    latest = _latest(records)
    if index.get("format_version") != 1 or set(index.get("cases", {})) != set(latest):
        raise ValueError("evidence index must cover exactly the selected reader cases")
    if previous.get("format_version") != 1 or set(previous.get("cases", {})) != set(
        latest
    ):
        raise ValueError(
            "accepted PDF library does not cover the selected reader cases"
        )
    if output.exists():
        raise FileExistsError("an evidence library requires a new destination")
    if receipt is not None and Path(receipt).resolve().is_relative_to(output.resolve()):
        raise ValueError(
            "physical source receipts must stay outside the public library"
        )
    prepared, source_receipts = {}, []
    # First pass validates identities and every selected byte before creating output.
    for case, (record, dataset) in latest.items():
        old = previous["cases"][case]
        if (
            old.get("record_sha256") != record_digest(record)
            or old.get("revision") != record["revision"]
        ):
            raise ValueError("accepted PDF library has a stale scientific snapshot")
        if _sha(report_source(record, dataset).read_bytes()) != old.get(
            "report_source_sha256"
        ):
            raise ValueError("accepted report PDF has a different source")
        article = _bytes(pdf_library, old["article"], pdf=True)
        _bytes(pdf_library, old["report"], pdf=True)
        if _sha(article) != record["audit"]["pdf_sha256"]:
            raise ValueError("accepted article differs from the inspected version")
        selection = index["cases"][case]
        if any(
            selection.get(key)
            for key in ("missing", "unresolved", "errors", "blocked", "ambiguous")
        ):
            raise ValueError(f"unresolved scientific evidence selection: {case}")
        row = {
            key: copy.deepcopy(value)
            for key, value in old.items()
            if key not in {"evidence", "references", "aliases", "unavailable"}
        }
        row["references"] = copy.deepcopy(selection.get("references", []))
        row["aliases"] = copy.deepcopy(selection.get("aliases", []))
        row["unavailable"] = copy.deepcopy(selection.get("unavailable", []))
        row["evidence"] = []
        for item in selection.get("evidence", []):
            public, _content = _prepared_file(item)
            row["evidence"].append(public)
            source_receipts.append(
                {
                    "case": case,
                    "archive_name": public["archive_name"],
                    **{
                        key: copy.deepcopy(item[key])
                        for key in (
                            "source_path",
                            "source_archive",
                            "source_member",
                            "public_source_path",
                        )
                        if key in item
                    },
                    "source_sha256": item["source_sha256"],
                    "sha256": public["sha256"],
                    "path": public["path"],
                    "transformation": public["transformation"],
                }
            )
        prepared[case] = row
    output.mkdir(parents=True, exist_ok=False)
    written = set()
    for case, (record, _dataset) in latest.items():
        row = prepared[case]
        old = previous["cases"][case]
        originals = [old["article"], old["report"]]
        originals.extend(
            item for revision in old.get("revisions", []) for item in revision["files"]
        )
        for item in originals:
            source = _file(pdf_library, item["path"])
            destination = output / item["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            _bytes(output, item, pdf=destination.suffix.lower() == ".pdf")
        for original_item, public_item in zip(
            index["cases"][case].get("evidence", []), row["evidence"], strict=True
        ):
            public, content = _prepared_file(original_item)
            if public != public_item:
                raise ValueError(
                    "scientific source changed during evidence preparation"
                )
            if public["path"] not in written:
                destination = output / public["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(content)
                written.add(public["path"])
        contents = [
            ("original article.pdf", _bytes(output, row["article"], pdf=True)),
            ("report.pdf", _bytes(output, row["report"], pdf=True)),
        ]
        for revision in row.get("revisions", []):
            if revision.get("published") is not True:
                raise ValueError(
                    "only explicitly published revisions may be downloaded"
                )
            for index, item in enumerate(revision["files"]):
                extension = PurePosixPath(item["path"]).suffix.lower()
                name = (
                    f"revision {revision['revision']}"
                    + (f" attachment {index}" if index else "")
                    + extension
                )
                contents.append((name, _bytes(output, item, pdf=extension == ".pdf")))
        _reader_evidence(record, row, output, contents)
    public_manifest = {"format_version": 1, "cases": dict(sorted(prepared.items()))}
    _check_public_content(
        (json.dumps(public_manifest, ensure_ascii=False)).encode("utf-8"),
        "reader-files.json",
    )
    (output / "reader-files.json").write_text(
        json.dumps(public_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    summary = {
        "cases": len(prepared),
        "pdfs_reused": 2 * len(prepared),
        "scientific_files": len(source_receipts),
        "unique_scientific_files": len(written),
        "sanitized_scientific_files": sum(
            row["transformation"]["kind"] == "sanitized-scientific-copy"
            for row in source_receipts
        ),
    }
    if receipt is not None:
        with Path(receipt).open("x", encoding="utf-8") as stream:
            json.dump(
                {"summary": summary, "sources": source_receipts},
                stream,
                ensure_ascii=False,
                indent=2,
            )
            stream.write("\n")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--records", type=Path, action="append", required=True)
    parser.add_argument("--pdf-library", type=Path, required=True)
    parser.add_argument("--evidence-index", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            prepare_evidence_library(
                args.records,
                args.pdf_library,
                args.evidence_index,
                args.output,
                receipt=args.receipt,
            )
        )
    )
