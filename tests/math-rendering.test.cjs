"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");
const math = require("../src/elvia/web/math.js");
const katex = require("../src/elvia/web/vendor/katex/katex.min.js");

class Node {
  constructor(tag, ownerDocument, text = "") {
    this.tagName = tag;
    this.ownerDocument = ownerDocument;
    this.children = [];
    this.attributes = {};
    this.className = "";
    this._text = text;
  }
  get textContent() { return this._text + this.children.map(node => node.textContent).join(""); }
  set textContent(value) { this._text = value; this.children = []; }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this._text = ""; this.children = nodes; }
  setAttribute(key, value) { this.attributes[key] = value; }
}
const document = {
  createElement(tag) { return new Node(tag, this); },
  createTextNode(text) { return new Node("#text", this, text); },
  createDocumentFragment() { return new Node("#fragment", this); }
};
const element = () => document.createElement("p");
const renderer = {
  render(tex, node, options) {
    node.textContent = katex.renderToString(tex, options);
    node.rendered = {tex, options};
  }
};

test("explicit inline and display delimiters preserve surrounding prose", () => {
  assert.deepEqual(math.parseExplicit("Let \\(x_i\\) satisfy \\[\\sum_i x_i=1.\\] Done."), [
    {kind: "text", text: "Let "},
    {kind: "math", tex: "x_i", display: false},
    {kind: "text", text: " satisfy "},
    {kind: "math", tex: "\\sum_i x_i=1.", display: true},
    {kind: "text", text: " Done."}
  ]);
});

test("scientific prose typesets counts, explicit comparisons and statistical numbers", () => {
  const node = element();
  node.className = "scientific-prose";
  const source = "There are 19 known relations; p<0.01, error -0.25 and power 2e-3 with 95% coverage.";
  assert.equal(math.renderInto(node, source, {renderer}).status, "rendered");
  const rendered = node.children[0].children.filter(child => child.rendered).map(child => child.rendered.tex);
  assert.deepEqual(rendered, ["19", "p<0.01,", "-0.25", "2\\times10^{-3}", "95\\%"]);
  assert.equal(source, "There are 19 known relations; p<0.01, error -0.25 and power 2e-3 with 95% coverage.");
});

test("scientific numbers preserve literal source identifiers and do not guess missing relations", () => {
  const node = element();
  node.className = "scientific-prose";
  const source = "See p. 19, Eq. (2), Table 3 and Section 4.1; DOI 10.1234/abc19; arXiv:2412.06512v1; `data/v2/file19.py`; C2, m256 and p0.0323. The observed value is 0.0323.";
  assert.equal(math.renderInto(node, source, {renderer}).status, "rendered");
  const children = node.children[0].children;
  assert.deepEqual(children.filter(child => child.rendered).map(child => child.rendered.tex), ["0.0323."]);
  const literal = children.filter(child => child.tagName === "#text").map(child => child.textContent).join("");
  for (const protectedText of ["p. 19", "Eq. (2)", "Table 3", "Section 4.1", "10.1234/abc19", "arXiv:2412.06512v1", "data/v2/file19.py", "C2", "m256", "p0.0323"]) assert.ok(literal.includes(protectedText), protectedText);
});

test("scientific numeric fractions retain their slash and protect dates and literal sources", () => {
  const node = element();
  node.className = "scientific-prose";
  const source = "Probability 1/2, discrepancy -27/8192000 and p=3/4. Keep 2026/10/26, pp. 1/2, https://example.org/1/2, `1/2`, data/1/2.json and id1/2 literal.";
  math.renderInto(node, source, {renderer});
  const children = node.children[0].children;
  assert.deepEqual(children.filter(child => child.rendered).map(child => child.rendered.tex), ["1/2,", "-27/8192000", "p=3/4."]);
  const literal = children.filter(child => child.tagName === "#text").map(child => child.textContent).join("");
  for (const value of ["2026/10/26", "pp. 1/2", "https://example.org/1/2", "`1/2`", "data/1/2.json", "id1/2"]) assert.ok(literal.includes(value), value);
  assert.equal(math.renderInto(element(), "Source location 1/2", {renderer}).status, "plain");
});

test("scientific numeric arithmetic keeps full equalities and operators in mathematical type", () => {
  const node = element();
  node.className = "scientific-prose";
  math.renderInto(node, "Compare 1+1=2, 0.2-0.8=-0.6, 3*(3/2)=9/2 and 8 > 141/20 = 7.05. Rate 45.6%+11.2%=56.8%.", {renderer});
  assert.deepEqual(node.children[0].children.filter(child => child.rendered).map(child => child.rendered.tex), [
    "1+1=2,", "0.2-0.8=-0.6,", "3\\cdot(3/2)=9/2", "8 > 141/20 = 7.05.", "45.6\\%+11.2\\%=56.8\\%."
  ]);
});

