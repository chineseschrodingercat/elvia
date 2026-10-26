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


def test_alternate_finding_schema_maps_source_conditions_and_remedy():
    convert = importer()["normalize_problem"]
    item = {
        "claim": "The fictional increment is bounded by the displayed expression.",
        "locations": ["Synthetic Appendix F, Equation (169)", "Synthetic page 24"],
        "evidence": (
            "At the synthetic input, the left side is 4 and the right side is 2."
        ),
        "counterevidence": (
            "The restricted synthetic example still satisfies the bound."
        ),
        "core_dependency": "Only the displayed synthetic estimate is inspected.",
        "hypotheses": ["The fictional input is positive."],
        "remedy": "Retain the original unsimplified synthetic expression.",
        "unexpected_scientific_field": {"finite_control": [3, 7]},
        "status": "pending",
    }
    p = convert(item, 1)
    assert p["title"] == item["claim"]
    assert all(location in p["source_location"] for location in item["locations"])
    assert p["assumptions"] == item["hypotheses"]
    assert p["repair"]["paragraphs"] == [item["remedy"]]
    assert any(item["evidence"] in text for text in p["result"])
    assert any(item["counterevidence"] in text for text in p["result"])
    assert any("Finite control" in text and "3" in text for text in p["analysis"])
    assert p["result"] != ["Status: pending"]


def test_retained_problem_heading_supplies_title_without_reinterpreting_the_claim():
    convert = importer()["normalize_problem"]
    report = [
        "# Corrections in the synthetic argument",
        "Problem 1 (Minor: a fictional bound omits the condition (A)). "
        "Original synthetic source paragraph and finite check.",
        "## 4. Problem 2 — A fictional second denominator",
    ]
    item = {"claim": "Original synthetic claim.", "source_locations": ["Equation (1)"]}
    assert convert(item, 1, report=report)["title"] == (
        "a fictional bound omits the condition (A)"
    )
    assert convert(item, 2, report=report)["title"] == "A fictional second denominator"


def test_explicit_decisive_finding_beats_machine_status_and_keeps_unknown_evidence():
    convert = importer()["normalize_problem"]
    p = convert(
        {
            "issue_title": "An original synthetic short title",
            "paper_location": "Synthetic Theorem 2",
            "claim_under_review": "The original synthetic universal claim.",
            "result": "supported",
            "decisive_finding": "The finite synthetic case gives a nonzero remainder.",
            "counterevidence": "The separate equality case remains valid.",
            "proposed_repair": (
                "Restrict the synthetic proposition to the equality case."
            ),
            "status": "pending",
            "custom_diagnostic": "Retain this original diagnostic too.",
        },
        1,
    )
    assert p["title"] == "An original synthetic short title"
    assert p["source_location"] == "Synthetic Theorem 2"
    assert p["claim"] == ["The original synthetic universal claim."]
    assert any("nonzero remainder" in text for text in p["result"])
    assert not any(
        text in {"Result: supported", "Status: pending"} for text in p["result"]
    )
    assert any("original diagnostic" in text for text in p["analysis"])
    assert p["repair"]["paragraphs"] == [
        "Restrict the synthetic proposition to the equality case."
    ]


def test_nested_explicit_source_references_and_implementation_locations_are_retained():
    convert = importer()["normalize_problem"]
    p = convert(
        {
            "claim": "An original synthetic source claim.",
            "implementation_location": "Synthetic reader.py lines 4–9",
            "evidence": {"source_locations": ["Synthetic Appendix A, Equation (3)"]},
            "acceptance_check": {"source_references": ["papers/fictional.pdf, page 2"]},
        },
        1,
    )
    for location in (
        "Synthetic reader.py lines 4–9",
        "Synthetic Appendix A, Equation (3)",
        "papers/fictional.pdf, page 2",
    ):
        assert location in p["source_location"]
    assert any("Synthetic Appendix A" in text for text in p["analysis"])


@pytest.mark.parametrize(
    "repair",
    [
        {
            "verification": "Finite check only",
            "runtime_reproduction": "not performed",
            "adoption": "not requested",
            "full_protocol_verified": False,
        },
        "No repair proposed",
        "not_proposed",
        {
            "status": "already_corrected",
            "statement": "An earlier source changed the sign.",
        },
    ],
)
def test_repair_metadata_or_historical_correction_is_not_a_new_proposal(repair):
    convert = importer()["normalize_problem"]
    p = convert({"title": "Synthetic boundary", "repair": repair}, 1)
    assert p["repair"] is None
    assert any("Repair" in text for text in p["analysis"])


def test_substantive_repair_statement_keeps_verification_metadata_in_analysis():
    convert = importer()["normalize_problem"]
    p = convert(
        {
            "title": "Synthetic correction",
            "repair": {
                "statement": "Restrict the fictional input to positive values.",
                "verification": "A finite synthetic diagnostic only.",
                "adoption": "not requested",
                "full_protocol_verified": False,
            },
        },
        1,
    )
    assert p["repair"]["paragraphs"] == [
        "Restrict the fictional input to positive values."
    ]
    assert any("finite synthetic diagnostic" in text for text in p["analysis"])
    assert any("Full protocol verified: False" in text for text in p["analysis"])


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
