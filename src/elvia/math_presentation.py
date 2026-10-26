"""Reviewed notation for frozen snapshots, separate from scientific evidence."""

import hashlib
import json
from importlib.resources import files


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _strings(child)


def prepare_presentation(records, *, catalog=None):
    """Return only notation reviewed for each exact selected record and revision.

    Unknown cases and later revisions use their own explicit TeX delimiters in
    the client. Never guess notation or carry a presentation to a new snapshot.
    A changed snapshot with the same identity fails before any export mutation.
    """
    if catalog is None:
        catalog = json.loads(
            files("elvia").joinpath("web/math-notation.json").read_text("utf-8")
        )
    if (
        not isinstance(catalog, dict)
        or catalog.get("format_version") != 1
        or not isinstance(catalog.get("cases"), dict)
    ):
        raise ValueError("unsupported math presentation format")
    result = {}
    for record in records:
        presentation = catalog["cases"].get(record["case_id"])
        if not presentation or presentation["revision"] != record["revision"]:
            continue
        canonical = json.dumps(
            record, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
        if hashlib.sha256(canonical).hexdigest() != presentation["record_sha256"]:
            raise ValueError("math presentation does not match scientific snapshot")
        originals = set(_strings(record))
        seen = set()
        for item in presentation["replacements"]:
            source = item["source"]
            if source not in originals or source in seen:
                raise ValueError("math presentation has stale or duplicate source text")
            if not isinstance(item["typeset"], str):
                raise ValueError("math presentation requires typeset text")
            seen.add(source)
        result[record["case_id"]] = presentation
    return result
