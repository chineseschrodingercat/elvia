"use strict";
// Synthetic records exercise loading boundaries, never scientific correctness.
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const assessment = require("../src/elvia/web/assessment.js");
const search = require("../src/elvia/web/search.js");
const caseNotes = require("../src/elvia/web/case-note.js");
const root = path.resolve(__dirname, "..");
const collection = "a".repeat(64);
const variants = ["src/elvia/web", "website/atlas-assets"];
const clone = value => JSON.parse(JSON.stringify(value));
const walk = node => [node, ...node.children.flatMap(walk)];

function fixtures() {
  const records = Array.from({length: 27}, (_, offset) => ({
    case_id: `loading-fixture-${offset + 1}`, revision: 1,
    source: {title: `Paper ${String(offset + 1).padStart(2, "0")}`, version: "1", review_scope: "Synthetic claims"},
    audit: {venue: offset % 2 ? "Venue B" : "Venue A", year: 2025, outcome: "candidate_issue", summary: `Summary ${offset + 1}.`, authors: ["Example Author"], limitations: ["Synthetic scope."], landing_url: "https://example.org/article"},
    concern: {severity: offset % 2 ? "minor" : "major", description: "A fictional concern."},
    adjudication: {status: "pending"}, publication: {status: "preliminary_ai"},
    proposition: {claim: "An explicitly fictional assertion.", location: "Theorem 1", domain: "Positive integers", assumptions: [], dependencies: []},
    evidence: [], repair: {content: "", changed_assumptions: [], changed_conclusion: null}
  }));
  const notes = Object.fromEntries(records.map((record, offset) => [record.case_id, {
    revision: 1, brief: [`Brief ${offset + 1}.`], review_scope: ["Synthetic inspection."], report: [`Retained report ${offset + 1}.`],
    problems: [
      {id: "minor-first", title: "A small fictional concern", severity: "minor", assessment: "supported", source_location: "Lemma 1", claim: ["Original minor claim."], assumptions: [], analysis_heading: "Proof", analysis: ["Minor working."], result: ["Minor scope."], repair: null},
      {id: "major-second", title: "A major fictional concern", severity: "major", assessment: "supported", source_location: "Theorem 2", claim: ["Original major claim."], statement: ["For every positive integer n, the source asserts the fictional bound."], assumptions: [], analysis_heading: "Proof", analysis: [offset === 11 ? "A cobalt telescope contradiction is the decisive calculation." : "A complete fictional calculation."], result: ["Major scope."], repair: null}
    ]
  }]));
  const fields = Object.fromEntries(records.map((record, offset) => [record.case_id, offset % 2 ? "Mathematics" : "Computer science"]));
  const full = {format_version: "1", records, case_notes: notes, research_fields: fields,
    presentation: {}, reader_bundles: Object.fromEntries(records.map(r => [r.case_id, `evidence/${r.case_id}.zip`])),
    reader: Object.fromEntries(records.map(r => [r.case_id, {revision: 1, citation: {title: r.source.title, authors: ["Author, Example"], container: "Fictional Proceedings", volume: "1", year: 2025, first_page: "1", last_page: "3", doi: "10.0000/fictional", editors: []}}]))};
  const discovery = {format_version: "1", payload_kind: "discovery", collection_id: collection,
    records: records.map(r => ({case_id: r.case_id, revision: r.revision, source: {title: r.source.title}, audit: {venue: r.audit.venue, year: r.audit.year, outcome: r.audit.outcome, summary: r.audit.summary}, concern: {severity: r.concern.severity}, adjudication: {status: r.adjudication.status}})),
    case_notes: Object.fromEntries(records.map(r => [r.case_id, {revision: 1, brief: notes[r.case_id].brief, problems: notes[r.case_id].problems.map(p => ({severity: p.severity, assessment: p.assessment}))}])),
    research_fields: fields, presentation: {}};
  const searchData = {...clone(full), payload_kind: "search", collection_id: collection};
  function detail(id) {
    const record = records.find(r => r.case_id === id);
    return {format_version: "1", payload_kind: "case", collection_id: collection, case_id: id, revision: record.revision,
      records: [clone(record)], ...Object.fromEntries(["case_notes", "research_fields", "presentation", "reader", "reader_bundles"].map(key => [key, full[key][id] === undefined ? {} : {[id]: clone(full[key][id])}]))};
  }
  return {full, discovery, searchData, detail};
}

