"""Synthetic public citations and context; never scientific review declarations."""

import copy
import json
from html.parser import HTMLParser

import pytest

from elvia.public_context import context_exports, finding_brief, presentation_points
from elvia.search_pages import case_overview, problems, supporting, write_search_pages


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


def test_static_problem_statement_and_proof_keep_history_out_of_visible_column(example):
    record, reader, problem = example
    problem["analysis_heading"] = "Proof"
    problem["claim_heading"] = "Problem statement"
    problem["method"] = ["Analytic two-path proof.", "Exact symbolic check."]
    problem["repair"] = {
        "heading": "Recorded correction",
        "paragraphs": ["A retained proposed solution."],
    }
    before = copy.deepcopy(problem)
    html = problems(record, {"problems": [problem]})
    assert ">Problem statement</h4>" in html
    assert html.count(">Problem statement<") == 1
    assert ">Proof</h4>" in html
    assert (
        html.index("Problem statement")
        < html.index("Source and method")
        < html.index(">Proof</h4>")
    )
    for method in problem["method"]:
        assert method in html
        for kind in ("ai-short", "ai-full"):
            assert method in context_exports(record, reader, None, problem, 1)[kind]
    assert '<p class="problem-statement scientific-prose"' in html
    assert " ".join(problem["assumptions"] + problem["claim"]) in html
    assert ">Conditions</h4>" not in html
    assert '<p class="proof-end scientific-prose"' in html
    assert html.index("\\(\\square\\)") < html.index("Detailed finding and scope")
    assert "A retained proposed solution." not in html
    assert "Recorded correction" not in html
    assert problem == before
    assert (
        "A retained proposed solution."
        in context_exports(record, reader, None, problem, 1)["ai-full"]
    )


def test_static_needs_evidence_keeps_verification_and_has_no_added_qed(example):
    record, _, problem = example
    problem.update(analysis_heading="Verification", assessment="needs_evidence")
    html = problems(record, {"problems": [problem]})
    assert ">Verification</h4>" in html
    assert ">Proof</h4>" not in html
    assert "proof-end" not in html


def test_explicit_local_proof_does_not_change_unresolved_historical_scope(example):
    record, _, problem = example
    record["audit"]["outcome"] = "needs_evidence"
    problem.update(analysis_heading="Proof", assessment="needs_evidence")
    before = copy.deepcopy((record, problem))
    html = problems(record, {"problems": [problem]})
    assert ">Proof</h4>" in html and "proof-end" in html
    assert (record, problem) == before


