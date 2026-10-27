"""Readable, escaped HTML from the same validated snapshots as the Atlas UI."""

import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from xml.etree.ElementTree import Element, SubElement, tostring

from elvia.public_context import (
    analysis_authors,
    context_exports,
    presentation_points,
    review_status,
)

LABELS = {
    "major": "Major",
    "minor": "Minor",
    "needs_evidence": "Needs Evidence",
    "no_issue_found": "No Issue Found",
}


def assessment(record):
    outcome = record["audit"]["outcome"]
    if outcome == "needs_evidence":
        return outcome
    if outcome in {"no_issue_found", "scope_clarification"}:
        return "no_issue_found"
    severity = record["concern"]["severity"]
    return {"critical": "major", "moderate": "minor"}.get(severity, severity)


def prose(value, tag="p", css="", *, scientific=False):
    if scientific:
        css = " ".join(filter(None, [css, "scientific-prose"]))
    attribute = f' class="{escape(css)}"' if css else ""
    return f"<{tag}{attribute} data-case-prose>{escape(str(value))}</{tag}>"


def paragraphs(values, *, scientific=False):
    return "".join(prose(value, scientific=scientific) for value in values if value)


def items(values, *, scientific=False):
    return (
        "<ul>"
        + "".join(prose(value, "li", scientific=scientific) for value in values)
        + "</ul>"
    )


def problem_statement(problem):
    """Keep complete edited premises and the challenged statement together."""
    return " ".join(
        value.strip()
        for value in [*problem.get("assumptions", []), *problem.get("claim", [])]
        if value.strip()
    )


def proof_heading(problem):
    explicit = problem.get("analysis_heading", "").strip() == "Proof"
    return "Proof" if explicit and any(problem.get("analysis", [])) else "Verification"


def problem_assessment(problem):
    if problem.get("assessment") == "not_issue":
        return "no_issue_found"
    if problem.get("assessment") == "needs_evidence":
        return "needs_evidence"
    return {"moderate": "minor"}.get(problem.get("severity"), problem.get("severity"))


def ordered_problems(entries):
    """Order visible findings while preserving their original report numbers."""
    ranks = {"major": 0, "minor": 1, "needs_evidence": 2}
    selected = [
        (number, problem)
        for number, problem in enumerate(entries, 1)
        if problem_assessment(problem) != "no_issue_found"
    ]
    return sorted(selected, key=lambda item: ranks.get(problem_assessment(item[1]), 3))


def method_paragraphs(problem):
    method = problem.get("method", [])
    return [method] if isinstance(method, str) else method


def proof_marker(problem):
    if proof_heading(problem) != "Proof":
        return ""
    text = " ".join(problem["analysis"]).strip()
    if re.search(r"(?:[□◻]|Q\.?E\.?D\.?|\\\(\\(?:square|Box)\\\))\s*$", text):
        return ""
    return prose(r"\(\square\)", css="proof-end", scientific=True)


def external(url, label):
    parts = urlsplit(url)
    if (
        parts.scheme != "https"
        or not parts.hostname
        or parts.username
        or parts.password
    ):
        return escape(label)
    return f'<a href="{escape(url)}" rel="noopener noreferrer">{escape(label)}</a>'


def citation(record, reader):
    c = reader.get("citation")
    if not c:
        return (
            escape(", ".join(record["audit"]["authors"]))
            + ". “"
            + prose(record["source"]["title"], "span")
            + ".” "
            + "<em>"
            + escape(record["audit"]["venue"])
            + "</em>, "
            + str(record["audit"]["year"])
            + ". "
            + external(record["audit"]["landing_url"], "Original article")
        )
    authors = c["authors"]
    credit = authors[0] + "."
    if len(authors) > 2:
        credit = authors[0] + ", et al."
    elif len(authors) == 2:
        credit = (
            authors[0] + ", and " + " ".join(reversed(authors[1].split(", "))) + "."
        )
    title = " ".join(c["title"].split())
    title_punctuation = "" if title.endswith((".", "!", "?")) else "."
    first, last = c.get("first_page", ""), c.get("last_page", "")
    end = last or first
    if first.isdigit() and end.isdigit() and len(first) == len(end):
        common = 0
        while common < len(end) - 2 and first[common] == end[common]:
            common += 1
        end = end[common:]
    pages = (
        ""
        if not first
        else (f", p. {first}" if not last or first == last else f", pp. {first}–{end}")
    )
    editors = c.get("editors", [])
    suffix = (
        (", edited by " + editors[0] + (" et al." if len(editors) > 1 else ""))
        if editors
        else ""
    )
    publisher = re.sub(r",? Inc\.$", "", c.get("publisher", ""))
    suffix += f", vol. {c['volume']}, " + (publisher + ", " if publisher else "")
    suffix += str(c["year"]) + pages + ", "
    source_url = "https://doi.org/" + c["doi"] if c.get("doi") else c["source_url"]
    return (
        escape(credit + " “")
        + prose(title, "span")
        + escape(title_punctuation + "” ")
        + "<em>"
        + escape(c["container"])
        + "</em>"
        + escape(suffix)
        + external(source_url, source_url)
        + "."
    )


