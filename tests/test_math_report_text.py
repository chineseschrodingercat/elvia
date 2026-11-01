"""Math publication conversions retain proofs and fail on lossy input handling."""

import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts/math_report_text.py"


@pytest.fixture
def converter():
    spec = importlib.util.spec_from_file_location("math_report_text", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def para(text):
    return {"t": "Para", "c": [{"t": "Str", "c": text}]}


def test_source_string_and_explicit_path_have_identical_reader_input(
    converter, monkeypatch, tmp_path
):
    source = r"\begin{document}Assume \(x_i>0\).\end{document}"
    path = tmp_path / "report.tex"
    path.write_text(source, encoding="utf-8")
    calls = []

    def pandoc(args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(
            args, 0, json.dumps({"blocks": [para("Preserved proof.")]}), ""
        )

    monkeypatch.setattr(converter.subprocess, "run", pandoc)
    assert converter.report_paragraphs(source) == ["Preserved proof."]
    assert converter.report_paragraphs(path) == ["Preserved proof."]
    assert all(options["input"] == source for _, options in calls)
    for args, options in calls:
        assert "--fail-if-warnings" in args
        assert options.get("shell", False) is False
        assert str(path) not in args


@pytest.mark.parametrize(
    "source",
    [
        r"\input{private.txt}",
        r"\write18{whoami}",
        r"\def\hidden{\input{private.txt}}\hidden",
        r"\newcommand{\hidden}{\input{private.txt}}\hidden",
        r"\csname input\endcsname{private.txt}",
        r"\begin{filecontents}{private.txt}Anything.\end{filecontents}",
    ],
)
def test_active_commands_remain_rejected_before_parser(converter, monkeypatch, source):
    def forbidden(*args, **kwargs):
        pytest.fail("An unsafe active command reached Pandoc")

    monkeypatch.setattr(converter.subprocess, "run", forbidden)
    with pytest.raises(ValueError, match="forbidden|unsafe"):
        converter.report_paragraphs(source)


def test_modern_figure_preserves_image_body_and_both_captions(converter, monkeypatch):
    figure = {
        "t": "Figure",
        "c": [
            ["fig-proof", [], []],
            [[{"t": "Str", "c": "Short caption."}], [para("Full scientific caption.")]],
            [
                para("The image body and its evidence are retained."),
                {"t": "Para", "c": [{"t": "Math", "c": [{"t": "DisplayMath"}, "a=b"]}]},
            ],
        ],
    }
    monkeypatch.setattr(
        converter.subprocess,
        "run",
        lambda args, **kwargs: subprocess.CompletedProcess(
            args, 0, json.dumps({"blocks": [figure]}), ""
        ),
    )
    text = "\n".join(converter.report_paragraphs("Figure fixture."))
    for expected in [
        "The image body and its evidence are retained.",
        "Short caption.",
        "Full scientific caption.",
        r"\[a=b\]",
    ]:
        assert expected in text


def test_warnings_and_unknown_ast_are_still_errors(converter, monkeypatch):
    monkeypatch.setattr(
        converter.subprocess,
        "run",
        lambda args, **kwargs: subprocess.CompletedProcess(
            args, 0, json.dumps({"blocks": [para("Partial text")]}), "Dropped material"
        ),
    )
    with pytest.raises(ValueError, match="warning"):
        converter.report_paragraphs("Fixture.")
    monkeypatch.setattr(
        converter.subprocess,
        "run",
        lambda args, **kwargs: subprocess.CompletedProcess(
            args,
            0,
            json.dumps({"blocks": [{"t": "NewUnknownBlock", "c": "Proof"}]}),
            "",
        ),
    )
    with pytest.raises(ValueError, match="Unsupported.*NewUnknownBlock"):
        converter.report_paragraphs("Fixture.")


def test_real_reader_retains_declared_math_macros_derivations_and_literal_programs(
    converter,
):
    pandoc = shutil.which("pandoc")
    if pandoc is None:
        pytest.skip("Optional installed-Pandoc mathematical report integration")
    source = r"""
\documentclass{article}
\usepackage{amsmath,amssymb}
\newcommand{\RR}{\mathbb{R}}
\newcommand{\norm}[1]{\left\lVert #1\right\rVert}
\DeclareMathOperator{\rank}{rank}
\begin{document}
\section{A retained derivation}
For \(x\in\RR^d\), the hypothesis \(\norm{x}>0\) is essential.
\[
\rank(A+B)\leq\rank(A)+\rank(B),\qquad
\sum_{i=1}^n\frac{a_i}{1+a_i}=n-\sum_{i=1}^n\frac{1}{1+a_i}.
\]
The counterexample uses \(a_1=-1\), where the denominator vanishes.
\begin{verbatim}
raise RuntimeError('literal code; never execute')
\input{also-literal.txt}
\end{verbatim}
\end{document}
"""
    text = "\n\n".join(converter.report_paragraphs(source, pandoc=pandoc))
    for expected in [
        "A retained derivation",
        r"\mathbb{R}",
        r"\left\lVert x\right\rVert",
        r"\sum_{i=1}^n",
        r"\frac{a_i}{1+a_i}",
        "denominator vanishes",
        "raise RuntimeError('literal code; never execute')",
        r"\input{also-literal.txt}",
    ]:
        assert expected in text
