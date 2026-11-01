"""PDF-only repairs preserve source notation, labels, and frozen document scope."""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "math_pdf_publication_format", ROOT / "scripts/math_publication_format.py"
)
formatter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(formatter)


def document(body):
    return r"\documentclass{article}\begin{document}" + body + r"\end{document}"


def test_trailing_aligned_labels_move_byte_intact_with_all_equations_retained():
    for label in ["R5", "R3", "3.1"]:
        tag = r"\tag{" + label + "}"
        source = r"\begin{aligned} a&=b+c\notag\\ d&=e-f. " + tag + r"\end{aligned}"
        after = formatter._pdf_single_aligned_tag(source, label)
        assert after == source.replace(tag, "") + tag
        assert after.count(tag) == 1
        assert formatter._pdf_single_aligned_tag(after, label) == after


def test_tag_star_and_trailing_comment_are_preserved():
    source = (
        "% leading note\n"
        r"\begin{aligned}a&=b\tag*{R1}% tag note"
        "\n"
        r"\end{aligned}% trailing note"
    )
    after = formatter._pdf_single_aligned_tag(source, "R1")
    assert after == (
        "% leading note\n"
        r"\begin{aligned}a&=b% tag note"
        "\n"
        r"\end{aligned}\tag*{R1}% trailing note"
    )


def test_nested_nonterminal_multiple_and_external_tags_are_not_promoted():
    sources = [
        r"\begin{aligned}\begin{gathered}a=b\tag{R1}\end{gathered}\end{aligned}",
        r"\begin{aligned}a=b\tag{R1}+c\end{aligned}",
        r"\begin{aligned}a=b\tag{R1}\\c=d\tag{R2}\end{aligned}",
        r"x+\begin{aligned}a=b\tag{R1}\end{aligned}",
        r"\begin{aligned}a=b\end{aligned}\tag{R1}",
        r"\begin{aligned}a=b\tag{R1}\end{aligned}+c",
    ]
    for source in sources:
        assert formatter._pdf_single_aligned_tag(source, "R1") == source


def test_row_break_letters_comments_and_literals_are_not_active_tags():
    sources = [
        r"\begin{aligned}x&=0\\tag{R1}&=1\end{aligned}",
        r"\begin{aligned}x&=\text{\tag{R1}}\end{aligned}",
        r"\begin{aligned}x&=\verb|\tag{R1}|\end{aligned}",
        "\\begin{aligned}x&=0% \\tag{R1}\n\\end{aligned}",
    ]
    for source in sources:
        assert formatter._pdf_single_aligned_tag(source, "R1") == source


def test_glyph_fallback_retains_exact_codepoints_and_math_class():
    game, n = formatter._pdf_math_typography(r"\Game\Gamma_l", "game_exact_glyph")
    assert n == 1
    assert game == r'\mathord{\text{\fontspec{DejaVu Serif}\char"2141}}\Gamma_l'
    triangle, n = formatter._pdf_math_typography(
        r"\mathcal L^{\triangledown}\boxtimes\mathcal L", "triangledown_exact_glyph"
    )
    assert n == 1
    assert r'\mathord{\text{\fontspec{DejaVu Serif}\char"25BF}}' in triangle
    assert triangle.startswith(r"\mathcal L^{")
    assert triangle.endswith(r"}\boxtimes\mathcal L")


def test_binary_set_difference_preserves_all_operands_and_groups():
    source = r"A\setminus(B\cup C),\quad V\setminus0"
    after, count = formatter._pdf_math_typography(source, "setminus_typography")
    assert count == 2
    assert after == r"A\smallsetminus(B\cup C),\quad V\smallsetminus0"
    literal = r"\text{\setminus}\quad\verb|\setminus|% \setminus"
    assert formatter._pdf_math_typography(literal, "setminus_typography") == (
        literal,
        0,
    )


def test_gamma_uses_the_same_operator_and_explicit_math_font():
    source = r"\operatorname{R\Gamma}_Z(Y,F)=\operatorname{R\Gamma}(Z,i^!F)"
    after, count = formatter._pdf_math_typography(source, "operator_gamma_math_font")
    assert count == 2
    assert after == (
        r"\operatorname{R\symit{\Gamma}}_Z(Y,F)="
        r"\operatorname{R\symit{\Gamma}}(Z,i^!F)"
    )


def test_pdf_rules_require_expected_occurrences_and_display_math():
    rule = {"kind": "single_aligned_tag", "label": "R1", "expected_occurrences": 1}
    source = document(r"\[\begin{aligned}a=b\tag{R1}\end{aligned}\]")
    after, applied = formatter._pdf_apply_rules(source, [rule])
    assert r"\end{aligned}\tag{R1}\]" in after
    assert applied[0]["actual_occurrences"] == 1
    inline = source.replace(r"\[", r"\(").replace(r"\]", r"\)")
    with unittest.TestCase().assertRaisesRegex(ValueError, "frozen occurrences"):
        formatter._pdf_apply_rules(inline, [rule])
    with unittest.TestCase().assertRaisesRegex(ValueError, "frozen occurrences"):
        formatter._pdf_apply_rules(source, [{**rule, "expected_occurrences": 2}])


def test_complete_source_hash_and_result_hash_are_both_enforced():
    source = document(r"\(A\setminus B\)")
    rules = [{"kind": "setminus_typography", "expected_occurrences": 1}]
    after, _ = formatter._pdf_apply_rules(source, rules)
    row = {
        "case_id": "test-case",
        "before_sha256": formatter.digest(source),
        "after_sha256": formatter.digest(after),
        "rules": rules,
    }
    original_catalog = formatter._pdf_catalog
    try:
        formatter._pdf_catalog = lambda: (
            {row["before_sha256"]: row},
            {row["after_sha256"]: row},
        )
        assert formatter.apply_pdf_presentation(source) == after
        assert formatter.apply_pdf_presentation(after) == after
        assert formatter.apply_pdf_presentation(source + " ") == source + " "
        audit = formatter.pdf_presentation_audit(after)
        assert audit["before_sha256"] == formatter.digest(source)
        assert audit["after_sha256"] == formatter.digest(after)
        assert audit["rules"][0]["actual_occurrences"] == 1
        row["after_sha256"] = "0" * 64
        with unittest.TestCase().assertRaisesRegex(ValueError, "frozen hash"):
            formatter.apply_pdf_presentation(source)
    finally:
        formatter._pdf_catalog = original_catalog


def test_catalog_is_limited_to_nine_reviewed_complete_documents():
    before, after = formatter._pdf_catalog()
    assert len(before) == len(after) == 9
    assert {row["case_id"] for row in before.values()} == {
        "math2025-0004",
        "math2025-0005",
        "math2025-0062",
        "math2025-0127",
        "math2025-0170",
        "math2025-0179",
        "math2025-0182",
        "math2025-0260",
        "math2025-0407",
    }


if __name__ == "__main__":
    suite = unittest.TestSuite(
        unittest.FunctionTestCase(function)
        for name, function in list(globals().items())
        if name.startswith("test_") and callable(function)
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
