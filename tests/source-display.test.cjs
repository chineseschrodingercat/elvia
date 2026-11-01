"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const {sourceLocation} = require("../src/elvia/web/case-note.js");

test("generic article pages and a dotted TeX filename retain their actual identities", () => {
  assert.equal(sourceLocation("Pages: 7 Pages: 8 Pages: 11 Primary: Section 2.2 " +
    "Source: hf+.tex Lines: 666 Lines: 669 Lines: 674 Lines: 675"),
  "Article pages: 7–8; 11; Section 2.2; hf+.tex, lines 666; 669; 674–675");
});

test("removing an unbound extraction offset does not discard a following claim", () => {
  assert.equal(sourceLocation("Pdf pages: 5 Source lines: 100 Claim: Theorem 2.6"),
    "Article PDF pages: 5; Theorem 2.6");
});

test("named code locations keep their actual line references", () => {
  assert.equal(sourceLocation("File: semigroup.c Source code lines: 1057 " +
    "Source code lines: 1152 Claim: psi_rep decides membership."),
  "semigroup.c, lines 1057; 1152; psi_rep decides membership");
});

test("successive page and anchor groups keep their recorded association", () => {
  assert.equal(sourceLocation("Pdf page: 12 Anchor: Theorem 1 Pdf page: 18 Anchor: Lemma 3"),
    "Article PDF pages: 12; Theorem 1; Article PDF pages: 18; Lemma 3");
});

test("separate references and supplements are not assigned article page numbers", () => {
  assert.equal(sourceLocation("Pdf pages: 26 Pdf pages: 27 Reference pdf: sources/reference.pdf " +
    "Reference pages: 11 Reference pages: 12"),
  "Article PDF pages: 26–27; Reference PDF: sources/reference.pdf; Reference pages: 11–12");
  assert.equal(sourceLocation("Supplement: extra.pdf Pdf pages: 2 Pdf pages: 8 Labels: Table S1"),
    "Supplement: extra.pdf; PDF pages: 2; 8; Table S1");
});

test("a flat filename array cannot assign its later line list to the last file", () => {
  assert.equal(sourceLocation("Source files: first.tex Source files: second.tex Tex lines: 12"),
    "first.tex; second.tex; TeX lines: 12");
});
