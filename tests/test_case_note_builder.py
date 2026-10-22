"""Reader narratives must match the immutable scientific snapshot they explain."""

import copy
import hashlib
import json
from pathlib import Path

import pytest

from elvia.storage import load_records

ROOT = Path(__file__).resolve().parents[1]


def catalog():
    return json.loads((ROOT / "studies/neurips2025/case-notes.json").read_text("utf-8"))


def records():
    return [r for _, r in load_records(ROOT / "studies/neurips2025/records")]


def test_reader_notes_are_bound_to_exact_revision_and_snapshot():
    from elvia.case_notes import prepare_case_notes

    original = records()
    unchanged = copy.deepcopy(original)
    notes = prepare_case_notes(original, catalog=catalog())
    assert set(notes) == set(catalog()["cases"])
    assert original == unchanged
    original[0]["proposition"]["claim"] += " Changed test fixture."
    with pytest.raises(ValueError, match="case note.*snapshot"):
        prepare_case_notes(original, catalog=catalog())


def test_future_revision_does_not_inherit_reader_narrative(valid_record):
    from elvia.case_notes import prepare_case_notes

    record = records()[0]
    record["revision"] += 1
    assert prepare_case_notes([record, valid_record], catalog=catalog()) == {}


@pytest.mark.parametrize("fault", ["evidence", "repair", "duplicate_problem"])
def test_inconsistent_narrative_is_rejected(fault):
    from elvia.case_notes import prepare_case_notes

    original = records()
    notes_catalog = catalog()
    record = next(r for r in original if r["case_id"] in notes_catalog["cases"])
    if fault == "repair":
        record["repair"]["content"] = None
        notes_catalog["cases"][record["case_id"]]["record_sha256"] = hashlib.sha256(
            json.dumps(
                record, sort_keys=True, separators=(",", ":"), ensure_ascii=True
            ).encode()
        ).hexdigest()
    note = notes_catalog["cases"][record["case_id"]]
    problem = note["problems"][0]
    if fault == "evidence":
        problem["evidence_ids"].append("nonexistent-evidence-test-fixture")
    elif fault == "repair":
        problem["repair"] = {"heading": "Invented repair", "paragraphs": ["Invalid."]}
    else:
        note["problems"].append(copy.deepcopy(problem))
    with pytest.raises(ValueError, match="case note"):
        prepare_case_notes(original, catalog=notes_catalog)


def test_builder_exports_selected_notes_without_rewriting_records(tmp_path):
    from elvia.site import build_site

    output = tmp_path / "atlas"
    assert build_site(ROOT / "studies/neurips2025/records", output) == 300
    payload = json.loads((output / "data.json").read_text("utf-8"))
    assert len(payload["case_notes"]) == 284
    assert payload["records"] == records()
    assert (output / "case-note.js").is_file()
    html = (output / "index.html").read_text("utf-8")
    assert html.index('src="math.js"') < html.index('src="case-note.js"')
    assert html.index('src="case-note.js"') < html.index('src="atlas.js"')
