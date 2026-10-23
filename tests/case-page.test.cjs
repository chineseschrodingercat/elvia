"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

class Node {
  constructor(dataset = {}) { this.dataset = dataset; this.hidden = true; this.listeners = {}; this.value = "analysis-plain"; this.textContent = ""; }
  addEventListener(name, handler) { this.listeners[name] = handler; }
  focus() { this.focused = true; }
  select() { this.selected = true; }
}

function fixture(clipboard) {
  const nodes = Object.fromEntries(["[data-copy-format]", "[data-copy-text]", ".copy-status", ".copy-options", "[data-copy-selected]"].map(key => [key, new Node()]));
  const buttons = ["analysis-plain", "original-plain", "ai-short"].map(copyMode => new Node({copyMode}));
  const section = {dataset: {contextKey: "problem-2"}, querySelector: key => nodes[key],
    querySelectorAll: key => key === "[data-copy-mode]" ? buttons : [...buttons, nodes["[data-copy-selected]"], nodes["[data-copy-format]"]]};
  const context = {"problem-2": {"analysis-plain": "Analysis 2; pending", "original-plain": "Original paper author", "ai-short": "Problem 2; bounded; pending", "ai-full": "Problem 2 complete evidence and scope"}};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, "../src/elvia/web/case-page.js"), "utf8"), {
    window: {ELVIA_CASE_CONTEXT: context, ELVIA_MATH: {renderInto() {}}}, navigator: {clipboard},
    document: {querySelectorAll: selector => selector === "[data-context-key]" ? [section] : []}
  });
  return {nodes, buttons};
}

test("one click copies the selected finding only, and reports its content type", async () => {
  const copied = [];
  const {nodes, buttons} = fixture({writeText: async text => copied.push(text)});
  assert.equal(buttons[2].hidden, false);
  await buttons[2].listeners.click();
  assert.deepEqual(copied, ["Problem 2; bounded; pending"]);
  assert.match(nodes[".copy-status"].textContent, /AI context.*copied/i);
  assert.equal(nodes["[data-copy-format]"].value, "ai-short");
});

test("permission denial opens a selected manual fallback without claiming success", async () => {
  const {nodes, buttons} = fixture({writeText: async () => { throw Error("denied"); }});
  await buttons[0].listeners.click();
  assert.equal(nodes[".copy-options"].open, true);
  assert.equal(nodes["[data-copy-text]"].focused, true);
  assert.equal(nodes["[data-copy-text]"].selected, true);
  assert.equal(nodes["[data-copy-text]"].value, "Analysis 2; pending");
  assert.match(nodes[".copy-status"].textContent, /select|selected/i);
  assert.doesNotMatch(nodes[".copy-status"].textContent, /copied/i);
});

test("full context selector and unsupported clipboard retain manual copy", async () => {
  const {nodes} = fixture(undefined);
  nodes["[data-copy-format]"].value = "ai-full";
  nodes["[data-copy-format]"].listeners.change();
  assert.equal(nodes["[data-copy-text]"].value, "Problem 2 complete evidence and scope");
  await nodes["[data-copy-selected]"].listeners.click();
  assert.equal(nodes["[data-copy-text]"].selected, true);
  assert.match(nodes[".copy-status"].textContent, /Ctrl|copy/i);
});

function disclosureFixture(hash) {
  const events = {};
  const outer = {tagName: "DETAILS", open: false, parentElement: null};
  const inner = {tagName: "DETAILS", open: false, parentElement: outer};
  const alreadyOpen = {tagName: "DETAILS", open: true, parentElement: null};
  const target = {tagName: "H4", parentElement: inner, scrollIntoView() { this.scrolled = true; }};
  const location = {hash};
  const ids = {"problem-2-analysis": target, "problem-2-evidence": inner};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, "../src/elvia/web/case-page.js"), "utf8"), {
    window: {ELVIA_MATH: {renderInto() {}}, location, addEventListener: (event, callback) => { events[event] = callback; }},
    document: {getElementById: id => ids[id] || null,
      querySelectorAll: selector => selector === "details.evidence-details" ? [outer, inner, alreadyOpen] : []}
  });
  return {events, outer, inner, alreadyOpen, target, location};
}

test("a deep link opens its evidence ancestors without losing the target", () => {
  const {outer, inner, alreadyOpen, target} = disclosureFixture("#problem-2-analysis");
  assert.equal(outer.open, true);
  assert.equal(inner.open, true);
  assert.equal(alreadyOpen.open, true);
  assert.equal(target.scrolled, true);
});

test("unknown and malformed fragments do not expand evidence; later hash navigation does", () => {
  for (const hash of ["", "#missing", "#%E0%A4%A"]) {
    const {events, outer, inner, location, target} = disclosureFixture(hash);
    assert.equal(outer.open, false);
    assert.equal(inner.open, false);
    location.hash = "#problem-2-analysis";
    events.hashchange();
    assert.equal(inner.open, true);
    assert.equal(target.scrolled, true);
  }
});

test("printing reveals every evidence block then restores the reader's expanded state", () => {
  const {events, outer, inner, alreadyOpen} = disclosureFixture("");
  events.beforeprint();
  events.beforeprint(); // Browsers may signal print setup more than once.
  assert.equal(outer.open, true);
  assert.equal(inner.open, true);
  assert.equal(alreadyOpen.open, true);
  events.afterprint();
  assert.equal(outer.open, false);
  assert.equal(inner.open, false);
  assert.equal(alreadyOpen.open, true);
  inner.open = true;
  events.beforeprint();
  events.afterprint();
  assert.equal(outer.open, false);
  assert.equal(inner.open, true);
});
