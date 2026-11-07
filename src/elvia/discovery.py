"""Small, source-bound loading projections of an already validated Atlas.

The complete public payload remains the export and scientific source of truth.
These projections only separate the inputs used by the existing browser views.
"""

import copy
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from elvia.public_context import presentation_points

CASE_MAPS = (
    "case_notes",
    "presentation",
    "research_fields",
    "reader",
    "reader_bundles",
)


def _fields(value, names):
    return {name: copy.deepcopy(value[name]) for name in names if name in value}


def _base(payload, collection_id, kind):
    if payload.get("format_version") != "1":
        raise ValueError("unsupported discovery source format")
    if not re.fullmatch(r"[a-f0-9]{64}", collection_id):
        raise ValueError("discovery requires the complete collection digest")
    return {
        "format_version": "1",
        "payload_kind": kind,
        "collection_id": collection_id,
        "case_count": len(payload["records"]),
        "counts": copy.deepcopy(payload.get("counts", {})),
        "records": [],
    }


def _listing_record(record):
    return {
        "case_id": record["case_id"],
        "revision": record["revision"],
        "source": _fields(record["source"], ("title",)),
        "audit": _fields(record["audit"], ("venue", "year", "outcome", "summary")),
        "concern": _fields(record.get("concern", {}), ("severity",)),
        "adjudication": _fields(record["adjudication"], ("status",)),
    }


def discovery_payload(payload, collection_id):
    """Keep all and only the existing list, filter and brief-rendering inputs."""
    result = _base(payload, collection_id, "discovery")
    result.update(case_notes={}, presentation={}, research_fields={})
    for record in payload["records"]:
        case_id = record["case_id"]
        result["records"].append(_listing_record(record))
        note = payload.get("case_notes", {}).get(case_id)
        current_note = (
            note if note and note.get("revision") == record["revision"] else None
        )
        if current_note:
            small_note = _fields(current_note, ("revision", "brief"))
            if "problems" in current_note:
                # Preserve source order for Read Problem N links after search.
                small_note["problems"] = [
                    _fields(problem, ("assessment", "severity"))
                    for problem in current_note["problems"]
                ]
            result["case_notes"][case_id] = small_note
        if case_id in payload.get("research_fields", {}):
            result["research_fields"][case_id] = payload["research_fields"][case_id]
        presentation = payload.get("presentation", {}).get(case_id)
        if presentation and presentation.get("revision") == record["revision"]:
            # The complete map contains notation for proofs and provenance too.
            # Only list titles and the existing visible brief need it at startup.
            visible = {
                record["source"]["title"],
                record["audit"]["summary"],
                " ".join(presentation_points(record, note=current_note)),
                *(current_note.get("brief", []) if current_note else []),
            }
            replacements = [
                copy.deepcopy(item)
                for item in presentation.get("replacements", [])
                if item["source"] in visible
            ]
            if replacements:
                result["presentation"][case_id] = {
                    **_fields(presentation, ("revision", "record_sha256")),
                    "replacements": replacements,
                }
    return result


def search_payload(payload, collection_id):
    """Retain every input read by search.js, without changing its algorithm.

    In particular, complete report text and full problem argument fields must
    remain available. A token-only index would lose the existing phrase bonus.
    """
    result = _base(payload, collection_id, "search")
    result.update(
        case_notes={},
        reader={},
        research_fields=copy.deepcopy(payload.get("research_fields", {})),
    )
    for record in payload["records"]:
        case_id = record["case_id"]
        projected = _listing_record(record)
        projected["source"] = _fields(
            record["source"], ("title", "version", "doi", "arxiv_id", "review_scope")
        )
        projected["audit"] = _fields(
            record["audit"],
            (
                "venue",
                "year",
                "outcome",
                "summary",
                "authors",
                "landing_url",
                "limitations",
            ),
        )
        projected["proposition"] = _fields(
            record.get("proposition", {}), ("claim", "location")
        )
        projected["concern"] = _fields(
            record.get("concern", {}), ("severity", "description")
        )
        result["records"].append(projected)
        note = payload.get("case_notes", {}).get(case_id)
        if note and note.get("revision") == record["revision"]:
            projected_note = _fields(note, ("revision", "report"))
            if "problems" in note:
                projected_note["problems"] = []
                for problem in note["problems"]:
                    projected_problem = _fields(
                        problem,
                        (
                            "title",
                            "assessment",
                            "severity",
                            "source_location",
                            "claim",
                            "assumptions",
                            "analysis",
                            "result",
                        ),
                    )
                    if "repair" in problem:
                        projected_problem["repair"] = (
                            _fields(problem["repair"], ("paragraphs",))
                            if isinstance(problem["repair"], dict)
                            else copy.deepcopy(problem["repair"])
                        )
                    projected_note["problems"].append(projected_problem)
            result["case_notes"][case_id] = projected_note
        reader = payload.get("reader", {}).get(case_id)
        if reader and reader.get("revision") == record["revision"]:
            projected_reader = _fields(reader, ("revision",))
            if isinstance(reader.get("citation"), dict):
                projected_reader["citation"] = _fields(reader["citation"], ("doi",))
            result["reader"][case_id] = projected_reader
    return result


