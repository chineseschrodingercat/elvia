"""Synthetic collection isolation and snapshot-bound research-field checks."""

import copy
import hashlib
import json
import zipfile

import pytest

from elvia.reader import record_digest
from elvia.site import build_site
from elvia.storage import save_record


def collection(tmp_path, name, original):
    root = tmp_path / name
    root.mkdir()
    record = copy.deepcopy(original)
    record.update(
        case_id=f"fixture-{name}",
        schema_version="1.1.0",
        case_type="prospective_audit",
    )
    record["publication"] = {
        "status": "preliminary_ai",
        "note": "Synthetic multi-collection software fixture only.",
    }
    record["audit"] = {
        "venue": f"Fixture {name}",
        "year": 2026,
        "authors": ["Fictional fixture"],
        "landing_url": "https://example.org/fixture",
        "pdf_url": "https://example.org/fixture.pdf",
        "pdf_sha256": "a" * 64,
        "retrieved_at": "2026-10-19T00:00:00Z",
        "outcome": "candidate_issue",
        "summary": "Synthetic software fixture only.",
        "limitations": ["No scientific conclusion; software test only."],
    }
    for artifact in [record["source"]["artifact"], record["evidence"][0]["artifact"]]:
        content = f"Synthetic {name} {artifact['path']}\n".encode()
        (root / artifact["path"]).write_bytes(content)
        artifact["sha256"] = hashlib.sha256(content).hexdigest()
    return root, record


def fields(root, record, field):
    catalog = {
        "format_version": 1,
        "cases": {
            record["case_id"]: {
                "revision": record["revision"],
                "record_sha256": record_digest(record),
                "field": field,
            }
        },
    }
    (root / "research-fields.json").write_text(json.dumps(catalog), "utf-8")
    return catalog


def notation(root, record, typeset):
    catalog = {
        "format_version": 1,
        "cases": {
            record["case_id"]: {
                "revision": record["revision"],
                "record_sha256": record_digest(record),
                "replacements": [
                    {"source": record["source"]["title"], "typeset": typeset}
                ],
            }
        },
    }
    (root / "math-notation.json").write_text(json.dumps(catalog), "utf-8")
    return catalog


def test_multi_collection_math_notation_uses_each_dataset_catalog(
    valid_record, tmp_path
):
    first, a = collection(tmp_path, "a", valid_record)
    second, b = collection(tmp_path, "b", valid_record)
    save_record(a, first / "records")
    save_record(b, second / "records")
    first_catalog = notation(first, a, r"Synthetic \(a\)")
    second_catalog = notation(second, b, r"Synthetic \(b\)")
    first_catalog["cases"][b["case_id"]] = {
        **second_catalog["cases"][b["case_id"]],
        "record_sha256": "0" * 64,
    }
    (first / "math-notation.json").write_text(json.dumps(first_catalog), "utf-8")
    output = tmp_path / "site"
    build_site([first / "records", second / "records"], output)
    payload = json.loads((output / "data.json").read_text("utf-8"))
    assert payload["presentation"][a["case_id"]] == first_catalog["cases"][a["case_id"]]
    assert (
        payload["presentation"][b["case_id"]] == second_catalog["cases"][b["case_id"]]
    )


@pytest.mark.parametrize("fault", ["snapshot", "source"])
def test_dataset_math_notation_rejects_drift_before_output(
    valid_record, tmp_path, fault
):
    root, record = collection(tmp_path, "a", valid_record)
    save_record(record, root / "records")
    catalog = notation(root, record, r"Synthetic \(a\)")
    row = catalog["cases"][record["case_id"]]
    if fault == "snapshot":
        row["record_sha256"] = "0" * 64
    else:
        row["replacements"][0]["source"] = "A different unrecorded source."
    (root / "math-notation.json").write_text(json.dumps(catalog), "utf-8")
    output = tmp_path / "site"
    with pytest.raises(ValueError, match="math presentation"):
        build_site(root / "records", output)
    assert not output.exists()


def test_multi_collection_keeps_dataset_artifacts_history_and_fields(
    valid_record, tmp_path
):
    first, a = collection(tmp_path, "a", valid_record)
    second, b = collection(tmp_path, "b", valid_record)
    save_record(a, first / "records")
    fields(first, a, "Mathematics")
    save_record(b, second / "records")
    b.update(revision=2, previous_revision=1)
    b["audit"]["summary"] = "Revised synthetic scope only."
    save_record(b, second / "records")
    fields(second, b, "Computer science")
    output = tmp_path / "site"

    assert build_site([first / "records", second / "records"], output) == 2
    payload = json.loads((output / "data.json").read_text("utf-8"))
    assert payload["research_fields"] == {
        a["case_id"]: "Mathematics",
        b["case_id"]: "Computer science",
    }
    assert payload["counts"]["candidate_issue"] == 2
    for root, record in [(first, a), (second, b)]:
        evidence = output / "evidence" / record["case_id"]
        assert (evidence / "source.txt").read_bytes() == (
            root / "source.txt"
        ).read_bytes()
        assert (output / "cases" / f"{record['case_id']}.html").is_file()
        context = json.loads(
            (output / "cases" / f"{record['case_id']}.context.json").read_text("utf-8")
        )
        assert context["research_fields"] == {
            record["case_id"]: payload["research_fields"][record["case_id"]]
        }
        for revision in range(1, record["revision"] + 1):
            name = f"{record['case_id']}.r{revision}.json"
            assert (evidence / "records" / name).read_bytes() == (
                root / "records" / name
            ).read_bytes()


