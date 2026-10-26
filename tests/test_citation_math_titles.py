"""Synthetic citation titles retain their own exact math-presentation node."""

from html.parser import HTMLParser

import pytest

from elvia.search_pages import citation


class CitationText(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.spans = []
        self.text = []
        self.active = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == "span" and "data-case-prose" in dict(attrs):
            self.active = []

    def handle_endtag(self, tag):
        if tag == "span" and self.active is not None:
            self.spans.append("".join(self.active))
            self.active = None

    def handle_data(self, text):
        self.text.append(text)
        if self.active is not None:
            self.active.append(text)


@pytest.mark.parametrize("doi", [None, "10.1234/fixture"])
def test_title_alone_matches_notation_sidecar_without_changing_mla_punctuation(doi):
    title = r"A Synthetic $\ell_2$ Mechanism"
    reader = {
        "citation": {
            "title": title,
            "authors": ["Author, Fixture"],
            "container": "Synthetic proceedings",
            "volume": "267",
            "year": 2025,
            "first_page": "1",
            "last_page": "2",
            "doi": doi,
            "source_url": "https://example.org/publisher",
        }
    }
    page = CitationText(citation({}, reader))
    assert page.spans.count(title) == 1
    text = "".join(page.text)
    assert (
        f"Author, Fixture. “{title}.” Synthetic proceedings, vol. 267, 2025, pp. 1–2, "
        in text
    )
    assert (
        "https://doi.org/" + doi if doi else "https://example.org/publisher"
    ) in text


def test_existing_title_punctuation_stays_in_title_node():
    title = r"Does $x=1$ Hold?"
    reader = {
        "citation": {
            "title": title,
            "authors": ["Fixture Author"],
            "container": "Fixture",
            "volume": "1",
            "year": 2025,
            "doi": None,
            "source_url": "https://example.org/publisher",
        }
    }
    page = CitationText(citation({}, reader))
    assert title in page.spans
    assert f"“{title}”" in "".join(page.text)
    assert "?." not in "".join(page.text)


def test_record_fallback_title_also_has_its_own_exact_prose_span(valid_record):
    valid_record["source"]["title"] = r"Synthetic $\mathcal{W}_2$ Title"
    valid_record["audit"] = {
        "authors": ["Original Author"],
        "venue": "Fixture venue",
        "year": 2025,
        "landing_url": "https://example.org/paper",
    }
    page = CitationText(citation(valid_record, {}))
    assert valid_record["source"]["title"] in page.spans
