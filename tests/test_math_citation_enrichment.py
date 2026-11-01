"""Regression tests for source-bound, citation-only Math enrichment."""

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "math_citation_enrichment.py"
SPEC = importlib.util.spec_from_file_location("math_citation_enrichment", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class CitationEnrichmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "catalog.json"
        self.case = "math2025-0001"
        self.source_hash = "a" * 64
        self.row = {
            "revision": 1,
            "record_sha256": "b" * 64,
            "citation": {
                "title": "A verified article",
                "authors": ["A. Mathematician"],
                "container": "Example Mathematics Journal",
                "volume": "",
                "year": 2025,
                "first_page": "",
                "last_page": "",
                "publisher": "",
                "doi": "10.1234/verified",
                "source_url": "https://doi.org/10.1234/verified",
            },
            "contributors": [
                {"name": "Reviewer", "role": "Initial report", "revision": 1}
            ],
            "verified_on": "2026-11-01",
        }
        self.updates = {
            "volume": "239",
            "first_page": "1",
            "last_page": "20",
            "publication_type": "journal",
        }

    def catalog(self, *, row=None, updates=None, extra=None):
        row = row or self.row
        updates = self.updates if updates is None else updates
        after = {**row["citation"], **updates}
        entry = {
            "status": "resolved",
            "source_manifest_sha256": self.source_hash,
            "citation_before_sha256": MOD.digest(row["citation"]),
            "citation_after_sha256": MOD.digest(after),
            "updates": updates,
            "field_sources": {
                k: [
                    {
                        "source": "accepted_source_manifest",
                        "pointer": "/publisher/" + k,
                        "value": v,
                    }
                ]
                for k, v in updates.items()
            },
        }
        if extra:
            entry.update(extra)
        self.path.write_text(
            json.dumps(
                {
                    "format_version": 1,
                    "collection": "math2025",
                    "cases": {self.case: entry},
                }
            ),
            encoding="utf-8",
        )
        MOD._load_catalog.cache_clear()
        return entry

    def apply(self, row=None, source_hash=None, case=None):
        return MOD.enrich_reader_row(
            case or self.case,
            self.row if row is None else row,
            self.source_hash if source_hash is None else source_hash,
            catalog_path=self.path,
        )

    def test_updates_only_citation_and_adds_auditable_provenance(self):
        self.catalog()
        original = copy.deepcopy(self.row)
        out = self.apply()
        self.assertEqual(self.row, original)
        self.assertEqual(out["citation"]["volume"], "239")
        self.assertEqual(out["citation"]["last_page"], "20")
        for key, value in original.items():
            if key != "citation":
                self.assertEqual(out[key], value)
        for key in ("doi", "source_url", "title", "authors", "container"):
            self.assertEqual(out["citation"][key], original["citation"][key])
        self.assertEqual(
            out["citation_provenance"]["source_manifest_sha256"], self.source_hash
        )
        self.assertEqual(
            out["citation_provenance"]["citation_after_sha256"],
            MOD.digest(out["citation"]),
        )

    def test_idempotent_complete_row(self):
        self.catalog()
        out = self.apply()
        self.assertEqual(self.apply(out), out)

    def test_changed_source_manifest_fails(self):
        self.catalog()
        with self.assertRaisesRegex(ValueError, "source manifest changed"):
            self.apply(source_hash="c" * 64)

    def test_changed_citation_identity_fails(self):
        self.catalog()
        changed = copy.deepcopy(self.row)
        changed["citation"]["doi"] = "10.1234/unrelated"
        with self.assertRaisesRegex(ValueError, "reviewed before/after"):
            self.apply(changed)

    def test_existing_verified_volume_cannot_be_overwritten(self):
        changed = copy.deepcopy(self.row)
        changed["citation"]["volume"] = "238"
        self.catalog(row=changed)
        with self.assertRaisesRegex(ValueError, "existing verified volume"):
            self.apply(changed)

    def test_other_collection_is_not_enriched(self):
        self.catalog()
        with self.assertRaisesRegex(ValueError, "limited to Math"):
            self.apply(case="icml2025-0001")

    def test_identity_field_update_is_rejected_even_with_matching_hash(self):
        self.catalog(updates={**self.updates, "doi": "10.1234/unrelated"})
        with self.assertRaisesRegex(ValueError, "unsupported fields"):
            self.apply()

    def test_each_changed_field_needs_evidence(self):
        self.catalog(extra={"field_sources": {}})
        with self.assertRaisesRegex(ValueError, "lacks field evidence"):
            self.apply()

    def test_empty_volume_without_explicit_status_still_fails(self):
        self.catalog(updates={"publication_type": "journal"})
        with self.assertRaisesRegex(ValueError, "volume is unresolved"):
            self.apply()

    def test_online_first_has_no_invented_volume_or_pages(self):
        self.catalog(
            updates={
                "publication_type": "journal",
                "publication_status": "online_first",
            },
            extra={
                "online_first_evidence": [
                    {"source": "publisher", "value": "Published online first"}
                ]
            },
        )
        out = self.apply()
        for key in ("volume", "first_page", "last_page"):
            self.assertEqual(out["citation"][key], "")
        self.assertEqual(out["citation"]["publication_status"], "online_first")

    def test_online_first_without_positive_evidence_is_rejected(self):
        self.catalog(
            updates={
                "publication_type": "journal",
                "publication_status": "online_first",
            }
        )
        with self.assertRaisesRegex(ValueError, "lacks explicit evidence"):
            self.apply()

    def test_online_first_cannot_hide_assigned_volume(self):
        self.catalog(
            updates={**self.updates, "publication_status": "online_first"},
            extra={
                "online_first_evidence": [
                    {"source": "publisher", "value": "Published online first"}
                ]
            },
        )
        with self.assertRaisesRegex(ValueError, "assigned volume"):
            self.apply()

    def test_standalone_preserves_other_collections(self):
        self.catalog()
        other = {"revision": 9, "citation": {"unchanged": [1, 2, 3]}}
        reader = {
            "format_version": 1,
            "cases": {self.case: self.row, "icml2025-0001": other},
        }
        manifest = {
            "papers": [
                {
                    "case_id": self.case,
                    "public_record_sha256": self.row["record_sha256"],
                    "archive_hashes": {"source_manifest": self.source_hash},
                }
            ]
        }
        output = MOD.enrich_reader_catalog(reader, manifest, catalog_path=self.path)
        self.assertEqual(output["cases"]["icml2025-0001"], other)
        self.assertEqual(reader["cases"][self.case], self.row)
        manifest["papers"][0]["public_record_sha256"] = "c" * 64
        with self.assertRaisesRegex(ValueError, "record binding mismatch"):
            MOD.enrich_reader_catalog(reader, manifest, catalog_path=self.path)

    def test_conflicting_existing_audit_is_rejected(self):
        self.catalog()
        output = self.apply()
        output["citation_provenance"]["entry_sha256"] = "c" * 64
        with self.assertRaisesRegex(
            ValueError, "conflicting existing citation provenance"
        ):
            self.apply(output)

    def test_unresolved_catalog_entry_is_not_a_placeholder(self):
        self.catalog(extra={"status": "unresolved"})
        with self.assertRaisesRegex(ValueError, "unresolved citation metadata"):
            self.apply()


if __name__ == "__main__":
    unittest.main()
