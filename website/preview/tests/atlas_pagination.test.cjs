"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const formal = path.resolve(__dirname, "../../..");
const web = path.join(formal, "website/atlas-assets");
const script = fs.readFileSync(path.join(web, "atlas.js"), "utf8");
const html = fs.readFileSync(path.join(web, "index.html"), "utf8");
const fixtureName = fs.readdirSync(path.join(formal, "studies/neurips2025/records")).find(name => name.endsWith(".json"));
const original = JSON.parse(fs.readFileSync(path.join(formal, "studies/neurips2025/records", fixtureName), "utf8"));

function openAtlas(hash = "", search = "") {
  const records = Array.from({length: 27}, (_, index) => {
    const number = index + 1;
    const record = structuredClone(original);
    record.case_id = "pagination-fixture-" + number;
    record.source.title = "Paper " + String(number).padStart(2, "0");
    record.audit.venue = number % 2 ? "Venue A" : "Venue B";
    record.audit.outcome = number % 3 ? "candidate_issue" : "scope_clarification";
    record.concern.severity = number % 2 ? "critical" : "moderate";
    return record;
  });
  class Node {
    constructor(tag) { this.tagName = tag; this.children = []; this.attributes = {}; this.className = ""; this._text = ""; this.value = ""; this.listeners = {}; this.open = false; this.disabled = false; }
    get textContent() { return this._text + this.children.map(node => node.textContent).join(""); }
    set textContent(value) { this._text = value; this.children = []; }
    append(...nodes) { this.children.push(...nodes); }
    replaceChildren(...nodes) { this._text = ""; this.children = nodes; }
    setAttribute(key, value) { this.attributes[key] = value; }
    addEventListener(name, listener) { this.listeners[name] = listener; }
    focus() { this.focused = true; }
    showModal() { this.open = true; }
    close() { this.open = false; }
  }
  const elements = new Map();
  const get = id => {
    if (!elements.has(id)) elements.set(id, new Node("div"));
    return elements.get(id);
  };
  const document = {getElementById: get, createElement: tag => new Node(tag), querySelectorAll: () => []};
  get("page-size").value = "10";
  const location = {hash, search};
  const events = {};
  vm.runInNewContext(script, {
    document,
    window: {ELVIA_DATA: {records, case_notes: {}}, ELVIA_CASE_NOTES: require(path.join(formal, "src/elvia/web/case-note.js")), ELVIA_ASSESSMENT: require(path.join(formal, "src/elvia/web/assessment.js")), addEventListener: (name, listener) => { events[name] = listener; }},
    location, history: {pushState(_state, _unused, value) { location.hash = value; }, replaceState(_state, _unused, value) { location.hash = value; }}, URL, URLSearchParams
  });
  const event = (id, type, value) => {
    if (value !== undefined) get(id).value = value;
    assert.equal(typeof get(id).listeners[type], "function", `${id} has a ${type} handler`);
    get(id).listeners[type]();
  };
  return {get, event, location, events, rows: () => get("case-list").children};
}

test("page-size is a labeled native select with only 5, 10, 15, 20 and default 10", () => {
  const select = html.match(/<select\b[^>]*id="page-size"[^>]*>([\s\S]*?)<\/select>/);
  assert.ok(select, "page-size select must exist");
  assert.deepEqual([...select[1].matchAll(/<option\b([^>]*)>(\d+)<\/option>/g)].map(([, attributes, text]) => [text, /\bselected\b/.test(attributes)]), [["5", false], ["10", true], ["15", false], ["20", false]]);
  assert.match(html, /<label\b[^>]*>[\s\S]*?Records per page[\s\S]*?<select\b[^>]*id="page-size"/);
});

test("actual Atlas defaults to 10 rows with range, page count and disabled previous controls", () => {
  const atlas = openAtlas();
  assert.equal(atlas.rows().length, 10);
  assert.equal(atlas.get("result-count").textContent, "1–10 of 27 cases shown");
  for (const suffix of ["", "-bottom"]) {
    assert.equal(atlas.get("page-status" + suffix).textContent, "Page 1 of 3");
    assert.equal(atlas.get("previous-page" + suffix).disabled, true);
    assert.equal(atlas.get("next-page" + suffix).disabled, false);
  }
});

test("top and bottom controls advance together and retain global case numbers", () => {
  const atlas = openAtlas();
  atlas.event("next-page", "click");
  assert.equal(atlas.rows().length, 10);
  assert.equal(atlas.rows()[0].children[0].textContent, "11");
  assert.equal(atlas.get("result-count").textContent, "11–20 of 27 cases shown");
  assert.equal(atlas.get("page-status-bottom").textContent, "Page 2 of 3");
  atlas.event("previous-page-bottom", "click");
  assert.equal(atlas.rows()[0].children[0].textContent, "01");
  assert.equal(atlas.get("page-status").textContent, "Page 1 of 3");
  atlas.event("previous-page", "click");
  assert.equal(atlas.get("page-status").textContent, "Page 1 of 3");
});

