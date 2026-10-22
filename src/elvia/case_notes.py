"""Snapshot-bound reader narratives derived from original preserved evidence."""

import hashlib
import json
import re
from importlib.resources import files


def _paragraphs(value, *, empty=False):
    return (
        isinstance(value, list)
        and (empty or bool(value))
        and all(isinstance(p, str) and p.strip() for p in value)
    )


def _check_problems(note, record):
    problems = note.get("problems")
    if not isinstance(problems, list) or not problems:
        raise ValueError("case note requires at least one inspected problem")
    evidence = {item["id"] for item in record["evidence"]}
    seen = set()
    for problem in problems:
        if not isinstance(problem, dict):
            raise ValueError("case note problem must be an object")
        identifier = problem.get("id")
        if (
            not isinstance(identifier, str)
            or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", identifier)
            or identifier in seen
        ):
            raise ValueError(
                "case note problem identifiers must be unique and portable"
            )
        seen.add(identifier)
        if "severity" in problem and problem["severity"] not in {
            "major",
            "moderate",
            "minor",
            "needs_evidence",
            "no_issue_found",
        }:
            raise ValueError("case note has an unknown problem severity")
        if "assessment" in problem and problem["assessment"] not in {
            "supported",
            "needs_evidence",
            "not_issue",
        }:
            raise ValueError("case note has an unknown problem assessment")
        for key in ("title", "source_location", "analysis_heading"):
            if not isinstance(problem.get(key), str) or not problem[key].strip():
                raise ValueError(f"case note requires {key}")
        for key in ("claim", "analysis", "result", "assumptions"):
            if not _paragraphs(problem.get(key), empty=key == "assumptions"):
                raise ValueError(f"case note requires readable {key} text")
        references = problem.get("evidence_ids")
        if (
            not _paragraphs(references)
            or len(set(references)) != len(references)
            or not set(references) <= evidence
        ):
            raise ValueError("case note references unknown or duplicate evidence")
        repair = problem.get("repair")
        if repair is not None:
            if not record["repair"]["content"]:
                raise ValueError("case note cannot invent an unrecorded repair")
            if (
                not isinstance(repair, dict)
                or not isinstance(repair.get("heading"), str)
                or not repair["heading"].strip()
                or not _paragraphs(repair.get("paragraphs"))
            ):
                raise ValueError("case note repair requires a heading and explanation")


def prepare_case_notes(records, *, catalog=None):
    """Select only narratives audited against the exact selected snapshots.

    Unknown cases and newer revisions use the record-driven browser fallback.
    Same-revision drift and invalid evidence/repair links fail before export.
    """
    if catalog is None:
        catalog = json.loads(
            files("elvia").joinpath("web/case-notes.json").read_text("utf-8")
        )
    if catalog.get("format_version") != 1 or not isinstance(catalog.get("cases"), dict):
        raise ValueError("unsupported case note presentation format")
    selected = {}
    for record in records:
        note = catalog["cases"].get(record["case_id"])
        if note is None:
            continue
        if not isinstance(note, dict):
            raise ValueError("case note must be an object")
        if note.get("revision") != record["revision"]:
            continue
        canonical = json.dumps(
            record, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
        if note.get("record_sha256") != hashlib.sha256(canonical).hexdigest():
            raise ValueError("case note does not match scientific snapshot")
        _check_problems(note, record)
        selected[record["case_id"]] = note
    return selected
