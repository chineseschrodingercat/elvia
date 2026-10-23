# Project status

The public website is [elvia-atlas.org](https://elvia-atlas.org/). It hosts the
homepage, 300-paper NeurIPS 2025 Atlas and contribution workspace. Windows starts
the service after boot; the computer must remain awake and connected.

## Current collection

- 300 first-edition scientific records.
- 104 Major, 177 Minor, 3 Needs Evidence and 16 No Issue Found assessments.
- 284 detailed notes with 1,088 problem sections.
- Independent scientific decisions remain pending.

## Contributor onboarding update — 23 October 2026

Ordinary registration now opens contribution choices. Required markers are
larger, red and starred. The reviewer application offers 28 positions, live ROR
institution suggestions with manual entry, 496 searchable expertise options
(optional; at most five including Other), and research-profile type/URL fields.
Contact is linked in public headers and has a dedicated page.

Submitted applicants see a 1–3 day estimate and Submitted / Under review /
Approved progress. Opening an individual application starts review; loading the
management queue does not. Stage changes queue email to the verified applicant,
with persistent retries, ordering and duplicate-transition protection. Requests
for more information and declines retain their own states and resubmission path.
An additive table preserves all earlier operational rows; no retrospective
stage emails are queued during migration.

Meaningful failing regressions reproduced the old routing, required-expertise,
selection-limit and missing-progress behavior. The browser walkthrough verified
registration, institution keyboard selection, five-field enforcement, Other
inputs and automatic Submitted → Under review → Approved transitions across
separate applicant/staff sessions. A 390-pixel layout showed no horizontal
overflow. Email was captured locally, not delivered to real users. Final local
checks, five CI results, backup/restore and rollout evidence belong to
[Issue #16](https://github.com/chineseschrodingercat/elvia/issues/16).
See [the decision](decisions/0007-contributor-onboarding.md).

## Evidence readability update — 23 October 2026

Case pages now show each complete key finding, all case limitations and the
review status before a native expandable evidence section. Detailed claims,
conditions, calculations and proposed repairs remain in the initial HTML response.
Copy for AI and citation packets are independent of disclosure state. The brief
no longer repeats the complete derivation before the detailed argument.

Keyboard disclosure, deep-link expansion and temporary print expansion have
regression coverage. Focused Python regressions, 141 Node tests and 225 isolated
backend tests passed. Full collection preservation, first-visit browser checks,
final CI and deployment evidence are tracked in
[Issue #14](https://github.com/chineseschrodingercat/elvia/issues/14).
See [the decision](decisions/0006-readable-evidence.md).

## Research discovery update — 23 October 2026

The ten P0 items in [Issue #12](https://github.com/chineseschrodingercat/elvia/issues/12)
add question-oriented local search, visible finding briefs, separate citations
for analyses and original papers (plain text, BibTeX and RIS), and short/full
Copy for AI context with revision, source, scope, review status and snapshot hash.
No model API or paid search service is used. Public template/examples and four
worked reading paths are available before registration. The 309-URL sitemap uses
the actual record timestamp for each case. Authoritative scientific JSON remains
unchanged.

Google's live inspection fetched a case successfully and confirmed indexing;
Search generative AI participation was set to Include. Cloudflare observed real
OAI-SearchBot, ChatGPT-User, PerplexityBot and BingBot requests with crawler blocks
off. Direct-open failures in the research tool persist without an HTTP diagnosis;
they do not establish that these crawlers are blocked. Index coverage is still
processing. Search appearance and ranking are not guaranteed.

Canonical public reads now send bounded shared-cache headers. APIs, account/query
routes, errors and session-setting responses remain uncached. The narrow free
Cloudflare cache rule, Bing verification, deployment and interruption check are
tracked in Issue #12. Warm cache availability does not guarantee cold-cache or
whole-PC outage coverage.

Local verification: 253 core tests passed with two Windows privilege skips,
followed by all seven public-context regressions after two additional tests;
225 isolated backend tests and 138 Node tests passed. Locked dependencies, Ruff,
both validators, 20,819 mathematical expressions, package build and fresh installed
wheel offline smoke passed. Release audits check all 300 records/contexts,
600 PDF members and 2,776 AI packets. Browser checks verified actual copy/paste,
citation identity and question-to-problem navigation. Final CI, deployment and
post-deployment evidence belong to Issue #12. See the
[discovery decision](decisions/0005-public-discovery.md).

PR CI on Ubuntu/Python 3.12 exposed a crawler-rule ordering incompatibility:
`urllib.robotparser` allowed `OAI-SearchBot` to read `/api/contributions` because
that interpreter uses the first matching rule and encountered `Allow: /` first.
The failure was reproduced locally with Python 3.12.15. Each crawler group now
places `Disallow: /api/` before the general allow rule, preserving the intended
public-reading policy for both first-match and longest-match readers. All 12
crawler checks and the 18-test public-ingress suite pass locally on Python 3.12.15
and 3.13. The robots file is outside the Atlas manifest; scientific records and
the verified reading release are unchanged. Final CI results remain in Issue #12.

## File contribution update — 23 October 2026

Both contribution routes now upload a PDF or complete LaTeX report instead of
requiring a manually prepared ZIP or retyping each scientific finding. Each route
shows only its corresponding LaTeX and three-page PDF template. First reports
also provide separate article and applicable original-supplement PDFs; revisions
retain those sources and optionally link existing problem numbers. Verification
code accepts one ZIP or up to ten files, with a visible 5 MiB total limit.
The report's 20 MiB limit and the original PDFs' combined 50 MiB limit appear only
when exceeded, with compression guidance. Replacing a PDF recalculates the total.

Signed-in entry and upload pages prominently encourage ChatGPT, Claude or Gemini
assistance and welcome fully manual reviews. AI configuration is free text;
suggested settings are recommendations, not an allowlist. Scientific detail and
AI provenance remain in the uploaded report. The application does not execute
code, compile uploaded TeX or infer scientific correctness from file validation.

Paper reservations persist through editorial acceptance until a maintainer/admin
verifies integration into a newer deployed record. Reading pages show the current
availability; simultaneous claim attempts are excluded transactionally. Existing
operational rows are preserved by an additive migration, rehearsed through a
verified backup and separate restore. Authoritative scientific JSON is unchanged.

Local verification includes 244 core tests (2 Windows symlink-privilege skips),
120 Node tests, both record validators, 20,819 checked mathematical expressions,
package build and a fresh installed-wheel offline smoke. All 300 case contexts,
600 reader PDF members and 3,380 release manifest files were checked. Both report
templates were compiled and all six PDF pages inspected. Isolated browser checks
cover new-tab entry, matching templates, upload, saved-file recovery, both report
formats, free-text AI configuration and a 390-pixel mobile viewport. Synthetic
providers do not verify live email or Turnstile.

[Issue #8](https://github.com/chineseschrodingercat/elvia/issues/8) owns the final
225-test backend run, five CI results, acceptance/integration walkthrough and
production deployment evidence. See [the workflow decision](decisions/0004-browser-reports.md).

Merged-head Windows CI exposed two test timing failures: a fixture HTTP deadline
and a slot-saturation setup racing request cleanup. The fixture now uses bounded
waiting and releases partially acquired slots; production concurrency limits and
request behavior are unchanged. Issue #8 retains both failures and final checks.
The asynchronous reset-mail test also holds delivery behind an explicit event,
checks acknowledgement before delivery completes, and drains worker slots on
both success and failure before deleting its isolated database. Its former
one-second VM deadline and incomplete failure cleanup are recorded in Issue #8.

## Reading update — 22 October 2026

The current update adds a dedicated password-reset completion page, verified
article citations with DOI links, clearer assessment/status typography, concise
supporting information and PDF reader bundles.

Local verification: 235 core tests passed (2 Windows symlink privilege skips),
201 isolated website backend tests passed, and 106 Node tests passed. The
collection checker covered 20,819 mathematical expressions without errors.
Locked dependency sync, lint/format checks, both record validators, package build
and fresh installed-wheel offline smoke passed.

All 300 article PDFs and 300 report PDFs parsed successfully. All 300 reader ZIPs
contain exactly the two intended PDFs with verified identities and valid CRCs.
Report layout checks found no remaining missing glyphs or overfull boxes; selected
reports and the desktop reading views were inspected visually. Scientific record
and evidence source bytes remain unchanged.

The [public repository](https://github.com/chineseschrodingercat/elvia) starts
with a clean snapshot of the maintained source and current collection. Earlier
development history remains in a separate private archive. Operational data,
credentials, private submissions and generated reader PDFs are outside Git.
[Issues](https://github.com/chineseschrodingercat/elvia/issues) track current
work, and [Actions](https://github.com/chineseschrodingercat/elvia/actions)
records the checks for each public commit.

## Search discovery update — 22 October 2026

Public reading pages now permit indexing. The Atlas provides 300 readable HTML
case URLs, and the root sitemap lists 307 public URLs. The homepage links to
public contribution and platform-selection guides. Account/recovery pages,
account query routes, APIs and errors retain indexing exclusions. The homepage
also contains the maintainer's public Google ownership-verification tag.

Local checks: 240 core tests passed with 2 Windows symlink-privilege skips;
202 isolated website backend tests and 106 Node tests passed. An initial backend
run had one Windows socket-abort error; the affected 11-test group and the full
202-test repeat passed without a source workaround. Locked sync, Ruff lint and
format checks, both record validators, the 20,819-expression collection check,
package build and fresh installed-wheel offline smoke passed. The source package
contains all 1,503 currently tracked collection files with exact bytes.

Release checks covered all 307 canonical/indexable URLs, internal links and file
hashes. All 300 case pages preserve the scientific prose, and all 300 reader ZIPs
retain the exact two existing PDFs. The standalone script rendered 14,093 prose
nodes and 10,472 mathematical expressions without fallback. Chrome desktop and
390-pixel mobile reading views were inspected. Scientific snapshots and evidence
sources remain unchanged. These are engineering checks, not scientific review.

See [search discovery](search-discovery.md) for query hypotheses and page routes.
[Issue #2](https://github.com/chineseschrodingercat/elvia/issues/2) records final
integration, deployment and Search Console outcomes. Submission and ownership
verification are separate from Google's later indexing and ranking decisions.
Repository inspection found no branch protection or rulesets; required check
results must be verified explicitly, rather than claimed as server-enforced.

## Contributor journey update — 22 October 2026

Case pages now show the current independent-review status and scoped summary
before the detailed findings, with a contents list and a contribution link for
each finding. The selected paper and finding follow registration into a saved
draft. Only source identity is prefilled; scientific judgments and declarations
remain for the contributor. Legal documents open in labeled separate tabs so
reading them does not clear registration progress. Account-persistence wording
and pending-application actions are consistent with the public service.

Local checks: 242 core tests passed (2 Windows symlink-privilege skips), 202
isolated website backend tests and 110 Node tests passed. Locked sync, Ruff,
both record validators, the 20,819-expression check, package build and fresh
installed-wheel offline smoke passed. A synthetic browser journey exercised
registration, both legal links, contextual draft creation, save and reload.
Email was captured locally; this does not verify production email or Turnstile.
The repeated bounded heuristic walkthrough scores 9/10, up from 6/10. The
remaining minor friction is preparing the required ZIP without an inline starter
example; this score is not independent human usability research.

The repository About description, seven relevant Topics and contributor-first
README explain research verification and paper correction. Repeating the same
eight non-brand GitHub queries with Repositories / Best match / page one found
the repository at position 7 for `paper errata` and position 9 for
`post publication peer review`; the other six first pages still had no match.
The earlier pass found no match on any of the eight first pages. This is a
same-session observation, not a guarantee of future rankings.

[Issue #4](https://github.com/chineseschrodingercat/elvia/issues/4) records the
integration, release checks and deployment outcome. Scientific records, review
authority and production account data are outside this interface change.

## First-visit update — 22 October 2026

An expanded cold-visitor walkthrough found a guest-workspace detour omitted by
the earlier bounded 9/10 assessment; that expanded starting route scored 6/10.
The participation guide and guest workspace now offer contextual registration
and sign-in directly. Signed-in members can continue to their selected note.
The homepage adds search and three real, scoped research questions. Atlas search
and results precede extended interpretation guidance and collection counts.
A plain-text starter and explicitly fictional example explain a small report,
including the standard ZIP accepted by the existing upload validator.

Local verification: 243 core tests passed (2 Windows symlink-privilege skips),
202 isolated website backend tests passed, and 114 Node tests passed. Three
new routing/search regressions failed before the fixes and passed afterward.
Locked sync, Ruff lint/format, both record validators, all 20,819 mathematical
expressions, package build and fresh installed-wheel offline smoke passed.
Release verification covered 3,380 file hashes, 300 case/context pairs, 1,088
finding links and 307 sitemap URLs. All 600 reader PDF members and scientific
record/source bytes are unchanged.

The browser walkthrough checks both guest entry paths and the retained paper
and finding at registration and sign-in. At 1280 × 720, the homepage search starts
at approximately 328 px and the first featured question at 628 px. Account and
draft mutations use isolated fixtures; these checks do not establish production
mail delivery, conversion rates, search rankings or scientific correctness.
[Issue #6](https://github.com/chineseschrodingercat/elvia/issues/6) tracks final
CI, compatible deployment and the repeated public desktop/narrow walkthrough.
See [the decision](decisions/0003-first-visit-contribution.md) for scope.

## Operations

Code and generated site files are separate from protected account/attachment
state. The automatic startup task has been exercised with manual start/stop and
process recovery; an actual computer reboot has not been observed in validation.
There is no configured off-machine disaster-recovery service.

See [website operations](../website/README.md),
[publication workflow](publication-workflow.md) and [project direction](ROADMAP.md).
