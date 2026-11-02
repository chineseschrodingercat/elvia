# Load the Atlas directory before full scientific context

Date: 2026-11-02

Work is tracked in [Issue #33](https://github.com/chineseschrodingercat/elvia/issues/33).

## Problem

The Scientific evidence notes page initially loaded `data.js` before the list
application could run. In the accepted 1,214-case release this file contains
45,959,438 bytes, or 10,110,438 bytes with gzip level 6. Complete reports, evidence
and scientific records therefore blocked the first ten case links even when the
reader only wanted to browse the collection.

## Decision

Generate a compact discovery payload for the initial directory. It carries the
metadata, exact existing briefs, presentation and assessment information needed
for browsing, counts, filters and pagination. Ordinary case links continue to
open the complete canonical static HTML pages.

Load a separate search projection only when a nonempty query needs it. Preserve
every field read by the existing search index, including retained report text,
finding arguments, source locators, proposed repairs and revision-matched DOI
metadata. Keep the same normalization, weights, full-collection term frequency,
phrase scoring and finding anchors. Filtering follows retrieval as before.
While loading, show an explicit search status and apply the current query when
the request completes. Reset and browser navigation must supersede stale input.

For legacy `#case=` links, load only that case's complete projection. Keep the
original record, note, reader citation, mathematical presentation and download
binding together. Validate the collection, case and revision before displaying
it; allow recovery from a failed request without showing another case's content.

The complete `data.json` and `data.js` exports remain available. New projections
are derived from the same validated payload and bound to the exact complete JSON
bytes. All new resources enter the existing serving manifests. No new public
API, paid service, credential, dependency or server permission is required.

## Boundaries and verification

This change affects retrieval and presentation, not scientific decisions. Keep
authoritative snapshots, complete statements, proofs, review status, citations,
static pages and reader archives intact. Verify the initial dependency boundary,
search equivalence, counts and filters, lazy case loading and failure recovery.
Measure startup payload bytes separately from conditional search and case data.
Browser timing depends on network and cache conditions; payload reduction alone
does not establish a universal page-load duration.

Repository checks, the five final-head CI results and production rollout evidence
belong to Issue #33. Follow the existing compatible release and protected-state
backup procedure before deployment.
