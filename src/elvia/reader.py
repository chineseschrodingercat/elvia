"""Snapshot-bound citations and explicitly selected public reader attachments."""

import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

REVISION_TYPES = {
    ".pdf",
    ".txt",
    ".md",
    ".tex",
    ".csv",
    ".json",
    ".png",
    ".jpg",
    ".zip",
}


def record_digest(record):
    return hashlib.sha256(
        json.dumps(
            record, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode()
    ).hexdigest()


def _bound(row, record):
    if row.get("revision") != record["revision"] or row.get(
        "record_sha256"
    ) != record_digest(record):
        raise ValueError("reader metadata does not match scientific snapshot")


def _https(value):
    if not isinstance(value, str) or any(c.isspace() for c in value):
        return False
    parsed = urlsplit(value)
    return (
        parsed.scheme == "https"
        and bool(parsed.netloc)
        and not parsed.username
        and not parsed.password
    )


def prepare_reader(records, catalog):
    """Require verified citation fields and explicit contributor credit."""
    if catalog.get("format_version") != 1 or not isinstance(catalog.get("cases"), dict):
        raise ValueError("unsupported reader catalog")
    selected = {}
    for record in records:
        row = catalog["cases"].get(record["case_id"])
        if row is None or row.get("revision") != record["revision"]:
            continue
        _bound(row, record)
        citation = row.get("citation", {})
        if not all(
            isinstance(citation.get(key), str) and citation[key].strip()
            for key in ("title", "container", "volume", "source_url")
        ):
            raise ValueError("reader citation is incomplete")
        authors = citation.get("authors")
        if (
            not isinstance(authors, list)
            or not authors
            or not all(isinstance(a, str) and a.strip() for a in authors)
        ):
            raise ValueError("reader citation requires authors")
        doi = citation.get("doi")
        if doi is not None and (
            not isinstance(doi, str) or not re.fullmatch(r"10\.\d{4,9}/[^\s<>]+", doi)
        ):
            raise ValueError("reader citation has an invalid DOI")
        if not _https(citation["source_url"]):
            raise ValueError("reader citation requires an HTTPS source")
        if (
            type(citation.get("year")) is not int
            or not 1800 <= citation["year"] <= 2200
        ):
            raise ValueError("invalid citation year")
        for key in ("first_page", "last_page"):
            if not isinstance(citation.get(key, ""), str):
                raise ValueError("invalid citation pages")
        contributors = row.get("contributors", [])
        if not isinstance(contributors, list):
            raise ValueError("invalid contributor credits")
        for person in contributors:
            if (
                not all(
                    isinstance(person.get(key), str) and person[key].strip()
                    for key in ("name", "role")
                )
                or type(person.get("revision")) is not int
                or not 1 <= person["revision"] <= record["revision"]
            ):
                raise ValueError("invalid contributor credit")
        selected[record["case_id"]] = row
    return selected


def _file(root, name):
    """No path discovery: only canonical, in-root, non-symlink manifest files."""
    if not isinstance(name, str) or not name or any(c in name for c in "\\:%?#"):
        raise ValueError("invalid reader file path")
    parts = name.split("/")
    if PurePosixPath(name).is_absolute() or any(
        p in {"", ".", ".."} or p.endswith((".", " ")) for p in parts
    ):
        raise ValueError("invalid reader file path")
    root = Path(root).resolve(strict=True)
    candidate = root
    for part in parts:
        candidate /= part
        if candidate.is_symlink() or candidate.is_junction():
            raise ValueError("reader file links are not allowed")
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise ValueError("reader file is missing") from exc
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError("reader file escapes library root")
    return resolved


def _bytes(root, item, *, pdf=False):
    path = _file(root, item["path"])
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != item.get("sha256"):
        raise ValueError("reader file hash mismatch")
    if pdf and (not content.startswith(b"%PDF-") or b"%%EOF" not in content[-1024:]):
        raise ValueError("reader file is not a complete PDF")
    return content


def report_source(record, dataset):
    sources = [
        item["artifact"]
        for item in record["evidence"]
        if item["artifact"]["path"].endswith("/report.tex")
    ]
    if len(sources) != 1:
        raise ValueError("reader report requires one registered LaTeX source")
    _bytes(dataset, sources[0])
    return _file(dataset, sources[0]["path"])


def write_reader_bundle(record, row, library, dataset, output):
    """Write only the reviewed article, current report and published revisions.

    The application database and upload directories are never searched. Adding a
    contributor file requires an explicit, reviewed publication manifest entry.
    All identities are validated before any ZIP output is created.
    """
    _bound(row, record)
    original = _bytes(library, row["article"], pdf=True)
    if hashlib.sha256(original).hexdigest() != record["audit"]["pdf_sha256"]:
        raise ValueError("reader original differs from the reviewed article")
    report = _bytes(library, row["report"], pdf=True)
    source = report_source(record, dataset)
    if hashlib.sha256(source.read_bytes()).hexdigest() != row.get(
        "report_source_sha256"
    ):
        raise ValueError("reader PDF report source has changed")
    contents = [("original article.pdf", original), ("report.pdf", report)]
    seen = set()
    for revision in row.get("revisions", []):
        number = revision.get("revision")
        if revision.get("published") is not True:
            raise ValueError("only explicitly published revisions may be downloaded")
        if (
            type(number) is not int
            or not 2 <= number <= record["revision"]
            or number in seen
        ):
            raise ValueError("invalid published revision number")
        seen.add(number)
        if not isinstance(revision.get("files"), list) or not revision["files"]:
            raise ValueError("published revision requires files")
        for index, item in enumerate(revision["files"]):
            extension = PurePosixPath(item["path"]).suffix.lower()
            if extension not in REVISION_TYPES or (index == 0 and extension != ".pdf"):
                raise ValueError(
                    "a revision starts with a PDF report and supported attachments"
                )
            name = (
                f"revision {number}"
                + (f" attachment {index}" if index else "")
                + extension
            )
            contents.append((name, _bytes(library, item, pdf=extension == ".pdf")))
    with zipfile.ZipFile(output, "x") as bundle:
        # Retain article attribution without adding a cluttering README file.
        bundle.comment = (
            "ELVIA reader bundle. Original article retains its authors' copyright "
            "and source terms. ELVIA report: CC BY 4.0. "
            + record.get("audit", {}).get("pdf_url", "")
        ).encode("utf-8")
        for name, content in contents:
            info = zipfile.ZipInfo(name)
            info.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(info, content)
