"""Original software fixtures only; these are never research evidence."""

import copy
import hashlib
import json
import shutil
import zipfile
from importlib.resources import files

import pytest

from elvia.cli import main
from elvia.records import validate_record
from elvia.storage import load_records, save_record

FONT_ASSETS = (
    "SourceSerif4Variable-Roman.otf.woff2",
    "SourceSans3VF-Upright.otf.woff2",
)
FONT_LICENSES = ("LICENSE-SourceSerif4.txt", "LICENSE-SourceSans3.txt")


@pytest.fixture
def public_record(valid_record):
    record = copy.deepcopy(valid_record)
    record.update(schema_version="1.1.0", case_type="prospective_audit")
    record["publication"] = {
        "status": "preliminary_ai",
        "note": "Synthetic software fixture, not a paper.",
    }
    record["audit"] = {
        "venue": "Fixture venue",
        "year": 2026,
        "authors": ["Fictional fixture"],
        "landing_url": "https://example.org/fixture",
        "pdf_url": "https://example.org/fixture.pdf",
        "pdf_sha256": "a" * 64,
        "retrieved_at": "2026-10-19T00:00:00Z",
        "outcome": "candidate_issue",
        "summary": "Original synthetic software fixture only.",
        "limitations": ["No scientific conclusion; software test only."],
    }
    return record


def build(records, output):
    from elvia.site import build_site

    return build_site(records, output)


def test_search_pages_are_readable_linked_and_indexable(public_record, tmp_path):
    from xml.etree import ElementTree

    from elvia.site import build_site

    save_record(public_record, tmp_path / "records")
    output = tmp_path / "site"
    build_site(
        tmp_path / "records",
        output,
        public_base_url="https://example.org/atlas/",
    )
    case_path = f"cases/{public_record['case_id']}.html"
    page = (output / case_path).read_text("utf-8")
    assert public_record["proposition"]["claim"] in page
    assert public_record["audit"]["summary"] in page
    assert 'name="robots" content="index, follow"' in page
    assert f'rel="canonical" href="https://example.org/atlas/{case_path}"' in page
    assert "Supporting record &amp; provenance" in page
    assert "Independent review pending" in page
    assert "Download evidence (.zip)" not in page
    assert f'href="{case_path}"' in (output / "index.html").read_text("utf-8")
    locations = [
        n.text
        for n in ElementTree.parse(output / "sitemap.xml").iter()
        if n.tag.endswith("}loc")
    ]
    assert locations == [
        "https://example.org/atlas/",
        f"https://example.org/atlas/{case_path}",
    ]


def test_offline_case_pages_escape_prose_and_stay_unindexed(public_record, tmp_path):
    attack = '<img src=x onerror="alert(1)">'
    public_record["audit"]["summary"] = attack
    save_record(public_record, tmp_path / "records")
    output = tmp_path / "site"
    build(tmp_path / "records", output)
    page = (output / f"cases/{public_record['case_id']}.html").read_text("utf-8")
    assert attack not in page
    assert "&lt;img" in page
    assert 'name="robots" content="noindex, nofollow"' in page
    assert not (output / "sitemap.xml").exists()


@pytest.mark.parametrize(
    ("assessment", "label"),
    [("not_issue", "No Issue Found"), ("needs_evidence", "Needs Evidence")],
)
def test_search_problem_outcome_overrides_legacy_severity(
    public_record, assessment, label
):
    from elvia.search_pages import problems

    note = {
        "problems": [
            {
                "title": "Synthetic bounded finding",
                "source_location": "Fixture section",
                "claim": ["Synthetic claim"],
                "assumptions": [],
                "analysis_heading": "Analysis",
                "analysis": ["Synthetic check"],
                "result": ["Synthetic scope"],
                "severity": "major",
                "assessment": assessment,
            }
        ]
    }
    page = problems(public_record, note)
    assert f">{label}</span>" in page
    assert ">Major</span>" not in page


def test_public_metadata_and_legacy_compatibility(
    public_record, valid_record, tmp_path
):
    assert validate_record(valid_record, tmp_path) == []
    assert validate_record(public_record, tmp_path) == []
    public_record["schema_version"] = "1.0.0"
    assert validate_record(public_record)


@pytest.mark.parametrize(
    "mutation", ["missing_audit", "synthetic", "confirmed", "old_version"]
)
def test_preliminary_constraints(public_record, mutation):
    if mutation == "missing_audit":
        del public_record["audit"]
    elif mutation == "synthetic":
        public_record["case_type"] = "synthetic_demo"
    elif mutation == "confirmed":
        public_record.update(revision=2, previous_revision=1)
        public_record["adjudication"]["status"] = "confirmed"
    else:
        public_record["schema_version"] = "1.0.0"
    assert validate_record(public_record)


