"""Publication cleanup keeps scientific content while removing workflow prose."""

import hashlib
import runpy
from pathlib import Path

import pytest


def cleaner():
    return runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "scripts/report_cleanup.py")
    )


def test_quoted_operational_tail_is_removed_without_touching_finding():
    rows = [
        "# Substantive finding",
        r"The ranking reverses under conventional macro-F1: \(a>b\).",
        "The published recall values remain correct; historical use is unresolved.",
        "# Evidence and provenance",
        "The source PDF SHA-256 is . The decisive evaluator SHA-256 is . "
        "The accompanying verification directory contains `inputs.json`, "
        "`coverage.json`, `findings.json` and `provenance.json`. "
        "Native auxiliary agents contributed theory checks; the parent "
        "independently compiled the final TeX and inspected the PDF. "
        "These are AI-assisted checks, not human acceptance.",
    ]
    result = cleaner()["clean_paragraphs"](rows)
    assert result["paragraphs"] == rows[:3]
    assert not result["review"]


def test_reference_section_after_workflow_is_preserved():
    rows = [
        "# Evidence and roles",
        "The compiler log and visual record are in provenance.json.",
        "# References",
        "Chen et al. (2025), PMLR 267. https://proceedings.mlr.press/example",
    ]
    result = cleaner()["clean_paragraphs"](rows)
    assert result["paragraphs"] == rows[2:]


def test_mixed_workflow_paragraph_retains_source_availability_boundary():
    rows = [
        "# Coverage, provenance and delivery limits",
        "OpenReview history was inaccessible. The report PDF was produced "
        "with the existing HTML renderer. The TeX file was not compiled "
        "because no TeX compiler was available.",
    ]
    result = cleaner()["clean_paragraphs"](rows)
    assert "OpenReview history was inaccessible." in result["paragraphs"]
    assert "compiler" not in " ".join(result["paragraphs"])


def test_original_rendered_page_check_is_scientific_evidence():
    rows = [
        "# Complete check",
        "The absolute-value bars are present in the rendered source PDF. "
        "This is not a text-extraction defect.",
    ]
    assert cleaner()["clean_paragraphs"](rows)["paragraphs"] == rows


def test_compiler_and_controller_are_not_automatically_review_workflow():
    rows = [
        "# Substantive finding",
        "The compiler folds the constant before evaluating the printed branch.",
        "Task descriptions determine which target the controller optimizes.",
        r"The controller is stable for \(0<\gamma<1\).",
    ]
    result = cleaner()["clean_paragraphs"](rows)
    assert result["paragraphs"] == rows
    assert not result["review"]


def test_scientific_selected_model_definition_is_not_role_metadata():
    rows = [
        "# Counterevidence",
        "Schweighofer et al., arXiv:2410.10786v1, pp2-3, offer an "
        "alternative selected-model entropy definition of AU.",
        "The runtime model predicts the target from an auxiliary model.",
    ]
    result = cleaner()["clean_paragraphs"](rows)
    assert result["paragraphs"] == rows
    assert not result["review"]


def test_auxiliary_scientific_loss_and_historical_model_ids_are_preserved():
    rows = [
        "# Counterevidence and scope",
        "Its auxiliary role and deterioration at excessive weight are "
        "counterevidence against treating collapse as a method failure.",
        "Exact historical masks, model identifiers and run provenance "
        "are needed before attributing the discrepancy to every accuracy curve.",
        "E10 – inaccessible adoption-report PDF; not verified evidence: "
        "https://example.org/report.pdf",
    ]
    result = cleaner()["clean_paragraphs"](rows)
    assert result["paragraphs"] == rows
    assert not result["review"]


def test_review_actor_can_be_neutralized_without_touching_scientific_parent_set():
    rows = [
        "# Calculation",
        r"The parent independently recomputed the exact value \(3/7\).",
        r"The parent set of \(Y\) is empty under the intervention.",
    ]
    result = cleaner()["clean_paragraphs"](rows)
    assert result["paragraphs"] == [
        rows[0],
        r"The independent check independently recomputed the exact value \(3/7\).",
        rows[2],
    ]
    assert not result["review"]


def test_scientific_evidence_and_provenance_headings_retain_their_scope():
    rows = [
        "# Experiment provenance remains unresolved",
        "Historical experimental attribution remains unresolved.",
        "# Figure evidence and scope of the negative result",
        "The plotted result concerns this benchmark only.",
    ]
    assert cleaner()["clean_paragraphs"](rows)["paragraphs"] == rows