def fallback_problems(record):
    repair = record["repair"]
    applicable = repair["content"] and record["audit"]["outcome"] in {
        "candidate_issue",
        "known_issue_reproduced",
    }
    return [
        {
            "title": "The recorded claim",
            "source_location": record["proposition"]["location"],
            "claim": [record["proposition"]["claim"]],
            "assumptions": [
                record["proposition"]["domain"],
                *record["proposition"]["assumptions"],
            ],
            "analysis_heading": "Known issue analysis"
            if record["audit"]["outcome"] == "known_issue_reproduced"
            else "Analysis",
            "analysis": [
                record["concern"]["description"],
                *[
                    e["description"]
                    for e in record["evidence"]
                    if e["stance"] == "support"
                ],
            ],
            "result": [record["audit"]["summary"], *record["audit"]["limitations"]],
            "brief": presentation_points(record),
            "repair": {
                "heading": "Proposed correction",
                "paragraphs": [
                    repair["content"],
                    *repair["changed_assumptions"],
                    repair["changed_conclusion"],
                ],
            }
            if applicable
            else None,
        }
    ]


def contribution_url(record, number=None):
    query = {"case": record["case_id"]}
    if number is not None:
        query["problem"] = number
    return "/participate.html?" + urlencode(query)


def evidence_files_note():
    return prose(
        "Supporting files are included in Download report files (.zip).",
        css="evidence-files-note",
    )


def case_evidence_disclosure(record, note, reader_bundle=False):
    return (
        '<details class="evidence-details" id="case-evidence">'
        '<summary>Evidence and reasoning</summary><div class="evidence-content">'
        + (evidence_files_note() if reader_bundle else "")
        + "<h4>Detailed finding and scope</h4>"
        + paragraphs(record["audit"]["limitations"], scientific=True)
        + "</div></details>"
    )


def context_tools(exports, key):
    """Useful static fallback; JavaScript adds clipboard controls progressively."""
    options = (
        ("analysis-plain", "This analysis — plain text"),
        ("analysis-bibtex", "This analysis — BibTeX"),
        ("analysis-ris", "This analysis — RIS"),
        ("original-plain", "Original paper — plain text"),
        ("original-bibtex", "Original paper — BibTeX"),
        ("original-ris", "Original paper — RIS"),
        ("ai-short", "Copy for AI — short context"),
        ("ai-full", "Copy for AI — full context"),
    )
    text = (
        f'<section class="case-tools" data-context-key="{escape(key)}" '
        'aria-label="Citations and AI context"><div class="case-copy-actions">'
    )
    for mode, label in (
        ("analysis-plain", "Cite this analysis"),
        ("original-plain", "Cite the original paper"),
        ("ai-short", "Copy for AI"),
    ):
        text += f'<button type="button" data-copy-mode="{mode}" hidden>{label}</button>'
    text += (
        '</div><details class="copy-options"><summary>'
        "Citation formats and full AI context</summary>"
        "<p>Choose the analysis or the original paper as the citation target. "
        "Copy for AI includes public evidence, scope and review status; "
        "nothing is sent to an AI service.</p>"
        f'<label class="copy-format" hidden for="copy-format-{key}">Content</label>'
        f'<select id="copy-format-{key}" data-copy-format hidden>'
    )
    text += "".join(
        f'<option value="{mode}">{label}</option>' for mode, label in options
    )
    text += (
        f'</select><label for="copy-text-{key}">Text to copy</label>'
        f'<textarea id="copy-text-{key}" data-copy-text readonly rows="7" '
        'spellcheck="false">' + escape(exports["analysis-plain"]) + "</textarea>"
        '<div class="case-copy-actions"><button type="button" '
        "data-copy-selected hidden>Copy selected text</button></div>"
        "<noscript><p>Select and copy the citation above. More formats and "
        "AI context are available when JavaScript is enabled.</p></noscript>"
        '</details><p class="copy-status" role="status" aria-live="polite"></p>'
        "</section>"
    )
    return text


