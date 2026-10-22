"""Create a new collection with additive, individually reviewed revisions.

Original snapshots and referenced bytes stay unchanged. New scientific content
comes from an individual review, never from an automatic impact classifier.
"""

import argparse
import copy
import hashlib
import json
import runpy
import shutil
import tempfile
from pathlib import Path

from elvia.case_notes import prepare_case_notes
from elvia.reader import prepare_reader
from elvia.records import _artifacts
from elvia.storage import load_records, save_record

IMPORTER = runpy.run_path(str(Path(__file__).with_name("import_review_collection.py")))
SOURCE_IDENTITY = ("title", "version", "doi", "arxiv_id")
AUDIT_IDENTITY = (
    "venue",
    "year",
    "authors",
    "landing_url",
    "pdf_url",
    "pdf_sha256",
    "retrieved_at",
)


def capture_collection(records, entries):
    """Capture only registered bytes, bound to the already validated records."""
    records = Path(records)
    allowed = {"README.md", "case-notes.json", "reader-catalog.json"}
    for path, record in entries:
        allowed.add("records/" + path.name)
        allowed.update(item["path"] for _, item in _artifacts(record))
    snapshot = {}
    for path in records.parent.rglob("*"):
        if (
            path.is_file()
            and path.relative_to(records.parent).as_posix() not in allowed
        ):
            raise ValueError("existing collection contains an unregistered file")
        if not path.resolve().is_relative_to(records.parent.resolve()):
            raise ValueError("existing collection contains an escaping path")
        if path.is_file():
            snapshot[path.relative_to(records.parent).as_posix()] = path.read_bytes()
    for path, record in entries:
        if json.loads(snapshot["records/" + path.name]) != record:
            raise ValueError("existing record changed during validation")
        for _, item in _artifacts(record):
            if hashlib.sha256(snapshot[item["path"]]).hexdigest() != item["sha256"]:
                raise ValueError("existing artifact changed during validation")
    if "reader-catalog.json" in snapshot:
        catalog = json.loads(snapshot["reader-catalog.json"])
        selected = prepare_reader([record for _, record in entries], catalog)
        if set(selected) != set(catalog["cases"]):
            raise ValueError("reader catalog references an unknown scientific snapshot")
    return snapshot


def validate_assessment(audit):
    """Require one assessment to follow the current individual-impact rubric."""
    for item in (audit, *audit["problems"]):
        if item["severity"] == "moderate":
            raise ValueError("new assessments use Major or Minor, not Moderate")
        if (
            not isinstance(item.get("impact_rationale"), str)
            or not item["impact_rationale"].strip()
        ):
            raise ValueError(
                "each revised assessment requires an individual impact rationale"
            )
    if any(p["assessment"] == "not_issue" and p["repair"] for p in audit["problems"]):
        raise ValueError(
            "a cleared concern may clarify scope but cannot propose a paper repair"
        )


def validate_assessments(audits):
    """Require individually recorded rationales and the current impact rubric."""
    for path in sorted(Path(audits).glob("[0-9][0-9][0-9][0-9].json")):
        validate_assessment(json.loads(path.read_text("utf-8")))


def revise_collection(records, audits, raw_root, output, *, expected_count=150):
    records, audits, output = Path(records), Path(audits), Path(output)
    if output.exists() or output.is_symlink():
        raise FileExistsError("review revision requires a new destination")
    old_entries = load_records(records)
    snapshot = capture_collection(records, old_entries)
    latest = {r["case_id"]: r for _, r in old_entries}
    if len(latest) != expected_count:
        raise ValueError("existing collection does not match the reviewed case count")
    for prior in latest.values():
        if (
            prior["adjudication"]["status"] != "pending"
            or prior["human_reviews"]
            or prior["repair"]["adoption_status"] != "not_requested"
        ):
            raise ValueError(
                "editorial revision cannot replace a human decision or adoption"
            )
    validate_assessments(audits)

    with tempfile.TemporaryDirectory(prefix="elvia-revision-") as temporary:
        temporary = Path(temporary)
        generated = temporary / "reviewed"
        IMPORTER["import_collection"](
            audits, raw_root, generated, expected_count=expected_count
        )
        fresh = load_records(generated / "records")
        if {r["case_id"] for _, r in fresh} != set(latest):
            raise ValueError("revised review identities differ from the existing cases")
        catalog = json.loads((generated / "case-notes.json").read_text("utf-8"))
        staging = temporary / "complete"
        staging.mkdir()
        for name, payload in snapshot.items():
            destination = staging / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("xb") as stream:
                stream.write(payload)
        updated = []
        for _, record in fresh:
            case_id = record["case_id"]
            prior = latest[case_id]
            if any(
                record["source"][k] != prior["source"][k] for k in SOURCE_IDENTITY
            ) or any(record["audit"][k] != prior["audit"][k] for k in AUDIT_IDENTITY):
                raise ValueError(
                    "source identity cannot change in an editorial revision"
                )
            record["revision"] = prior["revision"] + 1
            record["previous_revision"] = prior["revision"]
            record["source"]["artifact"] = copy.deepcopy(prior["source"]["artifact"])
            directory = Path("evidence") / case_id / f"r{record['revision']}"
            target = staging / directory
            target.mkdir(parents=True, exist_ok=False)
            for item in record["evidence"]:
                source = generated / item["artifact"]["path"]
                destination = target / source.name
                with destination.open("xb") as stream:
                    stream.write(source.read_bytes())
                item["artifact"]["path"] = (directory / source.name).as_posix()
            audit = json.loads((target / "verification.json").read_text("utf-8"))
            record["concern"]["description"] = (
                audit["summary"] + "\n\nImpact assessment. " + audit["impact_rationale"]
            )
            record["adjudication"]["history"] = copy.deepcopy(
                prior["adjudication"]["history"]
            ) + [
                {
                    "at": record["created_at"],
                    "status": "pending",
                    "rationale": "Maintainer-reviewed impact reassessment and "
                    "updated reasoning; scientific adjudication remains pending.",
                }
            ]
            record["publication"]["note"] = (
                "Maintainer-authorized revision. "
                "Impact reassessment "
                "and typesetting do not constitute independent scientific confirmation "
                "or author adoption."
            )
            save_record(record, staging / "records")
            if case_id in catalog["cases"]:
                note = catalog["cases"][case_id]
                note["revision"] = record["revision"]
                canonical = json.dumps(
                    record, sort_keys=True, separators=(",", ":"), ensure_ascii=True
                ).encode()
                note["record_sha256"] = hashlib.sha256(canonical).hexdigest()
            updated.append(record)
        load_records(staging / "records")
        prepare_case_notes(updated, catalog=catalog)
        (staging / "case-notes.json").write_text(
            json.dumps(catalog, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        output.mkdir(parents=True, exist_ok=False)
        try:
            shutil.copytree(staging, output, dirs_exist_ok=True)
        except BaseException:
            shutil.rmtree(output)
            raise
    return len(updated)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", required=True, type=Path)
    parser.add_argument("--audits", required=True, type=Path)
    parser.add_argument("--raw-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--expected-count", type=int, default=300)
    args = parser.parse_args()
    count = revise_collection(
        args.records,
        args.audits,
        args.raw_root,
        args.output,
        expected_count=args.expected_count,
    )
    print(f"Created {count} additive review revisions with unchanged predecessors")


if __name__ == "__main__":
    main()
