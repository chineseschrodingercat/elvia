"""Presentation is derived; scientific snapshots remain authoritative."""

import copy
import hashlib
import json
import re
from importlib.resources import files
from pathlib import Path

import pytest

from elvia.storage import load_records


def collection():
    return Path(__file__).resolve().parents[1] / "studies/neurips2025/records"


@pytest.fixture
def notation_fixture(tmp_path, monkeypatch, valid_record):
    from elvia import math_presentation

    record = copy.deepcopy(valid_record)
    entry = {
        "revision": record["revision"],
        "record_sha256": hashlib.sha256(
            json.dumps(
                record, sort_keys=True, separators=(",", ":"), ensure_ascii=True
            ).encode()
        ).hexdigest(),
        "replacements": [
            {"source": record["proposition"]["claim"], "typeset": r"\(x^2 \geq x\)"}
        ],
    }
    package = tmp_path / "package"
    (package / "web").mkdir(parents=True)
    (package / "web/math-notation.json").write_text(
        json.dumps({"format_version": 1, "cases": {record["case_id"]: entry}}), "utf-8"
    )
    monkeypatch.setattr(math_presentation, "files", lambda _: package)
    return record


def test_presentation_is_bound_to_exact_snapshot_and_does_not_mutate(notation_fixture):
    from elvia.math_presentation import prepare_presentation

    record = notation_fixture
    original = copy.deepcopy(record)
    assert prepare_presentation([record])[record["case_id"]]["replacements"]
    assert record == original
    record["proposition"]["claim"] += " Changed software fixture."
    with pytest.raises(ValueError, match="presentation.*snapshot"):
        prepare_presentation([record])


def test_future_revision_never_inherits_old_typesetting(notation_fixture):
    from elvia.math_presentation import prepare_presentation

    record = notation_fixture
    record["revision"] += 1
    assert prepare_presentation([record]) == {}


def test_unknown_records_need_no_legacy_mapping(valid_record):
    from elvia.math_presentation import prepare_presentation

    assert prepare_presentation([valid_record]) == {}


def test_local_math_assets_have_complete_css_closure_and_pinned_hashes(tmp_path):
    from elvia.site import MATH_HASHES, build_site

    output = tmp_path / "atlas"
    build_site(collection(), output)
    for name, expected in MATH_HASHES.items():
        assert hashlib.sha256((output / name).read_bytes()).hexdigest() == expected
    css_path = output / "vendor/katex/katex.min.css"
    css = css_path.read_text("utf-8")
    for name in re.findall(r"url\(([^)]+)\)", css):
        assert not name.startswith(("https:", "http:", "//", "data:"))
        assert (css_path.parent / name).is_file()
    html = (output / "index.html").read_text("utf-8")
    assert 'src="vendor/katex/katex.min.js"' in html
    assert 'href="vendor/katex/katex.min.css"' in html
    assert html.index("katex.min.js") < html.index('src="math.js"')
    assert html.index('src="math.js"') < html.index('src="atlas.js"')
    payload = json.loads((output / "data.json").read_text("utf-8"))
    assert payload["presentation"] == {}
    original = {r["case_id"]: r for _, r in load_records(collection())}
    assert {r["case_id"]: r for r in payload["records"]} == original


@pytest.mark.parametrize("asset", ["katex.min.js", "fonts/KaTeX_Main-Regular.woff2"])
def test_math_asset_corruption_fails_before_output(tmp_path, monkeypatch, asset):
    import shutil

    from elvia import site

    package = tmp_path / "package"
    shutil.copytree(files("elvia").joinpath("web"), package / "web")
    (package / "web/vendor/katex" / asset).write_bytes(b"corrupt software fixture")
    monkeypatch.setattr(site, "files", lambda _: package)
    with pytest.raises(ValueError, match="math.*hash"):
        site.build_site(collection(), tmp_path / "atlas")
    assert not (tmp_path / "atlas").exists()