def _search_chunks(value):
    """Match search.js flatten/normalize; keep every normalized word in order."""
    if isinstance(value, list):
        return [chunk for item in value for chunk in _search_chunks(item)]
    if not isinstance(value, (str, int, float)) or isinstance(value, bool):
        return []
    normalized = unicodedata.normalize("NFKC", str(value or "")).lower()
    normalized = re.sub(r"https?://(?:dx\.)?doi\.org/", "", normalized)
    normalized = " ".join(
        "".join(
            char if unicodedata.category(char)[0] in "LN" else " "
            for char in normalized
        ).split()
    )
    return [normalized] if normalized else []


def _base36(number):
    result = ""
    while number:
        result = "0123456789abcdefghijklmnopqrstuvwxyz"[number % 36] + result
        number //= 36
    return result or "0"


def compact_search_payload(payload, collection_id):
    """Encode repeated scientific prose once, preserving retrieval exactly.

    The dictionary stores complete normalized word sequences, including stop
    words, so phrase matches and paragraph boundaries retain their old meaning.
    It is a retrieval representation, not a replacement scientific export.
    Readable complete source text remains in data.json and each case payload.
    """
    result = search_payload(payload, collection_id)
    notes = result.pop("case_notes")
    chunks = {}
    documents = {}

    def field(value, weight, label, index=0, title="", display=0):
        references = []
        for chunk in _search_chunks(value):
            references.append(chunks.setdefault(chunk, len(chunks)))
        return [references, weight, label, index, title, display]

    for record in result["records"]:
        note = notes.get(record["case_id"])
        if not note:
            continue
        fields = []
        if isinstance(note.get("report"), list):
            fields.append(field(note["report"], 1, "complete retained report"))
        if record["audit"]["outcome"] not in (
            "no_issue_found",
            "scope_clarification",
        ):
            visible = []
            for offset, problem in enumerate(note.get("problems", [])):
                rating = (
                    "no_issue_found"
                    if problem.get("assessment") == "not_issue"
                    else "needs_evidence"
                    if problem.get("assessment") == "needs_evidence"
                    else "minor"
                    if problem.get("severity") == "moderate"
                    else problem.get("severity")
                )
                if rating != "no_issue_found":
                    rank = {"major": 0, "minor": 1, "needs_evidence": 2}.get(rating, 3)
                    visible.append((rank, offset, problem))
            for display, (_, offset, problem) in enumerate(sorted(visible), 1):
                label = f"Problem {display}"
                title = problem.get("title", "")
                fields.append(field(title, 5, label, offset + 1, title, display))
                repair = problem.get("repair")
                body = [
                    problem.get(name)
                    for name in (
                        "source_location",
                        "claim",
                        "assumptions",
                        "analysis",
                        "result",
                    )
                ]
                body.append(
                    repair.get("paragraphs") if isinstance(repair, dict) else None
                )
                fields.append(field(body, 3, label, offset + 1, title, display))
        documents[record["case_id"]] = {
            "revision": record["revision"],
            "fields": fields,
        }
    frequency = Counter(word for chunk in chunks for word in chunk.split())
    vocabulary = sorted(frequency, key=lambda word: (-frequency[word], word))
    codes = {word: _base36(index) for index, word in enumerate(vocabulary)}
    result["search_projection"] = {
        "encoding": "word-sequences-v1",
        "vocabulary": vocabulary,
        "chunks": [" ".join(codes[word] for word in chunk.split()) for chunk in chunks],
        "documents": documents,
    }
    return result


def case_payload(payload, record, collection_id):
    """Preserve complete scientific content for exactly one legacy case view."""
    result = _base(payload, collection_id, "case")
    result.update(
        case_id=record["case_id"],
        revision=record["revision"],
        case_count=1,
        records=[copy.deepcopy(record)],
    )
    result.pop("counts")
    for name in CASE_MAPS:
        entries = payload.get(name, {})
        result[name] = (
            {record["case_id"]: copy.deepcopy(entries[record["case_id"]])}
            if record["case_id"] in entries
            else {}
        )
    return result


def _json(value):
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), allow_nan=False)


def _script(value):
    return (
        _json(value)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )


def write_discovery_files(output: Path, payload):
    """Add projections after data.json is written, without changing any source.

    Hash actual file bytes: a Windows text writer can use CRLF, so hashing the
    pre-write Python string would bind a different collection on that platform.
    """
    source = (output / "data.json").read_bytes()
    if json.loads(source) != payload:
        raise ValueError("discovery source differs from the complete public payload")
    collection_id = hashlib.sha256(source).hexdigest()
    discovery = discovery_payload(payload, collection_id)
    (output / "discovery.json").write_bytes((_json(discovery) + "\n").encode("utf-8"))
    (output / "discovery.js").write_bytes(
        ("window.ELVIA_DISCOVERY = " + _script(discovery) + ";\n").encode("utf-8")
    )
    (output / "search-data.js").write_bytes(
        (
            "window.ELVIA_SEARCH_DATA = "
            + _script(compact_search_payload(payload, collection_id))
            + ";\n"
        ).encode("utf-8")
    )
    directory = output / "cases"
    directory.mkdir(exist_ok=True)
    for record in payload["records"]:
        case_id = record["case_id"]
        body = (
            "window.ELVIA_CASE_DATA = window.ELVIA_CASE_DATA || Object.create(null);\n"
            "window.ELVIA_CASE_DATA["
            + _json(case_id)
            + "] = "
            + _script(case_payload(payload, record, collection_id))
            + ";\n"
        )
        (directory / (case_id + ".data.js")).write_bytes(body.encode("utf-8"))
