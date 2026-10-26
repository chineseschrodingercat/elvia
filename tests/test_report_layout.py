"""Report-layout regressions using literal synthetic URL and hash strings."""

import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def formatter():
    path = Path(__file__).resolve().parents[1] / "website/reader_library.py"
    spec = importlib.util.spec_from_file_location("reader_library_layout", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.format_report


def test_plain_urls_and_hashes_get_breakable_typesetting_without_double_wrapping(
    formatter,
):
    url = "https://example.org/" + "long-segment/" * 12 + r"source\_file.py"
    digest = "abcdef0123456789" * 4
    existing = r"\url{https://example.org/already\_wrapped}"
    source = r"\begin{document}" + url + " " + digest + " " + existing
    result = formatter(source)
    assert r"\nolinkurl{" + url.replace(r"\_", "_") + "}" in result
    assert r"\nolinkurl{" + digest + "}" in result
    assert existing in result
    assert r"\nolinkurl{\url" not in result
    assert r"\url{\nolinkurl" not in result


def test_bracketed_prose_after_line_break_cannot_be_parsed_as_spacing(formatter):
    source = "Batch token:\\\\\n[internal identifier omitted]"
    result = formatter(source)
    assert "\\\\{}\n[internal identifier omitted]" in result
    assert result.replace("\\\\{}", "\\\\") == source


def test_url_and_hash_changes_do_not_rewrite_mathematical_spans(formatter):
    source = r"\(x_{abcdef0123456789abcdef0123456789abcdef01}>0\)"
    assert formatter(source) == source


def test_unicode_math_font_argument_in_script_gets_explicit_grouping(formatter):
    source = r"\[T_\mathcal M(x)=p^\mathcal M_j(x)\xi_j\]"
    result = formatter(source)
    assert r"T_{\mathcal{M}}(x)=p^{\mathcal{M}}_j(x)" in result


def test_blank_lines_inside_display_math_do_not_create_tex_paragraphs(formatter):
    source = "\\[\\begin{aligned}\n\n x&=1\\\\\n y&=2\n\\end{aligned}\\]"
    assert "\n\n" not in formatter(source)
    assert "x&=1\\\\\n y&=2" in formatter(source)


def test_glued_commit_and_long_function_path_can_wrap_without_changing_text(formatter):
    digest = "abcdef0123456789abcdef0123456789abcdef01"
    location = (
        r"metrics/precision\_recall\_cover/precision\_recall\_cover\_computer.py::"
        r"PrecisionRecallCoverComputer.compute\_metric"
    )
    result = formatter("commit" + digest + " " + location)
    assert "commit" + r"\nolinkurl{" + digest + "}" in result
    assert r"\nolinkurl{" + location.replace(r"\_", "_") + "}" in result


def test_code_indentation_remains_visible_in_the_compiled_copy(formatter):
    source = (
        "{\\ttfamily\\footnotesize for member in [True, False]:\\\\\n"
        "    response = int(member)\\\\\n"
        "        nested = True}\\par"
    )
    result = formatter(source)
    assert "\n\\hspace*{4\\fontdimen2\\font}response" in result
    assert "\n\\hspace*{8\\fontdimen2\\font}nested" in result
    assert source.replace("    ", "") not in result


def test_compact_code_dictionary_can_wrap_at_visible_punctuation(formatter):
    source = r"{\ttfamily\footnotesize 'n':len(nums),'sum':sum(nums)}\par"
    result = formatter(source)
    assert r"'n':\allowbreak{}len(nums),\allowbreak{}'sum':" in result
    assert result.replace(r"\allowbreak{}", "") == source
