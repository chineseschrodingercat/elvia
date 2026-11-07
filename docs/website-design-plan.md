# ELVIA: a website built around inspectable scientific arguments

Proposed direction, 6 November 2026. Planning only; no frontend implementation or deployment. Source baseline: `04fc9a5efebaa27f025143bedbeba0a868a75c3d`. Work tracking: [Issue #36](https://github.com/chineseschrodingercat/elvia/issues/36).

## 1. Positioning and current evidence

Keep **ELVIA**, repository **elvia**, and **elvia-atlas.org**. Use **Open Infrastructure for Scientific Verification** as the public descriptor and **Build the future on evidence.** as the mission. The ambition is infrastructure through which scientific arguments can be inspected, challenged and retained. Today's concrete entry point is the Atlas and contribution workspace. Automatic URL auditing, dependency maps and demonstrated downstream impact are future possibilities, not implemented services.

The checked latest records contain **1,214 papers: 514 Math, 400 ICML and 300 NeurIPS**, all with pending independent scientific decisions. `docs/protocol.md`, `docs/STATUS.md` and the three `studies/*/records/` collections establish these boundaries. Preliminary assessment totals must never become confirmed-error statistics. The historical 300-paper wording in `AGENTS.md` is superseded for collection size by the current records and protocol.

The source audit supports four concrete observations:

| Source owner and route | Observation | Proposed response |
| --- | --- | --- |
| `website/preview/site/index.html`, `/` | Hero already offers search and guest reading, but also gives registration and sign-in substantial first-screen space. | Make reading the dominant action; retain unobtrusive contributor access. |
| Same homepage | Several captions still describe only ICML/NeurIPS or an initial machine-learning collection despite the Math import. | Generate collection references consistently from the maintained collection configuration. |
| `website/atlas-assets/index.html` and `atlas.js`, `/atlas/` | Five-field discovery, ranked text search, pagination and pending labels exist. | Preserve these capabilities and loading projections while improving hierarchy. |
| `src/elvia/search_pages.py`, `src/elvia/web/case-note.js`, `case-page.js`, `case-page.css`; `/atlas/cases/{case_id}.html` | Canonical pages retain complete arguments, disclosures, source-index fragments, citation exports and print expansion. | Treat the reading surface as a scientific document, preserving these contracts. |

The hypothesis is that the current homepage underexpresses the project's scientific ambition and competes with its reading action. This is a **heuristic inference from source**, not an observed user-study result or numeric UX score. No rendered-device audit was performed for this proposal.

## 2. People, actions and continuity

Researchers evaluating a result should **find the paper and inspect a claim**. Mathematicians and methods specialists should **follow the decisive argument and its hypotheses**. Potential contributors should **choose a bounded check, inspect availability and prepare a report**. Software contributors should **reach the source and relevant Issue**. These are scientific reading journeys, not a media fact-checking feed.

Guest journey: homepage search → Atlas match → canonical case → numbered problem → original source and complete argument → optional report download or contribution. Reading, citations and source inspection remain available without registration. Supporting the original claim, documenting counterevidence and leaving a question unresolved remain useful outcomes. Current scientific work prioritizes decisive falsification; completing a repair is optional.

Use the existing context implementation in `website/preview/site/case-context.js`, `participate-entry.js`, `home-entry.js` and `workspace.js`. A selected case travels as `case={case_id}`, optionally `problem={source_index}`, through `/participate.html` or `/contribute.html?view=compose`. Registration and login remain homepage views, with the existing same-origin `next` validation. After authentication, restore the selected paper and revision draft, not a generic dashboard. Validate context against the generated `.context.json`; never silently substitute another paper. Preserve invalid-context feedback and a route back to the Atlas.

Availability is operational, separate from scientific status. Keep its existing loading, unavailable and retry states from `paper-availability.js`. An editorial submission or acceptance never changes adjudication automatically. Independent review of others' contributions retains its separate application.

## 3. Navigation and route map

Header: ELVIA → **Atlas**, **Reading paths**, **Method**, **Contribute**; small **Sign in** and GitHub links. On mobile, use a labelled Menu button with `aria-expanded`, Escape dismissal and focus return. Footer: maintainer identity, source, protocol, contact, privacy, terms and licenses. Do not invent a team or partner roster.

| Route | State and treatment |
| --- | --- |
| `/` | Existing; mission and reading entrance. |
| `/atlas/` | Existing; searchable collection. Preserve existing query/filter/history behavior. |
| `/atlas/cases/{case_id}.html#problem-{source_index}` | Existing canonical case and fragment contract; retain source identity and stable IDs. |
| `/exemplary-cases.html` | Existing worked-reading guide; retain URL and link to proposed paths. |
| `/project.html#protocol` | Existing method destination; `/project.html#governance` explains authority. |
| `/participate.html`, `/report-templates.html` | Existing public onboarding and templates. |
| `/contribute.html?view=compose`, `?view=my-work`, `?view=contributors` | Existing workspace views; preserve access boundaries. |
| `/?view=login#contributor-access`, `/?view=register#contributor-access` | Existing access routes, preserving validated `next` context. |
| `/contact.html`, `/privacy.html`, `/terms.html` | Existing secondary pages. |
| `/reading-paths/` and `/reading-paths/{editorial_slug}.html` | Proposed editorial hub and two initial stories; link onward to canonical cases. |

Hierarchy: home → Atlas → case; home → reading-path hub → selected story → canonical problem; each case → method and optional contribution. Search results always link to canonical cases. Editorial pages carry their own canonical URL and a prominent original-paper citation; they do not duplicate or replace case records. Preserve legacy `#case=` links handled by the Atlas. Add proposed pages to the maintained sitemap only when implemented; retain current account indexing exclusions.

## 4. Homepage sequence and focal moment

Desktop uses a 1,248 px shell. The opening has a seven-column text area and five-column source-grounded figure. The following order is the implementation brief:

1. **Header**, approximately 80 px high, with the descriptor beside the wordmark where it fits.
2. **Hero**: H1 **“Build the future on evidence.”** The descriptor belongs with the wordmark or in the supporting introduction, rather than a separate decorative eyebrow. Body: **“Inspect the proofs, assumptions and counterexamples behind scientific claims. Start with a paper analysis, follow the argument, and contribute a check others can examine.”** Primary CTA **“Explore the Atlas”** → `/atlas/`. Secondary text CTA **“Follow a worked argument”** → proposed `/reading-paths/`.
3. **Visible boundary**, immediately beneath the actions: **“1,214 paper analyses · Independent scientific decisions pending.”** Link “How review works” to `/project.html#protocol`.
4. **Search**, full width below the hero composition: label **“Find a paper or a question”**; placeholder **“Title, author, DOI or a question”**; button **“Search the Atlas”**. Keep GET submission to `/atlas/` with `q`. Explain “Search matches the public analysis text.” Do not imply a generated answer or automatic auditing service.
5. **Selected arguments**, initially two stories, eventually 3–5. Show a question-led heading, original title, field, one scoped implication and pending status. Avoid severity leaderboards.
6. **How evidence becomes reusable**: Source → Assumptions → Argument → Scope, with a method link. Follow with a compact present-service/future-ambition distinction.
7. **Contribution entrance**, “Start with one useful check,” public guide and templates; then sole-maintainer identity and footer.

The focal figure is two parallel lines on opposite sides of an origin, tied to math2025-0071. Caption: “Equal unsigned offsets can hide distinct lines. See the exact claim and its limits.” Use a proposed editorial heading “Two parallel lines and a lost sign.” The artwork links to the original-titled case, and carries “Illustration of the retained preliminary analysis.” No animated verdict or fabricated evidence network.

Below 768 px, stack header, hero copy, actions, pending boundary, search, figure, stories and remaining sections. Keep the first reading action and status before the illustration. Use a static figure, one-column stories and full-width search button where necessary. No forced scroll sequence or account interruption.

## 5. Atlas and canonical reading surface

Atlas begins with its title, one sentence of purpose and visible pending-review explanation. Search occupies the main row; Field and Assessment remain immediately available. Venue and Finding may sit in one labelled “More filters” disclosure on small screens, with active selections visible outside it. Keep the five approved field names exactly. Preserve the existing title ordering without a query, best-match ordering with a query, result count, reset, page-size choices and top/bottom pagination.

Each result row prioritizes original article title, field/venue/year, one analysis excerpt, preliminary assessment and explicit independent-review status. Availability is secondary. Keep query-match explanations and links to the matched problem. Loading distinguishes discovery from search-index loading; failure preserves the entered query and offers retry. Empty results offer reset and alternative terms. Preserve compact discovery and lazy search payloads; do not fetch full reports to draw the list.

Canonical page sequence: breadcrumb → **original article title** → authors/source/version/revision → visible pending status and important scope → **one Analysis abstract** → existing whole-note citation/context controls → black **Key findings** separator → numbered problems → supporting record/provenance and download. Preserve current full-width desktop problems; add no repair column, repeated “finding at a glance” boxes or duplicate contents navigation.

Within each problem, retain coherent **Problem statement**, useful **Source and Method** content, rigorous **Proof** or unresolved **Verification**, then **Detailed finding and scope**. The current renderer has removed a separate Sources subsection and still displays Possible revision; consolidate useful locator/method text and optional correction into the scoped narrative rather than reintroducing duplicate source panels or mandatory repair placeholders. This is a proposed presentation change, not scientific reassessment. Preserve all derivation steps, counterevidence and scope. Sort Major, Minor, Needs Evidence stably; never derive fragments from the new visible ordering. No Issue Found checks remain brief without invented numbered problems.

Retain native evidence disclosures and source text in initial HTML. Impact and review limitations remain outside closed disclosures. Keep original-paper quotation or precise-locator fallback, full report access, Copy for AI context, citation formats and the exact full-width button **“Download report files (.zip)”**. Do not revive the retired report/provenance duplicate sections.

## 6. Visual and interaction specification

The domain is a scientific notebook: hypotheses, witnesses, inequalities, source passages and bounded conclusions. The signature is a source-bound geometric or algebraic witness, paired with strong editorial type and quiet reading controls.

| Token/component | Proposed value |
| --- | --- |
| Fonts | Existing bundled Source Serif 4 for headings and proof prose; Source Sans 3 for overview text, navigation and controls; bundled KaTeX math fonts. Retain licenses. |
| Typography | Body 18/29 px; case prose 19/31 px; controls 16/24 px; metadata 14/21 px; H2 36/42 px; hero `clamp(44px,6vw,80px)` with 1.05 line height. |
| Color | Paper `#FFFFFF`; ink `#111111`; secondary `#454545`; action/focus `#2548CC`; tint `#EDF1FF`; separator `#C5C5C5`. Use labelled assessment chips; never color alone. |
| Space/width | 4, 8, 12, 16, 24, 32, 48, 72, 96 px scale; shell 1,248 px; ordinary prose 72ch; proof region can use the shell width. |
| Breakpoints | <768 px single column, 16 px gutters; 768–1,023 px 24 px gutters; ≥1,024 px 48 px gutters and two-column hero. |
| Components | Button/input minimum 44 px target, 48 px normal height; 4 px control radius; 1 px rule; no decorative shadow stack. |

Keep body/link contrast at least 4.5:1, large text and control boundaries at least 3:1 where required. Check actual combinations during implementation. Underline prose links. Focus-visible uses a 3 px blue outline with 3 px offset; hover adds underline/tint, pressed darkens, disabled has a visible reason where useful. Busy states show text and prevent duplicate actions without removing focus. Error messages preserve input and identify recovery. Respect forced colors and 200–400% zoom.

Long equations use meaningful aligned breaks when scientifically equivalent; otherwise a labelled horizontally scrollable equation region, without page-wide overflow or shrinking into illegibility. Keep minus signs, exponents and quantifiers intact. Keyboard users can reach disclosures, scroll regions and copy controls. Fragment navigation opens enclosing disclosures and offsets the sticky header. Print expands arguments, retains citation/status/caption, removes navigation and restores disclosure state afterward. Preserve the existing `case-page.js` behavior. Reduced motion disables movement and smooth scrolling; any optional transition is ≤180 ms and never carries scientific meaning.

## 7. Two verified editorial candidates

**math2025-0071 — Lower bounds for incidences**, Alex Cohen, Cosmin Pohoata and Dmitrii Zakharov, *Inventiones mathematicae* 240 (2025), 1045–1118, [DOI](https://doi.org/10.1007/s00222-025-01331-2). Checked `studies/math2025/records/math2025-0071.r1.json`, its bound report and `studies/math2025/case-notes.json`. Reading destination: `/atlas/cases/math2025-0071.html#problem-1`. The retained witness uses lines `y=1/4` and `y=-1/4`: unsigned-distance comparison collapses while phase-space separation remains. Minimal diagram: labelled axes, both lines, equal unsigned offsets, and the exact contrasting quantities. Scholarly value is making the lost sign and failed comparison inspectable. The incidence exponents, phase-space isometry and whole paper are not refuted; the second lattice issue remains separately available. Adjudication is pending.

**neurips2025-0029-private-hyperparameter-tuning-with-ex-post-guarantee — Private Hyperparameter Tuning with Ex-Post Guarantee**, Badih Ghazi, Pritish Kamath, Alexander Knop, Ravi Kumar, Pasin Manurangsi and Chiyuan Zhang, [NeurIPS 2025 proceedings](https://proceedings.neurips.cc/paper_files/paper/2025/hash/bd52e86ac018b3131276661901063ef8-Abstract-Conference.html). Checked its revision-1 record and `studies/neurips2025/case-notes.json`. Destination: `/atlas/cases/neurips2025-0029-private-hyperparameter-tuning-with-ex-post-guarantee.html#problem-1`. The retained witness has `alpha=2`, `epsilon=log(2)`, `ell=1`, `a=1/200`, `b=1/10`. Minimal diagram: ordered markers for the intermediate bound `exp(3/200)`, actual product `39601/39000`, and retained final bound `exp(1/8)`, with hypotheses and official Lemma 16, Appendix B, p.23. Scholarly value is separating a false intermediate inequality from a surviving final statement. No privacy violation, larger required privacy budget, author adoption or complete privacy audit is established. Adjudication and repair verification remain pending.

Commission only 3–5 initial flagship illustrations. Every diagram must bind to a case revision, locator and retained argument; provide editable SVG, textual equivalent and full caption. Diagrams explain existing evidence, never substitute for proof. Other analyses remain complete text. Select for explanatory value rather than severity, and retain surviving claims visibly.

## 8. Delivery phases, checks and learning

**Phase 1:** approved copy and route/content matrix, then static desktop/mobile specimens using existing HTML/CSS and assets. Acceptance: mission, current capability and pending boundary distinguishable; both example journeys preserve paper identity. **Phase 2:** shared header/tokens, homepage, Atlas rows and canonical presentation in a separate source preview. Add meaningful failing regressions for changed routing or disclosure behavior before implementation. **Phase 3:** selected SVGs and editorial routes with canonical links, source binding and accessibility review. No backend/schema redesign or production rollout belongs to this plan.

For implementation, follow `AGENTS.md` and `.github/workflows/ci.yml`: `uv sync --locked`; Ruff check/format; pytest; all three collection validators plus synthetic-demo validation; `uv build`; `node --test tests/*.test.cjs website/preview/tests/*.test.*`; review-note and ICML/Math format checks; isolated backend runner `website/preview/tests/run_private_auth_backend.py local all`. Relevant regressions include `first_visit_journey.test.mjs`, `atlas_pagination.test.cjs`, `test_private_origin.py`, `tests/test_website_storage.py` and case-layout tests. Use synthetic state, no real mail or live-state mutations. Retain five CI check names and verify the actual final integration head; packaging changes also require the documented fresh-wheel smoke.

Inspect representative pages at 320, 390, 768 and 1,440 px, keyboard-only, reduced motion, zoom and print. Verify formula signs, long titles, deep links, no-issue cases, search loading/failure and authentication return context. These are future implementation gates, not checks reported as run here.

Seek voluntary task-based feedback: locate a paper, explain the finding's boundary, reach the original claim, and return after opening contribution access. Record confusion and completion with sample size and task context. Later aggregate reading events may measure search-to-case navigation, evidence expansion and template access; define denominators and privacy first. Separate declared crawlers and suspected automation from interactive human-session estimates, disclose classification uncertainty, and never call server requests people. No traffic, savings or growth result is promised.

## 9. Selected guidance and tools

Used now: **site-architecture** for routes/context continuity; **interface-design** for Atlas and case components; **ux-heuristics** for source-based navigation/accessibility hypotheses; **elvia-maintenance** and case editorial guidance for scientific fidelity; **copywriting/content-strategy** for public introductions; **GitHub** for Issue #36; **Parallel** for primary design-source review. Later implementation: **impeccable** for the agreed homepage composition and responsive typography, **nature-figure/scientific-visualization** for source-bound diagrams, and **Playwright** for rendered reading/routing QA. **site-check** becomes relevant if an animated presentation is introduced. Figma can support a later collaborative design handoff, but no new design file or account is required for this plan. Existing source, bundled fonts/math renderer and preview workflow suffice; no new paid service or external publishing is needed.

[Dogstudio's Quanta case](https://dogstudio.co/cases/quanta-magazine/) supports continuity for demanding scientific reading; [MultiAdaptor's DeepMind case](https://www.multiadaptor.com/work/deepmind/) shows a reusable scientific visual language; [Pentagram's Isomorphic Labs case](https://www.pentagram.com/work/isomorphic-labs) connects an ambitious mission to a restrained identity. Borrow their principles, not their assets, prestige or claims of impact. [NN/g progressive disclosure](https://www.nngroup.com/articles/progressive-disclosure/) supports deferring secondary controls; ELVIA's qualifications and proof access remain primary. All four primary pages were returned by the connected source reader. Their relevance to ELVIA is a design inference, not evidence of measured conversion.
