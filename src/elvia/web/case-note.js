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
      result: [record.audit.summary],
      brief: briefPoints(record),
      repair: applicable ? {
        heading: "Proposed correction",
        paragraphs: [repair.content, ...repair.changed_assumptions, repair.changed_conclusion].filter(Boolean)
      } : null,
      evidence_ids: record.evidence.map(item => item.id)
    }];
  }

  function briefPoints(record, problem, note) {
    if (problem && Array.isArray(problem.brief) && problem.brief.length) return [...problem.brief];
    if (!problem && note && note.revision === record.revision && Array.isArray(note.brief) && note.brief.length) return [...note.brief];
    const groups = [[], []];
    for (const raw of problem ? problem.result : [record.audit.summary]) {
      let text = raw.replace(/^Recorded evidence:\s*/, "");
      const qualifier = /^(?:Counterevidence|Version scope|Impact\. Not established|Not established|Scope|Limitations?|Boundary)\b/i.test(text);
      text = text.replace(/^(?:Result[:.]|Impact:)\s*/, "")
        .replace(/^Archived assessment: (?:Major|Minor|Needs Evidence|No Issue Found)\.\s*/, "");
      if (text.replace(/[.\s]/g, "")) groups[Number(qualifier)].push(text);
    }
    const points = groups.filter(group => group.length).map(group => group.join(" "));
    const fallback = {
      no_issue_found: "No issue was found within the inspected scope.",
      scope_clarification: "The recorded check clarifies the scope of the inspected claim.",
      needs_evidence: "The inspected question remains unresolved; additional evidence is needed.",
      known_issue_reproduced: "The recorded check reproduces a previously documented issue.",
      candidate_issue: "The record describes a candidate issue in the inspected claim; independent review is pending."
    };
    return points.length ? points : [fallback[record.audit.outcome]];
  }

  function renderProblems(parent, record, note, helpers) {
    const {create, prose, assessmentLabels = {}} = helpers;
    const paragraphs = (container, values) => values.forEach(value => container.append(prose("p", value, record)));
    const recordEvidence = container => {
      const shared = create("section", undefined, "case-scope-evidence");
      shared.id = "case-scope-evidence";
      shared.append(create("h4", "Case-wide scope and evidence"));
      if (record.audit.limitations.length) {
        shared.append(create("h5", "Scope and limitations"));
        const list = create("ul");
        record.audit.limitations.forEach(value => list.append(prose("li", value, record)));
        shared.append(list);
      }
      shared.append(create("h5", "Recorded assessment"), prose("p", record.concern.description, record));
      for (const evidence of record.evidence) {
        if (!evidence.description) continue;
        const label = {support: "Supporting evidence", rebuttal: "Counterevidence", context: "Context"}[evidence.stance] || "Recorded evidence";
        shared.append(create("h5", label), prose("p", evidence.description, record));
      }
      container.append(shared);
    };
    const brief = (container, problem) => {
      const aside = create("aside", undefined, "finding-brief");
      aside.setAttribute("aria-label", "Finding at a glance");
      aside.append(create("h4", "Finding at a glance"));
      const list = create("ul");
      briefPoints(record, problem, note).forEach(value => list.append(prose("li", value, record)));
      aside.append(list);
      container.append(aside);
    };
    const disclosure = (container, id, label) => {
      const details = create("details", undefined, "evidence-details");
      details.id = id;
      const content = create("div", undefined, "evidence-content");
      details.append(create("summary", label), content);
      container.append(details);
      return content;
    };
    const caseEvidence = () => {
      const content = disclosure(parent, "case-evidence", "Evidence and reasoning");
      content.append(create("h4", "Detailed finding and scope"), prose("p", record.audit.summary, record));
      recordEvidence(content);
    };
    if (record.audit.outcome === "no_issue_found") {
      const result = create("section", undefined, "case-result no-issue-result");
      result.append(create("p", "No issue was found within the scope of this check."));
      parent.append(result);
      brief(parent);
      caseEvidence();
      return;
    }
    if (record.audit.outcome === "scope_clarification") {
      const result = create("section", undefined, "case-result scope-result");
      result.append(create("h3", "Scope clarification"), prose("p", record.audit.summary, record));
      parent.append(result);
      brief(parent);
      caseEvidence();
      return;
    }
    const problems = note && note.revision === record.revision && Array.isArray(note.problems) && note.problems.length
      ? note.problems : fallbackProblems(record);
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
      brief(section, problem);
      const content = disclosure(section, `problem-${index + 1}-evidence`, `Evidence and reasoning for Problem ${index + 1}`);
      content.append(create("h4", problem.claim_heading || "Claim in the source (paraphrase)"));
      content.append(prose("p", "Source. " + problem.source_location, record, "source-citation"));
      paragraphs(content, problem.claim);
      if (problem.assumptions.length) {
        content.append(create("h4", "Conditions"));
        const list = create("ul");
        problem.assumptions.forEach(value => list.append(prose("li", value, record)));
        content.append(list);
      }
      content.append(create("h4", problem.analysis_heading));
      paragraphs(content, problem.analysis);
      content.append(create("h4", "Detailed finding and scope"));
      paragraphs(content, problem.result);
      if (problem.repair) {
        content.append(create("h4", problem.repair.heading));
        paragraphs(content, problem.repair.paragraphs);
      }
      if (index === 0) recordEvidence(content);
      else {
        const link = create("a", "Case-wide scope and evidence");
        link.href = "#case-scope-evidence";
        const reference = create("p");
        reference.append(link);
        content.append(reference);
      }
      parent.append(section);
    });
  }
  return {renderProblems, fallbackProblems, briefPoints};
});
