"""Apply reviewed Math 2025 citation metadata without editing scientific records.

The catalog is a fixed transcription of identified publisher/Crossref evidence.
Each entry is bound to the accepted source manifest and the exact before/after
citation.  Unknown metadata, identities, and changed source hashes fail closed.
"""

import argparse
import copy
import hashlib
import json
import re
from functools import cache
from pathlib import Path

CATALOG_NAME = "math2025-citation-enrichment.json"
ALLOWED_FIELDS = {
    "volume",
    "year",
    "first_page",
    "last_page",
    "publisher",
    "publication_status",
    "publication_type",
}
CASE_ID = re.compile(r"math2025-\d{4}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()


def _hash(value, label):
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        raise ValueError(f"invalid {label} SHA-256")
    return value


@cache
def _load_catalog(path):
    raw = Path(path).read_bytes()
    catalog = json.loads(raw.decode("utf-8-sig"))
    if (
        catalog.get("format_version") != 1
        or catalog.get("collection") != "math2025"
        or not isinstance(catalog.get("cases"), dict)
    ):
        raise ValueError("unsupported Math citation catalog")
    return catalog, hashlib.sha256(raw).hexdigest()


def _catalog_path(catalog_path):
    return str(Path(catalog_path or Path(__file__).with_name(CATALOG_NAME)).resolve())


def _validate_citation(citation):
    for key in ("volume", "first_page", "last_page", "publisher"):
        if not isinstance(citation.get(key, ""), str):
            raise ValueError(f"invalid citation {key}")
    year = citation.get("year")
    if type(year) is not int or not 1800 <= year <= 2200:
        raise ValueError("invalid citation year")
    status = citation.get("publication_status")
    if status is not None and status != "online_first":
        raise ValueError("unsupported citation publication status")
    if not citation.get("volume", "").strip() and status != "online_first":
        raise ValueError("citation volume is unresolved")
    if status == "online_first" and citation.get("volume", "").strip():
        raise ValueError("online-first citation cannot invent an assigned volume")
    if citation.get("publication_type") != "journal":
        raise ValueError("Math citation must retain its verified journal type")
    if citation.get("last_page") and not citation.get("first_page"):
        raise ValueError("last page requires an explicit first page")


def enrich_reader_row(case_id, row, source_manifest_sha256, *, catalog_path=None):
    """Return an enriched copy, preserving record binding and every other field.

    Importers pass the source hash already verified against the accepted receipt.
    The standalone collection updater also verifies the scientific record binding
    against the existing import manifest before calling this function.
    """
    if not CASE_ID.fullmatch(case_id):
        raise ValueError("citation enrichment is limited to Math 2025")
    source_hash = _hash(source_manifest_sha256, "accepted source manifest")
    catalog, catalog_hash = _load_catalog(_catalog_path(catalog_path))
    entry = catalog["cases"].get(case_id)
    if not isinstance(entry, dict) or entry.get("status") != "resolved":
        raise ValueError(f"{case_id}: unresolved citation metadata")
    if entry.get("source_manifest_sha256") != source_hash:
        raise ValueError(f"{case_id}: accepted source manifest changed")
    updates = entry.get("updates")
    if not isinstance(updates, dict) or set(updates) - ALLOWED_FIELDS:
        raise ValueError(f"{case_id}: citation update changes unsupported fields")
    sources = entry.get("field_sources")
    if not isinstance(sources, dict) or any(not sources.get(k) for k in updates):
        raise ValueError(f"{case_id}: citation update lacks field evidence")
    if updates.get("publication_status") == "online_first" and not entry.get(
        "online_first_evidence"
    ):
        raise ValueError(f"{case_id}: online-first status lacks explicit evidence")
    before_hash = _hash(entry.get("citation_before_sha256"), "original citation")
    after_hash = _hash(entry.get("citation_after_sha256"), "enriched citation")
    citation = row.get("citation")
    if not isinstance(citation, dict):
        raise ValueError(f"{case_id}: missing reader citation")
    current_hash = digest(citation)
    if current_hash not in {before_hash, after_hash}:
        raise ValueError(f"{case_id}: citation differs from reviewed before/after")
    result = copy.deepcopy(row)
    if current_hash == before_hash:
        # An existing verified volume is never overwritten by enrichment.
        if citation.get("volume") and (
            updates.get("volume", citation["volume"]) != citation["volume"]
        ):
            raise ValueError(f"{case_id}: existing verified volume would change")
        result["citation"].update(updates)
    if digest(result["citation"]) != after_hash:
        raise ValueError(f"{case_id}: enriched citation does not match reviewed hash")
    _validate_citation(result["citation"])
    provenance = {
        "format_version": 1,
        "source_manifest_sha256": source_hash,
        "catalog_sha256": catalog_hash,
        "entry_sha256": digest(entry),
        "citation_before_sha256": before_hash,
        "citation_after_sha256": after_hash,
    }
    old_provenance = result.get("citation_provenance")
    if old_provenance is not None and old_provenance != provenance:
        raise ValueError(f"{case_id}: conflicting existing citation provenance")
    result["citation_provenance"] = provenance
    return result


def enrich_reader_catalog(reader_catalog, import_manifest, *, catalog_path=None):
    """Update only Math reader rows; scientific records and other rows are inert."""
    if reader_catalog.get("format_version") != 1 or not isinstance(
        reader_catalog.get("cases"), dict
    ):
        raise ValueError("unsupported reader catalog")
    bindings = {}
    for paper in import_manifest.get("papers", []):
        case_id = paper.get("case_id", "")
        if not CASE_ID.fullmatch(case_id):
            continue
        if case_id in bindings:
            raise ValueError(f"duplicate import binding: {case_id}")
        bindings[case_id] = paper
    output = copy.deepcopy(reader_catalog)
    for case_id, row in reader_catalog["cases"].items():
        if not CASE_ID.fullmatch(case_id):
            continue
        paper = bindings.get(case_id)
        if paper is None or paper.get("public_record_sha256") != row.get(
            "record_sha256"
        ):
            raise ValueError(f"{case_id}: import record binding mismatch")
        output["cases"][case_id] = enrich_reader_row(
            case_id,
            row,
            paper.get("archive_hashes", {}).get("source_manifest"),
            catalog_path=catalog_path,
        )
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reader-catalog", type=Path, required=True)
    parser.add_argument("--import-manifest", type=Path, required=True)
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.reader_catalog.read_text("utf-8-sig"))
    manifest = json.loads(args.import_manifest.read_text("utf-8-sig"))
    output = enrich_reader_catalog(source, manifest, catalog_path=args.catalog)
    # Never overwrite the only existing catalog on a failed or partial update.
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(output, stream, ensure_ascii=True, indent=2, allow_nan=False)
        stream.write("\n")
    changed = sum(source["cases"][k] != v for k, v in output["cases"].items())
    print(f"Enriched {changed} Math reader rows; scientific records unchanged")


if __name__ == "__main__":
    main()
