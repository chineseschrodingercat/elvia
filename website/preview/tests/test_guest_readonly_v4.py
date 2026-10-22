"""Guest writes are denied by real HTTP handlers against synthetic state only.

Public authentication bootstrap is deliberately separate: requesting a code,
verified registration, sign-in and OAuth state creation may change auth state.
These tests never use operational data, provider credentials or real delivery.
"""
import hashlib
import json
from pathlib import Path
import sys
import unittest
import urllib.error
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))
import test_local_service as baseline
from local_service import connect, password_hash, stamp


class RawClient(baseline.Client):
    """No automatic code request or registration fields injected by QA helpers."""

    def call(self, method, path, data=None, headers=None):
        request_headers = {"Origin": self.base, "X-CSRF-Token": self.csrf}
        if isinstance(data, dict):
            data = json.dumps(data).encode()
            request_headers["Content-Type"] = "application/json"
        request_headers.update(headers or {})
        request = urllib.request.Request(
            self.base + path, data=data, method=method, headers=request_headers
        )
        try:
            response = self.opener.open(request)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            body = response.read()
            result = (
                json.loads(body)
                if "json" in response.headers.get("Content-Type", "")
                else body
            )
            if isinstance(result, dict) and "csrf" in result:
                self.csrf = result["csrf"]
            return response.status, result


