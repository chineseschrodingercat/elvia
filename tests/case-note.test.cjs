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
  readerBundleAvailable: true,
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

test("a source-backed proof merges its premises into the statement and ends before the finding", () => {
  const complete = {...problem, analysis_heading: "Proof", assessment: "supported", claim_heading: "Problem statement",
    assumptions: ["Let \\(x=1/2\\).", "Assume \\(x>0\\)."],
    claim: ["The claimed inequality \\(x>1\\) fails."],
    analysis: ["The specified rational satisfies \\(0<x<1\\), contradicting the universal claim."]};
  const before = JSON.stringify(complete);
  const parent = render([complete]);
  const nodes = walk(parent);
  const headings = nodes.filter(node => node.tagName === "h4").map(node => node.textContent);
  assert.deepEqual(headings, ["Problem statement", "Source and method", "Proof", "Detailed finding and scope"]);
  assert.equal(nodes.filter(node => node.textContent === "Problem statement").length, 1);
  const statement = nodes.find(node => node.className.split(/\s+/).includes("problem-statement"));
  assert.equal(statement.tagName, "p");
  assert.equal(statement.textContent, [...complete.assumptions, ...complete.claim].join(" "));
  assert.ok(!nodes.filter(node => node.tagName === "li").some(node => complete.assumptions.includes(node.textContent)));
  assert.equal(nodes.filter(node => node.className.split(/\s+/).includes("proof-end")).length, 1);
  assert.ok(parent.textContent.indexOf("\\(\\square\\)") < parent.textContent.indexOf("Detailed finding and scope"));
  assert.ok(!parent.textContent.includes("The corrected identity."));
  assert.equal(JSON.stringify(complete), before);
});

test("unresolved verification never receives a proof heading or an invented QED", () => {
  for (const candidate of [problem, {...problem, analysis_heading: "Verification", assessment: "needs_evidence"}, {...problem, analysis_heading: "Proof", analysis: []}]) {
    const parent = render([candidate]);
    const nodes = walk(parent);
    assert.ok(nodes.some(node => node.tagName === "h4" && node.textContent === "Verification"));
    assert.ok(!nodes.some(node => node.tagName === "h4" && node.textContent === "Proof"));
    assert.ok(!nodes.some(node => node.className.split(/\s+/).includes("proof-end")));
    assert.ok(!parent.textContent.includes("The corrected identity."));
  }
});

test("an explicit local proof remains a proof while historical impact is unresolved", () => {
  const candidate = {...problem, analysis_heading: "Proof", assessment: "needs_evidence", method: ["Analytic two-path proof.", "Exact symbolic check."]};
  const source = {...record, audit: {...record.audit, outcome: "needs_evidence"}};
  const before = JSON.stringify([candidate, source]);
  const parent = render([candidate], source);
  const nodes = walk(parent);
  assert.ok(nodes.some(node => node.tagName === "h4" && node.textContent === "Proof"));
  assert.equal(nodes.filter(node => node.className.split(/\s+/).includes("proof-end")).length, 1);
  for (const method of candidate.method) assert.ok(parent.textContent.includes(method));
  assert.equal(JSON.stringify([candidate, source]), before);
  assert.equal(walk(render([{...candidate, analysis: ["A bounded contradiction. \\(\\square\\)"]}])).filter(node => node.className.split(/\s+/).includes("proof-end")).length, 0);
});