test("last partial page has seven records and next cannot go out of bounds", () => {
  const atlas = openAtlas();
  atlas.event("next-page-bottom", "click");
  atlas.event("next-page", "click");
  assert.equal(atlas.rows().length, 7);
  assert.equal(atlas.rows()[0].children[0].textContent, "21");
  assert.equal(atlas.get("result-count").textContent, "21–27 of 27 cases shown");
  for (const suffix of ["", "-bottom"]) assert.equal(atlas.get("next-page" + suffix).disabled, true);
  atlas.event("next-page", "click");
  assert.equal(atlas.get("page-status").textContent, "Page 3 of 3");
  assert.equal(atlas.rows().length, 7);
});

test("every page-size option resets to page 1 and limits rows", () => {
  const atlas = openAtlas();
  for (const size of [5, 10, 15, 20]) {
    atlas.event("next-page", "click");
    atlas.event("page-size", "change", String(size));
    assert.equal(atlas.rows().length, size);
    assert.equal(atlas.rows()[0].children[0].textContent, "01");
    assert.equal(atlas.get("page-status").textContent, `Page 1 of ${Math.ceil(27 / size)}`);
  }
});

test("all four search and filter changes reset page 1 without renumbering matches", () => {
  for (const [id, type, value, first] of [["search", "input", "Paper 02", "02"], ["venue", "change", "Venue B", "02"], ["outcome", "change", "scope_clarification", "03"], ["severity", "change", "minor", "02"]]) {
    const atlas = openAtlas();
    atlas.event("next-page", "click");
    atlas.event(id, type, value);
    assert.equal(atlas.get("previous-page").disabled, true, id);
    assert.match(atlas.get("page-status").textContent, /^Page 1 of /, id);
    assert.equal(atlas.rows()[0].children[0].textContent, first, id);
  }
});

test("reset clears every filter and returns page 1 while preserving selected size", () => {
  const atlas = openAtlas();
  atlas.event("page-size", "change", "5");
  atlas.event("venue", "change", "Venue A");
  atlas.event("next-page", "click");
  atlas.event("reset", "click");
  assert.equal(atlas.get("page-size").value, "5");
  assert.equal(atlas.rows().length, 5);
  assert.equal(atlas.get("page-status").textContent, "Page 1 of 6");
  for (const id of ["search", "venue", "outcome", "severity"]) assert.equal(atlas.get(id).value, "");
  assert.equal(atlas.get("search").focused, true);
});

test("empty matches have no phantom page and disable both navigation controls", () => {
  const atlas = openAtlas();
  atlas.event("next-page", "click");
  atlas.event("search", "input", "unmatched-pagination-query");
  assert.equal(atlas.rows().length, 0);
  assert.equal(atlas.get("empty").hidden, false);
  assert.equal(atlas.get("result-count").textContent, "0 of 27 cases shown");
  for (const suffix of ["", "-bottom"]) {
    assert.equal(atlas.get("page-status" + suffix).textContent, "No matching records");
    assert.equal(atlas.get("previous-page" + suffix).disabled, true);
    assert.equal(atlas.get("next-page" + suffix).disabled, true);
  }
  atlas.event("search", "input", "Paper 27");
  assert.equal(atlas.get("page-status").textContent, "Page 1 of 1");
  assert.equal(atlas.rows()[0].children[0].textContent, "27");
});

test("permalink opens any record beyond the current page and after filtering", () => {
  const atlas = openAtlas("#case=pagination-fixture-27");
  assert.equal(atlas.rows().length, 10);
  assert.equal(atlas.get("case-dialog").open, true);
  assert.match(atlas.get("detail-content").textContent, /Paper 27/);
  atlas.event("search", "input", "Paper 01");
  atlas.location.hash = "#case=pagination-fixture-26";
  atlas.events.hashchange();
  assert.match(atlas.get("detail-content").textContent, /Paper 26/);
  assert.equal(atlas.rows().length, 1);
  assert.equal(atlas.rows()[0].children[0].textContent, "01");
});

test("invalid injected page size falls back to default without unbounded rendering", () => {
  const atlas = openAtlas();
  atlas.event("page-size", "change", "99999");
  assert.equal(atlas.get("page-size").value, "10");
  assert.equal(atlas.rows().length, 10);
});

test("a homepage search opens the matching records immediately and can be reset", () => {
  const atlas = openAtlas('', '?q=Paper+27');
  assert.equal(atlas.get('search').value, 'Paper 27');
  assert.equal(atlas.rows().length, 1);
  assert.equal(atlas.rows()[0].children[0].textContent, '27');
  atlas.event('reset', 'click');
  assert.equal(atlas.rows().length, 10);
  assert.equal(atlas.get('search').value, '');
});