function openAtlas(variant, {hash = "", query = "", legacy = false} = {}) {
  const fixture = fixtures();
  const requests = [], elements = new Map(), timers = new Map(), events = {};
  let nextTimer = 1;
  class Node {
    constructor(tag) { this.tagName = tag; this.children = []; this.attributes = {}; this.className = ""; this._text = ""; this.value = ""; this.listeners = {}; this.open = false; this.disabled = false; this.isConnected = true; }
    get textContent() { return this._text + this.children.map(node => node.textContent).join(""); }
    set textContent(value) { this._text = String(value); this.children = []; }
    append(...nodes) { this.children.push(...nodes); nodes.forEach(node => { node.parent = this; }); }
    replaceChildren(...nodes) { this._text = ""; this.children = []; this.append(...nodes); }
    setAttribute(key, value) { this.attributes[key] = value; }
    addEventListener(name, handler) { this.listeners[name] = handler; }
    emit(name) { this.listeners[name]?.(); }
    remove() { if (this.parent) this.parent.children = this.parent.children.filter(node => node !== this); this.isConnected = false; }
    focus() { this.focused = true; }
    showModal() { this.open = true; }
    close() { this.open = false; this.emit("close"); }
  }
  const get = id => { if (!elements.has(id)) elements.set(id, new Node("div")); return elements.get(id); };
  const head = new Node("head");
  head.append = node => { requests.push(node); node.parent = head; head.children.push(node); };
  const document = {head, createElement: tag => new Node(tag), getElementById: get, querySelectorAll: () => []};
  const location = {hash, search: query, pathname: "/atlas/"};
  const setLocation = value => {
    const url = new URL(value, "https://example.org" + location.pathname + location.search + location.hash);
    location.hash = url.hash; location.search = url.search; location.pathname = url.pathname;
  };
  const window = {ELVIA_ASSESSMENT: assessment, ELVIA_SEARCH: search, ELVIA_CASE_NOTES: caseNotes, addEventListener: (name, handler) => { events[name] = handler; }};
  if (legacy) window.ELVIA_DATA = clone(fixture.full);
  else window.ELVIA_DISCOVERY = clone(fixture.discovery);
  vm.runInNewContext(fs.readFileSync(path.join(root, variant, "atlas.js"), "utf8"), {
    document, window, location, URL, URLSearchParams,
    history: {pushState(_state, _title, value) { setLocation(value); }, replaceState(_state, _title, value) { setLocation(value); }},
    setTimeout(handler) { const id = nextTimer++; timers.set(id, handler); return id; },
    clearTimeout(id) { timers.delete(id); }
  });
  const event = (id, type, value) => { if (value !== undefined) get(id).value = value; assert.equal(typeof get(id).listeners[type], "function"); get(id).emit(type); };
  const flushTimers = () => { const pending = [...timers.values()]; timers.clear(); pending.forEach(fn => fn()); };
  const settle = async () => { for (let i = 0; i < 12; i++) await Promise.resolve(); };
  const complete = async (request, payload) => {
    if (request.src.startsWith("search-data.js")) window.ELVIA_SEARCH_DATA = clone(payload || fixture.searchData);
    else { window.ELVIA_CASE_DATA ||= {}; window.ELVIA_CASE_DATA[payload.case_id] = clone(payload); }
    request.emit("load"); await settle();
  };
  const hashChange = value => { location.hash = value; events.hashchange(); };
  return {fixture, window, get, event, requests, flushTimers, settle, complete, hashChange, events, location, rows: () => get("case-list").children};
}

