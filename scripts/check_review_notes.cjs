/* Inspect every curated formula with the exact bundled offline renderer. */
"use strict";
const fs = require("node:fs");
const path = require("node:path");
const {createHash} = require("node:crypto");
const math = require("../src/elvia/web/math.js");
const katex = require("../src/elvia/web/vendor/katex/katex.min.js");
const folder = process.argv[2] || "studies/neurips2025/records";
const root = folder.endsWith("records") ? path.dirname(folder) : folder;
const auditMode = !fs.existsSync(path.join(root, "case-notes.json"));
const inputs = auditMode
  ? fs.readdirSync(root).filter(name => /^\d{4}\.json$/.test(name)).map(name => [name, JSON.parse(fs.readFileSync(path.join(root, name), "utf8"))])
  : Object.entries(JSON.parse(fs.readFileSync(path.join(root, "case-notes.json"), "utf8")).cases);
const errors = [];
let expressions = 0;
function checkProse(text, location) {
  if (/\\{2,}[()[\]]/.test(text)) throw Error("escaped math delimiter outside a rendered expression");
  if (/\\[A-Za-z]+\b/.test(text)) throw Error("unconverted LaTeX outside explicit math");
  if (/[\u0370-\u03ff\u2070-\u209f∑∏√≤≥≈≠∈∉∥∇∂∞×±∝∼−]/u.test(text)
      || /\b[A-Za-z][A-Za-z0-9_]*\s*(?:=|!=|<=|>=)\s*[A-Za-z0-9({+-]/.test(text)
      || /\w\^\{?[A-Za-z0-9+-]/.test(text)
      || /\b(?:sqrt|log|exp|KL|N)\([^)]*[A-Za-z0-9]/.test(text)) {
    throw Error("unmarked mathematics in prose");
  }
  const prose = text.replace(/\b(?:float|bfloat|uint|int|fp|bf)\d+\b/g, "type")
    .replace(/[\w/.-]+\.(?:py|cpp|json|csv|ya?ml|sh|m|ipynb)\b/g, "file");
  if (/\b[a-z]{3,}[−-]?(?:\d|\.\d)|\d(?:and|versus|tokens|samples|dimensional)\b/.test(prose)) {
    throw Error("cramped word/number in prose");
  }
  if (/\b(?:verification|validation|validating|sources|reports|backups)\/\d{4}\b/i.test(text)
      || /\b(?:our|unofficial|local|saved|retained|supplied)\s+(?:(?:private|local|validation|verification|source)\s+)*(?:bundle|backup|report|files|snapshots)\b/i.test(text)) {
    throw Error("internal evidence reference in the scientific narrative");
  }
}
function inspect(value, location) {
  if (typeof value === "string") {
    try {
      if (/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f\ufffd]/u.test(value)) throw Error("control or replacement character in prose or mathematics");
      for (const part of math.parseExplicit(value)) {
        if (part.kind === "math") {
          if (/\\(?:input|include|write|openout|read|catcode|def|newcommand|special|href|url|html\w*)\b/.test(part.tex)) throw Error("non-mathematical TeX command");
          katex.renderToString(part.tex, math.renderOptions(part.display));
          expressions++;
        } else if (!/\.(?:version|provenance_note)$/.test(location) && !/^(?:\d{4}\.json|.+\.latest\.verification)\.title$/.test(location)) checkProse(part.text, location);
      }
      if (/[A-Za-z0-9]\\[([]|\\[)\]][A-Za-z0-9]/.test(value)) throw Error("cramped word/math boundary in prose");
    } catch (error) { errors.push(`${location}: ${error.message}`); }
  } else if (Array.isArray(value)) value.forEach((item, i) => inspect(item, `${location}[${i}]`));
  else if (value && typeof value === "object") {
    for (const [key, item] of Object.entries(value)) if (!/^(source_checks|pdf_path|record_sha256|pdf_sha256|source_sha256|raw_report_sha256|pdf_url|landing_url|report_id|retrieved_at|id|evidence_ids)$/.test(key)) inspect(item, `${location}.${key}`);
  }
}
for (const [name, value] of inputs) inspect(value, name);
let recordCount = 0;
let verificationCount = 0;
function readVerification(artifact) {
  const relative = artifact.path;
  if (!relative || relative === "." || relative.includes("\\") || relative.includes(":")
      || path.posix.isAbsolute(relative) || relative.split("/").includes("..")) {
    throw Error("verification artifact path must be portable and dataset-relative");
  }
  const base = fs.realpathSync(root);
  const resolved = fs.realpathSync(path.resolve(base, ...relative.split("/")));
  const contained = path.relative(base, resolved);
  if (!contained || contained === ".." || contained.startsWith(".." + path.sep) || path.isAbsolute(contained)) {
    throw Error("verification artifact path escapes the dataset");
  }
  // Hash and parse the same bytes, so a second read cannot substitute content.
  const bytes = fs.readFileSync(resolved);
  if (typeof artifact.sha256 !== "string" || !/^[a-f0-9]{64}$/.test(artifact.sha256)
      || createHash("sha256").update(bytes).digest("hex") !== artifact.sha256) {
    throw Error("verification artifact hash mismatch");
  }
  return JSON.parse(bytes.toString("utf8"));
}
if (!auditMode) {
  const records = new Map();
  const recordFolder = path.join(root, "records");
  for (const name of fs.readdirSync(recordFolder).filter(name => name.endsWith(".json"))) {
    const record = JSON.parse(fs.readFileSync(path.join(recordFolder, name), "utf8"));
    if (!records.has(record.case_id) || record.revision > records.get(record.case_id).revision) records.set(record.case_id, record);
  }
  for (const record of records.values()) {
    inspect({summary: record.audit.summary, limitations: record.audit.limitations,
      review_scope: record.source.review_scope, proposition: record.proposition,
      concern: record.concern.description, repair: record.repair.content,
      evidence: record.evidence.map(item => ({description: item.description, method: item.method}))}, `${record.case_id}.latest`);
    for (const item of record.evidence) {
      const artifact = item.artifact;
      if (!artifact || typeof artifact.path !== "string" || !/(?:^|[\\/])verification\.json$/.test(artifact.path)) continue;
      const location = `${record.case_id}.latest.verification`;
      try {
        inspect(readVerification(artifact), location);
        verificationCount++;
      } catch (error) { errors.push(`${location}: ${error.message}`); }
    }
  }
  recordCount = records.size;
}
console.log(`${inputs.length} notes${recordCount ? ` and ${recordCount} latest records` : ""}${verificationCount ? ` and ${verificationCount} latest verification artifacts` : ""}, ${expressions} mathematical expressions, ${errors.length} errors`);
for (const error of errors) console.error(error);
if (errors.length) process.exitCode = 1;
