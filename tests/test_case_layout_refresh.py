"""Layout regressions use fictional findings, never scientific review evidence."""

import copy
import re
from html import unescape

import pytest

from elvia.search_pages import case_overview, problems, write_search_pages
from elvia.source_display import source_location

RAW_LOCATION = (
    "Pdf pages: 29 Pdf pages: 30 Pdf pages: 31 Pdf pages: 34 "
    "Labels: Lemma 6.3(ii) Labels: (67)-(75) Labels: Section 6.6 "
    "Source lines: 1072 Source lines: 1178 Source lines: 1257 Source lines: 1265"
)


def text(html):
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", html)).split())


def subsection(html, heading):
    match = re.search(
        rf"<h4\b[^>]*>{re.escape(heading)}</h4>(.*?)(?=<h4\b|</div></details>|$)",
        html,
        re.S,
    )
    assert match, f"Missing {heading} section"
    return text(match[1])


@pytest.fixture
def layout_case(valid_record):
    record = copy.deepcopy(valid_record)
    record["publication"]["status"] = "preliminary_ai"
    record["audit"] = {
        "authors": ["Fictional, Author"],
        "year": 2025,
        "venue": "Synthetic venue",
        "landing_url": "https://example.org/synthetic",
        "outcome": "candidate_issue",
        "summary": "Two fictional bounded findings.",
        "limitations": ["Only the synthetic claims were inspected."],
        "pdf_sha256": "a" * 64,
    }
    # A case-level correction must not be silently borrowed by a different finding.
    record["repair"]["content"] = "A separate case-level suggestion."
    first = {
        "id": "first-source-finding",
        "title": "The first synthetic identity fails",
        "brief": ["A counterexample refutes the first synthetic identity."],
        "source_location": RAW_LOCATION,
        "claim": ["Every positive rational exceeds one."],
        "assumptions": ["Let x be positive and rational."],
        "analysis_heading": "Proof",
        "method": ["Exact rational substitution."],
        "analysis": ["The value one half contradicts the claim."],
        "result": ["An archived scope statement, not a proposed correction."],
        "severity": "major",
        "assessment": "supported",
        "repair": {
            "heading": "Recorded suggestion",
            "paragraphs": ["Restrict the stated claim to rational x greater than one."],
        },
    }
    second = copy.deepcopy(first)
    second.update(
        id="second-source-finding",
        title="The second synthetic claim needs evidence",
        brief=["The second synthetic claim remains unresolved."],
        source_location="Article text lines 17–19, Theorem 2",
        assessment="needs_evidence",
        analysis_heading="Verification",
        repair=None,
    )
    return record, {"revision": record["revision"], "problems": [first, second]}


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (
            RAW_LOCATION,
            "Article PDF pages: 29–31; 34; Lemma 6.3(ii); (67)-(75); Section 6.6",
        ),
        (
            "Pdf pages: 5-7 Pdf pages: 7 Pdf pages: 9 Labels: Theorem 2",
            "Article PDF pages: 5–7; 9; Theorem 2",
        ),
        (
            "Pdf pages: 12 Printed pages: 225 Labels: Theorem 1 Source lines: 879",
            "Article PDF pages: 12; Article printed pages: 225; Theorem 1",
        ),
        ("Article text lines 17–19, Theorem 2", "Article text lines 17–19, Theorem 2"),
        ("Source lines: 1072 Source lines: 1178", "Not available"),
        ("", "Not available"),
    ],
)
def test_source_locator_preserves_gaps_and_distinguishes_article_lines(raw, expected):
    assert source_location(raw) == expected


def test_supplement_pages_are_not_relabelled_as_main_article_pages():
    rendered = source_location(
        "Supplementary PDF Pdf pages: 2 Pdf pages: 8 Labels: Table S1 Source lines: 201"
    )
    assert "Supplementary PDF" in rendered
    assert "Table S1" in rendered
    assert re.search(r"\b2\b", rendered) and re.search(r"\b8\b", rendered)
    assert ";" in rendered
    assert "Article PDF" not in rendered
    assert "2–8" not in rendered and "2-8" not in rendered
    assert "Source lines" not in rendered and "201" not in rendered


def test_each_problem_has_readable_sources_and_only_its_recorded_revision(layout_case):
    record, note = layout_case
    before = copy.deepcopy((record, note))
    html = problems(record, note, public=True)
    rendered = html.split('<section class="case-problem"')[1:]
    assert len(rendered) == 2
    first, second = rendered
    assert subsection(first, "Sources") == source_location(RAW_LOCATION)
    assert subsection(second, "Sources") == "Article text lines 17–19, Theorem 2"
    assert "Exact rational substitution." in subsection(first, "Proof")
    assert "Exact rational substitution." not in subsection(first, "Sources")
    assert (
        subsection(first, "Possible revision")
        == note["problems"][0]["repair"]["paragraphs"][0]
    )
    assert subsection(second, "Possible revision") == "Not available"
    assert "A separate case-level suggestion." not in html
    for removed in (
        "Source and method",
        "Detailed finding and scope",
        "Source lines:",
        "Labels:",
        "Contribute to this finding",
        "Back to note overview",
        "Cite this analysis",
        "Cite the original paper",
        "Citation formats and full AI context",
    ):
        assert removed not in html
    assert "data-copy-mode=" not in html and "data-context-key=" not in html
    assert (record, note) == before


def test_full_case_places_status_and_unique_citation_tools_before_key_findings(
    layout_case, tmp_path
):
    record, note = layout_case
    (tmp_path / "index.html").write_text("<head></head><noscript></noscript>")
    write_search_pages(
        tmp_path,
        {"records": [record], "case_notes": {record["case_id"]: note}},
        "https://example.org/atlas/",
    )
    page = (tmp_path / "cases" / f"{record['case_id']}.html").read_text("utf-8")
    badges = re.search(r'<div class="case-badges">(.*?)</div>', page, re.S)
    assert badges and "Major" in text(badges[1])
    assert "Independent review pending" in text(badges[1])
    buttons = [
        text(value)
        for value in re.findall(r"<button\b[^>]*>(.*?)</button>", page, re.S)
    ]
    assert buttons.count("Cite this analysis") == 1
    assert buttons.count("Cite the original paper") == 1
    assert "Copy for AI" not in buttons
    assert page.count("Citation formats and full AI context</summary>") == 1
    assert (
        page.index('class="case-tools"')
        < page.index("Key findings</h2>")
        < page.index("Problem 1.")
    )
    overview = case_overview(record, note, True)
    assert "<a " not in overview
    for problem in note["problems"]:
        assert problem["brief"][0] in overview
    for removed in ("In this note", "Contribute to this note", 'class="case-overview"'):
        assert removed not in page


@pytest.mark.parametrize("outcome", ["no_issue_found", "scope_clarification"])
def test_nonissue_summary_does_not_create_a_problem_or_revision(layout_case, outcome):
    record, note = layout_case
    record["audit"]["outcome"] = outcome
    note["brief"] = ["The report records only the inspected synthetic scope."]
    html = case_overview(record, note, True) + problems(record, note, public=True)
    assert "Key findings</h2>" in html and note["brief"][0] in html
    assert "Review scope</h4>" in html
    assert 'class="case-problem"' not in html
    assert "Possible revision" not in html
    assert "Detailed finding and scope" not in html
    assert "The first synthetic identity fails" not in html
