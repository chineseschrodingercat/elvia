"""Synthetic public citations and context; never scientific review declarations."""

import copy
import json

import pytest

from elvia.public_context import context_exports, finding_brief
from elvia.search_pages import write_search_pages


@pytest.fixture
def example(valid_record):
    record = copy.deepcopy(valid_record)
    record["audit"] = {
        "authors": ["Original, Author"],
        "year": 2025,
        "venue": "Fictional venue",
        "landing_url": "https://example.org/paper",
        "outcome": "candidate_issue",
        "summary": "Two synthetic findings only.",
        "limitations": ["No empirical impact established."],
        "pdf_sha256": "a" * 64,
    }
    record["publication"]["status"] = "preliminary_ai"
    reader = {
        "revision": 1,
        "contributors": [
            {"name": "Report Writer", "role": "Initial report", "revision": 1},
            {"name": "Fixture Reviewer", "role": "Reviewer", "revision": 1},
        ],
    }
    problem = {
        "title": "A bounded counterexample",
        "source_location": "Equation (1)",
        "claim": ["All positive rationals exceed one."],
        "assumptions": ["Positive rational input only."],
        "analysis_heading": "Exact check",
        "analysis": ["The value 1/2 is positive and less than one."],
        "result": ["The displayed universal statement fails; no other claim tested."],
        "severity": "major",
        "assessment": "supported",
        "repair": None,
    }
    return record, reader, problem


def test_analysis_citations_do_not_borrow_original_authors_or_reviewer(example):
    record, reader, problem = example
    exports = context_exports(record, reader, "https://example.org/atlas/", problem, 1)
    for kind in ("plain", "bibtex", "ris"):
        analysis = exports[f"analysis-{kind}"]
        assert "Report Writer" in analysis
        assert "Original, Author" not in analysis
        assert "Fixture Reviewer" not in analysis
        assert "pending" in analysis.lower()
        assert "#problem-1" in analysis
        original = exports[f"original-{kind}"]
        assert "Original, Author" in original
        assert "Report Writer" not in original
    assert "DO  -" not in exports["analysis-ris"]
    assert "author =" not in context_exports(record, {}, None)["analysis-bibtex"]


def test_selected_ai_packet_preserves_limits_status_and_exact_record_identity(example):
    record, reader, problem = example
    exports = context_exports(record, reader, "https://example.org/atlas/", problem, 1)
    for kind in ("short", "full"):
        text = exports[f"ai-{kind}"]
        for expected in (
            problem["result"][0],
            "No empirical impact established.",
            "Independent review pending",
            "Source version: 1",
            "Equation (1)",
            "Revision: 1",
            "#problem-1",
            "Original, Author",
            "synthetic-001.r1.json",
            "Canonical record SHA-256:",
        ):
            assert expected in text
        assert "Two synthetic findings only." not in text
    assert problem["analysis"][0] in exports["ai-full"]
    assert "Repair verification: not_proposed" in exports["ai-full"]
    assert "Author adoption: not_requested" in exports["ai-full"]


def test_finding_brief_does_not_shorten_away_scope_or_promote_supported(example):
    record, _, problem = example
    brief = finding_brief(record, problem)
    assert brief["answer"] == problem["result"]
    assert brief["evidence"] == problem["analysis"]
    assert brief["status"] == "Independent review pending"
    assert "?" in brief["question"]
    assert brief["limits"] == record["audit"]["limitations"]


def test_decisive_check_keeps_setup_calculation_and_countercontrol_together(example):
    record, reader, problem = example
    problem["analysis"] = [
        "For six tokens, take full positive probability vectors.",
        "The synthetic vectors produce 0.2 and 0.3, a strict inequality.",
        "The equal-vector control instead produces equality; no runtime claim follows.",
    ]
    brief = finding_brief(record, problem)
    assert brief["evidence"] == problem["analysis"]
    short = context_exports(record, reader, None, problem, 1)["ai-short"]
    for paragraph in problem["analysis"]:
        assert paragraph in short


def test_original_bibtex_uses_proceedings_and_protects_scientific_title_case(example):
    record, reader, _ = example
    record["source"]["title"] = "DFloat11: LLM Test"
    exports = context_exports(record, reader, None)
    assert exports["original-bibtex"].startswith("@inproceedings{")
    assert "title = {{DFloat11: LLM Test}}" in exports["original-bibtex"]
    assert (
        "title = {{ELVIA analysis of: DFloat11: LLM Test}}"
        in exports["analysis-bibtex"]
    )


def test_case_html_includes_readable_brief_and_manual_copy_fallback(example, tmp_path):
    record, reader, problem = example
    problem["title"] = '</script><img src=x onerror="oops">'
    (tmp_path / "index.html").write_text("<head></head><noscript></noscript>")
    write_search_pages(
        tmp_path,
        {
            "records": [record],
            "reader": {record["case_id"]: reader},
            "case_notes": {record["case_id"]: {"revision": 1, "problems": [problem]}},
        },
        "https://example.org/atlas/",
    )
    page = (tmp_path / "cases/synthetic-001.html").read_text("utf-8")
    assert "Finding at a glance" in page
    assert "Recorded check" in page
    assert "Cite this analysis" in page
    assert "Cite the original paper" in page
    assert "Copy for AI" in page
    assert 'data-context-key="problem-1"' in page
    assert "readonly" in page
    assert 'name="citation_title"' in page
    assert 'name="citation_author" content="Report Writer"' in page
    assert 'name="citation_author" content="Original, Author"' not in page
    assert "</script><img src=x" not in page
    script = (tmp_path / "cases/synthetic-001.js").read_text("utf-8")
    assert "window.ELVIA_CASE_CONTEXT =" in script
    assert "</script>" not in script
    value = json.loads(script.split("window.ELVIA_CASE_CONTEXT = ", 1)[1].rstrip(";\n"))
    assert "problem-1" in value
    assert problem["title"] in value["problem-1"]["ai-full"]


def test_bibtex_escapes_latex_and_ris_cannot_inject_fields(example):
    record, reader, _ = example
    record["source"]["title"] = "A {brace} & 50%_value\nAU  - Fake Author"
    exports = context_exports(record, reader, None)
    assert r"\{brace\}" in exports["original-bibtex"]
    assert r"\& 50\%\_value" in exports["original-bibtex"]
    assert "\nAU  - Fake Author" not in exports["original-ris"]
