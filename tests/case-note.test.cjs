"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const {renderProblems, fallbackProblems} = require("../src/elvia/web/case-note.js");
const math = require("../src/elvia/web/math.js");
const katex = require("../src/elvia/web/vendor/katex/katex.min.js");

class Node {
  constructor(tag) { this.tagName = tag; this.ownerDocument = document; this.children = []; this.attributes = {}; this.className = ""; this._text = ""; this.value = ""; this.listeners = {}; this.open = false; }
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
const document = {
  createElement: tag => new Node(tag),
  createTextNode: text => { const node = new Node("#text"); node.textContent = text; return node; },
  createDocumentFragment: () => new Node("#fragment")
};
const create = (tag, text, className) => {
  const node = new Node(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
};
const helpers = {
  create,
  prose: (tag, text, record, className) => create(tag, text, className),
  link: (label, href) => { const node = create("a", label); node.href = href; return node; },
  artifactURL: (record, path) => `evidence/${record.case_id}/${path}`
};
const record = {
  case_id: "example", revision: 1,
  proposition: {claim: "Original claim", location: "Page 2, Eq. (4)", domain: "Recorded domain", assumptions: ["Recorded assumption"]},
  audit: {outcome: "candidate_issue", summary: "Bounded conclusion", limitations: ["Finite check only"]},
  concern: {description: "Original counterexample"},
  repair: {content: "Original proposed correction", changed_assumptions: [], changed_conclusion: null},
  evidence: [{id: "actual-output", artifact: {path: "output.json"}}]
};
const problem = {
  id: "claim-1", title: "A local identity", source_location: "Appendix A, Eq. (12)",
  claim: ["The source claim."], assumptions: ["The stated conditions."],
  analysis_heading: "Counterexample", analysis: ["A worked counterexample."],
  result: ["The local consequence and its limits."],
  repair: {heading: "A proposed correction", paragraphs: ["The corrected identity."]},
  evidence_ids: ["actual-output"]
};
const walk = node => [node, ...node.children.flatMap(walk)];
const render = (problems, source = record) => {
  const parent = create("div");
  renderProblems(parent, source, {revision: source.revision, problems}, helpers);
  return parent;
};

test("problem reading order is claim and citation, analysis, finding, then applicable correction", () => {
  const parent = render([problem]);
  const nodes = walk(parent);
  assert.deepEqual(nodes.filter(node => ["h3", "h4"].includes(node.tagName)).map(node => node.textContent), [
    "Problem 1. A local identity", "Claim in the source (paraphrase)", "Conditions", "Counterexample", "Finding and scope", "A proposed correction"
  ]);
  const text = parent.textContent;
  for (const [before, after] of [["Appendix A, Eq. (12)", "The source claim."], ["The source claim.", "A worked counterexample."], ["A worked counterexample.", "The local consequence"], ["The local consequence", "The corrected identity."]]) {
    assert.ok(text.indexOf(before) < text.indexOf(after));
  }
  assert.equal(nodes.filter(node => node.tagName === "a").length, 0);
  assert.ok(!/output\.json|Inspect the working|Recorded output/.test(text));
});

test("problem with no applicable correction omits correction headings and filler", () => {
  const parent = render([{...problem, result: ["The local consequence."], repair: null}]);
  assert.ok(parent.textContent.includes("The local consequence."));
  assert.ok(!/correction|repair|not applicable/i.test(parent.textContent));
  assert.equal(walk(parent).filter(node => node.tagName === "h4").at(-1).textContent, "Finding and scope");
});

test("multiple bounded problems receive sequential headings and independent repairs", () => {
  const parent = render([problem, {...problem, id: "claim-2", title: "A separate statement", repair: null}]);
  assert.deepEqual(walk(parent).filter(node => node.tagName === "h3").map(node => node.textContent), [
    "Problem 1. A local identity", "Problem 2. A separate statement"
  ]);
  assert.equal(walk(parent).filter(node => node.textContent === "A proposed correction").length, 1);
});

test("untrusted prose and headings are text nodes, never markup", () => {
  const attack = '<img src=x onerror="alert(1)">';
  const parent = render([{...problem, title: attack, claim: [attack], source_location: attack, repair: null}]);
  assert.ok(parent.textContent.includes(attack));
  assert.ok(!walk(parent).some(node => ["img", "script"].includes(node.tagName)));
  assert.ok(walk(parent).every(node => !("innerHTML" in node)));
});

test("unknown and mismatched revisions fall back to the full recorded claim and check", () => {
  const parent = create("div");
  renderProblems(parent, record, {revision: 2, problems: [problem]}, helpers);
  for (const text of ["Original claim", "Page 2, Eq. (4)", "Recorded domain", "Recorded assumption", "Original counterexample", "Bounded conclusion", "Finite check only", "Original proposed correction"]) {
    assert.ok(parent.textContent.includes(text), text);
  }
  assert.ok(!parent.textContent.includes("The source claim."));
});

test("no-issue cases stay one brief sentence even if a full narrative is supplied", () => {
  const source = {...record, audit: {...record.audit, outcome: "no_issue_found", summary: "No issue in scope"}, repair: {...record.repair, content: null}};
  assert.deepEqual(fallbackProblems(source), []);
  for (const note of [null, {revision: 1, problems: [problem]}]) {
    const parent = create("div");
    renderProblems(parent, source, note, helpers);
    assert.equal(parent.textContent, "No issue was found within the scope of this check.");
    assert.equal(walk(parent).filter(node => node.className === "case-problem").length, 0);
    assert.equal(walk(parent).filter(node => node.tagName === "p").length, 1);
  }
});

test("scope clarifications show only their short recorded summary, never a problem or correction", () => {
  const source = {...record, audit: {...record.audit, outcome: "scope_clarification", summary: "A scoped condition matters here."}};
  assert.deepEqual(fallbackProblems(source), []);
  const parent = create("div");
  renderProblems(parent, source, {revision: 1, problems: [problem]}, helpers);
  assert.deepEqual(walk(parent).filter(node => ["h3", "h4"].includes(node.tagName)).map(node => node.textContent), ["Scope clarification"]);
  assert.equal(walk(parent).filter(node => node.tagName === "p").length, 1);
  assert.ok(parent.textContent.includes("A scoped condition matters here."));
  assert.ok(!/correction|counterexample|problem/i.test(parent.textContent));
});

test("candidate and historical fallback outcomes retain working without invented counterexamples", () => {
  for (const [outcome, heading] of Object.entries({candidate_issue: "Analysis", known_issue_reproduced: "Known issue analysis"})) {
    const source = {...record, audit: {...record.audit, outcome, summary: outcome}, evidence: [...record.evidence, {id: "work", stance: "support", description: "Recorded working", artifact: {path: "work.txt"}}]};
    const note = fallbackProblems(source)[0];
    assert.equal(note.analysis_heading, heading);
    assert.ok(note.analysis.includes("Recorded working"));
    assert.ok(note.result.includes(outcome));
  }
});

const root = path.join(__dirname, "..");
const catalog = () => JSON.parse(fs.readFileSync(path.join(root, "studies/neurips2025/case-notes.json"), "utf8"));
const originalRecords = () => fs.readdirSync(path.join(root, "studies/neurips2025/records"))
  .filter(name => name.endsWith(".json")).map(name => JSON.parse(fs.readFileSync(path.join(root, "studies/neurips2025/records", name), "utf8")));

test("all current reader views render their actual mathematics with the bundled strict engine", () => {
  const entries = catalog().cases;
  const notation = JSON.parse(fs.readFileSync(path.join(root, "src/elvia/web/math-notation.json"), "utf8")).cases;
  let expressions = 0;
  let problems = 0;
  let brief = 0;
  const renderer = {render(tex, node, options) { expressions++; node.textContent = katex.renderToString(tex, options); }};
  const records = originalRecords();
  assert.equal(records.length, 300);
  assert.equal(Object.keys(entries).length, 284);
  for (const source of records) {
    const rendered = create("div");
    const mathematicalHelpers = {...helpers, prose(tag, text, current, className) {
      const node = create(tag, undefined, className);
      const result = math.renderInto(node, text, {renderer, replacements: notation[current.case_id]?.replacements || []});
      assert.notEqual(result.status, "fallback", `${current.case_id}: ${text}`);
      return node;
    }};
    renderProblems(rendered, source, entries[source.case_id], mathematicalHelpers);
    const nodes = walk(rendered);
    problems += nodes.filter(node => node.className === "case-problem").length;
    brief += nodes.filter(node => node.className.startsWith("case-result ")).length;
    if (entries[source.case_id]) {
      assert.equal(nodes.filter(node => node.tagName === "h3").length, entries[source.case_id].problems.length);
    }
  }
  assert.equal(problems, 1088);
  assert.equal(brief, 16);
  assert.ok(expressions >= 9000, "substantive notes must render their actual worked mathematics");
});

test("both Atlas views keep citation, reasoning, concise support and the final reader download", () => {
  const records = originalRecords();
  const notes = catalog().cases;
  for (const scriptPath of ["src/elvia/web/atlas.js", "website/atlas-assets/atlas.js"]) {
    const script = fs.readFileSync(path.join(root, scriptPath), "utf8");
    for (const source of records) {
      const pages = [["33914", "33937", "pp. 33914–37"], ["1396", "1404", "pp. 1396–404"],
        ["99", "101", "pp. 99–101"], ["7", "7", "p. 7"]][records.indexOf(source) % 4];
      const elements = new Map();
      const get = id => {
        if (!elements.has(id)) elements.set(id, create("div"));
        return elements.get(id);
      };
      const reader = {[source.case_id]: {revision: source.revision,
        citation: {authors: ["Example, Alex", "Person, Another", "Third, One"],
          title: source.source.title, container: "Advances in Neural Information Processing Systems",
          volume: "38", year: 2025, first_page: pages[0], last_page: pages[1], doi: "10.1234/fixture"},
        contributors: [{name: "Example Contributor", role: "Initial report", revision: 1}]}};
      vm.runInNewContext(script, {
        document: {...document, getElementById: get, querySelectorAll: () => []},
        window: {ELVIA_DATA: {records, case_notes: notes, reader, reader_bundles: {
          [source.case_id]: `evidence/${source.case_id}.zip`}},
          ELVIA_CASE_NOTES: {renderProblems}, ELVIA_ASSESSMENT: require("../src/elvia/web/assessment.js"), addEventListener() {}},
        location: {hash: "#case=" + source.case_id}, history: {replaceState() {}, pushState() {}}, URL, URLSearchParams
      });
      const content = get("detail-content");
      const supporting = content.children.find(node => node.tagName === "details");
      assert.ok(supporting, source.case_id);
      assert.equal(supporting.open, false);
      assert.equal(supporting.children[0].textContent, "Supporting record & provenance");
      const narrative = content.children.find(node => node.className === "problem-notes");
      assert.ok(content.children.indexOf(narrative) < content.children.indexOf(supporting));
      const citation = content.children.find(node => node.className === "detail-citation");
      assert.ok(citation.textContent.includes("Example, Alex, et al."));
      assert.ok(citation.textContent.includes(pages[2]));
      assert.ok(citation.children.some(node => node.tagName === "em"));
      assert.ok(walk(citation).some(node => node.href === "https://doi.org/10.1234/fixture"));
      const primary = content.children.at(-1);
      assert.equal(primary.className, "detail-download");
      assert.equal(primary.children.filter(node => node.tagName === "a").length, 1);
      assert.ok(content.children.indexOf(supporting) < content.children.indexOf(primary));
      assert.ok(!content.textContent.includes("Case permalink"));
      assert.ok(!content.textContent.includes("SHA-256"));
      assert.ok(!content.textContent.includes("Preliminary AI analysis."));
      for (const field of [source.proposition.claim, source.proposition.location, source.proposition.domain,
        ...source.proposition.assumptions, ...source.proposition.dependencies, source.source.review_scope,
        source.concern.description, ...source.evidence.filter(item => item.id !== "editable-latex").map(item =>
          item.description.replace(/^Preliminary AI assessment; independent human scientific adjudication remains pending\.\s*/, ""))]) {
        assert.ok(supporting.textContent.includes(field), `${source.case_id}: missing substantive evidence ${field}`);
      }
      assert.deepEqual(walk(supporting).filter(node => node.tagName === "h3").map(node => node.textContent), [
        "Work status", "Original claim and review scope", "Complete evidence and counterevidence"]);
      assert.ok(supporting.textContent.includes("Version 1"));
      assert.ok(supporting.textContent.includes("Example Contributor"));
      assert.ok(!supporting.textContent.includes("Preliminary AI assessment; independent human scientific adjudication remains pending."));
      assert.ok(!supporting.textContent.includes("Typeset source generated from the same reviewed problem paragraphs."));
      assert.ok(!get("case-list").textContent.includes("Read the case note"));
      assert.ok(get("case-dialog").open);
      assert.ok(get("close-dialog").focused);
    }
  }
});

test("a later revision never displays old contributor credit or a stale citation catalog", () => {
  const source = {...originalRecords()[0], revision: 3};
  const elements = new Map();
  const get = id => {
    if (!elements.has(id)) elements.set(id, create("div"));
    return elements.get(id);
  };
  vm.runInNewContext(fs.readFileSync(path.join(root, "src/elvia/web/atlas.js"), "utf8"), {
    document: {...document, getElementById: get, querySelectorAll: () => []},
    window: {ELVIA_DATA: {records: [source], case_notes: {}, reader: {[source.case_id]: {
      revision: 1, citation: {title: "Stale citation"}, contributors: [{name: "Stale credit"}]}}},
      ELVIA_CASE_NOTES: {renderProblems}, ELVIA_ASSESSMENT: require("../src/elvia/web/assessment.js"), addEventListener() {}},
    location: {hash: "#case=" + source.case_id}, history: {replaceState() {}, pushState() {}}, URL
  });
  const content = get("detail-content");
  assert.ok(content.textContent.includes("Version 3"));
  assert.ok(!content.textContent.includes("Stale citation"));
  assert.ok(!content.textContent.includes("Stale credit"));
  assert.ok(!walk(content).some(node => node.attributes.download !== undefined));
});
