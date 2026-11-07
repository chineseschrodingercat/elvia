/* Deterministic local retrieval. Matches point to evidence; they do not answer it. */
"use strict";
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.ELVIA_SEARCH = api;
})(typeof window === "object" ? window : globalThis, function () {
  const stopWords = new Set(("a an and are as at be been being but by can could did do does for from had has have how i if in into is it its may me my of on or our should that the their these they this those to was we were what when where whether which who why will with would you your").split(" "));
  // Deliberately small, inspectable vocabulary: spelling and scientific word forms.
  // Related concepts such as calibration and coverage remain separate terms.
  const groups = [
    ["pool", "pooled", "pooling", "pools"],
    ["calibration", "calibrate", "calibrated", "calibrating"],
    ["score", "scores", "scoring"],
    ["patch", "patches"],
    ["average", "averages", "averaged", "averaging"],
    ["interpolation", "interpolate", "interpolates", "interpolated", "interpolating"],
    ["bilinear", "bilinearly"],
    ["preserve", "preserved", "preserves", "preserving", "maintain", "maintains", "maintained", "maintaining"],
    ["quantization", "quantisation", "quantized", "quantised"],
    ["normalization", "normalisation", "normalized", "normalised"],
    ["optimization", "optimisation", "optimized", "optimised"],
    ["initialization", "initialisation", "initialized", "initialised"],
    ["reproducibility", "reproducible"],
    ["outofbounds", "outofbound"],
    ["llm", "llms"],
    ["gpu", "gpus"]
  ];
  const aliases = new Map(groups.flatMap(group => group.map(word => [word, group[0]])));
  function normalize(value) {
    return String(value || "").normalize("NFKC").toLocaleLowerCase("en")
      .replace(/https?:\/\/(?:dx\.)?doi\.org\//g, "")
      .replace(/[^\p{L}\p{N}]+/gu, " ").trim().replace(/\s+/g, " ");
  }
  function canonical(word) {
    if (aliases.has(word)) return aliases.get(word);
    return word.length > 4 && /s$/.test(word) && !/(ss|us|is)$/.test(word) ? word.slice(0, -1) : word;
  }
  function words(value) {
    return normalize(value).split(" ").filter(word => word && !stopWords.has(word));
  }
  function flatten(value) {
    if (typeof value === "string" || typeof value === "number") return String(value);
    if (Array.isArray(value)) return value.map(flatten).join(" ");
    return "";
  }
  function field(text, weight, label, problemIndex = 0, problemTitle = "", problemDisplayNumber = 0) {
    const plain = flatten(text);
    return {normalized: normalize(plain), tokens: new Set(words(plain).map(canonical)), weight, label, problemIndex, problemTitle, problemDisplayNumber};
  }
  function projectionReader(projection) {
    if (!projection) return () => [];
    if (projection.encoding !== "word-sequences-v1" || !Array.isArray(projection.vocabulary) ||
        !Array.isArray(projection.chunks) || !projection.documents || typeof projection.documents !== "object" ||
        !projection.vocabulary.every(word => typeof word === "string" && word && normalize(word) === word && !word.includes(" "))) {
      throw new Error("Unsupported search projection.");
    }
    const tokens = projection.vocabulary.map(word => stopWords.has(word) ? null : canonical(word));
    const chunks = projection.chunks.map(encoded => {
      if (typeof encoded !== "string" || !/^[a-z0-9]+(?: [a-z0-9]+)*$/.test(encoded)) throw new Error("Invalid search sequence.");
      const ids = encoded.split(" ").map(code => Number.parseInt(code, 36));
      if (!ids.every(id => Number.isSafeInteger(id) && id >= 0 && id < tokens.length)) throw new Error("Invalid search word reference.");
      return {normalized: ids.map(id => projection.vocabulary[id]).join(" "),
        tokens: new Set(ids.map(id => tokens[id]).filter(Boolean))};
    });
    return record => {
      const document = projection.documents[record.case_id];
      if (!document || document.revision !== record.revision) return [];
      if (!Array.isArray(document.fields)) throw new Error("Invalid search document.");
      return document.fields.map(value => {
        if (!Array.isArray(value) || value.length !== 6 || !Array.isArray(value[0]) ||
            !value[0].every(id => Number.isInteger(id) && id >= 0 && id < chunks.length) ||
            ![1, 3, 5].includes(value[1]) || typeof value[2] !== "string" ||
            !Number.isInteger(value[3]) || value[3] < 0 || typeof value[4] !== "string" ||
            !Number.isInteger(value[5]) || value[5] < 0) throw new Error("Invalid search field.");
        const [ids, weight, label, problemIndex, problemTitle, problemDisplayNumber] = value;
        return {normalized: ids.map(id => chunks[id].normalized).join(" "),
          tokens: new Set(ids.flatMap(id => [...chunks[id].tokens])),
          weight, label, problemIndex, problemTitle, problemDisplayNumber};
      });
    };
  }
  function createIndex(records, {caseNotes = {}, reader = {}, extraTerms = () => [], searchProjection} = {}) {
    const projectedFields = projectionReader(searchProjection);
    const frequency = new Map();
    const documents = records.map((record, order) => {
      const source = record.source || {};
      const audit = record.audit || {};
      const proposition = record.proposition || {};
      const citation = reader[record.case_id]?.revision === record.revision ? reader[record.case_id].citation : null;
      const fields = [
        field(source.title, 7, "title"),
        field([record.case_id, source.version, source.doi, source.arxiv_id, audit.landing_url, citation?.doi], 8, "identifier"),
        field(audit.authors, 4, "authors"),
        field([audit.venue, audit.year, extraTerms(record)], 2, "record details"),
        field(audit.summary, 4, "summary"),
        field([proposition.claim, proposition.location], 4, "claim"),
        field([record.concern?.description, audit.limitations, source.review_scope], 2, "evidence and scope")
      ];
      const note = caseNotes[record.case_id];
      if (note?.revision === record.revision && Array.isArray(note.report)) {
        fields.push(field(note.report, 1, "complete retained report"));
      }
      if (note?.revision === record.revision && Array.isArray(note.problems) && !["no_issue_found", "scope_clarification"].includes(audit.outcome)) {
        const rating = problem => problem.assessment === "not_issue" ? "no_issue_found" : problem.assessment === "needs_evidence" ? "needs_evidence" : problem.severity === "moderate" ? "minor" : problem.severity;
        const ranks = {major: 0, minor: 1, needs_evidence: 2};
        const visible = note.problems.map((problem, offset) => ({problem, offset}))
          .filter(({problem}) => rating(problem) !== "no_issue_found")
          .sort((a, b) => (ranks[rating(a.problem)] ?? 3) - (ranks[rating(b.problem)] ?? 3));
        visible.forEach(({problem, offset}, displayOffset) => {
          const label = `Problem ${displayOffset + 1}`;
          fields.push(field(problem.title, 5, label, offset + 1, problem.title, displayOffset + 1));
          fields.push(field([problem.source_location, problem.claim, problem.assumptions, problem.analysis,
            problem.result, problem.repair?.paragraphs], 3, label, offset + 1, problem.title, displayOffset + 1));
        });
      }
      fields.push(...projectedFields(record));
      const tokens = new Set(fields.flatMap(item => [...item.tokens]));
      tokens.forEach(token => frequency.set(token, (frequency.get(token) || 0) + 1));
      return {record, order, fields};
    });
    const importance = token => 1 + Math.log(1 + records.length / (1 + (frequency.get(token) || 0)));
    function search(query) {
      if (!String(query || "").trim()) return documents.map(({record}) => ({record, score: 0, matchedTerms: [], explanation: "", problemIndex: 0}));
      const originals = new Map();
      // Question scaffolding is not a scientific concept. Preserve these words
      // in ordinary keyword/title queries and in every indexed source field.
      const question = /^(how|where|what|can|could|does|do|is|are|when|why)\b/.test(normalize(query));
      const queryWords = words(query).filter(word => !question || !["check", "find", "search", "looking"].includes(word));
      queryWords.forEach(word => { if (!originals.has(canonical(word))) originals.set(canonical(word), word); });
      const terms = [...originals.keys()];
      if (!terms.length) return [];
      const queryWeight = terms.reduce((sum, term) => sum + importance(term), 0);
      const phrase = normalize(query);
      const pairs = [...new Set(queryWords.slice(1).map((word, offset) => queryWords[offset] + " " + word))];
      return documents.flatMap(({record, order, fields}) => {
        const matched = [];
        const locations = new Map();
        let score = 0;
        let matchedWeight = 0;
        for (const term of terms) {
          let best = 0;
          for (const item of fields) {
            if (!item.tokens.has(term)) continue;
            best = Math.max(best, item.weight);
            const location = locations.get(item.label) || {weight: 0, item};
            // A term counts once in a finding even if its title and body both match.
            if (!location.terms) location.terms = new Set();
            if (!location.terms.has(term)) {
              location.weight += importance(term);
              location.terms.add(term);
            }
            locations.set(item.label, location);
          }
          if (best) {
            matched.push(originals.get(term));
            matchedWeight += importance(term);
            score += best * importance(term);
          }
        }
        // Partial wording is welcome; one generic word cannot stand in for a question.
        if (matched.length < Math.ceil(terms.length * 0.6) || matchedWeight / queryWeight < 0.6) return [];
        score *= matchedWeight / queryWeight;
        if (terms.length > 1) {
          const phraseWeight = Math.max(0, ...fields.filter(item => item.normalized.includes(phrase)).map(item => item.weight));
          score += phraseWeight * 5;
          // Adjacent content terms express a local concept even when a reader
          // wraps it in a question. Reward source co-occurrence rather than
          // assembling a match from unrelated parts of a long report.
          for (const pair of pairs) {
            score += Math.max(0, ...fields.filter(item => item.normalized.includes(pair)).map(item => item.weight)) * 2;
          }
        }
        const ordered = [...locations.values()].sort((a, b) => b.weight - a.weight || b.item.weight - a.item.weight);
        const problem = ordered.find(item => item.item.problemIndex && item.terms.size >= Math.min(2, terms.length));
        const location = problem?.item || ordered[0]?.item;
        const explanation = `Matched ${matched.join(", ")} in this record. Closest section: ${location?.label || "record text"}.`;
        return [{record, order, score, matchedTerms: matched, explanation,
          problemIndex: problem?.item.problemIndex || 0, problemTitle: problem?.item.problemTitle || "", problemDisplayNumber: problem?.item.problemDisplayNumber || 0}];
      }).sort((a, b) => b.score - a.score || a.record.source.title.localeCompare(b.record.source.title, "en", {sensitivity: "base", numeric: true}) || a.order - b.order);
    }
    return Object.freeze({search});
  }
  return Object.freeze({createIndex, normalize});
});
