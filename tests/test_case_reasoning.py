"""Presentation reasoning retains the source's actual mathematical boundaries."""

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "curate_case_reasoning", ROOT / "scripts/curate_case_reasoning.py"
)
curation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(curation)


def test_complete_proof_rewrite_rejects_a_changed_retained_source_paragraph():
    import pytest

    problem = {
        "claim": ["A bounded scalar claim."],
        "source_location": "Equation (1), p. 2",
        "assumptions": [],
        "analysis": ["Check: the scalar witness fails the claim."],
        "result": ["The separate theorem is unaffected."],
        "brief": [],
        "repair": None,
    }
    report = [r"At \(x=0\), the claimed upper bound is false."]
    entry = {
        "before_sha256": curation.visible_digest(problem),
        "source_report_paragraphs": [
            {"index": 0, "sha256": hashlib.sha256(report[0].encode()).hexdigest()}
        ],
        "fields": {"analysis": report, "analysis_heading": "Proof"},
    }
    assert curation.apply_reviewed(problem, entry, report)["analysis"] == report
    with pytest.raises(ValueError, match="proof source"):
        curation.apply_reviewed(problem, entry, ["A different source proposition."])


def test_source_math_does_not_typeset_curly_possessive_suffixes_as_variables():
    report = [r"Let \(s\), \(t\), and \(d\) denote the mathematical variables."]
    prose = "The paper’s proof doesn’t establish the method’s guarantee."
    assert curation.source_presentation(prose, report) == prose


def test_reviewed_source_quote_preserves_bytes_and_rejects_a_stale_pdf_binding():
    import copy

    import pytest

    quote = {
        "text": r"For \(n=20\), the stated confidence bound holds.",
        "locator": "PDF p. 14",
        "source_identity": "The inspected proceedings PDF",
        "source_sha256": "a" * 64,
    }
    catalog = {
        "cases": {"case": {"revision": 1, "record_sha256": "b" * 64, "report": []}}
    }
    reviewed = {
        "case_quotes": {
            "case": {
                "revision": 1,
                "record_sha256": "b" * 64,
                "source_pdf_sha256": "a" * 64,
                "before": None,
                "after": [quote],
            }
        }
    }
    result, _ = curation.curate_catalog(catalog, reviewed)
    assert result["cases"]["case"]["source_quotes"] == [quote]
    repeated, _ = curation.curate_catalog(result, reviewed)
    assert repeated == result
    stale = copy.deepcopy(reviewed)
    stale["case_quotes"]["case"]["source_pdf_sha256"] = "c" * 64
    with pytest.raises(ValueError, match="original PDF"):
        curation.curate_catalog(catalog, stale)


def test_scientific_qualifications_and_repair_details_survive_metadata_cleanup():
    rows = [
        "Repair. Changes: Assign res := true before loop",
        "Repair. General: Require a nonempty closed target region.",
        "Correction. Not verified: The finite scalar witness "
        "is not a full theorem counterexample.",
        "Evidence. Actual llama counterexample: False",
        "Evidence refs. Location: Independent exact Gaussian-moment calculation",
        "Counterevidence. Survival: No historical score effect was established.",
        "Evidence bindings. SHA256: " + "a" * 64,
        "Evidence bindings. Bytes: 4096",
        "Adjudication status: pending",
    ]
    grouped, removed = curation.clean_rows(rows)
    kept = " ".join(text for group in grouped.values() for text in group)
    assert "res := true" in kept
    assert "nonempty closed target region" in kept
    assert "not a full theorem counterexample" in kept
    assert "Actual llama counterexample: False" in kept
    assert "exact Gaussian-moment calculation" in kept
    assert "No historical score effect" in kept
    assert removed == rows[-3:]


def test_scientific_label_case_and_scalar_roles_are_not_collapsed():
    rows = [
        "Check. Alphabet. Correct: A",
        "Check. Alphabet. Incorrect: a",
        "Check. Equiprobable kernel. A: a",
        "Check. Equiprobable kernel. B: a",
    ]
    grouped, removed = curation.clean_rows(rows)
    assert removed == []
    assert len(grouped["check"]) == 4
    assert any("Correct: A" in value for value in grouped["check"])
    assert any("Incorrect: a" in value for value in grouped["check"])
    assert any("kernel. A: a" in value for value in grouped["check"])
    assert any("kernel. B: a" in value for value in grouped["check"])


