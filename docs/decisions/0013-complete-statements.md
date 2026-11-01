# Complete source statements and wider case arguments

Date: 1 November 2026

Issue: https://github.com/chineseschrodingercat/elvia/issues/31

This decision supersedes the Sources subsection and narrow problem layout in
decision 0012. It changes reader presentation, not scientific assessments,
original reports, immutable records or downloadable evidence.

## Reading layout

Remove the Atlas title directory, the Read each finding in context introduction
and the Keep the argument within reach section. Retain Assessment definitions
and collection counts and the site's standard navigation.

Case arguments occupy the same desktop width as Key findings. Remove the blue
rule above each problem; use a three-pixel black rule beneath Key findings.
Native disclosures, keyboard access and narrow-screen wrapping remain available.
Remove the standalone Sources subsection and redundant Statement subheading.
Keep the whole-note citation controls, full-context disclosure and the recorded
problem-specific Possible revision behavior established in decision 0012.

## Mathematical statements

Problem statement identifies the original claim, its mathematical objects,
domains, hypotheses, quantifiers and conclusion. Source theorem/lemma/equation
locators belong in the statement's prose. Counterexample parameters and proposed
repair hypotheses must not be presented as premises of the original claim.
Where a report leaves an important condition unclear, consult the exact original
PDF bound to that record, rather than substituting a newer version of the paper.

The Math 2025 collection has a separate `statement-presentations.json` catalog.
Each entry binds its paragraphs to the record revision and canonical record,
report and problem hashes. Its basis identifies retained report paragraphs or
page numbers in the exact source PDF. Same-revision drift fails before export;
a newer revision does not inherit an old presentation. This catalog is edited
prose, not a new scientific finding or an independent review decision.

Without a curated entry, preserve the retained claim. Only an explicit source
role or an unambiguous original-statement section may supplement it. Legacy
assumptions whose role is unspecified remain with the verification argument;
they may describe a witness instead of an original hypothesis. Do not infer a
source theorem from the first paragraph of a proof or a repair.

Build the shared statement paragraphs once for both static pages and the dynamic
Atlas. Add them to full AI context alongside the unchanged original claim,
analysis, scope and retained report. Keep source finding identifiers and links
independent of severity-sorted display numbering.

## Verification

Use source-binding and role-separation regressions, strict mathematical rendering
of all curated paragraphs, full collection preservation checks, representative
desktop and narrow-screen reading checks, and the five existing final-head CI
jobs. Deployment requires the existing verified backup and protected-state
comparison. These checks establish presentation and data integrity, not the
scientific validity of the reports.
