"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const {createIndex, normalize} = require("../src/elvia/web/search.js");
const root = path.resolve(__dirname, "..");
const directory = path.join(root, "studies/neurips2025/records");
const records = fs.readdirSync(directory).filter(name => name.endsWith(".json"))
  .map(name => JSON.parse(fs.readFileSync(path.join(directory, name), "utf8")));
const caseNotes = JSON.parse(fs.readFileSync(path.join(root, "studies/neurips2025/case-notes.json"), "utf8")).cases;
const index = createIndex(records, {caseNotes});
const conformal = "neurips2025-0016-accelerating-feature-conformal-prediction-via-taylor-approximat";

test("a research question finds the relevant calibration finding with traceable matches", () => {
  const results = index.search("Does pooling calibration scores preserve coverage?");
  assert.equal(results[0].record.case_id, conformal);
  assert.ok(results.length < records.length / 10, "generic overlap must not match the whole collection");
  assert.ok(results[0].matchedTerms.includes("pooling"));
  assert.ok(results[0].matchedTerms.includes("calibration"));
  assert.ok(results[0].problemIndex > 0);
  assert.match(results[0].explanation, /Matched/);
});

test("curated word variants retrieve the same scientific topic without an exact sentence", () => {
  assert.equal(index.search("Can pooled calibration scores maintain coverage?")[0].record.case_id, conformal);
  assert.equal(index.search("calibration pool coverage")[0].record.case_id, conformal);
});

test("scientific inflections retain the central interpolation terms in a natural question", () => {
  const results = index.search("Does bilinear interpolation average entire patches?");
  assert.equal(results[0].record.case_id, "neurips2025-0169-4d-vla-spatiotemporal-vision-language-action-pretraining-with-c");
  assert.equal(results[0].problemIndex, 1);
});

test("Unicode punctuation and case normalize while source record text stays untouched", () => {
  assert.equal(normalize("  ＤFloat11 — LOSSLESS / compression?  "), "dfloat11 lossless compression");
  const before = JSON.stringify(records);
  assert.ok(index.search("DFLOAT11: lossless compression!")[0].record.source.title.includes("Lossless"));
  assert.equal(JSON.stringify(records), before);
});

test("identifiers are searchable despite punctuation and DOI URL prefixes", () => {
  const record = records.find(item => item.case_id === conformal);
  const local = createIndex([record], {reader: {[record.case_id]: {revision: record.revision, citation: {doi: "10.1234/EXAMPLE.42"}}}});
  assert.equal(local.search("https://doi.org/10.1234/example.42")[0].record, record);
  assert.equal(local.search(record.case_id.replaceAll("-", " "))[0].record, record);
});

test("unrelated specific terms cannot match only a generic coverage word", () => {
  assert.equal(index.search("galactic banana coverage").length, 0);
  assert.equal(index.search("quantum banana").length, 0);
  assert.equal(index.search("zzzzzunmatched").length, 0);
});

test("empty input lists records while a question without searchable terms gives no matches", () => {
  assert.equal(index.search("  ").length, records.length);
  assert.equal(index.search("how can I do this?").length, 0);
  assert.equal(index.search("???").length, 0);
});

test("stale case notes and reader metadata never influence a current record match", () => {
  const record = records[0];
  const local = createIndex([record], {caseNotes: {[record.case_id]: {revision: record.revision + 1, problems: [{title: "phantomzzzzz", analysis: ["ghostzzzzz"]}]}}, reader: {[record.case_id]: {revision: record.revision + 1, citation: {doi: "10.1234/phantomzzzzz"}}}});
  assert.equal(local.search("phantomzzzzz").length, 0);
  assert.equal(local.search("ghostzzzzz").length, 0);
});

test("a report-only no-issue fixture remains searchable through its complete retained report", () => {
  const record = {
    case_id: "synthetic-report-only", revision: 1,
    source: {title: "Fictional report-only case", version: "Synthetic fixture"},
    audit: {venue: "Synthetic venue", outcome: "no_issue_found", authors: ["Fictional author"],
      summary: "Synthetic format check only.", limitations: ["Software fixture, no research conclusion."]},
    proposition: {claim: "Original synthetic scoped statement."}
  };
  const note = {revision: 1, report: ["A synthetic metagovernance passage remains available in full."]};
  const local = createIndex([record], {caseNotes: {[record.case_id]: note}});
  const found = local.search("metagovernance");
  assert.equal(found.length, 1);
  assert.equal(found[0].record, record);
  assert.equal(found[0].problemIndex, 0, "a retained report match must not invent a numbered finding");
  assert.match(found[0].explanation, /complete retained report/);
  const stale = createIndex([record], {caseNotes: {[record.case_id]: {...note, revision: 2}}});
  assert.equal(stale.search("metagovernance").length, 0);
});

test("a finding's body is searchable and links to its real position", () => {
  const record = records[0];
  const local = createIndex([record], {caseNotes: {[record.case_id]: {revision: record.revision,
    report: ["packedgapzzzzz boundaryzzzzz ".repeat(1000)],
    problems: [{title: "First finding"}, {title: "Tail access", analysis: ["packedgapzzzzz boundaryzzzzz"]}]}}});
  const found = local.search("packedgapzzzzz boundaryzzzzz")[0];
  assert.equal(found.problemIndex, 2);
  assert.equal(found.problemTitle, "Tail access");
  assert.ok(found.explanation.includes("Problem 2"));
});

test("severity-sorted search labels use display numbers and keep canonical finding positions", () => {
  const record = records[0];
  const note = {revision: record.revision, problems: [
    {id: "minor-first", title: "A local calculation", severity: "minor", analysis: ["localcalculationzzzzz"]},
    {id: "major-second", title: "A central counterexample", severity: "major", analysis: ["centralcounterexamplezzzzz"]},
    {id: "not-a-problem", title: "A surviving claim", assessment: "not_issue", severity: "major", analysis: ["notaproblemzzzzz"]}
  ]};
  const before = JSON.stringify(note);
  const local = createIndex([record], {caseNotes: {[record.case_id]: note}});
  const major = local.search("centralcounterexamplezzzzz")[0];
  assert.equal(major.problemIndex, 2);
  assert.equal(major.problemDisplayNumber, 1);
  assert.match(major.explanation, /Closest section: Problem 1\./);
  const minor = local.search("localcalculationzzzzz")[0];
  assert.equal(minor.problemIndex, 1);
  assert.equal(minor.problemDisplayNumber, 2);
  assert.equal(local.search("notaproblemzzzzz").length, 0);
  assert.equal(JSON.stringify(note), before);
});

test("ranking is deterministic and exact titles outrank incidental long-body mentions", () => {
  const first = structuredClone(records[0]);
  const second = structuredClone(records[0]);
  first.case_id = "first"; first.source.title = "Calibration coverage";
  second.case_id = "second"; second.source.title = "Other result";
  const local = createIndex([second, first], {caseNotes: {second: {revision: second.revision, problems: [{title: "Related material", analysis: ["calibration coverage ".repeat(1000)]}]}}});
  assert.equal(local.search("calibration coverage")[0].record.case_id, "first");
  assert.deepEqual(local.search("calibration coverage").map(item => item.record.case_id), local.search("calibration coverage").map(item => item.record.case_id));
});
