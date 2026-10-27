# Record formats 1.0.0, 1.1.0, 1.2.0 and 1.3.0

Authoritative records are UTF-8 JSON snapshots. The packaged
`src/elvia/schema/record.schema.json` defines every required field and enum.
Objects reject extra fields; use a new schema version for incompatible changes.
Version 1.2.0 supports the [reviewed collection](../studies/neurips2025/README.md)
It adds `moderate` concern severity, `needs_evidence` inspection outcome, and a
nullable `audit.retrieved_at` when the original download time was not recorded.
The source note explains missing provenance; file modification times are not
substituted. `pdf_sha256` identifies the exact inspected retained PDF. If that
copy was compressed, its version/note must say that it is not established as
publisher-identical bytes. Older versions retain their original constraints.
All strings described as text must contain a non-whitespace character. Lists
remain explicit even when empty. Times are RFC 3339 timestamps with time zones.

The current assessment rubric merges Moderate into Minor and limits Major
to core-claim damage or a substantial invalid derivation. The schema still accepts
historical Moderate snapshots. Reassessments use new revision numbers and new
artifact paths, preserving prior bytes and source identity; latest views bind to
the new canonical record hash. This is an impact/editorial revision, not a final
scientific adjudication.

The initial published report is revision 1. Future scientific updates append
new revisions and preserve their published predecessors.

| Field | Meaning |
| --- | --- |
| `schema_version` | `1.0.0`, `1.1.0`, `1.2.0` or `1.3.0`; existing snapshots stay unchanged and valid. |
| `case_id` | Portable lowercase identifier, 1–80 letters/digits/underscores/hyphens; starts with a letter or digit. |
| `revision` | Positive integer snapshot revision, starting at 1. Python floats such as `1.0` are rejected. |
| `previous_revision` | `null` at revision 1; otherwise integer `revision - 1`. Python floats are rejected. |
| `case_type` | `synthetic_demo`, `known_erratum`, or `prospective_audit`. Scientific collections use prospective_audit as a classification, not a preregistration claim. |
| `created_at` | Actual snapshot creation time. |
| `source` | Source identity, local artifact, and actual scope reviewed. |
| `source_update` | Optional in 1.3.0: explicit same-work source refresh linked to the preceding canonical record hash, with check time, reason and correspondence. |
| `proposition` | Exact claim and its boundaries. |
| `concern` | Finding under consideration, including its origin and impact. |
| `evidence` | Both supporting and rebutting evidence entries, without discarding adverse results. |
| `runs` | Actual tool executions; empty means no execution recorded. |
| `human_reviews` | Human declarations; empty means no human review recorded. |
| `adjudication` | Issue decision, rationale, and history. |
| `repair` | Proposed correction, separate verification, and separate adoption status. |
| `publication` | Draft, synthetic demonstration, or 1.1.0 preliminary AI publication; never a scientific signature. |
| `audit` | Optional in 1.1.0, required for preliminary AI publication; exactly the ten source/inspection fields below. Forbidden in 1.0.0. |

## Source and proposition

`source.title` and `source.version` identify the reviewed source. `doi` and
`arxiv_id` are strings when known, otherwise JSON `null`. Never fabricate them.
`identifier_note` explains missing identifiers or their provenance.
`source.artifact` is the local source reference defined below. `review_scope`
states what was actually examined, including any limits such as abstract-only
access. Source identity (title, version, DOI, arXiv identifier and artifact) and
case type cannot change along a revision chain. Expanded review scope may change.
A different source version requires a new case under formats 1.0.0–1.2.0.
Format 1.3.0 permits an explicit same-work source refresh with explicit provenance: `source_update` records the
preceding canonical JSON SHA-256, timezone-bearing `checked_at`, substantive
`reason` and `correspondence` declaration. The hash uses sorted keys, compact
separators and ASCII JSON escaping. A refresh must follow a predecessor, retain
case type and venue/year, start pending with no human reviews, unrequested
adoption and no inherited verified repair. Source notes and evidence use new
paths; predecessor bytes remain unchanged. Without this explicit transition,
source-identity changes are still rejected. Hashes and declarations do not prove
that two sources are the same scientific work or that the recheck is correct.

In the active collection, `source.artifact` points to an original source note, not
the upstream PDF. `audit` has exactly these required fields (no extra keys):

