"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const {createHash} = require("node:crypto");
const {spawnSync} = require("node:child_process");
const checker = path.resolve(__dirname, "../scripts/check_review_notes.cjs");
function inspect(text) {
  const folder = fs.mkdtempSync(path.join(os.tmpdir(), "elvia-prose-"));
  try {
    fs.writeFileSync(path.join(folder, "0001.json"), JSON.stringify({problems: [{analysis: [text]}]}));
    return spawnSync(process.execPath, [checker, folder], {encoding: "utf8"});
  } finally { fs.rmSync(folder, {recursive: true}); }
}
test("screenshot regressions detect unmarked algebra and cramped quantitative prose", () => {
  for (const text of [
    "The gradient-flow invariant is gamma=a²-b1²-b2²; q=a_infinity²=(gamma+sqrt(gamma²+4))/2.",
    "Two groups of lengths32 and288 yield losses-.1707128 versus-.1260209."
  ]) {
    const result = inspect(text);
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stderr, /unmarked mathematics|cramped word\/number/);
  }
});
test("double-escaped delimiters cannot silently pass as ordinary prose", () => {
  const result = inspect(String.raw`The value is \\(x=1\\).`);
  assert.equal(result.status, 1, result.stdout + result.stderr);
  assert.match(result.stderr, /escaped math delimiter/);
});
test("the proof cannot depend on internal validation and backup files", () => {
  const result = inspect("Our verification/0059/output.json contains the counterexample; see the retained local bundle.");
  assert.equal(result.status, 1, result.stdout + result.stderr);
  assert.match(result.stderr, /internal evidence reference/);
});
test("typeset quantitative prose and ordinary source citations remain valid", () => {
  const result = inspect(String.raw`The two groups have lengths \(32\) and \(288\), with losses \(-0.1707128\) and \(-0.1260209\). See Theorem 1, Section 3.2, Table 12 and the authors' loss.py.`);
  assert.equal(result.status, 0, result.stdout + result.stderr);
});

test("an accidentally interpreted escape cannot hide a corrupted math operator", () => {
  const result = inspect("The value is \u0007pprox one.");
  assert.equal(result.status, 1, result.stdout + result.stderr);
  assert.match(result.stderr, /control or replacement character/);
});

function withCollection(callback) {
  const workspace = fs.mkdtempSync(path.join(os.tmpdir(), "elvia-latest-prose-"));
  const root = path.join(workspace, "dataset");
  fs.mkdirSync(path.join(root, "records"), {recursive: true});
  fs.writeFileSync(path.join(root, "case-notes.json"), JSON.stringify({format_version: 1, cases: {}}));
  const verification = () => ({
    report_id: "0001", title: "Original title with β", version: "Original β version",
    provenance_note: "Original γ provenance", source_checks: [{note: "Original gamma=a² source note."}],
    summary: "A bounded scope clarification.", review_scope: "A synthetic scope.", limitations: [],
    impact_rationale: "No supported paper error.",
    problems: [{id: "p1", title: "A scoped condition", source_location: "Section 1",
      claim: ["A bounded claim."], analysis: [String.raw`The value is \(x=1\).`],
      result: ["A bounded finding."], assumptions: [], repair: null,
      impact_rationale: "The core claim survives.", existing_correction_status: "No paper repair required."}]
  });
  function writeRevision(revision, audit) {
    const relative = `evidence/fixture/r${revision}/verification.json`;
    const bytes = Buffer.from(JSON.stringify(audit));
    const filename = path.join(root, relative);
    fs.mkdirSync(path.dirname(filename), {recursive: true});
    fs.writeFileSync(filename, bytes);
    const record = {
      case_id: "fixture", revision,
      audit: {outcome: "scope_clarification", summary: "A bounded finding.", limitations: []},
      source: {review_scope: "A synthetic scope."},
      proposition: {claim: "A bounded claim.", domain: "Synthetic.", assumptions: [], location: "Section 1"},
      concern: {description: "A bounded concern."}, repair: {content: null},
      evidence: [{id: "scope-and-rebuttal", description: "A scope note.", method: "Synthetic check.",
        artifact: {path: relative, sha256: createHash("sha256").update(bytes).digest("hex")}}]
    };
    const recordPath = path.join(root, "records", `fixture.r${revision}.json`);
    const save = () => fs.writeFileSync(recordPath, JSON.stringify(record));
    save();
    return {record, save, filename};
  }
  const run = () => spawnSync(process.execPath, [checker, path.join(root, "records")], {encoding: "utf8"});
  try { callback({root, workspace, verification, writeRevision, run}); }
  finally { fs.rmSync(workspace, {recursive: true}); }
}

