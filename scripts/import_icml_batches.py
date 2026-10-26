"""Publish the four explicitly selected ICML batches, without repeating review.

The raw archive stays untouched. Public records preserve existing findings and
the complete report as a formatting-only transcription. Operational identifiers
and host paths are removed from public copies. No author code or TeX is executed.
"""

import argparse
import hashlib
import json
import re
import runpy
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

from elvia.case_notes import prepare_case_notes
from elvia.reader import record_digest
from elvia.records import validate_record
from elvia.storage import save_record

BATCHES = {"B001", "B002", "B003", "B004"}
RATING_KEYS = (
    "report_assessment",
    "assessment",
    "overall_assessment",
    "overall_supported_severity",
    "supported_severity",
    "paper_outcome",
    "overall_outcome",
    "overall_supported_impact",
    "overall_supported_judgment",
    "overall_judgment",
    "supported_judgment",
    "severity",
    "overall",
    "overall_recommendation",
    "outcome",
    "inspection_outcome",
)
CONTROL = {
    "batch_token",
    "task_id",
    "chat_id",
    "conversation_url",
    "conversation_id",
    "chat_url",
    "task_packet",
    "task_packet_sha256",
    "prompt_hash",
    "prompt_sha256",
    "frozen_packet_sha256",
    "frozen_contract_sha256",
    "controller_state",
    "assignment_id",
    "display_no",
    "batch_id",
    "attempt",
}
UUID = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", re.I)
HOST_PATH = re.compile(
    r"(?<![A-Za-z0-9])(?:[A-Za-z]:[\\/](?!/)|/mnt/data/|/home/oai/)"
    r"[^\s\"'<>|;,)]+"
)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text("utf-8-sig"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=True, indent=2, allow_nan=False)
        stream.write("\n")


def _public_plain(value):
    value = UUID.sub("[internal identifier omitted]", str(value))
    value = re.sub(r"https://chatgpt\.com/[^\s)]+", "[internal link omitted]", value)
    # Known archive roots contain spaces. Match only that root and its workflow
    # directories, then preserve any dataset-relative evidence path and prose.
    value = re.sub(
        r"D:[\\/]ELVIA report raw[\\/]ICML[\\/]"
        r"(?:_review_control[\\/]run_B\d{3}[\\/])?"
        r"(?:staging[\\/]chat-\d+[\\/]attempt-\d+[\\/])?",
        "archive/",
        value,
        flags=re.I,
    )
    value = HOST_PATH.sub("[local archive path omitted]", value)
    value = re.sub(r"\bchat-\d{4}\b", "[internal task]", value)
    value = value.replace("\\[internal", "/[internal")
    return value.replace("\ufffd", "[unavailable character]")


def public_text(value):
    value = str(value)
    # Mathematical domains such as C:\Omega are not filesystem paths.
    parts = re.split(r"(\\\(.*?\\\)|\\\[.*?\\\])", value, flags=re.S)
    return "".join(
        part if part.startswith((r"\(", r"\[")) else _public_plain(part)
        for part in parts
    ).strip()


def report_text(value):
    value = re.sub(r"(?m)^> +$", ">", public_text(value))
    if value.startswith("Code:\n"):
        return value
    # Equation labels are cross-reference metadata, not mathematical operators.
    # Keep their names visible in the public transcription instead of asking a
    # browser renderer to execute document-level LaTeX reference commands.
    labels = re.findall(r"\\label\{([^{}]+)\}", value)
    value = re.sub(r"\\label\{[^{}]+\}", "", value)
    value = re.sub(r"\\eqref\{([^{}]+)\}", r"\\text{(\1)}", value)
    for rule in ("toprule", "midrule", "bottomrule"):
        value = re.sub(r"\\" + rule + r"\b", r"\\hline", value)
    return ("Equation reference: " + ", ".join(labels) + ". " if labels else "") + value


def public_data(value):
    if isinstance(value, dict):
        return {
            k: public_data(v) for k, v in value.items() if k.casefold() not in CONTROL
        }
    if isinstance(value, list):
        return [public_data(v) for v in value]
    return public_text(value) if isinstance(value, str) else value


def text_rows(value, prefix=""):
    if value is None or value == "" or value == [] or value == {}:
        return []
    if isinstance(value, dict):
        return [
            s
            for k, v in value.items()
            for s in text_rows(
                v, (prefix + ". " if prefix else "") + k.replace("_", " ").capitalize()
            )
        ]
    if isinstance(value, list):
        return [s for item in value for s in text_rows(item, prefix)]
    text = public_text(value)
    return [(prefix + ": " if prefix else "") + text] if text else []


