"""ELVIA independent, loopback-only contribution workspace.

SQLite owns accounts, sessions, applications, claims, revisions and ZIP bytes.
No paper code execution, external model calls or repository access.
Verification email uses the maintainer-configured SMTP provider.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import hmac
import io
import json
import mimetypes
import re
import secrets
import sqlite3
import stat
import string
import threading
import time
import zipfile
from contextlib import contextmanager
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import quote, unquote, urlsplit, parse_qs
from admission import AdmissionEngine, CATALOG, fingerprint, unsafe_url, find_venue, arxiv_identifier, top_journal
from google_login import GoogleLogin, GoogleLoginError, POLICY_VERSION
from email_access import EmailAccess, MailError, eligible_email, normalize_email
from atlas_static import AtlasStatic
from origin_policy import OriginPolicy, validate_private_origin
from mail_abuse import AbuseBudget, initialize_abuse
from login_guard import LoginGuard, initialize_login_guard
from trusted_login_proxy import protected_action,verify_context,canonical_client_ip,load_proxy_key,HEADER_NAMES
from owner_identity import (initialize_owner_identity,is_retired,resolve_login,resolve_alias,
                            alias_claimed,login_claimed,alias_binding,recovery_user_ids,same_person)

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
POLICY = json.loads((Path(__file__).parent / "policy.json").read_text("utf-8"))
EDITABLE = ("draft", "needs_changes")
OPEN = ("draft", "needs_changes", "submitted")
ASSESSMENTS = {"supported", "clarification", "possible_issue", "unresolved"}
TEXT_FIELDS = {"title": 500, "venue": 200, "field": 40, "year": 4, "source_url": 2000, "source_version": 500, "summary": 6000,
               "location": 1500, "scope": 3000, "reasoning": 16000, "verification": 8000,
               "limits": 4000, "ai_model": 200, "ai_details": 4000}
FIELD_LABELS = {"title": "Paper title", "summary": "Review summary", "location": "Exact passage or result", "scope": "Question examined",
                "reasoning": "Reasoning", "verification": "Checks performed", "venue": "Journal or conference",
                "year": "Publication year", "source_url": "Published paper URL", "position": "Current position",
                "institution": "Institution or organization", "expertise": "Relevant expertise", "field": "Field for eligibility"}
DEMO_TASKS = [
    ("DEMO-001", "A convergence bound for an iterative estimator", "Mathematics",
     "Check the assumptions and limiting term in a geometric error bound.",
     "Fictional example: e(k+1) ≤ q e(k) + b, with 0 ≤ q < 1 and b ≥ 0. The draft analysis states that e(k) is bounded by q^k e(0) + b(1−q^k)/(1−q). Check the steps and whether the limiting term is retained. This is an original synthetic exercise, not a published paper."),
    ("DEMO-002", "Uncertainty in a repeated-measures comparison", "Statistics",
     "Identify the independent experimental unit and explain its effect on uncertainty.",
     "Fictional example: 12 specimens are each measured three times. A draft analysis treats the 36 readings as independent. Examine this assumption and explain what can be concluded without additional specimen-level data. No actual study or author is represented."),
    ("DEMO-003", "An evaluation protocol for a small classifier", "Machine learning",
     "Check how threshold selection relates to the reported test evaluation.",
     "Fictional example: the draft analysis proposes selecting a decision threshold on validation data and reporting performance on a separate held-out test set. Check what independence assumptions are needed and what information is missing. No actual study or author is represented.")
]


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def uid(prefix):
    return prefix + "_" + secrets.token_hex(12)


def dump(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


class Problem(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message


def require(condition, message, status=400):
    if not condition:
        raise Problem(status, message)


def require_fields(record, names):
    missing = [FIELD_LABELS.get(key, key) for key in names if not record.get(key, "").strip()]
    require(not missing, "Complete the required fields: " + "; ".join(missing) + ".")


def password_hash(password):
    require(isinstance(password,str) and 9<=len(password)<=256 and
            any('A'<=character<='Z' for character in password) and
            any(character in string.punctuation for character in password),
            "Use 9–256 characters, at least one uppercase letter (A–Z) and one ASCII special character, such as ! or /.")
    salt = secrets.token_bytes(16)
    key = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
    return salt.hex() + ":" + key.hex()


def generated_password():
    # The fixed prefix guarantees both required character classes; randomness
    # supplies 192 bits without relying on chance to satisfy the password rule.
    return 'A!'+secrets.token_urlsafe(24)


def password_matches(password, stored):
    if not isinstance(password, str) or len(password) > 256 or ':' not in stored:
        return False
    salt, expected = stored.split(":")
    actual = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
    return hmac.compare_digest(actual, expected)


def clean(value, limit, label):
    require(isinstance(value, str), f"{label} must be text.")
    value = value.strip()
    require(len(value) <= limit and "\x00" not in value, f"{label} is too long or contains an invalid character.")
    return value


def web_url(value):
    parsed = urlsplit(value)
    return parsed.scheme in ("http", "https") and bool(parsed.hostname) and not parsed.username and not parsed.password


def academic_email(email):
    return bool(re.search(r"\.(edu|ac\.[a-z]{2}|edu\.[a-z]{2})$", email, re.I))

def staff(user):
    return bool(user and user['role'] in ('admin','maintainer'))

def suspended(db,user_id):
    row=db.execute('SELECT suspended FROM account_controls WHERE user_id=?',(user_id,)).fetchone()
    return bool(row and row['suspended'])

def can_manage_account(actor,target):
    return bool(actor and target and actor['id']!=target['id'] and
                (actor['role']=='maintainer' and target['role'] in ('admin','reviewer') or
                 actor['role']=='admin' and target['role']=='reviewer'))

def can_view_work(db,actor,item):
    if not actor or not item:return False
    if item['owner']==actor['id']:return True
    if not staff(actor):return False
    owner=db.execute('SELECT role FROM users WHERE id=?',(item['owner'],)).fetchone()
    # Maintainer account isolation includes work that has not been submitted.
    if owner and owner['role']=='maintainer' and item['status'] not in ('submitted','accepted','declined'):return False
    return True


def inspect_zip(blob, filename):
    require(filename.lower().endswith(".zip"), "Upload one ZIP package.")
    require(0 < len(blob) <= POLICY["max_zip_bytes"], "The ZIP must be no larger than 10 MB (10,485,760 bytes).", 413)
    try:
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            entries = archive.infolist()
            require(0 < len(entries) <= POLICY["max_zip_entries"], "Use 1–200 entries in the ZIP.")
            total, seen, manifest = 0, set(), []
            for item in entries:
                name = item.filename.replace("\\", "/")
                parts = PurePosixPath(name).parts
                require(name and not name.startswith("/") and not any(p in ("..", ".") or ":" in p for p in parts)
                        and not any(ord(c) < 32 for c in name) and len(name) <= 300,
                        "The ZIP contains an unsafe path.")
                require(name.casefold() not in seen, "The ZIP contains duplicate filenames.")
                seen.add(name.casefold())
                require(not item.flag_bits & 1, "Password-protected ZIP files are not supported.")
                require(not stat.S_ISLNK(item.external_attr >> 16), "The ZIP cannot contain symbolic links.")
                require(item.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED), "Use a standard ZIP with stored or deflated entries.")
                total += item.file_size
                require(total <= POLICY["max_uncompressed_bytes"], "The unpacked package must be no larger than 50 MB.", 413)
                require(item.file_size <= max(item.compress_size * 300, 1024 * 1024), "An entry is compressed too heavily. Remove generated or repeated data.", 413)
                # Read bounded bytes for CRC validation; never extract or execute.
                if not item.is_dir():
                    count = 0
                    with archive.open(item) as stream:
                        while chunk := stream.read(65536):
                            count += len(chunk)
                            require(count <= item.file_size and count <= POLICY["max_uncompressed_bytes"], "Invalid ZIP entry size.", 413)
                    require(count == item.file_size, "An entry in the ZIP is incomplete.")
                    manifest.append({"name": name, "bytes": count})
            require(bool(manifest), "The ZIP needs at least one file.")
            return manifest
    except Problem:
        raise
    except (zipfile.BadZipFile, RuntimeError, OSError, EOFError, NotImplementedError, ValueError):
        raise Problem(400, "This ZIP cannot be read. Create a fresh ZIP and try again.") from None


@contextmanager
def connect(path):
    db = sqlite3.connect(path, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    # Used only by the public runtime's attachment quota triggers. Include all
    # retained revisions; reserve enough space for a failed transaction/rollback.
    def storage_available(size):
        import shutil
        try:
            return int(shutil.disk_usage(Path(path).parent).free >= 2_000_000_000 + 2 * size)
        except OSError:
            return 0
    db.create_function('elvia_storage_ok', 1, storage_available)
    try:
        with db:
            yield db
    finally:
        db.close()


def initialize(data_dir, bootstrap_password=None, *, seed_demo=True):
    data_dir.mkdir(parents=True, exist_ok=True)
    path = data_dir / "elvia.sqlite3"
    with connect(path) as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, login TEXT UNIQUE NOT NULL,
          name TEXT NOT NULL, role TEXT NOT NULL, password TEXT NOT NULL, force_change INTEGER NOT NULL DEFAULT 0, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id), csrf TEXT NOT NULL, expires REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS applications(user_id TEXT PRIMARY KEY REFERENCES users(id), profile TEXT NOT NULL, status TEXT NOT NULL, note TEXT NOT NULL, updated TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY, title TEXT NOT NULL, topic TEXT NOT NULL,
          question TEXT NOT NULL, context TEXT NOT NULL, synthetic INTEGER NOT NULL, source_id TEXT UNIQUE, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS contributions(id TEXT PRIMARY KEY, owner TEXT NOT NULL REFERENCES users(id),
          kind TEXT NOT NULL, task_id TEXT REFERENCES tasks(id), status TEXT NOT NULL, data TEXT NOT NULL,
          version INTEGER NOT NULL, revision INTEGER NOT NULL, note TEXT NOT NULL, created TEXT NOT NULL, updated TEXT NOT NULL);
        CREATE UNIQUE INDEX IF NOT EXISTS one_claim ON contributions(task_id) WHERE status IN ('draft','needs_changes','submitted','accepted');
        CREATE TABLE IF NOT EXISTS packages(id TEXT PRIMARY KEY, contribution_id TEXT NOT NULL REFERENCES contributions(id),
          revision INTEGER NOT NULL, name TEXT NOT NULL, sha256 TEXT NOT NULL, size INTEGER NOT NULL, manifest TEXT NOT NULL, body BLOB NOT NULL,
          UNIQUE(contribution_id, revision));
        CREATE TABLE IF NOT EXISTS revisions(contribution_id TEXT NOT NULL REFERENCES contributions(id), revision INTEGER NOT NULL,
          data TEXT NOT NULL, package_id TEXT NOT NULL REFERENCES packages(id), submitted TEXT NOT NULL, PRIMARY KEY(contribution_id,revision));
        CREATE TABLE IF NOT EXISTS source_files(id TEXT PRIMARY KEY, contribution_id TEXT NOT NULL REFERENCES contributions(id),
          revision INTEGER NOT NULL, name TEXT NOT NULL, mime TEXT NOT NULL, sha256 TEXT NOT NULL, size INTEGER NOT NULL,
          manifest TEXT NOT NULL, body BLOB NOT NULL, UNIQUE(contribution_id,revision));
        CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, actor TEXT, target TEXT NOT NULL,
          action TEXT NOT NULL, note TEXT NOT NULL, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS maintainer_revisions(id TEXT PRIMARY KEY, contribution_id TEXT NOT NULL REFERENCES contributions(id),
          author TEXT NOT NULL REFERENCES users(id), mode TEXT NOT NULL, data TEXT NOT NULL, note TEXT NOT NULL, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS amendments(id TEXT PRIMARY KEY, contribution_id TEXT NOT NULL REFERENCES contributions(id),
          final_revision TEXT NOT NULL REFERENCES maintainer_revisions(id), owner TEXT NOT NULL REFERENCES users(id), status TEXT NOT NULL,
          data TEXT NOT NULL, package_name TEXT NOT NULL, sha256 TEXT NOT NULL, size INTEGER NOT NULL, manifest TEXT NOT NULL,
          body BLOB, decision TEXT NOT NULL, created TEXT NOT NULL, updated TEXT NOT NULL);
        CREATE UNIQUE INDEX IF NOT EXISTS one_pending_amendment ON amendments(final_revision,owner) WHERE status='pending';
        CREATE TABLE IF NOT EXISTS revision_files(id TEXT PRIMARY KEY, revision_id TEXT NOT NULL REFERENCES maintainer_revisions(id),
          name TEXT NOT NULL, sha256 TEXT NOT NULL, size INTEGER NOT NULL, manifest TEXT NOT NULL, body BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS admission_checks(id TEXT PRIMARY KEY, contribution_id TEXT NOT NULL REFERENCES contributions(id),
          fingerprint TEXT NOT NULL, result TEXT NOT NULL, actor TEXT, created REAL NOT NULL);
        CREATE INDEX IF NOT EXISTS admission_lookup ON admission_checks(contribution_id,fingerprint,created);
        CREATE TABLE IF NOT EXISTS daily_usage(user_id TEXT NOT NULL REFERENCES users(id), day TEXT NOT NULL,
          action TEXT NOT NULL, target TEXT NOT NULL, created TEXT NOT NULL,
          PRIMARY KEY(user_id,day,action,target));
        CREATE TABLE IF NOT EXISTS email_challenges(id TEXT PRIMARY KEY,email TEXT NOT NULL,digest TEXT NOT NULL,created REAL NOT NULL,expires REAL NOT NULL,attempts INTEGER NOT NULL,sent INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS verified_emails(user_id TEXT PRIMARY KEY REFERENCES users(id),email TEXT NOT NULL,verified TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS password_reset_tokens(token_hash TEXT PRIMARY KEY,user_id TEXT NOT NULL REFERENCES users(id),email TEXT NOT NULL,binding_hash TEXT NOT NULL,created REAL NOT NULL,expires REAL NOT NULL,used INTEGER NOT NULL DEFAULT 0,sent INTEGER NOT NULL DEFAULT 0);
        CREATE UNIQUE INDEX IF NOT EXISTS one_active_password_reset ON password_reset_tokens(user_id) WHERE used=0;
        CREATE TABLE IF NOT EXISTS account_controls(user_id TEXT PRIMARY KEY REFERENCES users(id),suspended INTEGER NOT NULL,note TEXT NOT NULL,updated_by TEXT NOT NULL REFERENCES users(id),updated TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS role_reservations(email TEXT PRIMARY KEY,role TEXT NOT NULL,created_by TEXT NOT NULL REFERENCES users(id),created TEXT NOT NULL,updated TEXT NOT NULL);
        """)
        initialize_abuse(db)
        initialize_login_guard(db)
        initialize_owner_identity(db)
        if not db.execute("SELECT 1 FROM users WHERE role='maintainer'").fetchone():
            password = bootstrap_password or generated_password()
            db.execute("INSERT INTO users VALUES(?,?,?,?,?,?,?)", (uid("u"), "minhao", "Minhao Liu", "maintainer", password_hash(password), 1, stamp()))
            if bootstrap_password is None:
                (data_dir / "MAINTAINER-LOGIN.txt").write_text(
                    "ELVIA LOCAL WORKSPACE — PRIVATE INITIAL SIGN-IN\n\nAccount: minhao\nTemporary password: " + password +
                    "\n\nOpen http://127.0.0.1:8797/contribute.html?view=login\nChoose a new password after signing in.\n"
                    "This file is removed after the initial password is changed.\nNever share this file or include local-data in an export.\n", encoding="utf-8")
        for tid, title, topic, question, context in (DEMO_TASKS if seed_demo else ()):
            db.execute("INSERT OR IGNORE INTO tasks VALUES(?,?,?,?,?,?,?,?)", (tid, title, topic, question, context, 1, None, stamp()))
    return path


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, data_dir, port, bootstrap_password, *, private_origin=None,login_proxy_key_file=None):
        # Configuration errors must not create or modify operational state.
        validate_private_origin(private_origin)
        if private_origin and login_proxy_key_file is None:raise ValueError('Private sign-in requires the protected login proxy key file.')
        self.login_proxy_key=load_proxy_key(login_proxy_key_file) if login_proxy_key_file is not None else None
        self.atlas = AtlasStatic(SITE / "atlas")
        self.data_dir = Path(data_dir).resolve()
        self.db_path = initialize(self.data_dir, bootstrap_password)
        self.attempts = {}
        self.rate_lock = threading.Lock()
        self.reset_mail_slots = threading.BoundedSemaphore(2)
        self.auth_slots = threading.BoundedSemaphore(4)
        self.dummy_hash = password_hash(generated_password())
        self.admission = AdmissionEngine()
        super().__init__(("127.0.0.1", port), Handler)
        self.origins=OriginPolicy(self.server_port,private_origin)
        self.google=GoogleLogin(self.data_dir,self.server_port,private_origin=private_origin)
        self.mailer=EmailAccess(self.data_dir)
        self.abuse=AbuseBudget(self.mailer.key)
        self.login_guard=LoginGuard(self.mailer.key)
        with connect(self.db_path) as db:self.google.initialize(db)

    def deliver_password_reset(self,email,url,digest,account_id):
        try:
            self.mailer.send_password_reset(email,url)
            with connect(self.db_path) as db:
                changed=db.execute('UPDATE password_reset_tokens SET sent=1 WHERE token_hash=? AND used=0 AND expires>?',(digest,time.time())).rowcount
                if changed:
                    db.execute('INSERT INTO events(actor,target,action,note,created) VALUES(?,?,?,?,?)',(account_id,account_id,'password_reset_requested','',stamp()))
        except Exception:
            # Recovery responses never disclose account existence or transport
            # failures; background errors must not expose email links or tokens.
            pass
        finally:self.reset_mail_slots.release()


