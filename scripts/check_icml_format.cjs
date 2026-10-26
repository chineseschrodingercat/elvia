/* Check retained publication formatting, without re-adjudicating its prose. */
"use strict";
const fs = require("node:fs");
const path = require("node:path");
const math = require("../src/elvia/web/math.js");
const katex = require("../src/elvia/web/vendor/katex/katex.min.js");
const root = process.argv[2] || "studies/icml2025";
const notes = JSON.parse(fs.readFileSync(path.join(root, "case-notes.json"), "utf8"));
const errors = [];
let expressions = 0;
let codeBlocks = 0;
function inspect(value, location) {
  if (typeof value === "string") {
    if (value.startsWith("Code:\n")) { codeBlocks++; return; }
    try {
      for (const part of math.parseExplicit(value)) {
        if (part.kind !== "math") continue;
        katex.renderToString(part.tex, math.renderOptions(part.display));
        expressions++;
      }
    } catch (error) { errors.push(`${location}: ${error.message}`); }
  } else if (Array.isArray(value)) value.forEach((v, i) => inspect(v, `${location}[${i}]`));
  else if (value && typeof value === "object") {
    for (const [k, v] of Object.entries(value)) inspect(v, `${location}.${k}`);
  }
}
for (const [id, note] of Object.entries(notes.cases)) inspect(note, id);
const notation = JSON.parse(fs.readFileSync(path.join(root, "math-notation.json"), "utf8"));
for (const [id, entry] of Object.entries(notation.cases)) {
  if (Object.hasOwn(notes.cases, id)) inspect(entry.replacements.map(item => item.typeset), `${id}.title-notation`);
}
console.log(`${Object.keys(notes.cases).length} retained reports; ${expressions} explicit mathematical expressions; ${codeBlocks} code blocks; ${errors.length} formatting errors`);
for (const error of errors) console.error(error);
process.exitCode = errors.length ? 1 : 0;
