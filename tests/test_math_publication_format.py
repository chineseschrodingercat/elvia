"""Formatting retains mathematical atoms, conditions, labels, and source binds."""

import importlib.util
import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "math_publication_format", ROOT / "scripts/math_publication_format.py"
)
formatter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(formatter)


def rendered(text):
    """Use the unchanged, pinned renderer and exact production strict options."""
    node = shutil.which("node")
    if node is None:
        raise unittest.SkipTest(
            "Node is required for the pinned KaTeX compatibility check"
        )
    script = r"""
const fs = require('node:fs');
const math = require('./src/elvia/web/math.js');
const katex = require('./src/elvia/web/vendor/katex/katex.min.js');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const output = math.parseExplicit(input).filter(p => p.kind === 'math')
  .map(p => katex.renderToString(p.tex, math.renderOptions(p.display)));
console.log(JSON.stringify(output));
"""
    result = subprocess.run(
        [node, "-e", script],
        input=json.dumps(text),
        text=True,
        encoding="utf-8",
        capture_output=True,
        cwd=ROOT,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_compound_accents_preserve_argument_and_outer_indices():
    before = (
        "Field \\(\\overline\\mathbb Q_p^\\times\\), derivative "
        "\\(\\partial_1\\bar\\underline{w}>0\\), determinant "
        "\\(\\widetilde\\operatorname{Det}\\)."
    )
    after = formatter.format_publication_text(before)
    assert r"\overline{\mathbb Q}_p^\times" in after
    assert r"\partial_1\bar{\underline{w}}>0" in after
    assert r"\widetilde{\operatorname{Det}}" in after
    assert len(rendered(after)) == 3


def test_nested_text_math_preserves_every_condition():
    before = (
        "Assume \\[a\\le b\\quad\\text{for \\(x\\in S\\), \\(0<r<1\\), and "
        "\\(n\\ge2\\).}\\] Then conclude."
    )
    after = formatter.format_publication_text(before)
    assert after == (
        "Assume \\[a\\le b\\quad\\text{for $x\\in S$, $0<r<1$, and "
        "$n\\ge2$.}\\] Then conclude."
    )
    assert len(rendered(after)) == 1


def test_rule_geometry_and_average_integral_stay_present():
    before = (
        "\\[\\nu=c\\mathcal H^1\\mathbin{\\vrule height 1.4ex depth "
        "-0.3ex width 0.07ex\\vrule height 0.07ex depth 0ex width "
        "0.7ex}L,\\qquad \\mathop{\\rlap{\\ensuremath{\\mkern "
        "3mu-}}\\int}\\nolimits_B |u|\\,dx>0.\\]"
    )
    after = formatter.format_publication_text(before)
    assert r"\rule[0.3ex]{0.07ex}{1.1ex}\rule{0.7ex}{0.07ex}" in after
    assert r"\mathop{\mathrlap{\mkern 3mu-}\int}\nolimits_B |u|\,dx>0" in after
    assert len(rendered(after)) == 1


def test_scoped_text_fonts_and_all_digest_characters_are_retained():
    sha = "0123456789abcdef" * 4
    before = (
        r"\[\text{prefix \ttfamily X\normalfont Y}\quad\text{\nolinkurl{"
        + sha
        + r"}}\quad\text{\seqsplit{"
        + sha
        + r"}}\]"
    )
    after = formatter.format_publication_text(before)
    assert after.count(sha) == 2
    assert r"prefix \texttt{ X\textnormal{ Y}}" in after
    assert len(rendered(after)) == 1


def test_text_boxes_and_hook_arrow_keep_statements():
    before = (
        "\\[A\\lhook\\joinrel\\longrightarrow B,\\qquad "
        "x\\ge0\\quad\\mbox{for every }x\\in S.\\]"
    )
    after = formatter.format_publication_text(before)
    assert r"A\xhookrightarrow{} B" in after
    assert r"x\ge0\quad\text{for every }x\in S" in after
    assert len(rendered(after)) == 1


def test_multiple_aligned_tags_remain_visible_on_the_same_rows():
    before = (
        r"\[\begin{aligned}&a=b;\tag{a}\\&c>d;\tag{b}\\&e\ne f.\tag{c}\end{aligned}\]"
    )
    after = formatter.format_publication_text(before)
    assert r"a=b;\qquad\text{(a)}\\" in after
    assert r"c>d;\qquad\text{(b)}\\" in after
    assert r"e\ne f.\qquad\text{(c)}" in after
    assert len(rendered(after)) == 1


def test_tag_letters_after_row_breaks_are_not_tag_commands():
    source = r"\[\begin{aligned}x&=0\\tag{a}&=1\\tag{b}&=2\end{aligned}\]"
    assert formatter.format_publication_text(source) == source
    assert len(rendered(source)) == 1


def test_literal_verbatim_and_commented_tags_are_not_reinterpreted():
    literal = r"\(\verb|\bar\mathbb Q|\)"
    assert formatter.format_publication_text(literal) == literal
    assert len(rendered(literal)) == 1
    source = (
        "\\[\\begin{aligned}a&=b % \\tag{not-a-label}\n\\\\c&=d "
        "\\tag{a}\\end{aligned}\\]"
    )
    assert formatter.format_publication_text(source) == source
    assert len(rendered(source)) == 1


def test_unknown_macros_code_and_plain_prose_are_not_discarded():
    for text in [
        "Code:\n" + r"print('\\input{private.tex}'); # \(literal",
        r"No claim of a main-theorem counterexample; \normalfont is a quoted command.",
        r"\(x+\unknownScientificOperator{y}\)",
    ]:
        assert formatter.format_publication_text(text) == text
    with unittest.TestCase().assertRaisesRegex(ValueError, "Unclosed"):
        formatter.format_publication_text(r"Unknown source \(x+y")


def test_frozen_set_difference_override_requires_original_report_hash():
    row = formatter._overrides()["math2025-0068"][0]
    with unittest.TestCase().assertRaisesRegex(ValueError, "source report hash"):
        formatter.format_publication_text(
            row["before"], case_id="math2025-0068", source_report_sha256="0" * 64
        )
    audit = []
    after = formatter.format_publication_text(
        row["before"],
        case_id="math2025-0068",
        source_report_sha256=row["report_tex_sha256"],
        audit=audit,
    )
    assert after == row["after"]
    assert r"\(Q\setminus(S\cup U)\)" in after
    assert audit[0]["before_sha256"] == formatter.digest(row["before"])
    assert audit[0]["source_report_sha256"] == row["report_tex_sha256"]
    assert len(rendered(after)) == 1


def test_transformation_is_idempotent_and_audited_without_structure_changes():
    source = {
        "report": [r"\(\bar\mathbb{Q}\) is a field.", "Code:\n" + r"\(literal"],
        "revision": 1,
        "status": "pending",
    }
    audit = []
    once = formatter.format_publication_data(source, audit=audit, location="case")
    twice_audit = []
    twice = formatter.format_publication_data(once, audit=twice_audit, location="case")
    assert once == twice
    assert twice_audit == []
    assert once["revision"] == source["revision"]
    assert once["status"] == source["status"]
    assert once["report"][1] == source["report"][1]
    assert len(audit) == 1
    assert audit[0]["location"] == "case.report[0]"
    assert (
        audit[0]["outer_math_spans_before_normalization"]
        == audit[0]["outer_math_spans_after_normalization"]
        == 1
    )
    assert audit[0]["rules"] == {"brace_compound_accent_argument": 1}


def test_pdf_template_adds_math_dependencies_without_changing_body():
    preamble = (
        r"\documentclass{article}"
        + "\n"
        + r"\usepackage{amsmath,amssymb,fontspec,unicode-math,xurl,hyperref}"
    )
    body = r"\begin{document}\(\mathop{\mathrlap{-}\int}_B f\)\end{document}"
    rendered_tex = formatter.render_publication_tex(
        [], renderer=lambda _: preamble + "\n" + body
    )
    assert "amsmath,amssymb,mathtools,fontspec,unicode-math" in rendered_tex
    assert rendered_tex.endswith(body)
    assert preamble + "\n" + body != rendered_tex
    with unittest.TestCase().assertRaisesRegex(ValueError, "package list changed"):
        formatter.render_publication_tex(
            [], renderer=lambda _: r"\begin{document}changed template"
        )


if __name__ == "__main__":
    suite = unittest.TestSuite(
        unittest.FunctionTestCase(function)
        for name, function in list(globals().items())
        if name.startswith("test_") and callable(function)
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