def test_operational_checklist_states_do_not_survive_as_scientific_prose():
    rows = [
        "Mode: recovery",
        "Recovery verification. Verified dimensions: NeurIPS_batch_1_severity",
        "Recovery verification. Verified dimensions: counterevidence",
        "Result: accepted",
        "Adoption status: unknown",
        "Kind: analytic_counterexample_with_independent_exact_arithmetic",
        "Mode: posterior mode remains unresolved",
    ]
    grouped, removed = curation.clean_rows(rows)
    assert removed == rows[:5]
    text = " ".join(grouped["check"])
    assert "analytic counterexample with independent exact arithmetic" in text
    assert "posterior mode remains unresolved" in text


def test_source_formula_restore_is_idempotent_and_preserves_code():
    report = [r"The cases \(x^2\) and \(x^{2}\) have the same spelling."]
    actual = curation.source_presentation("Use x^2, and `x^2` remains code.", report)
    assert actual == r"Use \(x^{2}\), and `x^2` remains code."
    assert curation.source_presentation(actual, report) == actual


def test_source_formula_restore_uses_only_exact_unambiguous_source_spellings():
    report = [
        r"The residual is \(\mu^2+\sigma^2\), with \(W^{-1}\) and \(\alpha=2\).",
        r"The comparison is \(p=0.0323>0.01\).",
    ]
    value = (
        "Use mu^2+sigma^2, W^-1 and alpha=2; p0.0323 lacks an operator. "
        "src/W^-1.py stays literal."
    )
    actual = curation.source_presentation(value, report)
    assert r"\(\mu^{2}+\sigma^{2}\)" in actual
    assert r"\(W^{-1}\)" in actual
    assert r"\(\alpha=2\)" in actual
    assert "p0.0323 lacks an operator" in actual
    assert "src/W^-1.py stays literal" in actual
    assert curation.source_presentation(actual, report) == actual


def test_source_formula_terms_restore_inside_longer_source_equations():
    report = [r"The full expression is \[\rho^{2}+x^{3}-1.\]"]
    actual = curation.source_presentation(
        "Compare rho^2+x^3; unseen^7 is not sourced.", report
    )
    assert actual == r"Compare \(\rho^{2}+x^{3}\); unseen^7 is not sourced."


def test_literal_power_typography_does_not_guess_fractional_or_compound_powers():
    value = (
        "x^4 and rho^2; T^1/2 and dc^6 remain ambiguous; `x^4` and src/x^4.py are code."
    )
    actual = curation.literal_math(value)
    assert actual == (
        r"\(x^{4}\) and \(\rho^{2}\); T^1/2 and dc^6 remain ambiguous; "
        "`x^4` and src/x^4.py are code."
    )


def test_decimal_exponent_is_never_split_into_an_integer_power_and_decimal_tail():
    assert curation.literal_math("N^1.5 and N^-0.25.") == (
        r"\(N^{1.5}\) and \(N^{-0.25}\)."
    )
    assert curation.literal_math("N^1.5/2 is ambiguous") == ("N^1.5/2 is ambiguous")


def test_mu_shorthand_is_not_guessed_to_be_greek_for_model_size():
    report = [r"The model size is \(m_u\), with cost \(m_u k\ell^2\)."]
    assert curation.source_presentation("mu^2 remains source-ambiguous", report) == (
        "mu^2 remains source-ambiguous"
    )
    conflicting = [r"The variables include \(m_u^2\) and \(\mu^2\)."]
    assert curation.source_presentation("mu^2 is ambiguous", conflicting) == (
        "mu^2 is ambiguous"
    )


def test_compact_subscript_spelling_recovers_the_unique_source_expression():
    report = [r"The metric is \(W_2^2\); the tolerance is \(\varepsilon^4\)."]
    actual = curation.source_presentation("Use W2^2 and eps^4.", report)
    assert actual == r"Use \(W_2^{2}\) and \(\varepsilon^{4}\)."


def test_bare_source_variable_never_fragments_a_power_or_page_locator():
    report = [r"Let \(x\), \(p\) and \(\mu\) be the variables."]
    actual = curation.source_presentation("x^4 and mu^2; p. 6; paper's text.", report)
    assert actual == r"\(x^{4}\) and \(\mu^{2}\); p. 6; paper's text."
    code = "np.std(Phat[s,a,:]*Vstar[:,h+1])**2"
    assert (
        curation.source_presentation(code, [r"Let \(s\) and \(h\) be indices."]) == code
    )


def test_complete_source_expression_restores_at_sentence_end():
    report = [r"The rate is \(\varepsilon^{-2}\); the page variable is \(p\)."]
    assert curation.source_presentation(
        "The rate is epsilon^-2. See p. 6.", report
    ) == (r"The rate is \(\varepsilon^{-2}\). See p. 6.")


