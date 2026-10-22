"""Subprocess checks for the documented offline command sequence."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from elvia.storage import save_record

SOURCE = Path(__file__).resolve().parents[1] / "src"


def run_cli(tmp_path, *args):
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(SOURCE)
    environment["PYTHONIOENCODING"] = "utf-8"
    for key in list(environment):
        if key.endswith("API_KEY") or key in {"HF_TOKEN", "OPENAI_ACCESS_TOKEN"}:
            environment.pop(key)
    return subprocess.run(
        [sys.executable, "-m", "elvia", *map(str, args)],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )


def test_cli_complete_offline_sequence(tmp_path):
    result = run_cli(tmp_path, "demo", "--output", "demo-output")
    assert result.returncode == 0, result.stderr
    assert "records" in result.stdout
    records = tmp_path / "demo-output" / "records"
    for path in [records, next(records.glob("*.json"))]:
        result = run_cli(tmp_path, "validate", path)
        assert result.returncode == 0, result.stderr
        assert "1" in result.stdout
    result = run_cli(
        tmp_path,
        "index",
        "rebuild",
        "--records",
        records,
        "--db",
        "demo-output/index.sqlite",
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "demo-output/index.sqlite").is_file()
    result = run_cli(tmp_path, "export", records, "--output", "demo-output/export")
    assert result.returncode == 0, result.stderr
    result = run_cli(tmp_path, "validate", "demo-output/export/records")
    assert result.returncode == 0, result.stderr
    exported = next((tmp_path / "demo-output/export/records").glob("*.json"))
    assert (
        json.loads(exported.read_text("utf-8"))["adjudication"]["status"] == "pending"
    )


def test_cli_located_validation_error(tmp_path):
    assert run_cli(tmp_path, "demo", "--output", "demo").returncode == 0
    path = next((tmp_path / "demo/records").glob("*.json"))
    record = json.loads(path.read_text("utf-8"))
    record["repair"]["verification_status"] = "invented"
    path.write_text(json.dumps(record), encoding="utf-8")
    result = run_cli(tmp_path, "validate", path)
    assert result.returncode != 0
    assert path.name in result.stderr
    assert "$.repair.verification_status" in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("input_path", [".", "synthetic-001.r1.json"])
@pytest.mark.parametrize("command", ["validate", "index", "export"])
def test_cli_relative_inputs_from_records_directory(
    tmp_path, valid_record, input_path, command
):
    target = save_record(valid_record, tmp_path / "records")
    arguments = {
        "validate": ["validate", input_path],
        "index": [
            "index",
            "rebuild",
            "--records",
            input_path,
            "--db",
            "../index.sqlite",
        ],
        "export": ["export", input_path, "--output", "../export"],
    }[command]
    result = run_cli(target.parent, *arguments)
    assert result.returncode == 0, result.stderr
    assert "1" in result.stdout
    if command == "index":
        assert (tmp_path / "index.sqlite").is_file()
    elif command == "export":
        result = run_cli(target.parent, "validate", "../export/records")
        assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("value", [{}, []])
@pytest.mark.parametrize(
    "section,field", [("adjudication", "status"), ("concern", "severity")]
)
def test_cli_malformed_enum_types_fail_without_traceback(
    tmp_path, valid_record, section, field, value
):
    target = save_record(valid_record, tmp_path / "records")
    valid_record["adjudication"]["status"] = "confirmed"
    valid_record[section][field] = value
    target.write_text(json.dumps(valid_record), encoding="utf-8")
    result = run_cli(tmp_path, "validate", target)
    assert result.returncode == 1
    assert target.name in result.stderr
    assert f"$.{section}.{field}:" in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize(
    "arguments",
    [
        ["validate", "missing/records"],
        ["demo", "--output", "."],
        ["export", "missing/records", "--output", "export"],
        ["index", "rebuild", "--records", "missing/records", "--db", "index.sqlite"],
        ["index"],
        ["unknown"],
    ],
)
def test_cli_routine_errors_are_friendly(tmp_path, arguments):
    result = run_cli(tmp_path, *arguments)
    assert result.returncode != 0
    assert result.stderr
    assert "Traceback" not in result.stderr
    assert not (tmp_path / "export").exists()
    assert not (tmp_path / "index.sqlite").exists()


def test_cli_export_existing_directory_preserves_contents(tmp_path):
    assert run_cli(tmp_path, "demo", "--output", "demo").returncode == 0
    output = tmp_path / "export"
    output.mkdir()
    (output / "keep").write_bytes(b"keep")
    result = run_cli(tmp_path, "export", "demo/records", "--output", output)
    assert result.returncode != 0
    assert "new directory" in result.stderr
    assert "Traceback" not in result.stderr
    assert (output / "keep").read_bytes() == b"keep"