| Field | Constraint and interpretation |
| --- | --- |
| `venue` | Nonempty text; use the source venue name and retain historical names in source notes. |
| `year` | Integer in 1600–9999, not a float or boolean. Venue year can differ from the reviewed author's revision date. |
| `authors` | Nonempty unique list of nonempty text. |
| `landing_url`, `pdf_url` | HTTPS URLs with hostnames, valid ports if supplied, no userinfo, whitespace, controls or backslashes. |
| `pdf_sha256` | Lowercase 64-hex hash of the actual downloaded upstream PDF; distinct from source.artifact.sha256. |
| `retrieved_at` | Actual timezone-bearing RFC 3339 download timestamp; unknown historical retrieval may be null in 1.2.0. |
| `outcome` | no_issue_found, scope_clarification, candidate_issue or known_issue_reproduced; 1.2.0 also supports needs_evidence. An inspection label, not adjudication. |
| `summary` | Substantive bounded outcome description. |
| `limitations` | Nonempty unique text list retaining scope and evidentiary limits. |

The first seven fields (venue through retrieved_at, counting the two URLs
separately) are immutable once audit metadata appears. Neither removing audit
nor downgrading the schema can erase that identity. Outcome, summary, limitations
and reviewed scope may evolve in new revisions. Software checks declarations and
local artifact hashes; it does not independently fetch/authenticate the upstream PDF.

`proposition.claim`, `domain`, and `location` are text. `assumptions` is an explicit
list of text assumptions; `dependencies` lists cited prerequisite claims or
identifiers. These references do not imply those dependencies were verified.

## Concern and evidence

`concern.description` describes the issue. `type` is `counterexample`, `proof_gap`,
`computation`, `data`, `interpretation`, or `other`. `severity` is `minor`, `major`,
or `critical`, with `moderate` retained for historical 1.2.0 snapshots. New impact
reassessments use Major or Minor. `impact` is `local`, `main_result`, or `unknown`. `origin` is `ai`,
`human`, or `software`. An AI finding's revision 1 must be `pending`, including
when human declarations are already present. Decisions follow in later immutable
revisions after the pending first snapshot is preserved.

The legacy schema requires severity and impact even for no-issue and clarification
records. For those outcomes, `minor`/`local` are compatibility classifications
of the bounded inspection, not a paper-error severity rating. Read audit.outcome,
the concern description and scientific status together; do not advertise those
required legacy fields as established errors.

Each evidence entry has a unique text `id`, `stance` (`support` or `rebuttal`),
text `description`, text `method`, and one `artifact`. Keep exact computation,
finite diagnostic, source inspection, and scientific conclusions distinct.

Every artifact reference has exactly this shape:

```json
{"path": "evidence/counterexample.txt", "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"}
```

This hash illustrates the format only. Real records contain the actual lowercase
64-hex SHA-256 of file bytes. Paths are portable, forward-slash, dataset-relative
paths. Absolute paths, Windows drive paths, backslashes and `..` traversal are
rejected. The dataset root is the parent of the `records` directory. Files must
exist and resolve within that root; symlinks escaping it are rejected. These
rules cover source, evidence, and run output artifacts alike.

## Runs

Each run records unique `id`, actual `tool` and `tool_version`, nullable `model`,
and a required `model_note` explaining model identity or why no model was used.
`config_version` identifies the actual prompt/configuration version (for example,
a versioned local script identifier). `started_at` and `ended_at` are actual
execution times; the end cannot precede the start. `output_artifacts` contains at
least one raw output reference. `cost_usd` is a nonnegative finite number or
`null` when unknown; describe unknown costs in the run context (`model_note`).
Zero means known zero cost. An absent model or unknown cost is not an invented
model execution. A Python run's
null model does not erase interactive AI assistance in analysis/code/drafting;
explain that separately in model_note and source notes. Execution artifacts record real commands, interpreter, timestamps, exit status
and outputs without credentials or fabricated model run IDs.

## Human review and decisions

Every human review has `reviewer_id`, `role` (`domain_reviewer`, `reviewer`, or
`author`), boolean `independent` and `domain_review` declarations, `decision`
(`pending`, `confirmed`, `rejected`, `unresolved`), substantive `rationale`, and
`evidence_refs` listing existing evidence IDs. Reviewer identities must be
distinct after trimming and case folding. Synthetic test identities do not
represent real reviewers.

