/* Progressive math rendering: all scientific prose is already in the HTML. */
"use strict";
(() => {
  const presentation = window.ELVIA_CASE_PRESENTATION || {};
  for (const node of document.querySelectorAll("[data-case-prose]")) {
    window.ELVIA_MATH.renderInto(node, node.textContent, {
      replacements: presentation.replacements || [], renderer: window.katex
    });
  }
  const evidenceDetails = [...document.querySelectorAll("details.evidence-details")];
  if (evidenceDetails.length) {
    const revealFragment = () => {
      let id;
      try { id = decodeURIComponent(window.location.hash.slice(1)); }
      catch { return; }
      if (!id) return;
      const target = document.getElementById(id);
      if (!target) return;
      let expanded = false;
      for (let node = target; node; node = node.parentElement) {
        if (node.tagName === "DETAILS" && !node.open) {
          node.open = true;
          expanded = true;
        }
      }
      if (expanded) target.scrollIntoView({block: "start"});
    };
    window.addEventListener("hashchange", revealFragment);
    revealFragment();
    let printState = null;
    window.addEventListener("beforeprint", () => {
      if (!printState) printState = evidenceDetails.map(node => [node, node.open]);
      for (const node of evidenceDetails) node.open = true;
    });
    window.addEventListener("afterprint", () => {
      if (printState) for (const [node, open] of printState) node.open = open;
      printState = null;
    });
  }
  const labels = {
    "analysis-plain": "Analysis citation (plain text)", "analysis-bibtex": "Analysis citation (BibTeX)",
    "analysis-ris": "Analysis citation (RIS)", "original-plain": "Original paper citation (plain text)",
    "original-bibtex": "Original paper citation (BibTeX)", "original-ris": "Original paper citation (RIS)",
    "ai-short": "AI context (short)", "ai-full": "AI context (full)"
  };
  for (const section of document.querySelectorAll("[data-context-key]")) {
    const exports = (window.ELVIA_CASE_CONTEXT || {})[section.dataset.contextKey];
    if (!exports) continue;
    const format = section.querySelector("[data-copy-format]");
    const text = section.querySelector("[data-copy-text]");
    const status = section.querySelector(".copy-status");
    const details = section.querySelector(".copy-options");
    const choose = mode => {
      if (typeof exports[mode] !== "string") return false;
      format.value = mode;
      text.value = exports[mode];
      return true;
    };
    const copy = async mode => {
      if (!choose(mode)) return;
      status.textContent = "";
      try {
        if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error("Clipboard unavailable");
        await navigator.clipboard.writeText(text.value);
        status.textContent = `${labels[mode]} copied.`;
      } catch {
        details.open = true;
        text.focus();
        text.select();
        status.textContent = "Clipboard access is unavailable. The text is selected below; press Ctrl+C or ⌘C, or use your device’s Copy action.";
      }
    };
    for (const control of section.querySelectorAll("[hidden]")) control.hidden = false;
    for (const button of section.querySelectorAll("[data-copy-mode]")) {
      button.addEventListener("click", () => copy(button.dataset.copyMode));
    }
    format.addEventListener("change", () => {
      if (choose(format.value)) status.textContent = `${labels[format.value]} ready to copy.`;
    });
    section.querySelector("[data-copy-selected]").addEventListener("click", () => copy(format.value));
  }
})();