class GuestReadOnlyV4(unittest.TestCase):
    setUp = baseline.ServiceContract.setUp
    tearDown = baseline.ServiceContract.tearDown
    reviewer = baseline.ServiceContract.reviewer
    create = baseline.ServiceContract.create
    save = baseline.ServiceContract.save
    upload = baseline.ServiceContract.upload

    def snapshot(self):
        """Business/auth state and configuration, excluding auth-attempt row data.

        Denied authentication attempts intentionally persist their bounded HMAC
        request accounting. Keep its DDL and every other table (including mail
        reservations) in this snapshot; separately exercise accounting below.
        """
        with connect(self.server.db_path) as db:
            database = "\n".join(line for line in db.iterdump()
                                 if not line.startswith('INSERT INTO "abuse_requests" '))
        ancillary = {}
        for file in sorted(Path(self.tmp.name).rglob("*")):
            if file.is_file() and file.name not in {
                "elvia.sqlite3", "elvia.sqlite3-wal", "elvia.sqlite3-shm"
            }:
                ancillary[file.relative_to(self.tmp.name).as_posix()] = hashlib.sha256(
                    file.read_bytes()
                ).hexdigest()
        return database, ancillary

    def request_accounting(self):
        with connect(self.server.db_path) as db:
            return [tuple(row) for row in db.execute('SELECT rowid,identity_key,created FROM abuse_requests ORDER BY rowid')]

    def test_denied_auth_attempts_increment_only_bounded_request_accounting(self):
        guest=RawClient(self.base)
        before=self.snapshot();accounting=self.request_accounting()
        for _ in range(12):
            status,response=guest.call('POST','/api/auth/google/start',{'mode':'link','password':'irrelevant'})
            self.assertEqual(status,401,response)
            self.assertEqual(self.snapshot(),before)
        after=self.request_accounting()
        self.assertEqual(len(after),len(accounting)+12)
        for _,identity,_ in after[len(accounting):]:
            self.assertRegex(identity,r'^[0-9a-f]{64}$')
        # The thirteenth attempt is a separate abuse-limit assertion; the
        # twelve preceding 401s prove authorization was reached, not masked.
        self.assertEqual(guest.call('POST','/api/auth/google/start',{'mode':'link','password':'irrelevant'})[0],429)
        self.assertEqual(self.request_accounting(),after)
        self.assertEqual(self.snapshot(),before)
        self.assertEqual(guest.call('GET','/api/session')[0],200)
        self.assertEqual(self.request_accounting(),after)

    def mutation_requests(self, contribution, account):
        cid = contribution["id"]
        version = contribution["version"]
        return [
            ("POST", "/api/admin/email-settings", {"host": "smtp.invalid.example"}),
            ("POST", "/api/auth/google/start", {"mode": "link", "password": "irrelevant"}),
            ("POST", "/api/admin/roles", {"email": "outsider@example.edu", "role": "maintainer"}),
            ("POST", f"/api/admin/accounts/{account}/status", {"status": "suspended", "note": "Synthetic probe only."}),
            ("POST", f"/api/contributions/{cid}/check", {"version": version, "refresh": True}),
            ("POST", f"/api/admin/contributions/{cid}/check", {"version": version, "refresh": True}),
            ("POST", f"/api/contributions/{cid}/admission-resolution", {"version": version}),
            ("POST", f"/api/admin/contributions/{cid}/admission-resolution", {"version": version}),
            ("POST", "/api/auth/logout", {}),
            ("POST", "/api/auth/password", {"current": "irrelevant", "password": "Synthetic-new-password-48"}),
            ("POST", f"/api/admin/contributions/{cid}/revisions", {"version": version, "mode": "final", "data": {}}),
            ("POST", f"/api/finals/{cid}/amendments", {"final_revision": "mr_synthetic"}),
            ("POST", "/api/admin/amendments/am_synthetic", {"decision": "declined", "note": "Synthetic probe."}),
            ("POST", "/api/application", {"position": "Researcher", "institution": "Synthetic University", "expertise": "Synthetic HTTP boundary test"}),
            ("POST", f"/api/admin/applications/{account}", {"decision": "approved"}),
            ("POST", "/api/contributions", {"kind": "new", "role": "maintainer"}),
            ("POST", "/api/contributions", {"kind": "review", "task_id": "DEMO-002", "conflict_clear": True}),
            ("POST", f"/api/contributions/{cid}/package", {"version": version}),
            ("POST", f"/api/contributions/{cid}/source", {"version": version}),
            ("PUT", f"/api/contributions/{cid}", {"version": version, "data": {"title": "Unauthorized overwrite"}}),
            ("POST", f"/api/contributions/{cid}/release", {"version": version}),
            ("POST", f"/api/contributions/{cid}/submit", {"version": version, "attest": True}),
            ("POST", f"/api/admin/contributions/{cid}/decision", {"version": version, "decision": "accepted", "note": "Synthetic unauthorized probe."}),
        ]

    def fixture_work(self):
        reviewer, account = self.reviewer()
        item = self.save(reviewer, self.create(reviewer, "new"))
        _, item = self.upload(reviewer, item)
        return reviewer, account, item

    def test_guest_session_has_no_identity_or_authenticated_csrf(self):
        guest = RawClient(self.base)
        status, result = guest.call("GET", "/api/session")
        self.assertEqual(status, 200)
        self.assertIsNone(result["user"])
        self.assertEqual(result["csrf"], "")
        before = self.snapshot()
        for path in ("/api/health", "/api/tasks", "/api/admission-policy", "/api/contributors"):
            self.assertEqual(guest.call("GET", path)[0], 200, path)
        self.assertEqual(self.snapshot(), before)

    def test_all_business_writes_deny_guest_spoofed_identity_and_stale_sessions(self):
        reviewer, account, item = self.fixture_work()
        raw_expired = "synthetic-expired-session-not-an-operational-token"
        with connect(self.server.db_path) as db:
            db.execute(
                "INSERT INTO sessions VALUES(?,?,?,?)",
                (hashlib.sha256(raw_expired.encode()).hexdigest(), account, "expired-csrf", 1),
            )
        guest = RawClient(self.base)
        guest_csrf = guest.call("GET", "/api/session")[1]["csrf"]
        header_sets = {
            "guest_api_csrf": {"X-CSRF-Token": guest_csrf},
            "spoofed_headers": {"X-User-Id": account, "X-User-Role": "maintainer", "Authorization": "Bearer maintainer", "X-CSRF-Token": guest_csrf},
            "forged_cookie_borrowed_csrf": {"Cookie": f"elvia_session={account}; role=maintainer; user={account}", "X-CSRF-Token": reviewer.csrf},
            "expired_real_format_session": {"Cookie": "elvia_session=" + raw_expired, "X-CSRF-Token": "expired-csrf"},
        }
        before = self.snapshot()
        for identity, headers in header_sets.items():
            for method, path, body in self.mutation_requests(item, account):
                with self.subTest(identity=identity, method=method, path=path):
                    request_headers = headers
                    if path.endswith(("/package", "/source")):
                        body = baseline.package()
                        request_headers = {**headers, "Content-Type": "application/zip", "X-Version": str(item["version"]), "X-Filename": "synthetic.zip"}
                    status, response = guest.call(method, path + "?role=maintainer&user_id=" + account, body, request_headers)
                    self.assertEqual(status, 401, response)
                    self.assertEqual(self.snapshot(), before)

    def test_private_reads_are_not_unlocked_by_guest_role_headers(self):
        _, account, item = self.fixture_work()
        guest = RawClient(self.base)
        paths = (
            "/api/me", "/api/admin", "/api/admin/accounts", "/api/admin/email-settings",
            "/api/finals", f"/api/contributions/{item['id']}",
            f"/api/packages/{item['package']['id']}",
        )
        before = self.snapshot()
        for path in paths:
            with self.subTest(path=path):
                status, response = guest.call("GET", path, headers={"X-User-Role": "maintainer", "X-User-Id": account})
                self.assertEqual(status, 401, response)
                self.assertEqual(self.snapshot(), before)

    def test_missing_or_foreign_csrf_denies_valid_signed_in_business_writes(self):
        reviewer, account, item = self.fixture_work()
        before = self.snapshot()
        for csrf in ("", "synthetic-forged-token", self.admin.csrf):
            for method, path, body in self.mutation_requests(item, account):
                if path == "/api/auth/google/start":
                    # Contributor Google linking is rejected by role before CSRF.
                    continue
                with self.subTest(csrf_kind=bool(csrf), method=method, path=path):
                    status, response = reviewer.call(method, path, body, {"X-CSRF-Token": csrf})
                    self.assertEqual(status, 403, response)
                    self.assertEqual(self.snapshot(), before)

    def test_unsupported_methods_and_static_writes_cannot_mutate_state(self):
        _, account, item = self.fixture_work()
        guest = RawClient(self.base)
        before = self.snapshot()
        for method in ("PATCH", "DELETE"):
            for _, path, body in self.mutation_requests(item, account):
                with self.subTest(method=method, path=path):
                    self.assertEqual(guest.call(method, path, body)[0], 501)
                    self.assertEqual(self.snapshot(), before)
        for method in ("POST", "PUT"):
            for path in ("/", "/contribute.html", "/atlas/", "/atlas/data.json"):
                with self.subTest(method=method, path=path):
                    self.assertEqual(guest.call(method, path, {"title": "Unauthorized overwrite"})[0], 405)
                    self.assertEqual(self.snapshot(), before)

    def test_registration_requires_a_code_and_cannot_choose_a_role(self):
        guest = RawClient(self.base)
        email = "gateway@example.edu"
        data = {"email": email, "name": "Synthetic Gateway User", "password": "Synthetic-gateway-password-48", "accept_terms": True, "role": "maintainer"}
        before = self.snapshot()
        for supplied in (data, {**data, "email_code": "123456"}):
            status, response = guest.call("POST", "/api/auth/register", supplied)
            self.assertEqual(status, 400, response)
            self.assertEqual(self.snapshot(), before)
        self.assertEqual(guest.call("POST", "/api/auth/email-code", {"email": email})[0], 200)
        with connect(self.server.db_path) as db:
            self.assertIsNone(db.execute("SELECT id FROM users WHERE login=?", (email,)).fetchone())
            self.assertEqual(db.execute("SELECT count(*) FROM contributions").fetchone()[0], 0)
        code = baseline.TEST_MAILBOX[email]
        status, result = guest.call("POST", "/api/auth/register", {**data, "email_code": code})
        self.assertEqual(status, 201, result)
        self.assertEqual(result["user"]["role"], "reviewer")
        with connect(self.server.db_path) as db:
            self.assertIsNotNone(db.execute("SELECT 1 FROM verified_emails WHERE user_id=? AND email=?", (result["user"]["id"], email)).fetchone())
        self.assertEqual(guest.call("POST", "/api/contributions", {"kind": "new"})[0], 201)

    def test_legacy_unverified_reviewer_cannot_enter_workflows(self):
        # Defensive fixture: the public registration handler cannot create this.
        # A legacy/imported account must not bypass the verification requirement.
        account = "u_unverified_synthetic"
        with connect(self.server.db_path) as db:
            db.execute("INSERT INTO users VALUES(?,?,?,?,?,?,?)", (account, "unverified@example.edu", "Unverified synthetic account", "reviewer", password_hash("Synthetic-unverified-password-48"), 0, stamp()))
        client = RawClient(self.base)
        status, result = client.call("POST", "/api/auth/login", {"login": "unverified@example.edu", "password": "Synthetic-unverified-password-48"})
        self.assertEqual(status, 200, result)
        before = self.snapshot()
        for path, body in (
            ("/api/contributions", {"kind": "new"}),
            ("/api/application", {"position": "Researcher", "institution": "Synthetic University", "expertise": "Synthetic test only"}),
            ("/api/contributions", {"kind": "review", "task_id": "DEMO-001", "conflict_clear": True}),
        ):
            with self.subTest(path=path, body=body):
                status, response = client.call("POST", path, body)
                self.assertEqual(status, 403, response)
                self.assertEqual(self.snapshot(), before)

    def test_verification_revocation_blocks_existing_work_and_admission_but_preserves_recovery(self):
        reviewer, account, item = self.fixture_work()
        with connect(self.server.db_path) as db:
            db.execute("DELETE FROM verified_emails WHERE user_id=?", (account,))
        lookups = []
        self.server.admission.check = lambda record: lookups.append(record)
        before = self.snapshot()
        for method, path, body in self.mutation_requests(item, account):
            if path in ("/api/auth/logout", "/api/auth/password"):
                continue
            with self.subTest(method=method, path=path):
                status, response = reviewer.call(method, path, body)
                self.assertEqual(status, 403, response)
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(lookups, [])
        # Read-only access to existing own work and public task browsing survives.
        for path in ("/api/tasks", "/api/me", f"/api/contributions/{item['id']}"):
            self.assertEqual(reviewer.call("GET", path)[0], 200, path)
        self.assertEqual(self.snapshot(), before)
        status, response = reviewer.call("POST", "/api/auth/password", {"current": "Reviewer-test-password-42", "password": "Synthetic-recovery-password-48"})
        self.assertEqual(status, 200, response)
        status, response = reviewer.call("POST", "/api/auth/logout", {})
        self.assertEqual(status, 200, response)
        self.assertIsNone(reviewer.call("GET", "/api/session")[1]["user"])


if __name__ == "__main__":
    unittest.main()