def case_overview(record, note, public):
    status = record["adjudication"]["status"]
    label = (
        "Independent review pending"
        if status == "pending"
        else status.replace("_", " ").capitalize()
    )
    origin = (
        "Preliminary AI analysis. "
        if record.get("publication", {}).get("status") == "preliminary_ai"
        else ""
    )
    text = '<section class="case-overview" aria-label="Review status and summary">'
    text += '<p class="case-review-status">' + escape(label) + "</p>"
    text += prose(
        origin
        + "Assessment applies to the inspected claims and scope, not the whole paper."
    )
    text += "<h2>Analysis abstract</h2>"
    text += prose(
        " ".join(presentation_points(record, note=note)),
        css="analysis-abstract",
        scientific=True,
    )
    if public:
        text += (
            f'<a class="case-contribute" href="{escape(contribution_url(record))}">'
            "Contribute to this note</a>"
        )
    text += "</section>"
    if record["audit"]["outcome"] not in {"no_issue_found", "scope_clarification"}:
        entries = ordered_problems(note.get("problems") or fallback_problems(record))
        if entries:
            text += (
                '<nav class="case-contents" aria-label="Contents of this note">'
                "<h2>In this note</h2><ol>"
            )
            text += "".join(
                f'<li data-display-problem-number="{display}">'
                f'<a href="#problem-{number}">{escape(problem["title"])}</a></li>'
                for display, (number, problem) in enumerate(entries, 1)
            )
            text += "</ol></nav>"
    return text


def problems(record, note, public=False, exports=None, *, reader_bundle=False):
    outcome = record["audit"]["outcome"]
    if outcome == "no_issue_found":
        return (
            '<section class="case-result no-issue-result"><p>'
            "No issue was found within the scope of this check.</p></section>"
            + case_evidence_disclosure(record, note, reader_bundle)
        )
    if outcome == "scope_clarification":
        return (
            '<section class="case-result scope-result"><h3>Scope clarification</h3>'
            + "</section>"
            + case_evidence_disclosure(record, note, reader_bundle)
        )
    entries = ordered_problems(note.get("problems") or fallback_problems(record))
    if not entries:
        return (
            '<p class="case-result">The recorded checks and their scope '
            "are retained below.</p>"
            + case_evidence_disclosure(record, note, reader_bundle)
        )
    content = []
    for position, (number, problem) in enumerate(entries):
        display_number = position + 1
        content.append(
            f'<section class="case-problem" aria-labelledby="problem-{number}" '
            f'data-source-problem-id="{escape(problem.get("id", f"source-{number}"))}" '
            f'data-source-problem-number="{number}" '
            f'data-display-problem-number="{display_number}">'
            f'<h3 id="problem-{number}" data-case-prose>'
            + escape(f"Problem {display_number}. {problem['title']}")
            + "</h3>"
        )
        if problem.get("severity"):
            key = problem_assessment(problem)
            content.append(
                f'<span class="severity-tag {escape(key)}">'
                f"{escape(LABELS.get(key, key))}</span>"
            )
        if exports:
            content.append(
                context_tools(exports[f"problem-{number}"], f"problem-{number}")
            )
        content.append(
            f'<details class="evidence-details" id="problem-{number}-evidence">'
            f"<summary>Evidence and reasoning for Problem {display_number}</summary>"
            '<div class="evidence-content">'
            f'<h4 id="problem-{number}-claim">'
            + "Problem statement"
            + "</h4>"
            + (
                prose(problem["claim_heading"], css="statement-role")
                if problem.get("claim_heading")
                and problem["claim_heading"]
                not in {"Claim in the source (paraphrase)", "Problem statement"}
                else ""
            )
            + prose(
                problem_statement(problem), css="problem-statement", scientific=True
            )
            + "<h4>Source and method</h4>"
            + prose("Source. " + problem["source_location"], css="source-citation")
            + paragraphs(method_paragraphs(problem), scientific=True)
            + (evidence_files_note() if position == 0 and reader_bundle else "")
        )
        content.append(
            f'<h4 id="problem-{number}-analysis" data-case-prose>'
            + proof_heading(problem)
            + "</h4>"
            + paragraphs(problem["analysis"], scientific=True)
            + proof_marker(problem)
        )
        content.append(
            "<h4>Detailed finding and scope</h4>"
            + paragraphs(problem["result"], scientific=True)
        )
        content.append("</div></details>")
        if public:
            content.append(
                '<p class="problem-action">'
                f'<a href="{escape(contribution_url(record, number))}">'
                'Contribute to this finding</a> · <a href="#detail-title">'
                "Back to note overview</a></p>"
            )
        content.append("</section>")
    return "".join(content)