def label(value):
    if not isinstance(value, str):
        return None
    text = re.sub(r"[_-]+", " ", value.casefold()).strip()
    if re.match(r"^major(?:\b|$)", text):
        return "major"
    if re.match(r"^minor(?:\b|$)", text):
        return "minor"
    if text.startswith("needs evidence"):
        return "needs_evidence"
    if text.startswith(
        ("no issue", "scope clarification", "no major", "no demonstrated")
    ):
        return "no_issue_found"
    return None


def paper_rating(data):
    # Explicit paper-level labels outrank unresolved subitems; never infer Major
    # from the presence of the word in an impact narrative or hypothetical claim.
    for key in RATING_KEYS:
        rating = label(data.get(key))
        if rating:
            return rating
        if key == "supported_severity" and isinstance(data.get(key), dict):
            counts = data[key]
            if counts.get("Major", 0):
                return "major"
            if counts.get("Minor", 0):
                return "minor"
    raise ValueError("paper rating requires an explicit archived classification")


def normalize_problem(item, number):
    if not isinstance(item, dict):
        item = {"check": item}
    item = public_data(item)
    rating = next(
        (
            label(item[k])
            for k in ("judgment", "assessment", "severity", "supported_severity")
            if k in item and label(item[k])
        ),
        None,
    )
    claim_keys = ("source_claim", "claim", "paper_claim", "original_claim")
    result_keys = ("result", "conclusion", "finding", "impact", "scope", "disposition")
    repair_keys = ("repair", "correction", "proposed_correction")
    skipped = {
        "id",
        "title",
        "name",
        "location",
        "source_location",
        "assumptions",
        "judgment",
        "assessment",
        "severity",
        "supported_severity",
    }
    claim = [s for k in claim_keys for s in text_rows(item.get(k))]
    results = [s for k in result_keys for s in text_rows(item.get(k), k.capitalize())]
    analysis = [
        s
        for k, v in item.items()
        if k not in skipped | set(claim_keys) | set(result_keys) | set(repair_keys)
        for s in text_rows(v, k.replace("_", " ").capitalize())
    ]
    repairs = [s for k in repair_keys for s in text_rows(item.get(k))]
    problem = {
        "id": f"p{number}",
        "title": str(
            item.get("title") or item.get("name") or f"Recorded finding {number}"
        ),
        "source_location": " ".join(
            text_rows(item.get("location") or item.get("source_location"))
        )
        or "See the retained report for exact source locations.",
        "claim": claim
        or ["See the source claim and its conditions in the retained report."],
        "analysis": analysis or text_rows(item) or ["See the retained report."],
        "result": results
        or [
            s
            for k in ("judgment", "assessment", "status")
            for s in text_rows(item.get(k), k.capitalize())
        ]
        or [
            "The archived finding retains its stated scope; "
            "independent review is pending."
        ],
        "assumptions": text_rows(item.get("assumptions")),
        "analysis_heading": "Archived analysis and counterevidence",
        "repair": {
            "heading": "Recorded correction and verification scope",
            "paragraphs": repairs,
        }
        if repairs
        else None,
        "evidence_ids": ["retained-findings", "retained-report", "scope-and-rebuttal"],
    }
    if rating:
        problem["severity"] = rating
        problem["assessment"] = (
            "supported"
            if rating in {"major", "minor"}
            else "not_issue"
            if rating == "no_issue_found"
            else "needs_evidence"
        )
    return problem


def select_metadata(rows):
    selected = [r for r in rows if r.get("Batch") in BATCHES]
    if len(selected) != 400 or {int(r["No."]) for r in selected} != set(range(1, 401)):
        raise ValueError("selection must contain exactly the 400 papers in B001–B004")
    if len({r["Paper ID"] for r in selected}) != 400:
        raise ValueError("duplicate source paper identity")
    for row in selected:
        if row["Batch"] != f"B{(int(row['No.']) - 1) // 100 + 1:03d}":
            raise ValueError("source batch and report number disagree")
    return sorted(selected, key=lambda r: int(r["No."]))


