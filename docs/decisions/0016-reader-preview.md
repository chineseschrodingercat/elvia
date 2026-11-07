# Reader-first local preview

Date: 6 November 2026. Status: local implementation for maintainer review;
not deployed or integrated into main.

## Request

Implement the four findings from the target-reader walkthrough: more useful
text search, less obstruction on mobile, a short case-reading introduction,
and a prominent route through worked arguments. Keep source identity and
review status understandable at the point of reading. Illustrations and
animation are outside this change.

This continues the website planning scope of Issue #36 and the collection
loading work in Issue #33. The present authorization is local only; it does
not authorize publication, production operations or GitHub integration.

## Decisions

- Keep the ELVIA identity and original paper titles. The homepage leads with
  "Build the future on evidence." Reading actions precede account access.
- Describe search as matching public analysis text. Provide working examples;
  do not present a generated-answer service. Improve query ranking and encode
  repeated searchable text compactly while retaining full-search coverage.
- Keep Field and Assessment visible. Venue and Finding remain available in a
  native More filters disclosure, with active-filter feedback. Move the
  contribution invitation below results and reduce list metadata emphasis.
- Put inspected source version, analysis revision, analysis origin and
  independent review status together. Use source-bound introductory prose
  before citation tools and the complete problems. If a retained article-level
  abstract is absent, identify the first recorded finding as such; never
  silently treat it as a complete assessment of the paper. State explicitly
  when no concise summary is available.
- Retain full proofs, original problem IDs and source locations, rebuttal and
  counterevidence, context exports, citation tools, print and report links.
  Contribution availability is compact and follows immediate reader value.
- Promote the existing worked paths and add one source-bound mathematics
  path for *Lower bounds for incidences*, revision 1. Its example targets a
  comparison step; it does not establish the final incidence exponents false.

Scientific records, source/report bytes, formal decisions, review requirements
and production state remain unchanged. An interface improvement provides no
new scientific adjudication or evidence of real-user growth.

## Verification and review

Run the current AGENTS.md checks and isolated backend suite, with fresh
task-owned temporary directories. Inspect representative actual rendered pages
at desktop and narrow viewport widths, including a long mathematical proof,
no-issue case, query/filter/reset behavior and the worked-path destination.
Record actual results in the local acceptance report and docs/STATUS.md.

The preview uses a separate worktree, a loopback-only listener and fresh local
state without mail/OAuth providers. A build without the separately maintained
public PDF library is a source preview and does not offer reader ZIP downloads.
The maintainer reviews the local URL before any later integration or rollout.
