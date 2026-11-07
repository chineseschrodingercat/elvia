# ELVIA

**Open Infrastructure for Scientific Verification**

**Build the future on evidence.**

ELVIA is building open infrastructure to examine and strengthen the scientific
foundations that future research depends on.

Ambitious research programs inherit a network of published results. A new
direction may depend on a proof step, an experimental claim, or assumptions
carried from one setting into another. Making those foundations easier to
inspect helps researchers decide what to cite, extend, and put into practice.

ELVIA connects specific scientific claims to their source passages, supporting
arguments, counterevidence, and stated limits. AI-assisted analysis helps examine
the reasoning. Versioned records preserve what was checked and how an
interpretation changes. A protocol for independent review governs scientific
decisions.

The long-term ambition is a global, open resource through which researchers can
scrutinize and improve the arguments that future discoveries will build on.
Today's **ELVIA Atlas** contains preliminary analyses of **1,214 papers** across
mathematics and machine learning. **Independent scientific review remains pending.**

[**Explore the Atlas**](https://elvia-atlas.org/atlas/) ·
[**Contribute an analysis**](https://elvia-atlas.org/participate.html) ·
[**Read the methodology**](https://elvia-atlas.org/project.html)

## Why a single claim matters

A missing hypothesis can change where a theorem applies. An invalid comparison
can interrupt a proof. A discrepancy between a stated method and an implementation
can change what a researcher needs to check before reusing it. A focused analysis
can establish exactly which step fails while preserving conclusions that survive.

The immediate work is technical: inspect the original conditions, construct a
decisive counterexample or source-grounded check, and explain its consequences.
A proposed repair is useful when available; a rigorous error finding can stand
on its own. The same process should preserve evidence that supports the original
argument or leaves a question unresolved.

## See the work in two examples

- **A geometric comparison that loses a sign.** The preliminary analysis of
  [*Lower bounds for incidences*](https://elvia-atlas.org/atlas/cases/math2025-0071.html)
  uses two parallel lines to examine a specific comparison in an incidence proof.
  It discusses a local alternative and the remaining checks; it does not establish
  that the paper's final incidence bounds fail.
- **Repairing an argument while retaining its bound.** The preliminary analysis of
  [*Private Hyperparameter Tuning with Ex-Post Guarantee*](https://elvia-atlas.org/atlas/cases/neurips2025-0029-private-hyperparameter-tuning-with-ex-post-guarantee.html)
  gives an exact example exceeding an intermediate bound while remaining below
  the lemma's final bound. It proposes an alternative argument with the same
  constants. Independent review of the analysis remains pending.

[Follow four worked reading paths](https://elvia-atlas.org/exemplary-cases.html)
for more examples of source checks, calculations, and bounded conclusions.

## Start with a claim your research depends on

- **Examine an existing analysis:** [search the Atlas](https://elvia-atlas.org/atlas/),
  open a note and choose **Submit a revision** in its contribution-availability
  panel. The selected paper follows you through registration and into a draft.
- **Contribute a correction, clarification or verification:**
  [follow the contributor guide](https://elvia-atlas.org/participate.html).
  Supporting the original reasoning and documenting an unresolved question are
  useful contributions too. A verified institutional account can submit its own
  analysis; reviewing other contributions requires a separate application.
- **Improve the software or documentation:** read [CONTRIBUTING.md](CONTRIBUTING.md)
  and the [current Issues](https://github.com/chineseschrodingercat/elvia/issues).

You can read the Atlas without an account. For consistent public introductions
and selected-case communication, use the [public messaging guide](docs/outreach.md).

## Current collection and scientific status

The Atlas contains **514 Math 2025, 400 ICML 2025 and 300 NeurIPS 2025 papers**,
with detailed arguments, publisher references and downloadable reports and
supporting verification files. Search supports five research fields as well as
venue and assessment.

Preliminary assessments are **735 Major, 371 Minor, 18 Needs Evidence and
90 No Issue Found**. These describe bounded findings in the inspected material.
They are not whole-paper verdicts or estimates of venue error rates. Editorial
publication does not establish scientific confirmation, repair verification or
author adoption. Those states remain separate under the
[scientific protocol](docs/protocol.md).

[Current collection](docs/STATUS.md#current-collection) ·
[Website operations](website/README.md) ·
[Deployment status](docs/STATUS.md) ·
[Publishing contributions](docs/publication-workflow.md)

## Use the website

Readers can browse the Atlas and inspect the claim, decisive reasoning, scope,
counterevidence and current record. The contribution workspace supports verified
institutional email accounts, contribution applications, submissions, assignments,
attachments and amendment requests. Administrators manage contributors; the
maintainer also manages administrators. Explicitly linked staff accounts can use
Google sign-in. Email recovery, request limits and duplicate-submit protection
are implemented in the current application.

Each paper analysis has a readable, shareable HTML page. Researchers can start
with the [contributor guide](https://elvia-atlas.org/participate.html) or the
[research review platform guide](https://elvia-atlas.org/research-review-platforms.html).
Public pages are listed in the [sitemap](https://elvia-atlas.org/sitemap.xml);
account and recovery pages remain excluded from indexing.

Editorial acceptance, scientific adjudication, repair verification and author
adoption are separate. A website acceptance never automatically confirms a
scientific claim. Only a reviewed offline promotion may create a formal versioned
record; the application has no GitHub publishing integration or configured GitHub token.

## Project layout

| Path | Purpose |
| --- | --- |
| `website/` | Current website source, authentication, contribution workflow and operations |
| `studies/neurips2025/` | 300 NeurIPS 2025 records and their evidence notes |
| `studies/icml2025/` | 400 ICML 2025 records and their retained reports |
| `studies/math2025/` | 514 integrity-accepted Math 2025 records and public transcriptions |
| `src/elvia/` | Record validation, immutable revisions, exports and Atlas builder |
| `tests/` | Regression tests for current supported behavior |
| `docs/` | Protocol, publishing workflow and maintenance instructions |

Versioned JSON snapshots are authoritative scientific records. The website's
private SQLite database holds operational accounts and contributions; indexes
and website builds are derived. Credentials, live databases, private attachments,
backups and machine-specific runtime state are excluded from Git and exports.

## Local development

Use Python 3.12 or newer and [uv](https://docs.astral.sh/uv/):

```console
git clone https://github.com/chineseschrodingercat/elvia.git
cd elvia
uv sync --locked
uv run --no-sync elvia validate studies/neurips2025/records
uv run --no-sync python -m website.build --output atlas-output
uv run --no-sync python -m http.server 8000 --bind 127.0.0.1 --directory atlas-output
```

Open [the local Atlas](http://127.0.0.1:8000/). Use a fresh output directory for
each build. This command is a local preview; production deployment has its own
server and persistence requirements in [website operations](website/README.md).

## Update and maintain

The site runs on the maintainer's PC and is unavailable while it is off, asleep
or disconnected. Windows starts the service automatically after boot, without
requiring an interactive login.

Ordinary interface and feature changes follow a branch, regression checks and a
versioned deployment. Keep operational data outside code releases. A compatible
code release can be rolled back independently; a database change needs a versioned
migration, a verified backup and a restore test. Existing scientific records are
corrected through new immutable revisions.

The [website design plan](docs/website-design-plan.md) describes the next
presentation work; its proposed routes and layouts are not yet deployed.

Run the project checks:

```console
uv sync --locked
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
uv run --no-sync pytest -q
uv run --no-sync elvia validate examples/synthetic_demo/records
uv run --no-sync elvia validate studies/neurips2025/records
uv run --no-sync elvia validate studies/icml2025/records
uv run --no-sync elvia validate studies/math2025/records
node scripts/check_review_notes.cjs studies/neurips2025/records
node scripts/check_icml_format.cjs studies/icml2025
node scripts/check_icml_format.cjs studies/math2025
node --test tests/*.test.cjs website/preview/tests/*.test.*
uv run --no-sync python website/preview/tests/run_private_auth_backend.py local all
uv build
```

The test suite uses synthetic fixtures, separate from the research collection.
Production reader downloads use a verified PDF library outside Git; see
[reader bundles](docs/reader-bundles.md).

Minhao Liu ([@chineseschrodingercat](https://github.com/chineseschrodingercat)) is
the founder and sole maintainer. Read [contributing](CONTRIBUTING.md),
[governance](GOVERNANCE.md), [the protocol](docs/protocol.md) and
[license coverage](NOTICE.md). No independent scientific panel or confidential
scientific intake operation is represented as established.