test("severity ordering numbers visible findings sequentially while retaining original identity and anchors", () => {
  const candidates = [
    {severity: "minor"}, {severity: "major"}, {severity: "moderate"},
    {severity: "major", assessment: "needs_evidence"},
    {severity: "major", assessment: "not_issue"}, {severity: "major"}
  ].map((classification, index) => ({...problem, ...classification,
    id: `original-${index + 1}`, title: `Original title ${index + 1}`,
    claim: [`Original statement ${index + 1}.`], source_location: `Original source ${index + 1}`}));
  const before = JSON.stringify(candidates);
  const parent = render(candidates);
  const sections = parent.children.filter(node => node.className === "case-problem");
  assert.deepEqual(sections.map(section => section.children[0].id), ["problem-2", "problem-6", "problem-1", "problem-3", "problem-4"]);
  for (const [position, section] of sections.entries()) {
    const number = Number(section.children[0].id.slice(8));
    assert.equal(section.children[0].textContent, `Problem ${position + 1}. Original title ${number}`);
    assert.equal(section.attributes["data-source-problem-id"], `original-${number}`);
    assert.equal(section.attributes["data-source-problem-number"], String(number));
    assert.equal(section.attributes["data-display-problem-number"], String(position + 1));
    assert.ok(walk(section).some(node => node.id === `problem-${number}-evidence`));
    assert.ok(walk(section).some(node => node.tagName === "summary" && node.textContent === `Evidence and reasoning for Problem ${position + 1}`));
    assert.ok(section.textContent.includes(`Original statement ${number}.`));
    assert.ok(section.textContent.includes(`Original source ${number}`));
  }
  assert.equal(walk(parent).filter(node => node.className === "evidence-files-note").length, 1);
  assert.equal(JSON.stringify(candidates), before);
  assert.ok(!parent.textContent.includes("Original title 5"));
  assert.ok(!walk(parent).some(node => node.id === "problem-5"));
});

test("article abstract is one paragraph with no per-problem finding bullets", () => {
  const parent = create("div");
  renderProblems(parent, record, {revision: 1, brief: ["The checked identity fails.", "Impact is limited to the stated setting."], problems: [problem, {...problem, id: "p2"}]}, helpers);
  const nodes = walk(parent);
  assert.equal(nodes.filter(node => node.tagName === "h2" && node.textContent === "Analysis abstract").length, 1);
  const abstracts = nodes.filter(node => node.className.split(/\s+/).includes("analysis-abstract"));
  assert.equal(abstracts.length, 1);
  assert.equal(abstracts[0].tagName, "p");
  assert.equal(abstracts[0].textContent, "The checked identity fails. Impact is limited to the stated setting.");
  assert.ok(!nodes.some(node => node.className === "finding-brief" || node.tagName === "li"));
  const noIssue = render([{...problem, assessment: "not_issue", severity: "major"}]);
  assert.ok(!walk(noIssue).some(node => node.className === "case-problem"));
  assert.ok(noIssue.textContent.includes("Detailed finding and scope"));
});

test("problem reading order is statement, source and method, verification, then finding", () => {
  const parent = render([problem]);
  const nodes = walk(parent);
  assert.deepEqual(nodes.filter(node => ["h3", "h4"].includes(node.tagName)).map(node => node.textContent), [
    "Problem 1. A local identity", "Problem statement", "Source and method", "Verification", "Detailed finding and scope"
  ]);
  const details = nodes.find(node => node.className === "evidence-content");
  const text = details.textContent;
  for (const [before, after] of [["The stated conditions.", "The source claim."], ["The source claim.", "Appendix A, Eq. (12)"], ["Appendix A, Eq. (12)", "A worked counterexample."], ["A worked counterexample.", "The local consequence"]]) {
    assert.ok(text.indexOf(before) < text.indexOf(after));
  }
  assert.equal(nodes.filter(node => node.tagName === "a").length, 0);
  assert.ok(!/output\.json|Inspect the working|Recorded output/.test(text));
});

test("problem with no applicable correction omits correction headings and filler", () => {
  const parent = render([{...problem, result: ["The local consequence."], repair: null}]);
  assert.ok(parent.textContent.includes("The local consequence."));
  assert.ok(!/correction|repair|not applicable/i.test(parent.textContent));
  assert.ok(walk(parent).some(node => node.tagName === "h4" && node.textContent === "Detailed finding and scope"));
});

test("a recorded inspection subject keeps its role instead of becoming a source claim", () => {
  const parent = render([{...problem, claim_heading: "Inspection subject recorded in the report",
    claim: ["Recorded check: A fictional historical trace check."], repair: null}]);
  const headings = walk(parent).filter(node => node.tagName === "h4").map(node => node.textContent);
  assert.ok(headings.includes("Problem statement"));
  assert.ok(walk(parent).some(node => node.className === "statement-role" && node.textContent === "Inspection subject recorded in the report"));
  assert.ok(!headings.includes("Claim in the source (paraphrase)"));
  assert.ok(parent.textContent.includes("Recorded check: A fictional historical trace check."));
});

