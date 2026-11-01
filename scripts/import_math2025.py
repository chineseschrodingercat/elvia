"""Publish integrity-accepted Math 2025 reports without repeating scientific review.

Only the controller's accepted roster is selected. Both the immutable accepted
snapshot and current seven core files must still match their acceptance receipt.
The public collection retains exact source identities, findings, counterevidence,
full report arguments and pending human adjudication. Private control data stays
in the archive. Existing published collections are never rewritten by this tool.
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
from functools import cache
from pathlib import Path

from elvia.case_notes import prepare_case_notes
from elvia.reader import record_digest
from elvia.records import validate_record
from elvia.storage import save_record

CONTROL_ROOT = Path("verification/_control/run_math2025")
RATINGS = {"major", "minor", "needs_evidence", "no_issue_found"}
PRIVATE_KEY = re.compile(
    r"(?:^|_)(?:token|conversation|chat_id|task_id|task_packet|prompt|"
    r"controller_state|assignment_id|credential|password|secret|api_key)(?:_|$)",
    re.I,
)
OPERATION_KEYS = {
    "batch_id",
    "display_no",
    "attempt",
    "path_base",
    "raw_root",
    "archive_root",
    "original_task_id",
    "recovery_id",
    "frozen_packet_sha256",
    "frozen_contract_sha256",
    "input_packet",
    "task_packet",
}
ARCHIVE_ROOT = re.compile(
    r"D:[\\/]ELVIA report raw[\\/]Math 15 journals[\\/]2025[\\/]", re.I
)


@cache
def helper(name):
    return runpy.run_path(str(Path(__file__).with_name(name)))


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


def selected_ids(state):
    ids = state.get("accepted_paper_ids")
    bindings = state.get("accepted_integrity_records", {})
    if (
        not isinstance(ids, list)
        or len(ids) != len(set(ids))
        or state.get("accepted") != len(ids)
        or set(ids) != set(bindings)
        or any(not re.fullmatch(r"M25-\d{4}", pid) for pid in ids)
    ):
        raise ValueError("inconsistent integrity-accepted roster")
    return sorted(ids)


def core_paths(number):
    return {
        "article": f"papers/{number}/{number}.pdf",
        "source_manifest": f"papers/{number}/source_manifest.json",
        "tex": f"reports/{number}.tex",
        "report": f"reports/Pdf/{number}.pdf",
        "coverage": f"verification/{number}/coverage.json",
        "findings": f"verification/{number}/findings.json",
        "provenance": f"verification/{number}/provenance.json",
    }


def verify_core(raw, paper_id, binding):
    raw = raw.resolve(strict=True)
    receipt_path = Path(binding["receipt_path"]).resolve(strict=True)
    snapshot = Path(binding["snapshot_root"]).resolve(strict=True)
    if not receipt_path.is_relative_to(raw) or not snapshot.is_relative_to(raw):
        raise ValueError(f"{paper_id}: acceptance integrity path outside archive")
    if sha(receipt_path) != binding["receipt_sha256"]:
        raise ValueError(f"{paper_id}: acceptance integrity receipt changed")
    receipt = read(receipt_path)
    if receipt.get("paper_id") != paper_id:
        raise ValueError(f"{paper_id}: acceptance integrity identity mismatch")
    artifacts = {item["path"].replace("\\", "/"): item for item in receipt["artifacts"]}
    hashes = {}
    paths = core_paths(paper_id[-4:])
    for name, relative in paths.items():
        item = artifacts.get(relative)
        if not item:
            raise ValueError(f"{paper_id}: acceptance integrity missing {relative}")
        for root in (raw, snapshot):
            path = root / relative
            if (
                not path.is_file()
                or path.stat().st_size != item["bytes"]
                or sha(path) != item["sha256"]
            ):
                raise ValueError(
                    f"{paper_id}: acceptance integrity mismatch {relative}"
                )
        hashes[name] = item["sha256"]
    hashes["acceptance_receipt"] = binding["receipt_sha256"]
    return paths, hashes


def source_entry(manifest, number):
    entries = manifest.get("files", [])
    if isinstance(entries, dict):
        entries = list(entries.values())
    selected = [
        row
        for row in entries
        if str(row.get("relative_path") or row.get("path", "")).replace("\\", "/")
        == f"papers/{number}/{number}.pdf"
    ]
    if len(selected) != 1 or not str(selected[0].get("version", "")).strip():
        raise ValueError(f"{number}: exact PDF source version is required")
    entry = dict(selected[0])
    version = entry["version"]
    if isinstance(version, dict):
        entry["version_details"] = version
        kind = str(version.get("kind") or version.get("type") or "retained source")
        parts = [kind.replace("_", " ")]
        for key in (
            "arxiv_version",
            "arxiv_revision",
            "arxiv_id_version",
            "actual_pdf_publication_identity",
            "actual_pdf_bibliographic_header",
            "journal",
            "volume",
            "issue",
            "year",
            "pages",
            "repository",
            "record_status",
            "distribution",
            "review_scope",
            "limitation",
        ):
            if version.get(key) is not None:
                parts.append(key.replace("_", " ") + ": " + str(version[key]))
        for key, value in version.items():
            if value is False and ("equivalence" in key or "alignment" in key):
                parts.append(key.replace("_", " ") + ": not established")
        entry["version"] = "; ".join(parts)
    return entry


def protect_public_urls(text, transform):
    """A public repository UUID is a source identity, not an internal task token."""
    urls = {}

    def replace(match):
        url = match[0]
        if re.match(r"https://(?:chatgpt\.com|chat\.openai\.com)/", url, re.I):
            return "[internal link omitted]"
        marker = f"ELVIAPUBLICURLPLACEHOLDER{len(urls)}END"
        urls[marker] = url
        return marker

    text = re.sub(r"https://[^\s<>\"']+", replace, text)
    text = transform(text)
    for marker, url in urls.items():
        text = text.replace(marker, url)
    return text


def public_text(value):
    """Preserve mathematical domains and portable evidence references."""
    parts = re.split(r"(\\\(.*?\\\)|\\\[.*?\\\])", str(value), flags=re.S)
    plain = helper("import_icml_batches.py")["_public_plain"]
    for index in range(0, len(parts), 2):
        text = ARCHIVE_ROOT.sub("", parts[index])
        text = re.sub(
            r"(?:verification|papers|sources|reports)[\\/][^\s\"<>]+",
            lambda m: m[0].replace("\\", "/"),
            text,
        )
        text = re.sub(r"\b(?:accept|chat|recovery)-\d{4}\b", "[internal task]", text)
        parts[index] = protect_public_urls(text, plain)
    return "".join(parts).strip()


def report_text(value):
    return protect_public_urls(
        public_text(value), helper("import_icml_batches.py")["report_text"]
    )


def public_data(value):
    if isinstance(value, dict):
        return {
            k: public_data(v)
            for k, v in value.items()
            if not PRIVATE_KEY.search(k) and k.casefold() not in OPERATION_KEYS
        }
    if isinstance(value, list):
        return [public_data(item) for item in value]
    return public_text(value) if isinstance(value, str) else value


def reviewed_rating(paper_id, findings, hashes, reviewed):
    row = reviewed.get(paper_id)
    if row is not None:
        if (
            row.get("findings_sha256") != hashes["findings"]
            or row.get("report_tex_sha256") != hashes["tex"]
            or row.get("rating") not in RATINGS
            or not row.get("basis")
        ):
            raise ValueError(f"{paper_id}: reviewed classification binding mismatch")
        return row["rating"]
    return helper("import_icml_batches.py")["paper_rating"](findings)


def finding_items(findings):
    """Select current explicit finding containers, never rejected candidates."""
    for key in ("problems", "findings", "issues", "confirmed_findings"):
        values = findings.get(key)
        if isinstance(values, dict):
            if any(k in values for k in ("claim", "title", "severity", "location")):
                values = [values]
            else:
                values = [
                    dict(v, id=v.get("id", str(k)))
                    for k, v in values.items()
                    if isinstance(v, dict)
                ]
        if isinstance(values, list) and values:
            if not all(isinstance(v, dict) for v in values):
                raise ValueError(f"unsupported finding structure: {key}")
            return values
    result = []
    for key in ("major", "minor", "confirmed_major", "confirmed_minor"):
        values = findings.get(key)
        if isinstance(values, list):
            result += [
                dict(v, severity=v.get("severity", key.removeprefix("confirmed_")))
                for v in values
                if isinstance(v, dict)
            ]
    confirmed = findings.get("confirmed")
    if not result and isinstance(confirmed, list):
        result = [v for v in confirmed if isinstance(v, dict)]
    if not result and isinstance(confirmed, dict):
        for key in ("findings", "problems", "items"):
            if isinstance(confirmed.get(key), list):
                result = confirmed[key]
                break
    return result


def finding_rating(item):
    """Read explicit labels only, including historical spelling variants."""

    def label(value):
        if not isinstance(value, str):
            return None
        compact = re.sub(r"[^a-z]", "", value.casefold())
        if compact.startswith("needsevidence"):
            return "needs_evidence"
        if compact.startswith(("scopeclarification", "noissuefound")):
            return "no_issue_found"
        return helper("import_icml_batches.py")["label"](value)

    for key in (
        "severity",
        "assessment",
        "classification",
        "category",
        "supported_impact",
        "status",
    ):
        if result := label(item.get(key)):
            return result
    for key in ("independent_verification", "independent_acceptance"):
        nested = item.get(key)
        if isinstance(nested, dict):
            for field in ("severity", "severity_confirmed", "assessment"):
                if result := label(nested.get(field)):
                    return result
    return None


def make_problems(findings, report):
    base = helper("import_icml_batches.py")
    restoration = helper("restore_case_proofs.py")
    items = finding_items(findings)
    problems = [
        base["normalize_problem"](item, i, report=report)
        for i, item in enumerate(items, 1)
    ]
    sections = restoration["numbered_mapping"](report, problems) if problems else None
    for index, (item, problem) in enumerate(zip(items, problems, strict=True)):
        rating = finding_rating(item)
        if rating:
            problem["severity"] = rating
            problem["assessment"] = (
                "supported"
                if rating in {"major", "minor"}
                else "needs_evidence"
                if rating == "needs_evidence"
                else "not_issue"
            )
        identifier = str(
            item.get("id")
            or item.get("problem_id")
            or item.get("issue_id")
            or problem["id"]
        )
        portable = re.sub(r"[^a-z0-9]+", "-", identifier.casefold()).strip("-")
        problem["id"] = portable or problem["id"]
        problem["source_finding_id"] = identifier
        if sections:
            restored = restoration["restore_section"](report, sections[index])
            problem.update(restoration["restored_fields"](problem, restored))
        problem["claim_heading"] = "Statement"
        if problem.get("analysis_heading") not in {"Proof", "Verification"}:
            problem["analysis_heading"] = "Verification"
        method = item.get("method") or item.get("verification_method")
        if isinstance(method, str) and method.strip():
            problem["method"] = method
    if len({p["id"] for p in problems}) != len(problems):
        raise ValueError("duplicate source finding identifiers")
    return problems


@cache
def parser_fingerprint(pandoc):
    executable = Path(shutil.which(str(pandoc)) or pandoc).resolve(strict=True)
    return (
        sha(Path(__file__).with_name("math_report_text.py"))
        + sha(Path(__file__).with_name("icml_report_text.py"))
        + sha(Path(__file__).with_name("math2025-report-cleanup.json"))
        + sha(Path(__file__).with_name("math_publication_format.py"))
        + sha(Path(__file__).with_name("math2025-presentation-overrides.json"))
        + sha(Path(__file__).with_name("math2025-pdf-presentation.json"))
        + sha(executable)
    )


def cleanup_overrides(case_id):
    return read(Path(__file__).with_name("math2025-report-cleanup.json"))["cases"].get(
        case_id, []
    )


def prepare_input(raw, state, paper_id, reviewed, pandoc, cache_dir):
    number = paper_id[-4:]
    paths, hashes = verify_core(
        raw, paper_id, state["accepted_integrity_records"][paper_id]
    )
    findings = read(raw / paths["findings"])
    if findings.get("paper_id", paper_id) != paper_id:
        raise ValueError(f"{paper_id}: findings identity mismatch")
    rating = reviewed_rating(paper_id, findings, hashes, reviewed)
    entry = source_entry(read(raw / paths["source_manifest"]), number)
    if entry.get("sha256") != hashes["article"]:
        raise ValueError(f"{paper_id}: exact source PDF hash mismatch")
    cleanup_path = Path(__file__).with_name("report_cleanup.py")
    key = hashlib.sha256(
        (
            hashes["tex"]
            + parser_fingerprint(pandoc)
            + sha(cleanup_path)
            + sha(Path(__file__))
        ).encode()
    ).hexdigest()
    cached = cache_dir / (key + ".json") if cache_dir else None
    if cached and cached.is_file():
        report_info = read(cached)
    else:
        paragraphs = helper("math_report_text.py")["report_paragraphs"](
            (raw / paths["tex"]).read_text("utf-8-sig"), pandoc=pandoc
        )
        paragraphs = [report_text(p) for p in paragraphs]
        cleanup = helper("report_cleanup.py")["clean_paragraphs"](
            paragraphs,
            case_id="math2025-" + number,
            reviewed=cleanup_overrides("math2025-" + number),
        )
        report = cleanup["paragraphs"]
        formatted = helper("report_cleanup.py")["format_report_paragraphs"](
            report, case_id="math2025-" + number
        )
        if isinstance(formatted, dict):
            report = formatted["paragraphs"]
        else:
            report = formatted
        presentation_edits = []
        report = helper("math_publication_format.py")["format_publication_data"](
            report,
            case_id="math2025-" + number,
            source_report_sha256=hashes["tex"],
            audit=presentation_edits,
            location="report",
        )
        report_info = {
            "paragraphs": report,
            "presentation_edits": presentation_edits,
            "preserved_math": cleanup["preserved_math"],
            "cleanup_review": public_data(cleanup["review"]),
            "cleanup_edit_count": len(cleanup["edits"]),
        }
        if cached:
            cached.parent.mkdir(parents=True, exist_ok=True)
            write(cached, report_info)
    return {
        "paper_id": paper_id,
        "number": number,
        "hashes": hashes,
        "findings": public_data(findings),
        "coverage": public_data(read(raw / paths["coverage"])),
        "rating": rating,
        "source": public_data(entry),
        **report_info,
    }


def import_collection(raw, output, assessments, pandoc, cache_dir=None, expected=514):
    raw, output = Path(raw), Path(output)
    if output.exists():
        raise FileExistsError("publication requires a new destination")
    state_path = raw / CONTROL_ROOT / "controller_state.json"
    state = read(state_path)
    selected = selected_ids(state)
    if len(selected) != expected:
        raise ValueError(f"expected {expected} accepted papers, found {len(selected)}")
    rows = {
        row["paper_id"]: row
        for row in read(raw / CONTROL_ROOT / "papers_2025_887.json")
    }
    memberships = {
        row["paper_id"]: row
        for row in read(raw / CONTROL_ROOT / "membership_catalog_887.json")["papers"]
    }
    if not set(selected) <= rows.keys() & memberships.keys():
        raise ValueError("accepted paper missing from frozen membership")
    reviewed = read(assessments)
    if reviewed.get("format_version") != 1:
        raise ValueError("unsupported reviewed assessment format")
    reviewed = reviewed["cases"]
    errors, prepared = [], []

    def prepare(paper_id):
        try:
            return prepare_input(raw, state, paper_id, reviewed, pandoc, cache_dir)
        except Exception as exc:
            return {"paper_id": paper_id, "error": str(exc)}

    with ThreadPoolExecutor(max_workers=4) as pool:
        for item in pool.map(prepare, selected):
            if "error" in item:
                errors.append(item)
            else:
                prepared.append(item)
            if (len(prepared) + len(errors)) % 50 == 0:
                print(
                    f"Prepared {len(prepared)} reports; {len(errors)} errors",
                    flush=True,
                )
    if errors:
        if cache_dir:
            log = cache_dir / "import-errors.json"
            log.write_text(json.dumps(errors, indent=2) + "\n", encoding="utf-8")
        raise ValueError(f"{len(errors)} input errors: {errors[:5]}")
    now = datetime.now(UTC).isoformat()
    catalogs = {
        name: {"format_version": 1, "cases": {}}
        for name in ("case-notes", "reader-catalog", "research-fields", "math-notation")
    }
    manifest = {
        "format_version": 1,
        "selection": "integrity-accepted Math 2025",
        "accepted_paper_ids": selected,
        "controller_state_sha256": sha(state_path),
        "assessment_mapping_sha256": sha(assessments),
        "prepared_at": now,
        "scientific_reassessment_performed": False,
        "papers": [],
    }
    base = helper("import_icml_batches.py")
    with tempfile.TemporaryDirectory(prefix="elvia-math-publication-") as temporary:
        staging = Path(temporary) / "math2025"
        records = []
        for data in prepared:
            pid, number = data["paper_id"], data["number"]
            metadata, membership = rows[pid], memberships[pid]
            bibliographic = membership["record"]
            title = metadata["title"].strip()
            case = f"math2025-{number}"
            directory = staging / "evidence" / case
            directory.mkdir(parents=True)
            report, findings, coverage = (
                data[key] for key in ("paragraphs", "findings", "coverage")
            )
            (directory / "report.txt").write_text(
                "\n\n".join(report) + "\n", "utf-8", newline="\n"
            )
            write(directory / "findings.json", findings)
            write(directory / "coverage.json", coverage)
            (directory / "report.tex").write_text(
                helper("math_publication_format.py")["render_publication_tex"](
                    report, renderer=helper("report_cleanup.py")["render_icml_tex"]
                ),
                "utf-8",
                newline="\n",
            )
            provenance = {
                "paper_id": pid,
                "source_version": data["source"]["version"],
                "source_identity": data["source"],
                "archive_hashes": data["hashes"],
                "independent_ai_acceptance": True,
                "scientific_reassessment_performed": False,
                "scientific_decision": "pending",
                "human_reviews": [],
                "publication_issue": "https://github.com/chineseschrodingercat/elvia/issues/27",
            }
            source = staging / "source" / (case + ".md")
            source.parent.mkdir(exist_ok=True)
            source.write_text(
                f"# {title}\n\nPaper: {pid}\n\nJournal: {membership['journal']}\n\n"
                f"Publisher identity: {metadata['source_url']}\n\n"
                f"Exact reviewed version: {data['source']['version']}\n\n"
                f"Reviewed article SHA-256: {data['hashes']['article']}\n\n"
                f"Original report TeX SHA-256: {data['hashes']['tex']}\n\n"
                "Acceptance receipt SHA-256: "
                f"{data['hashes']['acceptance_receipt']}\n\n"
                "The journal identity and reviewed source version are distinct. "
                "A preprint finding is not attributed to an uninspected journal "
                "version. This publication preserves the independently checked "
                "AI-origin analysis; human scientific adjudication remains pending. "
                "Original archive files remain unchanged. Public copies omit private "
                "workflow identifiers and host paths.\n\n"
                "ELVIA analysis: Minhao Liu, CC BY 4.0. Source articles retain "
                "their own copyright and publication terms.\n",
                "utf-8",
                newline="\n",
            )

            def artifact(path):
                return {
                    "path": path.relative_to(staging).as_posix(),
                    "sha256": sha(path),
                }

            presentation_edits = list(data["presentation_edits"])
            problems = helper("math_publication_format.py")["format_publication_data"](
                make_problems(findings, report),
                case_id=case,
                source_report_sha256=data["hashes"]["tex"],
                audit=presentation_edits,
                location="problems",
            )
            presentation_rule_counts = {}
            for edit in presentation_edits:
                for rule, count in edit["rules"].items():
                    presentation_rule_counts[rule] = (
                        presentation_rule_counts.get(rule, 0) + count
                    )
            provenance["presentation_normalization"] = {
                "format_version": 1,
                "formatter_sha256": sha(
                    Path(__file__).with_name("math_publication_format.py")
                ),
                "overrides_sha256": sha(
                    Path(__file__).with_name("math2025-presentation-overrides.json")
                ),
                "source_math_span_count": data["preserved_math"],
                "source_cleanup_math_equality_gate_preserved": True,
                "rule_counts": presentation_rule_counts,
                "edits": presentation_edits,
            }
            provenance["pdf_presentation"] = {
                "catalog_sha256": sha(
                    Path(__file__).with_name("math2025-pdf-presentation.json")
                ),
                **helper("math_publication_format.py")["pdf_presentation_audit"](
                    (directory / "report.tex").read_text(encoding="utf-8")
                ),
            }
            write(directory / "provenance.json", provenance)
            summary = " ".join(
                base["text_rows"](
                    findings.get("summary") or findings.get("overall_summary")
                )
            )
            if not summary:
                summary = (
                    "Archived assessment: " + data["rating"].replace("_", " ").title()
                )
                titles = "; ".join(p["title"] for p in problems[:3])
                summary += ". " + titles if titles else "."
            limits = [
                public_text(text)
                for text in helper("icml_metadata.py")["collect_limits"](
                    findings, coverage
                )
            ]
            limits += [
                "The finding applies to the exact reviewed source version and "
                "inspected scope; uninspected publication versions "
                "are not adjudicated.",
                "The report retains counterevidence and unresolved questions. "
                "Publication does not repeat scientific review.",
                "Independent human scientific adjudication remains pending; "
                "author adoption has not been requested.",
            ]
            rating = data["rating"]
            outcome = (
                "candidate_issue"
                if rating in {"major", "minor"}
                else "needs_evidence"
                if rating == "needs_evidence"
                else "no_issue_found"
            )
            repairs = [
                s for p in problems if p["repair"] for s in p["repair"]["paragraphs"]
            ]
            if outcome == "no_issue_found":
                repairs = []
                for problem in problems:
                    problem["repair"] = None
            scope = (
                f"Accepted analysis of {pid}; exact scope and limits are "
                "retained in the complete report and coverage ledger."
            )
            authors = list(
                dict.fromkeys(
                    a.strip()
                    for a in metadata.get("authors", "").split(";")
                    if a.strip()
                )
            )
            doi = metadata.get("doi") or None
            record = {
                "schema_version": "1.2.0",
                "case_id": case,
                "revision": 1,
                "previous_revision": None,
                "case_type": "prospective_audit",
                "created_at": now,
                "source": {
                    "title": title,
                    "version": data["source"]["version"],
                    "doi": doi,
                    "arxiv_id": metadata.get("arxiv_id") or None,
                    "identifier_note": "Journal metadata identifies the work; "
                    "the reviewed PDF version and SHA-256 "
                    "identify the inspected source.",
                    "artifact": artifact(source),
                    "review_scope": scope,
                },
                "audit": {
                    "venue": membership["journal"],
                    "year": 2025,
                    "authors": authors,
                    "landing_url": metadata["source_url"],
                    "pdf_url": data["source"].get("source_url")
                    or metadata["source_url"],
                    "pdf_sha256": data["hashes"]["article"],
                    "retrieved_at": None,
                    "outcome": outcome,
                    "summary": summary,
                    "limitations": list(dict.fromkeys(limits)),
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
                        "id": eid,
                        "stance": stance,
                        "description": description,
                        "method": method,
                        "artifact": artifact(directory / filename),
                    }
                    for eid, stance, filename, description, method in [
                        (
                            "retained-findings",
                            "support",
                            "findings.json",
                            "Accepted findings with counterevidence "
                            "and bounded classifications.",
                            "Public transcription of accepted findings; "
                            "no reassessment.",
                        ),
                        (
                            "retained-report",
                            "support",
                            "report.txt",
                            "Complete public report with scientific "
                            "argument and limitations.",
                            "LaTeX parsed as data; no author code "
                            "or raw TeX execution.",
                        ),
                        (
                            "scope-and-rebuttal",
                            "rebuttal",
                            "coverage.json",
                            "Accepted coverage, counterevidence and unresolved scope.",
                            "Public copy of the retained coverage ledger.",
                        ),
                        (
                            "editable-latex",
                            "support",
                            "report.tex",
                            "Editable public report generated "
                            "from the same transcription.",
                            "Formatting conversion; original archive bytes preserved.",
                        ),
                        (
                            "acceptance-provenance",
                            "support",
                            "provenance.json",
                            "Exact accepted input identities "
                            "and publication provenance.",
                            "Receipt and seven core artifacts "
                            "hash-checked against live "
                            "and immutable accepted copies; "
                            "human adjudication pending.",
                        ),
                    ]
                ],
                "runs": [],
                "human_reviews": [],
                "adjudication": {
                    "status": "pending",
                    "rationale": "Independently checked "
                    "AI-origin analysis; independent human scientific adjudication "
                    "remains pending.",
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
                    "note": "Maintainer-authorized "
                    "publication of the 514 integrity-accepted Math 2025 analyses "
                    "(Issue #27). Existing scientific scope "
                    "and review state preserved.",
                },
            }
            errors = validate_record(record, staging)
            if errors:
                raise ValueError(pid + ": " + "\n".join(errors))
            save_record(record, staging / "records")
            bound = {"revision": 1, "record_sha256": record_digest(record)}
            catalogs["case-notes"]["cases"][case] = {
                **bound,
                "report": report,
                **({"problems": problems} if problems else {}),
            }
            pages = str(bibliographic.get("pages") or "").split("-")
            catalogs["reader-catalog"]["cases"][case] = {
                **bound,
                "citation": {
                    "title": title,
                    "authors": authors,
                    "container": membership["journal"],
                    "volume": str(bibliographic.get("volume") or ""),
                    "publisher": "",
                    "year": 2025,
                    "doi": doi,
                    "source_url": metadata["source_url"],
                    "first_page": pages[0],
                    "last_page": pages[-1] if len(pages) > 1 else "",
                },
                "contributors": [
                    {"name": "Minhao Liu", "role": "Initial report", "revision": 1}
                ],
                "verified_on": now[:10],
            }
            catalogs["research-fields"]["cases"][case] = {
                **bound,
                "field": "Mathematics",
                "reason": "Accepted article in the frozen "
                "Math 2025 journal collection.",
            }
            typeset = re.sub(r"\$([^$\n]+)\$", lambda m: r"\(" + m[1] + r"\)", title)
            if typeset != title:
                catalogs["math-notation"]["cases"][case] = {
                    **bound,
                    "replacements": [{"source": title, "typeset": typeset}],
                }
            manifest["papers"].append(
                {
                    "case_id": case,
                    "paper_id": pid,
                    "report_number": number,
                    "title": title,
                    "journal": membership["journal"],
                    "reviewed_version": data["source"]["version"],
                    "rating": rating,
                    "archive_hashes": data["hashes"],
                    "public_record_sha256": record_digest(record),
                    "public_report_source_sha256": sha(directory / "report.tex"),
                    "public_report_text_sha256": sha(directory / "report.txt"),
                    "preserved_math_spans": data["preserved_math"],
                    "cleanup_edit_count": data["cleanup_edit_count"],
                    "cleanup_review": data["cleanup_review"],
                    "presentation_edit_count": len(presentation_edits),
                    "presentation_rule_counts": presentation_rule_counts,
                }
            )
            records.append(record)
        prepare_case_notes(records, catalog=catalogs["case-notes"])
        for name, catalog in catalogs.items():
            write(staging / (name + ".json"), catalog)
        write(staging / "import-manifest.json", manifest)
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(staging, output)
    return len(records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--assessments", type=Path, required=True)
    parser.add_argument("--pandoc", default="pandoc")
    parser.add_argument("--cache", type=Path)
    parser.add_argument("--expected-count", type=int, default=514)
    args = parser.parse_args()
    print(
        import_collection(
            args.raw_root,
            args.output,
            args.assessments,
            args.pandoc,
            args.cache,
            args.expected_count,
        )
    )