def test_locator_spacing_keeps_code_paths_and_source_identity():
    raw = "Section5.3; Table3; Algorithm1; pp8–9; physical19 printed6; src/Table3.py; https://x.test/Section5.3"
    assert curation.normalize_location(raw) == (
        "Section 5.3; Table 3; Algorithm 1; pp. 8–9; physical p. 19 printed p. 6; "
        "src/Table3.py; https://x.test/Section5.3"
    )


def test_source_literal_tokens_cannot_rewrite_code_or_use_a_different_value():
    report = [r"The source fixes \(n=4\)."]
    row = {
        "field_path": "analysis[0]",
        "before_token": "n4",
        "after_source_TeX": r"\(n=4\)",
        "source_assignment": "n=4",
        "source_report_index": 0,
        "source_paragraph_sha256": hashlib.sha256(report[0].encode()).hexdigest(),
    }
    problem = {"analysis": ["Use n4; `n4` and np.fix(n4) remain code."]}
    actual, receipt = curation.apply_literal_tokens(problem, [row], report)
    assert actual["analysis"] == [r"Use \(n=4\); `n4` and np.fix(n4) remain code."]
    assert receipt[0]["count"] == 1
    again, receipt = curation.apply_literal_tokens(actual, [row], report)
    assert again == actual and receipt[0]["count"] == 0
    import pytest

    with pytest.raises(ValueError, match="source"):
        curation.apply_literal_tokens(
            problem, [{**row, "after_source_TeX": r"\(n=5\)"}], report
        )


def test_report_vocabulary_spacing_keeps_original_letters_and_named_entities():
    report = [
        "The finite example has a nonzero gradient. "
        "Separately, the scope remains conditional.",
        "FrobeniusNorm is a named identifier in this source.",
    ]
    value = (
        "Finiteexampleremainsconditional; hasnonzerogradient; "
        "FrobeniusNorm; `hasnonzerogradient`."
    )
    result = curation.source_presentation(value, report)
    assert (
        result == "Finite example remains conditional; has nonzero gradient; "
        "FrobeniusNorm; `hasnonzerogradient`."
    )
    assert result.replace(" ", "") == value.replace(" ", "")


def test_numeric_prose_spacing_keeps_scientific_values_code_and_identifiers():
    value = (
        "At0, nominal0.05 and647studies give Top4; has37samples, only.5. "
        "C2/L1/x0 remain identifiers; `at0 and647studies` remains code; "
        "https://example.test/at0/647studies and src/at0.json remain paths."
    )
    expected = (
        "At 0, nominal 0.05 and 647 studies give Top 4; has 37 samples, only .5. "
        "C2/L1/x0 remain identifiers; `at0 and647studies` remains code; "
        "https://example.test/at0/647studies and src/at0.json remain paths."
    )
    assert curation.source_presentation(value, []) == expected
    assert curation.finish_visible_math(value) == expected
    assert expected.replace(" ", "") == value.replace(" ", "")


def test_reviewed_number_word_suffixes_keep_models_hashes_and_code_literal():
    value = "20papers, 512words, 32runs; GPT-4o, 7B, 2PL and 6DoF."
    assert curation.finish_visible_math(value) == (
        "20 papers, 512 words, 32 runs; GPT-4o, 7B, 2PL and 6DoF."
    )
    code = "Code:\nprint('and647studies 20papers 32runs')"
    assert curation.source_presentation(code, []) == code
    assert curation.finish_visible_math(code) == code


def test_pure_file_references_do_not_become_reasoning_sentences():
    for raw in (
        "Evidence: source_p30.png",
        "Evidence: independent_checks.py",
        "Evidence: independent_checks.json",
        "Evidence. Artifact: verification/0020/independent_checks.json",
        "Recorded evidence: Evidence. File: WMDP/run_wmdp_unlearn.sh",
        "Evidence: independent_checks.json#/finite_diagnostic",
    ):
        assert curation.plain_row(raw) is None


def test_reference_cleanup_preserves_actual_results_scope_and_code():
    for raw in (
        "Evidence. Actual llama counterexample: False",
        "Evidence: independent_checks.py establishes only a finite check; "
        "no full replication.",
        "Counterevidence: missing_checks.py was unavailable; "
        "historical results remain unverified.",
        "Code: print('independent_checks.json')",
    ):
        assert curation.plain_row(raw) is not None


def test_compact_source_indices_never_replace_english_function_words():
    report = [r"Let \(I_n\), \(a_s\) and \(o_f\) be indexed quantities."]
    value = r"In Appendix A, as stated, use the norm of \(I_n\)."
    assert curation.source_presentation(value, report) == value


