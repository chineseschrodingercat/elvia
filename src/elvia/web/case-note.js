/* Reading order for bounded scientific problems; record text remains literal. */
"use strict";
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.ELVIA_CASE_NOTES = api;
})(typeof window === "object" ? window : globalThis, function () {
  function fallbackProblems(record) {
    if (["no_issue_found", "scope_clarification"].includes(record.audit.outcome)) return [];
    const headings = {
      candidate_issue: "Analysis",
      no_issue_found: "Verification",
      scope_clarification: "Scope analysis",
      known_issue_reproduced: "Known issue analysis"
    };
    const repair = record.repair;
    const applicable = repair.content && ["candidate_issue", "known_issue_reproduced"].includes(record.audit.outcome);
    return [{
      id: "recorded-claim",
      title: "The recorded claim",
      source_location: record.proposition.location,
      claim: [record.proposition.claim],
      assumptions: [record.proposition.domain, ...record.proposition.assumptions].filter(Boolean),
      analysis_heading: headings[record.audit.outcome] || "Analysis",
      analysis: [record.concern.description, ...record.evidence
        .filter(item => item.stance === "support").map(item => item.description)].filter(Boolean),
      result: [record.audit.summary, ...record.audit.limitations],
      repair: applicable ? {
        heading: "Proposed correction",
        paragraphs: [repair.content, ...repair.changed_assumptions, repair.changed_conclusion].filter(Boolean)
      } : null,
      evidence_ids: record.evidence.map(item => item.id)
    }];
  }

  function renderProblems(parent, record, note, helpers) {
    const {create, prose, assessmentLabels = {}} = helpers;
    if (record.audit.outcome === "no_issue_found") {
      const result = create("section", undefined, "case-result no-issue-result");
      result.append(create("p", "No issue was found within the scope of this check."));
      parent.append(result);
      return;
    }
    if (record.audit.outcome === "scope_clarification") {
      const result = create("section", undefined, "case-result scope-result");
      result.append(create("h3", "Scope clarification"), prose("p", record.audit.summary, record));
      parent.append(result);
      return;
    }
    const problems = note && note.revision === record.revision && Array.isArray(note.problems) && note.problems.length
      ? note.problems : fallbackProblems(record);
    const paragraphs = (container, values) => values.forEach(value => container.append(prose("p", value, record)));
    problems.forEach((problem, index) => {
      const section = create("section", undefined, "case-problem");
      const heading = prose("h3", `Problem ${index + 1}. ${problem.title}`, record);
      heading.id = `problem-${index + 1}`;
      section.setAttribute("aria-labelledby", heading.id);
      section.append(heading);
      if (problem.severity) {
        const key = problem.assessment === "not_issue" ? "no_issue_found"
          : problem.assessment === "needs_evidence" ? "needs_evidence"
          : problem.severity === "moderate" ? "minor" : problem.severity;
        const label = assessmentLabels[key];
        if (label) section.append(create("span", label, "severity-tag " + key));
      }
      section.append(create("h4", problem.claim_heading || "Claim in the source (paraphrase)"));
      section.append(prose("p", "Source. " + problem.source_location, record, "source-citation"));
      paragraphs(section, problem.claim);
      if (problem.assumptions.length) {
        section.append(create("h4", "Conditions"));
        const list = create("ul");
        problem.assumptions.forEach(value => list.append(prose("li", value, record)));
        section.append(list);
      }
      section.append(create("h4", problem.analysis_heading));
      paragraphs(section, problem.analysis);
      section.append(create("h4", "Finding and scope"));
      paragraphs(section, problem.result);
      if (problem.repair) {
        section.append(create("h4", problem.repair.heading));
        paragraphs(section, problem.repair.paragraphs);
      }
      parent.append(section);
    });
  }
  return {renderProblems, fallbackProblems};
});
