"""Review revisions preserve immutable synthetic predecessors and identities."""

import copy
import hashlib
import json
import runpy
from pathlib import Path

import pytest

from elvia.storage import load_records

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def _revision_fixture(tmp_path):
    from test_review_collection import reviewed_input

    audits, raw, audit = reviewed_input.__wrapped__(tmp_path)
    base = tmp_path / "first"
    runpy.run_path(str(SCRIPTS / "import_review_collection.py"))["import_collection"](
        audits, raw, base, expected_count=1
    )
    audit = copy.deepcopy(audit)
    audit["severity"] = "minor"
    audit["outcome"] = "candidate_issue"
    audit["summary"] = r"The local identity fails at \(x=0\)."
    audit["impact_rationale"] = "A local fixture identity; the central claim survives."
    problem = audit["problems"][0]
    problem.update(
        severity="minor",
        assessment="supported",
        impact_rationale="The fixture defect is local.",
        result=["A bounded defect."],
        repair=[],
    )
    (audits / "0001.json").write_text(json.dumps(audit), encoding="utf-8")
    return audits, raw, audit, base


def _builder():
    return runpy.run_path(str(SCRIPTS / "revise_review_collection.py"))[
        "revise_collection"
    ]


def test_review_revision_preserves_original_bytes_and_exports_both_revisions(tmp_path):
    from elvia.site import build_site

    audits, raw, _, base = _revision_fixture(tmp_path)
    original = {
        p.relative_to(base): p.read_bytes() for p in base.rglob("*") if p.is_file()
    }
    output = tmp_path / "revised"
    assert _builder()(base / "records", audits, raw, output, expected_count=1) == 1
    entries = load_records(output / "records")
    assert [r["revision"] for _, r in entries] == [1, 2]
    old, new = [r for _, r in entries]
    for name, value in original.items():
        if str(name) != "case-notes.json":
            assert (base / name).read_bytes() == (output / name).read_bytes() == value
    assert new["previous_revision"] == 1
    assert new["source"]["artifact"] == old["source"]["artifact"]
    assert new["audit"]["pdf_sha256"] == old["audit"]["pdf_sha256"]
    assert new["concern"]["severity"] == "minor"
    assert new["human_reviews"] == []
    assert new["adjudication"]["status"] == "pending"
    assert all("/r2/" in item["artifact"]["path"] for item in new["evidence"])
    note = json.loads((output / "case-notes.json").read_text("utf-8"))["cases"][
        new["case_id"]
    ]
    assert note["revision"] == 2
    canonical = json.dumps(
        new, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode()
    assert note["record_sha256"] == hashlib.sha256(canonical).hexdigest()
    site = tmp_path / "site"
    assert build_site(output / "records", site) == 1
    bundle = site / "evidence" / new["case_id"]
    assert len(list((bundle / "records").glob("*.json"))) == 2
    assert original == {
        p.relative_to(base): p.read_bytes() for p in base.rglob("*") if p.is_file()
    }


@pytest.mark.parametrize(
    "change", ["identity", "moderate", "missing_rationale", "clarification_repair"]
)
def test_invalid_review_revision_fails_before_creating_destination(tmp_path, change):
    audits, raw, audit, base = _revision_fixture(tmp_path)
    if change == "identity":
        audit["authors"] = ["A different fictional author"]
    elif change == "moderate":
        audit["severity"] = audit["problems"][0]["severity"] = "moderate"
    elif change == "missing_rationale":
        del audit["impact_rationale"]
    else:
        cleared = copy.deepcopy(audit["problems"][0])
        cleared.update(
            id="p2",
            assessment="not_issue",
            severity="no_issue_found",
            repair=["A clarification only."],
        )
        audit["problems"].append(cleared)
    (audits / "0001.json").write_text(json.dumps(audit), encoding="utf-8")
    output = tmp_path / "invalid"
    with pytest.raises(ValueError):
        _builder()(base / "records", audits, raw, output, expected_count=1)
    assert not output.exists()
    assert len(load_records(base / "records")) == 1


def test_revision_does_not_copy_unregistered_private_inputs(tmp_path):
    audits, raw, _, base = _revision_fixture(tmp_path)
    private = base / "private-draft.txt"
    private.write_text("Unregistered synthetic private input.", encoding="utf-8")
    output = tmp_path / "revised"
    with pytest.raises(ValueError, match="unregistered"):
        _builder()(base / "records", audits, raw, output, expected_count=1)
    assert not output.exists()
    assert private.read_text("utf-8") == "Unregistered synthetic private input."


def test_revision_retains_verified_reader_catalog_without_reassigning_credit(tmp_path):
    from elvia.reader import record_digest

    audits, raw, _, base = _revision_fixture(tmp_path)
    record = load_records(base / "records")[0][1]
    catalog = {
        "format_version": 1,
        "cases": {
            record["case_id"]: {
                "revision": 1,
                "record_sha256": record_digest(record),
                "citation": {
                    "authors": ["Example, Alex"],
                    "title": "Synthetic article",
                    "container": "Fixture",
                    "volume": "1",
                    "year": 2026,
                    "doi": "10.1234/fixture",
                    "source_url": "https://example.org/fixture",
                },
                "contributors": [
                    {"name": "Example Person", "role": "Initial report", "revision": 1}
                ],
            }
        },
    }
    path = base / "reader-catalog.json"
    path.write_text(json.dumps(catalog), encoding="utf-8")
    output = tmp_path / "revised"
    assert _builder()(base / "records", audits, raw, output, expected_count=1) == 1
    assert (output / path.name).read_bytes() == path.read_bytes()

    catalog["cases"][record["case_id"]]["record_sha256"] = "0" * 64
    path.write_text(json.dumps(catalog), encoding="utf-8")
    with pytest.raises(ValueError, match="snapshot"):
        _builder()(
            base / "records", audits, raw, tmp_path / "invalid", expected_count=1
        )


def test_revision_copies_only_validated_snapshot_despite_later_private_file(tmp_path):
    audits, raw, _, base = _revision_fixture(tmp_path)
    module = runpy.run_path(str(SCRIPTS / "revise_review_collection.py"))
    importer = module["IMPORTER"]
    original_import = importer["import_collection"]
    private = base / "private-draft.txt"

    def concurrent_addition(*args, **kwargs):
        private.write_text("Late synthetic private draft.", encoding="utf-8")
        return original_import(*args, **kwargs)

    importer["import_collection"] = concurrent_addition
    output = tmp_path / "revised"
    module["revise_collection"](base / "records", audits, raw, output, expected_count=1)
    assert private.read_text("utf-8") == "Late synthetic private draft."
    assert not (output / private.name).exists()
    assert len(load_records(output / "records")) == 2