class Handler(BaseHTTPRequestHandler):
    server_version = "ELVIA-local/5"
    sys_version = ""

    def setup(self):
        super().setup()
        self.connection.settimeout(25)

    def log_message(self, fmt, *args):
        pass  # Deliberately omit URLs, identities, credentials and request bodies.

    def send(self, status, value, content_type="application/json; charset=utf-8", extra=None):
        blob = dump(value).encode() if content_type.startswith("application/json") and not isinstance(value, bytes) else value
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(blob)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; font-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'self'; object-src 'none'; frame-ancestors 'none'")
        for key, val in (extra or {}).items():
            if key.casefold()=='set-cookie' and getattr(self,'request_origin',None):
                val=self.server.origins.cookie(val,self.request_origin)
            self.send_header(key, val)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(blob)

    def body(self, limit=100_000, binary=False):
        if not binary and hasattr(self, "cached_body"):
            return self.cached_body
        require(not self.headers.get("Transfer-Encoding"), "Unsupported request encoding.")
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise Problem(400, "Invalid request length.") from None
        require(0 <= size <= limit, "The upload is too large.", 413)
        raw = self.rfile.read(size)
        if not binary:self.cached_raw_body=raw
        require(len(raw) == size, "The upload was interrupted. Please try again.")
        if binary:
            return raw
        require(self.headers.get("Content-Type", "").split(";")[0] == "application/json", "Use a JSON request.", 415)
        try:
            value = json.loads(raw)
        except (ValueError, UnicodeError):
            raise Problem(400, "The request could not be read.") from None
        require(isinstance(value, dict), "Invalid request.")
        return value

    def identify(self, db):
        cookies = SimpleCookie()
        try:
            cookies.load(self.headers.get("Cookie", ""))
        except Exception:
            return None, None
        raw = cookies.get("elvia_session")
        if not raw:
            return None, None
        token = hashlib.sha256(raw.value.encode()).hexdigest()
        session = db.execute("SELECT * FROM sessions WHERE token=? AND expires>?", (token, time.time())).fetchone()
        user = db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone() if session else None
        if user and (suspended(db,user['id']) or is_retired(db,user['id'])):return None,None
        return user, session

    def session(self, db, user):
        require(not is_retired(db,user['id']),'This historical account no longer has a separate sign-in.',403)
        raw, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        db.execute("DELETE FROM sessions WHERE expires<?", (time.time(),))
        db.execute("INSERT INTO sessions VALUES(?,?,?,?)", (hashlib.sha256(raw.encode()).hexdigest(), user["id"], csrf, time.time() + 604800))
        self.cookie = "elvia_session=" + raw + "; Path=/; HttpOnly; SameSite=Strict; Max-Age=604800"
        return {"user": self.public_user(user), "csrf": csrf}

    @staticmethod
    def public_user(user):
        return {key: user[key] for key in ("id", "login", "name", "role", "force_change")} | {"has_password":":" in user["password"]}

    def auth(self, user, admin=False, maintainer=False, db=None):
        require(user is not None, "Sign in to continue.", 401)
        require(not user["force_change"], "Choose a new password before continuing.", 403)
        if maintainer:
            require(user["role"] == "maintainer", "This page is for the maintainer.", 403)
        elif admin:
            require(staff(user), "This page is for an admin or maintainer.", 403)
        # Registration already verifies email. Check it again for business writes
        # so a legacy/imported reviewer cannot bypass the verified-account rule.
        # Read-only browsing and account recovery/sign-out remain available.
        if db is not None and user["role"] == "reviewer":
            require(db.execute("SELECT 1 FROM verified_emails WHERE user_id=? AND email=?", (user["id"], user["login"])).fetchone(), "Verify your institutional email before contributing.", 403)

    def accounts_json(self,db,user):
        self.auth(user,admin=True)
        accounts=[]
        for row in db.execute('SELECT u.id,u.login,u.name,u.role,u.created,COALESCE(c.suspended,0) AS suspended,COALESCE(c.note,\'\') AS note,EXISTS(SELECT 1 FROM verified_emails v WHERE v.user_id=u.id) AS email_verified FROM users u LEFT JOIN account_controls c ON c.user_id=u.id ORDER BY u.name COLLATE NOCASE'):
            if is_retired(db,row['id']):continue
            if not can_manage_account(user,row):continue
            accounts.append({'id':row['id'],'email':row['login'],'name':row['name'],'role':row['role'],'created':row['created'],'status':'suspended' if row['suspended'] else 'active','note':row['note'],'email_verified':bool(row['email_verified'])})
        reservations=[dict(r) for r in db.execute('SELECT email,role,created,updated FROM role_reservations ORDER BY email')] if user['role']=='maintainer' else []
        return {'accounts':accounts,'reservations':reservations,'can_assign_roles':user['role']=='maintainer'}

    def approved(self, db, user):
        self.auth(user)
        if staff(user):
            return
        app = db.execute("SELECT status FROM applications WHERE user_id=?", (user["id"],)).fetchone()
        require(app and app["status"] == "approved", "A one-time reviewer application must be approved before you review another contribution.", 403)

    def quota(self, db, user):
        day=datetime.now(ZoneInfo("America/Chicago")).date().isoformat()
        limits={"new_submit":2,"review_claim":1,"review_submit":1}
        used={action:db.execute("SELECT COUNT(*) FROM daily_usage WHERE user_id=? AND day=? AND action=?",(user["id"],day,action)).fetchone()[0] for action in limits}
        return {"day":day,"timezone":"America/Chicago","unlimited":staff(user),"limits":limits,"used":used}

    def consume_quota(self, db, user, action, target):
        if staff(user):return
        quota=self.quota(db,user)
        if db.execute("SELECT 1 FROM daily_usage WHERE user_id=? AND day=? AND action=? AND target=?",(user["id"],quota["day"],action,target)).fetchone():return
        labels={"new_submit":"two paper submissions","review_claim":"one new review claim","review_submit":"one submitted review or amendment"}
        require(quota["used"][action]<quota["limits"][action],"Daily limit reached: "+labels[action]+" per day. Your draft is saved. The allowance resets at midnight America/Chicago.",429)
        db.execute("INSERT INTO daily_usage VALUES(?,?,?,?,?)",(user["id"],quota["day"],action,target,stamp()))

    def event(self, db, user, target, action, note=""):
        db.execute("INSERT INTO events(actor,target,action,note,created) VALUES(?,?,?,?,?)", (user["id"] if user else None, target, action, note, stamp()))

    def get_item(self, db, cid, user, edit=False):
        self.auth(user)
        item = db.execute("SELECT * FROM contributions WHERE id=?", (cid,)).fetchone()
        require(item is not None, "This contribution could not be found.", 404)
        require(can_view_work(db,user,item), "This contribution belongs to a private workspace you cannot access.", 403)
        if edit:
            if item["kind"]=="review":self.approved(db, user)
            require(item["owner"] == user["id"], "Only the contributor can edit this draft.", 403)
            require(item["status"] in EDITABLE, "This version is read-only.", 409)
            require(not self.final_revision(db, cid), "A maintainer final version is in effect. Submit an amendment request instead of editing the original.", 409)
        return item

    @staticmethod
    def final_revision(db, cid):
        row = db.execute("SELECT * FROM maintainer_revisions WHERE contribution_id=? AND mode='final' ORDER BY rowid DESC LIMIT 1", (cid,)).fetchone()
        return (dict(row) | {"data": json.loads(row["data"]),'author_name':db.execute('SELECT name FROM users WHERE id=?',(row['author'],)).fetchone()['name']}) if row else None

    @staticmethod
    def amendment_json(db, row):
        value = {key: row[key] for key in row.keys() if key not in ("body", "data", "manifest")}
        value.update(json.loads(row["data"]))
        value["manifest"] = json.loads(row["manifest"])
        value["owner_name"] = db.execute("SELECT name FROM users WHERE id=?", (row["owner"],)).fetchone()["name"]
        return value

    def item_json(self, db, item):
        value = dict(item)
        value["data"] = json.loads(item["data"])
        value["admission"] = self.admission_result(db, item)
        owner = db.execute("SELECT name FROM users WHERE id=?", (item["owner"],)).fetchone()
        value["owner_name"] = owner["name"]
        pack = db.execute("SELECT id,name,sha256,size,manifest,revision FROM packages WHERE contribution_id=? ORDER BY revision DESC LIMIT 1", (item["id"],)).fetchone()
        value["package"] = dict(pack) if pack else None
        if pack:
            value["package"]["manifest"] = json.loads(pack["manifest"])
        source = db.execute("SELECT id,name,mime,sha256,size,revision FROM source_files WHERE contribution_id=? ORDER BY revision DESC LIMIT 1", (item["id"],)).fetchone()
        value["source_file"] = dict(source) if source else None
        value["task"] = dict(db.execute("SELECT * FROM tasks WHERE id=?", (item["task_id"],)).fetchone()) if item["task_id"] else None
        value["revisions"] = [dict(r) | {"data": json.loads(r["data"])} for r in db.execute("SELECT * FROM revisions WHERE contribution_id=? ORDER BY revision", (item["id"],))]
        value["events"] = [dict(r) for r in db.execute("SELECT action,note,created FROM events WHERE target=? ORDER BY id", (item["id"],))]
        value["maintainer_revisions"] = [self.maintainer_revision_json(db, r) for r in db.execute("SELECT * FROM maintainer_revisions WHERE contribution_id=? ORDER BY rowid", (item["id"],))]
        value["final_revision"] = self.final_revision(db, item["id"])
        value["scientific_status"] = "Independent review pending" if item["kind"] == "new" else "Scientific adjudication pending"
        if value["final_revision"]:
            value["scientific_status"] = "Maintainer final decision recorded; independent-review status unchanged"
        return value

    @staticmethod
    def maintainer_revision_json(db, row):
        value = dict(row) | {"data": json.loads(row["data"])}
        author=db.execute('SELECT name,role FROM users WHERE id=?',(row['author'],)).fetchone()
        value.update(author_name=author['name'],author_role=value['data'].get('record_author_role',author['role']))
        package = db.execute("SELECT id,name,sha256,size FROM revision_files WHERE revision_id=?", (row["id"],)).fetchone()
        value["package"] = dict(package) if package else None
        return value

    @staticmethod
    def check_version(item, version):
        require(isinstance(version, int) and item["version"] == version,
                "A newer version was saved elsewhere. Reload this page before making another change.", 409)

    @staticmethod
    def read_embedded_zip(data):
        try:
            blob = base64.b64decode(data["package_base64"], validate=True)
        except (ValueError, TypeError, binascii.Error):
            raise Problem(400, "The package could not be read. Select the ZIP again.") from None
        filename = clean(data.get("package_name", ""), 180, "Filename")
        require(not any(c in filename for c in '/\\\r\n'), "Use a simple ZIP filename.")
        return blob, filename, inspect_zip(blob, filename)

    def rate_limit(self, key, maximum=12):
        now = time.time()
        with self.server.rate_lock:
            # Bound memory and retain hot keys: a new key cannot evict a live
            # limit and make username rotation reset the existing allowance.
            for old in list(self.server.attempts):
                if not self.server.attempts[old] or self.server.attempts[old][-1] <= now-900:
                    del self.server.attempts[old]
            key=self.server.abuse.digest('memory',key)
            require(key in self.server.attempts or len(self.server.attempts)<2048,"Too many attempts. Try again in 15 minutes.",429)
            times = [t for t in self.server.attempts.get(key, []) if t > now - 900]
            require(len(times) < maximum, "Too many attempts. Try again in 15 minutes.", 429)
            self.server.attempts[key] = times + [now]

    @staticmethod
    def admission_result(db, item):
        if item["kind"] != "new":
            return None
        key = fingerprint(json.loads(item["data"]))
        row = db.execute("SELECT id,result,created FROM admission_checks WHERE contribution_id=? AND fingerprint=? ORDER BY rowid DESC LIMIT 1", (item["id"], key)).fetchone()
        if not row:
            return None
        value = json.loads(row["result"])
        return value | {"id": row["id"], "stale": row["created"] < time.time() - 86400 and not value.get("manual")}

    def prepare_admission(self, path):
        """Perform slow public lookups outside the main SQLite write transaction."""
        match = re.fullmatch(r"/api/(admin/)?contributions/([a-z0-9_]+)/(check|submit)", path)
        if self.command != "POST" or not match:
            return
        admin_route, cid, action = match.groups()
        require(not admin_route or action == "check", "Action not found.", 404)
        body = self.body(); self.cached_body = body
        with connect(self.server.db_path) as db:
            user, session = self.identify(db)
            self.auth(user, admin=bool(admin_route), db=db)
            require(session and hmac.compare_digest(self.headers.get("X-CSRF-Token", ""), session["csrf"]), "Reload this page before checking the source.", 403)
            item = self.get_item(db, cid, user, edit=not admin_route)
            self.check_version(item, body.get("version"))
            if item["kind"] != "new":return
            record = json.loads(item["data"])
            # Submission still reports its ordinary missing-field errors before a lookup.
            if any(not record.get(k) for k in ("title", "venue", "field", "source_url")):
                if action == "check":require_fields(record, ("title", "venue", "field", "source_url"))
                return
            cached = self.admission_result(db, item)
            if cached and not cached["stale"] and not body.get("refresh"):
                return
            version = item["version"]
        self.rate_limit("admission:" + user["id"], 40)
        result = self.server.admission.check(record)
        with connect(self.server.db_path) as db:
            db.execute("BEGIN IMMEDIATE")
            fresh_user, fresh_session = self.identify(db)
            self.auth(fresh_user, admin=bool(admin_route), db=db)
            require(fresh_session and hmac.compare_digest(self.headers.get("X-CSRF-Token", ""), fresh_session["csrf"]), "Your sign-in changed during the check. Please sign in again.", 403)
            fresh = self.get_item(db, cid, fresh_user, edit=not admin_route)
            self.check_version(fresh, version)
            require(fingerprint(json.loads(fresh["data"])) == fingerprint(record), "The paper details changed during the check. Check the saved version again.", 409)
            db.execute("INSERT INTO admission_checks VALUES(?,?,?,?,?,?)", (uid("ac"), cid, fingerprint(record), dump(result), user["id"], time.time()))
            self.event(db, fresh_user, cid, "admission_" + result["status"], "Title, venue and scope check; " + CATALOG["version"])

    def dispatch(self, db, path, user, session):
        method = self.command
        if method in ("GET", "HEAD"):
            if path == "/api/health":
                return 200, {"service": "elvia-independent-local", "version": 6}
            if path == "/api/session":
                return 200, {"user": self.public_user(user) if user else None, "csrf": session["csrf"] if session else "", "policy": POLICY,"google":self.server.google.public(self.request_origin),"email_registration":self.server.mailer.public()}
            if path=="/api/admin/email-settings":
                self.auth(user,maintainer=True)
                return 200,self.server.mailer.settings()
            if path == "/api/admission-policy":
                return 200, self.server.admission.public_policy()
            if path == "/api/me":
                self.auth(user)
                app = db.execute("SELECT * FROM applications WHERE user_id=?", (user["id"],)).fetchone()
                return 200, {"application": (dict(app) | {"profile": json.loads(app["profile"])}) if app else None,
                             "quota":self.quota(db,user),
                             "google_linked":bool(db.execute("SELECT 1 FROM google_identities WHERE user_id=?",(user["id"],)).fetchone()),
                             "contributions": [self.item_json(db, i) for i in db.execute("SELECT * FROM contributions WHERE owner=? ORDER BY updated DESC", (user["id"],))],
                             "amendments": [self.amendment_json(db, r) for r in db.execute("SELECT * FROM amendments WHERE owner=? ORDER BY created DESC", (user["id"],))]}
            if path == "/api/tasks":
                tasks = []
                for row in db.execute("SELECT * FROM tasks ORDER BY created DESC,id"):
                    task = dict(row)
                    claim = db.execute("SELECT id,owner,status FROM contributions WHERE task_id=? AND status IN ('draft','needs_changes','submitted','accepted')", (row["id"],)).fetchone()
                    task["availability"] = ("Complete" if claim["status"] == "accepted" else "In progress") if claim else "Available"
                    task["final_contribution"] = claim["id"] if claim and self.final_revision(db, claim["id"]) else None
                    if task["final_contribution"]:
                        task["availability"] = "Final version recorded"
                    task["my_contribution"] = claim["id"] if claim and user and claim["owner"] == user["id"] else None
                    claimed_item=db.execute('SELECT * FROM contributions WHERE id=?',(claim['id'],)).fetchone() if claim else None
                    task["maintainer_contribution"] = claim["id"] if claim and staff(user) and can_view_work(db,user,claimed_item) else None
                    tasks.append(task)
                return 200, {"tasks": tasks}
            if path == "/api/admin":
                self.auth(user, admin=True)
                apps = [dict(a) | {"profile": json.loads(a["profile"]), "email_verified": bool(a["email_verified"])} for a in db.execute("SELECT a.*,u.name,u.login,EXISTS(SELECT 1 FROM verified_emails v WHERE v.user_id=u.id) AS email_verified FROM applications a JOIN users u ON u.id=a.user_id ORDER BY a.updated DESC")]
                apps=[a for a in apps if can_manage_account(user,db.execute('SELECT id,role FROM users WHERE id=?',(a['user_id'],)).fetchone())]
                items = [self.item_json(db, i) for i in db.execute("SELECT * FROM contributions ORDER BY CASE status WHEN 'submitted' THEN 0 ELSE 1 END,updated DESC") if can_view_work(db,user,i)]
                return 200, {"applications": apps, "contributions": items,
                             "amendments": [self.amendment_json(db, r) for r in db.execute("SELECT * FROM amendments ORDER BY CASE status WHEN 'pending' THEN 0 ELSE 1 END,created DESC")] if user['role']=='maintainer' else []}
            if path == '/api/admin/accounts':return 200,self.accounts_json(db,user)
            if path == "/api/finals":
                self.approved(db, user)
                items = []
                for row in db.execute("SELECT DISTINCT contribution_id FROM maintainer_revisions WHERE mode='final'"):
                    final = self.final_revision(db, row["contribution_id"])
                    items.append({"contribution_id": row["contribution_id"], "id": final["id"], "title": final["data"]["title"], "scope": final["data"].get("summary") or final["data"].get("scope", ""), "created": final["created"], "synthetic": final["data"].get("synthetic", False)})
                return 200, {"finals": items}
            match = re.fullmatch(r"/api/finals/([a-z0-9_]+)", path)
            if match:
                self.approved(db, user)
                final = self.final_revision(db, match[1])
                require(final, "No maintainer final version has been recorded for this contribution.", 404)
                history = [self.maintainer_revision_json(db, r) for r in db.execute("SELECT * FROM maintainer_revisions WHERE contribution_id=? ORDER BY rowid", (match[1],))]
                final["package"] = next(r["package"] for r in history if r["id"] == final["id"])
                return 200, {"final": final, "history": history, "maintainer": final['author_name']}
            if path.startswith("/api/revision-files/"):
                self.approved(db, user)
                package = db.execute("SELECT * FROM revision_files WHERE id=?", (path.rsplit("/", 1)[-1],)).fetchone()
                require(package, "Revision package not found.", 404)
                revision = db.execute("SELECT contribution_id FROM maintainer_revisions WHERE id=?", (package["revision_id"],)).fetchone()
                if not self.final_revision(db, revision["contribution_id"]):
                    self.get_item(db, revision["contribution_id"], user)
                return 200, bytes(package["body"]), "application/zip", {"Content-Disposition": "attachment; filename=\"revision.zip\"; filename*=UTF-8''" + quote(package["name"])}
            match = re.fullmatch(r"/api/amendments/([a-z0-9_]+)(/package)?", path)
            if match:
                self.auth(user)
                row = db.execute("SELECT * FROM amendments WHERE id=?", (match[1],)).fetchone()
                require(row, "Amendment request not found.", 404)
                require(row["owner"] == user["id"] or user["role"] == "maintainer", "This amendment request is private to its applicant and the maintainer.", 403)
                if match[2]:
                    require(row["body"] is not None, "This request has no package.", 404)
                    return 200, bytes(row["body"]), "application/zip", {"Content-Disposition": "attachment; filename=\"amendment.zip\"; filename*=UTF-8''" + quote(row["package_name"])}
                return 200, self.amendment_json(db, row)
            if path == "/api/contributors":
                people = {}
                for item in db.execute("SELECT * FROM contributions WHERE status='accepted' ORDER BY updated,id"):
                    data = json.loads(item["data"])
                    if data.get("credit") != "named" or data.get("synthetic"):
                        continue
                    u = db.execute("SELECT name FROM users WHERE id=?", (item["owner"],)).fetchone()
                    entry = people.setdefault(item["owner"], {"name": u["name"], "contributions": []})
                    entry["contributions"].append({"id": item["id"], "title": data["title"], "roles": data.get("roles", []), "accepted": item["updated"], "kind": item["kind"]})
                return 200, {"contributors": sorted(people.values(), key=lambda p: p["name"].casefold())}
            if path.startswith("/api/credit/"):
                cid = path.rsplit("/", 1)[-1]
                item = db.execute("SELECT * FROM contributions WHERE id=? AND status='accepted'", (cid,)).fetchone()
                require(item is not None, "A contribution record is available after acceptance.", 404)
                data = json.loads(item["data"])
                public = data.get("credit") == "named" and not data.get("synthetic")
                require(public or can_view_work(db,user,item), "Sign in with the contributing account to see this private record.", 401)
                name = db.execute("SELECT name FROM users WHERE id=?", (item["owner"],)).fetchone()["name"]
                package = db.execute("SELECT sha256 FROM packages WHERE contribution_id=? ORDER BY revision DESC LIMIT 1", (cid,)).fetchone()
                return 200, {"id": cid, "name": name, "title": data["title"], "roles": data.get("roles", []), "scope": data.get("summary") or data.get("scope", ""), "kind": item["kind"], "revision": item["revision"], "accepted": item["updated"], "synthetic": bool(data.get("synthetic")), "ai_used": data.get("ai_used"), "sha256": package["sha256"], "public": public, "issuer": "ELVIA", "status": "Contribution accepted; scientific adjudication remains separate."}
            match = re.fullmatch(r"/api/contributions/([a-z0-9_]+)", path)
            if match:
                return 200, self.item_json(db, self.get_item(db, match[1], user))
            if path.startswith(("/api/packages/", "/api/source-files/")):
                source_file = path.startswith("/api/source-files/")
                table = "source_files" if source_file else "packages"
                pack = db.execute("SELECT * FROM " + table + " WHERE id=?", (path.rsplit("/", 1)[-1],)).fetchone()
                require(pack is not None, "Package not found.", 404)
                self.auth(user)
                item = db.execute("SELECT * FROM contributions WHERE id=?", (pack["contribution_id"],)).fetchone()
                assigned = db.execute("SELECT 1 FROM contributions c JOIN tasks t ON c.task_id=t.id WHERE c.owner=? AND t.source_id=? AND c.status IN ('draft','needs_changes','submitted','accepted')", (user["id"], pack["contribution_id"])).fetchone()
                require(can_view_work(db,user,item) or assigned, "This package is private to its contributor, assigned reviewer and authorized managers.", 403)
                return 200, bytes(pack["body"]), pack["mime"] if source_file else "application/zip", {"Content-Disposition": "attachment; filename=\"download\"; filename*=UTF-8''" + quote(pack["name"])}
            if path.startswith("/api/task-source/"):
                self.approved(db, user)
                task = db.execute("SELECT source_id FROM tasks WHERE id=?", (path.rsplit("/", 1)[-1],)).fetchone()
                require(task and task["source_id"], "No source package for this exercise.", 404)
                assigned = db.execute("SELECT 1 FROM contributions WHERE task_id=? AND owner=? AND status IN ('draft','needs_changes','submitted','accepted')", (path.rsplit("/", 1)[-1], user["id"])).fetchone()
                require(assigned, "Claim this task before accessing its source package.", 403)
                pack = db.execute("SELECT id,name FROM packages WHERE contribution_id=? ORDER BY revision DESC LIMIT 1", (task["source_id"],)).fetchone()
                source = db.execute("SELECT id,name FROM source_files WHERE contribution_id=? ORDER BY revision DESC LIMIT 1", (task["source_id"],)).fetchone()
                original = json.loads(db.execute("SELECT data FROM contributions WHERE id=?", (task["source_id"],)).fetchone()["data"])
                return 200, dict(pack) | {"source_file": dict(source) if source else None, "source_url": original.get("source_url", "")}
            raise Problem(404, "Page not found.")

        # Mutations use a single write transaction for claim exclusivity and versions.
        if path=="/api/admin/email-settings" and method=="POST":
            self.auth(user,maintainer=True)
            require(session and hmac.compare_digest(self.headers.get("X-CSRF-Token",""),session["csrf"]),"Reload Account before changing email settings.",403)
            try:self.server.mailer.save(self.body())
            except MailError as exc:raise Problem(400,str(exc)) from None
            self.event(db,user,"email-service","email_settings_updated","SMTP configuration and institutional domains updated; secrets excluded from this log.")
            return 200,self.server.mailer.settings()
        if path == "/api/auth/google/start" and method == "POST":
            self.rate_limit("google-start",30)
            data=self.body();mode=data.get("mode","login")
            require(mode in ("login","link"),"Choose sign-in or account linking.")
            if mode=="link":
                self.auth(user,admin=True)
                require(session and hmac.compare_digest(self.headers.get("X-CSRF-Token",""),session["csrf"]),"Reload Account before linking Google.",403)
                require(password_matches(data.get("password",""),user["password"]),"Confirm your current local password to link Google.",403)
            else:require(data.get("accept_terms") is True,"Read and acknowledge the privacy notice and local terms before continuing.")
            try:url,self.cookie=self.server.google.start(db,user if mode=="link" else None,session if mode=="link" else None,mode,origin=self.request_origin)
            except GoogleLoginError as exc:raise Problem(503,str(exc)) from None
            return 200,{"authorization_url":url}
        if path == "/api/auth/login" and method == "POST":
            data = self.body()
            login = clean(data.get("login", ""), 254, "Account").lower()
            state=self.server.login_guard.state(db,self.login_source,time.time())
            if state['locked']:return self.login_failure(state)
            self.rate_limit("login:" + login)
            row = resolve_login(db,login)
            valid = password_matches(data.get("password", ""), row["password"] if row else self.server.dummy_hash)
            if not row or not valid:
                return self.login_failure(self.server.login_guard.failure(db,self.login_source,time.time()))
            require(not suspended(db,row['id']), 'This account is suspended. Contact a site manager to request a review.',403)
            self.server.login_guard.clear(db,self.login_source)
            return 200, self.session(db, row)
        if path == "/api/auth/register" and method == "POST":
            self.rate_limit("registration", 30)
            data = self.body()
            require(data.get("accept_terms") is True,"Read and acknowledge the privacy notice and local terms before creating an account.")
            email = clean(data.get("email", ""), 254, "Email").lower()
            name = clean(data.get("name", ""), 150, "Name")
            require(name and re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email), "Enter your name and a valid email address.")
            require(eligible_email(email,self.server.mailer.domains),"Use an academic email or an approved research-institution domain.")
            challenge=db.execute("SELECT * FROM email_challenges WHERE id=? AND email=? AND sent=1 AND expires>? AND attempts<5",(getattr(self,"verified_challenge",""),email,time.time())).fetchone()
            require(challenge,"Verify your email with a current code before creating an account.")
            hashed = password_hash(data.get("password", ""))
            require(not login_claimed(db,email), "An account with this email already exists. Sign in instead.", 409)
            user_id = uid("u")
            reserved=db.execute('SELECT role FROM role_reservations WHERE email=?',(email,)).fetchone()
            role=reserved['role'] if reserved and reserved['role'] in ('admin','maintainer') else 'reviewer'
            db.execute("INSERT INTO users VALUES(?,?,?,?,?,?,?)", (user_id, email, name, role, hashed, 0, stamp()))
            db.execute("INSERT INTO policy_acceptances VALUES(?,?,?,?)",(user_id,POLICY_VERSION,stamp(),"email"))
            db.execute("INSERT INTO verified_emails VALUES(?,?,?)",(user_id,email,stamp()))
            db.execute("UPDATE email_challenges SET sent=0 WHERE email=?",(email,))
            row = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
            self.event(db, row, user_id, "account_created")
            if reserved:
                db.execute('DELETE FROM role_reservations WHERE email=?',(email,))
                self.event(db,row,user_id,'reserved_role_activated',role+' after email verification')
            return 201, self.session(db, row)
        require(user is not None, "Sign in to continue.", 401)
        require(session and hmac.compare_digest(self.headers.get("X-CSRF-Token", ""), session["csrf"]), "Your sign-in token changed. Reload this page and try again.", 403)
        if path=='/api/admin/roles' and method=='POST':
            self.auth(user,maintainer=True)
            data=self.body();self.rate_limit('role-assignment:'+user['id'],30)
            require(password_matches(data.get('password',''),user['password']),'Confirm your current password before assigning or removing a role.',403)
            email=normalize_email(data.get('email',''));role=data.get('role')
            require(email and role in ('reviewer','admin','maintainer'),'Enter an exact email and choose a listed role.')
            target=resolve_login(db,email)
            require(target is not None or not login_claimed(db,email),'This historical or linked identity cannot receive a separate role.',403)
            if target:
                require(can_manage_account(user,target),'Your own account and other maintainer accounts are separately controlled.',403)
                require(role=='reviewer' or db.execute('SELECT 1 FROM verified_emails WHERE user_id=?',(target['id'],)).fetchone(),'Email ownership must be verified before granting a management role.')
                require(role!='maintainer' or not suspended(db,target['id']),'Reactivate this account before assigning the maintainer role.')
                db.execute('UPDATE users SET role=? WHERE id=?',(role,target['id']))
                db.execute('DELETE FROM sessions WHERE user_id=?',(target['id'],))
                db.execute('DELETE FROM role_reservations WHERE email=?',(email,))
                self.event(db,user,target['id'],'account_role_changed',target['role']+' -> '+role)
                return 200,{'status':'updated','message':'Role updated. The account must sign in again.','role':role}
            if role=='reviewer':
                db.execute('DELETE FROM role_reservations WHERE email=?',(email,))
                self.event(db,user,email,'role_reservation_removed')
                return 200,{'status':'removed','message':'Reserved role removed. No message was sent.'}
            require(eligible_email(email,self.server.mailer.domains),'Use an academic or approved research-institution email. The person must complete normal email verification.')
            db.execute('INSERT INTO role_reservations VALUES(?,?,?,?,?) ON CONFLICT(email) DO UPDATE SET role=excluded.role,updated=excluded.updated',(email,role,user['id'],stamp(),stamp()))
            self.event(db,user,email,'role_reserved',role)
            return 200,{'status':'reserved','message':'Role reserved for this exact email after verification. No invitation was sent.'}
        account_action=re.fullmatch(r'/api/admin/accounts/([a-z0-9_]+)/status',path)
        if account_action and method=='POST':
            self.auth(user,admin=True);data=self.body()
            target=db.execute('SELECT id,role FROM users WHERE id=?',(account_action[1],)).fetchone()
            require(target and not is_retired(db,target['id']),'This historical identity cannot be reactivated.',403)
            require(can_manage_account(user,target),'You cannot change your own account or an account at or above your role.',403)
            state=data.get('status');note=clean(data.get('note',''),1500,'Account decision reason')
            require(state in ('active','suspended') and len(note)>=10,'Choose a status and give a reason of at least 10 characters.')
            db.execute('INSERT INTO account_controls VALUES(?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET suspended=excluded.suspended,note=excluded.note,updated_by=excluded.updated_by,updated=excluded.updated',(target['id'],int(state=='suspended'),note,user['id'],stamp()))
            if state=='suspended':db.execute('DELETE FROM sessions WHERE user_id=?',(target['id'],))
            self.event(db,user,target['id'],'account_'+state,note)
            return 200,{'status':state,'message':'Account '+state+'. Saved work and its history are retained.'}
        match = re.fullmatch(r"/api/(admin/)?contributions/([a-z0-9_]+)/(check|admission-resolution)", path)
        if match and method == "POST":
            admin_route, cid, action = match.groups()
            self.auth(user, admin=bool(admin_route) or action == "admission-resolution", db=db)
            item = self.get_item(db, cid, user, edit=not admin_route)
            data = self.body(); self.check_version(item, data.get("version"))
            require(item["kind"] == "new", "Eligibility checks apply to new papers only.")
            if action == "admission-resolution":
                record = json.loads(item["data"])
                require_fields(record, ("title", "venue", "field", "source_url"))
                require(data.get("identity_confirmed") is True, "Confirm the title and venue against the official article record.")
                source = clean(data.get("evidence_url", ""), 2000, "Evidence URL")
                note = clean(data.get("note", ""), 4000, "Verification note")
                require(not unsafe_url(source) and len(note) >= 20, "Add a public HTTPS evidence link and a verification note of at least 20 characters.")
                metadata = {"title":record["title"], "venue":record["venue"], "issns":[], "bound_to_url":True,
                            "identity_source":source, "type":"journal-article", "paper_type":"unknown"}
                metric = None
                is_arxiv=bool(arxiv_identifier(record["source_url"]))
                if is_arxiv:
                    metadata.update(venue="arXiv",type="preprint",arxiv_id=arxiv_identifier(record["source_url"]))
                if record["field"] == "computer_science" and not is_arxiv:
                    require(data.get("full_paper") is True, "Confirm a full or regular main-conference paper, not a companion track.")
                    metadata.update(type="proceedings-article", paper_type="full")
                if record["field"] in ("chemistry", "biological_science") and not is_arxiv and not top_journal(record["venue"]):
                    try:
                        jif, year = float(data.get("jif", "")), int(data.get("jif_year", ""))
                    except (ValueError, TypeError):raise Problem(400, "Enter the verified JIF and its data year.") from None
                    require(1975 <= year <= datetime.now().year-1 and 10 < jif < 2000, "Use the most recent verifiable JIF, with its data year; the value must be strictly greater than 10.")
                    metric_source = clean(data.get("metric_url", ""), 2000, "Metric source")
                    metric = {"journal":record["venue"], "issns":[], "year":year, "value":jif, "source":metric_source, "verified_at":stamp(), "method":"Maintainer checked official evidence"}
                result = self.server.admission.evaluate(record, metadata, metric)
                require(result["status"] == "pass", "The supplied evidence does not satisfy the current hard criteria. Correct the source or update the published scope policy first.")
                result.update(manual=True, note=note, verifier=user["name"])
                db.execute("INSERT INTO admission_checks VALUES(?,?,?,?,?,?)", (uid("ac"), cid, fingerprint(record), dump(result), user["id"], time.time()))
                self.event(db, user, cid, "admission_verified_by_"+user["role"], note)
            return 200, self.item_json(db, self.get_item(db, cid, user))
        if path == "/api/auth/logout" and method == "POST":
            db.execute("DELETE FROM sessions WHERE token=?", (session["token"],))
            self.cookie = "elvia_session=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0"
            return 200, {"ok": True}
        if path == "/api/auth/password" and method == "POST":
            self.rate_limit("password:" + user["id"])
            data = self.body()
            require(password_matches(data.get("current", ""), user["password"]), "Your current password is incorrect.")
            require(data.get("current") != data.get("password"), "Choose a different password.")
            db.execute("UPDATE users SET password=?,force_change=0 WHERE id=?", (password_hash(data.get("password", "")), user["id"]))
            db.execute('UPDATE password_reset_tokens SET used=1 WHERE user_id=?',(user['id'],))
            db.execute("DELETE FROM sessions WHERE user_id=?", (user["id"],))
            row = db.execute("SELECT * FROM users WHERE id=?", (user["id"],)).fetchone()
            self.event(db, user, user["id"], "password_changed")
            if user['login']=='minhao' and user['force_change']:
                self.remove_bootstrap_file = True
            return 200, self.session(db, row)
        self.auth(user, db=db)
        match = re.fullmatch(r"/api/admin/contributions/([a-z0-9_]+)/revisions", path)
        if match and method == "POST":
            self.auth(user, admin=True)
            incoming = self.body(POLICY["max_zip_bytes"] * 4 // 3 + 100_000); item = self.get_item(db, match[1], user)
            self.check_version(item, incoming.get("version"))
            mode = incoming.get("mode")
            require(mode in ("ordinary", "final"), "Choose an ordinary revision or a maintainer final decision.")
            require(mode!='final' or user['role']=='maintainer','Only a maintainer can record a final decision.',403)
            note = clean(incoming.get("note", ""), 6000, "Revision explanation")
            supplied = incoming.get("data", {})
            require(isinstance(supplied, dict), "Invalid revision fields.")
            record = json.loads(item["data"])
            record["title"] = clean(supplied.get("title", record.get("title", "")), 500, "Paper title")
            require(record["title"], "Add the paper title before recording a revision.")
            record["record_author"] = user["name"]
            record['record_author_role']=user['role']
            for key in ("summary", "location", "scope", "reasoning", "verification", "limits", "ai_model", "ai_details"):
                record[key] = clean(supplied.get(key, record.get(key, "")), TEXT_FIELDS[key], key.replace("_", " "))
            record["summary"] = record["summary"] or record["reasoning"]
            require(len(record["summary"]) >= 40, "Add a revision summary of at least 40 characters.")
            note = note or record["summary"]
            record["assessment"] = supplied.get("assessment")
            require(record["assessment"] in ASSESSMENTS, "Choose a scoped assessment.")
            record["ai_used"] = supplied.get("ai_used")
            require(record["ai_used"] in ("yes", "no"), "Declare whether this revision used AI.")
            if record["ai_used"] == "yes":
                require(record["ai_model"] in POLICY["models"] and len(record["ai_details"]) >= 20, "Use a listed AI configuration and describe its use and your checks.")
            else:
                record["ai_model"] = record["ai_details"] = ""
            request_id = incoming.get("amendment_id")
            if request_id:
                request = db.execute("SELECT * FROM amendments WHERE id=?", (request_id,)).fetchone()
                require(request and request["contribution_id"] == item["id"] and request["status"] == "pending", "This amendment request is no longer pending for this contribution.", 409)
                current_final = self.final_revision(db, item["id"])
                require(current_final and request["final_revision"] == current_final["id"], "This request concerns an earlier final version. Review it against the current final version first.", 409)
                require(mode == "final", "Adopting an amendment requires a new maintainer final version.")
            revision_id = uid("mr")
            db.execute("INSERT INTO maintainer_revisions VALUES(?,?,?,?,?,?,?)", (revision_id, item["id"], user["id"], mode, dump(record), note, stamp()))
            if incoming.get("package_base64"):
                blob, filename, manifest = self.read_embedded_zip(incoming)
                db.execute("INSERT INTO revision_files VALUES(?,?,?,?,?,?,?)", (uid("rf"), revision_id, filename, hashlib.sha256(blob).hexdigest(), len(blob), dump(manifest), blob))
            db.execute("UPDATE contributions SET version=version+1 WHERE id=?", (item["id"],))
            self.event(db, user, item["id"], user['role'] + "_" + mode + "_revision", note)
            if request_id:
                db.execute("UPDATE amendments SET status='accepted',decision=?,updated=? WHERE id=?", (note, stamp(), request_id))
                self.event(db, user, request_id, "amendment_accepted", "Adopted in " + revision_id)
            return 200, self.item_json(db, self.get_item(db, item["id"], user))
        match = re.fullmatch(r"/api/finals/([a-z0-9_]+)/amendments", path)
        if match and method == "POST":
            self.approved(db, user)
            data = self.body(POLICY["max_zip_bytes"] * 4 // 3 + 100_000)
            final = self.final_revision(db, match[1])
            require(final and data.get("final_revision") == final["id"], "The final version changed. Reload it before submitting your request.", 409)
            require(not db.execute("SELECT 1 FROM amendments WHERE final_revision=? AND owner=? AND status='pending'", (final["id"], user["id"])).fetchone(), "You already have a pending request for this version. Its decision will appear in My work.", 409)
            record = {key: clean(data.get(key, ""), limit, key) for key, limit in [("reason", 6000), ("proposed", 12000), ("ai_details", 4000), ("ai_model", 200)]}
            require(len(record["reason"]) >= 40, "Explain the proposed change and reason, with at least 40 characters.")
            record["ai_used"] = data.get("ai_used")
            require(record["ai_used"] in ("yes", "no"), "Declare whether you used AI in this request.")
            if record["ai_used"] == "yes":
                require(record["ai_model"] in POLICY["models"] and len(record["ai_details"]) >= 20, "Add a listed AI configuration and describe your use and checks.")
            else:
                record["ai_model"] = record["ai_details"] = ""
            blob, filename, digest, manifest = None, "", "", []
            if data.get("package_base64"):
                try:
                    blob = base64.b64decode(data["package_base64"], validate=True)
                except (ValueError, TypeError, binascii.Error):
                    raise Problem(400, "The package could not be read. Select the ZIP again.") from None
                filename = clean(data.get("package_name", ""), 180, "Filename")
                require(not any(c in filename for c in '/\\\r\n'), "Use a simple ZIP filename.")
                manifest = inspect_zip(blob, filename)
                digest = hashlib.sha256(blob).hexdigest()
            aid = uid("am")
            self.consume_quota(db,user,"review_submit",match[1])
            db.execute("INSERT INTO amendments VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (aid, match[1], final["id"], user["id"], "pending", dump(record), filename, digest, len(blob) if blob else 0, dump(manifest), blob, "", stamp(), stamp()))
            self.event(db, user, aid, "amendment_requested", "For final version " + final["id"])
            return 201, self.amendment_json(db, db.execute("SELECT * FROM amendments WHERE id=?", (aid,)).fetchone())
        match = re.fullmatch(r"/api/admin/amendments/([a-z0-9_]+)", path)
        if match and method == "POST":
            self.auth(user, maintainer=True)
            data = self.body(); decision = data.get("decision"); note = clean(data.get("note", ""), 6000, "Decision note")
            require(decision in ("declined", "needs_changes") and note, "Explain the decision. To adopt a request, write a new final version.")
            row = db.execute("SELECT status FROM amendments WHERE id=?", (match[1],)).fetchone()
            require(row and row["status"] == "pending", "This request is no longer pending.", 409)
            db.execute("UPDATE amendments SET status=?,decision=?,updated=? WHERE id=?", (decision, note, stamp(), match[1]))
            self.event(db, user, match[1], "amendment_" + decision, note)
            return 200, {"status": decision}
        if path == "/api/application" and method == "POST":
            require(user["role"] == "reviewer", "Reviewer applications use a reviewer account.", 403)
            data = self.body()
            profile = {key: clean(data.get(key, ""), limit, key.replace("_", " ")) for key, limit in [("position", 150), ("institution", 300), ("expertise", 3000), ("profile_url", 2000), ("eligibility_note", 2000)]}
            require_fields(profile, ("position", "institution", "expertise"))
            require(not profile["profile_url"] or web_url(profile["profile_url"]), "Use a full http or https profile URL.")
            require(academic_email(user["login"]) or profile["eligibility_note"], "For a non-academic email, explain how the maintainer can assess your background.")
            existing = db.execute("SELECT status FROM applications WHERE user_id=?", (user["id"],)).fetchone()
            require(not existing or existing["status"] != "approved", "Your application is already approved.", 409)
            profile["academic_domain"] = academic_email(user["login"])
            db.execute("INSERT INTO applications VALUES(?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET profile=excluded.profile,status=excluded.status,note=excluded.note,updated=excluded.updated", (user["id"], dump(profile), "pending", "", stamp()))
            self.event(db, user, user["id"], "application_submitted")
            return 200, {"status": "pending"}
        match = re.fullmatch(r"/api/admin/applications/([a-z0-9_]+)", path)
        if match and method == "POST":
            self.auth(user, admin=True)
            data = self.body(); decision = data.get("decision"); note = clean(data.get("note", ""), 4000, "Decision note")
            require(can_manage_account(user,db.execute('SELECT id,role FROM users WHERE id=?',(match[1],)).fetchone()),'You cannot manage this account.',403)
            require(decision in ("approved", "needs_information", "declined"), "Choose an application decision.")
            require(decision == "approved" or note, "Explain what the applicant should know.")
            require(db.execute("SELECT 1 FROM applications WHERE user_id=?", (match[1],)).fetchone(), "Application not found.", 404)
            db.execute("UPDATE applications SET status=?,note=?,updated=? WHERE user_id=?", (decision, note, stamp(), match[1]))
            self.event(db, user, match[1], "application_" + decision, note)
            return 200, {"status": decision}
        if path == "/api/contributions" and method == "POST":
            data = self.body(); kind = data.get("kind")
            require(kind in ("review", "new"), "Choose a contribution track.")
            if kind=="review":self.approved(db,user)
            count = db.execute("SELECT COUNT(*) FROM contributions WHERE owner=? AND status IN ('draft','needs_changes')", (user["id"],)).fetchone()[0]
            require(staff(user) or count < 10, "Finish or set aside a saved draft first. You can have ten active drafts.", 409)
            task_id, record = None, {"credit": "private", "roles": ["Verification" if kind == "review" else "Analysis"]}
            if kind == "review":
                task_id = data.get("task_id")
                task = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
                require(task, "Task not found.", 404)
                require(data.get("conflict_clear") is True, "Confirm that you have no conflict with this review.")
                existing = db.execute("SELECT 1 FROM contributions WHERE task_id=? AND status IN ('draft','needs_changes','submitted','accepted')", (task_id,)).fetchone()
                require(not existing, "This task was already claimed. Choose another task.", 409)
                if task["source_id"]:
                    original = db.execute("SELECT owner FROM contributions WHERE id=?", (task["source_id"],)).fetchone()
                    require(not same_person(db,original["owner"],user["id"]), "An independent review needs a different contributor.", 403)
                record.update(title=task["title"], scope=task["question"], synthetic=bool(task["synthetic"]), conflict_clear=True)
                self.consume_quota(db,user,"review_claim",task_id)
            cid = uid("c")
            db.execute("INSERT INTO contributions VALUES(?,?,?,?,?,?,?,?,?,?,?)", (cid, user["id"], kind, task_id, "draft", dump(record), 1, 1, "", stamp(), stamp()))
            self.event(db, user, cid, "draft_created")
            return 201, self.item_json(db, self.get_item(db, cid, user))
        match = re.fullmatch(r"/api/contributions/([a-z0-9_]+)(?:/(package|source|submit|release))?", path)
        if match:
            cid, action = match.groups()
            item = self.get_item(db, cid, user, edit=True)
            if action in ("package", "source") and method == "POST":
                try:
                    version = int(self.headers.get("X-Version", "0"))
                except ValueError:
                    raise Problem(400, "Invalid draft version.") from None
                self.check_version(item, version)
                filename = clean(unquote(self.headers.get("X-Filename", "evidence.zip")), 180, "Filename")
                require(not any(c in filename for c in '/\\\r\n'), "Use a simple ZIP filename.")
                blob = self.body(POLICY["max_zip_bytes"], binary=True)
                if action == "source":
                    require(item["kind"] == "new", "Source uploads belong to a new paper analysis.")
                    if filename.lower().endswith(".pdf"):
                        require(blob.startswith(b"%PDF-") and b"%%EOF" in blob[-4096:], "This does not look like a complete PDF. Upload a PDF or ZIP.")
                        mime, manifest = "application/pdf", [{"name": filename, "size": len(blob)}]
                    else:
                        mime, manifest = "application/zip", inspect_zip(blob, filename)
                    existing = db.execute("SELECT id FROM source_files WHERE contribution_id=? AND revision=?", (cid, item["revision"])).fetchone()
                    sid = existing["id"] if existing else uid("src")
                    db.execute("INSERT INTO source_files VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(contribution_id,revision) DO UPDATE SET name=excluded.name,mime=excluded.mime,sha256=excluded.sha256,size=excluded.size,manifest=excluded.manifest,body=excluded.body", (sid, cid, item["revision"], filename, mime, hashlib.sha256(blob).hexdigest(), len(blob), dump(manifest), blob))
                    db.execute("UPDATE contributions SET version=version+1,updated=? WHERE id=?", (stamp(), cid))
                    self.event(db, user, cid, "source_saved", filename)
                    return 200, self.item_json(db, self.get_item(db, cid, user))
                manifest = inspect_zip(blob, filename)
                existing = db.execute("SELECT id FROM packages WHERE contribution_id=? AND revision=?", (cid, item["revision"])).fetchone()
                pid = existing["id"] if existing else uid("pkg")
                db.execute("INSERT INTO packages VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(contribution_id,revision) DO UPDATE SET name=excluded.name,sha256=excluded.sha256,size=excluded.size,manifest=excluded.manifest,body=excluded.body", (pid, cid, item["revision"], filename, hashlib.sha256(blob).hexdigest(), len(blob), dump(manifest), blob))
                db.execute("UPDATE contributions SET version=version+1,updated=? WHERE id=?", (stamp(), cid))
                self.event(db, user, cid, "package_saved", filename)
            else:
                data = self.body(); self.check_version(item, data.get("version"))
                if not action and method == "PUT":
                    incoming = data.get("data", {})
                    require(isinstance(incoming, dict), "Invalid contribution fields.")
                    record = {k: clean(incoming.get(k, ""), limit, k.replace("_", " ")) for k, limit in TEXT_FIELDS.items()}
                    for key, values in [("assessment", ASSESSMENTS | {""}), ("source_access", {"public", "upload", ""}), ("ai_used", {"yes", "no", ""}), ("credit", {"named", "private"})]:
                        record[key] = incoming.get(key, "private" if key == "credit" else "")
                        require(record[key] in values, f"Choose a valid {key.replace('_', ' ')} option.")
                    roles = incoming.get("roles", [])
                    require(isinstance(roles, list) and all(r in POLICY["roles"] for r in roles), "Choose listed contribution roles.")
                    record["roles"] = list(dict.fromkeys(roles)) or ["Verification" if item["kind"] == "review" else "Analysis"]
                    record["conflict_clear"] = incoming.get("conflict_clear") is True
                    record["synthetic"] = bool(json.loads(item["data"]).get("synthetic")) if item["task_id"] else incoming.get("synthetic") is True
                    if record["ai_used"] == "no":
                        record["ai_model"] = record["ai_details"] = ""
                    db.execute("UPDATE contributions SET data=?,version=version+1,updated=? WHERE id=?", (dump(record), stamp(), cid))
                elif action == "release" and method == "POST":
                    db.execute("UPDATE contributions SET status='released',version=version+1,updated=? WHERE id=?", (stamp(), cid))
                    self.event(db, user, cid, "released", "Draft retained; task available again.")
                elif action == "submit" and method == "POST":
                    record = json.loads(item["data"])
                    needed = ["title", "summary"]
                    if item["kind"] == "new":
                        needed += ["venue", "field"]
                    require_fields(record, needed)
                    require(len(record["summary"]) >= 40, "Add a review summary of at least 40 characters.")
                    require(record.get("assessment") in ASSESSMENTS and record.get("roles"), "Choose an assessment and at least one contribution role.")
                    require(record.get("conflict_clear") is True and data.get("attest") is True, "Confirm your relationship to the work and responsibility for this submission.")
                    require(record.get("ai_used") in ("yes", "no"), "Declare whether you used AI.")
                    if record["ai_used"] == "yes":
                        require(record.get("ai_model") in POLICY["models"] and len(record.get("ai_details", "")) >= 20, "Use a listed AI configuration and describe the actual model, setting, date and your checks.")
                    if item["kind"] == "new":
                        require(record.get("source_access") in ("public", "upload"), "Choose an official public link or upload the paper and supplementary materials.")
                        if record["source_access"] == "public":
                            require(web_url(record["source_url"]), "Published paper URL is required: use the official publicly accessible source.")
                        else:
                            source = db.execute("SELECT id FROM source_files WHERE contribution_id=? ORDER BY revision DESC LIMIT 1", (cid,)).fetchone()
                            require(source, "Upload the paper and supplementary materials as one PDF or ZIP before submitting.")
                            record["source_file_id"] = source["id"]
                        require(web_url(record["source_url"]), "The official article landing page URL is required even when you upload the full text.")
                        admission = self.admission_result(db, item)
                        require(admission and not admission["stale"], "Check the paper details against the current eligibility policy before submitting.")
                        require(admission["status"] != "blocked", "The paper does not meet the current submission requirements. See the eligibility check and correct the paper details.")
                        record["admission_check_id"] = admission["id"]
                        record["admission_status_at_submission"] = admission["status"]
                        existing = record["source_url"] and db.execute("SELECT id FROM contributions WHERE kind='new' AND id<>? AND status IN ('submitted','accepted') AND json_extract(data,'$.source_url')=?", (cid, record["source_url"])).fetchone()
                        require(not existing, "This source already has a submitted analysis. Ask the maintainer about a follow-up before duplicating it.", 409)
                    pack = db.execute("SELECT id FROM packages WHERE contribution_id=? ORDER BY revision DESC LIMIT 1", (cid,)).fetchone()
                    require(pack, "Attach one ZIP evidence package before submitting.")
                    record["policy_version"] = POLICY["policy_version"]
                    self.consume_quota(db,user,"new_submit" if item["kind"]=="new" else "review_submit",cid)
                    db.execute("INSERT INTO revisions VALUES(?,?,?,?,?)", (cid, item["revision"], dump(record), pack["id"], stamp()))
                    db.execute("UPDATE contributions SET status='submitted',data=?,version=version+1,updated=? WHERE id=?", (dump(record), stamp(), cid))
                    self.event(db, user, cid, "submitted", f"Revision {item['revision']}")
                else:
                    raise Problem(405, "This action is not available.")
            return 200, self.item_json(db, self.get_item(db, cid, user))
        match = re.fullmatch(r"/api/admin/contributions/([a-z0-9_]+)/decision", path)
        if match and method == "POST":
            self.auth(user, admin=True)
            data = self.body(); item = self.get_item(db, match[1], user)
            self.check_version(item, data.get("version"))
            require(user['role']=='maintainer' or item['owner']!=user['id'], 'Another admin or a maintainer must review your own submission.',403)
            require(item["status"] == "submitted", "Only a submitted contribution can receive this decision.", 409)
            decision, note = data.get("decision"), clean(data.get("note", ""), 6000, "Decision note")
            require(decision in ("accepted", "needs_changes", "declined") and note, "Choose a decision and explain it to the contributor.")
            if decision == "accepted" and item["kind"] == "new":
                admission = self.admission_result(db, item)
                require(admission and admission["status"] == "pass" and not admission["stale"], "Resolve or refresh the paper identity and venue eligibility check before accepting this contribution.", 409)
            revision = item["revision"] + (1 if decision == "needs_changes" else 0)
            db.execute("UPDATE contributions SET status=?,note=?,revision=?,version=version+1,updated=? WHERE id=?", (decision, note, revision, stamp(), item["id"]))
            self.event(db, user, item["id"], decision, note)
            if decision == "accepted" and item["kind"] == "new":
                record = json.loads(item["data"])
                summary = record.get("summary") or record.get("reasoning", "")
                context = "Submitted review summary (independent review pending):\n" + summary + "\n\nClaim this task to read the full review package and any uploaded source materials."
                if record.get("source_url"):
                    context += "\n\nSource: " + record["source_url"]
                db.execute("INSERT INTO tasks VALUES(?,?,?,?,?,?,?,?)", (uid("task"), record["title"], record["venue"], summary[:500], context, int(record.get("synthetic", False)), item["id"], stamp()))
            return 200, self.item_json(db, self.get_item(db, item["id"], user))
        raise Problem(404, "Action not found.")

    @staticmethod
    def password_recovery_account(db,email):
        alias=resolve_alias(db,email) if alias_claimed(db,email) else None
        if alias_claimed(db,email) and not alias:return None
        rows=db.execute('''
            SELECT u.*,v.email AS recovery_email,'email' AS recovery_source,'' AS recovery_subject
              FROM users u JOIN verified_emails v ON v.user_id=u.id
             WHERE v.email=? AND u.login=v.email
               AND NOT EXISTS(SELECT 1 FROM account_merges m WHERE m.retired_user_id=u.id)
            UNION ALL
            SELECT u.*,g.email AS recovery_email,'google' AS recovery_source,g.subject AS recovery_subject
              FROM users u JOIN google_identities g ON g.user_id=u.id
             WHERE g.email=? AND u.role IN ('admin','maintainer')
               AND NOT EXISTS(SELECT 1 FROM account_merges m WHERE m.retired_user_id=u.id)
            ''',(email,email)).fetchall()
        if alias:
            rows+=db.execute("SELECT u.*,v.email AS recovery_email,'email' AS recovery_source,'' AS recovery_subject FROM users u JOIN verified_emails v ON v.user_id=u.id WHERE u.id=? AND v.email=?",(alias['id'],email)).fetchall()
        if not rows or len({row['id'] for row in rows})!=1:return None
        return next((row for row in rows if row['recovery_source']=='email'),rows[0])

    def password_reset_binding(self,account,db):
        proof=[account['id'],account['password'],account['recovery_source'],account['recovery_email'],account['recovery_subject']]
        if account['recovery_source']=='google':proof.append(account['role'])
        proof+=alias_binding(db,account['recovery_email'])
        return hmac.new(self.server.mailer.key,('password-reset-binding:'+dump(proof)).encode(),hashlib.sha256).hexdigest()

    @staticmethod
    def login_failure(state):
        body={'login_locked':state['locked'],'login_attempts_remaining':state['remaining'],
              'retry_after':state['retry_after'],'password_reset_url':'/?view=forgot-password#contributor-access'}
        if state['locked']:
            body['error']='Too many incorrect sign-in attempts from this connection. Sign-in is locked for '+str(state['retry_after'])+' seconds. You can still browse or reset your password.'
            return 429,body,'application/json; charset=utf-8',{'Retry-After':str(state['retry_after'])}
        body['error']='The account or password is incorrect.'
        if state['remaining']<=5:
            body['error']+=' '+str(state['remaining'])+' attempts remain before this connection is locked for 60 minutes.'
        return 401,body

    def password_reset_request(self):
        response={'message':'If an eligible account exists, a password-reset link will be sent to its verified email. Check your inbox and spam folder.'}
        email=normalize_email(self.body().get('email',''))
        try:self.rate_limit('password-reset-request',40)
        except Problem:
            self.send(202,response);return
        if not email or not self.server.mailer.enabled:
            self.send(202,response);return
        reserved=False
        try:
            with connect(self.server.db_path) as db:
                db.execute('BEGIN IMMEDIATE')
                account=self.password_recovery_account(db,email)
                now=time.time()
                if account:
                    family=recovery_user_ids(db,account['id']);marks=','.join('?' for _ in family)
                    recent=db.execute('SELECT COUNT(*) FROM password_reset_tokens WHERE user_id IN ('+marks+') AND created>?',(*family,now-86400)).fetchone()[0]
                    cooldown=db.execute('SELECT 1 FROM password_reset_tokens WHERE user_id IN ('+marks+') AND created>?',(*family,now-60)).fetchone()
                    if recent<5 and not cooldown and self.server.reset_mail_slots.acquire(blocking=False):
                        reserved=True
                        if self.server.abuse.reserve_mail(db,account['recovery_email'],now):
                            token=secrets.token_urlsafe(32)
                            digest=hmac.new(self.server.mailer.key,('password-reset-token:'+self.request_origin+'\0'+token).encode(),hashlib.sha256).hexdigest()
                            db.execute('UPDATE password_reset_tokens SET used=1 WHERE user_id=?',(account['id'],))
                            db.execute('DELETE FROM password_reset_tokens WHERE created<?',(now-2592000,))
                            db.execute('INSERT INTO password_reset_tokens VALUES(?,?,?,?,?,?,0,0)',(digest,account['id'],account['recovery_email'],self.password_reset_binding(account,db),now,now+900))
                        else:
                            self.server.reset_mail_slots.release();reserved=False
            if reserved:
                url=self.request_origin+'/?view=reset-password#token='+token
                worker=threading.Thread(target=self.server.deliver_password_reset,args=(account['recovery_email'],url,digest,account['id']),daemon=True)
                try:worker.start();reserved=False
                except RuntimeError:pass
        finally:
            if reserved:self.server.reset_mail_slots.release()
        self.send(202,response)

    def password_reset_complete(self):
        invalid='This password-reset link is invalid, expired or has already been used. Request a new link.'
        data=self.body();token=data.get('token','')
        self.rate_limit('password-reset-complete',40)
        require(isinstance(token,str) and re.fullmatch(r'[A-Za-z0-9_-]{43}',token),invalid)
        replacement=password_hash(data.get('newpassword',''))
        digest=hmac.new(self.server.mailer.key,('password-reset-token:'+self.request_origin+'\0'+token).encode(),hashlib.sha256).hexdigest()
        with connect(self.server.db_path) as db:
            db.execute('BEGIN IMMEDIATE')
            pending=db.execute('SELECT * FROM password_reset_tokens WHERE token_hash=? AND used=0 AND sent=1 AND expires>?',(digest,time.time())).fetchone()
            require(pending and hmac.compare_digest(pending['token_hash'],digest),invalid)
            account=self.password_recovery_account(db,pending['email'])
            require(account and account['id']==pending['user_id'] and hmac.compare_digest(pending['binding_hash'],self.password_reset_binding(account,db)),invalid)
            db.execute('UPDATE users SET password=?,force_change=0 WHERE id=?',(replacement,account['id']))
            db.execute('UPDATE password_reset_tokens SET used=1 WHERE user_id=?',(account['id'],))
            db.execute('DELETE FROM oauth_states WHERE actor=? OR session_token IN (SELECT token FROM sessions WHERE user_id=?)',(account['id'],account['id']))
            db.execute('DELETE FROM sessions WHERE user_id=?',(account['id'],))
            db.execute('DELETE FROM email_challenges WHERE email IN (?,?)',(pending['email'],account['login']))
            self.event(db,account,account['id'],'password_reset_completed')
            self.server.login_guard.clear(db,self.login_source)
        self.send(200,{'reset':True,'message':'Your password has been reset. Sign in with your new password.'},extra={'Set-Cookie':'elvia_session=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0'})

    def email_code_request(self):
        email=normalize_email(self.body().get("email",""))
        require(eligible_email(email,self.server.mailer.domains),"Use an academic address (.edu, .edu.country or .ac.country), or an approved research-institution domain. Personal email accounts cannot register.")
        require(self.server.mailer.enabled,"Registration is waiting for the maintainer to configure the domain email service. No verification email was sent.",503)
        self.rate_limit("email-code",40)
        cid=uid("ec");code=f"{secrets.randbelow(1000000):06d}";now=time.time()
        digest=hmac.new(self.server.mailer.key,(cid+email+code).encode(),hashlib.sha256).hexdigest()
        require(self.server.reset_mail_slots.acquire(blocking=False),"Email delivery is busy. Try again shortly.",429)
        try:
            with connect(self.server.db_path) as db:
                db.execute("BEGIN IMMEDIATE")
                require(not login_claimed(db,email),"An account already exists. Sign in instead.",409)
                require(not db.execute("SELECT 1 FROM email_challenges WHERE email=? AND created>?",(email,now-60)).fetchone(),"Wait 60 seconds before requesting another code.",429)
                require(db.execute("SELECT COUNT(*) FROM email_challenges WHERE email=? AND created>?",(email,now-86400)).fetchone()[0]<10,"The daily email-code limit has been reached. Try again tomorrow.",429)
                require(self.server.abuse.reserve_mail(db,email,now),"The email allowance has been reached. Wait before trying again.",429)
                db.execute("DELETE FROM email_challenges WHERE expires<=?",(now,))
                db.execute("UPDATE email_challenges SET sent=0 WHERE email=?",(email,))
                db.execute("INSERT INTO email_challenges VALUES(?,?,?,?,?,?,?)",(cid,email,digest,now,now+600,0,0))
            try:self.server.mailer.send_code(email,code)
            except MailError as exc:raise Problem(503,str(exc)) from None
            with connect(self.server.db_path) as db:db.execute("UPDATE email_challenges SET sent=1 WHERE id=?",(cid,))
        finally:self.server.reset_mail_slots.release()
        self.send(200,{"sent":True,"expires_in":600,"resend_after":60})

    def prepare_email_registration(self):
        data=self.body();self.cached_body=data
        email=normalize_email(data.get("email",""));code=str(data.get("email_code","")).strip()
        require(eligible_email(email,self.server.mailer.domains),"Use an academic email or an approved research-institution domain.")
        require(re.fullmatch(r"[0-9]{6}",code),"Enter the six-digit email verification code.")
        valid=False
        with connect(self.server.db_path) as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT * FROM email_challenges WHERE email=? AND sent=1 ORDER BY created DESC LIMIT 1",(email,)).fetchone()
            if row and row["expires"]>time.time() and row["attempts"]<5:
                digest=hmac.new(self.server.mailer.key,(row["id"]+email+code).encode(),hashlib.sha256).hexdigest()
                valid=hmac.compare_digest(row["digest"],digest)
                if valid:self.verified_challenge=row["id"]
                else:db.execute("UPDATE email_challenges SET attempts=attempts+1 WHERE id=?",(row["id"],))
        require(valid,"The code is incorrect, expired or has reached five attempts. Request a new code if needed.")

    def google_callback(self):
        query=parse_qs(urlsplit(self.path).query)
        try:
            with connect(self.server.db_path) as db:
                db.execute("BEGIN IMMEDIATE")
                state=self.server.google.consume_state(db,query,self.headers.get("Cookie",""),origin=self.request_origin)
            if query.get("error"):raise GoogleLoginError("Google sign-in was cancelled. You can retry or use email sign-in.")
            code=query.get("code",[""])[0]
            if not code or len(code)>4096:raise GoogleLoginError("The Google authorization response is incomplete. Start again.")
            # External token validation deliberately occurs outside the SQLite write lock.
            identity=self.server.google.exchange(code,state)
            with connect(self.server.db_path) as db:
                db.execute("BEGIN IMMEDIATE")
                user=self.server.google.finish(db,identity,state,uid,stamp)
                self.session(db,user)
                self.event(db,user,user["id"],"google_linked" if state["mode"]=="link" else "google_signed_in")
            destination="/contribute.html?view="+("account" if state["mode"]=="link" else "maintainer" if user["role"]=="maintainer" else "my-work")
            self.send(303,b"","text/plain",{"Location":destination,"Set-Cookie":self.cookie})
        except GoogleLoginError as exc:
            self.send(303,b"","text/plain",{"Location":"/contribute.html?view=login&maintainer=1&auth_error="+quote(str(exc))})

    def handle_request(self):
        self.cookie = None
        self.request_origin = None
        self.login_source = None
        self.remove_bootstrap_file = False
        auth_slot=False
        if hasattr(self, "cached_body"):del self.cached_body
        if hasattr(self,"cached_raw_body"):del self.cached_raw_body
        try:
            try:self.request_origin=self.server.origins.request_origin(self.headers,self.command,allow_login_context=protected_action(self.command,self.path))
            except ValueError as exc:raise Problem(403,str(exc)) from None
            path = urlsplit(self.path).path
            if path.startswith('/api/auth/') and self.command in ('POST','PUT','GET'):
                auth_slot=self.server.auth_slots.acquire(blocking=False)
                if not auth_slot and path=='/api/auth/password-reset/request':
                    self.send(202,{'message':'If an eligible account exists, a password-reset link will be sent to its verified email. Check your inbox and spam folder.'});return
                require(auth_slot,'Sign-in services are busy. Try again shortly.',429)
                data=self.body() if self.command in ('POST','PUT') else {}
                self.cached_body=data
                if protected_action(self.command,self.path):
                    try:
                        if self.request_origin==self.server.origins.private_origin:
                            self.login_source=verify_context(self.server.login_proxy_key,self.headers,self.command,self.path,self.cached_raw_body)
                        else:
                            if any(name.casefold() in HEADER_NAMES for name in self.headers.keys()):raise ValueError('Unexpected login proxy context.')
                            self.login_source=canonical_client_ip(self.client_address[0])
                    except ValueError:raise Problem(403,'The trusted sign-in connection could not be verified.') from None
                    if path=='/api/auth/login':
                        with connect(self.server.db_path) as db:
                            db.execute('BEGIN IMMEDIATE')
                            locked=self.server.login_guard.state(db,self.login_source,time.time())
                        if locked['locked']:
                            status,value,*rest=self.login_failure(locked)
                            self.send(status,value,rest[0],rest[1]);return
                raw=(data.get('login','') if path=='/api/auth/login' else
                     data.get('email','') if path in ('/api/auth/register','/api/auth/email-code','/api/auth/password-reset/request') else '')
                identity=raw.strip().casefold()[:254] if isinstance(raw,str) else ''
                category=('mail-request' if path in ('/api/auth/email-code','/api/auth/password-reset/request') else
                          'google' if '/google/' in path else path)
                # A forgotten-password attempt must never spend the same
                # account's login allowance or invalidate an existing link.
                identity=category+'\0'+(identity or 'no-identity')
                with connect(self.server.db_path) as db:
                    db.execute('BEGIN IMMEDIATE')
                    allowed=self.server.abuse.reserve_request(db,identity,time.time())
                if not allowed and path=='/api/auth/password-reset/request':
                    self.send(202,{'message':'If an eligible account exists, a password-reset link will be sent to its verified email. Check your inbox and spam folder.'});return
                require(allowed,'Too many sign-in requests. Try again later.',429)
            if path=='/api/auth/password-reset/request' and self.command=='POST':
                self.password_reset_request();return
            if path=='/api/auth/password-reset/complete' and self.command=='POST':
                self.password_reset_complete();return
            if path=="/api/auth/email-code" and self.command=="POST":
                self.email_code_request();return
            if path=="/api/auth/register" and self.command=="POST":self.prepare_email_registration()
            if path=="/api/auth/google/callback" and self.command=="GET":
                self.google_callback();return
            if not path.startswith("/api/"):
                require(self.command in ("GET", "HEAD"), "Method not allowed.", 405)
                # Reserve the whole decoded mount before the general static
                # handler, so aliases cannot bypass the Atlas manifest.
                decoded = unquote(path)
                if decoded == "/atlas" or decoded.startswith("/atlas/"):
                    require(path == decoded or path.startswith("/atlas/"), "Page not found.", 404)
                    if path == "/atlas":
                        require(bool(self.server.atlas.files), "Page not found.", 404)
                        self.send(308, b"", "text/plain", {"Location": "/atlas/"})
                        return
                    require(path.startswith("/atlas/"), "Page not found.", 404)
                    result = self.server.atlas.read(path[len("/atlas/"):])
                    require(result is not None, "Page not found.", 404)
                    blob, content_type, headers = result
                    self.send(200, blob, content_type, headers)
                    return
                relative = unquote(path).lstrip("/") or "index.html"
                file = (SITE / relative).resolve()
                require(file.is_relative_to(SITE) and file.is_file() and not any(part.startswith(".") for part in Path(relative).parts), "Page not found.", 404)
                # Windows case and separator aliases must not fall through to
                # the older static handler and bypass the dedicated mount.
                require(not file.is_relative_to((SITE / "atlas").resolve()), "Page not found.", 404)
                allowed = {".html", ".css", ".js", ".svg", ".woff2", ".txt"}
                require(file.suffix in allowed, "Page not found.", 404)
                content_type = {".js": "text/javascript", ".woff2": "font/woff2"}.get(file.suffix, mimetypes.guess_type(file)[0] or "application/octet-stream")
                self.send(200, file.read_bytes(), content_type)
                return
            self.prepare_admission(path)
            with connect(self.server.db_path) as db:
                if self.command not in ("GET", "HEAD"):
                    db.execute("BEGIN IMMEDIATE")
                user, session = self.identify(db)
                result = self.dispatch(db, path, user, session)
            if self.remove_bootstrap_file:
                (self.server.data_dir / "MAINTAINER-LOGIN.txt").unlink(missing_ok=True)
            status, value, *rest = result
            headers = rest[1] if len(rest) > 1 else {}
            if self.cookie:
                headers["Set-Cookie"] = self.cookie
            self.send(status, value, rest[0] if rest else "application/json; charset=utf-8", headers)
        except Problem as exc:
            self.send(exc.status, {"error": exc.message})
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            pass
        except sqlite3.IntegrityError as exc:
            if str(exc) == 'ELVIA_STORAGE_QUOTA':
                self.send(507, {"error": "Attachment storage is full. Your earlier saved work is intact. Please contact the maintainer."})
            else:
                self.send(409, {"error": "This item changed in another session. Reload and try again."})
        except Exception as exc:
            # Error type is useful for diagnosis; no request content is logged.
            print(f"Local service error: {type(exc).__name__}", flush=True)
            self.send(500, {"error": "The local service could not save this change. Your earlier saved work is intact."})
        finally:
            if auth_slot:self.server.auth_slots.release()

    do_GET = handle_request
    do_HEAD = handle_request
    do_POST = handle_request
    do_PUT = handle_request


def make_server(data_dir, port=0, bootstrap_password=None, *, private_origin=None,login_proxy_key_file=None):
    return LocalServer(data_dir, port, bootstrap_password,private_origin=private_origin,login_proxy_key_file=login_proxy_key_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8797)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "local-data")
    parser.add_argument("--private-origin", help="Enable the explicitly authorized private HTTPS origin alongside loopback.")
    parser.add_argument('--login-proxy-key-file',type=Path,help='Protected release-local login proxy key; never a command-line secret.')
    args = parser.parse_args()
    try:
        validate_private_origin(args.private_origin)
        if args.private_origin and args.login_proxy_key_file is None:raise ValueError('Private sign-in requires the protected login proxy key file.')
        if args.login_proxy_key_file is not None:load_proxy_key(args.login_proxy_key_file,expected_root=ROOT.parent)
    except ValueError as exc:parser.error(str(exc))
    service = make_server(args.data_dir, args.port,private_origin=args.private_origin,login_proxy_key_file=args.login_proxy_key_file)
    print(f"ELVIA independent local service: http://127.0.0.1:{service.server_port}/", flush=True)
    try:
        service.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        service.server_close()


if __name__ == "__main__":
    main()
