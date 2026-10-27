"""Publication formatting tests use fictional data, without scientific review."""

import hashlib
import json
import runpy
from pathlib import Path

import pytest


def importer():
    return runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "scripts/import_icml_batches.py")
    )


def test_legacy_report_cache_cannot_hide_source_locators(tmp_path):
    module = importer()
    raw = tmp_path / "raw"
    batch = raw / "batch_B001"
    files = {
        "papers/0004/0004.pdf": b"%PDF-fixture source",
        "reports/Pdf/0004.pdf": b"%PDF-fixture report",
        "reports/0004.tex": b"In \\path{src/evaluate.py}, lines 1--4.",
    }
    for relative, data in files.items():
        path = batch / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    title = "Fictional source-locator fixture"
    findings = {"paper_id": "I25-FIXTURE", "title": title}
    evidence = batch / "verification/0004"
    evidence.mkdir(parents=True)
    for name, value in {
        "findings.json": findings,
        "coverage.json": {},
        "provenance.json": {
            "source": hashlib.sha256(files["papers/0004/0004.pdf"]).hexdigest()
        },
    }.items():
        (evidence / name).write_text(json.dumps(value), encoding="utf-8")
    cache = tmp_path / "cache"
    cache.mkdir()
    tex_hash = hashlib.sha256(files["reports/0004.tex"]).hexdigest()
    (cache / (tex_hash + ".json")).write_text(
        json.dumps([title, "In , lines 1–4."]), encoding="utf-8"
    )
    calls = []

    def parse(path, *, pandoc):
        calls.append(path)
        return [title, "In `src/evaluate.py`, lines 1–4."]

    prepared = module["prepare_input"](
        {"No.": 4, "Batch": "B001", "Paper ID": "I25-FIXTURE", "Title": title},
        raw,
        parse,
        "fixture-pandoc",
        cache=cache,
    )
    assert calls == [batch / "reports/0004.tex"]
    assert prepared[-1][-1] == "In `src/evaluate.py`, lines 1–4."


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


def test_inspection_subject_does_not_become_an_unrecorded_paper_assertion():
    convert = importer()["normalize_problem"]
    check = "The fictional release has no identified historical execution trace."
    p = convert({"title": "Historical trace check", "check": check}, 1)
    assert p["claim_heading"] == "Inspection subject recorded in the report"
    assert p["claim"] == ["Recorded check: " + check]
    assert all("See the source claim" not in text for text in p["claim"])
    assert "Historical trace check" in p["source_location"]


def test_nested_source_claim_keeps_the_paper_assertion_label():
    convert = importer()["normalize_problem"]
    claim = "The fictional paper states a positive-input bound."
    p = convert({"title": "Synthetic claim", "source": {"claim": claim}}, 1)
    assert p["claim_heading"] == "Claim in the source (paraphrase)"
    assert p["claim"] == [claim]


def test_witness_only_result_is_recorded_evidence_with_its_original_conditions():
    convert = importer()["normalize_problem"]
    p = convert(
        {
            "title": "Synthetic scalar conversion",
            "witness": {
                "input": 0.5,
                "output": 3.7,
                "assumptions": "Positive input and fixed synthetic scaling only.",
            },
        },
        2,
    )
    assert any("Recorded evidence" in text and "3.7" in text for text in p["result"])
    assert any("Positive input" in text for text in p["assumptions"])
    assert not any("No separate finding" in text for text in p["result"])
    assert all("See the retained report" not in text for text in p["analysis"])


def test_optional_claim_heading_must_be_readable_text(valid_record):
    from elvia.case_notes import prepare_case_notes
    from elvia.reader import record_digest

    p = importer()["normalize_problem"]({"title": "A synthetic inspection"}, 1)
    p["claim_heading"] = 5
    p["evidence_ids"] = ["ev-1"]
    note = {
        "revision": 1,
        "record_sha256": record_digest(valid_record),
        "problems": [p],
    }
    with pytest.raises(ValueError, match="claim_heading"):
        prepare_case_notes(
            [valid_record],
            catalog={"format_version": 1, "cases": {valid_record["case_id"]: note}},
        )


