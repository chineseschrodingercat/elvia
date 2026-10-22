"""Exercise the original exact computation and honest process state."""

import importlib
import importlib.util
import json

import pytest

from elvia.storage import load_records


def create(output):
    assert importlib.util.find_spec("elvia.demo") is not None, "demo is not implemented"
    return importlib.import_module("elvia.demo").create_demo(output)


def test_demo_pending_and_exact(tmp_path):
    path = create(tmp_path / "demo")
    record = load_records(path)[0][1]
    assert record["case_type"] == "synthetic_demo"
    assert record["adjudication"]["status"] == "pending"
    assert record["human_reviews"] == []
    assert record["proposition"]["claim"] == "For all real x, x² >= x."
    assert record["proposition"]["domain"] == "Real numbers"
    root = path.parent.parent
    evidence = (root / record["evidence"][0]["artifact"]["path"]).read_text("utf-8")
    assert "x = 1/2" in evidence
    assert "x² - x = -1/4" in evidence
    assert record["repair"]["verification_status"] == "pending"
    assert record["repair"]["changed_assumptions"] == ["x <= 0 or x >= 1"]
    assert record["repair"]["adoption_status"] == "not_requested"
    assert record["runs"][0]["model"] is None
    assert "No model" in record["runs"][0]["model_note"]
    for artifact in [record["source"]["artifact"], record["evidence"][0]["artifact"]]:
        assert b"\r" not in (root / artifact["path"]).read_bytes()
    assert json.loads(path.read_text("utf-8")) == record


def test_demo_never_overwrites_existing_directory(tmp_path):
    output = tmp_path / "demo"
    output.mkdir()
    sentinel = output / "keep.txt"
    sentinel.write_bytes(b"keep")
    with pytest.raises(FileExistsError):
        create(output)
    assert sentinel.read_bytes() == b"keep"
    assert list(output.iterdir()) == [sentinel]
