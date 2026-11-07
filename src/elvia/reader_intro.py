"""Compact reading introductions derived only from retained, revision-bound prose.

Never shorten a scientific sentence or synthesize a new impact claim. Long or
unavailable abstracts fall back to one explicitly identified finding, with a
route to the complete scope. Keep the browser derivation in case-note.js equal.
"""

import re

from elvia.public_context import review_status


def source_metadata(record):
    origins = {
        "ai": "AI-origin analysis",
        "human": "Human-origin analysis",
        "software": "Software-origin analysis",
    }
    origin = record.get("concern", {}).get("origin")
    return [
        ("Inspected paper version", record["source"]["version"]),
        ("Analysis revision", str(record["revision"])),
        ("Analysis origin", origins.get(origin, "See the provenance record")),
        ("Scientific status", review_status(record)),
    ]


def reader_introduction(record, note=None):
    """Select whole supported paragraphs; no truncation or severity inference."""
    note = note if note and note.get("revision") == record["revision"] else {}
    ranks = {"major": 0, "minor": 1, "needs_evidence": 2}
    entries = []
    if record["audit"]["outcome"] not in {"no_issue_found", "scope_clarification"}:
        entries = [
            (index, problem)
            for index, problem in enumerate(note.get("problems", []), 1)
            if problem.get("assessment") != "not_issue"
        ]
        entries.sort(
            key=lambda entry: ranks.get(
                "needs_evidence"
                if entry[1].get("assessment") == "needs_evidence"
                else {"moderate": "minor"}.get(
                    entry[1].get("severity"), entry[1].get("severity")
                ),
                3,
            )
        )
    fragment = f"problem-{entries[0][0]}-evidence" if entries else "case-evidence"
    text = " ".join(note.get("brief", [])).strip()
    coverage = "article_summary"
    if not text or len(text) > 1100:
        text = next(
            (
                re.sub(r"^Abstract\s*:\s*", "", paragraph, flags=re.I).strip()
                for paragraph in note.get("report", [])
                if re.match(r"^Abstract\s*:", paragraph, flags=re.I)
                and len(re.sub(r"^Abstract\s*:\s*", "", paragraph, flags=re.I)) <= 1100
            ),
            "",
        )
    if not text and entries:
        problem = entries[0][1]
        result = next(
            (
                value.strip()
                for value in problem.get("result", [])
                if value.strip()
                and len(value.strip()) <= 550
                and not value.startswith("Recorded evidence:")
            ),
            "",
        )
        title = problem["title"].strip()
        if len(title) <= 300:
            text = f"The first reported finding concerns “{title}”."
            if result:
                text += " " + result
            else:
                text += (
                    " A concise supported summary is not available here; "
                    "read the complete problem scope below."
                )
            coverage = "first_finding"
    if not text:
        summary = record["audit"]["summary"].strip()
        summary = re.sub(
            r"^Archived assessment: (?:Major|Minor|Needs Evidence|No Issue Found)\.\s*",
            "",
            summary,
        )
        text = (
            summary
            if summary and len(summary) <= 700
            else "A concise supported summary is not available here. "
            "Inspect the source claim and complete review scope below."
        )
        coverage = "record_summary" if text == summary else "scope_only"
        if record["audit"]["outcome"] not in {"no_issue_found", "scope_clarification"}:
            fragment = "problem-1-evidence"
    scope = next(
        (
            value.strip()
            for value in record["audit"].get("limitations", [])
            if value.strip()
            and len(value.strip()) <= 360
            and value.strip() not in text
            and not re.search(
                r"(?:not refut|not establish|not identif|unresolved|uninspected|"
                r"\bscope\b|surviv|weaker|remain)",
                text,
                re.I,
            )
            and re.search(
                r"\b(?:counterevidence|not refuted|not established|"
                r"unresolved|only|scope)\b",
                value,
                re.I,
            )
            and not re.search(
                r"(?:independent human|adjudication|author adoption|"
                r"exact reviewed source version)",
                value,
                re.I,
            )
        ),
        "",
    )
    return {
        "text": text,
        "scope": scope,
        "coverage": coverage,
        "evidence_fragment": fragment,
        "additional_findings": coverage == "first_finding" and len(entries) > 1,
    }
