"""Mechanical metadata collection; synthetic assertions are not scientific review."""

import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def collect():
    path = Path(__file__).resolve().parents[1] / "scripts/icml_metadata.py"
    spec = importlib.util.spec_from_file_location("icml_metadata", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.collect_limits


def test_nested_ledger_limits_and_missing_work_are_preserved_with_context(collect):
    findings = {
        "findings": [
            {
                "id": "F1",
                "title": "A synthetic finding",
                "claim": "Every admissible input passes.",
                "limitations": [r"Only the finite check \(n=10\) was performed."],
                "counterevidence": "The separate prediction claim survives this check.",
                "repair": {
                    "not_verified": "A complete corrected protocol was not verified."
                },
                "acceptance_check": {
                    "checks": {"counterevidence": True},
                    "scope": "All artifacts passed.",
                },
            }
        ]
    }
    coverage = {
        "ledger": [
            {
                "title": "Static source check",
                "limits": "The historical executable was unavailable.",
                "scope": "The local identity is verified.",
            }
        ],
        "missing_materials": ["Per-seed predictions"],
        "not_performed": ["Model retraining"],
        "scope_limitations": ["Only the inspected source version was checked."],
        "unresolved_claims": [
            {
                "id": "U1",
                "claim": "Accuracy must improve.",
                "description": "Empirical impact remains unresolved.",
                "accepted": True,
            }
        ],
    }
    values = collect(findings, coverage)
    text = "\n".join(values)
    for expected in (
        r"Only the finite check \(n=10\) was performed.",
        "The separate prediction claim survives this check.",
        "A complete corrected protocol was not verified.",
        "The historical executable was unavailable.",
        "Per-seed predictions",
        "Model retraining",
        "Only the inspected source version was checked.",
        "Empirical impact remains unresolved.",
        "Static source check",
        "F1",
    ):
        assert expected in text
    for excluded in (
        "Every admissible",
        "Accuracy must improve",
        "All artifacts passed",
        "local identity is verified",
        "True",
    ):
        assert excluded not in text


def test_bools_numbers_and_opaque_positive_fields_never_become_limits(collect):
    findings = {
        "counterevidence": True,
        "limitations": {
            "claim": "The theorem is correct",
            "result": "Check succeeded",
            "accepted": True,
        },
    }
    coverage = {
        "limits": 10,
        "missing_materials": [False, 4, None],
        "not_performed": False,
        "scope": "The full proof is verified.",
    }
    assert collect(findings, coverage) == []


def test_historical_metadata_and_acceptance_flags_do_not_reappear_as_current_limits(
    collect,
):
    findings = {
        "history": [{"limitations": ["An obsolete limitation"]}],
        "initial_review_artifact_metadata": {
            "values": {"not_performed": ["Already completed work"]}
        },
    }
    coverage = {
        "independent_acceptance_scope": {
            "original_full_review_not_repeated": True,
            "limits": "This focused check did not repeat the full scientific review.",
        }
    }
    values = collect(findings, coverage)
    assert len(values) == 1
    assert "This focused check did not repeat" in values[0]


def test_collection_is_deterministic_deduplicated_and_keeps_math_case(collect):
    data = {"limitations": ["Bound A", "Bound A", "Bound a", "none", "N/A", True]}
    assert collect(data, {}) == collect(data, {})
    values = collect(data, {})
    assert len(values) == 2
    assert values[0].endswith("Bound A") and values[1].endswith("Bound a")


def test_structured_unresolved_fields_collect_reasons_without_promoting_claims(collect):
    data = {
        "unresolved": [
            {
                "title": "A question",
                "claim": "All models fail.",
                "reason": "The required source dataset is missing.",
                "status": "pending",
                "counterevidence": ["A valid control survives."],
            }
        ]
    }
    text = "\n".join(collect(data, {}))
    assert "The required source dataset is missing." in text
    assert "A valid control survives." in text
    assert "All models fail" not in text
    assert "pending" not in text
