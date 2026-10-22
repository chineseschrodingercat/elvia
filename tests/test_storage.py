import copy
import json
import os
import subprocess
from pathlib import Path

import pytest

from elvia import storage as storage_api


def storage():
    return storage_api


def directory_link(link, target):
    """Exercise real junctions on Windows, real directory symlinks elsewhere."""
    if os.name == "nt":
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            capture_output=True,
            text=True,
        )
        if result.returncode:
            pytest.skip(f"Host cannot create junction: {result.stderr}")
    else:
        link.symlink_to(target, target_is_directory=True)


def test_save_and_load_roundtrip(valid_record, tmp_path):
    api = storage()
    target = api.save_record(valid_record, tmp_path / "records")
    assert target.name == "synthetic-001.r1.json"
    assert api.load_records(target) == [(target, valid_record)]
    assert api.load_records(target.parent) == [(target, valid_record)]


@pytest.mark.parametrize("input_path", [".", "synthetic-001.r1.json"])
def test_load_relative_to_records_directory(
    valid_record, tmp_path, monkeypatch, input_path
):
    target = storage_api.save_record(valid_record, tmp_path / "records")
    monkeypatch.chdir(target.parent)
    assert storage_api.load_records(Path(input_path)) == [(target, valid_record)]


def test_save_relative_to_records_directory_retains_history(
    valid_record, tmp_path, monkeypatch
):
    records = tmp_path / "records"
    records.mkdir()
    monkeypatch.chdir(records)
    first = storage_api.save_record(valid_record, Path("."))
    before = first.read_bytes()
    later = copy.deepcopy(valid_record)
    later.update(revision=2, previous_revision=1)
    second = storage_api.save_record(later, Path("."))
    assert first.read_bytes() == before
    assert storage_api.load_records(Path(".")) == [
        (records / "synthetic-001.r1.json", valid_record),
        (records / "synthetic-001.r2.json", later),
    ]
    assert second == records / "synthetic-001.r2.json"


def test_duplicate_is_not_overwritten(valid_record, tmp_path):
    api = storage()
    records = tmp_path / "records"
    first = api.save_record(valid_record, records)
    before = first.read_bytes()
    with pytest.raises((ValueError, FileExistsError)):
        api.save_record(valid_record, records)
    assert first.read_bytes() == before
    assert sorted(p.name for p in records.iterdir()) == [first.name]


def test_invalid_save_leaves_no_record(valid_record, tmp_path):
    api = storage()
    valid_record["adjudication"]["status"] = "confirmed"
    with pytest.raises(ValueError, match="human_reviews"):
        api.save_record(valid_record, tmp_path / "records")
    assert not list(tmp_path.glob("records/*.json"))


def test_missing_predecessor_rejected(valid_record, tmp_path):
    api = storage()
    valid_record.update(revision=2, previous_revision=1)
    with pytest.raises(ValueError, match="predecessor"):
        api.save_record(valid_record, tmp_path / "records")


def test_revision_history_is_retained(valid_record, tmp_path):
    api = storage()
    records = tmp_path / "records"
    first = api.save_record(valid_record, records)
    before = first.read_bytes()
    second_record = copy.deepcopy(valid_record)
    second_record.update(revision=2, previous_revision=1)
    second_record["adjudication"]["rationale"] = (
        "Additional synthetic evidence considered."
    )
    second = api.save_record(second_record, records)
    assert first.read_bytes() == before
    assert api.load_records(records) == [(first, valid_record), (second, second_record)]
    assert api.load_records(second) == [(second, second_record)]


@pytest.mark.parametrize(
    "field,value", [("case_type", "prospective_audit"), ("source", None)]
)
def test_source_identity_and_type_cannot_change(valid_record, tmp_path, field, value):
    api = storage()
    api.save_record(valid_record, tmp_path / "records")
    changed = copy.deepcopy(valid_record)
    changed.update(revision=2, previous_revision=1)
    if field == "source":
        changed["source"]["title"] = "A different synthetic source"
    else:
        changed[field] = value
    with pytest.raises(ValueError, match="identity|case_type"):
        api.save_record(changed, tmp_path / "records")


@pytest.mark.parametrize("revision,previous", [(1, 1), (2, None), (3, 1)])
def test_wrong_predecessor_number_rejected(valid_record, tmp_path, revision, previous):
    api = storage()
    valid_record.update(revision=revision, previous_revision=previous)
    with pytest.raises(ValueError, match="previous_revision"):
        api.save_record(valid_record, tmp_path / "records")


def test_empty_input_rejected(tmp_path):
    api = storage()
    with pytest.raises(ValueError, match="empty|No canonical"):
        api.load_records(tmp_path)