test("latest downloadable scientific arguments are checked without a curated case note", () => {
  for (const field of ["analysis", "paperImpact", "problemImpact", "correctionStatus"]) {
    withCollection(({verification, writeRevision, run}) => {
      const audit = verification();
      const rawMath = "The invariant is gamma=a²-b1²-b2².";
      if (field === "analysis") audit.problems[0].analysis = [rawMath];
      else if (field === "paperImpact") audit.impact_rationale = rawMath;
      else if (field === "problemImpact") audit.problems[0].impact_rationale = rawMath;
      else audit.problems[0].existing_correction_status = rawMath;
      writeRevision(2, audit);
      const result = run();
      assert.equal(result.status, 1, field + ": " + result.stdout + result.stderr);
      assert.match(result.stderr, /unmarked mathematics/);
    });
  }
});

test("only latest verification is checked while predecessor bytes and metadata stay literal", () => {
  withCollection(({verification, writeRevision, run}) => {
    const old = verification();
    old.problems[0].analysis = ["Historical gamma=a²-b1²-b2² remains unchanged."];
    const predecessor = writeRevision(1, old);
    predecessor.record.audit.summary = "Historical gamma=a².";
    predecessor.record.evidence[0].artifact.sha256 = "0".repeat(64);
    predecessor.save();
    const oldBytes = fs.readFileSync(predecessor.filename);
    writeRevision(2, verification());
    const result = run();
    assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.deepEqual(fs.readFileSync(predecessor.filename), oldBytes);
  });
});

test("verification bytes must match their declared hash before JSON or prose inspection", () => {
  withCollection(({verification, writeRevision, run}) => {
    const latest = writeRevision(2, verification());
    fs.writeFileSync(latest.filename, "Changed bytes that are not JSON.");
    const result = run();
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stderr, /verification artifact hash mismatch/);
    assert.doesNotMatch(result.stderr, /Unexpected token|not valid JSON/);
  });
});

test("verification references must be portable paths contained in the dataset", () => {
  for (const reference of ["../outside/verification.json", "..\\outside\\verification.json", "/outside/verification.json", "C:/outside/verification.json"]) {
    withCollection(({verification, writeRevision, run}) => {
      const latest = writeRevision(2, verification());
      latest.record.evidence[0].artifact.path = reference;
      latest.save();
      const result = run();
      assert.equal(result.status, 1, reference + ": " + result.stdout + result.stderr);
      assert.match(result.stderr, /verification artifact path/);
    });
  }
});

test("an internal verification reference cannot follow a directory link outside the dataset", t => {
  withCollection(({root, workspace, verification, writeRevision, run}) => {
    const latest = writeRevision(2, verification());
    const outside = path.join(workspace, "outside");
    fs.mkdirSync(outside);
    fs.copyFileSync(latest.filename, path.join(outside, "verification.json"));
    const linked = path.join(root, "evidence", "linked");
    try { fs.symlinkSync(outside, linked, "junction"); }
    catch (error) {
      if (["EPERM", "EACCES"].includes(error.code)) { t.skip("Directory links unavailable on this host."); return; }
      throw error;
    }
    latest.record.evidence[0].artifact.path = "evidence/linked/verification.json";
    latest.save();
    const result = run();
    assert.equal(result.status, 1, result.stdout + result.stderr);
    assert.match(result.stderr, /verification artifact path escapes/);
  });
});
