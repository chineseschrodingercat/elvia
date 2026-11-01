"""A publisher-confirmed online-first citation may lack an assigned volume."""

import copy

import pytest

from elvia.public_context import original_citation
from elvia.reader import prepare_reader, record_digest
from elvia.search_pages import citation as render_citation


def selected(citation):
    record = {"case_id": "math2025-0204", "revision": 1}
    row = {
        "revision": 1,
        "record_sha256": record_digest(record),
        "citation": citation,
        "contributors": [],
    }
    catalog = {"format_version": 1, "cases": {record["case_id"]: row}}
    return prepare_reader([record], catalog), row


def citation():
    return {
        "title": "A verified mathematical article",
        "authors": ["A. Author"],
        "container": "Journal of Mathematics",
        "volume": "12",
        "year": 2025,
        "doi": "10.1000/example",
        "source_url": "https://publisher.example/article",
        "first_page": "1",
        "last_page": "20",
    }


def test_assigned_volume_row_is_returned_unchanged():
    entry = citation()
    original = copy.deepcopy(entry)
    result, row = selected(entry)
    assert result["math2025-0204"] is row
    assert entry == original


@pytest.mark.parametrize("volume", ["", " "])
def test_explicit_online_first_allows_unassigned_volume(volume):
    entry = citation()
    entry.update(volume=volume, publication_status="online_first")
    result, row = selected(entry)
    assert result["math2025-0204"] == row


def test_explicit_online_first_allows_omitted_volume():
    entry = citation()
    entry.pop("volume")
    entry["publication_status"] = "online_first"
    result, row = selected(entry)
    assert result["math2025-0204"] == row
    assert "volume" not in row["citation"]


@pytest.mark.parametrize("status", [None, "", "online-first", "unknown"])
def test_missing_volume_without_exact_verified_status_remains_invalid(status):
    entry = citation()
    entry["volume"] = ""
    if status is not None:
        entry["publication_status"] = status
    with pytest.raises(ValueError, match="citation is incomplete"):
        selected(entry)


@pytest.mark.parametrize("volume", [None, 12, [], {}])
def test_online_first_does_not_allow_invalid_volume_type(volume):
    entry = citation()
    entry.update(volume=volume, publication_status="online_first")
    with pytest.raises(ValueError, match="citation is incomplete"):
        selected(entry)


@pytest.mark.parametrize(
    "field,value",
    [
        ("title", ""),
        ("container", ""),
        ("authors", []),
        ("source_url", "http://publisher.example/article"),
        ("doi", "invalid"),
        ("year", "2025"),
    ],
)
def test_online_first_retains_all_other_citation_requirements(field, value):
    entry = citation()
    entry.update(volume="", publication_status="online_first")
    entry[field] = value
    with pytest.raises(ValueError):
        selected(entry)


def render_fixture():
    record = {
        "case_id": "math2025-0204",
        "revision": 1,
        "source": {"title": "Fallback title"},
        "audit": {
            "authors": ["Fallback Author"],
            "venue": "Fallback venue",
            "year": 2024,
            "landing_url": "https://fallback.example/article",
        },
    }
    return record, {"citation": citation()}


def test_default_proceedings_outputs_remain_byte_identical():
    record, row = render_fixture()
    assert original_citation(record, row) == {
        "plain": (
            "A. Author. A verified mathematical article. Journal of Mathematics, "
            "vol. 12, 2025, pp. 1–20. https://doi.org/10.1000/example"
        ),
        "bibtex": (
            "@inproceedings{math2025-0204-original,\n"
            "  title = {{A verified mathematical article}},\n"
            "  author = {A. Author},\n"
            "  year = {2025},\n"
            "  booktitle = {Journal of Mathematics},\n"
            "  volume = {12},\n"
            "  pages = {1--20},\n"
            "  doi = {10.1000/example},\n"
            "  url = {https://doi.org/10.1000/example}\n}\n"
        ),
        "ris": (
            "TY  - CONF\nAU  - A. Author\nTI  - A verified mathematical article\n"
            "PY  - 2025\nT2  - Journal of Mathematics\nVL  - 12\n"
            "SP  - 1\nEP  - 20\nDO  - 10.1000/example\n"
            "UR  - https://doi.org/10.1000/example\nER  -\n"
        ),
    }
    assert render_citation(record, row) == (
        "A. Author. “<span data-case-prose>A verified mathematical article</span>."
        "” <em>Journal of Mathematics</em>, vol. 12, 2025, pp. 1–20, "
        '<a href="https://doi.org/10.1000/example" rel="noopener noreferrer">'
        "https://doi.org/10.1000/example</a>."
    )


@pytest.mark.parametrize("volume", ["", " ", None])
def test_online_first_journal_omits_unassigned_volume_in_all_formats(volume):
    record, row = render_fixture()
    entry = row["citation"]
    entry.update(publication_type="journal", publication_status="online_first")
    if volume is None:
        del entry["volume"]
    else:
        entry["volume"] = volume
    original = copy.deepcopy(row)
    exports = original_citation(record, row)
    html = render_citation(record, row)
    for rendered in [*exports.values(), html]:
        assert "Published online" in rendered
        assert "vol." not in rendered
    assert "volume =" not in exports["bibtex"]
    assert "VL  -" not in exports["ris"]
    assert exports["bibtex"].startswith("@article{")
    assert "journal = {Journal of Mathematics}" in exports["bibtex"]
    assert "booktitle =" not in exports["bibtex"]
    assert exports["ris"].startswith("TY  - JOUR\n")
    assert row == original


def test_assigned_volume_journal_uses_article_and_preserves_volume():
    record, row = render_fixture()
    previous = render_citation(record, row)
    row["citation"]["publication_type"] = "journal"
    exports = original_citation(record, row)
    assert exports["bibtex"].startswith("@article{")
    assert "journal = {Journal of Mathematics}" in exports["bibtex"]
    assert "volume = {12}" in exports["bibtex"]
    assert exports["ris"].startswith("TY  - JOUR\n")
    assert "VL  - 12\n" in exports["ris"]
    assert "Published online" not in exports["plain"]
    assert render_citation(record, row) == previous


def test_online_first_does_not_infer_journal_type():
    record, row = render_fixture()
    row["citation"].update(volume="", publication_status="online_first")
    exports = original_citation(record, row)
    assert exports["bibtex"].startswith("@inproceedings{")
    assert exports["ris"].startswith("TY  - CONF\n")