def test_static_severity_order_has_sequential_display_and_stable_source_links(
    example, tmp_path
):
    record, reader, problem = example
    candidates = [
        dict(
            problem,
            title=f"Original title {number}",
            id=f"original-{number}",
            claim=[f"Original statement {number}."],
            source_location=f"Original source {number}",
            **classification,
        )
        for number, classification in enumerate(
            [
                {"severity": "minor"},
                {"severity": "major"},
                {"severity": "moderate"},
                {"severity": "major", "assessment": "needs_evidence"},
                {"severity": "major", "assessment": "not_issue"},
                {"severity": "major"},
            ],
            1,
        )
    ]
    note = {"revision": record["revision"], "problems": candidates}
    before = copy.deepcopy(note)
    display_map = {source: display for display, source in enumerate([2, 6, 1, 3, 4], 1)}
    exports = {
        f"problem-{number}": context_exports(
            record, reader, None, item, number, display_number=display_map.get(number)
        )
        for number, item in enumerate(candidates, 1)
    }
    html = problems(record, note, exports=exports, reader_bundle=True)
    probe = DisclosureProbe(html)
    assert [node["attrs"]["id"] for node in probe.nodes if node["tag"] == "h3"] == [
        "problem-2",
        "problem-6",
        "problem-1",
        "problem-3",
        "problem-4",
    ]
    for number in (1, 2, 3, 4, 6):
        section = html.split(
            f'<section class="case-problem" aria-labelledby="problem-{number}"', 1
        )[1].split('<section class="case-problem"', 1)[0]
        display = display_map[number]
        assert f"Problem {display}. Original title {number}" in section
        assert f"Evidence and reasoning for Problem {display}" in section
        assert f'data-source-problem-id="original-{number}"' in section
        assert f'data-source-problem-number="{number}"' in section
        assert f'data-display-problem-number="{display}"' in section
        assert f"Original statement {number}." in section
        assert f"Original source {number}" in section
        assert f'data-context-key="problem-{number}"' in section
        assert f'id="problem-{number}-evidence"' in section
    nav = case_overview(record, note, False)
    assert [
        node["attrs"]["href"]
        for node in DisclosureProbe(nav).nodes
        if node["tag"] == "a"
    ] == ["#problem-2", "#problem-6", "#problem-1", "#problem-3", "#problem-4"]
    assert [
        node["attrs"]["data-display-problem-number"]
        for node in DisclosureProbe(nav).nodes
        if node["tag"] == "li"
    ] == ["1", "2", "3", "4", "5"]
    assert html.count('class="evidence-files-note"') == 1
    assert note == before
    assert 'id="problem-5"' not in html
    assert "Original title 5" not in nav
    assert "Original title 5" in exports["problem-5"]["ai-full"]
    (tmp_path / "index.html").write_text("<head></head><noscript></noscript>")
    write_search_pages(
        tmp_path,
        {
            "records": [record],
            "reader": {record["case_id"]: reader},
            "case_notes": {record["case_id"]: note},
        },
        "https://example.org/atlas/",
    )
    script = (tmp_path / "cases/synthetic-001.js").read_text("utf-8")
    actual = json.loads(
        script.split("window.ELVIA_CASE_CONTEXT = ", 1)[1].rstrip(";\n")
    )
    for source, display in display_map.items():
        for kind in (
            "analysis-plain",
            "analysis-bibtex",
            "analysis-ris",
            "ai-short",
            "ai-full",
        ):
            assert (
                f"Problem {display}: Original title {source}"
                in actual[f"problem-{source}"][kind]
            )
            assert f"#problem-{source}" in actual[f"problem-{source}"][kind]


def test_display_number_in_citation_never_changes_canonical_source_locator(example):
    record, reader, problem = example
    problem["id"] = "original-source-nine"
    packet = context_exports(record, reader, None, problem, 9, display_number=1)
    for kind in (
        "analysis-plain",
        "analysis-bibtex",
        "analysis-ris",
        "ai-short",
        "ai-full",
    ):
        assert "Problem 1: A bounded counterexample" in packet[kind]
        assert "#problem-9" in packet[kind]
    for kind in ("ai-short", "ai-full"):
        assert "Source problem ID: original-source-nine" in packet[kind]
        assert "Source report index: 9" in packet[kind]


def test_article_abstract_is_one_paragraph_and_nonissues_are_not_problems(
    example, tmp_path
):
    record, reader, problem = example
    note = {
        "revision": 1,
        "brief": [
            "The identity fails in the checked setting.",
            "The untested impact remains open.",
        ],
        "problems": [dict(problem, assessment="not_issue")],
    }
    html = case_overview(record, note, False) + problems(record, note)
    probe = DisclosureProbe(html)
    assert html.count("Analysis abstract</h2>") == 1
    assert (
        len(
            [
                node
                for node in probe.nodes
                if "analysis-abstract" in node["attrs"].get("class", "").split()
            ]
        )
        == 1
    )
    assert " ".join(note["brief"]) in html
    assert "Finding at a glance" not in html
    assert "finding-brief" not in html
    assert 'class="case-problem"' not in html
    assert "Detailed finding and scope" in html
    record["audit"]["outcome"] = "no_issue_found"
    (tmp_path / "index.html").write_text("<head></head><noscript></noscript>")
    write_search_pages(
        tmp_path,
        {
            "records": [record],
            "reader": {record["case_id"]: reader},
            "case_notes": {record["case_id"]: note},
        },
    )
    page = (tmp_path / "cases/synthetic-001.html").read_text("utf-8")
    assert 'class="severity-tag no_issue_found"' not in page


