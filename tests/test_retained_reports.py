"""Complete retained report visibility and copy preservation, with synthetic text."""

import copy
import json
from html.parser import HTMLParser

import pytest

from elvia.case_notes import prepare_case_notes
from elvia.public_context import context_exports
from elvia.reader import record_digest
from elvia.search_pages import fallback_problems, write_search_pages


@pytest.fixture
def report_case(valid_record):
    record = copy.deepcopy(valid_record)
    record["audit"] = {
        "venue": "Synthetic conference",
        "year": 2026,
        "authors": ["Fictional author"],
        "landing_url": "https://example.org/fixture",
        "outcome": "no_issue_found",
        "summary": "No issue established in the inspected synthetic scope.",
        "limitations": ["This is an original software fixture only."],
        "pdf_sha256": "a" * 64,
    }
    report = [
        "Synthetic full retained report heading.",
        r"The finite check retains \(x=1/2\) and its bounded conclusion.",
        'Code:\nfor value in ["<script>", r"\\(literal\\)"]:\n    print(value)',
        "Adverse control: no empirical or global conclusion follows.",
    ]
    note = {
        "revision": record["revision"],
        "record_sha256": record_digest(record),
        "report": report,
    }
    return record, note


def catalog(record, note):
    return {"format_version": 1, "cases": {record["case_id"]: note}}


@pytest.mark.parametrize("problems", [None, []])
def test_snapshot_bound_report_only_note_is_accepted(report_case, problems):
    record, note = report_case
    if problems is not None:
        note["problems"] = problems
    assert prepare_case_notes([record], catalog=catalog(record, note)) == {
        record["case_id"]: note
    }


@pytest.mark.parametrize("value", [None, "not a paragraph list", [], ["   "], [3]])
def test_invalid_retained_report_is_rejected(report_case, value):
    record, note = report_case
    record["audit"]["outcome"] = "candidate_issue"
    note["record_sha256"] = record_digest(record)
    note["problems"] = fallback_problems(record)
    note["problems"][0].update(id="problem-1", evidence_ids=["ev-1"])
    note["report"] = value
    with pytest.raises(ValueError, match="report"):
        prepare_case_notes([record], catalog=catalog(record, note))


def test_retained_report_does_not_bypass_existing_problem_validation(report_case):
    record, note = report_case
    note["problems"] = [{"id": "invalid-incomplete-problem"}]
    with pytest.raises(ValueError, match="case note"):
        prepare_case_notes([record], catalog=catalog(record, note))


def test_full_copy_retains_report_and_code_without_expanding_short_copy(report_case):
    record, note = report_case
    exports = context_exports(record, {}, None, report=note["report"])
    for paragraph in note["report"]:
        assert paragraph in exports["ai-full"]
        assert paragraph not in exports["ai-short"]
    assert "Complete retained report:" in exports["ai-full"]
    assert "Independent review pending" in exports["ai-full"]
    assert "Source PDF SHA-256: " + record["audit"]["pdf_sha256"] in exports["ai-full"]


class ReportProbe(HTMLParser):
    def __init__(self):
        super().__init__()
        self.nodes = []

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))


@pytest.mark.parametrize("outcome", ["no_issue_found", "candidate_issue"])
def test_complete_report_is_in_initial_html_before_supporting_and_full_context(
    report_case, tmp_path, outcome
):
    record, note = report_case
    record["audit"]["outcome"] = outcome
    (tmp_path / "index.html").write_text("<head></head><noscript></noscript>")
    write_search_pages(
        tmp_path,
        {"records": [record], "case_notes": {record["case_id"]: note}},
    )
    page = (tmp_path / "cases" / f"{record['case_id']}.html").read_text("utf-8")
    assert "Complete retained report" in page
    assert page.index('class="problem-notes"') < page.index("Complete retained report")
    assert page.index("Complete retained report") < page.index(
        'id="supporting-evidence"'
    )
    assert note["report"][0] in page
    assert note["report"][-1] in page
    assert "&lt;script&gt;" in page and "<script>" not in page
    probe = ReportProbe()
    probe.feed(page)
    code = [attrs for tag, attrs in probe.nodes if tag == "pre"]
    assert code and all("data-case-prose" not in attrs for attrs in code)
    script = (tmp_path / "cases" / f"{record['case_id']}.js").read_text("utf-8")
    contexts = json.loads(
        script.split("window.ELVIA_CASE_CONTEXT = ", 1)[1].rstrip(";\n")
    )
    for paragraph in note["report"]:
        assert paragraph in contexts["case"]["ai-full"]
        assert paragraph not in contexts["case"]["ai-short"]


def test_note_without_retained_report_keeps_existing_case_html(report_case, tmp_path):
    record, note = report_case
    del note["report"]
    (tmp_path / "index.html").write_text("<head></head><noscript></noscript>")
    write_search_pages(tmp_path, {"records": [record]})
    page = (tmp_path / "cases" / f"{record['case_id']}.html").read_text("utf-8")
    assert "Complete retained report" not in page
