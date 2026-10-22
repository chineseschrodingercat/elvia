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
  [...new Set(records.map(r => r.audit.venue))].sort().forEach(venue => {
    const option = create("option", venue);
    option.value = venue;
    $("venue").append(option);
  });
  const searchable = record => [record.source.title, record.audit.authors.join(" "), record.audit.venue,
    record.audit.year, record.audit.summary, record.proposition.claim, record.case_id,
    assessment(record).label, labels[record.audit.outcome]].join(" ").toLocaleLowerCase();
  function render() {
    const query = $("search").value.trim().toLocaleLowerCase();
    const venue = $("venue").value;
    const outcome = $("outcome").value;
    const severity = $("severity").value;
    const selected = records.filter(r => (!query || searchable(r).includes(query)) &&
      (!venue || r.audit.venue === venue) && (!outcome || r.audit.outcome === outcome) &&
      (!severity || assessment(r).key === severity));
    $("case-list").replaceChildren();
    $("result-count").textContent = `${selected.length} of ${records.length} cases shown`;
    $("empty").hidden = selected.length !== 0;
    selected.forEach(record => {
      const row = create("article", undefined, "case-row");
      row.append(create("span", String(records.indexOf(record) + 1).padStart(2, "0"), "case-number"));
      const main = create("div");
      main.append(create("p", `${record.audit.venue.toUpperCase()} / ${record.audit.year} / REV. ${record.revision}`, "case-meta"));
      const title = prose("a", record.source.title, record, "case-title");
      title.href = "cases/" + encodeURIComponent(record.case_id) + ".html";
      main.append(title, prose("p", record.audit.summary, record, "case-summary"));
      const side = create("div", undefined, "case-side");
      const state = create("div");
      state.append(tag(record), create("p", "Independent review pending", "case-state"));
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
      const doi = safeExternal("https://doi.org/" + c.doi);
      if (doi) citation.append(link(doi, doi));
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
  $("search").addEventListener("input", render);
  $("venue").addEventListener("change", render);
  $("outcome").addEventListener("change", render);
  $("severity").addEventListener("change", render);
  $("reset").addEventListener("click", () => {
    $("search").value = ""; $("venue").value = ""; $("outcome").value = ""; $("severity").value = "";
    render(); $("search").focus();
  });
  window.addEventListener("hashchange", syncHash);
  window.addEventListener("popstate", syncHash);
  render();
  syncHash();
})();