def test_inspection_subject_heading_is_consistent_in_html_and_full_copy(example):
    record, reader, problem = example
    problem["claim_heading"] = "Inspection subject recorded in the report"
    problem["claim"] = ["Recorded check: A fictional historical trace check."]
    html = problems(record, {"problems": [problem]})
    assert (
        'class="statement-role" data-case-prose>'
        "Inspection subject recorded in the report</p>" in html
    )
    assert ">Problem statement</h4>" in html
    assert "Claim in the source (paraphrase)</h4>" not in html
    full = context_exports(record, reader, None, problem, 1)["ai-full"]
    assert "Inspection subject recorded in the report:" in full
    assert "Source claim (paraphrase):" not in full
    case = context_exports(record, reader, None, report=["Synthetic retained text."])
    assert "Recorded claims and inspection subjects:" in case["ai-full"]
    assert "\nSource claim:\n" not in case["ai-full"]
    assert "\nSource claim:\n" in context_exports(record, reader, None)["ai-full"]


def test_source_excerpt_keeps_verbatim_text_locator_and_pdf_binding_in_html_and_copy(
    example,
    tmp_path,
):
    record, reader, problem = example
    quote = {
        "text": r"For every \(x>0\), \(f(x)>1\).",
        "locator": "Page 2, Theorem 1",
        "source_identity": "Fictional paper, frozen proceedings version",
        "source_sha256": record["audit"]["pdf_sha256"],
    }
    note = {
        "revision": record["revision"],
        "source_quotes": [quote],
        "problems": [problem],
    }
    before = copy.deepcopy((record, note))
    html = supporting(record, reader, note)
    probe = DisclosureProbe(html)
    assert len([node for node in probe.nodes if node["tag"] == "blockquote"]) == 1
    assert (
        '<blockquote class="source-quote"><p class="scientific-prose" data-case-prose>'
        in html
    )
    assert quote["text"].replace(">", "&gt;") in html
    assert quote["locator"] in html and quote["source_identity"] in html
    assert record["proposition"]["claim"] not in html
    assert "<ul>" not in html.split("<h3>Original claim and review scope</h3>", 1)[1]
    for selected in (None, problem):
        for kind in ("ai-short", "ai-full"):
            copied = context_exports(
                record,
                reader,
                None,
                selected,
                1 if selected else None,
                source_quotes=[quote],
            )[kind]
            for field in ("text", "locator", "source_identity", "source_sha256"):
                assert quote[field] in copied
    assert (record, note) == before
    fallback = supporting(record, reader)
    assert "blockquote" not in fallback
    assert "Source location" in fallback
    assert record["proposition"]["claim"] not in fallback
    assert record["proposition"]["location"] in fallback
    assert supporting(record, reader, {"source_quotes": []}) == fallback
    (tmp_path / "index.html").write_text("<head></head><noscript></noscript>")
    write_search_pages(
        tmp_path,
        {
            "records": [record],
            "reader": {record["case_id"]: reader},
            "case_notes": {record["case_id"]: note},
        },
    )
    page = (tmp_path / "cases/synthetic-001.html").read_text("utf-8")
    assert '<blockquote class="source-quote">' in page
    script = (tmp_path / "cases/synthetic-001.js").read_text("utf-8")
    packets = json.loads(
        script.split("window.ELVIA_CASE_CONTEXT = ", 1)[1].rstrip(";\n")
    )
    for key in ("case", "problem-1"):
        for kind in ("ai-short", "ai-full"):
            assert quote["text"] in packets[key][kind]
            assert quote["locator"] in packets[key][kind]


