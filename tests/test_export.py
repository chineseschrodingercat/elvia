"""Portable, lossless exports retain declarations and immutable history."""

import copy
import hashlib
import importlib
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

from elvia.storage import load_records, save_record


def export(input_path, output):
    assert importlib.util.find_spec("elvia.export") is not None, (
        "export not implemented"
    )
    return importlib.import_module("elvia.export").export_records(input_path, output)


def test_export_retains_full_records_artifacts_and_history(
    tmp_path, valid_record, human_review
):
    first = save_record(valid_record, tmp_path / "records")
    later = copy.deepcopy(valid_record)
    later.update(revision=2, previous_revision=1)
    later["human_reviews"] = [human_review]
    later["adjudication"] = {
        "status": "unresolved",
        "rationale": "Synthetic unresolved review.",
        "history": [
            {
                "at": "2026-10-19T00:00:00Z",
                "status": "pending",
                "rationale": "Original state retained.",
            }
        ],
    }
    later["repair"].update(
        content="Synthetic candidate",
        verification_status="pending",
        changed_assumptions=["Restrict domain"],
        changed_conclusion="Weaker claim",
        adoption_status="unknown",
    )
    raw = tmp_path / "raw.txt"
    raw.write_bytes(b"Original raw output\n")
    later["runs"] = [
        {
            "id": "local-run",
            "tool": "Synthetic test tool",
            "tool_version": "1",
            "model": None,
            "model_note": "No model execution in test fixture.",
            "config_version": "test-v1",
            "started_at": "2026-10-19T00:00:00Z",
            "ended_at": "2026-10-19T00:00:01Z",
            "cost_usd": 0,
            "output_artifacts": [
                {
                    "path": "raw.txt",
                    "sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
                }
            ],
        }
    ]
    second = save_record(later, first.parent)
    output = tmp_path / "portable"
    assert export(first.parent, output) == 2
    assert (output / "records" / first.name).read_bytes() == first.read_bytes()
    assert (output / "records" / second.name).read_bytes() == second.read_bytes()
    jsonl = [
        json.loads(line)
        for line in (output / "records.jsonl").read_text("utf-8").splitlines()
    ]
    assert jsonl == [valid_record, later]
    markdown = (output / "markdown" / f"{second.stem}.md").read_text("utf-8")
    for key in later:
        assert key in markdown
    for value in [
        "Synthetic unresolved review.",
        "Original state retained.",
        "Weaker claim",
        "No model execution in test fixture.",
        "synthetic-reviewer-a",
        "computation",
        "human adjudication",
    ]:
        assert value in markdown
    manifest = json.loads((output / "manifest.json").read_text("utf-8"))
    expected_files = {
        "source.txt",
        "evidence.txt",
        "raw.txt",
        "records.jsonl",
        f"records/{first.name}",
        f"records/{second.name}",
        f"markdown/{first.stem}.md",
        f"markdown/{second.stem}.md",
    }
    assert {item["path"] for item in manifest["files"]} == expected_files
    for item in manifest["files"]:
        assert (
            hashlib.sha256((output / item["path"]).read_bytes()).hexdigest()
            == (item["sha256"])
        )
    shutil.rmtree(first.parent)
    for name in ["source.txt", "evidence.txt", "raw.txt"]:
        (tmp_path / name).unlink()
    assert [r for _, r in load_records(output / "records")] == [valid_record, later]


def test_single_revision_export_includes_only_its_predecessor_case(
    tmp_path, valid_record
):
    first = save_record(valid_record, tmp_path / "records")
    later = copy.deepcopy(valid_record)
    later.update(revision=2, previous_revision=1)
    second = save_record(later, first.parent)
    unrelated = copy.deepcopy(valid_record)
    unrelated["case_id"] = "unrelated"
    save_record(unrelated, first.parent)
    output = tmp_path / "export"
    # Count means snapshots actually exported, including required predecessors.
    assert export(second, output) == 2
    assert [r["case_id"] for _, r in load_records(output / "records")] == [
        "synthetic-001",
        "synthetic-001",
    ]
    assert [r["revision"] for _, r in load_records(output / "records")] == [1, 2]


@pytest.mark.parametrize("input_path", [".", "synthetic-001.r2.json"])
def test_export_relative_to_records_directory_preserves_portable_history(
    tmp_path, valid_record, monkeypatch, input_path
):
    first = save_record(valid_record, tmp_path / "records")
    later = copy.deepcopy(valid_record)
    later.update(revision=2, previous_revision=1)
    second = save_record(later, first.parent)
    monkeypatch.chdir(first.parent)
    assert export(Path(input_path), Path("../export")) == 2
    output = tmp_path / "export"
    assert [record for _, record in load_records(output / "records")] == [
        valid_record,
        later,
    ]
    for target in (first, second):
        assert (output / "records" / target.name).read_bytes() == target.read_bytes()
    for name in ("source.txt", "evidence.txt"):
        assert (output / name).read_bytes() == (tmp_path / name).read_bytes()


@pytest.mark.parametrize(
    "artifact_path",
    [
        "manifest.json",
        "records.jsonl",
        "records",
        "markdown",
        "markdown/synthetic-001.r1.md",
        "markdown/synthetic-001.r1.md/child.txt",
        "records/extra.json",
    ],
)
def test_export_rejects_generated_path_collisions(
    tmp_path, valid_record, artifact_path
):
    collision = tmp_path / artifact_path
    collision.parent.mkdir(parents=True, exist_ok=True)
    collision.write_bytes(b"original artifact")
    valid_record["evidence"][0]["artifact"] = {
        "path": artifact_path,
        "sha256": hashlib.sha256(collision.read_bytes()).hexdigest(),
    }
    # A file named records prevents a records directory, so use another canonical
    # directory name; the dataset-relative artifact still collides at export.
    records = tmp_path / "snapshots"
    path = save_record(valid_record, records)
    output = tmp_path / "export"
    with pytest.raises(ValueError, match="collision"):
        export(path, output)
    assert not output.exists()
    assert collision.read_bytes() == b"original artifact"


def test_export_never_replaces_existing_output(tmp_path, valid_record):
    path = save_record(valid_record, tmp_path / "records")
    output = tmp_path / "existing"
    output.mkdir()
    keep = output / "keep.txt"
    keep.write_bytes(b"keep")
    with pytest.raises(FileExistsError):
        export(path, output)
    assert list(output.iterdir()) == [keep]
    assert keep.read_bytes() == b"keep"


@pytest.mark.parametrize("bad", ["empty", "malformed", "hash"])
def test_export_invalid_input_creates_nothing(tmp_path, valid_record, bad):
    records = tmp_path / "records"
    records.mkdir()
    if bad == "malformed":
        (records / "bad.r1.json").write_bytes(b"{")
    elif bad == "hash":
        save_record(valid_record, records)
        (tmp_path / "evidence.txt").write_bytes(b"changed")
    with pytest.raises(ValueError):
        export(records, tmp_path / "export")
    assert not (tmp_path / "export").exists()
