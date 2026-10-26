"""Publication formatting tests use fictional data, without scientific review."""

import runpy
from pathlib import Path

import pytest


def importer():
    return runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "scripts/import_icml_batches.py")
    )


def test_rating_preserves_unresolved_and_no_issue_scopes():
    rating = importer()["paper_rating"]
    assert rating({"assessment": "Needs Evidence"}) == "needs_evidence"
    assert (
        rating(
            {
                "supported_severity": None,
                "inspection_outcome": "No Issue Found within inspected scope",
            }
        )
        == "no_issue_found"
    )
    assert rating({"supported_severity": {"Major": 2, "Minor": 0}}) == "major"
    with pytest.raises(ValueError, match="rating"):
        rating({"summary": "There may be an issue"})


def test_public_metadata_drops_control_tokens_and_local_paths():
    clean = importer()["public_data"](
        {
            "batch_token": "private-token",
            "task_id": "private-task",
            "check": "A bounded calculation.",
            "repair": {"statement": "Keep the boundary", "adoption": "unknown"},
            "evidence": [r"D:\private\source.txt"],
        }
    )
    assert "batch_token" not in clean and "task_id" not in clean
    assert clean["check"] == "A bounded calculation."
    assert clean["repair"]["adoption"] == "unknown"
    assert "D:" not in str(clean)


def test_mathematical_domains_are_preserved_during_path_redaction():
    public = importer()["public_text"]
    text = r"For \(x\in C:\left\lVert x\right\rVert\le R\), keep the domain."
    assert public(text) == text
    assert "\\[internal" not in public(r"archive\chat-0001.json")


def test_scientific_tokens_and_training_checkpoints_are_not_operational_metadata():
    clean = importer()["public_data"]
    scientific = {
        "assumptions": {"tokens": [0, 1], "token_overlap": 0.5},
        "counterexample": {"eq12_first_token_0": 3},
        "finite_example": {"scores_checkpoint_by_dataset": [0.2, 0.4]},
        "focused_correction": {"token": "a mathematical token"},
        "check": {"process_id": "P1"},
    }
    assert clean(scientific) == scientific


def test_acceptance_scope_and_scientific_changes_survive_identifier_redaction():
    clean = importer()["public_data"]
    item = {
        "acceptance_check": {
            "scope": "Only the local repair is checked.",
            "token": "981a190e-1762-415e-bba1-d6a9c268f039",
        },
        "independent_acceptance_changes": ["The other inequality stays Minor."],
    }
    result = clean(item)
    assert result["acceptance_check"]["scope"] == item["acceptance_check"]["scope"]
    assert (
        result["independent_acceptance_changes"]
        == item["independent_acceptance_changes"]
    )
    assert "981a190e" not in str(result)


def test_problem_conversion_retains_counterevidence_without_upgrading_status():
    convert = importer()["normalize_problem"]
    p = convert(
        {
            "title": "A local concern",
            "assessment": "Needs Evidence",
            "source_claim": "A claim",
            "location": "Section 2",
            "check": "A finite check",
            "counterevidence": "A restriction",
            "impact": "Historical effect unknown",
            "repair": None,
        },
        1,
    )
    assert p["assessment"] == "needs_evidence"
    assert p["severity"] == "needs_evidence"
    assert any("A restriction" in s for s in p["analysis"])
    assert p["repair"] is None


def test_finding_paragraph_order_is_explicit():
    convert = importer()["normalize_problem"]
    finding = {"result": "A finding", "impact": "A bounded impact"}
    assert convert(finding, 1)["result"] == [
        "Result: A finding",
        "Impact: A bounded impact",
    ]


def test_selected_batches_cannot_silently_expand_to_other_papers():
    select = importer()["select_metadata"]
    rows = [
        {
            "No.": str(n),
            "Batch": "B001" if n <= 100 else "B005",
            "Paper ID": f"fixture-{n}",
            "Title": f"Fictional paper {n}",
        }
        for n in range(1, 501)
    ]
    with pytest.raises(ValueError, match="400"):
        select(rows)