test("multiple bounded problems preserve report numbering without a correction column", () => {
  const parent = render([problem, {...problem, id: "claim-2", title: "A separate statement", repair: null}]);
  assert.deepEqual(walk(parent).filter(node => node.tagName === "h3").map(node => node.textContent), [
    "Problem 1. A local identity", "Problem 2. A separate statement"
  ]);
  assert.equal(walk(parent).filter(node => node.textContent === "A proposed correction").length, 0);
});

test("case-wide metadata is omitted while scientific details and the ZIP notice remain", () => {
  const parent = render([problem, {...problem, id: "claim-2", repair: null}]);
  assert.ok(!parent.textContent.includes("Case-wide scope and evidence"));
  assert.ok(!walk(parent).some(node => node.id === "case-scope-evidence" || node.href === "#case-scope-evidence"));
  assert.equal(walk(parent).filter(node => node.className === "evidence-files-note").length, 1);
  assert.ok(parent.textContent.includes("Supporting files are included in Download report files (.zip)."));
  for (const text of [...problem.claim, ...problem.assumptions, ...problem.analysis, ...problem.result]) {
    assert.ok(parent.textContent.includes(text), text);
  }
});

test("a page without an available report bundle does not promise supporting files", () => {
  for (const outcome of ["candidate_issue", "no_issue_found", "scope_clarification"]) {
    const parent = create("div");
    renderProblems(parent, {...record, audit: {...record.audit, outcome}}, {revision: 1, problems: [problem]}, {...helpers, readerBundleAvailable: false});
    assert.ok(!parent.textContent.includes("Download report files (.zip)"));
    assert.ok(!walk(parent).some(node => node.className === "evidence-files-note"));
  }
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
  for (const text of ["Original claim", "Page 2, Eq. (4)", "Recorded domain", "Recorded assumption", "Original counterexample", "Bounded conclusion", "Finite check only"]) {
    assert.ok(parent.textContent.includes(text), text);
  }
  assert.ok(!parent.textContent.includes("The source claim."));
  assert.ok(!parent.textContent.includes("Original proposed correction"));
});

test("no-issue cases keep a brief summary and fold their scientific scope", () => {
  const source = {...record, audit: {...record.audit, outcome: "no_issue_found", summary: "No issue in scope"}, repair: {...record.repair, content: null}};
  assert.deepEqual(fallbackProblems(source), []);
  for (const note of [null, {revision: 1, problems: [problem]}]) {
    const parent = create("div");
    renderProblems(parent, source, note, helpers);
    assert.ok(parent.textContent.includes("No issue was found within the scope of this check."));
    assert.equal(walk(parent).filter(node => node.className === "case-problem").length, 0);
    assert.equal(walk(parent).filter(node => node.tagName === "details").length, 1);
    assert.ok(parent.textContent.includes("Finite check only"));
  }
});

