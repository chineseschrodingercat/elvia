"""Publication-boundary tests for the explicit reader-library merger."""

import errno
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "merge_reader_libraries.py"
SPEC = importlib.util.spec_from_file_location("merge_reader_libraries", SCRIPT)
merger = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(merger)


def sha(content):
    return hashlib.sha256(content).hexdigest()


def library(tmp_path, name, case_id, content=b"article"):
    root = tmp_path / name
    root.mkdir()
    article = f"articles/{case_id}.pdf"
    report = f"reports/{case_id}.pdf"
    revision = f"revisions/{case_id}/report.pdf"
    evidence = "evidence/sha256/" + sha(b"shared evidence")
    blobs = {
        article: content,
        report: b"report",
        revision: b"old report",
        evidence: b"shared evidence",
    }
    for relative, blob in blobs.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
    (root / "unreferenced-secret.txt").write_bytes(b"must not publish")
    case = {
        "revision": "r1",
        "record_sha256": sha(b"record"),
        "article": {"path": article, "sha256": sha(content)},
        "report": {"path": report, "sha256": sha(b"report")},
        "report_source_sha256": sha(b"source"),
        "compiled_source_sha256": sha(b"compiled"),
        "revisions": [{"files": [{"path": revision, "sha256": sha(b"old report")}]}],
        "evidence": [
            {
                "path": evidence,
                "sha256": sha(b"shared evidence"),
                "source_sha256": sha(b"different private source"),
                "archive_name": "evidence.txt",
                "references": ["finding:1"],
                "published": True,
                "transformation": {
                    "kind": "redaction",
                    "description": "Public transformed evidence",
                },
            }
        ],
        "references": ["finding:1"],
        "aliases": [],
        "unavailable": [],
    }
    manifest = {"format_version": 1, "cases": {case_id: case}}
    (root / merger.MANIFEST).write_text(json.dumps(manifest), encoding="utf-8")
    return root, manifest


def write_manifest(root, manifest):
    (root / merger.MANIFEST).write_text(json.dumps(manifest), encoding="utf-8")


def test_union_preserves_records_and_publishes_only_referenced_files(tmp_path):
    first, one = library(tmp_path, "one", "case-1")
    second, two = library(tmp_path, "two", "case-2")
    original = (first / merger.MANIFEST).read_bytes()
    result = merger.merge_libraries([first, second], tmp_path / "merged")
    output = tmp_path / "merged"
    assert json.loads((output / merger.MANIFEST).read_text()) == {
        "format_version": 1,
        "cases": one["cases"] | two["cases"],
    }
    assert result["cases"] == 2
    assert result["files"] == 7  # Shared content-addressed evidence is published once.
    assert result["linked"] == 7
    assert result["copied"] == 0
    assert not (output / "unreferenced-secret.txt").exists()
    assert (first / merger.MANIFEST).read_bytes() == original
    for relative in ("articles/case-1.pdf", "revisions/case-2/report.pdf"):
        assert (output / relative).is_file()
    assert (output / "articles/case-1.pdf").samefile(first / "articles/case-1.pdf")


def test_cross_volume_link_failure_falls_back_to_verified_copy(tmp_path, monkeypatch):
    source, _ = library(tmp_path, "source", "case")

    def cross_volume(*args, **kwargs):
        raise OSError(errno.EXDEV, "Cross-device link")

    monkeypatch.setattr(merger.os, "link", cross_volume)
    result = merger.merge_libraries([source], tmp_path / "merged")
    assert result["copied"] == 4
    assert result["linked"] == 0
    assert not (tmp_path / "merged/articles/case.pdf").samefile(
        source / "articles/case.pdf"
    )


def test_duplicate_case_rejected_before_any_output(tmp_path):
    first, _ = library(tmp_path, "one", "case")
    second, _ = library(tmp_path, "two", "CASE")
    with pytest.raises(merger.MergeError, match="disjoint"):
        merger.merge_libraries([first, second], tmp_path / "merged")
    assert not (tmp_path / "merged").exists()


def test_corrupt_source_is_rejected_without_publishing(tmp_path):
    source, _ = library(tmp_path, "source", "case")
    (source / "reports/case.pdf").write_bytes(b"modified")
    with pytest.raises(merger.MergeError, match="SHA-256 mismatch"):
        merger.merge_libraries([source], tmp_path / "merged")
    assert not (tmp_path / "merged").exists()


@pytest.mark.parametrize(
    "bad_path",
    [
        "../outside.pdf",
        "/outside.pdf",
        "C:/outside.pdf",
        "a\\b.pdf",
        "a/../b.pdf",
        "CON.pdf",
        "a//b.pdf",
        "a./b.pdf",
    ],
)
def test_nonportable_or_traversing_reference_is_rejected(tmp_path, bad_path):
    source, manifest = library(tmp_path, "source", "case")
    manifest["cases"]["case"]["article"]["path"] = bad_path
    write_manifest(source, manifest)
    with pytest.raises(merger.MergeError):
        merger.merge_libraries([source], tmp_path / "merged")
    assert not (tmp_path / "merged").exists()


def test_symlink_cannot_publish_external_file(tmp_path):
    source, _ = library(tmp_path, "source", "case")
    outside = tmp_path / "outside.pdf"
    outside.write_bytes(b"article")
    article = source / "articles/case.pdf"
    article.unlink()
    try:
        article.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"Symlink creation not available: {exc}")
    with pytest.raises(merger.MergeError, match="Symlink"):
        merger.merge_libraries([source], tmp_path / "merged")


def test_existing_output_is_never_overwritten(tmp_path):
    source, _ = library(tmp_path, "source", "case")
    output = tmp_path / "merged"
    output.mkdir()
    (output / "keep").write_bytes(b"original")
    with pytest.raises(merger.MergeError, match="already exist"):
        merger.merge_libraries([source], output)
    assert (output / "keep").read_bytes() == b"original"


def test_output_cannot_mutate_a_source_library(tmp_path):
    source, _ = library(tmp_path, "source", "case")
    with pytest.raises(merger.MergeError, match="outside every source"):
        merger.merge_libraries([source], source / "merged")
    assert not (source / "merged").exists()


def test_shared_path_with_different_hash_is_rejected(tmp_path):
    first, _ = library(tmp_path, "one", "case-1")
    second, manifest = library(tmp_path, "two", "case-2")
    evidence = manifest["cases"]["case-2"]["evidence"][0]
    (second / evidence["path"]).write_bytes(b"different")
    evidence["sha256"] = sha(b"different")
    write_manifest(second, manifest)
    with pytest.raises(merger.MergeError, match="Conflicting bytes"):
        merger.merge_libraries([first, second], tmp_path / "merged")


def test_failed_copy_cleans_only_its_new_output(tmp_path, monkeypatch):
    source, _ = library(tmp_path, "source", "case")

    def failed_copy(*args, **kwargs):
        raise OSError("Disk full")

    monkeypatch.setattr(merger.shutil, "copyfileobj", failed_copy)
    with pytest.raises(OSError, match="Disk full"):
        merger.merge_libraries([source], tmp_path / "merged", copy_only=True)
    assert not (tmp_path / "merged").exists()
    assert (source / "articles/case.pdf").read_bytes() == b"article"