test("numeric arithmetic preserves dates, code, source labels and scientific exponents", () => {
  const node = element();
  node.className = "scientific-prose";
  const source = "At 2026-10-27 and 2026/10/27, see pp. 1-2, Eq. (1), https://example.org/1+1=2, `1+1=2`, `id1+2` and value 2e-3+1e-3=3e-3.";
  math.renderInto(node, source, {renderer});
  const children = node.children[0].children;
  assert.deepEqual(children.filter(child => child.rendered).map(child => child.rendered.tex), ["2\\times10^{-3}+1\\times10^{-3}=3\\times10^{-3}."]);
  const literal = children.filter(child => child.tagName === "#text").map(child => child.textContent).join("");
  for (const value of ["2026-10-27", "2026/10/27", "pp. 1-2", "Eq. (1)", "https://example.org/1+1=2", "`1+1=2`", "id1+2"]) assert.ok(literal.includes(value), value);
});

test("numeric presentation is opt-in, preserves explicit mathematics and rejects prose-only replacement drift", () => {
  const plain = element();
  assert.equal(math.renderInto(plain, "Page 19, DOI 10.1234/abc", {renderer}).status, "plain");
  assert.equal(plain.textContent, "Page 19, DOI 10.1234/abc");
  const node = element();
  node.className = "scientific-prose";
  math.renderInto(node, "Use \\(x_i=1\\) with 19 observations.", {renderer});
  assert.deepEqual(node.children[0].children.filter(child => child.rendered).map(child => child.rendered.tex), ["x_i=1", "19"]);
  const mapped = element();
  mapped.className = "scientific-prose";
  math.renderInto(mapped, "19 observations", {renderer, replacements: [{source: "19 observations", typeset: "20 invented observations"}]});
  assert.deepEqual(mapped.children[0].children.filter(child => child.rendered).map(child => child.rendered.tex), ["19"]);
});

test("scientific Unicode variables and operators use math fonts without changing literal sources", () => {
  const node = element();
  node.className = "scientific-prose";
  const source = "The parameter θ has uncertainty ±0.1, α ≤ β and x − y → ∞. See `θ±.py`, sources/θ.py, https://example.org/α and Eq. (2).";
  assert.equal(math.renderInto(node, source, {renderer}).status, "rendered");
  const children = node.children[0].children;
  assert.deepEqual(children.filter(child => child.rendered).map(child => child.rendered.tex), ["\\theta", "\\pm", "0.1,", "\\alpha", "\\leq", "\\beta", "-", "\\to", "\\infty."]);
  const literal = children.filter(child => child.tagName === "#text").map(child => child.textContent).join("");
  for (const text of ["`θ±.py`", "sources/θ.py", "https://example.org/α", "Eq. (2)"]) assert.ok(literal.includes(text), text);
  const citation = element();
  citation.className = "source-citation";
  assert.equal(math.renderInto(citation, "θ et al., Table 2 ± appendix", {renderer}).status, "plain");
  assert.equal(citation.textContent, "θ et al., Table 2 ± appendix");
});

test("distinct Unicode Greek variants retain distinct TeX glyphs", () => {
  assert.deepEqual(math.parseScientific("φ ϕ ε ϵ θ ϑ ρ ϱ π ϖ σ ς κ ϰ").filter(part => part.kind === "math").map(part => part.tex), [
    "\\varphi", "\\phi", "\\varepsilon", "\\epsilon", "\\theta", "\\vartheta", "\\rho", "\\varrho", "\\pi", "\\varpi", "\\sigma", "\\varsigma", "\\kappa", "\\varkappa"
  ]);
  assert.deepEqual(math.parseScientific("2e−3").filter(part => part.kind === "math").map(part => part.tex), ["2\\times10^{-3}"]);
});

test("currency, code-like strings and escaped delimiter text stay literal", () => {
  const source = "$5, $$x$$, x_i=1, \\\\(literal\\\\)";
  assert.deepEqual(math.parseExplicit(source), [{kind: "text", text: source}]);
});

test("sentence punctuation stays on a display equation instead of starting a prose line", () => {
  const node = element();
  const source = "Use \\[x+y\\], where \\(x=1\\), then \\[y=2\\]. Done.";
  assert.equal(math.renderInto(node, source, {renderer}).status, "rendered");
  const children = node.children[0].children;
  assert.deepEqual(children.filter(child => child.rendered).map(child => child.rendered.tex), ["x+y,", "x=1,", "y=2."]);
  assert.deepEqual(children.filter(child => child.tagName === "#text").map(child => child.textContent), ["Use ", " where ", " then ", " Done."]);
});

