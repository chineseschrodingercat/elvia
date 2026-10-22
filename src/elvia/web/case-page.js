/* Progressive math rendering: all scientific prose is already in the HTML. */
"use strict";
(() => {
  const presentation = window.ELVIA_CASE_PRESENTATION || {};
  for (const node of document.querySelectorAll("[data-case-prose]")) {
    window.ELVIA_MATH.renderInto(node, node.textContent, {
      replacements: presentation.replacements || [], renderer: window.katex
    });
  }
})();
