/* Explicit TeX presentation only. Canonical record strings are never parsed as HTML. */
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

  return Object.freeze({parseExplicit, renderOptions, renderInto});
});
