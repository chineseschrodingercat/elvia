"""Callback metadata uses fake credentials and no provider or operational files."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/enable_project_domain_callback.py"


class CallbackSetup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("private_callback_setup", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def config(self):
        return {"client_id": "synthetic.apps.googleusercontent.com",
                "client_secret": "synthetic-only-secret",
                "redirect_uri": self.module.LOCAL_CALLBACK}

    def test_preserves_credentials_and_rollback_callback_while_adding_exact_project_callback(self):
        raw = self.config()
        raw["redirect_uris"] = [self.module.LOCAL_CALLBACK, self.module.PREVIOUS_CALLBACK]
        result = self.module.build_project_config(raw)
        self.assertEqual(result["client_id"], raw["client_id"])
        self.assertEqual(result["client_secret"], raw["client_secret"])
        self.assertEqual(result["redirect_uri"], self.module.LOCAL_CALLBACK)
        self.assertEqual(result["redirect_uris"], list(self.module.APPROVED_CALLBACKS))
        self.assertEqual(raw["redirect_uris"], [self.module.LOCAL_CALLBACK,
                                               self.module.PREVIOUS_CALLBACK])
        self.assertEqual(self.module.build_project_config(result), result)
        self.assertEqual(self.module.validate_saved_config(result), result)

    def test_existing_metadata_validation_does_not_add_new_callback_before_publication(self):
        raw = self.config()
        raw["redirect_uris"] = [self.module.LOCAL_CALLBACK, self.module.PREVIOUS_CALLBACK]
        self.assertEqual(self.module.validate_saved_config(raw), raw)
        self.assertNotIn(self.module.PROJECT_CALLBACK,
                         self.module.validate_saved_config(raw)["redirect_uris"])

    def test_rejects_unexpected_existing_callback_without_echoing_credentials(self):
        raw = self.config()
        raw["redirect_uris"] = [self.module.LOCAL_CALLBACK, "https://attacker.invalid/callback"]
        with self.assertRaises(ValueError) as caught:
            self.module.build_project_config(raw)
        self.assertNotIn(raw["client_secret"], str(caught.exception))

    def test_rejects_invalid_config_without_echoing_it(self):
        for raw in (None, [], {}, {**self.config(), "client_id": "invalid"}):
            with self.subTest(shape=type(raw).__name__), self.assertRaises(ValueError) as caught:
                self.module.build_project_config(raw)
            self.assertNotIn("synthetic-only-secret", str(caught.exception))

    def test_rejects_duplicate_or_missing_local_and_foreign_lookalike_callbacks(self):
        for redirects in ([self.module.LOCAL_CALLBACK] * 2,
                          [self.module.PROJECT_CALLBACK],
                          [self.module.LOCAL_CALLBACK, self.module.PROJECT_CALLBACK + "/"],
                          [self.module.LOCAL_CALLBACK, "https://www.elvia-atlas.org/api/auth/google/callback"],
                          [self.module.LOCAL_CALLBACK, "https://elvia-atlas.org:443/api/auth/google/callback"],
                          [self.module.LOCAL_CALLBACK, None]):
            with self.subTest(redirects=redirects), self.assertRaises(ValueError):
                self.module.build_project_config({**self.config(), "redirect_uris": redirects})

    def test_atomic_publication_adds_project_callback_once_without_losing_rollback_metadata(self):
        raw = self.config()
        raw["redirect_uris"] = [self.module.LOCAL_CALLBACK, self.module.PREVIOUS_CALLBACK]
        desired = self.module.build_project_config(raw)
        with tempfile.TemporaryDirectory() as folder, patch("configure_private_auth.private_acl"):
            data = Path(folder)
            destination = data / "google-oauth.json"
            destination.write_text(json.dumps(raw), "utf-8")
            self.assertTrue(self.module.publish(data, "google-oauth.json", desired,
                                                self.module.validate_saved_config, True))
            self.assertEqual(json.loads(destination.read_text("utf-8")), desired)
            before = destination.read_bytes()
            self.assertFalse(self.module.publish(data, "google-oauth.json", desired,
                                                 self.module.validate_saved_config, True))
            self.assertEqual(destination.read_bytes(), before)
