"""Structured reports and paper-wide reservations use isolated synthetic state."""
import io
import json
import unittest
import zipfile
import sqlite3
from concurrent.futures import ThreadPoolExecutor

import test_local_service as helpers
import browser_reports as reports


class SyntheticAtlas:
    def __init__(self):
        self.revision = 1

    def read(self, path):
        record = {
            "case_id": "synthetic-paper", "revision": self.revision,
            "source": {"title": "Synthetic paper", "doi": "10.1234/synthetic", "version": "v1"},
            "audit": {"venue": "NeurIPS", "landing_url": "https://doi.org/10.1234/synthetic", "outcome": "candidate_issue"},
        }
        if path not in ("data.json", "cases/synthetic-paper.context.json"):
            return None
        return json.dumps({"records": [record], "case_notes": {"synthetic-paper": {
            "revision": self.revision, "problems": [
                {"title": "First synthetic problem"}, {"title": "Second synthetic problem"},
            ],
        }}}).encode(), "application/json", {}


def problem(target=None):
    return {"target": target, "title": "A bounded synthetic question", "severity": "minor",
            "location": "Equation 2, page 3", "claim": "A synthetic quantity is normalized by its reference.",
            "reasoning": "Both values must use the same scale: 6 / 3 = 60 / 30 = 2.",
            "correction": "State the shared-scale assumption.", "limits": "This algebra does not validate an experiment."}