@pytest.mark.parametrize(
    "url",
    [
        "http://example.org",
        "javascript:alert(1)",
        "https://",
        "https://example.org/\nfoo",
        "https://user:password@example.org",
    ],
)
def test_source_urls_are_safe_https(public_record, url):
    public_record["audit"]["pdf_url"] = url
    assert validate_record(public_record)


@pytest.mark.parametrize(
    "field,value",
    [
        ("pdf_sha256", "b" * 64),
        ("pdf_url", "https://example.org/changed.pdf"),
        ("retrieved_at", "2026-10-20T00:00:00Z"),
        ("authors", ["Changed"]),
        ("venue", "Changed"),
        ("year", 2025),
        ("landing_url", "https://example.org/new"),
    ],
)
def test_upstream_identity_immutable(public_record, tmp_path, field, value):
    save_record(public_record, tmp_path / "records")
    later = copy.deepcopy(public_record)
    later.update(revision=2, previous_revision=1)
    later["audit"][field] = value
    with pytest.raises(ValueError, match="identity"):
        save_record(later, tmp_path / "records")


def test_latest_public_selection_and_portable_evidence(
    public_record, valid_record, tmp_path
):
    directory = tmp_path / "records"
    save_record(public_record, directory)
    later = copy.deepcopy(public_record)
    later.update(revision=2, previous_revision=1)
    later["audit"]["outcome"] = "scope_clarification"
    save_record(later, directory)
    draft = copy.deepcopy(public_record)
    draft["case_id"] = "private-fixture"
    draft["publication"]["status"] = "draft"
    save_record(draft, directory)
    valid_record["case_id"] = "demo-fixture"
    save_record(valid_record, directory)
    output = tmp_path / "site"
    assert build(directory, output) == 1
    data = json.loads((output / "data.json").read_text("utf-8"))
    assert [r["case_id"] for r in data["records"]] == [public_record["case_id"]]
    assert data["records"][0]["revision"] == 2
    assert data["counts"]["scope_clarification"] == 1
    assert data["counts"]["candidate_issue"] == 0
    assert (
        len(load_records(output / "evidence" / public_record["case_id"] / "records"))
        == 2
    )
    assert not list(output.rglob("private-fixture*"))
    assert not list(output.rglob("demo-fixture*"))
    case_root = output / "evidence" / public_record["case_id"]
    with zipfile.ZipFile(case_root.with_suffix(".zip")) as bundle:
        assert (
            bundle.read("records/synthetic-001.r2.json")
            == (case_root / "records/synthetic-001.r2.json").read_bytes()
        )
        exported_manifest = json.loads(bundle.read("manifest.json"))
        for artifact in exported_manifest["files"]:
            assert (
                hashlib.sha256(bundle.read(artifact["path"])).hexdigest()
                == artifact["sha256"]
            )
    manifest = json.loads((output / "manifest.json").read_text("utf-8"))
    for artifact in manifest["files"]:
        assert (
            hashlib.sha256((output / artifact["path"]).read_bytes()).hexdigest()
            == artifact["sha256"]
        )


def test_latest_draft_hides_previously_public_case(public_record, tmp_path):
    save_record(public_record, tmp_path / "records")
    public_record.update(revision=2, previous_revision=1)
    public_record["publication"]["status"] = "draft"
    save_record(public_record, tmp_path / "records")
    assert build(tmp_path / "records", tmp_path / "site") == 0
    assert json.loads((tmp_path / "site/data.json").read_text())["records"] == []


def test_private_predecessor_fails_closed(public_record, tmp_path):
    public_record["publication"]["status"] = "draft"
    save_record(public_record, tmp_path / "records")
    public_record.update(revision=2, previous_revision=1)
    public_record["publication"]["status"] = "preliminary_ai"
    save_record(public_record, tmp_path / "records")
    with pytest.raises(ValueError, match="predecessor"):
        build(tmp_path / "records", tmp_path / "site")
    assert not (tmp_path / "site").exists()


def test_invalid_records_cannot_create_output(public_record, tmp_path):
    path = save_record(public_record, tmp_path / "records")
    (tmp_path / "evidence.txt").write_text("modified")
    with pytest.raises(ValueError, match="hash"):
        build(path.parent, tmp_path / "site")
    assert not (tmp_path / "site").exists()


def test_never_overwrite_output(public_record, tmp_path):
    save_record(public_record, tmp_path / "records")
    output = tmp_path / "site"
    output.mkdir()
    (output / "precious.txt").write_text("keep")
    with pytest.raises(FileExistsError):
        build(tmp_path / "records", output)
    assert list(output.iterdir()) == [output / "precious.txt"]