def test_compact_patch_size_is_not_guessed_as_an_index_from_another_formula():
    report = [r"The probability is \(p_1\); the one-pixel patch has \(p=1\)."]
    assert curation.source_presentation(
        "The patch size p1 uses one pixel.", report
    ) == ("The patch size p1 uses one pixel.")
    row = {
        "field_path": "analysis[0]",
        "before_token": "p1",
        "after_source_TeX": r"\(p_1\)",
        "source_assignment": "p_1",
        "source_report_index": 0,
        "source_paragraph_sha256": hashlib.sha256(report[0].encode()).hexdigest(),
    }
    actual, _ = curation.apply_literal_tokens(
        {"analysis": ["The reviewed probability p1 is an index."]}, [row], report
    )
    assert actual["analysis"] == [r"The reviewed probability \(p_1\) is an index."]


def test_case_overview_math_binds_to_revision_without_changing_the_record():
    catalog = {
        "cases": {
            "synthetic-case": {
                "revision": 1,
                "record_sha256": "source-pin",
                "problems": [],
            }
        }
    }
    reviewed = {
        "cases": {},
        "case_briefs": {
            "synthetic-case": {
                "revision": 1,
                "record_sha256": "source-pin",
                "before": None,
                "after": [r"The recorded construction has \(V_T=T^2-1/2\)."],
            }
        },
    }
    actual, _ = curation.curate_catalog(catalog, reviewed)
    assert (
        actual["cases"]["synthetic-case"]["brief"]
        == reviewed["case_briefs"]["synthetic-case"]["after"]
    )
    assert actual["cases"]["synthetic-case"]["record_sha256"] == "source-pin"
    assert curation.curate_catalog(actual, reviewed)[0] == actual


def test_case_overview_rejects_a_different_record_revision():
    import pytest

    catalog = {
        "cases": {
            "synthetic-case": {
                "revision": 2,
                "record_sha256": "new-pin",
                "problems": [],
            }
        }
    }
    reviewed = {
        "cases": {},
        "case_briefs": {
            "synthetic-case": {
                "revision": 1,
                "record_sha256": "old-pin",
                "before": None,
                "after": ["A source-bound presentation summary."],
            }
        },
    }
    with pytest.raises(ValueError, match="source revision"):
        curation.curate_catalog(catalog, reviewed)


def test_curated_paragraph_roles_are_stable_on_repeated_runs():
    problem = {
        "id": "p1",
        "analysis_heading": "Archived analysis and counterevidence",
        "analysis": [
            "Check: A finite calculation gives zero.",
            "Counterevidence: No global proof follows.",
        ],
        "claim": ["The result is universal"],
        "assumptions": [],
        "result": ["Result: A finite check is insufficient"],
        "repair": None,
        "source_location": "Table3",
    }
    first, _ = curation.generic_problem(problem, [])
    second, _ = curation.generic_problem(first, [])
    assert first == second
    assert len(second["analysis"]) == 2


def test_icml_0268_has_readable_set_and_rank_arguments_without_inventory_dump():
    notes = json.loads(
        (ROOT / "studies/icml2025/case-notes.json").read_text(encoding="utf-8")
    )["cases"]
    note = next(note for key, note in notes.items() if key.startswith("icml2025-0268-"))
    first, second = note["problems"]
    first_statement = "\n".join(first["claim"])
    first_text = "\n".join(first["analysis"])
    first_scope = "\n".join(first["result"])
    second_text = "\n".join(second["analysis"])
    second_scope = "\n".join(second["result"])
    for text in (first_text, second_text):
        assert "Evidence bindings" not in text
        assert "Adjudication status:" not in text
        assert "Correction." not in text
        assert "verification/0268" not in text
    assert first["assumptions"] == second["assumptions"] == []
    assert first["analysis_heading"] == second["analysis_heading"] == "Proof"
    assert r"S\setminus" in first_statement
    assert r"0.0323>0.01" in first_text
    assert "0.0002" in first_text
    assert "0.05" in first_scope and "would pass" in first_scope
    assert "19" in first_scope and "known relationships" in first_scope
    assert "adjusted" in first_scope and "unreported" in first_scope
    assert r"\operatorname{rank}" in second_text
    assert "255" in second_text
    assert r"0^{-1/2}" in second_text
    assert "implementation" in second_scope and "unresolved" in second_scope
    # The proof establishes undefinedness; a proposed regularized solution is
    # retained only in the separate historical data, not imported into Proof.
    assert "20/21" not in second_text
