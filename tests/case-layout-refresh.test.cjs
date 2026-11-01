"use strict";
// Original fictional fixtures test presentation, never scientific correctness.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const caseNotes = require("../src/elvia/web/case-note.js");

class Node {
  constructor(tag) {
    this.tagName = tag; this.ownerDocument = document;
    this.children = []; this.attributes = {}; this.className = "";
    this._text = ""; this.value = ""; this.open = false;
  }
  get textContent() { return this._text + this.children.map(node => node.textContent).join(""); }
  set textContent(value) { this._text = String(value); this.children = []; }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this._text = ""; this.children = nodes; }
  setAttribute(key, value) { this.attributes[key] = value; }
  addEventListener() {}
  focus() { this.focused = true; }
  showModal() { this.open = true; }
  close() { this.open = false; }
}
const document = {
  createElement: tag => new Node(tag),
  createTextNode: value => create("#text", value),
  createDocumentFragment: () => create("#fragment")
};
function create(tag, value, className) {
  const node = new Node(tag);
  if (value !== undefined) node.textContent = value;
  if (className) node.className = className;
  return node;
}
const walk = node => [node, ...node.children.flatMap(walk)];
const hasClass = (node, name) => node.className.split(/\s+/).includes(name);
const clone = value => JSON.parse(JSON.stringify(value));
const helpers = {
  create,
  prose: (tag, value, record, className) => create(tag, value, className),
  link: (label, href) => Object.assign(create("a", label), {href}),
  artifactURL: (record, file) => `evidence/${record.case_id}/${file}`,
  assessmentLabels: {major: "Major", minor: "Minor", needs_evidence: "Needs Evidence"}
};
const rawLocation = "Pdf pages: 29 Pdf pages: 30 Pdf pages: 31 Pdf pages: 34 " +
  "Labels: Lemma 6.3(ii) Labels: (67)-(75) Labels: Section 6.6 " +
  "Source lines: 1072 Source lines: 1178 Source lines: 1257 Source lines: 1265";
const record = {
  case_id: "layout-synthetic", revision: 1,
  source: {title: "Fictional layout fixture", version: "1", review_scope: "Synthetic claims only"},
  proposition: {claim: "Every positive rational exceeds one.", location: "Article text lines 17–19", domain: "Positive rationals", assumptions: [], dependencies: []},
  audit: {outcome: "candidate_issue", summary: "Two fictional findings.", limitations: ["Synthetic scope only."], venue: "Fictional venue", year: 2025, authors: ["Fixture Author"], landing_url: "https://example.org/fixture"},
  concern: {description: "A synthetic counterexample.", severity: "major"},
  repair: {content: "A separate case-level suggestion.", changed_assumptions: [], changed_conclusion: null},
  adjudication: {status: "pending"}, publication: {status: "preliminary_ai"},
  evidence: [{id: "ev-1", stance: "support", description: "Exact substitution.", artifact: {path: "output.txt"}}]
};
const first = {
  id: "first-source-finding", title: "The first synthetic identity fails",
  brief: ["A counterexample refutes the first synthetic identity."],
  source_location: rawLocation,
  claim: ["Every positive rational exceeds one."], assumptions: ["Let x be positive and rational."],
  analysis_heading: "Proof", method: ["Exact rational substitution."],
  analysis: ["The value one half contradicts the claim."],
  result: ["An archived scope statement, not a proposed correction."],
  severity: "major", assessment: "supported",
  repair: {heading: "Recorded suggestion", paragraphs: ["Restrict the stated claim to rational x greater than one."]}
};
const second = {...first, id: "second-source-finding", title: "The second synthetic claim needs evidence",
  brief: ["The second synthetic claim remains unresolved."],
  source_location: "Article text lines 17–19, Theorem 2", assessment: "needs_evidence",
  analysis_heading: "Verification", repair: null};
function render(source = record, note = {revision: 1, problems: [first, second]}) {
  const parent = create("div");
  caseNotes.renderProblems(parent, source, note, helpers);
  return parent;
}
function subsection(section, heading) {
  const content = walk(section).find(node => hasClass(node, "evidence-content"));
  assert.ok(content, "Evidence disclosure must exist");
  const index = content.children.findIndex(node => node.tagName === "h4" && node.textContent === heading);
  assert.notEqual(index, -1, `Missing ${heading} section`);
  const end = content.children.findIndex((node, offset) => offset > index && node.tagName === "h4");
  return content.children.slice(index + 1, end < 0 ? undefined : end).map(node => node.textContent).join(" ").trim();
}

test("Key findings is a concise summary before the problems, without a duplicate navigation panel", () => {
  const parent = render();
  const overview = parent.children.find(node => hasClass(node, "key-findings"));
  assert.ok(overview);
  assert.ok(walk(overview).some(node => node.tagName === "h2" && node.textContent === "Key findings"));
  for (const problem of [first, second]) assert.ok(overview.textContent.includes(problem.brief[0]));
  assert.equal(walk(overview).filter(node => node.tagName === "a").length, 0);
  assert.ok(parent.children.indexOf(overview) < parent.children.findIndex(node => hasClass(node, "case-problem")));
  for (const obsolete of ["In this note", "Analysis abstract", "Contribute to this note"]) assert.ok(!parent.textContent.includes(obsolete));
});