def test_supporting_scope_uses_editorial_paragraphs_without_flattened_record_metadata(
    example,
):
    record, reader, _ = example
    record["proposition"]["domain"] = "N0:2/N1:1/Target:2"
    record["proposition"]["assumptions"] = ["Raw field: synthetic-target=2"]
    record["proposition"]["dependencies"] = [
        record["evidence"][0]["id"],
        "E7",
        "The stated differentiability hypothesis.",
    ]
    record["source"]["review_scope"] = "Completed report; see coverage ledger."
    note = {
        "review_scope": [
            "The review concerns only the displayed scalar identity.",
            "Empirical results were not tested.",
        ]
    }
    before = copy.deepcopy((record, note))
    html = supporting(record, reader, note)
    for text in note["review_scope"]:
        assert text in html
        assert (
            text
            in context_exports(record, reader, None, review_scope=note["review_scope"])[
                "ai-full"
            ]
        )
    assert "The stated differentiability hypothesis." in html
    for text in [
        record["proposition"]["domain"],
        *record["proposition"]["assumptions"],
        record["source"]["review_scope"],
    ]:
        assert text not in html
        assert text in context_exports(record, reader, None)["ai-full"]
    assert ">E7<" not in html
    assert (record, note) == before
    fallback = supporting(record, reader)
    assert "Completed report" not in fallback and "N0:2" not in fallback


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
    assert "Analysis abstract" in page
    assert "Finding at a glance" not in page
    assert "Evidence and reasoning for Problem 1" in page
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


class DisclosureProbe(HTMLParser):
    """Read the HTML as a no-JavaScript visitor, retaining closed-details scope."""

    def __init__(self, html):
        super().__init__()
        self.stack = []
        self.nodes = []
        self.text = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        node = {"tag": tag, "attrs": dict(attrs), "ancestors": list(self.stack)}
        self.nodes.append(node)
        if tag not in {"input", "br", "hr", "meta", "link", "img"}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]["tag"] == tag:
                self.stack = self.stack[:index]
                break

    def handle_data(self, data):
        closed = any(
            n["tag"] == "details" and "open" not in n["attrs"] for n in self.stack
        )
        self.text.append((data, closed))


def test_problem_details_keep_concise_points_visible_and_full_evidence_in_html(
    example,
):
    record, reader, problem = example
    problem["result"].append("The original special case remains valid.")
    problem["brief"] = [
        "A bounded counterexample; the original special case remains valid."
    ]
    problem["analysis"].append("Countercontrol: input 2 satisfies the source claim.")
    problem["repair"] = {
        "heading": "Proposed correction",
        "paragraphs": [
            "Restrict the input to numbers greater than one.",
            "Adoption is not established.",
        ],
    }
    exports = {"problem-1": context_exports(record, reader, None, problem, 1)}
    note = {
        "revision": 1,
        "problems": [problem],
        "brief": ["A bounded synthetic counterexample has limited impact."],
    }
    html = case_overview(record, note, False) + problems(record, note, True, exports)
    probe = DisclosureProbe(html)
    visible = " ".join(text for text, closed in probe.text if not closed)
    folded = " ".join(text for text, closed in probe.text if closed)
    evidence = next(
        node for node in probe.nodes if node["attrs"].get("id") == "problem-1-evidence"
    )
    assert evidence["tag"] == "details" and "open" not in evidence["attrs"]
    assert note["brief"][0] in visible
    assert "Finding at a glance" not in html
    for value in (
        *problem["result"],
        problem["source_location"],
        *problem["claim"],
        *problem["assumptions"],
        *problem["analysis"],
    ):
        assert value in folded
        assert value not in visible
        assert html.count(value) == 1
    for value in problem["repair"]["paragraphs"]:
        assert value not in html
        assert value in exports["problem-1"]["ai-full"]
    tools = next(
        node
        for node in probe.nodes
        if node["attrs"].get("data-context-key") == "problem-1"
    )
    heading = next(
        node for node in probe.nodes if node["attrs"].get("id") == "problem-1"
    )
    assert not any(n["tag"] == "details" for n in tools["ancestors"])
    assert not any(n["tag"] == "details" for n in heading["ancestors"])
    assert "<dt>" not in html
    assert "Inspected source" not in visible
    assert "What does the recorded analysis establish" not in visible


