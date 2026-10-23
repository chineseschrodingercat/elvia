"""Validate and retain report files. Uploaded code and TeX are never executed."""
import base64
import binascii
import hashlib
import io
import json
import re
import zipfile

from browser_reports import need

REPORT_LIMIT = 20 * 1024 * 1024
PAPER_LIMIT = 50 * 1024 * 1024
CODE_LIMIT = 5 * 1024 * 1024
REPORT_SIZE_MESSAGE = "Your report is too large. Compress the PDF or reduce the LaTeX file, then upload again (20 MB maximum)."
PAPER_SIZE_MESSAGE = "The original article and supplementary PDF are too large together. Compress one or both PDFs, then upload again (50 MB combined maximum)."
SLOTS = {"report", "paper-supplement", "verification-code"}
CODE_EXTENSIONS = {".py", ".r", ".jl", ".m", ".ipynb", ".c", ".cpp", ".cc", ".h", ".hpp", ".rs", ".go", ".java", ".js", ".ts", ".sh", ".bash", ".ps1", ".sql", ".stan", ".f", ".f90", ".f95", ".wl", ".wls", ".nb", ".sage", ".lean", ".v", ".Rmd", ".qmd", ".md", ".txt", ".json", ".toml", ".yaml", ".yml", ".ini", ".cfg", ".csv", ".tsv"}
CODE_EXTENSIONS = {x.lower() for x in CODE_EXTENSIONS}


def filename(value):
    need(isinstance(value, str) and 0 < len(value) <= 180 and value not in (".", "..") and not any(c in value for c in '/\\:') and not any(ord(c) < 32 for c in value), "Use a simple filename without folders or control characters.")
    return value


def pdf(blob, name, limit=PAPER_LIMIT):
    need(name.lower().endswith(".pdf"), "Upload a PDF in this slot.")
    need(0 < len(blob) <= limit, REPORT_SIZE_MESSAGE if limit == REPORT_LIMIT else PAPER_SIZE_MESSAGE, 413)
    need(blob.startswith(b"%PDF-") and b"%%EOF" in blob[-4096:], "This does not look like a complete PDF. Export the complete document as PDF and try again.")
    return "application/pdf"


def report(blob, name):
    need(0 < len(blob) <= REPORT_LIMIT, REPORT_SIZE_MESSAGE, 413)
    if name.lower().endswith(".pdf"):
        return pdf(blob, name, REPORT_LIMIT)
    need(name.lower().endswith(".tex"), "Upload one report PDF or LaTeX (.tex) file.")
    try:
        source = blob.decode("utf-8-sig")
    except UnicodeError:
        need(False, "Save the LaTeX file using UTF-8 encoding.")
    source = re.sub(r"(?<!\\)%[^\n]*", "", source)
    need("\x00" not in source and all(re.search(pattern, source) for pattern in (r"\\documentclass(?:\[[^]]*\])?\s*\{", r"\\begin\s*\{document\}", r"\\end\s*\{document\}")), "Upload a complete LaTeX document with documentclass and begin/end document. Use the matching template above.")
    return "text/plain; charset=utf-8"


def code_files(payload):
    items = payload.get("files")
    need(isinstance(items, list) and 1 <= len(items) <= 10, "Choose between 1 and 10 code files, or one ZIP.")
    total, seen, members = 0, set(), []
    for item in items:
        need(isinstance(item, dict), "Each code file needs a name and content.")
        name = filename(item.get("name"))
        suffix = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
        need(suffix in CODE_EXTENSIONS or name.lower() in ("makefile", "dockerfile"), "Choose source-code or plain-text support files. Put other supporting formats in a ZIP.")
        need(name.casefold() not in seen, "Choose code files with distinct filenames.")
        seen.add(name.casefold())
        try:
            blob = base64.b64decode(item.get("content"), validate=True)
        except (ValueError, TypeError, binascii.Error):
            need(False, "A code file could not be read. Choose the files again.")
        total += len(blob)
        need(total <= CODE_LIMIT, "Verification code must total no more than 5 MB.", 413)
        members.append((name, blob))
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, blob in members:
            archive.writestr(name, blob)
    # The individual originals are retained byte-for-byte in this generated archive.
    return buffer.getvalue(), "verification-code.zip"


def validate(slot, blob, name, inspect_zip, *, loose_code=False):
    filename(name)
    if slot == "report":
        return report(blob, name), [{"name": name, "bytes": len(blob)}]
    if slot == "paper-supplement":
        return pdf(blob, name), [{"name": name, "bytes": len(blob)}]
    need(slot == "verification-code", "Unknown attachment slot.")
    need(loose_code or len(blob) <= CODE_LIMIT, "Verification code must total no more than 5 MB.", 413)
    manifest = inspect_zip(blob, name, max_bytes=CODE_LIMIT + 65536) if loose_code else inspect_zip(blob, name)
    need(sum(row["bytes"] for row in manifest) <= CODE_LIMIT, "The unpacked verification code must total no more than 5 MB.", 413)
    return "application/zip", manifest


def paper_budget(db, cid, slot, incoming_size):
    """Count the latest other PDF; replaced files and old revisions do not stack."""
    if slot == "source":
        other = db.execute("SELECT size FROM contribution_files WHERE contribution_id=? AND slot='paper-supplement' ORDER BY revision DESC LIMIT 1", (cid,)).fetchone()
    else:
        other = db.execute("SELECT size FROM source_files WHERE contribution_id=? ORDER BY revision DESC LIMIT 1", (cid,)).fetchone()
    need(incoming_size + (other["size"] if other else 0) <= PAPER_LIMIT, PAPER_SIZE_MESSAGE, 413)


def current(db, cid):
    result = {}
    for row in db.execute("SELECT id,slot,revision,name,mime,sha256,size,manifest FROM contribution_files WHERE contribution_id=? ORDER BY revision", (cid,)):
        result[row["slot"]] = dict(row) | {"manifest": json.loads(row["manifest"])}
    return result


def save(db, cid, revision, slot, blob, name, mime, manifest, new_id):
    previous = db.execute("SELECT id FROM contribution_files WHERE contribution_id=? AND revision=? AND slot=?", (cid, revision, slot)).fetchone()
    ident = previous["id"] if previous else new_id
    db.execute("INSERT INTO contribution_files VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(contribution_id,revision,slot) DO UPDATE SET name=excluded.name,mime=excluded.mime,sha256=excluded.sha256,size=excluded.size,manifest=excluded.manifest,body=excluded.body", (ident, cid, revision, slot, name, mime, hashlib.sha256(blob).hexdigest(), len(blob), json.dumps(manifest), blob))


def submission_archive(data, report_row):
    """Keep the legacy versioned package pointer, without requiring a user ZIP."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        suffix = ".pdf" if report_row["mime"] == "application/pdf" else ".tex"
        archive.writestr("report" + suffix, bytes(report_row["body"]))
        archive.writestr("submission.json", json.dumps(data, ensure_ascii=False, indent=2))
    return buffer.getvalue()
