"""Synthetic HTTP checks for the isolated Atlas mount; never use paper code."""

import hashlib
import http.client
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))
import local_service  # noqa: E402


class AtlasRoutes(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        # Windows CI may return a short-name TEMP path (for example RUNNER~1).
        # The static handler resolves its file paths, so use the same canonical
        # spelling for the injected site root as the real module-level SITE.
        self.root = Path(self.temporary.name).resolve()
        self.site = self.root / "site"
        self.atlas = self.site / "atlas"
        self.atlas.mkdir(parents=True)
        self.files = {
            "index.html": b"<!doctype html><title>Synthetic Atlas</title>",
            "case.html": b"<!doctype html><title>Synthetic case</title>",
            "atlas.css": b"body { color: black; }",
            "data.json": b'{"case_count":1}\n',
            "vendor/fonts/test.woff2": b"synthetic-font-only",
            "evidence/SYNTHETIC-001.zip": b"synthetic-download-only",
            "evidence/SYNTHETIC-001/record.json": b'{"synthetic":true}\n',
            "evidence/SYNTHETIC-001/report.md": b"Synthetic report only.\n",
            "evidence/SYNTHETIC-001/report.tex": b"Synthetic TeX only.\n",
            "evidence/SYNTHETIC-001/check.py": b"raise RuntimeError('never execute')\n",
            "evidence/SYNTHETIC-001/proof.html": b"<script>alert('never inline')</script>",
        }
        for name, body in self.files.items():
            destination = self.atlas / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(body)
        (self.site / "index.html").write_bytes(b"Synthetic contribution home")
        (self.site / "private.json").write_bytes(b"Must remain outside general allowlist")
        self.write_manifest()
        self.site_patch = patch.object(local_service, "SITE", self.site)
        self.site_patch.start()
        self.server = None
        self.thread = None

    def write_manifest(self, extras=()):
        rows = [
            {"path": name, "sha256": hashlib.sha256(body).hexdigest()}
            for name, body in self.files.items()
        ]
        rows.extend(extras)
        (self.atlas / "integration-files.json").write_text(
            json.dumps({"schema_version": 1, "files": rows}), encoding="utf-8"
        )

    def start(self):
        self.server = local_service.make_server(
            self.root / "synthetic-data", bootstrap_password="Synthetic-route-test-password-42"
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def request(self, path, method="GET", headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port)
        try:
            connection.request(method, path, headers=headers or {})
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def tearDown(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.thread.join()
        self.site_patch.stop()
        self.temporary.cleanup()

    def test_mount_redirect_index_and_case_query(self):
        self.start()
        status, headers, _ = self.request("/atlas")
        self.assertEqual(status, 308)
        self.assertEqual(headers["Location"], "/atlas/")
        for path, expected in [
            ("/atlas/", self.files["index.html"]),
            ("/atlas/case.html?case=SYNTHETIC-001", self.files["case.html"]),
        ]:
            status, headers, body = self.request(path)
            self.assertEqual(status, 200, path)
            self.assertEqual(body, expected)
            self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
            self.assertIn("script-src 'self'", headers["Content-Security-Policy"])

    def test_manifest_assets_and_exports_have_safe_types_and_exact_bytes(self):
        self.start()
        expected_types = {
            "atlas.css": "text/css",
            "data.json": "application/json",
            "vendor/fonts/test.woff2": "font/woff2",
            "evidence/SYNTHETIC-001.zip": "application/zip",
            "evidence/SYNTHETIC-001/record.json": "application/json",
            "evidence/SYNTHETIC-001/report.md": "text/markdown",
            "evidence/SYNTHETIC-001/report.tex": "application/x-tex",
            "evidence/SYNTHETIC-001/check.py": "application/octet-stream",
            "evidence/SYNTHETIC-001/proof.html": "application/octet-stream",
        }
        for name, content_type in expected_types.items():
            with self.subTest(name=name):
                status, headers, body = self.request("/atlas/" + name)
                self.assertEqual(status, 200)
                self.assertEqual(body, self.files[name])
                self.assertEqual(headers["Content-Type"].split(";")[0], content_type)
                if name.startswith("evidence/"):
                    self.assertTrue(headers["Content-Disposition"].startswith("attachment;"))

    def test_head_reports_exact_length_without_sending_body(self):
        self.start()
        status, headers, body = self.request("/atlas/data.json", "HEAD")
        self.assertEqual(status, 200)
        self.assertEqual(int(headers["Content-Length"]), len(self.files["data.json"]))
        self.assertEqual(body, b"")

    def test_added_files_and_mutated_manifest_do_not_expand_startup_allowlist(self):
        self.start()
        (self.atlas / "added.html").write_bytes(b"Unregistered added page")
        self.files["added.html"] = b"Unregistered added page"
        self.write_manifest()
        self.assertEqual(self.request("/atlas/added.html")[0], 404)
        self.assertEqual(self.request("/atlas/integration-files.json")[0], 404)

    def test_corrupted_registered_file_is_never_served(self):
        self.start()
        (self.atlas / "atlas.css").write_bytes(b"body { color: brown; }")
        self.assertEqual(self.request("/atlas/atlas.css")[0], 404)

    def test_unsafe_paths_dotfiles_and_general_json_remain_blocked(self):
        self.start()
        for path in [
            "/atlas/../index.html", "/atlas/%2e%2e/index.html",
            "/atlas/%2f../index.html", "/atlas/vendor/../index.html",
            "/atlas/%5c..%5cindex.html", "/atlas//index.html",
            "/atlas/./index.html", "/atlas/.secret", "/atlas/.git/config",
            "/atlas/index.html:private", "/atlas/%00index.html", "/private.json",
            "/Atlas/index.html", "/atlas%5cindex.html", "/atlas\\index.html",
            "/%61tlas/index.html", "/atlas%2findex.html",
        ]:
            with self.subTest(path=path):
                self.assertEqual(self.request(path)[0], 404)
        self.assertEqual(self.request("/")[0], 200)

    def test_existing_host_origin_and_auth_checks_are_unchanged(self):
        self.start()
        self.assertEqual(self.request("/atlas/", headers={"Host": "example.org"})[0], 403)
        self.assertEqual(self.request("/atlas/", "POST")[0], 403)
        origin = f"http://127.0.0.1:{self.server.server_port}"
        self.assertEqual(self.request("/atlas/", "POST", {"Origin": origin})[0], 405)
        self.assertEqual(self.request("/api/me")[0], 401)
        self.assertEqual(self.request("/api/admin")[0], 401)

    def test_missing_atlas_leaves_existing_preview_usable(self):
        (self.atlas / "integration-files.json").unlink()
        self.start()
        self.assertEqual(self.request("/")[0], 200)
        self.assertEqual(self.request("/atlas/")[0], 404)
        self.assertEqual(self.request("/atlas/index.html")[0], 404)

    def test_atlas_added_after_startup_is_unavailable_until_restart(self):
        (self.atlas / "integration-files.json").unlink()
        self.start()
        self.write_manifest()
        self.assertEqual(self.request("/atlas/index.html")[0], 404)

    def test_invalid_manifest_fails_closed(self):
        self.write_manifest([{"path": "../index.html", "sha256": "0" * 64}])
        self.start()
        self.assertEqual(self.request("/atlas/index.html")[0], 404)

    def test_manifest_hash_mismatch_fails_closed_at_startup(self):
        (self.atlas / "atlas.css").write_bytes(b"Changed before startup")
        self.start()
        self.assertEqual(self.request("/atlas/index.html")[0], 404)

    def test_duplicate_manifest_paths_fail_closed(self):
        self.write_manifest([{
            "path": "INDEX.HTML", "sha256": hashlib.sha256(self.files["index.html"]).hexdigest()
        }])
        self.start()
        self.assertEqual(self.request("/atlas/index.html")[0], 404)

    def test_registered_dotfile_disables_the_mount(self):
        (self.atlas / ".private").write_bytes(b"Synthetic private bytes")
        self.write_manifest([{
            "path": ".private", "sha256": hashlib.sha256(b"Synthetic private bytes").hexdigest()
        }])
        self.start()
        self.assertEqual(self.request("/atlas/.private")[0], 404)
        self.assertEqual(self.request("/atlas/index.html")[0], 404)

    def test_runtime_directory_link_is_blocked_even_when_bytes_match(self):
        self.start()
        original = self.atlas / "vendor"
        retained = self.atlas / "retained-vendor"
        original.rename(retained)
        outside = self.root / "outside-vendor"
        (outside / "fonts").mkdir(parents=True)
        (outside / "fonts" / "test.woff2").write_bytes(self.files["vendor/fonts/test.woff2"])
        if os.name == "nt":
            result = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(original), str(outside)],
                capture_output=True, check=False,
            )
            if result.returncode:
                retained.rename(original)
                self.skipTest("Windows junction creation is unavailable")
        else:
            original.symlink_to(outside, target_is_directory=True)
        try:
            self.assertEqual(self.request("/atlas/vendor/fonts/test.woff2")[0], 404)
        finally:
            if os.name == "nt":
                original.rmdir()
            else:
                original.unlink()
            retained.rename(original)

    def test_registered_link_to_outside_is_blocked(self):
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "leak.txt").write_bytes(b"Synthetic outside secret")
        linked = self.atlas / "linked"
        if os.name == "nt":
            result = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(linked), str(outside)],
                capture_output=True, check=False,
            )
            if result.returncode:
                self.skipTest("Windows junction creation is unavailable")
        else:
            linked.symlink_to(outside, target_is_directory=True)
        try:
            self.write_manifest([{
                "path": "linked/leak.txt",
                "sha256": hashlib.sha256(b"Synthetic outside secret").hexdigest(),
            }])
            self.start()
            self.assertEqual(self.request("/atlas/linked/leak.txt")[0], 404)
        finally:
            if os.name == "nt":
                linked.rmdir()
            else:
                linked.unlink()


if __name__ == "__main__":
    unittest.main()