def test_descriptive_judgment_and_complex_headline_are_complete_in_analysis():
    convert = importer()["normalize_problem"]
    item = {
        "title": "A fictional display title",
        "judgment": "Major only under the literal synthetic exponent class",
        "headline": {
            "reported": "Synthetic rates are 90.0 and 95.3 percent.",
            "actual_metric": "Synthetic non-event rate, not a reduction.",
            "values": [90.0, 95.3],
            "scope": "Keep the two fictional baselines separate.",
        },
    }
    p = convert(item, 1)
    rendered = "\n".join(p["analysis"])
    assert item["judgment"] in rendered
    for key in ("reported", "actual_metric", "scope"):
        assert item["headline"][key] in rendered
    assert "90.0" in rendered and "95.3" in rendered


def test_duplicate_nested_source_location_is_shown_once():
    location = "Synthetic PDF p.6, Equations (12)–(15)"
    p = importer()["normalize_problem"](
        {
            "title": "Synthetic locator",
            "location": location,
            "focused_acceptance": {"source_location": location},
        },
        1,
    )
    assert p["source_location"] == location


@pytest.mark.parametrize(
    "fields",
    [
        {
            "general": "Use a closed synthetic region.",
            "special_case": "For positive margin use its boundary.",
        },
        {
            "conditional": "Use the conditional synthetic density.",
            "marginal": "Integrate over the synthetic latent value.",
        },
        {
            "alternatives": [
                "Concatenate the synthetic arrays.",
                "Use one reference at a time.",
            ]
        },
        {
            "verified_local": "Use the synthetic local upper bound.",
            "partial_slack": "Other synthetic counting steps remain open.",
        },
        {
            "linear_weights": "Use the synthetic linear-weight identity.",
            "general_weights": "Use the synthetic general-weight identity.",
        },
        {
            "winner_only": "Use the synthetic winner distribution.",
            "pair_conditioned": "Use the conditional synthetic pair likelihood.",
            "conditions": ["Fixed fictional ratings."],
        },
        {
            "positive_tie": "Add the synthetic tie mass.",
            "negative_tie_alternative": "Use the strict synthetic branch instead.",
        },
        {"note": "Select offset o_k+d*q+j for the synthetic last-coordinate check."},
    ],
)
def test_scoped_formula_alternatives_remain_repairs_without_becoming_verified(fields):
    p = importer()["normalize_problem"](
        {"title": "Synthetic alternatives", "repair": fields}, 1
    )
    assert p["repair"] is not None
    rendered = "\n".join(p["repair"]["paragraphs"])
    for value in fields.values():
        for text in value if isinstance(value, list) else [value]:
            assert text in rendered
    assert "verification_status" not in p["repair"]


def test_original_leaf_projection_is_lossless_when_title_is_an_excerpt():
    convert = importer()["normalize_problem"]
    claim = "An original synthetic claim with " + "specific original words " * 20
    item = {
        "claim": claim,
        "judgment": "Only a scoped local synthetic conclusion",
        "headline": {"scope": "A separate retained synthetic scope.", "array": [2, 7]},
    }
    p = convert(item, 1)
    assert claim.strip() in "\n".join(p["claim"] + p["analysis"])
    assert item["judgment"] in "\n".join(p["analysis"])
    assert item["headline"]["scope"] in "\n".join(p["analysis"])


def test_version_scope_cannot_replace_existing_concrete_evidence_in_the_finding():
    item = {
        "title": "Synthetic bound check",
        "version_scope": "Frozen synthetic source only; no historical inference.",
        "evidence": (
            "The synthetic integral is at least x^4, "
            "contradicting the displayed x^3 bound."
        ),
        "counterevidence": "The corrected synthetic x^4 bound survives.",
        "verification_artifact": "verification/fictional/check.json",
    }
    p = importer()["normalize_problem"](item, 1)
    assert p["result"][0] == "Recorded evidence: Evidence: " + item["evidence"]
    assert any(item["counterevidence"] in text for text in p["result"])
    assert item["version_scope"] in p["result"][-1]


def test_artifact_and_scope_only_check_is_an_inspection_subject_not_a_conclusion():
    p = importer()["normalize_problem"](
        {
            "title": "Synthetic historical artifact check",
            "evidence": ["verification/fictional/check.json"],
            "version_scope": "Frozen fictional source only.",
        },
        1,
    )
    assert p["result"][0] == (
        "Recorded inspection subject: Synthetic historical artifact check"
    )
    assert not any(text.startswith("Recorded evidence:") for text in p["result"])


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
