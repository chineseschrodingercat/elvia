"""Collection ingestion and presentation regressions use synthetic fixtures."""

import copy
import hashlib
import json
import runpy
from pathlib import Path

import pytest

from elvia.records import validate_record
from elvia.storage import save_record

IMPORTER = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "scripts/import_review_collection.py")
)


@pytest.fixture
def reviewed_input(tmp_path):
    raw = tmp_path / "private-raw"
    (raw / "reports").mkdir(parents=True)
    report = raw / "reports/0001.tex"
    report.write_text("Original private synthetic fixture report.", encoding="utf-8")
    pdf = raw / "original.pdf"
    pdf.write_bytes(b"Synthetic upstream bytes, never exported.")
    problem = {
        "id": "p1",
        "title": "A scoped clarification",
        "source_location": "Fictional fixture section",
        "claim": ["A bounded claim."],
        "analysis": [r"The domain \(A:\Omega\to\Omega\) is math, not a drive."],
        "result": ["The weak reading is consistent."],
        "assumptions": [],
        "severity": "no_issue_found",
        "assessment": "not_issue",
        "repair": ["An existing clarification, not a paper repair."],
        "existing_correction_status": "No adoption.",
    }
    audit = {
        "report_id": "0001",
        "title": "Original synthetic collection fixture",
        "authors": ["Fictional fixture author"],
        "version": "Synthetic source",
        "pdf_path": str(pdf),
        "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
        "raw_report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
        "pdf_url": "https://example.org/fixture.pdf",
        "landing_url": "https://example.org/fixture",
        "retrieved_at": None,
        "provenance_note": "No source identity beyond this software fixture.",
        "severity": "no_issue_found",
        "outcome": "scope_clarification",
        "summary": "No error established in the fixture's scoped reading.",
        "review_scope": "Synthetic fixture only.",
        "limitations": ["Not research data."],
        "source_checks": [
            {"path": str(pdf), "location": "Fixture", "note": "Synthetic."}
        ],
        "problems": [problem],
    }
    audits = tmp_path / "audits"
    audits.mkdir()
    (audits / "0001.json").write_text(json.dumps(audit), encoding="utf-8")
    return audits, raw, audit


def test_import_keeps_scope_clarifications_separate_from_repairs(
    reviewed_input, tmp_path
):
    from elvia.storage import load_records

    audits, raw, _ = reviewed_input
    output = tmp_path / "collection"
    assert IMPORTER["import_collection"](audits, raw, output, expected_count=1) == 1
    record = load_records(output / "records")[0][1]
    assert record["repair"]["content"] is None
    assert record["repair"]["verification_status"] == "not_proposed"
    assert record["audit"]["retrieved_at"] is None
    assert not list(output.rglob("*.pdf"))
    assert json.loads((output / "case-notes.json").read_text("utf-8"))["cases"] == {}
    content = "".join(p.read_text("utf-8") for p in output.rglob("*") if p.is_file())
    assert str(raw) not in content
    assert "Synthetic upstream bytes" not in content
    assert "An existing clarification" in content
    assert all(b"\r\n" not in p.read_bytes() for p in output.rglob("*") if p.is_file())


def test_bad_narrative_never_leaves_a_partial_import(reviewed_input, tmp_path):
    audits, raw, audit = reviewed_input
    audit.update(outcome="candidate_issue", severity="moderate")
    audit["problems"][0].update(
        assessment="supported", severity="moderate", analysis=[]
    )
    (audits / "0001.json").write_text(json.dumps(audit), encoding="utf-8")
    output = tmp_path / "invalid-collection"
    with pytest.raises(ValueError, match="analysis"):
        IMPORTER["import_collection"](audits, raw, output, expected_count=1)
    assert not output.exists()


def test_copy_failure_removes_only_new_import(reviewed_input, tmp_path, monkeypatch):
    audits, raw, _ = reviewed_input
    output = tmp_path / "interrupted-collection"

    def interrupted_copy(source, destination, **kwargs):
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "partial.txt").write_text("Partial copy.", encoding="utf-8")
        raise OSError("injected copy failure")

    monkeypatch.setattr(IMPORTER["shutil"], "copytree", interrupted_copy)
    with pytest.raises(OSError, match="injected copy failure"):
        IMPORTER["import_collection"](audits, raw, output, expected_count=1)
    assert not output.exists()


