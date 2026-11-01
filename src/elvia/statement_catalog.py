"""Bind reading statements to immutable records and retained argument text."""

import copy
import hashlib
import json

from elvia.statement_display import statement_paragraphs


def statement_digest(value):
    canonical = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _check_entry(entry, problem, note, record):
    if not isinstance(entry, dict):
        raise ValueError("statement presentation must be an object")
    if entry.get("problem_sha256") != statement_digest(problem):
        raise ValueError("statement presentation does not match retained problem")
    paragraphs = entry.get("paragraphs")
    if not (
        isinstance(paragraphs, list)
        and paragraphs
        and all(isinstance(p, str) and p.strip() for p in paragraphs)
    ):
        raise ValueError("statement presentation requires complete paragraphs")
    basis = entry.get("basis")
    if not isinstance(basis, dict) or not basis:
        raise ValueError("statement presentation requires its source basis")
    if set(basis) - {"claim", "analysis", "report", "source_pdf"}:
        raise ValueError("statement presentation has an unknown source basis")
    supported = False
    for key in ("claim", "analysis", "report"):
        indices = basis.get(key, [])
        source = note.get("report", []) if key == "report" else problem.get(key, [])
        if not isinstance(indices, list) or any(
            type(index) is not int or not 0 <= index < len(source) for index in indices
        ):
            raise ValueError("statement presentation references unknown paragraphs")
        if len(set(indices)) != len(indices):
            raise ValueError("statement presentation repeats a paragraph reference")
        supported |= bool(indices)
    if "source_pdf" in basis:
        source = basis["source_pdf"]
        pages = source.get("pages", []) if isinstance(source, dict) else []
        if (
            not isinstance(source, dict)
            or source.get("sha256") != record.get("audit", {}).get("pdf_sha256")
            or not isinstance(pages, list)
            or not pages
            or any(type(page) is not int or page < 1 for page in pages)
        ):
            raise ValueError("statement presentation does not match the inspected PDF")
        supported = True
    if not supported:
        raise ValueError("statement presentation has no bound source paragraphs")


def prepare_statement_notes(records, notes, catalog=None):
    """Add shared display paragraphs without rewriting claims, proof or reports."""
    if catalog is None:
        cases = {}
    elif catalog.get("format_version") != 1 or not isinstance(
        catalog.get("cases"), dict
    ):
        raise ValueError("unsupported statement presentation format")
    else:
        cases = catalog["cases"]
    prepared = copy.deepcopy(notes)
    for record in records:
        case_id = record["case_id"]
        if case_id not in notes:
            continue
        original = notes[case_id]
        note = prepared[case_id]
        entry = cases.get(case_id)
        overrides = {}
        if entry is not None:
            if not isinstance(entry, dict):
                raise ValueError("statement case presentation must be an object")
            if entry.get("revision") != record["revision"]:
                entry = None
            elif entry.get("record_sha256") != statement_digest(record) or entry.get(
                "report_sha256"
            ) != statement_digest(original.get("report", [])):
                raise ValueError(
                    "statement presentation does not match retained sources"
                )
            if entry is not None:
                overrides = entry.get("problems")
                if not isinstance(overrides, dict) or set(overrides) - {
                    problem["id"] for problem in original.get("problems", [])
                }:
                    raise ValueError(
                        "statement presentation references unknown problems"
                    )
        for index, problem in enumerate(note.get("problems", [])):
            bound = overrides.get(problem["id"])
            if bound is not None:
                _check_entry(bound, original["problems"][index], original, record)
                problem["statement"] = list(bound["paragraphs"])
            else:
                problem["statement"] = statement_paragraphs(problem, original)
    return prepared
