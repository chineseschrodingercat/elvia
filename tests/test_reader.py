"""Reader metadata and explicit public-file boundaries, using synthetic PDFs."""

import copy
import hashlib
import importlib.util
import json
import re
import zipfile
from pathlib import Path

import pytest

from elvia.reader import prepare_reader, write_reader_bundle


def digest(value):
    return hashlib.sha256(value).hexdigest()


def bound(record):
    return digest(json.dumps(record, sort_keys=True, separators=(",", ":")).encode())


@pytest.fixture
def reader_evidence():
    source = Path(__file__).parents[1] / "website/reader_evidence.py"
    spec = importlib.util.spec_from_file_location("reader_evidence", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def evidence_file(root, name, content, *, reference=None, version=None):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    row = {
        "path": name,
        "archive_name": name,
        "sha256": digest(content),
        "source_sha256": digest(content),
        "references": [reference or name],
        "published": True,
        "transformation": {
            "kind": "verbatim",
            "description": "Exact scientific fixture.",
        },
    }
    if version:
        row["source_version"] = version
    return row


def test_reader_bundle_includes_referenced_scientific_files_and_pdf_aliases(
    reader_fixture, tmp_path
):
    record, root, dataset, row = reader_fixture
    script = b"raise RuntimeError('This evidence must never be executed')\n"
    result = b'{"exact_result": "20/21", "scope": "finite witness only"}\n'
    row["evidence"] = [
        evidence_file(root, "verification/0268/check.py", script),
        evidence_file(root, "verification/0268/check.json", result),
    ]
    row["references"] = [
        "papers/0268/0268.pdf",
        "verification/0268/check.py",
        "verification/0268/check.json",
    ]
    row["aliases"] = [
        {"reference": "papers/0268/0268.pdf", "archive_name": "original article.pdf"}
    ]
    output = tmp_path / "reader.zip"
    write_reader_bundle(record, row, root, dataset, output)
    with zipfile.ZipFile(output) as bundle:
        assert bundle.read("verification/0268/check.py") == script
        assert bundle.read("verification/0268/check.json") == result
        manifest = json.loads(bundle.read("evidence-manifest.json"))
        assert manifest["references"] == row["references"]
        assert manifest["aliases"] == row["aliases"]
        files = {item["archive_name"]: item for item in manifest["files"]}
        assert files["verification/0268/check.py"]["sha256"] == digest(script)
        assert files["verification/0268/check.json"]["source_sha256"] == digest(result)
        assert bundle.testzip() is None


@pytest.mark.parametrize(
    "fault",
    [
        "hash",
        "unpublished",
        "traversal",
        "duplicate",
        "missing_reference",
        "source_hash",
    ],
)
def test_reader_bundle_rejects_incomplete_or_unsafe_evidence_before_output(
    reader_fixture, tmp_path, fault
):
    record, root, dataset, row = reader_fixture
    item = evidence_file(root, "verification/check.json", b'{"result": 1}\n')
    row["evidence"] = [item]
    row["references"] = list(item["references"])
    if fault == "hash":
        item["sha256"] = "0" * 64
    elif fault == "unpublished":
        item["published"] = False
    elif fault == "traversal":
        item["archive_name"] = "../private.json"
    elif fault == "duplicate":
        item["archive_name"] = "Report.pdf"
    elif fault == "missing_reference":
        row["references"].append("verification/missing.json")
    else:
        item["source_sha256"] = "0" * 64
    output = tmp_path / "bad.zip"
    with pytest.raises(ValueError):
        write_reader_bundle(record, row, root, dataset, output)
    assert not output.exists()


def test_reader_bundle_keeps_two_explicitly_inspected_source_versions(
    reader_fixture, tmp_path
):
    record, root, dataset, row = reader_fixture
    row["references"] = ["trainer/core.py"]
    row["evidence"] = [
        evidence_file(
            root,
            "sources/pinned/core.py",
            b"printed_formula = 'historical version'\n",
            reference="trainer/core.py",
            version="pinned source commit A (synthetic)",
        ),
        evidence_file(
            root,
            "sources/current/core.py",
            b"printed_formula = 'current inspected version'\n",
            reference="trainer/core.py",
            version="current source commit B (synthetic)",
        ),
    ]
    output = tmp_path / "versions.zip"
    write_reader_bundle(record, row, root, dataset, output)
    with zipfile.ZipFile(output) as bundle:
        assert bundle.read("sources/pinned/core.py") != bundle.read(
            "sources/current/core.py"
        )
        manifest = json.loads(bundle.read("evidence-manifest.json"))
        versions = {
            f["source_version"] for f in manifest["files"] if "source_version" in f
        }
        assert len(versions) == 2


def test_evidence_preparation_reuses_pdfs_and_rehashes_explicit_sources(
    reader_fixture, tmp_path, monkeypatch, reader_evidence
):
    record, library, dataset, row = reader_fixture
    (library / "reader-files.json").write_text(
        json.dumps({"format_version": 1, "cases": {record["case_id"]: row}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        reader_evidence, "_latest", lambda _: {record["case_id"]: (record, dataset)}
    )
    source = tmp_path / "retained/check.py"
    source.parent.mkdir()
    source.write_text(
        "raise RuntimeError('Never execute retained evidence')\n", encoding="utf-8"
    )
    selected = {
        "source_path": str(source),
        "source_sha256": digest(source.read_bytes()),
        "archive_name": "verification/check.py",
        "references": ["verification/check.py"],
        "published": True,
        "transformation": {
            "kind": "verbatim",
            "description": "Exact scientific fixture.",
        },
    }
    index = tmp_path / "selected.json"
    index.write_text(
        json.dumps(
            {
                "format_version": 1,
                "cases": {
                    record["case_id"]: {
                        "references": selected["references"],
                        "evidence": [selected],
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    output, receipt = tmp_path / "public", tmp_path / "private-source-receipt.json"
    summary = reader_evidence.prepare_evidence_library(
        [], library, index, output, receipt=receipt
    )
    assert summary["pdfs_reused"] == 2
    assert summary["scientific_files"] == 1
    public = json.loads((output / "reader-files.json").read_text())["cases"][
        record["case_id"]
    ]
    assert "source_path" not in public["evidence"][0]
    assert (output / public["evidence"][0]["path"]).read_bytes() == source.read_bytes()
    assert json.loads(receipt.read_text())["sources"][0]["source_path"] == str(source)
    assert (output / row["article"]["path"]).read_bytes() == (
        library / row["article"]["path"]
    ).read_bytes()
    selected["source_sha256"] = "0" * 64
    index.write_text(
        json.dumps(
            {
                "format_version": 1,
                "cases": {
                    record["case_id"]: {
                        "references": selected["references"],
                        "evidence": [selected],
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    blocked = tmp_path / "blocked"
    with pytest.raises(ValueError, match="source hash"):
        reader_evidence.prepare_evidence_library([], library, index, blocked)
    assert not blocked.exists()


def test_scientific_public_copy_is_explicit_and_blocks_credential_leaks(
    tmp_path, reader_evidence
):
    source, public = tmp_path / "raw.json", tmp_path / "public.json"
    source.write_text(
        '{"result":"20/21", "output_root":"C:/Users/liumi/private"}', encoding="utf-8"
    )
    public.write_text('{"result":"20/21"}', encoding="utf-8")
    item = {
        "source_path": str(source),
        "public_source_path": str(public),
        "source_sha256": digest(source.read_bytes()),
        "archive_name": "verification/notes.json",
        "references": ["notes.json"],
        "published": True,
        "transformation": {
            "kind": "sanitized-scientific-copy",
            "description": "Removed output_root; retained the scientific result.",
        },
    }
    selected, content = reader_evidence._prepared_file(item)
    assert selected["source_sha256"] != selected["sha256"]
    assert json.loads(content) == {"result": "20/21"}
    public.write_bytes(b'{"token":"sk-proj-' + b"A" * 40 + b'"}')
    with pytest.raises(ValueError, match="credential"):
        reader_evidence._prepared_file(item)


def test_selected_scientific_archive_is_read_as_data_and_checks_each_member(
    tmp_path, reader_evidence
):
    archive = tmp_path / "retained.zip"
    script = b"raise RuntimeError('This retained source must never execute')\n"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("science/check.py", script)
        bundle.writestr("science/results.json", '{"result":"20/21"}')
    item = {
        "source_archive": str(archive),
        "source_member": "science/check.py",
        "source_sha256": digest(script),
        "archive_name": "sources/check.py",
        "references": [],
        "published": True,
        "transformation": {"kind": "verbatim", "description": "Exact source."},
    }
    selected, content = reader_evidence._prepared_file(item)
    assert content == script
    assert selected["source_sha256"] == digest(script)
    reader_evidence._check_public_content(archive.read_bytes(), "science.zip")
    with zipfile.ZipFile(archive, "a") as bundle:
        bundle.writestr("science/.env", "synthetic private account fixture")
    with pytest.raises(ValueError, match="private files"):
        reader_evidence._check_public_content(archive.read_bytes(), "science.zip")


def test_notebook_evidence_rejects_private_host_paths_before_publication(
    tmp_path, monkeypatch, reader_evidence
):
    monkeypatch.setattr(
        reader_evidence,
        "_PRIVATE_HOST",
        re.compile(r"C:[/\\]+Users[/\\]+synthetic-reader\b", re.I),
    )
    source = tmp_path / "check.ipynb"
    source.write_text(
        json.dumps(
            {
                "cells": [{"source": ["exact_ratio = '20/21'\n"]}],
                "metadata": {
                    "output_root": "C:/Users/synthetic-reader/private-fixture"
                },
            }
        ),
        encoding="utf-8",
    )
    item = {
        "source_path": str(source),
        "source_sha256": digest(source.read_bytes()),
        "archive_name": "verification/check.ipynb",
        "references": ["check.ipynb"],
        "published": True,
        "transformation": {"kind": "verbatim", "description": "Exact notebook."},
    }
    with pytest.raises(ValueError, match="private host"):
        reader_evidence._prepared_file(item)


def test_evidence_preparation_aliases_actual_published_revision_members(
    reader_fixture, tmp_path, monkeypatch, reader_evidence
):
    record, library, dataset, row = reader_fixture
    record["revision"] = row["revision"] = 2
    row["record_sha256"] = bound(record)
    revision = b"%PDF-1.4\nApproved synthetic revision\n%%EOF\n"
    result = b'{"exact_result":"20/21"}\n'
    (library / "revision.pdf").write_bytes(revision)
    (library / "revision-result.json").write_bytes(result)
    row["revisions"] = [
        {
            "revision": 2,
            "published": True,
            "files": [
                {"path": "revision.pdf", "sha256": digest(revision)},
                {"path": "revision-result.json", "sha256": digest(result)},
            ],
        }
    ]
    (library / "reader-files.json").write_text(
        json.dumps({"format_version": 1, "cases": {record["case_id"]: row}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        reader_evidence, "_latest", lambda _: {record["case_id"]: (record, dataset)}
    )
    index = tmp_path / "selected.json"
    selection = {
        "references": ["revised derivation", "revised result"],
        "evidence": [],
        "aliases": [
            {"reference": "revised derivation", "archive_name": "revision 2.pdf"},
            {
                "reference": "revised result",
                "archive_name": "revision 2 attachment 1.json",
            },
        ],
    }
    index.write_text(
        json.dumps({"format_version": 1, "cases": {record["case_id"]: selection}}),
        encoding="utf-8",
    )
    output = tmp_path / "public"
    reader_evidence.prepare_evidence_library([], library, index, output)
    prepared = json.loads((output / "reader-files.json").read_text())["cases"][
        record["case_id"]
    ]
    archive = tmp_path / "revised.zip"
    write_reader_bundle(record, prepared, output, dataset, archive)
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.read("revision 2.pdf") == revision
        assert bundle.read("revision 2 attachment 1.json") == result
        manifest = json.loads(bundle.read("evidence-manifest.json"))
        assert manifest["aliases"] == selection["aliases"]
        files = {item["archive_name"]: item["sha256"] for item in manifest["files"]}
        assert files["revision 2.pdf"] == digest(revision)
        assert files["revision 2 attachment 1.json"] == digest(result)
