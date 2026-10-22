"""Reader metadata and explicit public-file boundaries, using synthetic PDFs."""

import copy
import hashlib
import json
import zipfile

import pytest

from elvia.reader import prepare_reader, write_reader_bundle


def digest(value):
    return hashlib.sha256(value).hexdigest()


def bound(record):
    return digest(json.dumps(record, sort_keys=True, separators=(",", ":")).encode())


@pytest.fixture
def reader_fixture(valid_record, tmp_path):
    record = copy.deepcopy(valid_record)
    article = b"%PDF-1.4\nOriginal synthetic article\n%%EOF\n"
    report = b"%PDF-1.4\nSynthetic report\n%%EOF\n"
    record["audit"] = {"pdf_sha256": digest(article)}
    root = tmp_path / "library"
    root.mkdir()
    (root / "article.pdf").write_bytes(article)
    (root / "report.pdf").write_bytes(report)
    source = tmp_path / "dataset/evidence" / record["case_id"] / "report.tex"
    source.parent.mkdir(parents=True)
    source.write_text("Original synthetic report source.", encoding="utf-8")
    record["evidence"].append(
        {
            "id": "editable-latex",
            "stance": "support",
            "description": "Report source",
            "method": "Original fixture",
            "artifact": {
                "path": source.relative_to(source.parents[2]).as_posix(),
                "sha256": digest(source.read_bytes()),
            },
        }
    )
    row = {
        "revision": 1,
        "record_sha256": bound(record),
        "article": {"path": "article.pdf", "sha256": digest(article)},
        "report": {"path": "report.pdf", "sha256": digest(report)},
        "report_source_sha256": digest(source.read_bytes()),
        "revisions": [],
    }
    return record, root, source.parents[2], row


def test_revision_report_must_follow_its_registered_source_not_version_one(
    reader_fixture, tmp_path
):
    record, root, dataset, row = reader_fixture
    new_source = dataset / "evidence" / record["case_id"] / "r2/report.tex"
    new_source.parent.mkdir()
    new_source.write_text("A revised scientific conclusion.", encoding="utf-8")
    record["revision"] = row["revision"] = 2
    record["evidence"][-1]["artifact"] = {
        "path": new_source.relative_to(dataset).as_posix(),
        "sha256": digest(new_source.read_bytes()),
    }
    row["record_sha256"] = bound(record)
    with pytest.raises(ValueError, match="source"):
        write_reader_bundle(record, row, root, dataset, tmp_path / "stale.zip")


def test_reader_zip_contains_only_named_pdfs_and_explicit_published_revisions(
    reader_fixture, tmp_path
):
    record, root, dataset, row = reader_fixture
    (root / "private.txt").write_text("Never discover private files")
    output = tmp_path / "reader.zip"
    write_reader_bundle(record, row, root, dataset, output)
    with zipfile.ZipFile(output) as bundle:
        assert bundle.namelist() == ["original article.pdf", "report.pdf"]
        assert (
            digest(bundle.read("original article.pdf")) == record["audit"]["pdf_sha256"]
        )
        assert bundle.testzip() is None


@pytest.mark.parametrize(
    "fault", ["snapshot", "source", "pdf", "traversal", "absolute"]
)
def test_reader_bundle_rejects_stale_or_outside_files_before_creating_output(
    reader_fixture, tmp_path, fault
):
    record, root, dataset, row = reader_fixture
    if fault == "snapshot":
        row["record_sha256"] = "0" * 64
    elif fault == "source":
        row["report_source_sha256"] = "0" * 64
    elif fault == "pdf":
        (root / "report.pdf").write_bytes(b"private attachment with changed bytes")
    elif fault == "traversal":
        row["article"]["path"] = "../private.pdf"
    else:
        row["article"]["path"] = str(root / "article.pdf")
    output = tmp_path / "reader.zip"
    with pytest.raises(ValueError):
        write_reader_bundle(record, row, root, dataset, output)
    assert not output.exists()


def test_only_published_revision_files_may_join_the_reader_bundle(
    reader_fixture, tmp_path
):
    record, root, dataset, row = reader_fixture
    record["revision"] = row["revision"] = 2
    row["record_sha256"] = bound(record)
    revision = b"%PDF-1.4\nApproved contributor revision\n%%EOF\n"
    (root / "revision.pdf").write_bytes(revision)
    row["revisions"] = [
        {
            "revision": 2,
            "published": False,
            "files": [{"path": "revision.pdf", "sha256": digest(revision)}],
        }
    ]
    with pytest.raises(ValueError, match="published"):
        write_reader_bundle(record, row, root, dataset, tmp_path / "blocked.zip")
    row["revisions"][0]["published"] = True
    output = tmp_path / "revision.zip"
    write_reader_bundle(record, row, root, dataset, output)
    with zipfile.ZipFile(output) as bundle:
        assert bundle.namelist() == [
            "original article.pdf",
            "report.pdf",
            "revision 2.pdf",
        ]
        assert bundle.read("revision 2.pdf") == revision


def test_citation_and_credit_catalog_cannot_silently_drift(reader_fixture):
    record, _, _, _ = reader_fixture
    note = {
        "revision": 1,
        "record_sha256": bound(record),
        "citation": {
            "authors": ["Example, Alex"],
            "title": "Synthetic article",
            "container": "Fixture",
            "volume": "1",
            "year": 2026,
            "first_page": "1",
            "last_page": "2",
            "doi": "10.1234/fixture",
            "source_url": "https://example.org/fixture",
        },
        "contributors": [
            {"name": "Example Person", "role": "Initial report", "revision": 1}
        ],
    }
    catalog = {"format_version": 1, "cases": {record["case_id"]: note}}
    assert prepare_reader([record], catalog)[record["case_id"]] == note
    note["record_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="snapshot"):
        prepare_reader([record], catalog)