@pytest.mark.parametrize(
    "name,content",
    [
        ("broken.json", "{}"),
        ("synthetic-001.r1.json", "{"),
        ("synthetic-001.r2.json", None),
    ],
)
def test_malformed_candidates_rejected(valid_record, tmp_path, name, content):
    api = storage()
    records = tmp_path / "records"
    records.mkdir()
    (records / name).write_text(
        content if content is not None else json.dumps(valid_record), encoding="utf-8"
    )
    with pytest.raises(ValueError):
        api.load_records(records)


def test_hash_checked_on_load(valid_record, tmp_path):
    api = storage()
    target = api.save_record(valid_record, tmp_path / "records")
    (tmp_path / "source.txt").write_bytes(b"Changed after snapshot")
    with pytest.raises(ValueError, match="hash mismatch"):
        api.load_records(target)


def test_discovery_ignores_non_json_artifacts(valid_record, tmp_path):
    api = storage()
    target = api.save_record(valid_record, tmp_path / "records")
    (target.parent / "notes.txt").write_text("Unrelated note", encoding="utf-8")
    assert len(api.load_records(target.parent)) == 1


def test_load_rejects_missing_history(valid_record, tmp_path):
    api = storage()
    valid_record.update(revision=2, previous_revision=1)
    records = tmp_path / "records"
    records.mkdir()
    target = records / "synthetic-001.r2.json"
    target.write_text(json.dumps(valid_record), encoding="utf-8")
    with pytest.raises(ValueError, match="predecessor"):
        api.load_records(target)


def test_artifact_symlink_escape(valid_record, tmp_path):
    api = storage()
    outside = tmp_path.parent / f"{tmp_path.name}-outside.txt"
    outside.write_bytes(b"outside")
    link = tmp_path / "link.txt"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"Host cannot create symlinks: {exc}")
    valid_record["source"]["artifact"]["path"] = "link.txt"
    with pytest.raises(ValueError, match="escapes"):
        api.save_record(valid_record, tmp_path / "records")


def test_concurrent_writers_publish_one_complete_snapshot(valid_record, tmp_path):
    from concurrent.futures import ThreadPoolExecutor

    api = storage()

    def write_once(_):
        try:
            return api.save_record(valid_record, tmp_path / "records")
        except (ValueError, FileExistsError):
            return None

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(write_once, range(4)))
    assert sum(result is not None for result in results) == 1
    assert api.load_records(tmp_path / "records")[0][1] == valid_record


def test_records_directory_cannot_redirect_save_outside_dataset(valid_record, tmp_path):
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    records = tmp_path / "records"
    directory_link(records, outside)
    with pytest.raises(ValueError, match="escapes dataset root"):
        storage_api.save_record(valid_record, records)
    assert list(outside.iterdir()) == []


@pytest.mark.parametrize("operation", ["load_directory", "load_file", "save"])
def test_relative_records_link_cannot_escape_dataset(
    valid_record, tmp_path, monkeypatch, operation
):
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    name = "synthetic-001.r1.json"
    payload = json.dumps(valid_record)
    (outside / name).write_text(payload, encoding="utf-8")
    directory_link(tmp_path / "records", outside)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="escapes dataset root"):
        if operation == "save":
            storage_api.save_record(valid_record, Path("records"))
        else:
            path = (
                Path("records") / name if operation == "load_file" else Path("records")
            )
            storage_api.load_records(path)
    assert (outside / name).read_text("utf-8") == payload
    assert sorted(path.name for path in outside.iterdir()) == [name]


@pytest.mark.parametrize("single_file", [False, True])
def test_records_directory_cannot_redirect_load_outside_dataset(
    valid_record, tmp_path, single_file
):
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    name = "synthetic-001.r1.json"
    (outside / name).write_text(json.dumps(valid_record), encoding="utf-8")
    records = tmp_path / "records"
    directory_link(records, outside)
    path = records / name if single_file else records
    with pytest.raises(ValueError, match="escapes dataset root"):
        storage_api.load_records(path)


def test_float_revision_is_rejected_without_publishing(valid_record, tmp_path):
    valid_record["revision"] = 1.0
    with pytest.raises(ValueError, match="revision"):
        storage_api.save_record(valid_record, tmp_path / "records")
    assert not list(tmp_path.glob("records/*"))


def test_ai_confirmation_follows_pending_snapshot(valid_record, human_review, tmp_path):
    first = storage_api.save_record(valid_record, tmp_path / "records")
    before = first.read_bytes()
    later = copy.deepcopy(valid_record)
    later.update(revision=2, previous_revision=1)
    later["adjudication"]["status"] = "confirmed"
    second_review = copy.deepcopy(human_review)
    second_review["reviewer_id"] = "synthetic-reviewer-b"
    later["human_reviews"] = [human_review, second_review]
    second = storage_api.save_record(later, tmp_path / "records")
    assert first.read_bytes() == before
    assert storage_api.load_records(second) == [(second, later)]