def test_workflow_region_removes_roles_even_without_build_marker():
    rows = [
        "# Reproducibility and roles",
        "Native auxiliary tasks supplied mathematical checks. "
        "The exposed model label is GPT-6 Astra Pro. "
        "Scientific adjudication remains pending.",
    ]
    result = cleaner()["clean_paragraphs"](rows)
    assert result["paragraphs"] == [
        "# Scope and limitations",
        "Scientific adjudication remains pending.",
    ]
    assert not result["review"]


def test_explicit_ai_roles_and_tool_build_history_are_cleaned():
    rows = [
        "# Supporting record",
        "AI roles: the primary assistant assembled the report. "
        "No human review is asserted.",
        "Initial-review and proposal build history. "
        "Lumen's PDF reader failed. OpenReview history was inaccessible.",
    ]
    result = cleaner()["clean_paragraphs"](rows)
    assert result["paragraphs"] == [
        "# Supporting record",
        "No human review is asserted.",
        "OpenReview history was inaccessible.",
    ]


def test_formal_source_identity_is_not_removed_by_hash_keyword():
    rows = [
        "# Source identity",
        "arXiv:2505.12366v5, revised 6 January 2026",
        "https://arxiv.org/pdf/2505.12366v5",
        "Reviewed PDF SHA-256: " + "a" * 64,
    ]
    assert cleaner()["clean_paragraphs"](rows)["paragraphs"] == rows


def test_author_final_pdf_reference_and_source_availability_are_preserved():
    rows = [
        "E6. Weiss et al., COLM 2024; final PDF access failed: "
        "https://openreview.net/forum?id=Zq9Dfj4nBo",
        "No raw annotation release was identified within the final PDF; "
        "this is an availability limitation.",
    ]
    result = cleaner()["clean_paragraphs"](rows)
    assert result["paragraphs"] == rows
    assert not result["review"]


def test_role_sentence_cannot_hide_scientific_rejection_boundary():
    row = (
        "The parent rejected the Major grading because the synthetic "
        "trajectory's trained-RNN conditions were unverified."
    )
    result = cleaner()["clean_paragraphs"](["# Provenance and roles", row])
    assert row in result["paragraphs"]
    assert result["review"]


def test_all_code_is_preserved_and_operational_commands_are_flagged():
    code = "Code:\nfrom fractions import Fraction\na = Fraction(1, 3)\nassert 3*a == 1"
    rows = [
        "# Reproducibility and roles",
        code,
        "Code:\ntectonic --untrusted report.tex\npdfinfo report.pdf",
        "The compiler result is stored in provenance.json.",
    ]
    result = cleaner()["clean_paragraphs"](rows)
    assert code in result["paragraphs"]
    assert rows[2] in result["paragraphs"]
    assert result["review"]


def test_math_inside_mixed_workflow_is_preserved_and_flagged_for_review():
    row = r"The independent check found \(x^2=1\); compiler records are retained."
    result = cleaner()["clean_paragraphs"](["# Evidence and provenance", row])
    assert row in result["paragraphs"]
    assert result["review"]


def test_cleaning_is_idempotent_and_does_not_rewrite_scientific_limits():
    rows = [
        "# Evidence and roles",
        "No author code was executed. Historical training results were not reproduced.",
        "Native auxiliary agents supplied static-source checks.",
    ]
    once = cleaner()["clean_paragraphs"](rows)["paragraphs"]
    assert rows[1] in once
    assert cleaner()["clean_paragraphs"](once)["paragraphs"] == once


def reviewed(index, before, after, kind="reviewed_scope_or_narrative_cleanup", **extra):
    return {
        "index": index,
        "before_sha256": hashlib.sha256(before.encode()).hexdigest(),
        "after": after,
        "kind": kind,
        **extra,
    }


def test_reviewed_replacement_rejects_changed_original_paragraph():
    with pytest.raises(ValueError, match="frozen source"):
        cleaner()["clean_paragraphs"](
            ["Changed paragraph"], reviewed=[reviewed(0, "Original paragraph", None)]
        )


def test_empty_internal_heading_can_be_removed_by_frozen_review():
    row = "# Source identity and role provenance"
    result = cleaner()["clean_paragraphs"](
        ["Scientific scope remains bounded.", row],
        reviewed=[reviewed(1, row, None)],
    )
    assert result["paragraphs"] == ["Scientific scope remains bounded."]


def test_reviewed_hash_display_removal_preserves_scientific_math():
    value = (
        r"\[\begin{gathered}\texttt{aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa}\\"
        r"\texttt{bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb}.\end{gathered}\]"
    )
    row = "Original PDF SHA-256: " + value
    science = r"The diagnostic gives \(x^2=1\)."
    result = cleaner()["clean_paragraphs"](
        [row, science],
        reviewed=[
            reviewed(
                0,
                row,
                None,
                kind="remove_hash_display_bookkeeping",
                allowed_removed_math_spans=[value],
            )
        ],
    )
    assert result["paragraphs"] == [science]
    assert result["preserved_math"] == result["removed_hash_displays"] == 1


