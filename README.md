# ELVIA

**Expert-Led Verification of Inferences and Arguments**

ELVIA is an open **research verification** project for checking scientific claims,
contributing **paper corrections and clarifications**, and documenting evidence
for **research reproducibility**. Its post-publication peer review workflow links
each question to the source, assumptions, analysis and counterevidence needed to
inspect it. Independent scientific decisions remain pending until the protocol's
review requirements are met.

**Start with one claim you understand well:**

- **Examine an existing analysis:** [search the public Atlas](https://elvia-atlas.org/atlas/),
  open a note and choose **Contribute to this finding**. The selected paper follows
  you through registration and into a draft.
- **Contribute a correction, clarification or verification:**
  [follow the contributor guide](https://elvia-atlas.org/participate.html).
  Supporting the original reasoning and documenting an unresolved question are
  useful contributions too. A verified institutional account can submit its own
  analysis; reviewing other contributions requires a separate application.
- **Improve the software or documentation:** read [CONTRIBUTING.md](CONTRIBUTING.md)
  and the [current Issues](https://github.com/chineseschrodingercat/elvia/issues).

You can read the Atlas without an account. The project supports constructive
paper errata and evidence-based review; it is not a catalogue of confirmed errors.

The current Atlas contains **700 papers: 400 ICML 2025 and 300 NeurIPS 2025**, with
detailed arguments, publisher references and downloadable reports and supporting
verification files. Search
supports five research fields as well as venue and assessment. Preliminary
assessments are **366 Major, 278 Minor, 14 Needs Evidence and 42 No Issue Found**. These describe
bounded findings in the inspected material. Independent scientific review remains
pending; they are not whole-paper verdicts or estimates of venue error rates.

**Website:** [elvia-atlas.org](https://elvia-atlas.org/) is publicly accessible.
**Source:** [chineseschrodingercat/elvia](https://github.com/chineseschrodingercat/elvia)
is the public project repository.

[Current collection](studies/neurips2025/README.md) ·
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
| `studies/neurips2025/` | The active 300-paper collection and original evidence notes |
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

Run the project checks:

```console
uv sync --locked
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
uv run --no-sync pytest -q
uv run --no-sync elvia validate examples/synthetic_demo/records
uv run --no-sync elvia validate studies/neurips2025/records
uv run --no-sync elvia validate studies/icml2025/records
node scripts/check_review_notes.cjs studies/neurips2025/records
node scripts/check_icml_format.cjs studies/icml2025
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
