"""HTTP integration tests use isolated databases and independent cookie jars."""
import sys
import base64
import unittest
import contextlib
import http.cookiejar
import io
import json
import tempfile
import threading
import urllib.error
import urllib.request
import zipfile
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))
from local_service import make_server, connect, stamp  # noqa: E402
from admission import CATALOG
TEST_MAILBOX = {}


class Client:
    def __init__(self, base):
        self.base = base
        self.csrf = ""
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def call(self, method, path, data=None, headers=None):
        if method=="POST" and path=="/api/auth/register" and isinstance(data,dict):
            data={**data}
            data.setdefault("accept_terms",True)
            if "email_code" not in data:
                self.call("POST","/api/auth/email-code",{"email":data["email"]})
                data["email_code"]=TEST_MAILBOX.get(data["email"].strip().lower(),"000000")
        h = {"Origin": self.base, "X-CSRF-Token": self.csrf}
        if isinstance(data, dict):
            data = json.dumps(data).encode()
            h["Content-Type"] = "application/json"
        if headers:
            h.update(headers)
        request = urllib.request.Request(self.base + path, data=data, method=method, headers=h)
        try:
            # Hosted Windows workers can pause during isolated database and
            # password-hash work. This bounds fixture I/O, not service latency.
            result = self.opener.open(request, timeout=30)
        except urllib.error.HTTPError as exc:
            result = exc
        with result:
            body = result.read()
            content = json.loads(body) if "json" in result.headers.get("Content-Type", "") else body
            if isinstance(content, dict) and "csrf" in content:
                self.csrf = content["csrf"]
            return result.status, content


def package(name="report.md", body=b"Synthetic test evidence only."):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, body)
    return stream.getvalue()