def supporting(record, reader, note=None):
    summary = (
        "Read the evidence and review scope"
        if record["audit"]["outcome"] in {"no_issue_found", "scope_clarification"}
        else "Supporting record & provenance"
    )
    text = (
        '<details class="supporting-record evidence-details" id="supporting-evidence">'
        "<summary>" + escape(summary) + "</summary>"
        '<div class="supporting-content">'
    )
    text += (
        '<section class="detail-section"><h3>Work status</h3>'
        '<p class="detail-label">Current version</p>'
        + prose(f"Version {record['revision']}")
    )
    if reader.get("contributors"):
        text += prose(
            "; ".join(
                [
                    f"{p['name']} · {p['role']} · Version {p['revision']}"
                    for p in reader["contributors"]
                ]
            )
        )
    status = record["adjudication"]["status"]
    text += (
        prose(
            "Independent review pending"
            if status == "pending"
            else status.replace("_", " ").capitalize()
        )
        + "</section>"
    )
    text += '<section class="detail-section"><h3>Original claim and review scope</h3>'
    proposition = record["proposition"]
    quotes = (note or {}).get("source_quotes", [])
    if quotes:
        for quote in quotes:
            text += (
                '<blockquote class="source-quote">'
                + prose(quote["text"], scientific=True)
                + "</blockquote>"
            )
            text += prose(
                quote["source_identity"] + "; " + quote["locator"],
                css="source-quote-citation",
            )
    else:
        text += prose("Source location", css="detail-label")
        text += prose(proposition["location"], css="source-citation")
    evidence_ids = {item["id"] for item in record["evidence"]}
    dependencies = [
        value
        for value in proposition["dependencies"]
        if value not in evidence_ids
        and not re.fullmatch(
            r"(?:[ESPIT]\d+(?:[._-]\d+)*|(?:evidence|source|claim|check|problem|assumption)[_-]\S+)",
            value,
            re.I,
        )
    ]
    if dependencies:
        text += prose("Dependencies: " + " ".join(dependencies), scientific=True)
    scope = (note or {}).get("review_scope")
    curated_scope = bool(scope)
    if not scope:
        locations = list(
            dict.fromkeys(
                " ".join(problem["source_location"].split())
                for problem in (note or {}).get("problems", [])
                if problem_assessment(problem) != "no_issue_found"
            )
        )
        if not locations:
            locations = [" ".join(proposition["location"].split())]
        scope = "The recorded inspection concerns these source locations: " + "; ".join(
            locations
        )
        if not scope.endswith((".", "!", "?")):
            scope += "."
    text += (
        '<p class="detail-label">Actual review scope</p>'
        + paragraphs(
            [scope] if isinstance(scope, str) else scope, scientific=curated_scope
        )
        + "</section>"
    )
    return text + "</div></details>"


def validate_base(base):
    if base is None:
        return
    p = urlsplit(base)
    if (
        p.scheme != "https"
        or not p.hostname
        or p.username
        or p.password
        or p.query
        or p.fragment
        or not base.endswith("/")
        or any(c.isspace() for c in base)
    ):
        raise ValueError(
            "public base URL must be an absolute HTTPS directory "
            "without credentials, query or fragment"
        )