test("scope clarifications keep their brief summary and scientific scope without metadata", () => {
  const source = {...record, audit: {...record.audit, outcome: "scope_clarification", summary: "A scoped condition matters here."}};
  assert.deepEqual(fallbackProblems(source), []);
  const parent = create("div");
  renderProblems(parent, source, {revision: 1, problems: [problem]}, helpers);
  assert.deepEqual(walk(parent).filter(node => ["h3", "h4"].includes(node.tagName)).map(node => node.textContent), ["Scope clarification", "Detailed finding and scope"]);
  assert.equal(walk(parent).filter(node => node.tagName === "details").length, 1);
  assert.ok(parent.textContent.includes("A scoped condition matters here."));
  assert.equal(walk(parent).filter(node => node.className === "case-problem").length, 0);
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

test("both opened Atlas views quote only current original-source excerpts and keep noissue scope ordinary", () => {
  for (const scriptPath of ["src/elvia/web/atlas.js", "website/atlas-assets/atlas.js"]) {
    for (const stale of [false, true]) {
      const source = originalRecords()[0];
      source.audit.outcome = "no_issue_found";
      const quote = {text: "A verbatim synthetic excerpt with \\(x>0,\\ldots\\).", locator: "Page 2, Theorem 1", source_identity: "Frozen original-paper PDF", source_sha256: source.audit.pdf_sha256};
      const note = {revision: source.revision + Number(stale), source_quotes: [quote]};
      const elements = new Map();
      const get = id => {
        if (!elements.has(id)) elements.set(id, create("div"));
        return elements.get(id);
      };
      vm.runInNewContext(fs.readFileSync(path.join(root, scriptPath), "utf8"), {
        document: {...document, getElementById: get, querySelectorAll: () => []},
        window: {ELVIA_DATA: {records: [source], case_notes: {[source.case_id]: note}},
          ELVIA_SEARCH: require("../src/elvia/web/search.js"), ELVIA_CASE_NOTES: require("../src/elvia/web/case-note.js"),
          ELVIA_ASSESSMENT: require("../src/elvia/web/assessment.js"), ELVIA_MATH: math,
          katex: {render(tex, node, options) { node.textContent = katex.renderToString(tex, options); }}, addEventListener() {}},
        location: {hash: "#case=" + source.case_id}, history: {replaceState() {}, pushState() {}}, URL, URLSearchParams
      });
      const content = get("detail-content");
      const supporting = content.children.find(node => node.tagName === "details");
      assert.equal(walk(supporting).filter(node => node.tagName === "blockquote").length, Number(!stale));
      if (!stale) {
        for (const value of ["A verbatim synthetic excerpt with", quote.locator, quote.source_identity]) assert.ok(supporting.textContent.includes(value));
        const block = walk(supporting).find(node => node.tagName === "blockquote");
        assert.ok(walk(block).some(node => node.className === "scientific-prose"));
        assert.ok(walk(block).some(node => node.className === "math-expression math-inline"));
        assert.ok(!walk(block).some(node => node.className === "math-fallback"));
        assert.ok(!supporting.textContent.includes(source.proposition.claim));
      } else {
        assert.ok(supporting.textContent.includes("Source location"));
        assert.ok(supporting.textContent.includes(source.proposition.location));
        assert.ok(!supporting.textContent.includes(source.proposition.claim));
      }
      assert.equal(walk(content).filter(node => node.className.split(/\s+/).includes("analysis-abstract")).length, 1);
      assert.ok(!walk(content).some(node => node.className === "case-problem" || node.className === "severity-tag no_issue_found"));
      assert.ok(walk(get("case-list")).some(node => node.className === "severity-tag no_issue_found"));
    }
  }
});

test("all current reader views render their actual mathematics with the bundled strict engine", () => {
  const entries = catalog().cases;
  const notation = JSON.parse(fs.readFileSync(path.join(root, "src/elvia/web/math-notation.json"), "utf8")).cases;
  let expressions = 0;
  let problems = 0;
  let brief = 0;
  const renderer = {render(tex, node, options) { expressions++; node.textContent = katex.renderToString(tex, options); }};
  const records = originalRecords();
  assert.equal(records.length, 300);
  assert.equal(Object.values(entries).filter(note => note.problems.length).length, 284);
  for (const source of records) {
    const rendered = create("div");
    const proseSources = [];
    const mathematicalHelpers = {...helpers, prose(tag, text, current, className) {
      proseSources.push(text);
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
      const visibleProblems = entries[source.case_id].problems.filter(problem => problem.assessment !== "not_issue" && problem.severity !== "no_issue_found");
      assert.equal(nodes.filter(node => node.tagName === "h3" && /^problem-\d+$/.test(node.id || "")).length, visibleProblems.length, source.case_id);
      for (const problem of visibleProblems) {
        for (const value of [...problem.analysis, ...problem.result]) assert.ok(proseSources.includes(value), `${source.case_id}: scientific reasoning or scope was omitted`);
        assert.ok(proseSources.includes([...problem.assumptions, ...problem.claim].map(value => value.trim()).filter(Boolean).join(" ")), `${source.case_id}: the complete statement was omitted`);
      }
    }
  }
  assert.equal(problems, Object.values(entries).reduce((sum, note) => sum + note.problems.filter(problem => problem.assessment !== "not_issue" && problem.severity !== "no_issue_found").length, 0));
  assert.equal(brief, 16);
  assert.ok(expressions > problems, "the retained statements and reasoning must render substantive actual mathematics");
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
          ELVIA_SEARCH: require("../src/elvia/web/search.js"), ELVIA_CASE_NOTES: {renderProblems}, ELVIA_ASSESSMENT: require("../src/elvia/web/assessment.js"), addEventListener() {}},
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
      assert.equal(primary.children[0].textContent, "Download report files (.zip)");
      assert.ok(!content.textContent.includes("Download evidence (.zip)"));
      assert.ok(content.children.indexOf(supporting) < content.children.indexOf(primary));
      assert.ok(!content.textContent.includes("Case permalink"));
      assert.ok(!content.textContent.includes("SHA-256"));
      assert.ok(!content.textContent.includes("Preliminary AI analysis."));
      const quotes = notes[source.case_id]?.source_quotes || [];
      if (quotes.length) {
        for (const quote of quotes) {
          assert.ok(supporting.textContent.includes(quote.locator));
          assert.ok(supporting.textContent.includes(quote.source_identity));
        }
      } else assert.ok(supporting.textContent.includes(source.proposition.location));
      assert.deepEqual(walk(supporting).filter(node => node.tagName === "h3").map(node => node.textContent), [
        "Work status", "Original claim and review scope"]);
      assert.ok(!content.textContent.includes("Complete evidence and counterevidence"));
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
      ELVIA_SEARCH: require("../src/elvia/web/search.js"), ELVIA_CASE_NOTES: {renderProblems}, ELVIA_ASSESSMENT: require("../src/elvia/web/assessment.js"), addEventListener() {}},
    location: {hash: "#case=" + source.case_id}, history: {replaceState() {}, pushState() {}}, URL, URLSearchParams
  });
  const content = get("detail-content");
  assert.ok(content.textContent.includes("Version 3"));
  assert.ok(!content.textContent.includes("Stale citation"));
  assert.ok(!content.textContent.includes("Stale credit"));
  assert.ok(!walk(content).some(node => node.attributes.download !== undefined));
});