test("inline sentence punctuation stays inside rendered math instead of a separate text node", () => {
  const node = element();
  const source = "Let \\(x=1\\), then \\(y=2\\). Next.";
  assert.equal(math.renderInto(node, source, {renderer}).status, "rendered");
  const children = node.children[0].children;
  const equations = children.filter(child => child.rendered);
  assert.deepEqual(equations.map(child => child.rendered.tex), ["x=1,", "y=2."]);
  assert.ok(equations.every(child => child.rendered.options.displayMode === false));
  assert.deepEqual(children.filter(child => child.tagName === "#text").map(child => child.textContent), ["Let ", " then ", " Next."]);
});

test("unclosed, nested or mismatched delimiters fail explicitly", () => {
  for (const source of ["\\(x", "\\[x\\)", "\\(x\\[y\\]\\)", "\\(\\)"]) {
    assert.throws(() => math.parseExplicit(source));
  }
});

test("exact replacement chooses the current record's presentation only", () => {
  const node = element();
  const options = {renderer, replacements: [{source: "x=1/2", typeset: "\\(x=\\frac12\\)"}]};
  assert.equal(math.renderInto(node, "x=1/2", options).status, "rendered");
  assert.ok(node.textContent.includes("katex-mathml"));
  assert.equal(math.renderInto(node, " prefix x=1/2", options).status, "plain");
  assert.equal(node.textContent, " prefix x=1/2");
});

test("source HTML remains literal text and never becomes a DOM element", () => {
  const node = element();
  const source = '<img src=x onerror="alert(1)"> \\(x^2\\)';
  math.renderInto(node, source, {renderer});
  const fragment = node.children[0];
  assert.equal(fragment.children[0].tagName, "#text");
  assert.equal(fragment.children[0].textContent, '<img src=x onerror="alert(1)"> ');
  assert.equal(fragment.children[1].tagName, "span");
});

test("render options prohibit trusted extensions and isolate macro state", () => {
  const calls = [];
  const spy = {render(tex, node, options) { calls.push(options); renderer.render(tex, node, options); }};
  math.renderInto(element(), "\\(x\\), \\(y\\)", {renderer: spy});
  assert.equal(calls.length, 2);
  for (const options of calls) {
    assert.equal(options.trust, false);
    assert.equal(options.strict, "error");
    assert.equal(options.throwOnError, true);
    assert.equal(options.output, "htmlAndMathml");
    assert.equal(options.maxSize, 20);
    assert.equal(options.maxExpand, 1000);
  }
  assert.notEqual(calls[0].macros, calls[1].macros);
});

test("hostile and unsupported TeX restores exact original source with an accessible visible note", () => {
  for (const tex of [
    "\\href{https://evil.example}{x}",
    "\\includegraphics{https://evil.example/x.png}",
    "\\htmlStyle{color:red}{x}",
    "\\notACommand{x}",
    "\\def\\a{\\a}\\a"
  ]) {
    const node = element();
    const source = "Recorded formula: " + tex;
    const result = math.renderInto(node, source, {
      renderer, replacements: [{source, typeset: "Recorded formula: \\(" + tex + "\\)"}]
    });
    assert.equal(result.status, "fallback", tex);
    assert.equal(node.children[0].textContent, source);
    assert.equal(node.children[1].attributes.role, "note");
    assert.match(node.children[1].textContent, /math shown as source/i);
  }
});

test("late renderer failure does not expose a partially rendered paragraph", () => {
  const node = element();
  const source = "Two expressions: x=1; y=2.";
  const result = math.renderInto(node, source, {
    renderer,
    replacements: [{source, typeset: "Two expressions: \\(x=1\\); \\(\\badcommand{y}\\)."}]
  });
  assert.equal(result.status, "fallback");
  assert.equal(node.children[0].textContent, source);
  assert.ok(!node.textContent.includes("katex-mathml"));
});

test("missing renderer and malformed mapping preserve original canonical text", () => {
  const source = "canonical x=1/2";
  const mappings = ["\\(x=\\frac12\\)", "\\(x=1"];
  for (const typeset of mappings) {
    const node = element();
    assert.equal(math.renderInto(node, source, {
      renderer: null, replacements: [{source, typeset}]
    }).status, "fallback");
    assert.equal(node.children[0].textContent, source);
  }
});

test("display equations have a labeled keyboard-scrollable region; inline math does not", () => {
  const node = element();
  math.renderInto(node, "\\(x\\) and \\[x=\\frac12\\]", {renderer});
  const inline = node.children[0].children[0];
  const display = node.children[0].children[2];
  assert.equal(inline.attributes.tabindex, undefined);
  assert.equal(display.attributes.tabindex, "0");
  assert.equal(display.attributes.role, "region");
  assert.match(display.attributes["aria-label"], /equation/i);
});

test("legacy pilot presentation is absent from the distributed toolkit", () => {
  const fs = require("node:fs");
  for (const name of ["math-notation.json", "case-notes.json"]) {
    const catalog = JSON.parse(fs.readFileSync(path.join(__dirname, "../src/elvia/web", name), "utf8"));
    assert.deepEqual(catalog, {format_version: 1, cases: {}});
  }
});
