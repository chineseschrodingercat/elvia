"""Statement curation is presentation, never a new scientific record."""

import copy

import pytest

from elvia.statement_catalog import prepare_statement_notes, statement_digest


@pytest.fixture
def bound_statement(valid_record):
    record = copy.deepcopy(valid_record)
    problem = {
        "id": "p1",
        "claim": ["A bounded fictional claim."],
        "assumptions": ["A verification-only parameter."],
        "analysis": ["The fictional source explicitly states its condition."],
    }
    note = {
        "revision": record["revision"],
        "report": ["Fictional report."],
        "problems": [problem],
    }
    catalog = {
        "format_version": 1,
        "cases": {
            record["case_id"]: {
                "revision": record["revision"],
                "record_sha256": statement_digest(record),
                "report_sha256": statement_digest(note["report"]),
                "problems": {
                    "p1": {
                        "problem_sha256": statement_digest(problem),
                        "paragraphs": [
                            "For every fictional x in the stated domain, "
                            "the source asserts P(x)."
                        ],
                        "basis": {"analysis": [0]},
                    }
                },
            }
        },
    }
    return record, note, catalog


def test_bound_statement_adds_only_presentation_and_preserves_inputs(bound_statement):
    record, note, catalog = bound_statement
    before = copy.deepcopy((record, note, catalog))
    prepared = prepare_statement_notes([record], {record["case_id"]: note}, catalog)
    problem = prepared[record["case_id"]]["problems"][0]
    assert (
        problem.pop("statement")
        == catalog["cases"][record["case_id"]]["problems"]["p1"]["paragraphs"]
    )
    assert prepared[record["case_id"]] == note
    assert (record, note, catalog) == before


@pytest.mark.parametrize("target", ["record", "report", "problem", "reference", "pdf"])
def test_bound_statement_rejects_source_drift(bound_statement, target):
    record, note, catalog = bound_statement
    case = catalog["cases"][record["case_id"]]
    entry = case["problems"]["p1"]
    if target == "record":
        case["record_sha256"] = "0" * 64
    elif target == "report":
        note["report"][0] += " Changed."
    elif target == "problem":
        note["problems"][0]["analysis"][0] += " Changed."
    elif target == "reference":
        entry["basis"]["analysis"] = [99]
    else:
        entry["basis"] = {"source_pdf": {"sha256": "0" * 64, "pages": [2]}}
    with pytest.raises(ValueError, match="statement presentation"):
        prepare_statement_notes([record], {record["case_id"]: note}, catalog)


def test_new_revision_does_not_inherit_old_statement(bound_statement):
    record, note, catalog = bound_statement
    record["revision"] += 1
    note["revision"] = record["revision"]
    prepared = prepare_statement_notes([record], {record["case_id"]: note}, catalog)
    assert (
        prepared[record["case_id"]]["problems"][0]["statement"]
        == note["problems"][0]["claim"]
    )