class BrowserReports(unittest.TestCase):
    setUp = helpers.ServiceContract.setUp
    tearDown = helpers.ServiceContract.tearDown
    reviewer = helpers.ServiceContract.reviewer

    def initial(self, client=None, url="https://example.org/new-paper"):
        client = client or self.admin
        code, item = client.call("POST", "/api/contributions", {"kind": "new", "editor": "files", "source_url": url})
        self.assertEqual(code, 201, item)
        return item

    def save_report(self, item, client=None, problems=None, **fields):
        client = client or self.admin
        data = {**item["data"], "title": "Synthetic paper", "venue": "NeurIPS", "field": "computer_science",
                "summary": "A focused synthetic check preserves the normalization assumption.", "assessment": "clarification",
                "source_access": "upload", "source_version": "Published version", "paper_supplement": "not_applicable", "ai_used": "no",
                "conflict_clear": True, "synthetic": True,
                "addressed_problems": [p["target"] for p in (problems or []) if p["target"] is not None], **fields}
        code, result = client.call("PUT", f"/api/contributions/{item['id']}", {"version": item["version"], "data": data})
        self.assertEqual(code, 200, result)
        if "report" not in result["files"]:
            code, result = client.call("POST", f"/api/contributions/{result['id']}/report", rb"\documentclass{article}\begin{document}Synthetic report. Equation 2.\end{document}", {"X-Filename": "report.tex", "X-Version": str(result["version"])})
            self.assertEqual(code, 200, result)
        return result

    def test_browser_report_is_saved_and_submitted_without_a_manual_zip(self):
        item = self.save_report(self.initial())
        self.assertEqual(item["files"]["report"]["name"], "report.tex")
        code, result = self.admin.call("POST", f"/api/contributions/{item['id']}/submit", {"version": item["version"], "attest": True})
        self.assertEqual(code, 400)
        self.assertIn("PDF", result["error"])
        code, item = self.admin.call("POST", f"/api/contributions/{item['id']}/source", b"%PDF-1.4\nSynthetic fixture only\n%%EOF", {"X-Filename": "paper.pdf", "X-Version": str(item["version"])})
        self.assertEqual(code, 200, item)
        code, item = self.admin.call("POST", f"/api/contributions/{item['id']}/submit", {"version": item["version"], "attest": True})
        self.assertEqual(code, 200, item)
        self.assertEqual(item["status"], "submitted")
        code, blob = self.admin.call("GET", "/api/packages/" + item["package"]["id"])
        self.assertEqual(code, 200)
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            self.assertIn("report.tex", archive.namelist())
            self.assertIn("Equation 2", archive.read("report.tex").decode())

    def test_atlas_revision_targets_existing_problem_and_locks_other_routes(self):
        self.server.atlas = SyntheticAtlas()
        code, item = self.admin.call("POST", "/api/contributions", {"kind": "revision", "case_id": "synthetic-paper", "problem": 2})
        self.assertEqual(code, 201, item)
        self.assertEqual(item["paper"]["base"]["problems"][1]["number"], 2)
        item = self.save_report(item, problems=[problem(2), problem()])
        code, result = self.admin.call("POST", "/api/contributions", {"kind": "revision", "case_id": "synthetic-paper"})
        self.assertEqual(code, 409, result)
        code, result = self.admin.call("POST", "/api/contributions", {"kind": "new", "editor": "files", "source_url": "https://doi.org/10.1234/synthetic"})
        self.assertEqual(code, 409, result)
        code, availability = helpers.Client(self.base).call("GET", "/api/papers/synthetic-paper")
        self.assertEqual(code, 200)
        self.assertEqual(availability["status"], "in_progress")
        self.assertNotIn("owner", availability)

    def test_new_paper_claim_is_exclusive_before_submission(self):
        self.initial()
        code, result = self.admin.call("POST", "/api/contributions", {"kind": "new", "editor": "files", "source_url": "https://example.org/new-paper/"})
        self.assertEqual(code, 409, result)

    def test_optional_code_rejects_more_than_five_mib(self):
        item = self.initial()
        code, result = self.admin.call("POST", f"/api/contributions/{item['id']}/verification-code", b"x" * (5 * 1024 * 1024 + 1), {"X-Filename": "extra.zip", "X-Version": str(item["version"])})
        self.assertEqual(code, 413, result)

    def revision(self, client=None):
        self.server.atlas = SyntheticAtlas()
        client = client or self.admin
        code, item = client.call("POST", "/api/contributions", {"kind": "revision", "case_id": "synthetic-paper"})
        self.assertEqual(code, 201, item)
        return self.save_report(item, client, [problem(2), problem()])

    def test_acceptance_stays_locked_until_verified_new_published_revision(self):
        item = self.revision()
        code, item = self.admin.call("POST", f"/api/contributions/{item['id']}/submit", {"version": item["version"], "attest": True})
        self.assertEqual(code, 200, item)
        code, item = self.admin.call("POST", f"/api/admin/contributions/{item['id']}/decision", {"version": item["version"], "decision": "accepted", "note": "Synthetic editorial acceptance"})
        self.assertEqual(code, 200, item)
        self.assertEqual(self.admin.call("GET", "/api/papers/synthetic-paper")[1]["status"], "awaiting_integration")
        code, _ = self.admin.call("POST", "/api/contributions", {"kind": "revision", "case_id": "synthetic-paper"})
        self.assertEqual(code, 409)
        request = {"version": item["version"], "case_id": "synthetic-paper", "revision": 1, "integration_confirmed": True, "note": "Synthetic changes checked against the published record."}
        endpoint = f"/api/admin/contributions/{item['id']}/integrate"
        self.assertEqual(self.admin.call("POST", endpoint, request)[0], 409)
        self.server.atlas.revision = 2
        request["revision"] = 2
        code, integrated = self.admin.call("POST", endpoint, request)
        self.assertEqual(code, 200, integrated)
        self.assertFalse(integrated["paper"]["active"])
        self.assertEqual(self.admin.call("GET", "/api/papers/synthetic-paper")[1]["status"], "available")
        code, next_item = self.admin.call("POST", "/api/contributions", {"kind": "revision", "case_id": "synthetic-paper"})
        self.assertEqual(code, 201, next_item)
        self.assertEqual(next_item["paper"]["base"]["revision"], 2)

    def test_simultaneous_claims_have_exactly_one_winner(self):
        self.server.atlas = SyntheticAtlas()
        clients = [self.reviewer(n)[0] for n in (1, 2)]
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda client: client.call("POST", "/api/contributions", {"kind": "revision", "case_id": "synthetic-paper"}), clients))
        self.assertEqual(sorted(code for code, _ in results), [201, 409])

    def test_target_validation_and_stale_base_preserve_saved_draft(self):
        item = self.revision()
        for problems in ([problem(3)], [problem(2), problem(2)], [problem(True)]):
            code, _ = self.admin.call("PUT", f"/api/contributions/{item['id']}", {"version": item["version"], "data": {**item["data"], "addressed_problems": [p["target"] for p in problems]}})
            self.assertEqual(code, 400)
        self.server.atlas.revision = 2
        code, _ = self.admin.call("POST", f"/api/contributions/{item['id']}/submit", {"version": item["version"], "attest": True})
        self.assertEqual(code, 409)
        self.assertEqual(self.admin.call("GET", f"/api/contributions/{item['id']}")[1]["data"], item["data"])

    def test_changes_requested_keep_lock_and_release_reopens(self):
        item = self.revision()
        _, item = self.admin.call("POST", f"/api/contributions/{item['id']}/submit", {"version": item["version"], "attest": True})
        _, item = self.admin.call("POST", f"/api/admin/contributions/{item['id']}/decision", {"version": item["version"], "decision": "needs_changes", "note": "Clarify the scope of this synthetic check."})
        self.assertEqual(self.admin.call("GET", "/api/papers/synthetic-paper")[1]["status"], "in_progress")
        self.assertEqual(self.admin.call("POST", f"/api/contributions/{item['id']}/release", {"version": item["version"]})[0], 200)
        self.assertTrue(self.admin.call("GET", "/api/papers/synthetic-paper")[1]["available"])

    def test_public_catalog_availability_has_no_private_identifiers(self):
        self.revision()
        code, result = helpers.Client(self.base).call("GET", "/api/paper-availability")
        self.assertEqual(code, 200, result)
        self.assertEqual(result["papers"]["synthetic-paper"]["status"], "in_progress")
        self.assertNotIn("owner", json.dumps(result))
        self.assertNotIn("my_contribution", json.dumps(result))

    def test_legacy_amendment_creation_cannot_bypass_paper_reservation(self):
        item = self.revision()
        code, result = self.admin.call("POST", f"/api/finals/{item['id']}/amendments", {"reason": "A different suggestion about this already reserved paper.", "ai_used": "no"})
        self.assertEqual(code, 409, result)
        self.assertIn("browser revision editor", result["error"])

    def test_private_files_and_immutable_resubmission(self):
        client, _ = self.reviewer()
        item = self.revision(client)
        attachment = item["files"]["report"]["id"]
        other, _ = self.reviewer(2)
        self.assertEqual(other.call("GET", "/api/contribution-files/" + attachment)[0], 403)
        self.assertEqual(helpers.Client(self.base).call("GET", "/api/contribution-files/" + attachment)[0], 401)
        original = client.call("GET", "/api/contribution-files/" + attachment)[1]
        endpoint = f"/api/contributions/{item['id']}/submit"
        code, item = client.call("POST", endpoint, {"version": item["version"], "attest": True})
        self.assertEqual(code, 200, item)
        frozen = item["revisions"][0]["data"]
        self.assertEqual(frozen["file_ids"]["report"], attachment)
        self.assertEqual(client.call("POST", f"/api/contributions/{item['id']}/report", original, {"X-Filename": "report.tex", "X-Version": str(item["version"])})[0], 409)
        _, item = self.admin.call("POST", f"/api/admin/contributions/{item['id']}/decision", {"version": item["version"], "decision": "needs_changes", "note": "State the synthetic code limitations."})
        code, item = client.call("POST", f"/api/contributions/{item['id']}/report", original.replace(b"Equation 2", b"Equation 3"), {"X-Filename": "report-v2.tex", "X-Version": str(item["version"])})
        self.assertEqual(code, 200, item)
        self.assertNotEqual(item["files"]["report"]["id"], attachment)
        self.assertEqual(client.call("GET", "/api/contribution-files/" + attachment)[1], original)
        self.assertEqual(item["revisions"][0]["data"], frozen)

    def test_integration_is_staff_only_and_source_identity_is_server_owned(self):
        client, _ = self.reviewer()
        item = self.revision(client)
        item = self.save_report(item, client, title="Tampered identity", source_url="https://example.org/wrong", source_version="forged")
        self.assertEqual(item["data"]["title"], "Synthetic paper")
        self.assertEqual(item["data"]["source_url"], "https://doi.org/10.1234/synthetic")
        code, _ = client.call("POST", f"/api/admin/contributions/{item['id']}/integrate", {"version": item["version"]})
        self.assertEqual(code, 403)

    def test_final_decision_cannot_freeze_an_unfinished_browser_draft(self):
        item = self.revision()
        code, result = self.admin.call("POST", f"/api/admin/contributions/{item['id']}/revisions", {"version": item["version"], "mode": "final", "data": item["data"], "note": "Synthetic premature final decision."})
        self.assertEqual(code, 409, result)
        self.assertEqual(self.admin.call("POST", f"/api/contributions/{item['id']}/release", {"version": item["version"]})[0], 200)