for (const variant of variants) {
  test(`${variant}: the entry page boots discovery without eager complete data`, () => {
    const html = fs.readFileSync(path.join(root, variant, "index.html"), "utf8");
    assert.match(html, /<script\b[^>]*\bsrc="discovery\.js"/);
    assert.doesNotMatch(html, /<script\b[^>]*\bsrc="(?:data|search-data)\.js"/);
    assert.ok(html.indexOf('src="discovery.js"') < html.indexOf('src="atlas.js?v=discovery-1"'));
  });

  test(`${variant}: compact boot paints the list, summaries and filters without a lazy request`, () => {
    const atlas = openAtlas(variant);
    assert.equal(atlas.get("count-total").textContent, "27");
    assert.equal(atlas.get("count-major").textContent, "14");
    assert.equal(atlas.get("count-minor").textContent, "13");
    assert.equal(atlas.rows().length, variant.startsWith("website/") ? 10 : 27);
    assert.match(atlas.rows()[0].textContent, /Paper 01.*Brief 1\./);
    assert.equal(walk(atlas.rows()[0]).find(node => node.className === "case-title").href, "cases/loading-fixture-1.html");
    atlas.event("venue", "change", "Venue B");
    assert.ok(atlas.rows().every(row => row.textContent.includes("VENUE B")));
    assert.equal(atlas.rows()[0].children[0].textContent, "02");
    if (variant.startsWith("website/")) {
      atlas.event("field", "change", "Mathematics");
      atlas.event("next-page", "click");
      assert.equal(atlas.rows().length, 3);
      assert.equal(atlas.rows()[0].children[0].textContent, "22");
    }
    assert.equal(atlas.requests.length, 0);
  });

  test(`${variant}: query entry debounces one compact search load and preserves full-text finding identity`, async () => {
    const atlas = openAtlas(variant);
    atlas.event("search", "input", "cobalt");
    atlas.event("search", "input", "cobalt telescope");
    assert.equal(atlas.requests.length, 0);
    assert.doesNotMatch(atlas.get("result-count").textContent, /^0 of /);
    atlas.flushTimers();
    assert.equal(atlas.requests.length, 1);
    assert.equal(atlas.requests[0].src, "search-data.js?collection=" + collection);
    assert.match(atlas.get("result-count").textContent, /Loading search/);
    await atlas.complete(atlas.requests[0]);
    assert.equal(atlas.rows().length, 1);
    assert.equal(atlas.rows()[0].children[0].textContent, "12");
    assert.match(atlas.rows()[0].textContent, /Brief 12\./);
    const anchor = walk(atlas.rows()[0]).find(node => node.textContent === "Read Problem 1");
    assert.ok(anchor);
    assert.equal(anchor.href, "cases/loading-fixture-12.html#problem-2");
    atlas.event("search", "input", "Paper 27"); atlas.flushTimers();
    assert.equal(atlas.requests.length, 1);
    assert.match(atlas.rows()[0].textContent, /Paper 27/);
  });

  test(`${variant}: encoded scientific fields retain finding links and invalid sequences can retry`, async () => {
    const atlas = openAtlas(variant, {query: "?q=cobalt+telescope"});
    const encoded = clone(atlas.fixture.searchData);
    delete encoded.case_notes;
    encoded.search_projection = {encoding: "word-sequences-v1", vocabulary: ["cobalt", "telescope"],
      chunks: ["0 1"], documents: {"loading-fixture-12": {revision: 1,
        fields: [[[0], 3, "Problem 1", 2, "A major fictional concern", 1]]}}};
    const invalid = clone(encoded); invalid.search_projection.chunks[0] = "z";
    await atlas.complete(atlas.requests[0], invalid);
    assert.match(atlas.get("result-count").textContent, /could not be loaded/i);
    walk(atlas.get("case-list")).find(node => node.tagName === "button").emit("click");
    await atlas.complete(atlas.requests[1], encoded);
    assert.equal(atlas.rows().length, 1);
    const anchor = walk(atlas.rows()[0]).find(node => node.textContent === "Read Problem 1");
    assert.equal(anchor.href, "cases/loading-fixture-12.html#problem-2");
  });

  test(`${variant}: initial query waits honestly, and reset defeats an in-flight completion`, async () => {
    const atlas = openAtlas(variant, {query: "?q=cobalt+telescope"});
    assert.equal(atlas.requests.length, 1);
    assert.match(atlas.get("result-count").textContent, /Loading search/);
    assert.equal(atlas.get("empty").hidden, true);
    atlas.event("reset", "click");
    const resetCount = atlas.get("result-count").textContent;
    await atlas.complete(atlas.requests[0]);
    assert.equal(atlas.get("search").value, "");
    assert.equal(atlas.get("result-count").textContent, resetCount);
    assert.match(atlas.rows()[0].textContent, /Paper 01/);
    assert.equal(atlas.requests.length, 1);
  });

  test(`${variant}: the latest query wins while a shared search download is in flight`, async () => {
    const atlas = openAtlas(variant, {query: "?q=cobalt+telescope"});
    atlas.event("search", "input", "Paper 27"); atlas.flushTimers();
    assert.equal(atlas.requests.length, 1);
    await atlas.complete(atlas.requests[0]);
    assert.equal(atlas.rows().length, 1);
    assert.match(atlas.rows()[0].textContent, /Paper 27/);
  });

  test(`${variant}: failed and mixed-build search payloads show a retry, never zero matches`, async () => {
    const atlas = openAtlas(variant, {query: "?q=cobalt+telescope"});
    atlas.requests[0].emit("error"); await atlas.settle();
    assert.match(atlas.get("result-count").textContent, /could not be loaded/i);
    assert.doesNotMatch(atlas.get("result-count").textContent, /^0 of /);
    let retry = walk(atlas.get("case-list")).find(node => node.tagName === "button");
    assert.equal(retry.textContent, "Retry search"); retry.emit("click");
    assert.equal(atlas.requests.length, 2);
    await atlas.complete(atlas.requests[1], {...atlas.fixture.searchData, collection_id: "b".repeat(64)});
    assert.match(atlas.get("result-count").textContent, /could not be loaded/i);
    retry = walk(atlas.get("case-list")).find(node => node.tagName === "button"); retry.emit("click");
    await atlas.complete(atlas.requests[2]);
    assert.equal(atlas.rows().length, 1);
    assert.match(atlas.rows()[0].textContent, /Paper 12/);
  });

  test(`${variant}: legacy case links load only one complete note with its statement, citation and bundle`, async () => {
    const atlas = openAtlas(variant, {hash: "#case=loading-fixture-27"});
    assert.equal(atlas.get("case-dialog").open, true);
    assert.match(atlas.get("detail-content").textContent, /Loading note/);
    assert.equal(atlas.requests.length, 1);
    assert.equal(atlas.requests[0].src, "cases/loading-fixture-27.data.js?collection=" + collection);
    await atlas.complete(atlas.requests[0], atlas.fixture.detail("loading-fixture-27"));
    const content = atlas.get("detail-content");
    assert.match(content.textContent, /For every positive integer n, the source asserts the fictional bound/);
    assert.match(content.textContent, /A complete fictional calculation/);
    assert.match(content.textContent, /Fictional Proceedings/);
    assert.ok(walk(content).some(node => node.href === "https://doi.org/10.0000/fictional"));
    assert.ok(walk(content).some(node => node.href === "evidence/loading-fixture-27.zip"));
    atlas.hashChange("#atlas"); atlas.hashChange("#case=loading-fixture-27"); await atlas.settle();
    assert.equal(atlas.requests.length, 1);
    assert.equal(atlas.get("case-dialog").open, true);
  });

  test(`${variant}: late case responses cannot replace a newer selection or reopen a closed dialog`, async () => {
    const atlas = openAtlas(variant, {hash: "#case=loading-fixture-1"});
    atlas.hashChange("#case=loading-fixture-2");
    await atlas.complete(atlas.requests[1], atlas.fixture.detail("loading-fixture-2"));
    await atlas.complete(atlas.requests[0], atlas.fixture.detail("loading-fixture-1"));
    assert.match(atlas.get("detail-content").textContent, /Paper 02/);
    assert.doesNotMatch(atlas.get("detail-content").textContent, /Paper 01/);
    atlas.hashChange("#case=loading-fixture-3");
    atlas.event("close-dialog", "click");
    await atlas.complete(atlas.requests[2], atlas.fixture.detail("loading-fixture-3"));
    assert.equal(atlas.get("case-dialog").open, false);
    assert.equal(atlas.location.hash, "#atlas");
  });

  test(`${variant}: failed or mismatched case data keeps a static reading link and can retry`, async () => {
    const atlas = openAtlas(variant, {hash: "#case=loading-fixture-4"});
    atlas.requests[0].emit("error"); await atlas.settle();
    let content = atlas.get("detail-content");
    assert.match(content.textContent, /could not be loaded/i);
    assert.ok(walk(content).some(node => node.href === "cases/loading-fixture-4.html"));
    walk(content).find(node => node.tagName === "button").emit("click");
    const wrong = atlas.fixture.detail("loading-fixture-4"); wrong.records[0].revision = 2;
    await atlas.complete(atlas.requests[1], wrong);
    assert.match(atlas.get("detail-content").textContent, /could not be loaded/i);
    content = atlas.get("detail-content"); walk(content).find(node => node.tagName === "button").emit("click");
    await atlas.complete(atlas.requests[2], atlas.fixture.detail("loading-fixture-4"));
    assert.match(atlas.get("detail-content").textContent, /A complete fictional calculation/);
    atlas.hashChange("#case=not-a-published-case");
    assert.equal(atlas.requests.length, 3);
  });

  test(`${variant}: older complete-data builds retain synchronous search and case behavior`, () => {
    const atlas = openAtlas(variant, {legacy: true, hash: "#case=loading-fixture-27"});
    assert.equal(atlas.get("case-dialog").open, true);
    assert.match(atlas.get("detail-content").textContent, /Paper 27/);
    atlas.event("search", "input", "cobalt telescope");
    assert.equal(atlas.rows().length, 1);
    assert.match(atlas.rows()[0].textContent, /Paper 12/);
    assert.equal(atlas.requests.length, 0);
  });
}
