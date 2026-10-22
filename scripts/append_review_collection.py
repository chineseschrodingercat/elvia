"""Append newly reviewed papers without replacing existing scientific snapshots."""

import argparse
import json
import runpy
import shutil
import tempfile
from pathlib import Path

from elvia.case_notes import prepare_case_notes
from elvia.storage import load_records

SCRIPTS = Path(__file__).resolve().parent
IMPORTER = runpy.run_path(str(SCRIPTS / "import_review_collection.py"))
REVISION = runpy.run_path(str(SCRIPTS / "revise_review_collection.py"))


def _title_key(title):
    return " ".join(title.casefold().split())


def append_collection(records, audits, raw_root, output, *, expected_count=150):
    records, audits, raw_root, output = map(Path, (records, audits, raw_root, output))
    if output.exists() or output.is_symlink():
        raise FileExistsError("collection append requires a new destination")
    entries = load_records(records)
    snapshot = REVISION["capture_collection"](records, entries)
    catalog = json.loads(snapshot["case-notes.json"])
    latest = {record["case_id"]: record for _, record in entries}
    prepare_case_notes(list(latest.values()), catalog=catalog)
    REVISION["validate_assessments"](audits)
    titles = {_title_key(record["source"]["title"]) for record in latest.values()}
    pdf_hashes = {record["audit"]["pdf_sha256"] for record in latest.values()}
    for path in sorted(audits.glob("[0-9][0-9][0-9][0-9].json")):
        audit = json.loads(path.read_text("utf-8"))
        key = _title_key(audit["title"])
        if key in titles or audit["pdf_sha256"] in pdf_hashes:
            raise ValueError(
                "duplicate or existing paper requires explicit reconciliation"
            )
        titles.add(key)
        pdf_hashes.add(audit["pdf_sha256"])

    with tempfile.TemporaryDirectory(prefix="elvia-append-") as temporary:
        temporary = Path(temporary)
        generated = temporary / "newly-reviewed"
        count = IMPORTER["import_collection"](
            audits, raw_root, generated, expected_count=expected_count, issue_number=25
        )
        incoming = load_records(generated / "records")
        if set(latest) & {record["case_id"] for _, record in incoming}:
            raise ValueError("duplicate existing case identity")
        # Inputs can change after preflight. Bind the decisive identity check
        # to the validated records that will actually enter the collection.
        titles = {_title_key(record["source"]["title"]) for record in latest.values()}
        pdf_hashes = {record["audit"]["pdf_sha256"] for record in latest.values()}
        for _, record in incoming:
            key = _title_key(record["source"]["title"])
            pdf_hash = record["audit"]["pdf_sha256"]
            if key in titles or pdf_hash in pdf_hashes:
                raise ValueError(
                    "duplicate or existing paper requires explicit reconciliation"
                )
            titles.add(key)
            pdf_hashes.add(pdf_hash)
        incoming_files = REVISION["capture_collection"](generated / "records", incoming)
        for name, payload in incoming_files.items():
            if Path(name).name == "verification.json":
                REVISION["validate_assessment"](json.loads(payload))
        new_notes = json.loads(incoming_files.pop("case-notes.json"))
        if set(catalog["cases"]) & set(new_notes["cases"]):
            raise ValueError("duplicate existing case note")
        catalog["cases"].update(new_notes["cases"])
        staging = temporary / "combined"
        staging.mkdir()
        for files in (snapshot, incoming_files):
            for name, payload in files.items():
                if name == "case-notes.json":
                    continue
                destination = staging / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                with destination.open("xb") as stream:
                    stream.write(payload)
        combined = load_records(staging / "records")
        current = {record["case_id"]: record for _, record in combined}
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
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", required=True, type=Path)
    parser.add_argument("--audits", required=True, type=Path)
    parser.add_argument("--raw-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    count = append_collection(args.records, args.audits, args.raw_root, args.output)
    print(f"Appended {count} newly reviewed papers with existing snapshots unchanged")


if __name__ == "__main__":
    main()
