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

function openAtlas(hash = "", search = "", options = {}) {
  const records = options.records || Array.from({length: 27}, (_, index) => {
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
  const location = {hash, search, pathname: "/atlas/"};
  const events = {};
  const setLocation = value => {
    const next = new URL(value, "https://elvia-atlas.org" + location.pathname + location.search + location.hash);
    location.pathname = next.pathname; location.search = next.search; location.hash = next.hash;
  };
  vm.runInNewContext(script, {
    document,
    window: {ELVIA_DATA: {records, case_notes: options.caseNotes || {}, research_fields: options.researchFields || {}}, ELVIA_SEARCH: require(path.join(formal, "src/elvia/web/search.js")), ELVIA_CASE_NOTES: require(path.join(formal, "src/elvia/web/case-note.js")), ELVIA_ASSESSMENT: require(path.join(formal, "src/elvia/web/assessment.js")), addEventListener: (name, listener) => { events[name] = listener; }},
    location, history: {pushState(_state, _unused, value) { setLocation(value); }, replaceState(_state, _unused, value) { setLocation(value); }}, URL, URLSearchParams
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

test("a question entered from the homepage shows its matching finding and preserves reset behavior", () => {
  const id = "neurips2025-0016-accelerating-feature-conformal-prediction-via-taylor-approximat";
  const record = JSON.parse(fs.readFileSync(path.join(formal, "studies/neurips2025/records", id + ".r1.json"), "utf8"));
  const notes = JSON.parse(fs.readFileSync(path.join(formal, "studies/neurips2025/case-notes.json"), "utf8")).cases;
  const atlas = openAtlas("", "?q=Does+pooling+calibration+scores+preserve+coverage%3F", {records: [original, record], caseNotes: notes});
  assert.equal(atlas.get("sort-caption").textContent, "Best match");
  assert.match(atlas.rows()[0].textContent, /Accelerating Feature Conformal Prediction/);
  const explanation = atlas.rows()[0].children[1].children.find(node => node.className === "search-match");
  assert.match(explanation.textContent, /Matched.*pooling.*calibration/);
  const anchor = explanation.children.find(node => node.tagName === "a");
  assert.match(anchor.href, new RegExp("cases/" + id + "\\.html#problem-\\d+$"));
  atlas.event("reset", "click");
  assert.equal(atlas.get("sort-caption").textContent, "Title · A–Z");
  assert.equal(atlas.rows().length, 2);
  assert.equal(atlas.get("search").focused, true);
  assert.ok(atlas.rows().every(row => !row.textContent.includes("Matched")));
});

test("both Atlas entry pages load local search before the UI and label question search", () => {
  for (const contents of [html, fs.readFileSync(path.join(formal, "src/elvia/web/index.html"), "utf8")]) {
    assert.ok(contents.indexOf('src="search.js"') < contents.indexOf('src="atlas.js"'));
    assert.match(contents, /id="search"[^>]*aria-describedby="search-help"/);
    assert.match(contents, /id="search-help"/);
    assert.match(contents, /id="sort-caption"/);
    assert.match(contents, /Question, title, author, DOI or keyword/);
  }
});

test("Field is a labeled native filter with the five requested disciplines", () => {
  const select = html.match(/<select\b[^>]*id="field"[^>]*>([\s\S]*?)<\/select>/);
  assert.ok(select, "Field select must exist");
  assert.deepEqual([...select[1].matchAll(/<option\b[^>]*>([^<]*)<\/option>/g)].map(match => match[1]),
    ["All fields", "Mathematics", "Biological science", "Computer science", "Chemistry", "Others"]);
  assert.match(html, /<label\b[^>]*><span>Field<\/span><select\b[^>]*id="field"/);
  assert.doesNotMatch(html, /Read 300 NeurIPS|<title>NeurIPS|id="hero-title">NeurIPS/);
});

test("Field combines with search, venue, assessment and finding and resets pagination", () => {
  const researchFields = Object.fromEntries(Array.from({length: 27}, (_, index) =>
    ["pagination-fixture-" + (index + 1), index % 2 ? "Biological science" : "Mathematics"]));
  const atlas = openAtlas("", "", {researchFields});
  atlas.event("next-page", "click");
  atlas.event("field", "change", "Biological science");
  assert.equal(atlas.get("page-status").textContent, "Page 1 of 2");
  assert.equal(atlas.rows()[0].children[0].textContent, "02");
  assert.ok(atlas.rows().every(row => row.textContent.includes("Biological science")));
  atlas.event("venue", "change", "Venue B");
  atlas.event("severity", "change", "no_issue_found");
  atlas.event("outcome", "change", "scope_clarification");
  assert.equal(atlas.rows().length, 4);
  atlas.event("search", "input", "Paper 12");
  assert.equal(atlas.rows().length, 1);
  assert.equal(atlas.rows()[0].children[0].textContent, "12");
  atlas.event("reset", "click");
  assert.equal(atlas.get("field").value, "");
  assert.equal(atlas.rows().length, 10);
  assert.equal(atlas.get("page-status").textContent, "Page 1 of 3");
});

test("missing or invalid discipline uses Others without inferring a field from venue", () => {
  const atlas = openAtlas("", "", {researchFields: {"pagination-fixture-1": "Chemistry", "pagination-fixture-2": "Unverified field"}});
  atlas.event("field", "change", "Others");
  assert.match(atlas.get("result-count").textContent, /of 26 cases/);
  assert.equal(atlas.rows()[0].children[0].textContent, "02");
  atlas.event("field", "change", "Chemistry");
  assert.equal(atlas.rows().length, 1);
  assert.equal(atlas.rows()[0].children[0].textContent, "01");
});

test("shared search URLs retain Field and combined filters through reload and reset", () => {
  const researchFields = {"pagination-fixture-6": "Computer science"};
  const atlas = openAtlas("", "?q=Paper+06&field=Computer+science&venue=Venue+B&severity=no_issue_found&outcome=scope_clarification", {researchFields});
  assert.equal(atlas.get("field").value, "Computer science");
  assert.equal(atlas.rows().length, 1);
  assert.equal(atlas.rows()[0].children[0].textContent, "06");
  atlas.event("search", "input", "Paper");
  const params = new URLSearchParams(atlas.location.search);
  assert.equal(params.get("field"), "Computer science");
  assert.equal(params.get("q"), "Paper");
  const reopened = openAtlas("", atlas.location.search, {researchFields});
  assert.equal(reopened.rows().length, 1);
  assert.equal(reopened.get("field").value, "Computer science");
  reopened.event("reset", "click");
  assert.equal(reopened.location.search, "");
  assert.equal(reopened.rows().length, 10);
});

test("popstate restores shared filters and invalid URL fields fall back to all fields", () => {
  const atlas = openAtlas("", "?field=unknown", {researchFields: {"pagination-fixture-4": "Mathematics"}});
  assert.equal(atlas.get("field").value, "");
  assert.equal(atlas.rows().length, 10);
  atlas.location.search = "?field=Mathematics";
  atlas.events.popstate();
  assert.equal(atlas.rows().length, 1);
  assert.equal(atlas.rows()[0].children[0].textContent, "04");
});