@pytest.mark.parametrize("outcome", ["no_issue_found", "scope_clarification"])
def test_non_problem_cases_have_closed_evidence_and_visible_short_summary(
    example, outcome
):
    record, reader, _ = example
    record["audit"]["outcome"] = outcome
    html = (
        case_overview(record, {}, False)
        + problems(record, {})
        + supporting(record, reader)
    )
    probe = DisclosureProbe(html)
    evidence = next(
        node for node in probe.nodes if node["attrs"].get("id") == "supporting-evidence"
    )
    assert evidence["tag"] == "details" and "open" not in evidence["attrs"]
    assert "Read the evidence and review scope" in html
    visible = " ".join(text for text, closed in probe.text if not closed)
    assert record["audit"]["summary"] in visible
    folded = " ".join(text for text, closed in probe.text if closed)
    for text in record["audit"]["limitations"]:
        assert text in folded and text not in visible
    assert "The recorded inspection concerns these source locations:" in folded
    assert "Independent review pending" in folded
    assert 'id="case-evidence"' in html


def test_display_brief_is_short_while_full_result_and_global_scope_stay_in_evidence(
    example,
):
    record, _, problem = example
    problem["brief"] = [
        "A bounded synthetic statement fails.",
        "The untested case stays open.",
    ]
    problem["result"] = ["Full result: " + "exact witness " * 100]
    record["audit"]["limitations"] = ["Unique case-wide limitation."]
    problem["result"].append("Unique case-wide limitation.")
    problem["analysis"].append("A unique adverse control survives.")
    record["evidence"].append(
        {
            "id": "rebuttal",
            "stance": "rebuttal",
            "description": "A unique adverse control survives.",
            "artifact": {"path": "control.txt"},
        }
    )
    note = {
        "revision": 1,
        "problems": [problem],
        "brief": ["A bounded counterexample has limited impact."],
    }
    html = case_overview(record, note, False) + problems(record, note)
    probe = DisclosureProbe(html)
    visible = " ".join(text for text, closed in probe.text if not closed)
    folded = " ".join(text for text, closed in probe.text if closed)
    assert note["brief"][0] in visible
    assert "finding-brief" not in html
    for detailed in (
        *problem["result"],
        *record["audit"]["limitations"],
        "A unique adverse control survives.",
    ):
        assert detailed in folded and detailed not in visible
    assert "<dt>" not in html
    assert "Inspected source" not in visible
    assert "Case-wide scope and evidence" not in html


def test_case_wide_metadata_is_omitted_and_zip_support_is_named_once(
    example,
):
    record, _, problem = example
    record["audit"]["limitations"] = ["A shared scientific qualification."]
    html = problems(
        record,
        {"problems": [problem, {**problem, "id": "p2", "title": "Second check"}]},
        reader_bundle=True,
    )
    assert "Case-wide scope and evidence" not in html
    assert 'id="case-scope-evidence"' not in html
    assert 'href="#case-scope-evidence"' not in html
    notice = "Supporting files are included in Download report files (.zip)."
    assert html.count(notice) == 1
    assert html.count(problem["analysis"][0]) == 2
    probe = DisclosureProbe(html)
    folded = " ".join(text for text, closed in probe.text if closed)
    assert folded.count(problem["result"][0]) == 2


@pytest.mark.parametrize(
    "outcome", ["needs_evidence", "candidate_issue", "known_issue_reproduced"]
)
def test_empty_assessment_summary_never_becomes_no_issue(example, outcome):
    record, _, _ = example
    record["audit"]["outcome"] = outcome
    record["audit"]["summary"] = "Archived assessment: Needs Evidence."
    points = presentation_points(record)
    assert points and "No issue" not in " ".join(points)
    assert record["audit"]["outcome"] == outcome
