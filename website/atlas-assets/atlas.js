/* Offline UI. Record prose uses explicit, revision-checked TeX presentation. */
"use strict";
(() => {
  const data = window.ELVIA_DATA;
  const labels = {
    candidate_issue: "Candidate issue",
    scope_clarification: "Scope clarification",
    no_issue_found: "No issue in scope",
    known_issue_reproduced: "Known issue reproduced",
    needs_evidence: "Needs Evidence"
  };
  const $ = id => document.getElementById(id);
  const create = (tag, text, className) => {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  };
  if (!data || !Array.isArray(data.records)) {
    $("result-count").textContent = "Record data unavailable. Please download a complete site build.";
    return;
  }
  const {assessment, sortByTitle, labels: severityLabels} = window.ELVIA_ASSESSMENT;
  const records = sortByTitle(data.records);
  const fieldLabels = ["Mathematics", "Biological science", "Computer science", "Chemistry", "Others"];
  const researchField = record => {
    const value = data.research_fields && data.research_fields[record.case_id];
    return fieldLabels.includes(value) ? value : "Others";
  };
  let searchIndex = null;
  function search(query) {
    if (!query) return records.map(record => ({record}));
    searchIndex ||= window.ELVIA_SEARCH.createIndex(records, {
      caseNotes: data.case_notes, reader: data.reader,
      extraTerms: record => [assessment(record).label, labels[record.audit.outcome], researchField(record)]
    });
    return searchIndex.search(query);
  }
  const pageSizes = [5, 10, 15, 20];
  let pageSize = 10;
  let currentPage = 1;
  $("page-size").value = String(pageSize);
  const prose = (tag, text, record, className) => {
    const node = create(tag, undefined, className);
    const presentation = data.presentation && data.presentation[record.case_id];
    if (window.ELVIA_MATH) {
      window.ELVIA_MATH.renderInto(node, text, {
        replacements: presentation && presentation.revision === record.revision ? presentation.replacements : [],
        renderer: window.katex
      });
    } else node.textContent = text;
    return node;
  };
  document.querySelectorAll("[data-math]").forEach(node => {
    if (window.ELVIA_MATH) window.ELVIA_MATH.renderInto(node, node.textContent, {renderer: window.katex});
  });
  const dialog = $("case-dialog");
  let lastTrigger = null;
  let activeCase = null;
  const pretty = value => value.replaceAll("_", " ");
  const safeExternal = url => {
    try {
      const parsed = new URL(url);
      return parsed.protocol === "https:" && !parsed.username && !parsed.password ? parsed.href : null;
    } catch { return null; }
  };
  const evidenceRoot = record => "evidence/" + encodeURIComponent(record.case_id) + "/";
  const artifactURL = (record, path) => evidenceRoot(record) + path.split("/").map(encodeURIComponent).join("/");
  const link = (label, href, download = false) => {
    const anchor = create("a", label);
    anchor.href = href;
    if (download) anchor.setAttribute("download", "");
    else if (href.startsWith("https:")) anchor.rel = "noopener noreferrer";
    return anchor;
  };
  const tag = record => {
    const rating = assessment(record);
    const badge = create("span", rating.label, "severity-tag " + rating.key);
    badge.setAttribute("aria-label", "Preliminary assessment: " + rating.label);
    return badge;
  };
  $("count-total").textContent = String(records.length).padStart(2, "0");
  for (const severity of Object.keys(severityLabels)) {
    $("count-" + severity).textContent = String(records.filter(r => assessment(r).key === severity).length).padStart(2, "0");
  }
  const venues = [...new Set(records.map(r => r.audit.venue))].sort();
  venues.forEach(venue => {
    const option = create("option", venue);
    option.value = venue;
    $("venue").append(option);
  });
  function readFilters() {
    const params = new URLSearchParams(location.search);
    $("search").value = params.get("q") || "";
    for (const [id, allowed] of [["field", fieldLabels], ["venue", venues], ["outcome", Object.keys(labels)], ["severity", Object.keys(severityLabels)]]) {
      const value = params.get(id) || "";
      $(id).value = allowed.includes(value) ? value : "";
    }
  }
  function writeFilters() {
    const params = new URLSearchParams(location.search);
    for (const [key, id] of [["q", "search"], ["field", "field"], ["venue", "venue"], ["outcome", "outcome"], ["severity", "severity"]]) {
      const value = $(id).value.trim();
      if (value) params.set(key, value);
      else params.delete(key);
    }
    const query = params.toString();
    history.replaceState(null, "", (location.pathname || "/atlas/") + (query ? "?" + query : "") + (location.hash || ""));
  }
  readFilters();
  function render() {
    const query = $("search").value.trim();
    const venue = $("venue").value;
    const outcome = $("outcome").value;
    const severity = $("severity").value;
    const field = $("field").value;
    const matches = search(query).filter(({record: r}) =>
      (!venue || r.audit.venue === venue) && (!outcome || r.audit.outcome === outcome) &&
      (!severity || assessment(r).key === severity) && (!field || researchField(r) === field));
    const selected = matches.map(match => match.record);
    const matchById = new Map(matches.map(match => [match.record.case_id, match]));
    $("sort-caption").textContent = query ? "Best match" : "Title · A–Z";
    const pageCount = Math.ceil(selected.length / pageSize);
    currentPage = Math.max(1, Math.min(currentPage, pageCount || 1));
    const start = (currentPage - 1) * pageSize;
    const visible = selected.slice(start, start + pageSize);
    $("case-list").replaceChildren();
    $("result-count").textContent = selected.length
      ? `${start + 1}–${start + visible.length} of ${selected.length} cases shown${selected.length === records.length ? "" : ` (${records.length} total)`}`
      : `0 of ${records.length} cases shown`;
    for (const suffix of ["", "-bottom"]) {
      $("page-status" + suffix).textContent = pageCount ? `Page ${currentPage} of ${pageCount}` : "No matching records";
      $("previous-page" + suffix).disabled = currentPage === 1 || pageCount === 0;
      $("next-page" + suffix).disabled = currentPage >= pageCount;
    }
    $("empty").hidden = selected.length !== 0;
    visible.forEach(record => {
      const row = create("article", undefined, "case-row");
      row.append(create("span", String(records.indexOf(record) + 1).padStart(2, "0"), "case-number"));
      const main = create("div");
      main.append(create("p", `${record.audit.venue.toUpperCase()} / ${record.audit.year} / REV. ${record.revision} / ${researchField(record)}`, "case-meta"));
      const title = prose("a", record.source.title, record, "case-title");
      title.href = "cases/" + encodeURIComponent(record.case_id) + ".html";
      main.append(title, prose("p", record.audit.summary, record, "case-summary"));
      const match = matchById.get(record.case_id);
      if (query && match) {
        const explanation = create("p", match.explanation, "search-match");
        if (match.problemIndex) {
          explanation.append(create("span", " "), link("Read Problem " + match.problemIndex,
            title.href + "#problem-" + match.problemIndex));
        }
        main.append(explanation);
      }
      const side = create("div", undefined, "case-side");
      const state = create("div");
      state.append(tag(record), create("p", "Independent review pending", "case-state"));
      const availability = create("div");
      state.append(availability);
      window.ELVIA_PAPER_STATUS?.attach(availability, record.case_id, true);
      side.append(state);
      row.append(main, side);
      $("case-list").append(row);
    });
  }
  function section(parent, title) {
    const node = create("section", undefined, "detail-section");
    node.append(create("h3", title));
    parent.append(node);
    return node;
  }
  function show(record) {
    const paragraph = (parent, text, label) => {
      if (label) parent.append(prose("p", label, record, "detail-label"));
      parent.append(prose("p", text, record));
    };
    const list = (parent, values) => {
      const ul = create("ul");
      values.forEach(value => ul.append(prose("li", value, record)));
      parent.append(ul);
    };
    activeCase = record.case_id;
    const content = $("detail-content");
    content.replaceChildren();
    content.append(create("p", `${record.audit.venue} ${record.audit.year}`, "detail-publication"), tag(record));
    const title = prose("h2", record.source.title, record);
    title.id = "detail-title";
    content.append(title);
    const entry = data.reader && data.reader[record.case_id];
    const reader = entry && entry.revision === record.revision ? entry : null;
    const citation = create("p", undefined, "detail-citation");
    if (reader && reader.citation) {
      const c = reader.citation;
      const authors = c.authors;
      const natural = name => { const parts = name.split(", "); return parts.length === 2 ? `${parts[1]} ${parts[0]}` : name; };
      const credit = authors.length > 2 ? `${authors[0]}, et al.`
        : authors.length === 2 ? `${authors[0]}, and ${natural(authors[1])}.` : `${authors[0]}.`;
      citation.append(prose("span", `${credit} “${c.title.replace(/\s+/g, " ").trim()}${/[.!?]$/.test(c.title.trim()) ? "" : "."}” `, record));
      citation.append(create("em", c.container));
      let endPage = c.last_page || c.first_page;
      if (/^\d+$/.test(c.first_page) && /^\d+$/.test(endPage) && c.first_page.length === endPage.length) {
        let common = 0;
        while (common < endPage.length - 2 && c.first_page[common] === endPage[common]) common++;
        endPage = endPage.slice(common);
      }
      const pages = !c.first_page ? "" : !c.last_page || c.first_page === c.last_page
        ? `, p. ${c.first_page}` : `, pp. ${c.first_page}–${endPage}`;
      const editors = c.editors && c.editors.length ? `, edited by ${c.editors[0]}${c.editors.length > 1 ? " et al." : ""}` : "";
      const publisher = c.publisher ? `${c.publisher.replace(/,? Inc\.$/, "")}, ` : "";
      citation.append(create("span", `${editors}, vol. ${c.volume}, ${publisher}${c.year}${pages}, `));
      const citationURL = safeExternal(c.doi ? "https://doi.org/" + c.doi : c.source_url);
      if (citationURL) citation.append(link(citationURL, citationURL));
      citation.append(create("span", "."));
    } else {
      citation.append(create("span", `${record.audit.authors.join(", ")}. “${record.source.title}.” `),
        create("em", record.audit.venue), create("span", `, ${record.audit.year}. `));
      const source = safeExternal(record.audit.landing_url);
      if (source) citation.append(link("Original article", source));
    }
    content.append(citation);
    const narrative = create("div", undefined, "problem-notes");
    window.ELVIA_CASE_NOTES.renderProblems(narrative, record, data.case_notes && data.case_notes[record.case_id], {
      create, prose, link, artifactURL, assessmentLabels: severityLabels
    });
    content.append(narrative);

    const supporting = create("details", undefined, "supporting-record");
    supporting.append(create("summary", "Supporting record & provenance"));
    const support = create("div", undefined, "supporting-content");
    supporting.append(support);
    content.append(supporting);
    const workflow = section(support, "Work status");
    paragraph(workflow, `Version ${record.revision}`, "Current version");
    if (reader && reader.contributors && reader.contributors.length) {
      list(workflow, reader.contributors.map(person => `${person.name} · ${person.role} · Version ${person.revision}`));
    }
    paragraph(workflow, record.adjudication.status === "pending" ? "Independent review pending" : pretty(record.adjudication.status));
    const scope = section(support, "Original claim and review scope");
    paragraph(scope, record.proposition.claim, record.proposition.location);
    if (record.proposition.domain !== record.source.review_scope) paragraph(scope, record.proposition.domain, "Recorded domain");
    if (record.proposition.assumptions.length) { paragraph(scope, "Assumptions recorded for this check:"); list(scope, record.proposition.assumptions); }
    if (record.proposition.dependencies.length) { paragraph(scope, "Dependencies:"); list(scope, record.proposition.dependencies); }
    paragraph(scope, record.source.review_scope, "Actual review scope");
    const check = section(support, "Complete evidence and counterevidence");
    paragraph(check, record.concern.description);
    const shownEvidence = new Set([record.concern.description]);
    record.evidence.filter(item => item.id !== "editable-latex").forEach(item => {
      const description = item.description.replace(/^Preliminary AI assessment; independent human scientific adjudication remains pending\.\s*/, "");
      if (!description || shownEvidence.has(description)) return;
      shownEvidence.add(description);
      const evidence = create("div", undefined, "detail-evidence");
      evidence.append(create("h4", item.stance === "rebuttal" ? "Counterevidence and scope" : pretty(item.stance)));
      paragraph(evidence, description);
      check.append(evidence);
    });
    const bundle = data.reader_bundles && data.reader_bundles[record.case_id];
    if (bundle === "evidence/" + record.case_id + ".zip") {
      const downloads = create("div", undefined, "detail-download");
      downloads.append(link("Download evidence (.zip)", "evidence/" + encodeURIComponent(record.case_id) + ".zip", true));
      content.append(downloads);
    }
    if (!dialog.open) dialog.showModal();
    dialog.scrollTop = 0;
    $("close-dialog").focus();
  }
  function navigate(record, trigger) {
    lastTrigger = trigger;
    history.pushState(null, "", "#case=" + encodeURIComponent(record.case_id));
    show(record);
  }
  function syncHash() {
    if (!location.hash.startsWith("#case=")) { if (dialog.open) dialog.close(); return; }
    let id;
    try { id = decodeURIComponent(location.hash.slice(6)); } catch { return; }
    const record = records.find(r => r.case_id === id);
    if (record) show(record);
  }
  $("close-dialog").addEventListener("click", () => dialog.close());
  dialog.addEventListener("close", () => {
    if (location.hash === "#case=" + encodeURIComponent(activeCase)) history.replaceState(null, "", "#atlas");
    activeCase = null;
    if (lastTrigger && lastTrigger.isConnected) lastTrigger.focus();
  });
  function resetPage() { currentPage = 1; writeFilters(); render(); }
  $("search").addEventListener("input", resetPage);
  $("venue").addEventListener("change", resetPage);
  $("outcome").addEventListener("change", resetPage);
  $("severity").addEventListener("change", resetPage);
  $("field").addEventListener("change", resetPage);
  $("page-size").addEventListener("change", () => {
    const requestedSize = Number($("page-size").value);
    pageSize = pageSizes.includes(requestedSize) ? requestedSize : 10;
    $("page-size").value = String(pageSize);
    resetPage();
  });
  for (const suffix of ["", "-bottom"]) {
    $("previous-page" + suffix).addEventListener("click", () => { currentPage--; render(); });
    $("next-page" + suffix).addEventListener("click", () => { currentPage++; render(); });
  }
  $("reset").addEventListener("click", () => {
    $("search").value = ""; $("venue").value = ""; $("outcome").value = ""; $("severity").value = ""; $("field").value = "";
    resetPage(); $("search").focus();
  });
  window.addEventListener("hashchange", syncHash);
  window.addEventListener("popstate", () => { readFilters(); currentPage = 1; render(); syncHash(); });
  render();
  syncHash();
})();