def prepare_input(row, raw, parser, pandoc, cache=None):
    number = f"{int(row['No.']):04d}"
    batch = raw / ("batch_" + row["Batch"])
    paths = {
        "article": batch / f"papers/{number}/{number}.pdf",
        "report": batch / f"reports/Pdf/{number}.pdf",
        "tex": batch / f"reports/{number}.tex",
        "findings": batch / f"verification/{number}/findings.json",
        "coverage": batch / f"verification/{number}/coverage.json",
        "provenance": batch / f"verification/{number}/provenance.json",
    }
    hashes = {k: sha(p) for k, p in paths.items()}
    if hashes["article"] not in json.dumps(read(paths["provenance"])):
        raise ValueError(
            f"{number}: article identity is absent from archived provenance"
        )
    findings = read(paths["findings"])
    if findings.get("paper_id") not in {None, row["Paper ID"]}:
        raise ValueError(f"{number}: finding/source identity mismatch")
    if findings.get("title") and findings["title"].strip() != row["Title"].strip():
        raise ValueError(f"{number}: finding/source title mismatch")
    manifest = paths["article"].with_name("source_manifest.json")
    if manifest.exists() and hashes["article"] not in json.dumps(read(manifest)):
        raise ValueError(f"{number}: article changed after source preparation")
    for role in ("article", "report"):
        if not paths[role].read_bytes().startswith(b"%PDF-"):
            raise ValueError(f"{number}: {role} is not a PDF")
    rating = "needs_evidence" if number == "0004" else paper_rating(findings)
    cached = cache / (hashes["tex"] + ".json") if cache else None
    paragraphs = (
        read(cached)
        if cached and cached.exists()
        else parser(paths["tex"], pandoc=pandoc)
    )
    report = [report_text(s) for s in paragraphs]
    if not report or not any(row["Title"][:30] in s for s in report):
        # Math/punctuation can differ after formatting; identity is also checked
        # against source manifests and the explicit paper ID in the report.
        if not any(row["Paper ID"] in s for s in report):
            raise ValueError(f"{number}: report/source identity requires inspection")
    return (
        row,
        number,
        paths,
        hashes,
        public_data(findings),
        public_data(read(paths["coverage"])),
        rating,
        report,
    )