def test_data_does_not_become_executable_html(public_record, tmp_path):
    attack = '</script><script>alert("fixture")</script>'
    public_record["audit"]["summary"] = attack
    save_record(public_record, tmp_path / "records")
    build(tmp_path / "records", tmp_path / "site")
    assert attack not in (tmp_path / "site/index.html").read_text("utf-8")
    assert "</script>" not in (tmp_path / "site/data.js").read_text("utf-8")
    assert (
        json.loads((tmp_path / "site/data.json").read_text("utf-8"))["records"][0][
            "audit"
        ]["summary"]
        == attack
    )
    script = (tmp_path / "site/atlas.js").read_text("utf-8")
    assert "innerHTML" not in script
    assert "textContent" in script


def test_bundled_assets_and_cli(valid_record, tmp_path):
    for name in ("index.html", "atlas.css", "atlas.js"):
        assert files("elvia").joinpath("web", name).is_file()
    save_record(valid_record, tmp_path / "records")
    assert (
        main(
            [
                "site",
                "build",
                "--records",
                str(tmp_path / "records"),
                "--output",
                str(tmp_path / "site"),
            ]
        )
        == 0
    )
    assert (tmp_path / "site/index.html").is_file()


def test_offline_fonts_and_licenses_are_complete_and_hashed(valid_record, tmp_path):
    save_record(valid_record, tmp_path / "records")
    output = tmp_path / "site"
    build(tmp_path / "records", output)
    manifest = json.loads((output / "manifest.json").read_text("utf-8"))
    hashes = {entry["path"]: entry["sha256"] for entry in manifest["files"]}
    css = (output / "atlas.css").read_text("utf-8")
    for asset in FONT_ASSETS + FONT_LICENSES:
        original = files("elvia").joinpath("web", asset).read_bytes()
        assert (output / asset).read_bytes() == original
        assert hashes[asset] == hashlib.sha256(original).hexdigest()
    for font in FONT_ASSETS:
        assert f'url("{font}")' in css
    assert "https://" not in css
    assert "font-src 'self'" in (output / "index.html").read_text("utf-8")


@pytest.mark.parametrize("fault", ["missing_font", "corrupt_font", "missing_license"])
def test_incomplete_asset_bundle_cannot_create_output(
    valid_record, tmp_path, monkeypatch, fault
):
    from elvia import site

    package = tmp_path / "package"
    shutil.copytree(files("elvia").joinpath("web"), package / "web")
    font = package / "web" / FONT_ASSETS[0]
    if fault == "corrupt_font":
        font.write_bytes(b"corrupted font software fixture")
    elif fault == "missing_font":
        font.unlink(missing_ok=True)
    else:
        (package / "web" / FONT_LICENSES[0]).unlink(missing_ok=True)
    monkeypatch.setattr(site, "files", lambda _: package)
    save_record(valid_record, tmp_path / "records")
    with pytest.raises((FileNotFoundError, ValueError)):
        build(tmp_path / "records", tmp_path / "site")
    assert not (tmp_path / "site").exists()


def test_export_collision_is_detected_before_output(public_record, tmp_path):
    bad = tmp_path / "manifest.json"
    bad.write_text("original software fixture", encoding="utf-8")
    public_record["source"]["artifact"] = {
        "path": bad.name,
        "sha256": hashlib.sha256(bad.read_bytes()).hexdigest(),
    }
    save_record(public_record, tmp_path / "records")
    with pytest.raises(ValueError, match="collision"):
        build(tmp_path / "records", tmp_path / "site")
    assert not (tmp_path / "site").exists()


def test_audit_identity_cannot_be_removed_or_downgraded(public_record, tmp_path):
    save_record(public_record, tmp_path / "records")
    public_record.update(schema_version="1.0.0", revision=2, previous_revision=1)
    public_record["publication"]["status"] = "draft"
    del public_record["audit"]
    with pytest.raises(ValueError, match="identity"):
        save_record(public_record, tmp_path / "records")


def test_audit_is_optional_for_nonpublic_v11_records(valid_record):
    valid_record["schema_version"] = "1.1.0"
    assert validate_record(valid_record) == []


def test_legacy_cannot_use_preliminary_state_without_metadata(valid_record):
    valid_record["publication"]["status"] = "preliminary_ai"
    valid_record["case_type"] = "prospective_audit"
    assert validate_record(valid_record)


def test_site_requires_directory_for_latest_selection(public_record, tmp_path):
    first = save_record(public_record, tmp_path / "records")
    with pytest.raises(ValueError, match="directory"):
        build(first, tmp_path / "site")
    assert not (tmp_path / "site").exists()
