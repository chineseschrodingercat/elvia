/* Explicit TeX and bounded scientific-number typography; never parse record HTML. */
"use strict";
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.ELVIA_MATH = api;
})(typeof window === "object" ? window : globalThis, function () {
  function delimiterAt(text, index) {
    if (text[index] !== "\\" || !"()[]".includes(text[index + 1] || " ")) return null;
    let preceding = 0;
    for (let i = index - 1; i >= 0 && text[i] === "\\"; i--) preceding++;
    return preceding % 2 === 0 ? text.slice(index, index + 2) : null;
  }

  function parseExplicit(text) {
    if (typeof text !== "string") throw new TypeError("Mathematical presentation must be text.");
    const parts = [];
    let start = 0;
    let opening = null;
    for (let i = 0; i < text.length - 1; i++) {
      const delimiter = delimiterAt(text, i);
      if (!delimiter) continue;
      if (!opening) {
        if (delimiter !== "\\(" && delimiter !== "\\[") throw new Error("Unmatched math delimiter.");
        if (i > start) parts.push({kind: "text", text: text.slice(start, i)});
        opening = delimiter;
        start = i + 2;
      } else {
        const closing = opening === "\\(" ? "\\)" : "\\]";
        if (delimiter !== closing) throw new Error("Nested or mismatched math delimiter.");
        const tex = text.slice(start, i);
        if (!tex.trim() || tex.length > 10000) throw new Error("Empty or oversized math expression.");
        parts.push({kind: "math", tex, display: opening === "\\["});
        opening = null;
        start = i + 2;
      }
      i++;
    }
    if (opening) throw new Error("Unclosed math delimiter.");
    if (start < text.length || !parts.length) parts.push({kind: "text", text: text.slice(start)});
    return parts;
  }

  function renderOptions(display) {
    return {
      displayMode: display,
      output: "htmlAndMathml",
      trust: false,
      strict: "error",
      throwOnError: true,
      maxSize: 20,
      maxExpand: 1000,
      macros: {}
    };
  }

  function numberTex(value) {
    value = value.replace(/−/g, "-");
    const percentage = value.endsWith("%");
    if (percentage) value = value.slice(0, -1);
    const exponent = value.match(/^(.+)[eE]([+-]?\d+)$/);
    const tex = exponent ? `${exponent[1]}\\times10^{${exponent[2].replace(/^\+/, "")}}` : value;
    return tex.replace(/,/g, "{,}") + (percentage ? "\\%" : "");
  }

  function scientificText(text) {
    // Restrict this to explicitly marked scientific prose. Source locations,
    // literal code/URLs/identifiers and existing equations are not reinterpreted.
    const number = String.raw`[+−-]?(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|\.\d+)(?:[eE][+−-]?\d+)?%?`;
    const fraction = String.raw`[+−-]?(?:\d+(?:\.\d+)?|\.\d+)\/(?:\d+(?:\.\d+)?|\.\d+)`;
    const left = String.raw`(?<![A-Za-z0-9_./:\\-])`;
    const right = String.raw`(?![A-Za-z0-9_/:\\-]|\.[A-Za-z0-9_])`;
    const quantity = new RegExp(`${left}(?:([A-Za-z])\\s*(<=|>=|!=|=|<|>|≤|≥|≠|≈)\\s*)?(${fraction}|${number})${right}`, "g");
    const numeric = `(?:${fraction}|${number})`;
    const arithmeticOperator = String.raw`(?:<=|>=|!=|[+*/=<>≤≥≠≈×−-])`;
    const flatNumeric = `${numeric}(?:\\s*${arithmeticOperator}\\s*${numeric})*`;
    const operand = `(?:${numeric}|\\(${flatNumeric}\\))`;
    const arithmetic = new RegExp(`${left}${operand}(?:\\s*${arithmeticOperator}\\s*${operand})+${right}`, "g");
    const references = String.raw`\b(?:Tables?|Figures?|Figs?\.?|Eq(?:uation)?s?\.?|Sections?|Secs?\.?|Algorithms?|Theorems?|Lemmas?|Corollar(?:y|ies)|Propositions?|Definitions?|Problems?|Pages?|pp?\.)(?:\s*\(?[A-Z]?\d+(?:\.\d+)*(?:[-–]\d+(?:\.\d+)*)?\)?)(?:\s*(?:,|and|[-–])\s*\(?[A-Z]?\d+(?:\.\d+)*\)?)*`;
    const sourceFile = String.raw`(?:[\p{L}\p{N}_.-]+[/\\])*[\p{L}\p{N}_±.-]+\.(?:py|ipynb|cpp|cu|sh|yaml|yml|json|txt|md|pdf)\b`;
    const literal = new RegExp(String.raw`\x60[^\x60]*\x60|https?:\/\/[^\s]+|\bwww\.[^\s]+|\b(?:doi|arxiv)\s*:[^\s]+|\b10\.\d{4,9}\/[^\s]+|${sourceFile}|${references}`, "giu");
    // These are direct glyph-to-command substitutions, not inferred equations.
    // Superscripts, subscripts and compact missing relations require source TeX.
    const glyphs = {
      α: "\\alpha", β: "\\beta", γ: "\\gamma", δ: "\\delta", ε: "\\varepsilon", ζ: "\\zeta", η: "\\eta", θ: "\\theta",
      ι: "\\iota", κ: "\\kappa", λ: "\\lambda", μ: "\\mu", ν: "\\nu", ξ: "\\xi", π: "\\pi", ρ: "\\rho",
      σ: "\\sigma", τ: "\\tau", υ: "\\upsilon", φ: "\\varphi", χ: "\\chi", ψ: "\\psi", ω: "\\omega",
      ϕ: "\\phi", ϵ: "\\epsilon", ϑ: "\\vartheta", ϱ: "\\varrho", ϖ: "\\varpi", ς: "\\varsigma", ϰ: "\\varkappa",
      Γ: "\\Gamma", Δ: "\\Delta", Θ: "\\Theta", Λ: "\\Lambda", Ξ: "\\Xi", Π: "\\Pi", Σ: "\\Sigma", Υ: "\\Upsilon", Φ: "\\Phi", Ψ: "\\Psi", Ω: "\\Omega",
      "−": "-", "×": "\\times", "±": "\\pm", "∓": "\\mp", "·": "\\cdot", "⊥": "\\perp", "∈": "\\in", "∉": "\\notin",
      "⊂": "\\subset", "⊆": "\\subseteq", "∪": "\\cup", "∩": "\\cap", "∀": "\\forall", "∃": "\\exists", "∞": "\\infty",
      "≈": "\\approx", "≤": "\\leq", "≥": "\\geq", "≠": "\\ne", "≡": "\\equiv", "∝": "\\propto", "∇": "\\nabla", "∂": "\\partial",
      "→": "\\to", "↔": "\\leftrightarrow", "⇒": "\\Rightarrow", "⇔": "\\Leftrightarrow", "ℝ": "\\mathbb{R}", "ℂ": "\\mathbb{C}", "ℤ": "\\mathbb{Z}", "ℕ": "\\mathbb{N}", "ℚ": "\\mathbb{Q}", "ℓ": "\\ell"
    };
    const symbol = /[−×±∓·⊥∈∉⊂⊆∪∩∀∃∞≈≤≥≠≡∝∇∂→↔⇒⇔ℝℂℤℕℚℓ]|(?<![\p{L}\p{N}_])[αβγδεζηθικλμνξπρστυφχψωΓΔΘΛΞΠΣΥΦΨΩϕϵϑϱϖςϰ](?![\p{L}\p{N}_])/gu;
    const parts = [];
    const append = value => {
      if (!value) return;
      const previous = parts[parts.length - 1];
      if (previous?.kind === "text") previous.text += value;
      else parts.push({kind: "text", text: value});
    };
    const symbols = value => {
      let start = 0;
      for (const match of value.matchAll(symbol)) {
        append(value.slice(start, match.index));
        parts.push({kind: "math", tex: glyphs[match[0]], display: false});
        start = match.index + match[0].length;
      }
      append(value.slice(start));
    };
    const numbers = value => {
      let start = 0;
      for (const match of value.matchAll(quantity)) {
        symbols(value.slice(start, match.index));
        const operator = {"<=": "\\leq", ">=": "\\geq", "!=": "\\ne", "≤": "\\leq", "≥": "\\geq", "≠": "\\ne", "≈": "\\approx"}[match[2]] || match[2] || "";
        parts.push({kind: "math", tex: (match[1] || "") + operator + numberTex(match[3]), display: false});
        start = match.index + match[0].length;
      }
      symbols(value.slice(start));
    };
    const quantities = value => {
      let start = 0;
      for (const match of value.matchAll(arithmetic)) {
        // A slash or hyphen alone can be a date, source label or range. Only
        // explicit numeric arithmetic/comparisons use the complete expression.
        if (!/[+*=<>≤≥≠≈×]/.test(match[0])) continue;
        numbers(value.slice(start, match.index));
        const operators = {"<=": "\\leq", ">=": "\\geq", "!=": "\\ne", "≤": "\\leq", "≥": "\\geq", "≠": "\\ne", "≈": "\\approx", "×": "\\times", "*": "\\cdot", "−": "-"};
        const tex = match[0].replace(new RegExp(number, "g"), numberTex)
          .replace(/<=|>=|!=|[≤≥≠≈×*−]/g, token => operators[token]);
        parts.push({kind: "math", tex, display: false});
        start = match.index + match[0].length;
      }
      numbers(value.slice(start));
    };
    let start = 0;
    for (const match of text.matchAll(literal)) {
      quantities(text.slice(start, match.index));
      append(match[0]);
      start = match.index + match[0].length;
    }
    quantities(text.slice(start));
    return parts;
  }

  function parseScientific(text) {
    return parseExplicit(text).flatMap(part => part.kind === "text" ? scientificText(part.text) : [part]);
  }

  function fallback(node, source) {
    const document = node.ownerDocument;
    const note = document.createElement("span");
    note.className = "math-rendering-note";
    note.setAttribute("role", "note");
    note.textContent = " (math shown as source)";
    node.replaceChildren(document.createTextNode(source), note);
    return {status: "fallback", expressions: 0};
  }

  function renderInto(node, source, options = {}) {
    const document = node.ownerDocument;
    const replacements = Array.isArray(options.replacements) ? options.replacements : [];
    const replacement = replacements.find(item => item && item.source === source);
    const typeset = replacement ? replacement.typeset : source;
    let parts;
    try { parts = parseExplicit(typeset); }
    catch { return fallback(node, source); }
    // A replacement must include real explicit mathematics; number styling
    // cannot be used to turn an unrelated prose rewrite into a valid mapping.
    if (replacement && !parts.some(part => part.kind === "math")) {
      try { parts = parseExplicit(source); }
      catch { return fallback(node, source); }
    }
    const classes = typeof node.className === "string" ? node.className.split(/\s+/) : [];
    const scientific = options.scientificNumbers === true || options.scientificNumbers !== false &&
      (classes.includes("scientific-prose") || classes.includes("case-summary"));
    if (scientific) parts = parts.flatMap(part => part.kind === "text" ? scientificText(part.text) : [part]);
    const expressions = parts.filter(part => part.kind === "math").length;
    if (!expressions) {
      // A presentation entry cannot silently rewrite non-mathematical prose.
      node.replaceChildren(document.createTextNode(source));
      return {status: "plain", expressions: 0};
    }
    const renderer = options.renderer;
    if (!renderer || typeof renderer.render !== "function") return fallback(node, source);
    const fragment = document.createDocumentFragment();
    try {
      for (let index = 0; index < parts.length; index++) {
        const part = parts[index];
        if (part.kind === "text") {
          fragment.append(document.createTextNode(part.text));
          continue;
        }
        // These extensions require trusted URLs or HTML attributes. Reject them
        // explicitly as well as setting KaTeX trust:false, so the source remains
        // available rather than displaying an unsupported-command approximation.
        if (/\\(?:href|url|includegraphics|htmlClass|htmlId|htmlStyle|htmlData)\b/.test(part.tex)) {
          throw new Error("Trusted TeX extensions are disabled.");
        }
        const span = document.createElement("span");
        span.className = part.display ? "math-expression math-display" : "math-expression math-inline";
        if (part.display) {
          span.setAttribute("tabindex", "0");
          span.setAttribute("role", "region");
          span.setAttribute("aria-label", "Display equation; scroll horizontally if needed");
        }
        // Keep sentence punctuation with math so wrapping cannot strand it
        // at the beginning of the following prose line.
        let tex = part.tex;
        const next = parts[index + 1];
        if (next?.kind === "text" && /^[,;:.!?](?=\s|$)/.test(next.text)) {
          tex += next.text[0];
          next.text = next.text.slice(1);
        }
        renderer.render(tex, span, renderOptions(part.display));
        fragment.append(span);
      }
    } catch { return fallback(node, source); }
    node.replaceChildren(fragment);
    return {status: "rendered", expressions};
  }

  return Object.freeze({parseExplicit, parseScientific, renderOptions, renderInto});
});