def test_scientific_equation_cannot_be_exempted_as_a_hash():
    value = r"\[x^2=1\]"
    row = "Original PDF SHA-256: " + value
    with pytest.raises(ValueError, match="artifact hash display"):
        cleaner()["clean_paragraphs"](
            [row],
            reviewed=[reviewed(0, row, None, allowed_removed_math_spans=[value])],
        )


def test_review_cannot_silently_change_a_scientific_formula():
    row = r"The diagnostic gives \(x^2=1\)."
    with pytest.raises(ValueError, match="mathematical source"):
        cleaner()["clean_paragraphs"](
            [row], reviewed=[reviewed(0, row, "The diagnostic gives a value.")]
        )


def test_review_cannot_remove_an_actual_scientific_check_program():
    row = "Code:\nfrom fractions import Fraction\nassert Fraction(1,3)*3 == 1"
    with pytest.raises(ValueError, match="operation-only block"):
        cleaner()["clean_paragraphs"](
            [row],
            reviewed=[reviewed(0, row, None, kind="remove_operational_command")],
        )


def test_pdf_template_renders_all_markdown_heading_levels_and_preserves_math():
    module = cleaner()
    paragraphs = [
        "# Main finding",
        "## Scope",
        r"### The exact value \(3/7\)",
        "#### Calculation",
        "##### Boundary",
        "###### Additional qualification",
        r"The bound is \(x^2+1\), with the stated assumptions.",
    ]
    tex = module["render_icml_tex"](paragraphs)
    assert r"\section*{Main finding}" in tex
    assert r"\subsection*{Scope}" in tex
    assert r"\subsubsection*{The exact value \(3/7\)}" in tex
    assert r"\paragraph*{Calculation}" in tex
    assert r"\subparagraph*{Boundary}" in tex
    assert r"\subparagraph*{\normalfont\itshape Additional qualification}" in tex
    assert r"\#" not in tex
    assert module["MATH"].findall(tex) == module["MATH"].findall("\n".join(paragraphs))


def test_pdf_template_has_real_title_and_no_empty_metadata_or_invented_date():
    module = cleaner()
    paragraphs = [
        "Abstract: The original bounded conclusion remains unchanged.",
        "Author: AI-assisted technical review",
        "Date:",
        "Title: Technical Verification of\nAn Example Paper",
        "# Finding",
        "The original scientific paragraph remains unchanged.",
    ]
    tex = module["render_icml_tex"](paragraphs)
    assert r"\title{Technical Verification of" in tex
    assert r"\author{AI-assisted technical review}" in tex
    assert r"\date{}" in tex
    assert r"\maketitle" in tex
    assert "Date:" not in tex
    assert "Title:" not in tex
    assert "Author:" not in tex
    assert tex.index(r"\maketitle") < tex.index("Abstract:")
    assert tex.index("Abstract:") < tex.index("The original scientific paragraph")


def test_formatting_plan_removes_only_empty_header_fields():
    module = cleaner()
    paragraphs = [
        "Title: A report",
        "Author:",
        "Date:   ",
        "# Scope",
        r"The claim remains conditional on \(x>0\).",
        "Code:\nassert 2 + 2 == 4",
    ]
    result = module["format_report_paragraphs"](paragraphs)
    assert result["paragraphs"] == [paragraphs[i] for i in [0, 3, 4, 5]]
    assert result["removed_indices"] == [1, 2]
    assert [e["before_sha256"] for e in result["edits"]] == [
        module["digest"](paragraphs[1]),
        module["digest"](paragraphs[2]),
    ]
    assert result["preserved_math"] == result["preserved_code_blocks"] == 1


def test_pdf_template_preserves_supplied_date_and_code_chunk_bytes():
    module = cleaner()
    code = "Code:\nfrom fractions import Fraction\nassert Fraction(1, 3) * 3 == 1"
    paragraphs = [
        "Title: A report",
        "Date: Review date: 23 October 2026 (America/Chicago)",
        code,
    ]
    tex = module["render_icml_tex"](paragraphs)
    assert r"\date{Review date: 23 October 2026 (America/Chicago)}" in tex
    legacy = module["render_icml_tex_legacy"]([code])
    code_chunk = legacy.split(r"\begin{document}" + "\n", 1)[1].split(
        r"\end{document}", 1
    )[0]
    assert code_chunk in tex


