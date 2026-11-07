"""Reader introductions preserve bounded source prose, using fictional fixtures."""

import copy
import json
import subprocess
from pathlib import Path

from elvia.reader_intro import reader_introduction, source_metadata
from elvia.search_pages import write_search_pages

ROOT = Path(__file__).resolve().parents[1]


def reader_case(valid_record):
    record = copy.deepcopy(valid_record)
    record["audit"] = {
        "authors": ["Fictional Author"],
        "year": 2025,
        "venue": "Fictional venue",
        "landing_url": "https://example.org/fictional",
        "outcome": "candidate_issue",
        "summary": "A local fictional comparison fails.",
        "limitations": ["The final fictional theorem is not refuted."],
        "pdf_sha256": "a" * 64,
    }
    record["source"]["version"] = "publisher PDF, corrected 2025-05-02"
    note = {
        "revision": record["revision"],
        "report": [
            "Abstract: The fictional comparison fails at x=1/2. "
            "The final fictional theorem is not refuted."
        ],
        "problems": [
            {
                "id": "fictional-local-comparison",
                "title": "A local fictional comparison fails",
                "severity": "major",
                "assessment": "supported",
                "claim": ["Every positive rational exceeds one."],
                "assumptions": [],
                "source_location": "Fictional Lemma 2, p. 3",
                "analysis_heading": "Proof",
                "analysis": ["The value one half contradicts the comparison."],
                "result": ["The final fictional theorem is not refuted."],
                "repair": None,
            }
        ],
    }
    return record, note


def test_introduction_keeps_whole_bound_abstract_and_separate_source_version(
    valid_record,
):
    record, note = reader_case(valid_record)
    before = copy.deepcopy((record, note))
    intro = reader_introduction(record, note)
    assert intro["text"] == note["report"][0].removeprefix("Abstract: ")
    assert intro["evidence_fragment"] == "problem-1-evidence"
    metadata = dict(source_metadata(record))
    assert metadata["Inspected paper version"] == record["source"]["version"]
    assert metadata["Analysis revision"] == "1"
    assert metadata["Analysis origin"] == "AI-origin analysis"
    assert metadata["Scientific status"] == "Independent review pending"
    assert (record, note) == before


def test_stale_or_long_abstract_never_gets_truncated_into_an_unqualified_claim(
    valid_record,
):
    record, note = reader_case(valid_record)
    note["report"] = ["Abstract: " + "A long claim. " * 200 + "But it is unproved."]
    intro = reader_introduction(record, note)
    assert "A long claim." not in intro["text"]
    assert note["problems"][0]["title"] in intro["text"]
    assert note["problems"][0]["result"][0] in intro["text"]
    assert intro["coverage"] == "first_finding"
    note["revision"] += 1
    assert "x=1/2" not in reader_introduction(record, note)["text"]


def test_opening_precedes_tools_findings_and_complete_unchanged_proof(
    valid_record, tmp_path
):
    record, note = reader_case(valid_record)
    (tmp_path / "index.html").write_text("<head></head><noscript></noscript>")
    write_search_pages(
        tmp_path, {"records": [record], "case_notes": {record["case_id"]: note}}
    )
    page = (tmp_path / "cases" / f"{record['case_id']}.html").read_text("utf-8")
    assert (
        page.index('id="detail-title"')
        < page.index('class="detail-citation"')
        < page.index('class="source-metadata"')
        < page.index('class="reader-introduction"')
        < page.index('class="case-tools"')
        < page.index('class="key-findings"')
    )
    assert 'href="#problem-1-evidence"' in page
    assert "Before reusing the checked step" in page
    assert note["problems"][0]["analysis"][0] in page


def test_static_and_dynamic_introductions_agree_for_every_current_case():
    fixtures = []
    for study in ("math2025", "icml2025", "neurips2025"):
        dataset = ROOT / "studies" / study
        notes = json.loads((dataset / "case-notes.json").read_text("utf-8"))["cases"]
        for path in sorted((dataset / "records").glob("*.json")):
            record = json.loads(path.read_text("utf-8"))
            fixtures.append(
                {"record": record, "note": notes.get(record["case_id"], {})}
            )
    assert len(fixtures) == 1214
    code = (
        "const fs=require('node:fs');"
        "const api=require('./src/elvia/web/case-note.js');"
        "const cases=JSON.parse(fs.readFileSync(0,'utf8'));"
        "process.stdout.write(JSON.stringify(cases.map(({record,note})=>"
        "({intro:api.readerIntroduction(record,note),metadata:api.sourceMetadata(record)}))));"
    )
    result = subprocess.run(
        ["node", "-e", code],
        input=json.dumps(fixtures),
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
        cwd=ROOT,
    )
    actual = json.loads(result.stdout)
    for fixture, dynamic in zip(fixtures, actual, strict=True):
        record, note = fixture["record"], fixture["note"]
        assert dynamic == {
            "intro": reader_introduction(record, note),
            "metadata": [list(value) for value in source_metadata(record)],
        }, record["case_id"]
        assert dynamic["intro"]["text"]
        assert len(dynamic["intro"]["text"]) <= 1100


def test_website_places_compact_availability_after_immediate_reader_value(
    valid_record, tmp_path, monkeypatch
):
    monkeypatch.syspath_prepend(str(ROOT))
    from website import build as website_build

    record, note = reader_case(valid_record)

    def fake_build_site(datasets, output, **kwargs):
        output.mkdir()
        payload = {
            "records": [record],
            "case_notes": {record["case_id"]: note},
        }
        (output / "index.html").write_text("<head></head><noscript></noscript>")
        (output / "data.json").write_text(json.dumps(payload))
        write_search_pages(output, payload)
        return 1

    monkeypatch.setattr(website_build, "build_site", fake_build_site)
    output = tmp_path / "source-preview"
    assert website_build.build(output) == 1
    page = (output / "cases" / f"{record['case_id']}.html").read_text("utf-8")
    assert (
        page.index('class="reader-introduction"')
        < page.index('class="case-tools"')
        < page.index('class="paper-availability"')
        < page.index('class="key-findings"')
    )
    assert 'aria-label="Contribution availability"' in page
    assert "<h2>Contribution availability</h2>" not in page
