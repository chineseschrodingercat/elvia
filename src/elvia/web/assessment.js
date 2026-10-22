/* Preliminary impact labels are separate from scientific adjudication. */
"use strict";
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.ELVIA_ASSESSMENT = api;
})(typeof window === "object" ? window : globalThis, function () {
  const labels = Object.freeze({major: "Major", minor: "Minor", needs_evidence: "Needs Evidence", no_issue_found: "No Issue Found"});
  function assessment(record) {
    const outcome = record.audit.outcome;
    const key = outcome === "needs_evidence" ? "needs_evidence"
      : ["no_issue_found", "scope_clarification"].includes(outcome) ? "no_issue_found"
      : record.concern.severity === "critical" ? "major"
      : record.concern.severity === "moderate" ? "minor" : record.concern.severity;
    return {key, label: labels[key] || labels.needs_evidence};
  }
  function sortByTitle(records) {
    return [...records].sort((a, b) => a.source.title.localeCompare(b.source.title, "en", {sensitivity: "base", numeric: true}) || a.case_id.localeCompare(b.case_id, "en"));
  }
  return Object.freeze({assessment, sortByTitle, labels});
});
