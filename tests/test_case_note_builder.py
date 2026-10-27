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


@pytest.mark.parametrize(
    "method",
    ["Exact symbolic verification.", ["Analytic proof.", "Static source check."]],
)
def test_source_method_is_retained_without_mutating_scientific_snapshots(method):
    from elvia.case_notes import prepare_case_notes

    original = records()
    before = copy.deepcopy(original)
    notes_catalog = catalog()
    identifier = next(iter(notes_catalog["cases"]))
    notes_catalog["cases"][identifier]["problems"][0]["method"] = method
    selected = prepare_case_notes(original, catalog=notes_catalog)
    assert selected[identifier]["problems"][0]["method"] == method
    assert original == before


@pytest.mark.parametrize("method", ["", "  ", [], [""], ["Exact check.", 3], {}, 1])
def test_source_method_rejects_non_readable_or_structured_payloads(method):
    from elvia.case_notes import prepare_case_notes

    notes_catalog = catalog()
    identifier = next(iter(notes_catalog["cases"]))
    notes_catalog["cases"][identifier]["problems"][0]["method"] = method
    with pytest.raises(ValueError, match="case note.*method"):
        prepare_case_notes(records(), catalog=notes_catalog)


@pytest.mark.parametrize(
    "fault",
    [
        None,
        "text",
        "locator",
        "source_identity",
        "source_sha256",
        "wrong_pdf",
        "not_list",
    ],
)
def test_source_quotes_require_readable_original_text_and_exact_pdf_identity(fault):
    from elvia.case_notes import prepare_case_notes

    original = records()
    notes_catalog = catalog()
    identifier = next(iter(notes_catalog["cases"]))
    record = next(record for record in original if record["case_id"] == identifier)
    quote = {
        "text": "A synthetic source quotation.",
        "locator": "Page 2, Theorem 1",
        "source_identity": "Original paper, frozen proceedings PDF",
        "source_sha256": record["audit"]["pdf_sha256"],
    }
    if fault in quote:
        quote[fault] = ""
    elif fault == "wrong_pdf":
        quote["source_sha256"] = "0" * 64
    notes_catalog["cases"][identifier]["source_quotes"] = (
        quote if fault == "not_list" else [quote]
    )
    if fault is None:
        assert prepare_case_notes(original, catalog=notes_catalog)[identifier][
            "source_quotes"
        ] == [quote]
    else:
        with pytest.raises(ValueError, match="case note.*source quote"):
            prepare_case_notes(original, catalog=notes_catalog)


@pytest.mark.parametrize(
    "outcome", ["no_issue_found", "scope_clarification", "candidate_issue"]
)
def test_only_nonproblem_records_can_have_quote_only_notes(valid_record, outcome):
    from elvia.case_notes import prepare_case_notes

    record = copy.deepcopy(valid_record)
    record["audit"] = {"outcome": outcome, "pdf_sha256": "a" * 64}
    note = {
        "revision": record["revision"],
        "record_sha256": hashlib.sha256(
            json.dumps(
                record, sort_keys=True, separators=(",", ":"), ensure_ascii=True
            ).encode()
        ).hexdigest(),
        "problems": [],
        "source_quotes": [
            {
                "text": "A complete synthetic source sentence.",
                "locator": "Abstract, PDF p. 1",
                "source_identity": "Synthetic original PDF",
                "source_sha256": "a" * 64,
            }
        ],
    }
    source = {"format_version": 1, "cases": {record["case_id"]: note}}
    if outcome == "candidate_issue":
        with pytest.raises(ValueError, match="case note.*problem"):
            prepare_case_notes([record], catalog=source)
    else:
        assert prepare_case_notes([record], catalog=source)[record["case_id"]] == note


def test_builder_exports_selected_notes_without_rewriting_records(tmp_path):
    from elvia.site import build_site

    output = tmp_path / "atlas"
    assert build_site(ROOT / "studies/neurips2025/records", output) == 300
    payload = json.loads((output / "data.json").read_text("utf-8"))
    assert len(payload["case_notes"]) == len(catalog()["cases"])
    assert payload["records"] == records()
    assert (output / "case-note.js").is_file()
    html = (output / "index.html").read_text("utf-8")
    assert html.index('src="math.js"') < html.index('src="case-note.js"')
    assert html.index('src="case-note.js"') < html.index('src="atlas.js"')
