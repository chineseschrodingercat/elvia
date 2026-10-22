# ELVIA contributor instructions

## Scope and authority

- Read README.md, docs/STATUS.md and the relevant GitHub Issue before changes.
- GitHub Issues own work status; docs/STATUS.md summarizes evidence and next work.
- The 2026-10-22 user instruction authorizes the public website at
  elvia-atlas.org, hosting on the existing PC, boot-time recovery and a clean
  public source repository. No additional paid hosting was authorized.
- The active Atlas contains the supplied 300-paper collection. Keep scientific
  decisions pending unless the formal protocol's independent review is supplied.
- The public repository starts from the maintained source and current collection.
  Earlier development history remains in the private internal archive; do not
  import its branches, tags or Issues into this repository. Current accounts,
  operational state and the 300 scientific records remain protected.
  No author contact, recruitment, model spending or author-code execution is authorized.
- Keep private proposal/starter files, conversation logs, credentials and local
  tooling out of Git and exports. Never stage all files without inspecting them.
- Minhao Liu / @chineseschrodingercat is the sole maintainer. Do not invent staff,
  reviewers, credentials, paper identifiers, releases or scientific endorsement.

## Scientific and storage invariants

- Versioned JSON under records/ is authoritative; SQLite and views are derived.
- Preserve immutable revisions, full predecessors, source identity and hashes.
- AI findings begin pending. Software checks declarations, not human authenticity,
  independence, expertise or scientific correctness.
- Separate issue decision, repair verification and adoption. Preserve rebuttal,
  failed attempts, scope limits and unresolved results.
- Synthetic data stays labeled and excluded from real research statistics.
- Preliminary publication is not scientific confirmation. Clarifications are not
  paper repairs; keep independent-human requirements for final decisions.
- Validate before mutations; never overwrite records, unrelated files or outputs.
- Keep portable dataset-relative paths within the dataset root after resolution.
- Read docs/record-format.md and docs/protocol.md before changing workflow/schema.

## Implementation and verification

- Use Python >=3.12, uv and committed uv.lock; no parallel dependency workflow.
- Start behavior changes with a meaningful failing test. Prose/config edits need
  relevant checks, not artificial tests. Avoid unrelated refactors.
- Run `uv sync --locked`, `uv run --no-sync ruff check .`,
  `uv run --no-sync ruff format --check .`, `uv run --no-sync pytest -q`,
  `uv run --no-sync elvia validate examples/synthetic_demo/records`, and `uv build`.
- Validate `studies/neurips2025/records` and run
  `node scripts/check_review_notes.cjs studies/neurips2025/records`.
- For website changes run the isolated backend suite, current Node UI tests and
  public-ingress/storage tests; never send real mail or mutate live state in tests.
- Packaging changes require the fresh installed-wheel offline smoke in
  docs/maintainer-guide.md; check bundled schema and source-distribution fixtures.
- Record actual commands/results, limitations and failed attempts. Never report
  unrun Actions, pending reviews or a prepared PR as completed integration.
- Project documentation, Issues, PRs and interface text use English.
- See NOTICE.md for Apache-2.0 and CC BY 4.0 path coverage; retain third-party terms.
- Use focused commits; inspect staged diff and history for private inputs.
- Keep the five existing CI check names and require all green at the final merge
  head. Verify actual repository settings before claiming server enforcement.
  Do not purchase an upgrade.
- Do not force-push, delete unrelated history or silently rewrite evidence.

## Working process

- Follow explicit user authorization; do not add repeated approval gates.
- Ask only when ambiguity affects scientific correctness or authority, while
  continuing unaffected work. Keep durable decisions in docs/decisions/.
- Engineering AI review is not scientific peer review. Human-review declarations
  in tests are synthetic fixtures only.
- SECURITY.md covers private software vulnerabilities. No confidential scientific
  intake or independent real-case appeal panel currently exists.