def write_sitemap(output: Path, urls, last_modified=None):
    root = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for url in urls:
        entry = SubElement(root, "url")
        SubElement(entry, "loc").text = url
        if last_modified and last_modified.get(url):
            SubElement(entry, "lastmod").text = last_modified[url]
    (output / "sitemap.xml").write_bytes(
        tostring(root, encoding="utf-8", xml_declaration=True)
    )


def prepare_index(output: Path, payload, base):
    """Run after presentation overrides, before either file manifest is signed."""
    validate_base(base)
    path = output / "index.html"
    html = path.read_text("utf-8")
    if base:
        html = html.replace(
            'name="robots" content="noindex, nofollow"',
            'name="robots" content="index, follow"',
        )
        html = html.replace(
            "</head>", f'<link rel="canonical" href="{escape(base)}">\n</head>'
        )
    links = "".join(
        '<li><a href="cases/'
        + escape(r["case_id"])
        + '.html">'
        + escape(r["source"]["title"])
        + "</a></li>"
        for r in sorted(
            payload["records"], key=lambda r: r["source"]["title"].casefold()
        )
    )
    directory = (
        '<details class="paper-directory"><summary>'
        "All paper analyses — browse by title</summary>"
        "<p>Each case has a readable page with its source citation, analysis "
        "and evidence. Interactive filters above require JavaScript.</p><ol>"
        + links
        + "</ol></details>"
    )
    html = html.replace("<noscript>", directory + "\n<noscript>", 1)
    path.write_text(html, "utf-8")


def write_search_pages(output: Path, payload, base=None):
    validate_base(base)
    directory = output / "cases"
    directory.mkdir()
    urls = [base] if base else []
    last_modified = {}
    for record in payload["records"]:
        case_id = record["case_id"]
        relative = f"cases/{case_id}.html"
        canonical = (
            f'<link rel="canonical" href="{escape(base + relative)}">' if base else ""
        )
        robots = "index, follow" if base else "noindex, nofollow"
        reader = payload.get("reader", {}).get(case_id, {})
        note = payload.get("case_notes", {}).get(case_id, {})
        reader_bundle = payload.get("reader_bundles", {}).get(case_id) == (
            f"evidence/{case_id}.zip"
        )
        if reader.get("revision") != record["revision"]:
            reader = {}
        if note.get("revision") != record["revision"]:
            note = {}
        exports = {
            "case": context_exports(
                record,
                reader,
                base,
                report=note.get("report"),
                source_quotes=note.get("source_quotes"),
                review_scope=note.get("review_scope"),
            )
        }
        display_numbers = {}
        if record["audit"]["outcome"] not in {"no_issue_found", "scope_clarification"}:
            entries = note.get("problems") or fallback_problems(record)
            display_numbers = {
                source: display
                for display, (source, _) in enumerate(ordered_problems(entries), 1)
            }
            exports.update(
                {
                    f"problem-{number}": context_exports(
                        record,
                        reader,
                        base,
                        problem,
                        number,
                        source_quotes=note.get("source_quotes"),
                        review_scope=note.get("review_scope"),
                        display_number=display_numbers.get(number),
                    )
                    for number, problem in enumerate(entries, 1)
                }
            )
        title = record["source"]["title"]
        research_field = payload.get("research_fields", {}).get(case_id, "Others")
        description = (
            review_status(record) + ". " + " ".join(record["audit"]["summary"].split())
        )
        if len(description) > 190:
            description = description[:187].rsplit(" ", 1)[0] + "…"
        key = assessment(record)
        citation_meta = (
            '<meta name="citation_title" content="'
            + escape("ELVIA analysis of: " + title)
            + '">\n'
            + '<meta name="citation_publication_date" content="'
            + escape(record["created_at"][:10])
            + '">\n'
            + '<meta name="citation_publisher" content="ELVIA">\n'
            + "".join(
                '<meta name="citation_author" content="' + escape(name) + '">\n'
                for name in analysis_authors(reader)
            )
        )
        navigation = '<a href="../index.html">Evidence Atlas</a>'
        if base:
            navigation = (
                '<a href="/">ELVIA</a><a href="/atlas/">Evidence Atlas</a>'
                f'<a href="{escape(contribution_url(record))}">Contribute</a>'
            )
        narrative = problems(
            record, note, bool(base), exports, reader_bundle=reader_bundle
        )
        rating = (
            f'<span class="severity-tag {escape(key)}">'
            f"{escape(LABELS.get(key, key))}</span>"
            if key != "no_issue_found"
            else ""
        )
        html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} — Analysis &amp; Evidence | ELVIA</title>
