"use strict";
// Original fictional claims and synthetic availability responses only.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const notes = require("../src/elvia/web/case-note.js");

class Node {
  constructor(tag) { this.tagName = tag; this.children = []; this._text = ""; this.attributes = {}; this.dataset = {}; this.className = ""; this.listeners = {}; this.classList = {add: value => { this.className += " " + value; }}; }
  set textContent(value) { this._text = value; this.children = []; }
  get textContent() { return this._text + this.children.map(node => node.textContent).join(""); }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this._text = ""; this.children = nodes; }
  setAttribute(key, value) { this.attributes[key] = value; }
  addEventListener(key, value) { this.listeners[key] = value; }
}
function create(tag, text, className) {
  const node = new Node(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
const walk = node => [node, ...node.children.flatMap(walk)];
const record = {
  case_id: "fictional-opening", revision: 2,
  source: {version: "publisher PDF v3"}, concern: {origin: "ai"},
  audit: {outcome: "candidate_issue", summary: "A bounded fictional check.", limitations: ["The final fictional theorem is not refuted."]},
  adjudication: {status: "pending"}
};
const note = {revision: 2, report: ["Abstract: A fictional inequality fails. The final theorem is not refuted."], problems: [
  {title: "First source minor finding", severity: "minor", assessment: "supported", result: ["Minor scope."]},
  {title: "Second source major finding", severity: "major", assessment: "supported", result: ["Major scope."]}
]};

test("opening groups the actual paper version, analysis revision, origin and scientific status with source prose", () => {
  const parent = create("div");
  notes.renderReaderOpening(parent, record, note, {create, prose: (tag, text, record, css) => create(tag, text, css)});
  assert.equal(parent.children[0].tagName, "details", "source metadata is available on demand");
  assert.equal(parent.children[0].className, "source-details");
  for (const value of ["publisher PDF v3", "Analysis revision", "2", "AI-origin analysis", "Independent review pending"]) assert.ok(parent.children[0].textContent.includes(value));
  assert.equal(parent.children[1].className, "reader-introduction");
  assert.ok(parent.children[1].textContent.includes(note.report[0].replace("Abstract: ", "")));
  const links = walk(parent).filter(node => node.tagName === "a");
  assert.deepEqual(links.map(node => node.href), ["#problem-2-evidence", "#supporting-evidence"]);
  assert.ok(!parent.textContent.includes("confirmed"));
  assert.ok(!parent.textContent.includes("Broader effects are not established by this summary"));
});

test("an unavailable concise abstract points to the first ordered finding without discarding full-scope access", () => {
  const source = {...note, report: []};
  const intro = notes.readerIntroduction(record, source);
  assert.equal(intro.coverage, "first_finding");
  assert.ok(intro.text.includes("Second source major finding"));
  assert.ok(intro.text.includes("Major scope."));
  assert.equal(intro.additional_findings, true);
  assert.equal(intro.evidence_fragment, "problem-2-evidence");
  const stale = notes.readerIntroduction(record, {...source, revision: 1});
  assert.ok(!stale.text.includes("Second source major finding"));
});

async function availability(result, failure = false) {
  const node = create("aside"); node.dataset.paperAvailability = record.case_id;
  const calls = [];
  const document = {createElement: create, querySelectorAll: () => [node]};
  const context = {document, window: {}, URLSearchParams, fetch: async url => {
    calls.push(url);
    if (failure) throw new Error("Synthetic failure");
    return {ok: true, json: async () => ({papers: {[record.case_id]: result}})};
  }};
  vm.runInNewContext(fs.readFileSync("website/preview/site/paper-availability.js", "utf8"), context);
  await new Promise(resolve => setImmediate(resolve));
  return {node, calls};
}

test("contribution availability stays compact and retains its exact paper route and optional details", async () => {
  const {node, calls} = await availability({status: "available", available: true, message: "Synthetic operational availability only."});
  assert.deepEqual(calls, ["/api/paper-availability"]);
  assert.equal(walk(node).filter(item => item.tagName === "h2").length, 0);
  assert.ok(node.children[0].textContent.startsWith("Contribution availability:"));
  const action = walk(node).find(item => item.tagName === "a");
  assert.equal(action.href, "/contribute.html?view=compose&case=fictional-opening");
  assert.equal(action.target, "_blank");
  const details = walk(node).find(item => item.tagName === "details");
  assert.ok(details.textContent.includes("Synthetic operational availability only."));
  assert.equal(details.open, undefined);
});

test("availability failure remains actionable without implying a scientific decision", async () => {
  const {node} = await availability(null, true);
  assert.ok(node.textContent.includes("Availability could not be loaded"));
  const retry = walk(node).find(item => item.tagName === "button");
  assert.equal(retry.textContent, "Check again");
  assert.equal(typeof retry.listeners.click, "function");
});
