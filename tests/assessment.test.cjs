"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const {assessment, sortByTitle} = require("../src/elvia/web/assessment.js");

test("uncertain and no-issue outcomes override required legacy severity", () => {
  for (const [outcome, expected] of [["needs_evidence", "Needs Evidence"], ["no_issue_found", "No Issue Found"], ["scope_clarification", "No Issue Found"]]) {
    assert.equal(assessment({audit: {outcome}, concern: {severity: "major"}}).label, expected);
  }
  for (const [severity, label] of [["minor", "Minor"], ["moderate", "Minor"], ["major", "Major"], ["critical", "Major"]]) {
    assert.equal(assessment({audit: {outcome: "candidate_issue"}, concern: {severity}}).label, label);
  }
});

test("title ordering is deterministic and does not mutate authoritative order", () => {
  const input = ["Zeta", "alpha 10", "Alpha 2"].map((title, i) => ({case_id: String(i), source: {title}}));
  const ordered = sortByTitle(input);
  assert.deepEqual(ordered.map(r => r.source.title), ["Alpha 2", "alpha 10", "Zeta"]);
  assert.equal(input[0].source.title, "Zeta");
});
