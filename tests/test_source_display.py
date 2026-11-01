"""Source display keeps scientific locators while removing importer scaffolding."""

import pytest

from elvia.source_display import source_location


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (
            "Pages: 7 Pages: 8 Pages: 11 Primary: Section 2.2 "
            "Source: hf+.tex Lines: 666 Lines: 669 Lines: 674 Lines: 675",
            "Article pages: 7–8; 11; Section 2.2; hf+.tex, lines 666; 669; 674–675",
        ),
        (
            "Pdf pages: 5 Source lines: 100 Claim: Theorem 2.6",
            "Article PDF pages: 5; Theorem 2.6",
        ),
        (
            "File: semigroup.c Source code lines: 1057 Source code lines: 1152 "
            "Claim: psi_rep decides membership.",
            "semigroup.c, lines 1057; 1152; psi_rep decides membership",
        ),
        (
            "Physical pages: 5 Physical pages: 6 Printed pages: 1363 "
            "Printed pages: 1364 Labels: Theorem 1",
            "Article physical pages: 5–6; Article printed pages: 1363–1364; Theorem 1",
        ),
        (
            "Pdf page: 12 Anchor: Theorem 1 Pdf page: 18 Anchor: Lemma 3",
            "Article PDF pages: 12; Theorem 1; Article PDF pages: 18; Lemma 3",
        ),
        (
            "Pdf pages: 26 Pdf pages: 27 Reference pdf: sources/reference.pdf "
            "Reference pages: 11 Reference pages: 12",
            "Article PDF pages: 26–27; Reference PDF: sources/reference.pdf; "
            "Reference pages: 11–12",
        ),
        (
            "Supplement: extra.pdf Pdf pages: 2 Pdf pages: 8 Labels: Table S1",
            "Supplement: extra.pdf; PDF pages: 2; 8; Table S1",
        ),
        (
            "Source files: first.tex Source files: second.tex Tex lines: 12",
            "first.tex; second.tex; TeX lines: 12",
        ),
        (
            "Pdf page: 3 Source lines: 100 Unrecognized locator text",
            "Article PDF pages: 3; Unrecognized locator text",
        ),
    ],
)
def test_structured_locator_preserves_source_identity_and_scope(raw, expected):
    assert source_location(raw) == expected


def test_natural_code_locator_is_not_rewritten_as_article_text_lines():
    raw = "anc/eulerian.py lines304-318, especially316 LemmaB.23 p111"
    assert source_location(raw) == raw