def import_batches(raw, output, fields, pandoc, cache=None):
    selected = select_metadata(read(raw / "_review_control/papers.normalized.json"))
    if output.exists():
        raise FileExistsError("a publication import requires a new destination")
    parser = runpy.run_path(str(Path(__file__).with_name("icml_report_text.py")))[
        "report_paragraphs"
    ]
    with ThreadPoolExecutor(max_workers=4) as pool:
        prepared = list(
            pool.map(lambda r: prepare_input(r, raw, parser, pandoc, cache), selected)
        )
    now = datetime.now(UTC).isoformat()
    catalogs = {
        name: {"format_version": 1, "cases": {}}
        for name in ("case-notes", "reader-catalog", "research-fields", "math-notation")
    }
    manifest = {
        "format_version": 1,
        "selection": sorted(BATCHES),
        "prepared_at": now,
        "scientific_reassessment_performed": False,
        "metadata_sha256": sha(raw / "_review_control/papers.normalized.json"),
        "papers": [],
    }
    with tempfile.TemporaryDirectory(prefix="elvia-icml-publication-") as temporary:
        staging = Path(temporary) / "icml2025"
        records = []
        for row, number, _paths, hashes, findings, coverage, rating, report in prepared:
            title = row["Title"].strip().replace(" --- ", " — ")
            slug = re.sub(r"[^a-z0-9]+", "-", title.casefold()).strip("-")
            case = f"icml2025-{number}-{slug}"[:80].rstrip("-")
            directory = staging / "evidence" / case
            directory.mkdir(parents=True)
            (directory / "report.txt").write_text(
                "\n\n".join(report) + "\n", "utf-8", newline="\n"
            )
            write(directory / "findings.json", findings)
            write(directory / "coverage.json", coverage)
            # Public editable source is generated solely from the retained
            # transcription, after removal of operational identifiers/host paths.
            old = runpy.run_path(
                str(Path(__file__).with_name("import_review_collection.py"))
            )
            tex_text = old["tex_text"]
            public_tex = "\n".join(
                [
                    r"\documentclass[10pt]{article}",
                    r"\usepackage[margin=20mm]{geometry}",
                    r"\usepackage{amsmath,amssymb,fontspec,unicode-math,xurl,hyperref}",
                    r"\IfFontExistsTF{DejaVu Serif}{\setmainfont{DejaVu Serif}}"
                    r"{\setmainfont{Latin Modern Roman}}",
                    r"\setmathfont{latinmodern-math.otf}",
                    r"\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}\sloppy",
                    r"\begin{document}",
                    *[
                        (
                            r"{\ttfamily\footnotesize "
                            + "".join(tex_text(c) for c in s[6:]).replace(
                                "\n", "\\\\\n"
                            )
                            + "}"
                        )
                        + r"\par"
                        if s.startswith("Code:\n")
                        else tex_text(s) + r"\par"
                        for s in report
                    ],
                    r"\end{document}",
                    "",
                ]
            )
            (directory / "report.tex").write_text(public_tex, "utf-8", newline="\n")
            source = staging / "source" / (case + ".md")
            source.parent.mkdir(exist_ok=True)
            source.write_text(
                f"# {title}\n\nSource paper: {row['Paper ID']}\n\n"
                f"Publisher source: {row['Source URL']}\n\n"
                f"Reviewed article SHA-256: {hashes['article']}\n\n"
                f"Retained original report TeX SHA-256: {hashes['tex']}\n\n"
                f"Retained original report PDF SHA-256: {hashes['report']}\n\n"
                "This publication formats the completed report; it does not repeat "
                "scientific review. Original archive files remain unchanged. Public "
                "copies remove host paths and internal workflow identifiers. Unknown "
                "original download times remain unknown. Independent scientific "
                "review is pending. No author contact or adoption request was made.\n\n"
                "Original ELVIA analysis: Minhao Liu, CC BY 4.0. Source articles "
                "retain their own copyright and publication terms.\n",
                "utf-8",
                newline="\n",
            )

            def artifact(p):
                return {"path": p.relative_to(staging).as_posix(), "sha256": sha(p)}

            raw_problems = (
                findings.get("problems")
                or findings.get("findings")
                or findings.get("issues")
                or []
            )
            if isinstance(raw_problems, dict):
                raw_problems = list(raw_problems.values())
            problems = [normalize_problem(p, i) for i, p in enumerate(raw_problems, 1)]
            summary = " ".join(
                text_rows(findings.get("summary") or findings.get("overall_summary"))
            )
            if not summary:
                summary = (
                    "Archived assessment: "
                    + rating.replace("_", " ").title()
                    + ". "
                    + "; ".join(p["title"] for p in problems[:3])
                    + ("." if problems else "")
                )
            limits = text_rows(findings.get("limitations"))
            for key in (
                "missing_materials",
                "not_performed",
                "limitations",
                "review_limits",
                "scope_limits",
            ):
                limits += text_rows(
                    coverage.get(key), key.replace("_", " ").capitalize()
                )
            limits += [
                "The original report's complete scope, counterevidence and "
                "unresolved questions are retained below.",
                "This import checks publication format and identity; "
                "it does not repeat scientific review.",
                "Independent human scientific review is pending; "
                "author adoption has not been requested.",
            ]
            limits = list(dict.fromkeys(limits))
            repairs = [
                s for p in problems if p["repair"] for s in p["repair"]["paragraphs"]
            ]
            outcome = (
                "candidate_issue"
                if rating in {"major", "minor"}
                else "needs_evidence"
                if rating == "needs_evidence"
                else "scope_clarification"
                if "scope_clarification"
                in str(findings.get("inspection_outcome", "")).casefold()
                else "no_issue_found"
            )
            if outcome in {"no_issue_found", "scope_clarification"}:
                repairs = []
                for p in problems:
                    p["repair"] = None
            version = str(
                findings.get("reviewed_version")
                or "Published ICML 2025 proceedings PDF (PMLR 267)"
            )
            scope = (
                "Completed report for "
                + row["Paper ID"]
                + "; exact inspected scope and limitations are retained "
                "in the report and coverage ledger."
            )
            record = {
                "schema_version": "1.2.0",
                "case_id": case,
                "revision": 1,
                "previous_revision": None,
                "case_type": "prospective_audit",
                "created_at": now,
                "source": {
                    "title": title,
                    "version": version,
                    "doi": None,
                    "arxiv_id": None,
                    "identifier_note": "Publisher proceedings identity "
                    "and supplied paper identifier "
                    + row["Paper ID"]
                    + "; no DOI is fabricated.",
                    "artifact": artifact(source),
                    "review_scope": scope,
                },
                "audit": {
                    "venue": "ICML",
                    "year": 2025,
                    "authors": list(
                        dict.fromkeys(
                            a.strip() for a in row["Authors"].split(";") if a.strip()
                        )
                    ),
                    "landing_url": row["Source URL"],
                    "pdf_url": row["PDF URL"],
                    "pdf_sha256": hashes["article"],
                    "retrieved_at": None,
                    "outcome": outcome,
                    "summary": summary,
                    "limitations": limits,
                },
                "proposition": {
                    "claim": "\n\n".join(s for p in problems for s in p["claim"])
                    or summary,
                    "domain": scope,
                    "assumptions": list(
                        dict.fromkeys(s for p in problems for s in p["assumptions"])
                    ),
                    "location": "\n\n".join(p["source_location"] for p in problems)
                    or scope,
                    "dependencies": [],
                },
                "concern": {
                    "description": summary,
                    "type": "other",
                    "severity": rating if rating in {"major", "minor"} else "minor",
                    "impact": "unknown",
                    "origin": "ai",
                },
                "evidence": [
                    {
                        "id": "retained-findings",
                        "stance": "support",
                        "description": "Existing findings, counterevidence and "
                        "bounded classifications; no scientific reassessment "
                        "performed during import.",
                        "method": "Formatting-only transcription "
                        "of the selected completed report.",
                        "artifact": artifact(directory / "findings.json"),
                    },
                    {
                        "id": "retained-report",
                        "stance": "support",
                        "description": "Complete public transcription of the "
                        "retained report, with internal workflow identifiers "
                        "and host paths omitted.",
                        "method": "LaTeX parsed as data; "
                        "no author code or TeX execution.",
                        "artifact": artifact(directory / "report.txt"),
                    },
                    {
                        "id": "scope-and-rebuttal",
                        "stance": "rebuttal",
                        "description": "Existing inspection coverage, "
                        "counterevidence, missing materials and unresolved "
                        "scope remain as supplied.",
                        "method": "Public copy of the archived coverage ledger.",
                        "artifact": artifact(directory / "coverage.json"),
                    },
                    {
                        "id": "editable-latex",
                        "stance": "support",
                        "description": "Public editable report generated "
                        "from the same retained transcription.",
                        "method": "Formatting conversion only; "
                        "original archive bytes remain unchanged.",
                        "artifact": artifact(directory / "report.tex"),
                    },
                ],
                "runs": [],
                "human_reviews": [],
                "adjudication": {
                    "status": "pending",
                    "rationale": "Preliminary AI-assisted report; independent "
                    "human scientific adjudication remains pending.",
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
                    "note": "Maintainer-authorized publication of ICML batches "
                    "B001–B004 (Issue #18). Existing findings retain their scope; "
                    "publication is not independent scientific confirmation.",
                },
            }
            errors = validate_record(record, staging)
            if errors:
                raise ValueError(number + ": " + "\n".join(errors))
            save_record(record, staging / "records")
            bound = {"revision": 1, "record_sha256": record_digest(record)}
            typeset_title = re.sub(
                r"\$([^$\n]+)\$",
                lambda m: r"\(" + m[1].replace("\\\\", "\\") + r"\)",
                title,
            )
            if typeset_title != title:
                catalogs["math-notation"]["cases"][case] = {
                    **bound,
                    "replacements": [{"source": title, "typeset": typeset_title}],
                }
            catalogs["case-notes"]["cases"][case] = (
                {**bound, "problems": problems, "report": report}
                if problems
                else {**bound, "report": report}
            )
            catalogs["reader-catalog"]["cases"][case] = {
                **bound,
                "citation": {
                    "title": title,
                    "authors": record["audit"]["authors"],
                    "container": "Proceedings of the 42nd International "
                    "Conference on Machine Learning",
                    "volume": "267",
                    "publisher": "PMLR",
                    "year": 2025,
                    "doi": None,
                    "source_url": row["Source URL"],
                    "first_page": "",
                    "last_page": "",
                },
                "contributors": [
                    {"name": "Minhao Liu", "role": "Initial report", "revision": 1}
                ],
                "verified_on": now[:10],
            }
            field = fields[f"icml2025-{number}"]
            catalogs["research-fields"]["cases"][case] = {
                **bound,
                "field": field["field"],
                "reason": field["reason"],
            }
            manifest["papers"].append(
                {
                    "case_id": case,
                    "report_number": number,
                    "paper_id": row["Paper ID"],
                    "batch": row["Batch"],
                    "title": title,
                    "field": field["field"],
                    "topic": row["Topic"],
                    "archive_hashes": hashes,
                    "public_record_sha256": record_digest(record),
                    "public_report_source_sha256": sha(directory / "report.tex"),
                    "public_report_text_sha256": sha(directory / "report.txt"),
                }
            )
            records.append(record)
        # Presentation validation also checks every narrative's snapshot binding.
        prepare_case_notes(records, catalog=catalogs["case-notes"])
        for name, catalog in catalogs.items():
            write(staging / (name + ".json"), catalog)
        write(staging / "import-manifest.json", manifest)
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(staging, output)
    return len(prepared)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fields", type=Path, required=True)
    parser.add_argument("--pandoc", default="pandoc")
    parser.add_argument("--cache", type=Path)
    args = parser.parse_args()
    print(
        import_batches(
            args.raw_root, args.output, read(args.fields), args.pandoc, args.cache
        )
    )
