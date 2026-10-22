"""Additive collection ingestion uses only synthetic scientific fixtures."""

import copy
import hashlib
import json
import runpy
from pathlib import Path

import pytest

from elvia.storage import load_records

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def _fixture(tmp_path):
    from test_review_revision import _builder, _revision_fixture

    audits, raw, audit, first = _revision_fixture(tmp_path)
    existing = tmp_path / "existing"
    _builder()(first / "records", audits, raw, existing, expected_count=1)
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    second = copy.deepcopy(audit)
    second.update(report_id="0002", title="Second fictional collection paper")
    report = raw / "reports/0002.tex"
    report.write_text("Second original synthetic report.", encoding="utf-8")
    pdf = raw / "second.pdf"
    pdf.write_bytes(b"Second fictional PDF bytes, excluded from exports.")
    second.update(
        pdf_path=str(pdf),
        pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
        raw_report_sha256=hashlib.sha256(report.read_bytes()).hexdigest(),
        source_checks=[{"path": str(pdf), "location": "Fixture", "note": "Synthetic."}],
    )
    (incoming / "0002.json").write_text(json.dumps(second), encoding="utf-8")
    return existing, incoming, raw, second


def _module():
    return runpy.run_path(str(SCRIPTS / "append_review_collection.py"))


def test_append_preserves_all_predecessors_and_combines_exact_bound_notes(tmp_path):
    from elvia.site import build_site

    existing, incoming, raw, _ = _fixture(tmp_path)
    original = {
        p.relative_to(existing): p.read_bytes()
        for p in existing.rglob("*")
        if p.is_file()
    }
    output = tmp_path / "combined"
    assert (
        _module()["append_collection"](
            existing / "records", incoming, raw, output, expected_count=1
        )
        == 1
    )
    assert len(load_records(output / "records")) == 3
    for name, value in original.items():
        if name.as_posix() != "case-notes.json":
            assert (output / name).read_bytes() == value
    catalog = json.loads((output / "case-notes.json").read_text("utf-8"))["cases"]
    assert sorted(note["revision"] for note in catalog.values()) == [1, 2]
    latest = {r["case_id"]: r for _, r in load_records(output / "records")}
    added = next(r for r in latest.values() if r["revision"] == 1)
    assert "Issue #25" in added["publication"]["note"]
    assert added["human_reviews"] == []
    assert added["adjudication"]["status"] == "pending"
    assert added["repair"]["adoption_status"] == "not_requested"
    assert not list(output.rglob("*.pdf"))
    assert build_site(output / "records", tmp_path / "site") == 2
    assert original == {
        p.relative_to(existing): p.read_bytes()
        for p in existing.rglob("*")
        if p.is_file()
    }


@pytest.mark.parametrize("collision", ["case_id", "source_pdf", "source_title"])
def test_append_rejects_duplicate_cases_or_papers_before_output(tmp_path, collision):
    existing, incoming, raw, audit = _fixture(tmp_path)
    prior = load_records(existing / "records")[-1][1]
    if collision == "case_id":
        audit.update(report_id="0001", title=prior["source"]["title"])
        report = raw / "reports/0001.tex"
        audit["raw_report_sha256"] = hashlib.sha256(report.read_bytes()).hexdigest()
        (incoming / "0002.json").unlink()
    elif collision == "source_pdf":
        old_audit = json.loads(
            next(existing.glob("evidence/*/r2/verification.json")).read_text("utf-8")
        )
        audit["pdf_path"] = str(raw / "original.pdf")
        audit["pdf_sha256"] = old_audit["pdf_sha256"]
    else:
        audit["title"] = prior["source"]["title"].upper() + "  "
    (incoming / f"{audit['report_id']}.json").write_text(
        json.dumps(audit), encoding="utf-8"
    )
    output = tmp_path / "duplicate"
    with pytest.raises(ValueError, match="duplicate|existing"):
        _module()["append_collection"](
            existing / "records", incoming, raw, output, expected_count=1
        )
    assert not output.exists()


def test_append_excludes_a_private_file_added_after_validation(tmp_path):
    existing, incoming, raw, _ = _fixture(tmp_path)
    module = _module()
    importer = module["IMPORTER"]
    original_import = importer["import_collection"]
    private = existing / "private-draft.txt"

    def add_private(*args, **kwargs):
        private.write_text("Concurrent private fixture.", encoding="utf-8")
        return original_import(*args, **kwargs)

    importer["import_collection"] = add_private
    output = tmp_path / "safe"
    module["append_collection"](
        existing / "records", incoming, raw, output, expected_count=1
    )
    assert private.is_file()
    assert not (output / private.name).exists()


