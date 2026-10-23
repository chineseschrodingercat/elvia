# Project status

The public website is [elvia-atlas.org](https://elvia-atlas.org/). It hosts the
homepage, 300-paper NeurIPS 2025 Atlas and contribution workspace. Windows starts
the service after boot; the computer must remain awake and connected.

## Current collection

- 300 first-edition scientific records.
- 104 Major, 177 Minor, 3 Needs Evidence and 16 No Issue Found assessments.
- 284 detailed notes with 1,088 problem sections.
- Independent scientific decisions remain pending.

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
