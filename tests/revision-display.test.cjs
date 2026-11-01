"use strict";
const assert = require("node:assert/strict");
const test = require("node:test");
const {possibleRevision} = require("../src/elvia/web/case-note.js");

test("an explicit report proposal takes priority and does not repeat review boilerplate", () => {
  const suggestion = "Restrict the displayed claim to positive inputs.";
  const problem = {repair: {paragraphs: [
    suggestion,
    "A proposed correction is retained where stated; independent verification and author adoption remain unestablished."
  ]}, analysis: ["The corrected local formula is y = 2x."], result: []};
  assert.deepEqual(possibleRevision(problem), [suggestion]);
});

test("an explicit proposal embedded in the same problem retains its full scope", () => {
  for (const text of [
    "Changing the cutoff is a plausible local repair. This does not establish the global theorem.",
    "Repair and counterevidence. Restrict the claim to finite cubes. No complete repair is claimed.",
    "The corrected local formula is y = 2x, rather than y = x."
  ]) assert.deepEqual(possibleRevision({analysis: [text], result: []}), [text]);
});

test("negated fixes and unspecified future tasks do not become proposed revisions", () => {
  for (const text of [
    "Changing the normalization cannot repair the equation.",
    "Removing the empty words alone does not repair the identity.",
    "The report does not claim that adding an assumption repairs the theorem.",
    "A complete repair requires rechecking every estimate and proving the theorem.",
    "A repair must state a defensible loss/class restriction and rederive constants.",
    "The specification must be corrected. There is no uniquely justified repair."
  ]) assert.deepEqual(possibleRevision({analysis: [text], result: []}), [], text);
});

test("an explicitly introduced revision list retains its options and boundaries", () => {
  const result = [
    "Three definitions remove the demonstrated obstruction:",
    "1. Use the unoriented quotient.",
    "2. Assign the averaged measure.",
    "3. Count oriented curves with their actual stabilizer.",
    "The second formulation requires the stated qualification.",
    "These local repairs are verified; a full convergence theorem is not claimed.",
    "Recorded evidence: The existing counterexample remains."
  ];
  assert.deepEqual(possibleRevision({analysis: [], result}), result.slice(0, 6));
});