<meta name="description" content="{escape(description)}">
<meta name="robots" content="{robots}">
<meta http-equiv="Content-Security-Policy" content="default-src 'none';
script-src 'self'; style-src 'self'; font-src 'self'; img-src 'self' data:;
base-uri 'none'; form-action 'none'; object-src 'none'">
{canonical}
{citation_meta}
<link rel="stylesheet" href="../vendor/katex/katex.min.css">
<link rel="stylesheet" href="../atlas.css">
<link rel="stylesheet" href="../case-page.css">
<script defer src="../vendor/katex/katex.min.js"></script>
<script defer src="../math.js"></script>
<script defer src="{escape(case_id)}.js"></script>
<script defer src="../case-page.js"></script>
</head><body class="standalone-case">
<a class="skip" href="#detail-title">Skip to case note</a>
<nav class="case-navigation" aria-label="Navigation">{navigation}</nav>
<main id="detail-content"><article>
<p class="detail-publication">{escape(record["audit"]["venue"])}
{record["audit"]["year"]} · {escape(research_field)}</p>
{rating}
<h1 id="detail-title" data-case-prose>{escape(title)}</h1>
<p class="detail-citation">{citation(record, reader)}</p>
{case_overview(record, note, bool(base))}
{context_tools(exports["case"], "case")}
<div class="problem-notes">{narrative}</div>
{supporting(record, reader, note)}'''
        if reader_bundle:
            html += (
                '<div class="detail-download">'
                f'<a href="../evidence/{escape(case_id)}.zip" download>'
                "Download report files (.zip)</a></div>"
            )
        html += (
            '</article></main><footer class="case-footer">'
            '<a href="../index.html">Browse all paper analyses</a>'
            "<p>ELVIA · Versioned scientific evidence</p>"
            "</footer></body></html>\n"
        )
        (output / relative).write_text(html, "utf-8")
        # Small public identity payload: onboarding need not download the whole Atlas.
        context_record = {
            "case_id": case_id,
            "revision": record["revision"],
            "source": {"title": title},
            "audit": {
                key: record["audit"][key] for key in ("venue", "landing_url", "outcome")
            },
        }
        context_note = {
            "revision": record["revision"],
            "problems": [
                {
                    "title": problem["title"],
                    "source_problem_id": problem.get("id", f"source-{number}"),
                    "source_number": number,
                    "display_number": display_numbers.get(number),
                }
                for number, problem in enumerate(note.get("problems", []), 1)
            ],
        }
        (directory / f"{case_id}.context.json").write_text(
            json.dumps(
                {
                    "records": [context_record],
                    "case_notes": {case_id: context_note},
                    "research_fields": {
                        case_id: payload.get("research_fields", {}).get(
                            case_id, "Others"
                        )
                    },
                },
                ensure_ascii=False,
            )
            + "\n",
            "utf-8",
        )
        presentation = payload.get("presentation", {}).get(case_id, {})
        if presentation.get("revision") != record["revision"]:
            presentation = {}
        safe_json = (
            json.dumps(presentation, ensure_ascii=True)
            .replace("<", "\\u003c")
            .replace(">", "\\u003e")
            .replace("&", "\\u0026")
        )
        (directory / f"{case_id}.js").write_text(
            "window.ELVIA_CASE_PRESENTATION = "
            + safe_json
            + ";\n"
            + "window.ELVIA_CASE_CONTEXT = "
            + json.dumps(exports, ensure_ascii=True)
            .replace("<", "\\u003c")
            .replace(">", "\\u003e")
            .replace("&", "\\u0026")
            + ";\n",
            "utf-8",
        )
        if base:
            urls.append(base + relative)
            last_modified[base + relative] = record["created_at"]
    prepare_index(output, payload, base)
    if base:
        write_sitemap(output, urls, last_modified)
