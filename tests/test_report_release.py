"""Incremental report publication uses only synthetic PDFs and a fake compiler."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from elvia.reader import record_digest


def digest(value):
    return hashlib.sha256(value).hexdigest()


@pytest.fixture
def release_tool():
    path = Path(__file__).resolve().parents[1] / "scripts/build_report_release.py"
    spec = importlib.util.spec_from_file_location("report_release_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def report_case(valid_record, tmp_path):
    record = copy.deepcopy(valid_record)
    record["audit"] = {"pdf_sha256": digest(b"%PDF-1.4\nArticle fixture\n%%EOF\n")}
    dataset = tmp_path / "dataset"
    source = dataset / "evidence" / record["case_id"] / "report.tex"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"\\begin{document}\nOriginal fixture.\n\\end{document}\n")
    record["evidence"].append(
        {
            "id": "editable-latex",
            "stance": "support",
            "description": "Synthetic editable report",
            "method": "Fixture only",
            "artifact": {
                "path": source.relative_to(dataset).as_posix(),
                "sha256": digest(source.read_bytes()),
            },
        }
    )
    baseline = tmp_path / "baseline"
    baseline.mkdir()
    article = b"%PDF-1.4\nArticle fixture\n%%EOF\n"
    report = b"%PDF-1.4\nAccepted fixture report\n%%EOF\n"
    (baseline / "article.pdf").write_bytes(article)
    (baseline / "report.pdf").write_bytes(report)
    row = {
        "revision": 1,
        "record_sha256": record_digest(record),
        "article": {"path": "article.pdf", "sha256": digest(article)},
        "report": {"path": "report.pdf", "sha256": digest(report)},
        "report_source_sha256": digest(source.read_bytes()),
        "compiled_source_sha256": digest(source.read_bytes()),
        "revisions": [],
    }
    (baseline / "reader-files.json").write_text(
        json.dumps({"format_version": 1, "cases": {record["case_id"]: row}}),
        encoding="utf-8",
    )
    return record, dataset, source, baseline, row


def test_unchanged_pdf_is_reused_without_starting_compiler(
    release_tool, report_case, tmp_path, monkeypatch
):
    record, dataset, _, baseline, _ = report_case
    monkeypatch.setattr(
        release_tool.subprocess,
        "run",
        lambda *args, **kwargs: pytest.fail("Unchanged PDF must not be recompiled"),
    )
    target = tmp_path / "published"
    result = release_tool.build_release(
        [(record, dataset)], baseline, target, Path("unused-compiler"), workers=1
    )
    assert result["reused"] == 1 and result["compiled"] == 0
    row = json.loads((target / "reader-files.json").read_text())["cases"][
        record["case_id"]
    ]
    assert (target / row["report"]["path"]).read_bytes() == (
        baseline / "report.pdf"
    ).read_bytes()


def test_changed_report_compiles_exact_lf_bytes_and_rebinds_pdf(
    release_tool, report_case, tmp_path, monkeypatch
):
    record, dataset, source, baseline, _ = report_case
    source.write_bytes(b"\\begin{document}\nCleaned fixture.\n\\end{document}\n")
    record["evidence"][-1]["artifact"]["sha256"] = digest(source.read_bytes())
    seen = []

    def compile_fixture(arguments, **kwargs):
        assert "--untrusted" in arguments
        actual = Path(arguments[-1]).read_bytes()
        assert b"\r\n" not in actual
        seen.append(actual)
        directory = Path(arguments[arguments.index("--outdir") + 1])
        (directory / "report.pdf").write_bytes(b"%PDF-1.4\nCleaned fixture\n%%EOF\n")
        return SimpleNamespace(returncode=0, stdout=b"fixture", stderr=b"")

    monkeypatch.setattr(release_tool.subprocess, "run", compile_fixture)
    target = tmp_path / "published"
    result = release_tool.build_release(
        [(record, dataset)], baseline, target, Path("fake-compiler"), workers=1
    )
    assert result["compiled"] == len(seen) == 1
    row = json.loads((target / "reader-files.json").read_text())["cases"][
        record["case_id"]
    ]
    assert row["compiled_source_sha256"] == digest(seen[0])
    assert row["report_source_sha256"] == digest(source.read_bytes())
    assert row["record_sha256"] == record_digest(record)
    assert (target / row["article"]["path"]).read_bytes() == (
        baseline / "article.pdf"
    ).read_bytes()


def test_corrupt_baseline_pdf_is_rejected_before_creating_output(
    release_tool, report_case, tmp_path
):
    record, dataset, _, baseline, _ = report_case
    (baseline / "report.pdf").write_bytes(b"Changed unapproved input")
    target = tmp_path / "published"
    with pytest.raises(ValueError, match="hash|PDF"):
        release_tool.build_release(
            [(record, dataset)], baseline, target, Path("unused")
        )
    assert not target.exists()


def test_record_change_without_corresponding_report_change_is_not_silently_reused(
    release_tool, report_case, tmp_path
):
    record, dataset, _, baseline, _ = report_case
    record["concern"]["description"] = "Different synthetic finding, unchanged PDF."
    with pytest.raises(ValueError, match="snapshot|report source"):
        release_tool.build_release(
            [(record, dataset)], baseline, tmp_path / "blocked", Path("unused")
        )