def test_append_preserves_a_competing_destination(tmp_path, monkeypatch):
    existing, incoming, raw, _ = _fixture(tmp_path)
    module = _module()
    importer = module["IMPORTER"]
    original_import = importer["import_collection"]
    output = tmp_path / "competing"

    def competing(*args, **kwargs):
        count = original_import(*args, **kwargs)
        output.mkdir()
        (output / "unrelated.txt").write_text("Other actor.", encoding="utf-8")
        return count

    monkeypatch.setitem(importer, "import_collection", competing)
    with pytest.raises(FileExistsError):
        module["append_collection"](
            existing / "records", incoming, raw, output, expected_count=1
        )
    assert (output / "unrelated.txt").read_text("utf-8") == "Other actor."


@pytest.mark.parametrize("identity", ["source_pdf", "source_title"])
@pytest.mark.parametrize("target", ["existing", "incoming"])
def test_append_rechecks_changed_incoming_paper_identity(
    tmp_path, monkeypatch, identity, target
):
    existing, incoming, raw, second = _fixture(tmp_path)
    module = _module()
    original_import = module["IMPORTER"]["import_collection"]
    expected_count = 1
    changed_path = incoming / "0002.json"
    reference = load_records(existing / "records")[-1][1]
    reference_title = reference["source"]["title"]
    reference_pdf = raw / "original.pdf"
    if target == "incoming":
        third = copy.deepcopy(second)
        third.update(report_id="0003", title="Third fictional collection paper")
        report = raw / "reports/0003.tex"
        report.write_text("Third original synthetic report.", encoding="utf-8")
        pdf = raw / "third.pdf"
        pdf.write_bytes(b"Third fictional PDF bytes, excluded from exports.")
        third.update(
            pdf_path=str(pdf),
            pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
            raw_report_sha256=hashlib.sha256(report.read_bytes()).hexdigest(),
        )
        changed_path = incoming / "0003.json"
        changed_path.write_text(json.dumps(third), encoding="utf-8")
        reference_title = second["title"]
        reference_pdf = Path(second["pdf_path"])
        expected_count = 2

    def change_after_preflight(*args, **kwargs):
        changed = json.loads(changed_path.read_text("utf-8"))
        if identity == "source_pdf":
            changed["pdf_path"] = str(reference_pdf)
            changed["pdf_sha256"] = hashlib.sha256(
                reference_pdf.read_bytes()
            ).hexdigest()
        else:
            changed["title"] = reference_title.upper() + "  "
        changed_path.write_text(json.dumps(changed), encoding="utf-8")
        return original_import(*args, **kwargs)

    monkeypatch.setitem(module["IMPORTER"], "import_collection", change_after_preflight)
    output = tmp_path / "changed-identity"
    with pytest.raises(ValueError, match="duplicate|existing"):
        module["append_collection"](
            existing / "records", incoming, raw, output, expected_count=expected_count
        )
    assert not output.exists()


@pytest.mark.parametrize(
    "change",
    [
        "moderate",
        "missing_paper_rationale",
        "blank_paper_rationale",
        "missing_problem_rationale",
        "blank_problem_rationale",
    ],
)
def test_append_validates_the_exported_assessment_after_input_changes(
    tmp_path, monkeypatch, change
):
    existing, incoming, raw, _ = _fixture(tmp_path)
    module = _module()
    original_import = module["IMPORTER"]["import_collection"]

    def change_after_preflight(*args, **kwargs):
        path = incoming / "0002.json"
        audit = json.loads(path.read_text("utf-8"))
        if change == "moderate":
            audit["severity"] = "moderate"
            for problem in audit["problems"]:
                problem["severity"] = "moderate"
        else:
            item = audit if "paper" in change else audit["problems"][0]
            if change.startswith("missing"):
                item.pop("impact_rationale")
            else:
                item["impact_rationale"] = "  \n  "
        path.write_text(json.dumps(audit), encoding="utf-8")
        return original_import(*args, **kwargs)

    monkeypatch.setitem(module["IMPORTER"], "import_collection", change_after_preflight)
    output = tmp_path / "changed-assessment"
    with pytest.raises(ValueError, match="Moderate|impact rationale"):
        module["append_collection"](
            existing / "records", incoming, raw, output, expected_count=1
        )
    assert not output.exists()