def test_formatting_overlay_rejects_before_hash_and_duplicate_index_conflicts():
    module = cleaner()
    row = {
        "case": "icml-example",
        "index": 0,
        "before": "Original paragraph",
        "before_sha256": module["digest"]("Original paragraph"),
        "after": None,
    }
    with pytest.raises(ValueError, match="frozen source"):
        module["format_report_paragraphs"](
            ["Changed paragraph"], case_id="icml-example", overrides=[row]
        )
    with pytest.raises(ValueError, match="duplicate"):
        module["format_report_paragraphs"](
            ["Original paragraph"], case_id="icml-example", overrides=[row, row]
        )


def test_formatting_overlay_is_sparse_and_does_not_mutate_its_inputs():
    from copy import deepcopy

    module = cleaner()
    paragraphs = ["Title: A report", "Date:", "Internal workflow note", "# Scope"]
    overlay = [
        {
            "case": "icml-example",
            "index": 2,
            "before": paragraphs[2],
            "before_sha256": module["digest"](paragraphs[2]),
            "after": "A reviewed replacement.",
        }
    ]
    frozen = deepcopy((paragraphs, overlay))
    result = module["format_report_paragraphs"](
        paragraphs, case_id="icml-example", overrides=overlay
    )
    assert result["paragraphs"] == [
        "Title: A report",
        "A reviewed replacement.",
        "# Scope",
    ]
    assert (paragraphs, overlay) == frozen
    assert [row["index"] for row in result["edits"]] == [1, 2]


def test_formatting_overlay_cannot_change_mathematics_or_code():
    module = cleaner()
    for text in [r"The exact value is \(3/7\).", "Code:\nassert 2 + 2 == 4"]:
        row = {
            "index": 0,
            "before": text,
            "before_sha256": module["digest"](text),
            "after": None,
        }
        with pytest.raises(ValueError, match="mathematical source|scientific code"):
            module["format_report_paragraphs"]([text], overrides=[row])


def test_format_plan_counts_tex_only_changes_and_keeps_standard_reports(tmp_path):
    import json

    module = cleaner()
    rows = ["Title: Example", "# Scope", "The original conclusion remains bounded."]
    for collection, case, paragraphs in [
        ("icml2025", "icml-example", rows),
        ("neurips2025", "neurips-example", None),
    ]:
        dataset = tmp_path / "studies" / collection
        evidence = dataset / "evidence" / case
        evidence.mkdir(parents=True)
        note = {"report": paragraphs} if paragraphs is not None else {"summary": "A"}
        (dataset / "case-notes.json").write_text(
            json.dumps({"cases": {case: note}}), encoding="utf-8"
        )
        (evidence / "report.tex").write_text(
            module["render_icml_tex_legacy"](paragraphs)
            if paragraphs is not None
            else "A retained standard scientific report.\n",
            encoding="utf-8",
        )
        (evidence / "report.txt").write_text(
            "\n\n".join(paragraphs or []) + "\n", encoding="utf-8"
        )
    output = tmp_path / "candidates"
    plan = module["build_format_plan"](tmp_path, output)
    assert plan["counts"]["reports_scanned"] == 2
    assert plan["counts"]["reports_changed"] == 1
    assert plan["counts"]["tex_only_reports"] == 1
    assert plan["cases"]["icml-example"]["edits"] == []
    assert not plan["cases"]["neurips-example"]["changed"]
    assert (output / "candidates/icml-example/report.tex").exists()
    assert not (output / "candidates/neurips-example").exists()


def test_retained_citation_wrappers_keep_exact_keys_and_explicit_pages():
    rows = [
        r"The sources are [Retained latex: \cite{paper,code}] and "
        r"[Retained latex: \cite[p.~7]{theorem_source}]; compare "
        r"[Retained latex: \cite[p.~15]{later}].",
    ]
    result = cleaner()["format_report_paragraphs"](rows)
    assert result["paragraphs"] == [
        "The sources are [paper, code] and [theorem_source, p. 7]; "
        "compare [later, p. 15]."
    ]
    assert result["normalized_citation_wrappers"] == 3
    assert not result["review"]


def test_citation_cleanup_does_not_touch_code_or_mathematical_source():
    code = r"Code:" + "\n" + r"print('[Retained latex: \cite{paper}]')"
    math = r"\(\text{[Retained latex: \cite{paper}]}\)"
    rows = [code, math, r"Source: [Retained latex: \cite{repo}]."]
    result = cleaner()["format_report_paragraphs"](rows)
    assert result["paragraphs"] == [code, math, "Source: [repo]."]


def test_unknown_retained_citation_is_kept_for_manual_review():
    row = r"Source: [Retained latex: \cite[pp.~7--9]{paper}]."
    result = cleaner()["format_report_paragraphs"]([row])
    assert result["paragraphs"] == [row]
    assert result["review"]
