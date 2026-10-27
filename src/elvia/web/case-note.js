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

  function problemStatement(problem) {
    return [...problem.assumptions, ...problem.claim].map(value => value.trim()).filter(Boolean).join(" ");
  }

  function proofHeading(problem) {
    return problem.analysis_heading?.trim() === "Proof" && problem.analysis.some(value => value.trim())
      ? "Proof" : "Verification";
  }

  function problemAssessment(problem) {
    return problem.assessment === "not_issue" ? "no_issue_found"
      : problem.assessment === "needs_evidence" ? "needs_evidence"
      : problem.severity === "moderate" ? "minor" : problem.severity;
  }

  function orderedProblems(problems) {
    const ranks = {major: 0, minor: 1, needs_evidence: 2};
    return problems.map((problem, index) => ({problem, index}))
      .filter(({problem}) => problemAssessment(problem) !== "no_issue_found")
      .sort((left, right) => (ranks[problemAssessment(left.problem)] ?? 3) - (ranks[problemAssessment(right.problem)] ?? 3));
  }

  function needsProofMarker(problem) {
    return proofHeading(problem) === "Proof" && !/(?:[□◻]|Q\.?E\.?D\.?|\\\(\\(?:square|Box)\\\))\s*$/.test(problem.analysis.join(" ").trim());
  }

  function renderProblems(parent, record, note, helpers) {
    const {create, prose, assessmentLabels = {}} = helpers;
    const scientific = (tag, value) => prose(tag, value, record, "scientific-prose");
    const paragraphs = (container, values) => values.forEach(value => container.append(scientific("p", value)));
    const filesNote = container => {
      if (helpers.readerBundleAvailable) container.append(create("p", "Supporting files are included in Download report files (.zip).", "evidence-files-note"));
    };
    const abstract = create("section", undefined, "case-overview");
    abstract.append(create("h2", "Analysis abstract"), prose("p", briefPoints(record, undefined, note).join(" "), record, "analysis-abstract scientific-prose"));
    parent.append(abstract);
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
      filesNote(content);
      content.append(create("h4", "Detailed finding and scope"));
      paragraphs(content, record.audit.limitations);
    };
    if (record.audit.outcome === "no_issue_found") {
      const result = create("section", undefined, "case-result no-issue-result");
      result.append(create("p", "No issue was found within the scope of this check."));
      parent.append(result);
      caseEvidence();
      return;
    }
    if (record.audit.outcome === "scope_clarification") {
      const result = create("section", undefined, "case-result scope-result");
      result.append(create("h3", "Scope clarification"));
      parent.append(result);
      caseEvidence();
      return;
    }
    const problems = note && note.revision === record.revision && Array.isArray(note.problems) && note.problems.length
      ? note.problems : fallbackProblems(record);
    const entries = orderedProblems(problems);
    if (!entries.length) {
      parent.append(create("p", "The recorded checks and their scope are retained below.", "case-result"));
      caseEvidence();
      return;
    }
    entries.forEach(({problem, index}, position) => {
      const displayNumber = position + 1;
      const section = create("section", undefined, "case-problem");
      const heading = prose("h3", `Problem ${displayNumber}. ${problem.title}`, record);
      heading.id = `problem-${index + 1}`;
      section.setAttribute("aria-labelledby", heading.id);
      section.setAttribute("data-source-problem-id", problem.id || `source-${index + 1}`);
      section.setAttribute("data-source-problem-number", String(index + 1));
      section.setAttribute("data-display-problem-number", String(displayNumber));
      section.append(heading);
      if (problem.severity) {
        const key = problemAssessment(problem);
        const label = assessmentLabels[key];
        if (label) section.append(create("span", label, "severity-tag " + key));
      }
      const content = disclosure(section, `problem-${index + 1}-evidence`, `Evidence and reasoning for Problem ${displayNumber}`);
      content.append(create("h4", "Problem statement"));
      if (problem.claim_heading && !["Claim in the source (paraphrase)", "Problem statement"].includes(problem.claim_heading)) content.append(prose("p", problem.claim_heading, record, "statement-role"));
      content.append(prose("p", problemStatement(problem), record, "problem-statement scientific-prose"));
      content.append(create("h4", "Source and method"));
      content.append(prose("p", "Source. " + problem.source_location, record, "source-citation"));
      if (problem.method) paragraphs(content, typeof problem.method === "string" ? [problem.method] : problem.method);
      if (position === 0) filesNote(content);
      content.append(create("h4", proofHeading(problem)));
      paragraphs(content, problem.analysis);
      if (needsProofMarker(problem)) content.append(prose("p", "\\(\\square\\)", record, "proof-end scientific-prose"));
      content.append(create("h4", "Detailed finding and scope"));
      paragraphs(content, problem.result);
      parent.append(section);
    });
  }
  return {renderProblems, fallbackProblems, briefPoints};
});
