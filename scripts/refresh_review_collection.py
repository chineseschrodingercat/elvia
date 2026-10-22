"""Add explicit latest-source revisions for a reviewed subset of a collection."""

import argparse
import copy
import hashlib
import json
import runpy
import shutil
import tempfile
from pathlib import Path

from elvia.case_notes import prepare_case_notes
from elvia.storage import load_records, save_record

SCRIPTS = Path(__file__).resolve().parent
IMPORTER = runpy.run_path(str(SCRIPTS / "import_review_collection.py"))
REVISION = runpy.run_path(str(SCRIPTS / "revise_review_collection.py"))


def _canonical_hash(record):
    return hashlib.sha256(
        json.dumps(
            record, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode()
    ).hexdigest()


def refresh_collection(records, audits, raw_root, output, *, expected_count=150):
    records, audits, raw_root, output = map(Path, (records, audits, raw_root, output))
    if output.exists() or output.is_symlink():
        raise FileExistsError("source refresh requires a new destination")
    old_entries = load_records(records)
    snapshot = REVISION["capture_collection"](records, old_entries)
    latest = {record["case_id"]: record for _, record in old_entries}
    catalog = json.loads(snapshot["case-notes.json"])
    prepare_case_notes(list(latest.values()), catalog=catalog)
    REVISION["validate_assessments"](audits)
    with tempfile.TemporaryDirectory(prefix="elvia-source-refresh-") as temporary:
        temporary = Path(temporary)
        generated = temporary / "reviewed"
        IMPORTER["import_collection"](
            audits, raw_root, generated, expected_count=expected_count, issue_number=27
        )
        fresh = load_records(generated / "records")
        incoming = REVISION["capture_collection"](generated / "records", fresh)
        notes = json.loads(incoming["case-notes.json"])["cases"]
        staging = temporary / "combined"
        staging.mkdir()
        for name, payload in snapshot.items():
            destination = staging / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("xb") as stream:
                stream.write(payload)
        refreshed = set()
        for _, record in fresh:
            verification = next(
                e["artifact"]
                for e in record["evidence"]
                if e["artifact"]["path"].endswith("/verification.json")
            )
            audit = json.loads(incoming[verification["path"]])
            REVISION["validate_assessment"](audit)
            prefix = f"neurips2025-{audit['report_id']}-"
            matches = [r for key, r in latest.items() if key.startswith(prefix)]
            if len(matches) != 1:
                raise ValueError(
                    "source refresh requires one existing corresponding case"
                )
            prior = matches[0]
            case_id = prior["case_id"]
            if case_id in refreshed:
                raise ValueError("duplicate source refresh identity")
            if (
                prior["adjudication"]["status"] != "pending"
                or prior["human_reviews"]
                or prior["repair"]["adoption_status"] != "not_requested"
            ):
                raise ValueError(
                    "source refresh cannot replace human decisions or adoption"
                )
            old_fresh_id = record["case_id"]
            record.update(
                case_id=case_id,
                schema_version="1.3.0",
                revision=prior["revision"] + 1,
                previous_revision=prior["revision"],
            )
            record["source_update"] = {
                "previous_record_sha256": _canonical_hash(prior),
                "checked_at": record["created_at"],
                "reason": (
                    "Issue #27: latest paper/resource inspection; fixed historical "
                    "concerns do not count as current errors."
                ),
                "correspondence": audit["provenance_note"],
            }
            source_name = f"source/{case_id}.r{record['revision']}.md"
            source_path = staging / source_name
            with source_path.open("xb") as stream:
                stream.write(incoming[record["source"]["artifact"]["path"]])
            record["source"]["artifact"]["path"] = source_name
            directory = Path("evidence") / case_id / f"r{record['revision']}"
            target = staging / directory
            target.mkdir(parents=True, exist_ok=False)
            for item in record["evidence"]:
                original = item["artifact"]["path"]
                name = Path(original).name
                with (target / name).open("xb") as stream:
                    stream.write(incoming[original])
                item["artifact"]["path"] = (directory / name).as_posix()
            record["concern"]["description"] = (
                audit["summary"] + "\n\nImpact assessment. " + audit["impact_rationale"]
            )
            record["adjudication"]["history"] = copy.deepcopy(
                prior["adjudication"]["history"]
            ) + [
                {
                    "at": record["created_at"],
                    "status": "pending",
                    "rationale": (
                        "Issue #27: refreshed source versions and current concern "
                        "status; no human adjudication."
                    ),
                }
            ]
            save_record(record, staging / "records")
            catalog["cases"].pop(case_id, None)
            if old_fresh_id in notes:
                note = notes[old_fresh_id]
                note["revision"] = record["revision"]
                note["record_sha256"] = _canonical_hash(record)
                catalog["cases"][case_id] = note
            refreshed.add(case_id)
        combined = load_records(staging / "records")
        current = {record["case_id"]: record for _, record in combined}
        titles = [
            " ".join(r["source"]["title"].casefold().split()) for r in current.values()
        ]
        hashes = [r["audit"]["pdf_sha256"] for r in current.values()]
        if len(set(titles)) != len(titles) or len(set(hashes)) != len(hashes):
            raise ValueError("duplicate current paper identity after source refresh")
        prepare_case_notes(list(current.values()), catalog=catalog)
        (staging / "case-notes.json").write_text(
            json.dumps(catalog, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        output.mkdir(parents=True, exist_ok=False)
        try:
            shutil.copytree(staging, output, dirs_exist_ok=True)
        except BaseException:
            shutil.rmtree(output)
            raise
    return len(refreshed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("records", "audits", "raw-root", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    count = refresh_collection(args.records, args.audits, args.raw_root, args.output)
    print(f"Created {count} source-refresh revisions with all predecessors unchanged")


if __name__ == "__main__":
    main()
