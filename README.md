# ELVIA

**Expert-Led Verification of Inferences and Arguments**

ELVIA connects a research claim to the source, assumptions, analysis and evidence
needed to inspect it. The website brings together a searchable evidence Atlas
and a contribution workspace for submissions, review assignments and amendments.

The current Atlas contains **300 NeurIPS 2025 papers**, with detailed arguments,
MLA-style references, DOI links and downloadable PDF evidence. Its preliminary assessments are
**104 Major, 177 Minor, 3 Needs Evidence and 16 No Issue Found**. These describe
bounded findings in the inspected material. Independent scientific review remains
pending; they are not whole-paper verdicts or estimates of venue error rates.

**Website:** [elvia-atlas.org](https://elvia-atlas.org/) is publicly accessible.
**Source:** [chineseschrodingercat/elvia](https://github.com/chineseschrodingercat/elvia)
is the public project repository.

The site runs on the maintainer's PC and is unavailable while it is off, asleep
or disconnected. Windows starts the service automatically after boot, without
requiring an interactive login.

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
node scripts/check_review_notes.cjs studies/neurips2025/records
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
