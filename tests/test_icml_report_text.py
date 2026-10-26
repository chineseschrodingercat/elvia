"""Loss-sensitive format conversion tests; all programs remain literal text."""

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts/icml_report_text.py"


@pytest.fixture
def converter():
    spec = importlib.util.spec_from_file_location("icml_report_text", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def str_node(text):
    return {"t": "Str", "c": text}


def para(text):
    return {"t": "Para", "c": [str_node(text)]}


def run_ast(converter, monkeypatch, tmp_path, ast, tex="Plain text."):
    source = tmp_path / "report.tex"
    source.write_text(tex, encoding="utf-8")
    calls = []

    def pandoc(args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args, 0, json.dumps(ast), "")

    monkeypatch.setattr(converter.subprocess, "run", pandoc)
    paragraphs = converter.report_paragraphs(source, pandoc="fixture-pandoc")
    return paragraphs, calls


def test_keeps_headers_math_links_footnotes_lists_and_literal_code(
    converter, monkeypatch, tmp_path
):
    ast = {
        "pandoc-api-version": [1, 22],
        "meta": {"title": {"t": "MetaInlines", "c": [str_node("Fixture title")]}},
        "blocks": [
            {"t": "Header", "c": [2, ["", [], []], [str_node("Scope")]]},
            {
                "t": "Para",
                "c": [
                    str_node("Assume"),
                    {"t": "Space"},
                    {"t": "Math", "c": [{"t": "InlineMath"}, r"x_i>0"]},
                    {"t": "Space"},
                    {
                        "t": "Link",
                        "c": [
                            ["", [], []],
                            [str_node("Source")],
                            ["https://example.org/paper", "Publisher"],
                        ],
                    },
                    {"t": "Note", "c": [para("Finite scope only.")]},
                ],
            },
            {
                "t": "Para",
                "c": [{"t": "Math", "c": [{"t": "DisplayMath"}, r"\sum_i x_i=1"]}],
            },
            {
                "t": "BulletList",
                "c": [[para("First condition")], [para("Second condition")]],
            },
            {
                "t": "OrderedList",
                "c": [[3, {"t": "Decimal"}, {"t": "Period"}], [[para("Third step")]]],
            },
            {
                "t": "CodeBlock",
                "c": [
                    ["", ["python"], []],
                    "raise RuntimeError('never execute')\nprint(7)\n",
                ],
            },
            {"t": "RawBlock", "c": ["latex", r"\unknown{retained argument}"]},
        ],
    }
    values, calls = run_ast(converter, monkeypatch, tmp_path, ast)
    text = "\n\n".join(values)
    for expected in [
        "Fixture title",
        "## Scope",
        r"\(x_i>0\)",
        r"\[\sum_i x_i=1\]",
        "Source",
        "https://example.org/paper",
        "Publisher",
        "Footnote",
        "Finite scope only.",
        "- First condition",
        "3. Third step",
        "raise RuntimeError('never execute')\nprint(7)\n",
        r"\unknown{retained argument}",
    ]:
        assert expected in text
    assert any(value.startswith("Code:\nraise RuntimeError") for value in values)
    args, options = calls[0]
    assert args[0] == "fixture-pandoc"
    assert "--from=latex" in args and "--to=json" in args
    assert "--fail-if-warnings" in args
    assert options["input"] == "Plain text."
    assert options.get("shell", False) is False
    assert options["cwd"] != str(tmp_path)
    assert all(str(tmp_path / "report.tex") != arg for arg in args)


def test_table_preserves_every_cell_row_caption_and_span(
    converter, monkeypatch, tmp_path
):
    attr = ["", [], []]

    def cell(text, span=1):
        return [attr, {"t": "AlignDefault"}, 1, span, [para(text)]]

    header = [attr, [cell("Case"), cell("Returned bit / proof")]]
    rows = [
        [attr, [cell("Member"), cell("1 / inclusion")]],
        [attr, [cell("Nonmember"), cell("0 / non-inclusion")]],
        [attr, [cell("A retained spanning note", 2)]],
    ]
    table = {
        "t": "Table",
        "c": [
            attr,
            [None, [para("Dispatch comparison")]],
            [],
            [attr, [header]],
            [[attr, 0, [], rows]],
            [attr, [[attr, [cell("Footer")]]]],
        ],
    }
    values, _ = run_ast(
        converter, monkeypatch, tmp_path, {"meta": {}, "blocks": [table]}
    )
    text = "\n".join(values)
    for expected in [
        "Dispatch comparison",
        "Case | Returned bit / proof",
        "Member | 1 / inclusion",
        "Nonmember | 0 / non-inclusion",
        "A retained spanning note",
        "colspan=2",
        "Footer",
    ]:
        assert expected in text


@pytest.mark.parametrize(
    "command",
    [
        r"\input{private.txt}",
        r"\include{private}",
        r"\write18{whoami}",
        r"\openin1=private.txt",
        r"\read1 to \data",
        r"\csname input\endcsname{private}",
        r"\InputIfFileExists{private}{}{}",
        r"\lstinputlisting{private.py}",
    ],
)
def test_file_or_execution_commands_rejected_before_pandoc(
    converter, monkeypatch, tmp_path, command
):
    source = tmp_path / "report.tex"
    source.write_text(command, encoding="utf-8")

    def forbidden(*args, **kwargs):
        pytest.fail("Unsafe report reached Pandoc")

    monkeypatch.setattr(converter.subprocess, "run", forbidden)
    with pytest.raises(ValueError, match="forbidden|unsafe"):
        converter.report_paragraphs(source)


def test_commands_in_comments_and_verbatim_are_literal_not_active(
    converter, monkeypatch, tmp_path
):
    tex = (
        "% \\input{commented}\n\\begin{Verbatim}\n\\input{literal}\n"
        "\\end{Verbatim}\n\\verb|\\write18{literal}|\nText."
    )
    values, _ = run_ast(
        converter, monkeypatch, tmp_path, {"meta": {}, "blocks": [para("Text.")]}, tex
    )
    assert values == ["Text."]


def test_unknown_ast_node_fails_instead_of_dropping_its_content(
    converter, monkeypatch, tmp_path
):
    with pytest.raises(ValueError, match="Unsupported.*FutureBlock"):
        run_ast(
            converter,
            monkeypatch,
            tmp_path,
            {"meta": {}, "blocks": [{"t": "FutureBlock", "c": "Must remain visible"}]},
        )


def test_raw_latex_cannot_reintroduce_file_commands(converter, monkeypatch, tmp_path):
    with pytest.raises(ValueError, match="forbidden"):
        run_ast(
            converter,
            monkeypatch,
            tmp_path,
            {
                "meta": {},
                "blocks": [{"t": "RawBlock", "c": ["latex", r"\input{private.txt}"]}],
            },
        )


def test_fixed_layout_preamble_is_removed_without_opening_fonts_or_packages(
    converter, monkeypatch, tmp_path
):
    source = (
        r"\title{Kept title}\author{Kept author}"
        r"\def\UrlBreaks{\do\/\do\a\do\0}"
        r"\input{ot1lmr.fd}"
        r"\IfFileExists{bookmark.sty}{\usepackage{bookmark}}{\usepackage{hyperref}}"
        r"\begin{document}Body.\end{document}"
    )
    _, calls = run_ast(
        converter,
        monkeypatch,
        tmp_path,
        {"meta": {}, "blocks": [para("Body.")]},
        source,
    )
    parsed = calls[0][1]["input"]
    assert r"\title{Kept title}\author{Kept author}" in parsed
    assert r"\input" not in parsed
    assert r"\IfFileExists" not in parsed
    assert r"\def" not in parsed


def test_exact_numeric_enumeration_label_is_layout_only(converter):
    source = r"\begin{document}\def\labelenumi{\arabic{enumi}.}Item."
    assert converter._checked_source(source) == r"\begin{document}Item."


@pytest.mark.parametrize(
    "source",
    [
        r"\begin{document}\input{ot1lmr.fd}\end{document}",
        r"\IfFileExists{bookmark.sty}{Discarded science}{}\begin{document}Body.",
        r"\input{private.fd}\begin{document}Body.",
        r"\def\UrlBreaks{\input{private}}\begin{document}Body.",
    ],
)
def test_layout_allowlist_does_not_allow_body_input_or_discard_unrecognized_text(
    converter, monkeypatch, tmp_path, source
):
    with pytest.raises(ValueError, match="forbidden"):
        run_ast(
            converter,
            monkeypatch,
            tmp_path,
            {"meta": {}, "blocks": [para("Body.")]},
            source,
        )


def test_pandoc_warnings_and_invalid_json_fail_closed(converter, monkeypatch, tmp_path):
    source = tmp_path / "report.tex"
    source.write_text("Fixture.", encoding="utf-8")
    monkeypatch.setattr(
        converter.subprocess,
        "run",
        lambda args, **kwargs: subprocess.CompletedProcess(
            args, 0, "{}", "Ignored content warning"
        ),
    )
    with pytest.raises(ValueError, match="warning"):
        converter.report_paragraphs(source)
    monkeypatch.setattr(
        converter.subprocess,
        "run",
        lambda args, **kwargs: subprocess.CompletedProcess(args, 0, "not JSON", ""),
    )
    with pytest.raises(ValueError, match="JSON"):
        converter.report_paragraphs(source)


def test_pandoc_212_real_table_numbers_survive_layout_prefix(converter, tmp_path):
    executable = Path(r"C:\ProgramData\anaconda3\Scripts\pandoc.exe")
    if not executable.is_file():
        pytest.skip("Optional local Pandoc 2.12 integration")
    source = tmp_path / "report.tex"
    source.write_text(
        r"\begin{tabularx}{\linewidth}{>{\raggedright\arraybackslash}X>{\raggedright\arraybackslash}X}"
        r"Member & 1 / inclusion\\Nonmember & 0 / non-inclusion\\\end{tabularx}",
        encoding="utf-8",
    )
    text = "\n".join(converter.report_paragraphs(source, pandoc=executable))
    assert "Member | 1 / inclusion" in text
    assert "Nonmember | 0 / non-inclusion" in text
