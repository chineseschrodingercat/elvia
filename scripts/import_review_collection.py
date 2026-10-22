"""Import individually reviewed notes; never execute or export upstream materials.

Inputs are the maintainer's local review files. The destination must be new.
This command verifies retained report/PDF bytes and saves immutable JSON records.
It does not decide scientific correctness: each input was reviewed separately.
"""

import argparse
import hashlib
import json
import re
import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from elvia.case_notes import prepare_case_notes
from elvia.records import validate_record
from elvia.storage import save_record

RATINGS = {"major", "moderate", "minor", "needs_evidence", "no_issue_found"}
LABELS = {
    "major": "Major",
    "moderate": "Moderate",
    "minor": "Minor",
    "needs_evidence": "Needs Evidence",
    "no_issue_found": "No Issue Found",
}
OUTCOMES = {
    "candidate_issue",
    "known_issue_reproduced",
    "scope_clarification",
    "no_issue_found",
    "needs_evidence",
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def paragraphs(values):
    return "\n\n".join(values)


def tex_text(value):
    """Escape prose while preserving explicit, separately checked math spans."""
    pieces = re.split(r"(\\\(.*?\\\)|\\\[.*?\\\])", value, flags=re.S)
    for piece in pieces:
        if piece.startswith((r"\(", r"\[")) and re.search(
            r"\\(?:input|include|write|openout|read|catcode|def|newcommand|special)\b",
            piece,
        ):
            raise ValueError("non-mathematical TeX command in a math span")
    escape = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(
        part
        if part.startswith((r"\(", r"\["))
        else "".join(escape.get(char, char) for char in part)
        for part in pieces
    )


def readable_review(audit):
    lines = [
        "# " + audit["title"],
        "",
        "Preliminary assessment: " + LABELS[audit["severity"]],
        "Independent scientific review: pending. Author adoption: not requested.",
        "",
        audit["summary"],
        "",
        "## Scope",
        audit["review_scope"],
    ]
    for index, problem in enumerate(audit["problems"], 1):
        lines += [
            "",
            f"## Problem {index}: {problem['title']}",
            f"Assessment: {problem['assessment']}; impact: {problem['severity']}",
            "",
            "Source: " + problem["source_location"],
            "",
            "### Source claim (paraphrase)",
            paragraphs(problem["claim"]),
            "",
            "### Analysis",
            paragraphs(problem["analysis"]),
            "",
            "### Finding and scope",
            paragraphs(problem["result"]),
        ]
        if problem["repair"]:
            lines += [
                "",
                "### Proposed correction",
                paragraphs(problem["repair"]),
                problem["existing_correction_status"],
            ]
    lines += ["", "## Limits", *["- " + value for value in audit["limitations"]]]
    return "\n\n".join(lines) + "\n"


def latex_review(audit):
    lines = [
        r"\documentclass[11pt]{article}",
        r"\usepackage[margin=25mm]{geometry}",
        r"\usepackage{amsmath,amssymb,fontspec,unicode-math}",
        r"\IfFontExistsTF{DejaVu Serif}{\setmainfont{DejaVu Serif}}"
        r"{\setmainfont{Latin Modern Roman}}",
        r"\IfFontExistsTF{Latin Modern Math}{\setmathfont{Latin Modern Math}}"
        r"{\setmathfont{DejaVu Math TeX Gyre}}",
        r"\usepackage{xurl,hyperref}",
        r"\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}",
        r"\begin{document}",
        r"\title{" + tex_text(audit["title"]) + "}",
        r"\author{ELVIA preliminary AI analysis}\date{"
        + datetime.now(UTC).strftime("%d %B %Y")
        + r"}\maketitle",
        "Preliminary assessment: " + LABELS[audit["severity"]] + r".\par",
        "Independent scientific review remains pending. "
        "Author adoption has not been requested.",
        tex_text(audit["summary"]),
        r"\section*{Review scope}",
        tex_text(audit["review_scope"]),
    ]
    for index, problem in enumerate(audit["problems"], 1):
        lines += [
            r"\section*{" + tex_text(f"Problem {index}: {problem['title']}") + "}",
            tex_text("Source: " + problem["source_location"]),
            tex_text(
                f"Assessment: {problem['assessment']}; impact: {problem['severity']}"
            ),
        ]
        for heading, key in [
            ("Source claim (paraphrase)", "claim"),
            ("Analysis", "analysis"),
            ("Finding and scope", "result"),
        ]:
            lines += [
                r"\subsection*{" + heading + "}",
                *[tex_text(value) for value in problem[key]],
            ]
        if problem["repair"]:
            lines += [
                r"\subsection*{Proposed correction}",
                *[tex_text(value) for value in problem["repair"]],
                tex_text(problem["existing_correction_status"]),
            ]
    lines += [
        r"\section*{Limits}",
        *[tex_text(x) + r"\par" for x in audit["limitations"]],
        r"\section*{Source identity}",
        tex_text(audit["version"]),
        r"\url{" + audit["pdf_url"] + "}",
        "Reviewed PDF SHA-256: " + r"\nolinkurl{" + audit["pdf_sha256"] + "}",
        tex_text(audit["provenance_note"]),
        r"\end{document}",
    ]
    return "\n\n".join(lines) + "\n"


def normalized_audit(audit, raw_root):
    """Keep scientific provenance, stripping private machine-specific paths."""
    audit = json.loads(json.dumps(audit))
    identifier = audit["report_id"]
    if not re.fullmatch(r"\d{4}", identifier):
        raise ValueError("invalid report identity")
    report = raw_root / "reports" / f"{identifier}.tex"
    if digest(report) != audit["raw_report_sha256"]:
        raise ValueError(f"{identifier}: original report bytes changed")
    if digest(audit["pdf_path"]) != audit["pdf_sha256"]:
        raise ValueError(f"{identifier}: inspected PDF bytes changed")
    del audit["pdf_path"]
    for check in audit["source_checks"]:
        path = Path(check.pop("path"))
        check["material"] = path.name
        if path.is_file():
            check["sha256"] = digest(path)

    def texts(value):
        if isinstance(value, str):
            yield value
        elif isinstance(value, dict):
            for item in value.values():
                yield from texts(item)
        elif isinstance(value, list):
            for item in value:
                yield from texts(item)

    for value in texts(audit):
        # A domain declaration such as A:\Omega is mathematics, not a drive.
        prose = re.sub(r"\\\(.*?\\\)|\\\[.*?\\\]", "", value, flags=re.S)
        if re.search(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]|/mnt/|/home/|/Users/", prose):
            raise ValueError(f"{identifier}: private absolute path in curated notes")
    if audit["severity"] not in RATINGS or audit["outcome"] not in OUTCOMES:
        raise ValueError(f"{identifier}: invalid assessment")
    for problem in audit["problems"]:
        for key in ("title", "source_location"):
            if not isinstance(problem.get(key), str) or not problem[key].strip():
                raise ValueError(f"{identifier}/{problem.get('id')}: missing {key}")
        for key in ("claim", "analysis", "result"):
            values = problem.get(key)
            if (
                not isinstance(values, list)
                or not values
                or not all(isinstance(value, str) and value.strip() for value in values)
            ):
                raise ValueError(f"{identifier}/{problem.get('id')}: missing {key}")
    supported = [p for p in audit["problems"] if p["assessment"] == "supported"]
    rank = {"minor": 1, "moderate": 2, "major": 3}
    supported_impact = max((rank.get(p["severity"], 0) for p in supported), default=0)
    if supported_impact and rank.get(audit["severity"], 0) != supported_impact:
        raise ValueError(f"{identifier}: paper rating differs from supported impact")
    if audit["severity"] in {"major", "moderate", "minor"} and not supported:
        raise ValueError(f"{identifier}: impact rating without supported finding")
    if audit["outcome"] == "no_issue_found" and supported:
        raise ValueError(f"{identifier}: no-issue outcome contradicts findings")
    return audit


def import_collection(audits, raw_root, output, *, expected_count=150, issue_number=21):
    inputs = sorted(Path(audits).glob("[0-9][0-9][0-9][0-9].json"))
    if len(inputs) != expected_count:
        raise ValueError(
            f"expected {expected_count} individually reviewed notes, got {len(inputs)}"
        )
    if output.exists():
        raise FileExistsError("collection import requires a new directory")
    # Inspect every input and all external bytes before creating the dataset.
    reviewed = [
        normalized_audit(json.loads(p.read_text("utf-8")), raw_root) for p in inputs
    ]
    if len({a["report_id"] for a in reviewed}) != len(reviewed):
        raise ValueError("duplicate report identity")
    with tempfile.TemporaryDirectory(prefix="elvia-reviewed-") as temporary:
        staging = Path(temporary) / "collection"
        count = (
            _write_collection(reviewed, staging)
            if issue_number == 21
            else _write_collection(reviewed, staging, issue_number=issue_number)
        )
        # Claim the destination exclusively before cleanup can own it. A rival
        # destination created after preflight must never be removed on failure.
        output.mkdir(parents=True, exist_ok=False)
        try:
            shutil.copytree(staging, output, dirs_exist_ok=True)
        except BaseException:
            shutil.rmtree(output)
            raise
    return count


def _write_collection(reviewed, output, *, issue_number=21):
    now = datetime.now(UTC).isoformat()
    catalog = {"format_version": 1, "cases": {}}
    records = []
    for audit in reviewed:
        slug = re.sub(r"[^a-z0-9]+", "-", audit["title"].casefold()).strip("-")
        case_id = f"neurips2025-{audit['report_id']}-{slug}"[:80].rstrip("-")
        directory = output / "evidence" / case_id
        directory.mkdir(parents=True, exist_ok=False)
        note = output / "source" / f"{case_id}.md"
        note.parent.mkdir(exist_ok=True)
        note.write_text(
            f"# {audit['title']}\n\nSource version: {audit['version']}\n\n"
            f"Primary PDF: {audit['pdf_url']}\n\n"
            f"Reviewed PDF SHA-256: {audit['pdf_sha256']}\n\n"
            "Original retrieval timestamp: "
            f"{audit['retrieved_at'] or 'not recorded'}\n\n"
            f"{audit['provenance_note']}\n\nOriginal supplied report SHA-256: "
            f"{audit['raw_report_sha256']}\n\n"
            "The original report is retained locally. This export contains the "
            "newly curated English analysis, not upstream PDFs, extracted paper "
            "text, code or machine logs. Historical computations were inspected "
            "as retained evidence; no author code was "
            "executed during this source-reading pass.\n\n"
            "Original ELVIA analysis: Minhao Liu, CC BY 4.0. "
            "https://creativecommons.org/licenses/by/4.0/\n"
            "Scientific review and author adoption remain pending/not requested "
            "respectively.\n",
            encoding="utf-8",
            newline="\n",
        )
        (directory / "verification.json").write_text(
            json.dumps(audit, ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        (directory / "review.md").write_text(
            readable_review(audit), encoding="utf-8", newline="\n"
        )
        (directory / "report.tex").write_text(
            latex_review(audit), encoding="utf-8", newline="\n"
        )

        def artifact(path):
            return {"path": path.relative_to(output).as_posix(), "sha256": digest(path)}

        evidence = [
            {
                "id": "analysis-and-boundaries",
                "stance": "support",
                "description": audit["summary"],
                "method": "Current AI source and argument inspection; "
                "retained computations were not rerun.",
                "artifact": artifact(directory / "review.md"),
            },
            {
                "id": "scope-and-rebuttal",
                "stance": "rebuttal",
                "description": " ".join(audit["limitations"]),
                "method": "Per-problem assessment, source checks, counterevidence "
                "and inherited execution limits.",
                "artifact": artifact(directory / "verification.json"),
            },
            {
                "id": "editable-latex",
                "stance": "support",
                "description": "Editable English LaTeX of the curated analysis "
                "and existing corrections.",
                "method": "Typeset source generated from the same reviewed "
                "problem paragraphs.",
                "artifact": artifact(directory / "report.tex"),
            },
        ]
        problems = audit["problems"]
        issue_outcome = audit["outcome"] not in {
            "no_issue_found",
            "scope_clarification",
        }
        repairs = (
            [paragraphs(p["repair"]) for p in problems if p["repair"]]
            if issue_outcome
            else []
        )
        # Null repair remains null; no invented correction or verification.
        record = {
            "schema_version": "1.2.0",
            "case_id": case_id,
            "revision": 1,
            "previous_revision": None,
            "case_type": "prospective_audit",
            "created_at": now,
            "source": {
                "title": audit["title"],
                "version": audit["version"],
                "doi": None,
                "arxiv_id": None,
                "identifier_note": audit["provenance_note"],
                "artifact": artifact(note),
                "review_scope": audit["review_scope"],
            },
            "audit": {
                "venue": "NeurIPS",
                "year": 2025,
                "authors": audit["authors"],
                **{
                    k: audit[k]
                    for k in (
                        "landing_url",
                        "pdf_url",
                        "pdf_sha256",
                        "retrieved_at",
                        "outcome",
                        "summary",
                        "limitations",
                    )
                },
            },
            "proposition": {
                "claim": "\n\n".join(paragraphs(p["claim"]) for p in problems)
                or audit["summary"],
                "domain": audit["review_scope"],
                "assumptions": list(
                    dict.fromkeys(x for p in problems for x in p["assumptions"])
                ),
                "location": "\n\n".join(p["source_location"] for p in problems)
                or audit["review_scope"],
                "dependencies": [],
            },
            "concern": {
                "description": audit["summary"],
                "type": "other",
                "severity": audit["severity"]
                if audit["severity"] in {"major", "moderate", "minor"}
                else "minor",
                "impact": "unknown",
                "origin": "ai",
            },
            "evidence": evidence,
            "runs": [],
            "human_reviews": [],
            "adjudication": {
                "status": "pending",
                "rationale": "Preliminary AI source/logic review; "
                "no independent human scientific adjudication.",
                "history": [],
            },
            "repair": {
                "content": "\n\n".join(repairs) or None,
                "verification_status": "pending" if repairs else "not_proposed",
                "verification_refs": [],
                "changed_assumptions": [],
                "changed_conclusion": None,
                "adoption_status": "not_requested",
            },
            "publication": {
                "status": "preliminary_ai",
                "note": "Maintainer-authorized private review collection "
                f"(Issue #{issue_number}). Source/logic inspection is distinct from "
                "independent "
                "scientific confirmation. No author contact or adoption.",
            },
        }
        errors = validate_record(record, output)
        if errors:
            raise ValueError(f"{audit['report_id']}: " + "\n".join(errors))
        save_record(record, output / "records")
        if problems and issue_outcome:
            rendered = [
                {
                    **{
                        k: p[k]
                        for k in (
                            "id",
                            "title",
                            "source_location",
                            "claim",
                            "analysis",
                            "result",
                            "assumptions",
                            "severity",
                            "assessment",
                        )
                    },
                    "analysis_heading": "Source and argument check",
                    "repair": {
                        "heading": "Proposed correction",
                        "paragraphs": p["repair"] + [p["existing_correction_status"]],
                    }
                    if p["repair"]
                    else None,
                    "evidence_ids": [e["id"] for e in evidence],
                }
                for p in problems
            ]
            canonical = json.dumps(
                record, sort_keys=True, separators=(",", ":"), ensure_ascii=True
            ).encode()
            catalog["cases"][case_id] = {
                "revision": 1,
                "record_sha256": hashlib.sha256(canonical).hexdigest(),
                "problems": rendered,
            }
        records.append(record)
    prepare_case_notes(records, catalog=catalog)
    (output / "case-notes.json").write_text(
        json.dumps(catalog, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return len(records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audits", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    count = import_collection(args.audits, args.raw_root, args.output)
    print(f"Imported {count} individually reviewed papers")


if __name__ == "__main__":
    main()
