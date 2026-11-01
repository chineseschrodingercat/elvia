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

  function pageRanges(values) {
    const ranges = [];
    for (const value of values) {
      if (!/^\d+(?:\s*[-–]\s*\d+)?(?:\s*[,;]\s*\d+(?:\s*[-–]\s*\d+)?)*$/.test(value)) return [...new Set(values)].join("; ");
      for (const item of value.split(/\s*[,;]\s*/)) {
        const ends = item.split(/\s*[-–]\s*/).map(Number);
        const start = ends[0], end = ends.at(-1);
        if (start > end) return [...new Set(values)].join("; ");
        ranges.push([start, end]);
      }
    }
    const merged = [];
    for (const [start, end] of ranges.sort((left, right) => left[0] - right[0] || left[1] - right[1])) {
      if (merged.length && start <= merged.at(-1)[1] + 1) merged.at(-1)[1] = Math.max(end, merged.at(-1)[1]);
      else merged.push([start, end]);
    }
    return merged.map(([start, end]) => start === end ? String(start) : `${start}–${end}`).join("; ");
  }

  function sourceLocation(value) {
    const text = String(value ?? "").replace(/\s+/g, " ").trim();
    const fieldPattern = "printed pages same|pdf sha256|" +
      "(?:(?:physical pdf|primary pdf|publisher pdf|author v2 pdf|reference printed|" +
      "pdf|printed|physical|dependency|related|counterevidence|proof|statement|reference) )?pages?|" +
      "author tex lines?\\. [a-z0-9 _-]+|" +
      "(?:(?:related older tex|source code|source tex|author tex|tex|source|text|" +
      "exact step|decisive) )?lines?(?: (?:1|one) based)?|" +
      "(?:source |tex )?files?|reference pdf|version|tex labels?|" +
      "claim locations?|source locations?|paper location|precise anchors?|exact locators?|" +
      "source references?|dependent results|dependency proposition|reference equations?|" +
      "labels?|anchors?|primary|locators?|locations?|claims?|items?|statements?|objects?|" +
      "details|headings?|failed step|paragraphs?|" +
      "sections?|lemmas?|theorems?|propositions?|equations?|definitions?|remarks?|" +
      "tables?|figures?|appendix|proof|application|code|source|supplement|author supplement";
    const matches = [...text.matchAll(new RegExp("(?<![\\w./+-])(" + fieldPattern + ")\\s*:\\s*", "gi"))];
    if (!matches.length) return text || "Not available";
    const trim = value => value.replace(/^[ ;,.]+|[ ;,.]+$/g, "");
    let prefix = trim(text.slice(0, matches[0].index));
    if (prefix.toLowerCase() === "source") prefix = "";
    const fields = matches.map((match, index) => [match[1].toLowerCase(),
      trim(text.slice(match.index + match[0].length, matches[index + 1]?.index ?? text.length)), match[1]]);
    const pageLabels = {pdf: "PDF pages", printed: "printed pages", physical: "physical pages",
      "physical pdf": "physical PDF pages", "": "pages", "primary pdf": "primary PDF pages",
      "publisher pdf": "publisher PDF pages", "author v2 pdf": "author v2 PDF pages",
      dependency: "dependency pages", related: "related pages", counterevidence: "counterevidence pages",
      proof: "proof pages", statement: "statement pages", reference: "reference pages",
      "reference printed": "reference printed pages"};
    const filename = /[^\s;,]+\.(?:tex|py|c|cpp|h|hpp|jl|m|js|ts|rs|r|sh|pdf)\b/i;
    const parts = prefix ? [{text: prefix}] : [];
    let namedFile = prefix && filename.test(prefix) ? parts[0] : null;
    let sourcePrefix = prefix ? "" : "Article ";
    let fileRun = 0;
    const appendText = item => {
      if (item && parts.at(-1)?.text !== item) parts.push({text: item});
    };
    const appendRange = (label, item) => {
      if (parts.at(-1)?.label === label) parts.at(-1).values.push(item);
      else parts.push({label, values: [item]});
    };
    for (const [field, item, originalField] of fields) {
      if (!item) continue;
      const isFile = /^(?:source |tex )?files?$/.test(field) || ["source", "code", "reference pdf"].includes(field);
      fileRun = isFile ? fileRun + 1 : 0;
      if (field === "printed pages same" && /^(?:true|false)$/i.test(item)) continue;
      if (field === "pdf sha256" && /^[a-f0-9]{64}$/i.test(item)) continue;
      const page = field.match(/^(?:(.*?) )?pages?$/);
      if (page && Object.hasOwn(pageLabels, page[1] || "")) {
        const kind = page[1] || "";
        let label = pageLabels[kind];
        label = /^(?:reference|publisher|author)/.test(kind) ? label[0].toUpperCase() + label.slice(1) : sourcePrefix + label;
        appendRange(label, item);
        continue;
      }
      if (isFile) {
        appendText(field === "reference pdf" ? "Reference PDF: " + item : item);
        if (field === "reference pdf" || /\bsupplement/i.test(item)) sourcePrefix = "";
        // A flat array of filenames cannot assign a later line list to one file.
        namedFile = filename.test(item) && fileRun === 1 ? parts.at(-1) : null;
        continue;
      }
      const nestedTex = originalField.match(/^author tex lines?\. ([a-z0-9 _-]+)$/i);
      if (nestedTex || /^(?:(?:related older tex|source code|source tex|author tex|tex|source|text|exact step|decisive) )?lines?(?: (?:1|one) based)?$/.test(field)) {
        if (namedFile) (namedFile.lines ||= []).push(item);
        else if (field.startsWith("source line") || field.startsWith("exact step") || field.startsWith("decisive")) {
          // Remove only the offset itself, preserving any unrecognized prose.
          appendText(trim(item.replace(/^\d+(?:\s*[-–]\s*\d+)?(?:\s*[,;]\s*\d+(?:\s*[-–]\s*\d+)?)*/, "")));
        } else {
          let label = field.includes("tex") ? "TeX lines" : field.includes("code") ? "Code lines" : "Text lines";
          if (field.startsWith("related older")) label = "Earlier TeX lines";
          if (nestedTex) label = "TeX lines (" + nestedTex[1] + ")";
          appendRange(label, item);
        }
        continue;
      }
      if (/^(?:sections?|lemmas?|theorems?|propositions?|equations?|definitions?|remarks?|tables?|figures?|appendix|reference equations?|dependency proposition)$/.test(field)) {
        const label = field[0].toUpperCase() + field.slice(1);
        appendText(item.toLowerCase().startsWith(field + " ") ? item : label + " " + item);
      } else if (field.startsWith("tex label")) appendText("TeX label " + item);
      else if (["proof", "application", "supplement", "author supplement", "version"].includes(field)) {
        appendText(field[0].toUpperCase() + field.slice(1) + ": " + item);
        if (["supplement", "author supplement", "version"].includes(field)) {
          sourcePrefix = "";
          namedFile = filename.test(item) ? parts.at(-1) : null;
        }
      }
      else appendText(item);
    }
    return parts.map(part => part.label ? part.label + ": " + pageRanges(part.values)
      : part.text + (part.lines?.length ? ", lines " + pageRanges(part.lines) : "")).join("; ") || "Not available";
  }

  // Keep the same source-bound proposal rules as revision_display.py.
  const proposalPattern = "\\b(?:repair|correction|revision|fix)\\s+(?:is\\s+to|would\\s+be\\s+to|consists?\\s+of|requires?\\s+(?:adding|replacing|restricting|correcting|changing|removing|retaining|specifying|stating|inserting|recomputing|renormalizing|swapping)|(?:must|should|needs?\\s+to)\\s+(?:add|replace|restrict|correct|change|remove|retain|specify|state|insert|recompute|renormalize|swap)|(?:could|may|can|would)\\s+(?:replace|restrict|add|remove|change|retain|state|specify|evaluate|correct|bound|require|insert|distinguish|exclude)|(?:can\\s+be|is)\\s+(?:obtained|achieved|made)\\s+by|using|by)\\b|\\b(?:repair|correction|revision|fix)(?:\\s+and\\s+(?:limits?|scope|counterevidence|impact)|\\s+boundary)?\\s*(?:is\\s+proved\\s*)?[:.]\\s*(?:use|choose|replace|restrict|add|remove|change|retain|state|specify|evaluate|correct|bound|prove|recompute|require|insert|distinguish|exclude|supply|assume|define|normalize|separate|delete|count|introduce)\\b|\\b(?:changing|replacing|restricting|adding|removing|correcting|inserting|separating|imposing|renormalizing|reversing|swapping|strengthening|weakening)\\b[^.]{0,450}\\b(?:is\\s+(?:a\\s+)?(?:plausible\\s+)?(?:local\\s+)?repair|repairs?|corrects?|restores?|removes?\\s+the\\s+(?:(?:first|second|third|demonstrated)\\s+)?(?:obstruction|contradiction)|preserves?\\s+the\\s+claimed)\\b|\\b(?:delete|remove)\\s+(?:that|this|the\\s+(?:printed|displayed|unsupported))\\s+(?:claim|assertion|statement)\\b|\\breplace\\s+(?:Eq\\.?|Equation|Lemma|Theorem|Proposition|the\\s+(?:printed|displayed|original)\\s+(?:formula|identity|claim|statement))[^.]{0,180}\\b(?:with|by)\\b|\\breplace\\s+(?:the|that|this)\\s+[^.]{0,60}\\b(?:formula|identity|equality|assertion|statement|condition|coefficient|sign|term|factor|exponent|bound)\\s+(?:with|by)\\b|\\binsert\\b[^.]{0,100}\\bin\\s+(?:that|the\\s+printed|the\\s+displayed)\\s+(?:formula|identity|equation)\\b|\\b(?:should|must)\\s+be\\s+(?:replaced|restricted|corrected|rewritten)\\s+(?:by|with|to|as)\\b|\\b(?:formula|representation|statement|display)\\s+(?:must|should)\\s+read\\b|\\b(?:gives?|yields?|proves?|obtain(?:s)?)\\s+the\\s+corrected\\s+(?:local\\s+)?(?:formula|identity|statement|system|equation|bound|estimate|expression)\\b|\\b(?:the\\s+)?correct(?:ed)?\\s+(?:local\\s+)?(?:formula|identity|statement|system|equation|bound|estimate|expression)\\s+(?:is|reads|becomes)\\b|\\bthe\\s+replacement\\s+is\\s*(?:\\\\\\[|\\\\\\(|[0-9])";
  const proposalGerund = new RegExp("^(?:changing|replacing|restricting|adding|removing|correcting|inserting|separating|imposing|renormalizing|reversing|swapping|strengthening|weakening)\\b", "i");
  const proposalNegation = new RegExp("\\b(?:not|cannot|never|insufficient|fails?\\s+to)\\b", "i");
  const proposalDenial = new RegExp("\\b(?:does?\\s+not\\s+(?:claim|establish|show)|no\\s+claim|cannot\\s+conclude|without\\s+claiming)\\b[^.]{0,100}$", "i");
  function hasProposal(value) {
    for (const match of value.matchAll(new RegExp(proposalPattern, "gi"))) {
      if (proposalGerund.test(match[0]) && proposalNegation.test(match[0])) continue;
      const before = value.slice(Math.max(0, match.index - 120), match.index);
      if (proposalDenial.test(before) || /\b(?:no|not\s+a)\s*$/i.test(before)) continue;
      if (/\b(?:state|specify)$/i.test(match[0]) && /^\s+(?:a|an)\s+(?:defensible|appropriate|suitable)\b/i.test(value.slice(match.index + match[0].length))) continue;
      return true;
    }
    return false;
  }
  function possibleRevision(problem) {
    const boilerplate = "A proposed correction is retained where stated; independent verification and author adoption remain unestablished.";
    const explicit = (problem.repair?.paragraphs || []).filter(value => typeof value === "string" && value.trim() && value.trim() !== boilerplate);
    if (explicit.length) return [...explicit];
    const narrative = [], recorded = [];
    const values = [...(problem.analysis || []), ...(problem.result || [])];
    values.forEach((value, index) => {
      if (/\b(?:two|three|four|several|the following)\s+(?:definitions|revisions|changes|corrections|repairs|alternatives|options)\s+(?:remove|avoid|repair|resolve|correct)\b/i.test(value)) {
        const group = [];
        let following = index + 1;
        while (following < values.length && /^\s*\d+[.)]\s+/.test(values[following])) group.push(values[following++]);
        if (group.length) {
          narrative.push(value, ...group);
          for (const boundary of values.slice(following, following + 2)) if (!boundary.startsWith("Recorded evidence:")) narrative.push(boundary);
        }
      }
      if (!hasProposal(value)) return;
      if (value.startsWith("Recorded evidence:")) recorded.push(value.replace(/^Recorded evidence:\s*(?:Check\.\s*)?/, ""));
      else narrative.push(value);
    });
    return [...new Set(narrative.length ? narrative : recorded)];
  }

  function renderProblems(parent, record, note, helpers) {
    const {create, prose, assessmentLabels = {}} = helpers;
    const scientific = (tag, value) => prose(tag, value, record, "scientific-prose");
    const paragraphs = (container, values) => values.forEach(value => container.append(scientific("p", value)));
    const filesNote = container => {
      if (helpers.readerBundleAvailable) container.append(create("p", "Supporting files are included in Download report files (.zip).", "evidence-files-note"));
    };
    const outcome = record.audit.outcome;
    const problems = note && note.revision === record.revision && Array.isArray(note.problems) && note.problems.length
      ? note.problems : fallbackProblems(record);
    const entries = ["no_issue_found", "scope_clarification"].includes(outcome) ? [] : orderedProblems(problems);
    const overview = create("section", undefined, "key-findings");
    overview.setAttribute("aria-labelledby", "key-findings-title");
    const overviewTitle = create("h2", "Key findings");
    overviewTitle.id = "key-findings-title";
    overview.append(overviewTitle);
    if (entries.length) {
      const list = create("ol", undefined, "key-findings-list");
      entries.forEach(({problem}, position) => {
        const item = create("li");
        item.setAttribute("data-display-problem-number", String(position + 1));
        const points = Array.isArray(problem.brief) && problem.brief.length ? problem.brief : [problem.title];
        item.append(scientific("p", points.join(" ")));
        list.append(item);
      });
      overview.append(list);
    } else paragraphs(overview, briefPoints(record, undefined, note));
    parent.append(overview);
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
      content.append(create("h4", "Review scope"));
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
      content.append(create("h4", "Sources"));
      content.append(prose("p", sourceLocation(problem.source_location), record, "source-citation"));
      content.append(create("h4", proofHeading(problem)));
      if (problem.method) paragraphs(content, typeof problem.method === "string" ? [problem.method] : problem.method);
      paragraphs(content, problem.analysis);
      if (needsProofMarker(problem)) content.append(prose("p", "\\(\\square\\)", record, "proof-end scientific-prose"));
      if (position === 0) filesNote(content);
      content.append(create("h4", "Possible revision"));
      const revision = possibleRevision(problem);
      paragraphs(content, revision.length ? revision : ["Not available"]);
      parent.append(section);
    });
  }
  return {renderProblems, fallbackProblems, briefPoints, sourceLocation, possibleRevision};
});
