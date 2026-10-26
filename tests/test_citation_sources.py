"""Synthetic citations with genuinely absent DOI metadata; no network access."""

import copy

import pytest

from elvia.public_context import original_citation
from elvia.reader import prepare_reader, record_digest
from elvia.search_pages import citation


@pytest.fixture
def citation_fixture(valid_record):
    record = copy.deepcopy(valid_record)
    record["audit"] = {
        "authors": ["Fixture Author"],
        "year": 2025,
        "venue": "Synthetic conference",
        "landing_url": "https://example.org/original-landing",
    }
    row = {
        "revision": record["revision"],
        "record_sha256": record_digest(record),
        "citation": {
            "title": "Synthetic proceedings article",
            "authors": ["Author, Fixture"],
            "container": "Synthetic proceedings",
            "volume": "267",
            "publisher": "Synthetic publisher",
            "year": 2025,
            "first_page": "",
            "last_page": "",
            "doi": None,
            "source_url": "https://example.org/publisher/article.html",
        },
        "contributors": [],
    }
    catalog = {"format_version": 1, "cases": {record["case_id"]: row}}
    return record, row, catalog


def test_reader_accepts_explicit_null_doi_with_https_publisher_source(citation_fixture):
    record, row, catalog = citation_fixture
    assert prepare_reader([record], catalog)[record["case_id"]] == row
    assert row["citation"]["doi"] is None


def test_static_citation_uses_source_when_doi_is_absent(citation_fixture):
    record, row, _ = citation_fixture
    html = citation(record, row)
    assert 'href="https://example.org/publisher/article.html"' in html
    assert "Synthetic proceedings" in html
    assert "doi.org" not in html
    assert "None" not in html
    assert ", pp." not in html


def test_copied_citation_formats_use_publisher_source_without_inventing_doi(
    citation_fixture,
):
    record, row, _ = citation_fixture
    exported = original_citation(record, row)
    for text in exported.values():
        assert row["citation"]["source_url"] in text
        assert "doi.org" not in text
        assert "None" not in text
        assert record["audit"]["landing_url"] not in text
    assert "doi =" not in exported["bibtex"]
    assert "DO  -" not in exported["ris"]


def test_present_doi_retains_existing_link_and_copy_behavior(citation_fixture):
    record, row, catalog = citation_fixture
    row["citation"]["doi"] = "10.1234/fixture"
    assert prepare_reader([record], catalog)[record["case_id"]] == row
    assert 'href="https://doi.org/10.1234/fixture"' in citation(record, row)
    for text in original_citation(record, row).values():
        assert "10.1234/fixture" in text


@pytest.mark.parametrize("doi", ["", "not-a-doi", "https://doi.org/10.1234/fixture", 7])
def test_nonnull_invalid_doi_is_still_rejected(citation_fixture, doi):
    record, row, catalog = citation_fixture
    row["citation"]["doi"] = doi
    with pytest.raises(ValueError, match="DOI"):
        prepare_reader([record], catalog)


@pytest.mark.parametrize(
    "url",
    ["http://example.org/article", "javascript:alert(1)", "https://user@example.org"],
)
def test_absent_doi_does_not_relax_https_source_validation(citation_fixture, url):
    record, row, catalog = citation_fixture
    row["citation"]["source_url"] = url
    with pytest.raises(ValueError, match="HTTPS"):
        prepare_reader([record], catalog)