`adjudication.status` uses the same four decisions; `rationale` explains it.
`history` is an explicit list of objects with `at`, `status`, and `rationale`.
Confirmed or rejected decisions require at least one agreeing non-author human
review referencing evidence. Confirmation of a major/critical issue or a
main-result issue requires two distinct agreeing `domain_reviewer` identities,
both declaring `independent: true` and `domain_review: true`.

Software checks the presence and consistency of declarations. It cannot verify
reviewer identity, real independence, qualifications, expertise, or correctness
of the scientific judgment. An exact computation alone does not become human
confirmation. Adjudication remains separate from repair and adoption.

## Repair and publication

`repair.content` is nullable proposed correction text. `verification_status` is
`not_proposed`, `pending`, `verified`, `rejected`, or `unresolved`. A proposed
repair requires content; a verified repair additionally requires nonempty
`verification_refs` naming existing evidence IDs. `changed_assumptions` explicitly
lists changed assumptions; `changed_conclusion` is nullable text. These fields
preserve restricted-domain repairs without implying the original claim holds.

`adoption_status` is `not_requested`, `pending`, `adopted`, `declined`, or `unknown`.
Adoption requires repair content, but does not imply verification; verification
does not imply author adoption. Null repair content/conclusion means no content
or changed conclusion recorded, not successful verification. An adoption event is recorded only when it actually occurs.

`publication.status` is `draft`, `synthetic_demo`, or (only with 1.1.0)
`preliminary_ai`; `note` explains the context. Preliminary AI publication requires
complete audit metadata, a non-synthetic case type and pending/unresolved
adjudication. It does not supply scientific signing or human confirmation.
This state describes eligibility for a preliminary view, not actual access.
Access changes do not rewrite scientific snapshots.
Clarification records use null repair content/conclusion, empty changed assumptions
and verification references, and verification_status=not_proposed. A candidate
repair remains pending and author adoption stays not_requested unless actually requested.

`elvia site build --records DATASET/records --output NEW_DIRECTORY` validates the
complete dataset before building. It takes a records directory, selects latest
preliminary non-synthetic snapshots, and publishes complete predecessor chains.
A public latest snapshot with a non-public ancestor fails closed. A latest draft
hides that case. The target must be new; validation/export failure leaves it absent.
Portable per-case trees retain records, referenced artifacts, readable views
and hash manifests. The public website's reader ZIPs separately contain the
reviewed article PDF, current report PDF, explicitly approved supporting evidence
and approved revision files. A snapshot-bound publication sidecar maps cited
evidence to actual downloadable files and checks their bytes before packaging;
this does not change the authoritative record schema. Site building never
executes artifact code.

## Storage and verification boundaries

Canonical snapshots are `records/<case_id>.r<revision>.json`. Other JSON artifacts
belong outside `records`. Directory loads reject noncanonical `.json` candidates,
invalid records and empty inputs. They return every revision in case/revision
order. A single-file load returns that snapshot while also checking its complete
predecessor chain in the same directory. All loads check artifacts and hashes.
Relative load/save paths are anchored to the current working directory before
deriving the dataset root; returned snapshot paths are absolute. From inside
`records`, `elvia validate .` and `elvia validate <case_id>.r1.json` use its parent
as the dataset root, as do indexing and exporting those relative inputs. Anchoring
does not resolve directory links before the containment check.

`validate_record(record, root=None)` returns located error messages. Without
`root`, it checks schema, workflow and path syntax only. Supply the dataset root
to also check real files, containment and hashes. Malformed structures can stop
dependent semantic checks; independent schema errors are still reported together.

`save_record(record, records_dir)` validates before writing. Revisions are
immutable snapshots, never in-place edits. A complete flushed temporary file is
published with an exclusive hard link, then the temporary name is removed.
An existing target is never replaced, including during concurrent writes. A
filesystem without hard-link support fails with `OSError`; there is no partial
write fallback. Atomic publication is distinct from power-loss durability of a
directory entry. This local workflow assumes artifacts and directories are not
being maliciously replaced during validation/publication. It does not sandbox
external code, authenticate declarations, or establish a scientific theorem.
Both save and load reject a pre-existing records-directory symlink or junction
whose resolved location escapes its dataset root, before reading or writing
snapshots through that directory.
