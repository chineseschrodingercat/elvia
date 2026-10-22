"""Explicit source refreshes preserve immutable synthetic predecessor evidence."""

import copy
import hashlib
import json
import runpy
from pathlib import Path

import pytest

from elvia.storage import load_records, save_record


def canonical_hash(record):
    return hashlib.sha256(
        json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def updated(record):
    current = copy.deepcopy(record)
    current.update(schema_version="1.3.0", revision=2, previous_revision=1)
    current["source"]["version"] = "2"
    current["source_update"] = {
        "previous_record_sha256": canonical_hash(record),
        "checked_at": "2026-10-21T06:00:00Z",
        "reason": "Recheck a newer original synthetic source.",
        "correspondence": "Both texts belong to the same original synthetic case.",
    }
    return current


def test_explicit_source_update_preserves_and_loads_both_versions(
    valid_record, tmp_path
):
    records = tmp_path / "records"
    first = save_record(valid_record, records)
    original = first.read_bytes()
    later = updated(valid_record)
    second = save_record(later, records)
    assert first.read_bytes() == original
    assert load_records(second) == [(second, later)]
    assert [r["source"]["version"] for _, r in load_records(records)] == ["1", "2"]


@pytest.mark.parametrize(
    "change",
    [
        "wrong_hash",
        "old_schema",
        "missing_transition",
        "human_review",
        "decision",
        "adoption",
        "case_type",
    ],
)
def test_source_update_cannot_bypass_history_or_inherit_decisions(
    valid_record, human_review, tmp_path, change
):
    records = tmp_path / "records"
    first = save_record(valid_record, records)
    original = first.read_bytes()
    later = updated(valid_record)
    if change == "wrong_hash":
        later["source_update"]["previous_record_sha256"] = "0" * 64
    elif change == "old_schema":
        later["schema_version"] = "1.2.0"
    elif change == "missing_transition":
        del later["source_update"]
    elif change == "human_review":
        later["human_reviews"] = [human_review]
    elif change == "decision":
        later["adjudication"]["status"] = "unresolved"
    elif change == "adoption":
        later["repair"]["adoption_status"] = "requested"
    else:
        later["case_type"] = "prospective_audit"
    with pytest.raises(ValueError):
        save_record(later, records)
    assert first.read_bytes() == original
    assert len(list(records.glob("*.json"))) == 1


def builder():
    path = Path(__file__).resolve().parents[1] / "scripts/refresh_review_collection.py"
    return runpy.run_path(str(path))["refresh_collection"]


def test_source_update_hash_is_checked_when_loading_existing_files(
    valid_record, tmp_path
):
    records = tmp_path / "records"
    save_record(valid_record, records)
    later = updated(valid_record)
    later["source_update"]["previous_record_sha256"] = "f" * 64
    path = records / "synthetic-001.r2.json"
    path.write_text(json.dumps(later), encoding="utf-8")
    with pytest.raises(ValueError, match="predecessor record hash"):
        load_records(path)


def test_cleared_source_refresh_removes_stale_detailed_note(tmp_path):
    from test_review_revision import _revision_fixture

    audits, raw, audit, base = _revision_fixture(tmp_path)
    audit.update(severity="no_issue_found", outcome="no_issue_found")
    audit["problems"][0].update(
        assessment="not_issue",
        severity="no_issue_found",
        repair=[],
        impact_rationale="The current original synthetic source fixes the old defect.",
    )
    (audits / "0001.json").write_text(json.dumps(audit), encoding="utf-8")
    output = tmp_path / "cleared"
    builder()(base / "records", audits, raw, output, expected_count=1)
    latest = load_records(output / "records")[-1][1]
    assert latest["audit"]["outcome"] == "no_issue_found"
    assert json.loads((output / "case-notes.json").read_text("utf-8"))["cases"] == {}
    assert latest["repair"]["content"] is None


def test_refresh_validates_actual_captured_assessment_after_late_input_change(tmp_path):
    from test_review_revision import _revision_fixture

    audits, raw, audit, base = _revision_fixture(tmp_path)
    path = Path(__file__).resolve().parents[1] / "scripts/refresh_review_collection.py"
    module = runpy.run_path(str(path))
    original = module["IMPORTER"]["import_collection"]

    def substitute(*args, **kwargs):
        audit["problems"][0]["impact_rationale"] = " "
        (audits / "0001.json").write_text(json.dumps(audit), encoding="utf-8")
        return original(*args, **kwargs)

    module["IMPORTER"]["import_collection"] = substitute
    output = tmp_path / "unsafe"
    with pytest.raises(ValueError, match="individual impact rationale"):
        module["refresh_collection"](
            base / "records", audits, raw, output, expected_count=1
        )
    assert not output.exists()


def test_partial_source_refresh_keeps_other_cases_and_all_predecessors(tmp_path):
    from test_review_append import _fixture, _module

    existing, incoming, raw, audit = _fixture(tmp_path)
    combined = tmp_path / "combined"
    _module()["append_collection"](
        existing / "records", incoming, raw, combined, expected_count=1
    )
    before = {
        p.relative_to(combined).as_posix(): p.read_bytes()
        for p in combined.rglob("*")
        if p.is_file()
    }
    pdf = raw / "latest.pdf"
    pdf.write_bytes(b"Newer original synthetic source bytes.")
    audit.update(
        title="Updated title of the second fictional paper",
        version="Latest synthetic version",
        pdf_path=str(pdf),
        pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
    )
    audit["source_checks"] = [
        {
            "path": str(pdf),
            "location": "Synthetic source",
            "note": "Same original fictional work, newer version.",
        }
    ]
    (incoming / "0002.json").write_text(json.dumps(audit), encoding="utf-8")
    output = tmp_path / "refreshed"
    assert builder()(combined / "records", incoming, raw, output, expected_count=1) == 1
    entries = load_records(output / "records")
    assert len(entries) == 4
    current = {r["case_id"]: r for _, r in entries}
    assert len(current) == 2
    newest = next(r for r in current.values() if "0002" in r["case_id"])
    prior = next(
        r
        for _, r in load_records(combined / "records")
        if r["case_id"] == newest["case_id"]
    )
    assert newest["revision"] == 2
    assert newest["source_update"]["previous_record_sha256"] == canonical_hash(prior)
    assert newest["source"]["title"] == audit["title"]
    assert newest["audit"]["pdf_sha256"] == audit["pdf_sha256"]
    assert newest["source"]["artifact"] != prior["source"]["artifact"]
    assert newest["adjudication"]["status"] == "pending"
    assert newest["human_reviews"] == []
    assert "Issue #27" in newest["publication"]["note"]
    for name, data in before.items():
        if name != "case-notes.json":
            assert (output / name).read_bytes() == data
    assert before == {
        p.relative_to(combined).as_posix(): p.read_bytes()
        for p in combined.rglob("*")
        if p.is_file()
    }
    assert not list(output.rglob("*.pdf"))
    catalog = json.loads((output / "case-notes.json").read_text("utf-8"))["cases"]
    assert catalog[newest["case_id"]]["record_sha256"] == canonical_hash(newest)


@pytest.mark.parametrize("collision", ["title", "pdf"])
def test_source_refresh_cannot_replace_a_case_with_another_existing_paper(
    tmp_path, collision
):
    from test_review_append import _fixture, _module

    existing, incoming, raw, audit = _fixture(tmp_path)
    combined = tmp_path / "combined"
    _module()["append_collection"](
        existing / "records", incoming, raw, combined, expected_count=1
    )
    other = next(
        r for _, r in load_records(combined / "records") if "0001" in r["case_id"]
    )
    if collision == "title":
        audit["title"] = other["source"]["title"].upper() + " "
    else:
        audit["pdf_path"] = str(raw / "original.pdf")
        audit["pdf_sha256"] = other["audit"]["pdf_sha256"]
    (incoming / "0002.json").write_text(json.dumps(audit), encoding="utf-8")
    output = tmp_path / "duplicate"
    with pytest.raises(ValueError, match="duplicate"):
        builder()(combined / "records", incoming, raw, output, expected_count=1)
    assert not output.exists()