class ServiceContract(unittest.TestCase):
    def test_admin_application_shows_verified_email_state(self):
        _,user_id=self.reviewer(approve=False)
        status,result=self.admin.call('GET','/api/admin')
        self.assertEqual(status,200)
        app=next(x for x in result['applications'] if x['user_id']==user_id)
        self.assertTrue(app['email_verified'])

    def test_scope_policy_change_invalidates_cached_checks(self):
        item=self.save(self.admin,self.create(self.admin,kind="new"),field="mathematics",venue="Annals of Mathematics")
        status,item=self.admin.call("POST",f"/api/contributions/{item['id']}/check",{"version":item['version']})
        self.assertEqual(status,200,item)
        self.assertFalse(item['admission']['stale'])
        with patch.dict(CATALOG,{'version':'synthetic-next-policy'}):
            status,result=self.admin.call("GET",f"/api/contributions/{item['id']}")
            self.assertIsNone(result['admission'])
            status,result=self.admin.call("POST",f"/api/contributions/{item['id']}/check",{"version":item['version']})
            self.assertEqual(status,200,result)
            self.assertEqual(result['admission']['policy_version'],'synthetic-next-policy')

    def test_top_list_allows_submission_and_manual_identity_resolution_without_jif(self):
        item=self.save(self.admin,self.create(self.admin,kind="new"),field="chemistry",venue="Chemical Science")
        status,result=self.admin.call("POST",f"/api/admin/contributions/{item['id']}/admission-resolution",{
            "version":item["version"],"identity_confirmed":True,"evidence_url":"https://doi.org/10.1234/synthetic",
            "note":"Synthetic identity confirmation; no scientific review has occurred."})
        self.assertEqual(status,200,result)
        self.assertEqual(result['admission']['eligibility_basis'],['top_list'])
        reviewer,_=self.reviewer(approve=False)
        item=self.save(reviewer,self.create(reviewer,kind="new"),field="biological_science",venue="Plant Phenomics")
        _,item=self.upload(reviewer,item)
        status,result=reviewer.call("POST",f"/api/contributions/{item['id']}/submit",{"version":item['version'],"attest":True})
        self.assertEqual(status,200,result)
        self.assertEqual(result['admission']['eligibility_basis'],['top_list'])

    def test_manual_eligibility_resolution_requires_saved_paper_identity(self):
        item=self.create(self.admin,kind="new")
        status,result=self.admin.call("POST",f"/api/admin/contributions/{item['id']}/admission-resolution",{
            "version":item["version"],"identity_confirmed":True,"evidence_url":"https://doi.org/10.1234/synthetic",
            "note":"Synthetic verification attempt without saved paper details."})
        self.assertEqual(status,400,result)
        self.assertIn("required",result["error"].lower())

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.server = make_server(Path(self.tmp.name), bootstrap_password="Initial-test-password-42")
        TEST_MAILBOX.clear()
        self.server.mailer.config={"host":"smtp.example.org","sender":"noreply@example.org","username":"test","password":"synthetic-only","security":"ssl","port":465,"research_domains":["example.org"]}
        self.server.mailer.send_code=lambda email,code:TEST_MAILBOX.update({email:code})
        # All source metadata in integration tests is synthetic; no live network.
        self.server.admission.check = lambda record: self.server.admission.evaluate(record, {
            "title":record.get("title", ""), "venue":record.get("venue", ""), "issns":[],
            "type":"proceedings-article" if record.get("field") == "computer_science" else "journal-article",
            "paper_type":"full", "bound_to_url":True, "identity_source":"https://example.org/synthetic-metadata"}, None)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"
        self.admin = Client(self.base)
        self.assertEqual(self.admin.call("POST", "/api/auth/login", {"login": "minhao", "password": "Initial-test-password-42"})[0], 200)
        self.assertEqual(self.admin.call("POST", "/api/auth/password", {"current": "Initial-test-password-42", "password": "Changed-test-password-42"})[0], 200)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        # Responses can precede request/SMTP cleanup. Drain fixture workers
        # before removing SQLite files, including after a failed assertion.
        with contextlib.ExitStack() as held:
            for slots, count in ((self.server.auth_slots, 4), (self.server.reset_mail_slots, 2)):
                for _ in range(count):
                    self.assertTrue(slots.acquire(timeout=30))
                    held.callback(slots.release)
            self.tmp.cleanup()

    def reviewer(self, number=1, approve=True):
        client = Client(self.base)
        status, account = client.call("POST", "/api/auth/register", {"email": f"reviewer{number}@example.edu", "name": f"Test Reviewer {number}", "password": "Reviewer-test-password-42"})
        self.assertEqual(status, 201, account)
        status, app = client.call("POST", "/api/application", {"position": "Doctoral researcher", "institution": "Fictional Test University", "expertise": "Mathematical argument verification", "profile_url": "https://example.edu/researcher", "eligibility_note": ""})
        self.assertEqual(status, 200, app)
        if approve:
            self.assertEqual(self.admin.call("POST", f"/api/admin/applications/{account['user']['id']}", {"decision": "approved", "note": "Synthetic test approval"})[0], 200)
        return client, account["user"]["id"]

    def create(self, client, kind="review", task="DEMO-001"):
        status, item = client.call("POST", "/api/contributions", {"kind": kind, "task_id": task, "conflict_clear": True})
        self.assertEqual(status, 201, item)
        if kind == "new":
            # Historical ZIP drafts must remain editable after the migration.
            # Current browser intake is exercised in test_browser_reports.py.
            item["data"].pop("editor", None)
            item["data"].pop("report", None)
            with connect(self.server.db_path) as db:
                db.execute("UPDATE contributions SET data=? WHERE id=?", (json.dumps(item["data"]), item["id"]))
        return item

    def save(self, client, item, **overrides):
        data = {"title": "Synthetic test contribution", "venue": "NeurIPS", "year": "2025", "source_url": "https://example.org/paper/" + item["id"], "source_version": "Published conference version", "location": "Theorem 2, page 4", "scope": "Check one geometric error bound", "assessment": "supported", "reasoning": "The geometric recurrence retains a nonzero limiting term. This supports the scoped original argument.", "verification": "Worked through the recurrence by hand and checked the limiting expression.", "limits": "Only this recurrence was examined.", "ai_used": "no", "ai_model": "", "ai_details": "", "credit": "named", "roles": ["Verification"], "conflict_clear": True, "synthetic": True}
        data.update(overrides)
        data.setdefault("field", "computer_science")
        if "summary" not in overrides:
            data["summary"] = data["reasoning"]
        if "source_access" not in overrides:
            data["source_access"] = "public"
        status, item = client.call("PUT", f"/api/contributions/{item['id']}", {"version": item["version"], "data": data})
        self.assertEqual(status, 200, item)
        return item

    def upload(self, client, item, content=None, filename="evidence.zip"):
        return client.call("POST", f"/api/contributions/{item['id']}/package", content or package(), {"Content-Type": "application/zip", "X-Filename": filename, "X-Version": str(item["version"])})

    def integrate_fixture(self, item):
        """Publish a synthetic matching snapshot before testing the next reviewer."""
        record = {"case_id": "legacy-fixture", "revision": 1, "source": {"title": item["data"]["title"]}, "audit": {"venue": "NeurIPS", "landing_url": item["data"]["source_url"], "outcome": "candidate_issue"}}
        class PublishedFixture:
            def read(self, path):
                if path not in ("data.json", "cases/legacy-fixture.context.json"):
                    return None
                return json.dumps({"records": [record], "case_notes": {}}).encode(), "application/json", {}
        self.server.atlas = PublishedFixture()
        code, result = self.admin.call("POST", f"/api/admin/contributions/{item['id']}/integrate", {"version": item["version"], "case_id": "legacy-fixture", "revision": 1, "integration_confirmed": True, "note": "Synthetic publication fixture includes the accepted report."})
        self.assertEqual(code, 200, result)
        return result

    def test_required_fields_are_named_and_optional_fields_do_not_block(self):
        reviewer, _ = self.reviewer()
        item = self.save(reviewer, self.create(reviewer, "new"), summary="", location="", limits="", source_version="")
        _, item = self.upload(reviewer, item)
        status, result = reviewer.call("POST", f"/api/contributions/{item['id']}/submit", {"version": item["version"], "attest": True})
        self.assertEqual(status, 400)
        self.assertIn("Review summary", result["error"])
        item = self.save(reviewer, item, location="", scope="", verification="", limits="", source_version="", year="")
        status, result = reviewer.call("POST", f"/api/contributions/{item['id']}/submit", {"version": item["version"], "attest": True})
        self.assertEqual(status, 200, result)
        self.assertEqual(result["status"], "submitted")

    def test_uploaded_source_pdf_or_zip_required_for_nonpublic_paper(self):
        reviewer, _ = self.reviewer()
        item = self.save(reviewer, self.create(reviewer, "new"), source_access="upload", source_url="", year="", location="", verification="", scope="", limits="")
        _, item = self.upload(reviewer, item)
        status, error = reviewer.call("POST", f"/api/contributions/{item['id']}/submit", {"version": item["version"], "attest": True})
        self.assertEqual(status, 400)
        self.assertIn("paper and supplementary", error["error"])
        headers = {"Content-Type": "application/octet-stream", "X-Filename": "paper.pdf", "X-Version": str(item["version"])}
        endpoint = f"/api/contributions/{item['id']}/source"
        self.assertEqual(reviewer.call("POST", endpoint, b"not a PDF", headers)[0], 400)
        pdf = b"%PDF-1.4\n% Synthetic source upload test\n%%EOF\n"
        status, item = reviewer.call("POST", endpoint, pdf, headers)
        self.assertEqual(status, 200, item)
        source = item["source_file"]
        self.assertEqual(reviewer.call("GET", "/api/source-files/"+source["id"])[1], pdf)
        other, _ = self.reviewer(2)
        self.assertEqual(other.call("GET", "/api/source-files/"+source["id"])[0], 403)
        item = self.save(reviewer, item, source_access="upload", source_url="https://example.org/paper")
        status, item = reviewer.call("POST", f"/api/contributions/{item['id']}/submit", {"version": item["version"], "attest": True})
        self.assertEqual(status, 200, item)
        self.assertEqual(item["revisions"][0]["data"]["source_file_id"], source["id"])
        _, item = self.admin.call("POST", f"/api/admin/contributions/{item['id']}/decision", {"version": item["version"], "decision": "accepted", "note": "Synthetic source test"})
        item = self.integrate_fixture(item)
        task = next(t for t in other.call("GET", "/api/tasks")[1]["tasks"] if t["source_id"] == item["id"])
        self.create(other, task=task["id"])
        self.assertEqual(other.call("GET", "/api/source-files/"+source["id"])[1], pdf)

    def test_admission_is_enforced_on_direct_submit_and_bound_to_paper(self):
        reviewer, _ = self.reviewer()
        item = self.save(reviewer, self.create(reviewer, "new"))
        _, item = self.upload(reviewer, item)
        original = self.server.admission.check
        self.server.admission.check = lambda record: self.server.admission.evaluate(record, {"title":"A completely unrelated paper", "venue":"NeurIPS", "type":"proceedings-article", "paper_type":"full", "bound_to_url":True}, None)
        status, result = reviewer.call("POST", f"/api/contributions/{item['id']}/submit", {"version":item['version'],"attest":True})
        self.assertEqual(status,400,result)
        current = reviewer.call("GET", f"/api/contributions/{item['id']}")[1]
        self.assertEqual(current['status'],'draft')
        self.assertEqual(current['admission']['status'],'blocked')
        self.server.admission.check = original
        item = self.save(reviewer, current, title="Changed synthetic title")
        self.assertIsNone(item['admission'])
        status, item = reviewer.call("POST", f"/api/contributions/{item['id']}/submit", {"version":item['version'],"attest":True})
        self.assertEqual(status,200,item)
        self.assertEqual(item['admission']['status'],'pass')
        self.assertEqual(item['revisions'][0]['data']['admission_check_id'],item['admission']['id'])

    def test_missing_metric_blocks_until_maintainer_records_valid_evidence(self):
        reviewer, _ = self.reviewer()
        item = self.save(reviewer,self.create(reviewer,"new"),field="chemistry",venue="Test Chemistry Journal")
        _, item = self.upload(reviewer,item)
        status, error = reviewer.call("POST",f"/api/contributions/{item['id']}/submit",{"version":item['version'],"attest":True})
        self.assertEqual(status,400,error)
        item=reviewer.call("GET",f"/api/contributions/{item['id']}")[1]
        self.assertEqual(item['admission']['status'],'blocked')
        decision={"version":item['version'],"decision":"accepted","note":"Synthetic acceptance"}
        self.assertEqual(self.admin.call("POST",f"/api/admin/contributions/{item['id']}/decision",decision)[0],409)
        endpoint=f"/api/admin/contributions/{item['id']}/admission-resolution"
        resolution={"version":item['version'],"identity_confirmed":True,"evidence_url":"https://pubs.acs.org/doi/10.1234/synthetic","note":"Synthetic manual source and metric verification fixture.","jif":10,"jif_year":2025,"metric_url":"https://pubs.acs.org/journal-metrics"}
        self.assertEqual(reviewer.call("POST",endpoint,resolution)[0],403)
        self.assertEqual(self.admin.call("POST",endpoint,resolution)[0],400)
        status, item=self.admin.call("POST",endpoint,{**resolution,"jif":10.1})
        self.assertEqual(status,200,item)
        self.assertTrue(item['admission']['manual'])
        status,item=reviewer.call("POST",f"/api/contributions/{item['id']}/submit",{"version":item['version'],"attest":True})
        self.assertEqual(status,200,item)
        decision['version']=item['version']
        self.assertEqual(self.admin.call("POST",f"/api/admin/contributions/{item['id']}/decision",decision)[0],200)

    def test_others_blocked_and_check_does_not_hold_database_lock(self):
        reviewer, _ = self.reviewer()
        item = self.save(reviewer,self.create(reviewer,"new"),field="others")
        _, item = self.upload(reviewer,item)
        self.assertEqual(reviewer.call("POST",f"/api/contributions/{item['id']}/submit",{"version":item['version'],"attest":True})[0],400)
        item = self.save(reviewer,item,field="computer_science")
        entered,finish=threading.Event(),threading.Event()
        original=self.server.admission.check
        def slow(record):
            entered.set();finish.wait(5);return original(record)
        self.server.admission.check=slow
        response=[]
        t=threading.Thread(target=lambda:response.append(reviewer.call("POST",f"/api/contributions/{item['id']}/check",{"version":item['version']})))
        t.start();self.assertTrue(entered.wait(3))
        try:
            # A separate writer succeeds while the network lookup is waiting.
            other=self.create(self.admin,"new")
            self.assertEqual(other['status'],'draft')
        finally:finish.set();t.join(5)
        self.assertEqual(response[0][0],200,response)

    def test_approval_owner_permissions_cross_browser_and_restart(self):
        reviewer, uid = self.reviewer(approve=False)
        self.assertEqual(reviewer.call("POST", "/api/contributions", {"kind": "review", "task_id": "DEMO-001", "conflict_clear": True})[0], 403)
        self.assertEqual(reviewer.call("GET", "/api/admin")[0], 403)
        self.admin.call("POST", f"/api/admin/applications/{uid}", {"decision": "approved", "note": "Approved test"})
        item = self.save(reviewer, self.create(reviewer))
        status, item = self.upload(reviewer, item)
        self.assertEqual(status, 200)
        second_browser = Client(self.base)
        self.assertEqual(second_browser.call("POST", "/api/auth/login", {"login": "reviewer1@example.edu", "password": "Reviewer-test-password-42"})[0], 200)
        self.assertEqual(second_browser.call("GET", f"/api/contributions/{item['id']}")[1]["data"]["scope"], "Check one geometric error bound")
        other, _ = self.reviewer(2)
        self.assertEqual(other.call("GET", f"/api/contributions/{item['id']}")[0], 403)
        self.assertEqual(other.call("GET", f"/api/packages/{item['package']['id']}")[0], 403)
        self.assertEqual(other.call("POST", "/api/contributions", {"kind": "review", "task_id": "DEMO-001", "conflict_clear": True})[0], 409)
        self.server.shutdown(); self.server.server_close(); self.thread.join()
        self.server = make_server(Path(self.tmp.name))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True); self.thread.start()
        restarted = Client(f"http://127.0.0.1:{self.server.server_port}")
        self.assertEqual(restarted.call("POST", "/api/auth/login", {"login": "reviewer1@example.edu", "password": "Reviewer-test-password-42"})[0], 200)
        self.assertEqual(restarted.call("GET", f"/api/packages/{item['package']['id']}")[1], package())

    def test_zip_only_traversal_bomb_and_size(self):
        reviewer, _ = self.reviewer()
        item = self.create(reviewer)
        for content, name in [(b"plain text", "evidence.zip"), (package(), "report.pdf"), (package("../outside.txt"), "evidence.zip"), (package("C:/outside.txt"), "evidence.zip"), (package("huge.txt", b"0" * 2_000_000), "evidence.zip")]:
            self.assertIn(self.upload(reviewer, item, content, name)[0], (400, 413))
        # The server rejects the declared size before reading the body. Sending
        # megabytes after that early rejection races Linux's socket close and
        # tests urllib's BrokenPipe handling instead of the upload boundary.
        code, _ = reviewer.call('POST', f"/api/contributions/{item['id']}/package", b'', {
            'Content-Type': 'application/zip', 'X-Filename': 'evidence.zip',
            'X-Version': str(item['version']), 'Content-Length': str(10 * 1024 * 1024 + 1),
        })
        self.assertEqual(code, 413)
        self.assertEqual(self.upload(reviewer, item)[0], 200)

    def test_submit_revision_ai_policy_and_scoped_credit(self):
        reviewer, _ = self.reviewer()
        item = self.save(reviewer, self.create(reviewer, "new"), ai_used="yes", ai_model="", ai_details="Test model disclosure")
        _, item = self.upload(reviewer, item)
        self.assertEqual(reviewer.call("POST", f"/api/contributions/{item['id']}/submit", {"version": item["version"], "attest": True})[0], 400)
        item = self.save(reviewer, item, ai_used="yes", ai_model="Astra 6 Max", ai_details="Astra 6 / Max; 2026-10-21; checked recurrence independently.")
        status, item = reviewer.call("POST", f"/api/contributions/{item['id']}/submit", {"version": item["version"], "attest": True})
        self.assertEqual(status, 200, item)
        self.assertEqual(reviewer.call("PUT", f"/api/contributions/{item['id']}", {"version": item["version"], "data": {}})[0], 409)
        status, item = self.admin.call("POST", f"/api/admin/contributions/{item['id']}/decision", {"version": item["version"], "decision": "needs_changes", "note": "Please explain the boundary condition."})
        self.assertEqual(status, 200)
        self.assertEqual(len(item["revisions"]), 1)
        item = self.save(reviewer, item)
        _, item = reviewer.call("POST", f"/api/contributions/{item['id']}/submit", {"version": item["version"], "attest": True})
        status, item = self.admin.call("POST", f"/api/admin/contributions/{item['id']}/decision", {"version": item["version"], "decision": "accepted", "note": "Accepted as a contribution; scientific conclusion remains open."})
        self.assertEqual(status, 200)
        self.assertEqual(len(item["revisions"]), 2)
        self.assertEqual(item["scientific_status"], "Independent review pending")
        self.assertEqual(reviewer.call("GET", "/api/contributors")[1]["contributors"], [])
        self.assertTrue(reviewer.call("GET", f"/api/credit/{item['id']}")[1]["synthetic"])

    def test_csrf_stale_edits_password_and_anonymous_access(self):
        reviewer, _ = self.reviewer()
        item = self.create(reviewer)
        self.assertEqual(reviewer.call("PUT", f"/api/contributions/{item['id']}", {"version": 999, "data": {}})[0], 409)
        self.assertEqual(reviewer.call("POST", "/api/auth/logout", {}, {"X-CSRF-Token": "bad"})[0], 403)
        self.assertEqual(reviewer.call("POST", "/api/auth/logout", {}, {"Origin": "https://example.net"})[0], 403)
        anon = Client(self.base)
        self.assertEqual(anon.call("GET", f"/api/contributions/{item['id']}")[0], 401)
        self.assertEqual(anon.call("GET", "/local-data/elvia.sqlite3")[0], 404)
        self.assertEqual(anon.call("GET", "/server/local_service.py")[0], 404)
        self.assertEqual(reviewer.call("POST", "/api/auth/password", {"current": "wrong", "password": "Changed-test-password-42"})[0], 400)
        self.assertEqual(reviewer.call("POST", "/api/auth/logout", {})[0], 200)
        self.assertEqual(reviewer.call("GET", f"/api/contributions/{item['id']}")[0], 401)

    def test_simultaneous_claims_are_exclusive_and_release_preserves_draft(self):
        first, _ = self.reviewer(1)
        second, _ = self.reviewer(2)
        barrier = threading.Barrier(2)
        results = []
        def claim(client):
            barrier.wait()
            results.append((client, client.call("POST", "/api/contributions", {"kind": "review", "task_id": "DEMO-002", "conflict_clear": True})))
        threads = [threading.Thread(target=claim, args=(client,)) for client in (first, second)]
        for thread in threads: thread.start()
        for thread in threads: thread.join()
        self.assertEqual(sorted(result[0] for _, result in results), [201, 409])
        winner, (_, item) = next(r for r in results if r[1][0] == 201)
        item = self.save(winner, item)
        status, released = winner.call("POST", f"/api/contributions/{item['id']}/release", {"version": item["version"]})
        self.assertEqual(status, 200)
        self.assertEqual(released["data"]["scope"], item["data"]["scope"])
        loser = second if winner is first else first
        self.assertEqual(loser.call("POST", "/api/contributions", {"kind": "review", "task_id": "DEMO-002", "conflict_clear": True})[0], 201)

    def test_new_analysis_enters_review_queue_with_private_package_and_opt_in_credit(self):
        first, first_id = self.reviewer(1)
        second, _ = self.reviewer(2)
        item = self.save(first, self.create(first, "new"), synthetic=False, venue="Not in scope")
        _, item = self.upload(first, item)
        self.assertEqual(first.call("POST", f"/api/contributions/{item['id']}/submit", {"version": item["version"], "attest": True})[0], 400)
        item = self.save(first, item, synthetic=False)
        _, item = first.call("POST", f"/api/contributions/{item['id']}/submit", {"version": item["version"], "attest": True})
        _, accepted = self.admin.call("POST", f"/api/admin/contributions/{item['id']}/decision", {"version": item["version"], "decision": "accepted", "note": "Isolated HTTP test fixture, not a real research finding."})
        tasks = first.call("GET", "/api/tasks")[1]["tasks"]
        task = next(t for t in tasks if t["source_id"] == item["id"])
        self.assertEqual(task["availability"], "Awaiting integration")
        self.assertEqual(second.call("POST", "/api/contributions", {"kind": "review", "task_id": task["id"], "conflict_clear": True})[0], 409)
        accepted = self.integrate_fixture(accepted)
        self.assertEqual(first.call("POST", "/api/contributions", {"kind": "review", "task_id": task["id"], "conflict_clear": True})[0], 403)
        self.assertEqual(second.call("GET", f"/api/packages/{item['package']['id']}")[0], 403)
        review = self.create(second, "review", task["id"])
        self.assertEqual(second.call("GET", f"/api/packages/{item['package']['id']}")[0], 200)
        anon = Client(self.base)
        people = anon.call("GET", "/api/contributors")[1]["contributors"]
        self.assertEqual(len(people), 1)
        self.assertNotIn("email", json.dumps(people).lower())
        self.assertEqual(anon.call("GET", f"/api/credit/{item['id']}")[0], 200)
        self.assertEqual(anon.call("GET", f"/api/packages/{item['package']['id']}")[0], 401)
        self.assertEqual(accepted["scientific_status"], "Independent review pending")

    def test_password_change_invalidates_other_sessions(self):
        first, _ = self.reviewer(1)
        second = Client(self.base)
        self.assertEqual(second.call("POST", "/api/auth/login", {"login": "reviewer1@example.edu", "password": "Reviewer-test-password-42"})[0], 200)
        self.assertEqual(first.call("POST", "/api/auth/password", {"current": "Reviewer-test-password-42", "password": "Updated-reviewer-password-42"})[0], 200)
        self.assertEqual(first.call("GET", "/api/me")[0], 200)
        self.assertEqual(second.call("GET", "/api/me")[0], 401)

    def test_maintainer_final_authority_and_amendment_requests(self):
        reviewer, _ = self.reviewer(1)
        other, _ = self.reviewer(2)
        item = self.save(reviewer, self.create(reviewer))
        original = item["data"].copy()
        change = {"mode": "ordinary", "version": item["version"], "data": original, "note": "An ordinary maintainer contribution."}
        endpoint = f"/api/admin/contributions/{item['id']}/revisions"
        self.assertEqual(reviewer.call("POST", endpoint, change)[0], 403)
        status, item = self.admin.call("POST", endpoint, change)
        self.assertEqual(status, 200, item)
        self.assertIsNone(item["final_revision"])
        change.update(mode="final", version=item["version"], note="Maintainer final decision on this scoped argument.")
        status, item = self.admin.call("POST", endpoint, change)
        self.assertEqual(status, 200, item)
        first_final = item["final_revision"]["id"]
        self.assertEqual(item["data"], original)
        self.assertEqual(reviewer.call("PUT", f"/api/contributions/{item['id']}", {"version": item["version"], "data": original})[0], 409)
        self.assertEqual(other.call("GET", f"/api/finals/{item['id']}")[0], 200)
        # An old request remains actionable; the retired creation API must not
        # bypass the new paper reservation (covered by BrowserReports).
        request = {"id": "am_historical_fixture"}
        owner = other.call("GET", "/api/session")[1]["user"]["id"]
        with connect(self.server.db_path) as db:
            db.execute("INSERT INTO amendments VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (request["id"], item["id"], first_final, owner, "pending", json.dumps({"reason": "The boundary case could be explained more explicitly.", "proposed": "Clarify q=0.", "ai_used": "no", "ai_model": "", "ai_details": ""}), "", "", 0, "[]", None, "", stamp(), stamp()))
        self.assertEqual(other.call("POST", f"/api/admin/amendments/{request['id']}", {"decision": "declined", "note": "Unauthorized"})[0], 403)
        self.assertEqual(self.admin.call("GET", "/api/admin")[1]["amendments"][0]["id"], request["id"])
        revised = original | {"reasoning": original["reasoning"] + " At q=0 the bound reduces to b after one step."}
        change.update(version=item["version"], data=revised, amendment_id=request["id"], note="Adopted the boundary-case clarification as a new final version.")
        status, item = self.admin.call("POST", endpoint, change)
        self.assertEqual(status, 200, item)
        self.assertNotEqual(item["final_revision"]["id"], first_final)
        self.assertEqual(len(item["maintainer_revisions"]), 3)
        self.assertEqual(other.call("GET", "/api/me")[1]["amendments"][0]["status"], "accepted")
        self.assertEqual(reviewer.call("GET", f"/api/contributions/{item['id']}")[1]["data"], original)
        ordinary = {"mode": "ordinary", "version": item["version"], "data": revised, "note": "A later ordinary note does not replace the final version."}
        _, after = self.admin.call("POST", endpoint, ordinary)
        self.assertEqual(after["final_revision"]["id"], item["final_revision"]["id"])
        concise = {"mode": "final", "version": after["version"], "data": {"summary": "A concise revised conclusion with the boundary condition explained. The detailed derivation is in the attached ZIP.", "assessment": "supported", "ai_used": "no"}, "package_name": "revised-report.zip", "package_base64": base64.b64encode(package()).decode()}
        status, after = self.admin.call("POST", endpoint, concise)
        self.assertEqual(status, 200, after)
        status, final_view = other.call("GET", f"/api/finals/{item['id']}")
        self.assertEqual(status, 200)
        self.assertEqual(other.call("GET", "/api/revision-files/" + final_view["final"]["package"]["id"])[1], package())
        self.assertEqual(self.admin.call("POST", "/api/contributions", {"kind": "new"})[0], 201)
        self.assertEqual(self.admin.call("POST", "/api/contributions", {"kind": "new"})[0], 201)
        self.assertEqual(self.admin.call("POST", "/api/contributions", {"kind": "new"})[0], 201)


if __name__ == "__main__":
    unittest.main()
