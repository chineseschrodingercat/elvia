"""File-first submission contracts, with no providers or real paper contents."""
import base64
import random
import unittest

import test_local_service as helpers
from test_browser_reports import SyntheticAtlas

PDF = b"%PDF-1.4\nSynthetic upload fixture only\n%%EOF"
TEX = rb"\documentclass{article}\begin{document}Synthetic bounded report.\end{document}"


class FileReports(unittest.TestCase):
    setUp = helpers.ServiceContract.setUp
    tearDown = helpers.ServiceContract.tearDown

    def create(self, initial=False):
        self.server.atlas = SyntheticAtlas()
        data = {"kind": "new", "source_url": "https://example.org/file-first"} if initial else {"kind": "revision", "case_id": "synthetic-paper"}
        code, item = self.admin.call("POST", "/api/contributions", data)
        self.assertEqual(code, 201, item)
        return item

    def upload(self, item, slot="report", name="report.tex", blob=TEX, expected=200):
        code, result = self.admin.call("POST", f"/api/contributions/{item['id']}/{slot}", blob, {"X-Filename": name, "X-Version": str(item["version"])})
        self.assertEqual(code, expected, result if not isinstance(result, bytes) else "unexpected bytes")
        return result if code == 200 else item

    def save(self, item, **extra):
        data = {**item["data"], "title": "Synthetic paper", "field": "computer_science", "venue": "NeurIPS", "source_version": "Published version", "ai_used": "no", "conflict_clear": True, "synthetic": True, "paper_supplement": "not_applicable", **extra}
        code, item = self.admin.call("PUT", f"/api/contributions/{item['id']}", {"version": item["version"], "data": data})
        self.assertEqual(code, 200, item)
        return item

    def submit(self, item):
        return self.admin.call("POST", f"/api/contributions/{item['id']}/submit", {"version": item["version"], "attest": True})

    def test_revision_requires_uploaded_report_without_retyping_scientific_fields(self):
        item = self.save(self.create())
        self.assertEqual(self.submit(item)[0], 400)
        item = self.upload(item)
        code, result = self.submit(item)
        self.assertEqual(code, 200, result)
        self.assertEqual(result["status"], "submitted")
        self.assertNotIn("report", result["data"])
        self.assertEqual(result["files"]["report"]["mime"], "text/plain; charset=utf-8")

    def test_first_report_requires_paper_and_applicable_supplement_in_distinct_slots(self):
        item = self.save(self.create(True), paper_supplement="provided")
        item = self.upload(item, blob=PDF, name="report.pdf")
        self.assertEqual(self.submit(item)[0], 400)
        item = self.upload(item, "source", "paper.pdf", PDF)
        self.assertEqual(self.submit(item)[0], 400)
        item = self.upload(item, "paper-supplement", "supplement.pdf", PDF)
        code, result = self.submit(item)
        self.assertEqual(code, 200, result)
        self.assertNotEqual(result["files"]["report"]["id"], result["files"]["paper-supplement"]["id"])

    def test_pdf_and_latex_reports_are_bounded_and_invalid_upload_preserves_prior_file(self):
        item = self.upload(self.create())
        original = item["files"]["report"]["sha256"]
        accepted = PDF[:-5].ljust(20 * 1024 * 1024 - 5, b" ") + b"%%EOF"
        item = self.upload(item, name="large-report.pdf", blob=accepted)
        original = item["files"]["report"]["sha256"]
        for name, blob, status in [("report.txt", b"text", 400), ("report.tex", b"not a document", 400), ("report.pdf", b"not a PDF", 400), ("report.tex", b"x" * (20 * 1024 * 1024 + 1), 413)]:
            with self.subTest(name=name, size=len(blob)):
                self.upload(item, name=name, blob=blob, expected=status)
        current = self.admin.call("GET", "/api/contributions/" + item["id"])[1]
        self.assertEqual(current["files"]["report"]["sha256"], original)

    def test_article_and_supplement_share_fifty_mib_and_replacements_free_capacity(self):
        item = self.create(True)
        def sized(mib, extra=0):
            return b"%PDF-1.4\n" + b"x" * (mib * 1024 * 1024 + extra - 15) + b"\n%%EOF"
        item = self.upload(item, "source", "paper.pdf", sized(50))
        self.upload(item, "paper-supplement", "supplement.pdf", PDF, 413)
        item = self.upload(item, "source", "paper.pdf", sized(30))
        item = self.upload(item, "paper-supplement", "supplement.pdf", sized(20))
        self.upload(item, "source", "paper.pdf", sized(30, 1), 413)
        self.upload(item, "paper-supplement", "supplement.pdf", sized(20, 1), 413)
        item = self.upload(item, "source", "paper.pdf", sized(25))
        item = self.upload(item, "paper-supplement", "supplement.pdf", sized(25))
        self.upload(item, "paper-supplement", "supplement.tex", TEX, 400)

    def test_ai_configuration_is_free_text_and_over_limit_errors_explain_compression(self):
        item = self.save(self.create(), ai_used="yes", ai_model="Research model Z / custom high setting")
        item = self.upload(item)
        code, result = self.submit(item)
        self.assertEqual(code, 200, result)
        self.assertEqual(result["data"]["ai_model"], "Research model Z / custom high setting")
        from file_reports import report
        from browser_reports import ReportError
        with self.assertRaisesRegex(ReportError, "[Cc]ompress"):
            report(b"x" * (20 * 1024 * 1024 + 1), "report.pdf")

    def test_verification_code_accepts_multiple_files_and_limits_total_count_and_bytes(self):
        item = self.create()
        endpoint = f"/api/contributions/{item['id']}/verification-code"
        def body(files):
            return {"files": [{"name": n, "content": base64.b64encode(b).decode()} for n, b in files]}
        request = body([("check.py", b"# never execute"), ("README.md", b"Synthetic fixture instructions")])
        code, item = self.admin.call("POST", endpoint, request, {"X-Version": str(item["version"])})
        self.assertEqual(code, 200, item)
        self.assertEqual(len(item["files"]["verification-code"]["manifest"]), 2)
        code, item = self.admin.call("POST", endpoint, body([("large.py", random.Random(42).randbytes(5 * 1024 * 1024))]), {"X-Version": str(item["version"])})
        self.assertEqual(code, 200, item)
        for files in [[(f"check{i}.py", b"x") for i in range(11)], [("check.py", b"x" * (5 * 1024 * 1024 + 1))], [("../check.py", b"x")], [("check.exe", b"MZ")]]:
            code, result = self.admin.call("POST", endpoint, body(files), {"X-Version": str(item["version"])})
            self.assertIn(code, (400, 413), result)
        self.upload(item, "verification-code", "code.zip", b"x" * (5 * 1024 * 1024 + 1), 413)

    def test_templates_only_use_public_download_routes(self):
        for kind in ("first-report", "revision-report"):
            for suffix in ("tex", "pdf"):
                status, body = helpers.Client(self.base).call("GET", f"/assets/report-templates/{kind}/main.{suffix}")
                self.assertEqual(status, 200, (kind, suffix, body))


if __name__ == "__main__":
    unittest.main()