test("both Atlas lists use the current concise case summary without changing the record", () => {
  const caseNotes = require("../src/elvia/web/case-note.js");
  for (const scriptPath of ["src/elvia/web/atlas.js", "website/atlas-assets/atlas.js"]) {
    for (const stale of [false, true]) {
      const source = JSON.parse(JSON.stringify(originalRecords()[0]));
      source.audit.summary = "Archived assessment: Major.";
      const note = {revision: source.revision + Number(stale), brief: ["A concise bounded summary with its empirical limit."]};
      const elements = new Map();
      const get = id => {
        if (!elements.has(id)) elements.set(id, create("div"));
        return elements.get(id);
      };
      vm.runInNewContext(fs.readFileSync(path.join(root, scriptPath), "utf8"), {
        document: {...document, getElementById: get, querySelectorAll: () => []},
        window: {ELVIA_DATA: {records: [source], case_notes: {[source.case_id]: note}},
          ELVIA_SEARCH: require("../src/elvia/web/search.js"), ELVIA_CASE_NOTES: caseNotes,
          ELVIA_ASSESSMENT: require("../src/elvia/web/assessment.js"), addEventListener() {}},
        location: {hash: ""}, history: {replaceState() {}, pushState() {}}, URL, URLSearchParams
      });
      const summary = walk(get("case-list")).find(node => node.className === "case-summary");
      assert.ok(summary);
      if (stale) assert.ok(!summary.textContent.includes(note.brief[0]));
      else assert.equal(summary.textContent, note.brief[0]);
      assert.equal(source.audit.summary, "Archived assessment: Major.");
    }
  }
});