def test_duplicate_case_across_collections_fails_before_output(valid_record, tmp_path):
    first, a = collection(tmp_path, "a", valid_record)
    second, b = collection(tmp_path, "b", valid_record)
    b["case_id"] = a["case_id"]
    save_record(a, first / "records")
    save_record(b, second / "records")
    output = tmp_path / "site"
    with pytest.raises(ValueError, match="duplicate case"):
        build_site([first / "records", second / "records"], output)
    assert not output.exists()


@pytest.mark.parametrize("fault", ["snapshot", "field"])
def test_invalid_research_field_metadata_fails_before_output(
    valid_record, tmp_path, fault
):
    root, record = collection(tmp_path, "a", valid_record)
    save_record(record, root / "records")
    catalog = fields(root, record, "Mathematics")
    row = catalog["cases"][record["case_id"]]
    row["record_sha256" if fault == "snapshot" else "field"] = "invalid"
    (root / "research-fields.json").write_text(json.dumps(catalog), "utf-8")
    output = tmp_path / "site"
    with pytest.raises(ValueError, match="research field"):
        build_site(root / "records", output)
    assert not output.exists()


def test_missing_research_field_is_others(valid_record, tmp_path):
    root, record = collection(tmp_path, "a", valid_record)
    save_record(record, root / "records")
    output = tmp_path / "site"
    build_site(root / "records", output)
    payload = json.loads((output / "data.json").read_text("utf-8"))
    assert payload["research_fields"] == {record["case_id"]: "Others"}


def test_research_field_cannot_carry_to_a_later_revision(valid_record, tmp_path):
    root, record = collection(tmp_path, "a", valid_record)
    save_record(record, root / "records")
    fields(root, record, "Mathematics")
    record.update(revision=2, previous_revision=1)
    record["audit"]["summary"] = "Synthetic revised scope."
    save_record(record, root / "records")
    output = tmp_path / "site"
    build_site(root / "records", output)
    payload = json.loads((output / "data.json").read_text("utf-8"))
    assert payload["research_fields"] == {record["case_id"]: "Others"}


def test_other_collection_field_catalog_cannot_override_its_owner(
    valid_record, tmp_path
):
    first, a = collection(tmp_path, "a", valid_record)
    second, b = collection(tmp_path, "b", valid_record)
    save_record(a, first / "records")
    save_record(b, second / "records")
    first_catalog = fields(first, a, "Mathematics")
    second_catalog = fields(second, b, "Computer science")
    foreign_row = copy.deepcopy(second_catalog["cases"][b["case_id"]])
    foreign_row["field"] = "Chemistry"
    first_catalog["cases"][b["case_id"]] = foreign_row
    (first / "research-fields.json").write_text(json.dumps(first_catalog), "utf-8")
    output = tmp_path / "site"
    build_site([first / "records", second / "records"], output)
    payload = json.loads((output / "data.json").read_text("utf-8"))
    assert payload["research_fields"][b["case_id"]] == "Computer science"


def test_multi_collection_reader_uses_each_registered_report_source(
    valid_record, tmp_path
):
    library = tmp_path / "library"
    library.mkdir()
    rows = {}
    roots = []
    for name in ["a", "b"]:
        root, record = collection(tmp_path, name, valid_record)
        source = root / "evidence" / "report.tex"
        source.parent.mkdir()
        source.write_text(f"Synthetic report {name}.", "utf-8")
        record["evidence"].append(
            {
                "id": "editable-latex",
                "stance": "support",
                "description": "Synthetic report source.",
                "method": "Original software fixture.",
                "artifact": {
                    "path": "evidence/report.tex",
                    "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                },
            }
        )
        selected = {}
        for role in ["article", "report"]:
            content = f"%PDF-1.4\nSynthetic {name} {role}\n%%EOF\n".encode()
            filename = f"{name}-{role}.pdf"
            (library / filename).write_bytes(content)
            selected[role] = {
                "path": filename,
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        record["audit"]["pdf_sha256"] = selected["article"]["sha256"]
        save_record(record, root / "records")
        rows[record["case_id"]] = {
            "revision": 1,
            "record_sha256": record_digest(record),
            **selected,
            "report_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "revisions": [],
        }
        roots.append(root / "records")
    (library / "reader-files.json").write_text(
        json.dumps({"format_version": 1, "cases": rows}), "utf-8"
    )
    output = tmp_path / "site"
    assert build_site(roots, output, reader_library=library) == 2
    for case, row in rows.items():
        with zipfile.ZipFile(output / "evidence" / f"{case}.zip") as bundle:
            assert bundle.namelist() == ["original article.pdf", "report.pdf"]
            assert (
                bundle.read("report.pdf")
                == (library / row["report"]["path"]).read_bytes()
            )
