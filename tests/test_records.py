import copy

import pytest

from elvia.records import validate_record as validate


def test_complete_original_fixture(valid_record, tmp_path):
    assert validate(valid_record, tmp_path) == []


@pytest.mark.parametrize(
    "field",
    [
        "source",
        "proposition",
        "concern",
        "evidence",
        "runs",
        "human_reviews",
        "adjudication",
        "repair",
        "publication",
    ],
)
def test_required_explicit_fields(valid_record, field):
    del valid_record[field]
    assert any(field in error for error in validate(valid_record))


def test_null_unknown_identifiers_are_valid(valid_record):
    assert validate(valid_record) == []
    valid_record["source"]["identifier_note"] = ""
    assert any("identifier_note" in error for error in validate(valid_record))


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema_version", "2.0.0"),
        ("revision", 0),
        ("case_id", "../escape"),
        ("created_at", "yesterday"),
        ("created_at", "20261019T000000Z"),
    ],
)
def test_invalid_metadata(valid_record, field, value):
    valid_record[field] = value
    assert any(field in error for error in validate(valid_record))


def test_all_useful_located_errors(valid_record):
    valid_record["source"]["title"] = None
    valid_record["repair"]["adoption_status"] = "accepted"
    errors = validate(valid_record)
    assert any("$.source.title" in error for error in errors)
    assert any("$.repair.adoption_status" in error for error in errors)


def test_ai_output_is_not_human_confirmation(valid_record):
    valid_record["adjudication"]["status"] = "confirmed"
    assert any("human_reviews" in error for error in validate(valid_record))


def test_major_confirmation_requires_two_distinct_declarations(
    valid_record, human_review
):
    valid_record.update(revision=2, previous_revision=1)
    valid_record["adjudication"]["status"] = "confirmed"
    valid_record["human_reviews"] = [human_review]
    assert validate(valid_record)
    second = copy.deepcopy(human_review)
    second["reviewer_id"] = "synthetic-reviewer-b"
    valid_record["human_reviews"].append(second)
    assert validate(valid_record) == []
    second["independent"] = False
    assert any("human_reviews" in error for error in validate(valid_record))


@pytest.mark.parametrize("field", ["revision", "previous_revision"])
def test_revision_numbers_require_python_integers(valid_record, field):
    if field == "previous_revision":
        valid_record.update(revision=2, previous_revision=1)
    valid_record[field] = 1.0
    assert any(f"$.{field}" in error for error in validate(valid_record))


@pytest.mark.parametrize("decision", ["confirmed", "rejected", "unresolved"])
def test_initial_ai_finding_must_remain_pending(valid_record, human_review, decision):
    valid_record["adjudication"]["status"] = decision
    human_review["decision"] = decision
    second = copy.deepcopy(human_review)
    second["reviewer_id"] = "synthetic-reviewer-b"
    valid_record["human_reviews"] = [human_review, second]
    assert any("$.adjudication.status" in error for error in validate(valid_record))


def test_duplicate_reviewer_identity_rejected(valid_record, human_review):
    valid_record["human_reviews"] = [human_review, copy.deepcopy(human_review)]
    assert any("reviewer_id" in error for error in validate(valid_record))


def test_human_rationale_and_evidence_refs_required(valid_record, human_review):
    valid_record["human_reviews"] = [human_review]
    human_review["rationale"] = " "
    human_review["evidence_refs"] = ["unknown"]
    errors = validate(valid_record)
    assert any("rationale" in error for error in errors)
    assert any("evidence_refs" in error for error in errors)


@pytest.mark.parametrize(
    "section,field,value",
    [
        ("adjudication", "status", "verified"),
        ("repair", "verification_status", "accepted"),
        ("repair", "adoption_status", "verified"),
        ("publication", "status", "signed"),
    ],
)
def test_statuses_are_separate(valid_record, section, field, value):
    valid_record[section][field] = value
    assert any(field in error for error in validate(valid_record))


@pytest.mark.parametrize("value", [{}, []])
@pytest.mark.parametrize(
    "section,field", [("adjudication", "status"), ("concern", "severity")]
)
def test_malformed_enum_types_return_located_errors(
    valid_record, section, field, value
):
    valid_record.update(revision=2, previous_revision=1)
    valid_record["adjudication"]["status"] = "confirmed"
    valid_record[section][field] = value
    errors = validate(valid_record)
    assert any(error.startswith(f"$.{section}.{field}:") for error in errors)


def test_verified_repair_requires_content_and_references(valid_record):
    valid_record["repair"]["verification_status"] = "verified"
    assert any("repair" in error for error in validate(valid_record))


@pytest.mark.parametrize(
    "path", ["../outside.txt", "/absolute.txt", "C:/absolute.txt", "..\\outside.txt"]
)
def test_artifact_escape_rejected_without_io(valid_record, path):
    valid_record["source"]["artifact"]["path"] = path
    assert any("source.artifact.path" in error for error in validate(valid_record))


def test_artifact_hash_is_verified(valid_record, tmp_path):
    (tmp_path / "evidence.txt").write_text("Changed", encoding="utf-8")
    assert any(
        "evidence[0].artifact.sha256" in error
        for error in validate(valid_record, tmp_path)
    )


def test_missing_artifact_and_invalid_hash(valid_record, tmp_path):
    valid_record["source"]["artifact"]["sha256"] = "bad"
    (tmp_path / "evidence.txt").unlink()
    errors = validate(valid_record, tmp_path)
    assert any("source.artifact.sha256" in error for error in errors)
    assert any("evidence[0].artifact.path" in error for error in errors)


def test_null_run_model_needs_explanation(valid_record):
    valid_record["runs"] = [
        {
            "id": "run-1",
            "tool": "python",
            "tool_version": "3.13",
            "model": None,
            "model_note": None,
            "config_version": "demo-v1",
            "started_at": "2026-10-19T00:00:00Z",
            "ended_at": "2026-10-19T00:00:01Z",
            "output_artifacts": [valid_record["evidence"][0]["artifact"]],
            "cost_usd": 0,
        }
    ]
    assert any("model_note" in error for error in validate(valid_record))
    valid_record["runs"][0]["model_note"] = "No model used; local exact arithmetic."
    assert validate(valid_record) == []
    valid_record["runs"][0]["ended_at"] = "2026-10-19t00:00:01z"
    assert validate(valid_record) == []


@pytest.mark.parametrize("cost", [float("nan"), float("inf")])
def test_run_cost_must_be_finite(valid_record, cost):
    valid_record["runs"] = [
        {
            "id": "run-1",
            "tool": "python",
            "tool_version": "3.13",
            "model": None,
            "model_note": "No model used.",
            "config_version": "demo-v1",
            "started_at": "2026-10-19T00:00:00Z",
            "ended_at": "2026-10-19T00:00:01Z",
            "output_artifacts": [valid_record["evidence"][0]["artifact"]],
            "cost_usd": cost,
        }
    ]
    assert any("cost_usd" in error for error in validate(valid_record))