class ReportMigration(unittest.TestCase):
    def old_database(self, duplicate=False):
        db = sqlite3.connect(":memory:")
        db.row_factory = sqlite3.Row
        db.execute("CREATE TABLE users(id TEXT PRIMARY KEY)")
        db.execute("INSERT INTO users VALUES('fixture')")
        db.execute("CREATE TABLE contributions(id TEXT PRIMARY KEY,data TEXT,task_id TEXT,status TEXT,created TEXT)")
        db.execute("CREATE UNIQUE INDEX one_claim ON contributions(task_id) WHERE status IN ('draft','needs_changes','submitted','accepted')")
        for i in range(2 if duplicate else 1):
            db.execute("INSERT INTO contributions VALUES(?,?,?,?,?)", (str(i), json.dumps({"source_url": "https://doi.org/10.1234/synthetic"}), None, "accepted", "2026-01-01"))
        db.commit()
        return db

    def test_migration_is_additive_idempotent_and_backfills_accepted_lock(self):
        db = self.old_database()
        before = [tuple(r) for r in db.execute("SELECT * FROM contributions")]
        with db:
            reports.migrate(db)
        with db:
            reports.migrate(db)
        self.assertEqual([tuple(r) for r in db.execute("SELECT * FROM contributions")], before)
        self.assertEqual(db.execute("SELECT COUNT(*) FROM report_schema").fetchone()[0], 1)
        self.assertEqual(db.execute("SELECT active FROM paper_claims").fetchone()[0], 1)

    def test_overlapping_legacy_claims_roll_back_without_losing_work(self):
        db = self.old_database(duplicate=True)
        with self.assertRaises(reports.ReportError), db:
            reports.migrate(db)
        self.assertIsNone(db.execute("SELECT name FROM sqlite_master WHERE name='paper_claims'").fetchone())
        self.assertEqual(db.execute("SELECT COUNT(*) FROM contributions").fetchone()[0], 2)

    def test_arxiv_aliases_and_doi_case_have_one_reservation_key(self):
        urls = ["https://doi.org/10.48550/arXiv.2312.12345", "https://arxiv.org/pdf/2312.12345v2.pdf", "https://arxiv.org/abs/2312.12345", "https://arxiv.org/html/2312.12345v1"]
        self.assertEqual({reports.url_key(url) for url in urls}, {"arxiv:2312.12345"})
        self.assertEqual(reports.url_key("https://dx.doi.org/10.1234/SYNTHETIC/"), "doi:10.1234/synthetic")



if __name__ == "__main__":
    unittest.main()
