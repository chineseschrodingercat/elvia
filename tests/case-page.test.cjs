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
