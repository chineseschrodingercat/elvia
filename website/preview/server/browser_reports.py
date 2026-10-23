"""Structured report intake and transactional, paper-wide editorial reservations.

This operational schema never writes scientific records or executes uploads.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from urllib.parse import unquote, urlsplit

ACTIVE = ("draft", "needs_changes", "submitted", "accepted")

class ReportError(ValueError):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def need(condition, message, status=400):
    if not condition:
        raise ReportError(message, status)


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def text(value, limit, label):
    need(isinstance(value, str), label + " must be text.")
    value = value.strip()
    need(len(value) <= limit and "\x00" not in value, label + " is too long or contains an invalid character.")
    return value


def url_key(url):
    """Known DOI/arXiv aliases share a paper key; no network request is made."""
    if not isinstance(url, str) or not url:
        return ""
    try:
        parsed = urlsplit(url.strip())
        host = (parsed.hostname or "").lower()
        if parsed.scheme not in ("http", "https") or not host or parsed.username or parsed.password:
            return ""
        path = unquote(parsed.path).rstrip("/")
        if host in ("doi.org", "www.doi.org", "dx.doi.org"):
            if path.casefold().startswith("/10.48550/arxiv."):
                return "arxiv:" + re.sub(r"v\d+$", "", path[len("/10.48550/arxiv."):], flags=re.I).casefold()
            return "doi:" + path.lstrip("/").casefold()
        if host in ("arxiv.org", "www.arxiv.org", "export.arxiv.org"):
            match = re.fullmatch(r"/(?:abs|pdf|html)/(.+?)(?:v\d+)?(?:\.pdf)?", path)
            if match:
                return "arxiv:" + match[1].casefold()
        port = parsed.port
        authority = host + (":" + str(port) if port and port not in (80, 443) else "")
        return "url:https://" + authority + path + ("?" + parsed.query if parsed.query else "")
    except ValueError:
        return ""


def atlas_records(atlas):
    if atlas is not None and hasattr(atlas, "report_catalog"):
        return atlas.report_catalog
    response = atlas.read("data.json") if atlas else None
    if not response:
        return []
    rows = json.loads(response[0]).get("records", [])
    atlas.report_catalog = rows
    return rows


def record_keys(record):
    source, audit = record.get("source", {}), record.get("audit", {})
    keys = [url_key(audit.get("landing_url")), url_key(audit.get("pdf_url"))]
    if source.get("doi"):
        keys.insert(0, url_key("https://doi.org/" + source["doi"]))
    if source.get("arxiv_id"):
        keys.append(url_key("https://arxiv.org/abs/" + source["arxiv_id"]))
    return [key for key in dict.fromkeys(keys) if key]


def source_key(url, atlas=None):
    key = url_key(url)
    if key:
        for record in atlas_records(atlas):
            keys = record_keys(record)
            if key in keys:
                return keys[0]
    return key


def atlas_context(atlas, case_id):
    need(isinstance(case_id, str) and re.fullmatch(r"[-a-z0-9_]{1,160}", case_id), "Choose a valid Atlas paper.")
    response = atlas.read("cases/" + case_id + ".context.json") if atlas else None
    need(response, "The published paper is unavailable. Return to the Atlas and choose a current note.", 404)
    payload = json.loads(response[0])
    record = next((row for row in payload.get("records", []) if row.get("case_id") == case_id), None)
    need(record, "The published paper identity could not be verified.", 409)
    note = payload.get("case_notes", {}).get(case_id, {})
    problems = note.get("problems", []) if note.get("revision") == record["revision"] else []
    if record.get("audit", {}).get("outcome") in ("no_issue_found", "scope_clarification"):
        problems = []
    elif not problems:
        problems = [{"title": "The recorded claim"}]
    keys = record_keys(record)
    need(keys, "The published source identity is incomplete.", 409)
    return {"key": keys[0], "case_id": case_id, "revision": record["revision"],
            "title": record["source"]["title"], "venue": record["audit"]["venue"],
            "source_url": record["audit"]["landing_url"], "source_version": record["source"].get("version", ""),
            "problems": [{"number": i + 1, "title": p.get("title", "Recorded problem")}
                         for i, p in enumerate(problems)],
            "context_sha256": hashlib.sha256(response[0]).hexdigest()}


def migrate(db, atlas=None):
    """Additive v1 migration; fail atomically if old live claims overlap."""
    if not db.in_transaction:
        db.execute("BEGIN IMMEDIATE")
    db.execute("CREATE TABLE IF NOT EXISTS report_schema(version INTEGER PRIMARY KEY,applied TEXT NOT NULL)")
    if db.execute("SELECT 1 FROM report_schema WHERE version=1").fetchone():
        return
    db.execute("CREATE TABLE paper_claims(contribution_id TEXT PRIMARY KEY REFERENCES contributions(id),paper_key TEXT NOT NULL,base TEXT NOT NULL,active INTEGER NOT NULL CHECK(active IN (0,1)),created TEXT NOT NULL)")
    db.execute("CREATE UNIQUE INDEX one_active_paper ON paper_claims(paper_key) WHERE active=1")
    db.execute("CREATE TABLE paper_integrations(contribution_id TEXT PRIMARY KEY REFERENCES contributions(id),case_id TEXT NOT NULL,revision INTEGER NOT NULL,context_sha256 TEXT NOT NULL,actor TEXT NOT NULL REFERENCES users(id),note TEXT NOT NULL,created TEXT NOT NULL)")
    db.execute("CREATE TABLE contribution_files(id TEXT PRIMARY KEY,contribution_id TEXT NOT NULL REFERENCES contributions(id),revision INTEGER NOT NULL,slot TEXT NOT NULL,name TEXT NOT NULL,mime TEXT NOT NULL,sha256 TEXT NOT NULL,size INTEGER NOT NULL,manifest TEXT NOT NULL,body BLOB NOT NULL,UNIQUE(contribution_id,revision,slot))")
    rows = list(db.execute("SELECT * FROM contributions ORDER BY created,id"))
    for item in rows:
        record = json.loads(item["data"])
        key = source_key(record.get("source_url", ""), atlas)
        if item["task_id"]:
            task = db.execute("SELECT * FROM tasks WHERE id=?", (item["task_id"],)).fetchone()
            original = db.execute("SELECT data FROM contributions WHERE id=?", (task["source_id"],)).fetchone() if task["source_id"] else None
            key = source_key(json.loads(original["data"]).get("source_url", ""), atlas) if original else "task:" + task["id"]
        if key:
            try:
                db.execute("INSERT INTO paper_claims VALUES(?,?,?,?,?)", (item["id"], key, "{}", int(item["status"] in ACTIVE), now()))
            except sqlite3.IntegrityError as exc:
                raise ReportError("Existing overlapping paper claims need maintainer reconciliation before migration.", 409) from exc
    # Accepted reviews remain reserved by one_active_paper until integration.
    db.execute("DROP INDEX IF EXISTS one_claim")
    db.execute("CREATE UNIQUE INDEX one_claim ON contributions(task_id) WHERE status IN ('draft','needs_changes','submitted')")
    db.execute("INSERT INTO report_schema VALUES(1,?)", (now(),))


def claim_info(db, cid):
    row = db.execute("SELECT * FROM paper_claims WHERE contribution_id=?", (cid,)).fetchone()
    if not row:
        return None
    integration = db.execute("SELECT * FROM paper_integrations WHERE contribution_id=?", (cid,)).fetchone()
    return {"key": row["paper_key"], "base": json.loads(row["base"]), "active": bool(row["active"]),
            "integration": dict(integration) if integration else None}


def reserve(db, cid, key, base=None):
    need(key, "Enter an official paper URL before reserving this paper.")
    other = db.execute("SELECT contribution_id FROM paper_claims WHERE paper_key=? AND active=1 AND contribution_id<>?", (key, cid)).fetchone()
    need(not other, "This paper already has an active contribution. Wait until editorial review and integration are complete, or choose another paper.", 409)
    previous = claim_info(db, cid)
    if base is None:
        base = previous["base"] if previous else {}
    db.execute("INSERT INTO paper_claims VALUES(?,?,?,?,?) ON CONFLICT(contribution_id) DO UPDATE SET paper_key=excluded.paper_key,base=excluded.base,active=1", (cid, key, encoded(base), 1, now()))


def release(db, cid):
    db.execute("UPDATE paper_claims SET active=0 WHERE contribution_id=?", (cid,))


def task_base(db, task, atlas):
    if not task["source_id"]:
        return {"key": "task:" + task["id"], "title": task["title"], "revision": 1, "problems": []}
    original = db.execute("SELECT * FROM contributions WHERE id=?", (task["source_id"],)).fetchone()
    data = json.loads(original["data"])
    key = source_key(data.get("source_url", ""), atlas)
    integrated = db.execute("SELECT i.case_id FROM paper_integrations i JOIN paper_claims p ON i.contribution_id=p.contribution_id WHERE p.paper_key=? ORDER BY i.created DESC,i.rowid DESC LIMIT 1", (key,)).fetchone()
    if integrated:
        return atlas_context(atlas, integrated["case_id"])
    return {"key": key, "title": task["title"], "revision": original["revision"], "problems": [],
            "source_url": data.get("source_url", ""), "venue": data.get("venue", "")}


def availability(db, key, user=None):
    row = db.execute("SELECT c.id,c.owner,c.status FROM paper_claims p JOIN contributions c ON c.id=p.contribution_id WHERE p.paper_key=? AND p.active=1", (key,)).fetchone()
    status = {"draft": "in_progress", "needs_changes": "in_progress", "submitted": "awaiting_review", "accepted": "awaiting_integration"}.get(row["status"], "in_progress") if row else "available"
    messages = {
        "available": "Available for a contribution. One contributor can reserve this paper at a time.",
        "in_progress": "A contributor is working on this paper. The next contribution opens after editorial review and integration.",
        "awaiting_review": "A contribution is awaiting editorial review. This paper remains reserved.",
        "awaiting_integration": "A contribution has been accepted and is awaiting integration. The next review is not open yet.",
    }
    result = {"status": status, "message": messages[status], "available": row is None}
    if row and user and row["owner"] == user["id"]:
        result["my_contribution"] = row["id"]
    return result


def integrate(db, item, user, incoming, atlas):
    need(item["status"] == "accepted", "Accept the contribution before recording integration.", 409)
    claim = claim_info(db, item["id"])
    need(claim and claim["active"], "This contribution has no active paper reservation.", 409)
    need(incoming.get("integration_confirmed") is True, "Confirm that the accepted changes are included in the published record.")
    note = text(incoming.get("note", ""), 6000, "Integration note")
    need(len(note) >= 20, "Explain where the accepted changes were integrated (at least 20 characters).")
    current = atlas_context(atlas, incoming.get("case_id"))
    need(current["key"] == claim["key"], "The published record belongs to a different paper.", 409)
    need(type(incoming.get("revision")) is int and incoming["revision"] == current["revision"], "Use the currently deployed published revision.", 409)
    base = claim["base"]
    if base.get("case_id"):
        need(current["case_id"] == base["case_id"] and current["revision"] > base["revision"], "Deploy a new immutable scientific revision before reopening this paper.", 409)
    db.execute("INSERT INTO paper_integrations VALUES(?,?,?,?,?,?,?)", (item["id"], current["case_id"], current["revision"], current["context_sha256"], user["id"], note, now()))
    release(db, item["id"])
    return current