test("Sources keeps page gaps and labels while removing extraction offsets and separating the method", () => {
  const sections = walk(render()).filter(node => hasClass(node, "case-problem"));
  const sources = subsection(sections[0], "Sources");
  assert.equal(sources, "Article PDF pages: 29–31; 34; Lemma 6.3(ii); (67)-(75); Section 6.6");
  assert.ok(!sources.includes("29–34"));
  for (const hidden of ["Labels:", "Source lines:", "1072", "1178", "1257", "1265", first.method[0]]) assert.ok(!sources.includes(hidden));
  assert.ok(subsection(sections[0], "Proof").includes(first.method[0]));
  assert.equal(subsection(sections[1], "Sources"), "Article text lines 17–19, Theorem 2");
});

test("Possible revision shows only the corresponding recorded suggestion, with an explicit absent value", () => {
  const source = clone(record), note = clone({revision: 1, problems: [first, second]});
  const before = JSON.stringify([source, note]);
  const parent = render(source, note);
  const sections = walk(parent).filter(node => hasClass(node, "case-problem"));
  assert.equal(subsection(sections[0], "Possible revision"), first.repair.paragraphs[0]);
  assert.equal(subsection(sections[1], "Possible revision"), "Not available");
  assert.ok(!parent.textContent.includes(record.repair.content));
  for (const section of sections) {
    for (const obsolete of ["Detailed finding and scope", "Source and method", "Cite this analysis", "Cite the original paper", "Copy for AI", "Citation formats and full AI context", "Contribute to this finding", "Back to note overview"]) assert.ok(!section.textContent.includes(obsolete));
    assert.ok(!walk(section).some(node => node.tagName === "button" || node.attributes["data-context-key"]));
  }
  assert.equal(JSON.stringify([source, note]), before);
});

test("Supplement sources retain their identity and metadata-only locations have an honest empty fallback", () => {
  const supplement = {...first, source_location: "Supplementary PDF Pdf pages: 2 Pdf pages: 8 Labels: Table S1 Source lines: 201"};
  const internalOnly = {...second, source_location: "Source lines: 1072 Source lines: 1178"};
  const sections = walk(render(record, {revision: 1, problems: [supplement, internalOnly]})).filter(node => hasClass(node, "case-problem"));
  const sources = subsection(sections[0], "Sources");
  assert.match(sources, /Supplementary PDF/);
  assert.match(sources, /\b2\b/); assert.match(sources, /\b8\b/);
  assert.match(sources, /Table S1/); assert.match(sources, /;/);
  assert.ok(!sources.includes("Article PDF") && !sources.includes("2–8") && !sources.includes("201"));
  assert.equal(subsection(sections[1], "Sources"), "Not available");
});

test("No-issue and scope-only records preserve the summary without inventing a problem or revision", () => {
  for (const outcome of ["no_issue_found", "scope_clarification"]) {
    const source = clone(record); source.audit.outcome = outcome;
    const note = {revision: 1, brief: ["The report records only the inspected synthetic scope."], problems: [first]};
    const parent = render(source, note);
    const nodes = walk(parent);
    assert.ok(nodes.some(node => node.tagName === "h2" && node.textContent === "Key findings"));
    assert.ok(parent.textContent.includes(note.brief[0]));
    assert.ok(nodes.some(node => node.tagName === "h4" && node.textContent === "Review scope"));
    assert.ok(!nodes.some(node => hasClass(node, "case-problem")));
    assert.ok(!parent.textContent.includes("Possible revision") && !parent.textContent.includes(first.title));
  }
});

test("Both opened Atlas views group the real review status with severity", () => {
  for (const relative of ["src/elvia/web/atlas.js", "website/atlas-assets/atlas.js"]) {
    for (const [status, label] of [["pending", "Independent review pending"], ["confirmed", "Confirmed"]]) {
    const elements = new Map();
    const get = id => { if (!elements.has(id)) elements.set(id, create("div")); return elements.get(id); };
    const source = clone(record);
    source.adjudication.status = status;
    vm.runInNewContext(fs.readFileSync(path.join(__dirname, "..", relative), "utf8"), {
      document: {...document, getElementById: get, querySelectorAll: () => []},
      window: {
        ELVIA_DATA: {records: [source], case_notes: {[source.case_id]: {revision: 1, problems: [first, second]}}},
        ELVIA_CASE_NOTES: caseNotes,
        ELVIA_ASSESSMENT: {sortByTitle: records => records, labels: helpers.assessmentLabels,
          assessment: () => ({key: "major", label: "Major"})},
        addEventListener() {}
      },
      location: {search: "", hash: "#case=" + source.case_id},
      history: {replaceState() {}, pushState() {}}, URL, URLSearchParams
    });
    const badgeGroup = walk(get("detail-content")).find(node => hasClass(node, "case-badges"));
    assert.ok(badgeGroup, relative);
    assert.ok(walk(badgeGroup).some(node => hasClass(node, "severity-tag") && node.textContent === "Major"));
    assert.ok(walk(badgeGroup).some(node => hasClass(node, "review-status-tag") && node.textContent === label));
    }
  }
});