def test_destination_race_preserves_other_actor_files(
    reviewed_input, tmp_path, monkeypatch
):
    audits, raw, _ = reviewed_input
    output = tmp_path / "raced-collection"
    original_write = IMPORTER["import_collection"].__globals__["_write_collection"]

    def competing_destination(reviewed, staging):
        count = original_write(reviewed, staging)
        output.mkdir()
        (output / "unrelated.txt").write_text("Other actor.", encoding="utf-8")
        return count

    monkeypatch.setitem(
        IMPORTER["import_collection"].__globals__,
        "_write_collection",
        competing_destination,
    )
    with pytest.raises(FileExistsError):
        IMPORTER["import_collection"](audits, raw, output, expected_count=1)
    assert (output / "unrelated.txt").read_text("utf-8") == "Other actor."


def test_latex_download_rejects_nonmathematical_commands():
    with pytest.raises(ValueError, match="non-mathematical"):
        IMPORTER["tex_text"](r"Claim \(\input{private-file}\)")


@pytest.mark.parametrize("severity", ["moderate", "minor"])
def test_v12_preserves_unknown_retrieval_and_uncertain_outcome(valid_record, severity):
    record = copy.deepcopy(valid_record)
    record.update(schema_version="1.2.0", case_type="prospective_audit")
    record["concern"]["severity"] = severity
    record["publication"]["status"] = "preliminary_ai"
    record["audit"] = {
        "venue": "Synthetic fixture",
        "year": 2025,
        "authors": ["Fixture author"],
        "landing_url": "https://example.org/fixture",
        "pdf_url": "https://example.org/fixture.pdf",
        "pdf_sha256": "a" * 64,
        "retrieved_at": None,
        "outcome": "needs_evidence",
        "summary": "Evidence is insufficient to assess the fixture claim.",
        "limitations": ["Original retrieval time is undocumented."],
    }
    assert validate_record(record) == []
    record["schema_version"] = "1.1.0"
    assert validate_record(record)


def test_dataset_reader_notes_are_snapshot_bound_and_exported(valid_record, tmp_path):
    from elvia.site import build_site

    record = copy.deepcopy(valid_record)
    record.update(schema_version="1.1.0", case_type="prospective_audit")
    record["publication"]["status"] = "preliminary_ai"
    record["audit"] = {
        "venue": "Synthetic fixture",
        "year": 2025,
        "authors": ["Fixture author"],
        "landing_url": "https://example.org/fixture",
        "pdf_url": "https://example.org/fixture.pdf",
        "pdf_sha256": "a" * 64,
        "retrieved_at": "2026-10-20T00:00:00Z",
        "outcome": "candidate_issue",
        "summary": "A scoped fixture concern.",
        "limitations": ["Software fixture."],
    }
    save_record(record, tmp_path / "records")
    canonical = json.dumps(
        record, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    problem = {
        "id": "fixture-problem",
        "title": "A fixture claim",
        "source_location": "Fixture section",
        "claim": ["A claim."],
        "analysis_heading": "Verification",
        "analysis": ["The decisive working."],
        "result": ["A bounded result."],
        "assumptions": [],
        "repair": None,
        "evidence_ids": [record["evidence"][0]["id"]],
    }
    catalog = {
        "format_version": 1,
        "cases": {
            record["case_id"]: {
                "revision": 1,
                "record_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
                "problems": [problem],
            }
        },
    }
    note_path = tmp_path / "case-notes.json"
    note_path.write_text(json.dumps(catalog), encoding="utf-8")
    build_site(tmp_path / "records", tmp_path / "site")
    payload = json.loads((tmp_path / "site/data.json").read_text("utf-8"))
    assert payload["case_notes"][record["case_id"]]["problems"] == [problem]
    catalog["cases"][record["case_id"]]["record_sha256"] = "b" * 64
    note_path.write_text(json.dumps(catalog), encoding="utf-8")
    with pytest.raises(ValueError, match="snapshot"):
        build_site(tmp_path / "records", tmp_path / "drifted-site")
    assert not (tmp_path / "drifted-site").exists()
