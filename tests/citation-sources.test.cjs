"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..");
const fixtureName = fs.readdirSync(path.join(root, "studies/neurips2025/records")).find(name => name.endsWith(".json"));
const original = JSON.parse(fs.readFileSync(path.join(root, "studies/neurips2025/records", fixtureName), "utf8"));

function citationNode(scriptPath, doi) {
  const record = structuredClone(original);
  record.case_id = "synthetic-citation";
  class Node {
    constructor(tag) { this.tagName = tag; this.children = []; this.attributes = {}; this._text = ""; this.value = ""; this.open = false; }
    get textContent() { return this._text + this.children.map(node => node.textContent).join(""); }
    set textContent(value) { this._text = value; this.children = []; }
    append(...nodes) { this.children.push(...nodes); }
    replaceChildren(...nodes) { this._text = ""; this.children = nodes; }
    setAttribute(key, value) { this.attributes[key] = value; }
    addEventListener() {}
    focus() {}
    showModal() { this.open = true; }
  }
  const elements = new Map();
  const get = id => {
    if (!elements.has(id)) elements.set(id, new Node("div"));
    return elements.get(id);
  };
  const row = {revision: record.revision, citation: {
    title: "Synthetic article", authors: ["Fixture, Author"], container: "Synthetic proceedings",
    volume: "267", publisher: "Fixture Publisher", year: 2025, first_page: "", last_page: "",
    doi, source_url: "https://example.org/publisher/article.html"
  }};
  vm.runInNewContext(fs.readFileSync(path.join(root, scriptPath), "utf8"), {
    document: {getElementById: get, createElement: tag => new Node(tag), querySelectorAll: () => []},
    window: {ELVIA_DATA: {records: [record], reader: {[record.case_id]: row}},
      ELVIA_CASE_NOTES: {renderProblems() {}}, ELVIA_ASSESSMENT: require("../src/elvia/web/assessment.js"), addEventListener() {}},
    location: {hash: "#case=" + record.case_id, search: ""},
    history: {pushState() {}, replaceState() {}}, URL, URLSearchParams
  });
  return get("detail-content").children.find(node => node.className === "detail-citation");
}

test("both Atlas citation views use publisher URL for null DOI and retain actual DOI links", () => {
  for (const script of ["src/elvia/web/atlas.js", "website/atlas-assets/atlas.js"]) {
    const absent = citationNode(script, null);
    assert.ok(absent.children.some(node => node.href === "https://example.org/publisher/article.html"), script);
    assert.ok(!absent.children.some(node => node.href && node.href.includes("doi.org")), script);
    assert.doesNotMatch(absent.textContent, /null|undefined/);
    const present = citationNode(script, "10.1234/fixture");
    assert.ok(present.children.some(node => node.href === "https://doi.org/10.1234/fixture"), script);
  }
});
