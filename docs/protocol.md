# Scientific workflow protocol

ELVIA records a specific claim, the evidence examined and the scope of the finding.
The current collection contains 300 NeurIPS 2025 papers. Its AI-assisted analyses
have pending independent scientific decisions. Impact labels describe the
inspected material; they are not whole-paper verdicts or venue error rates.

## Inspect and document

1. Identify the exact paper version, source location, proposition, domain,
   assumptions and dependencies. Record actual review scope and source-file
   identity. Unknown identifiers or retrieval times remain unknown.
2. Inspect the implicated current source and relevant released resources. Keep
   same-work correspondence explicit when reviewing a new source version.
   Defects already corrected in the current source remain historical.
3. Record support and counterevidence. Distinguish exact arguments, finite
   diagnostics, source inspection and unresolved hypotheses. Preserve failed
   interpretations and adverse controls.
4. Retain applicable proposed corrections with their assumptions and limits.
   A clarification of an existing condition is not a paper repair.

Inspection outcomes are `candidate_issue`, `known_issue_reproduced`,
`scope_clarification`, `no_issue_found` and `needs_evidence`. No-issue findings
apply only to the inspected scope. Known findings retain attribution.
AI assistance is described accurately; a local calculation is not an invented
model API run or independent human review.

## Assess and review

**Major** requires demonstrated damage to a central claim or a substantial
invalid derivation. **Minor** covers local defects without that demonstrated
central impact. The highest supported impact determines the case label;
unsettled subitems do not inflate it. **Needs Evidence** and **No Issue Found**
remain distinct outcomes. Historical schema values remain readable.

An initial AI-origin finding starts `pending`. A confirmed or rejected decision
requires a substantive agreeing non-author human review with evidence references.
Confirmation of a major/critical or main-result issue requires two distinct
agreeing domain reviewers declaring independent domain review. The maintainer
checks identity, expertise, conflicts and substantive evidence; software checks
the declarations' consistency.

Adjudication can be `pending`, `confirmed`, `rejected` or `unresolved`. Repair
verification and author adoption have their own recorded states and evidence.
Verification does not establish adoption, and adoption does not establish
verification. Use `not_requested` when no adoption request was made.

## Publish and revise

The initial published report is version 1. Accepted changes create version 2,
then version 3, retaining published predecessors. Citation or layout updates
alone do not re-adjudicate a finding. Source refreshes use explicit schema 1.3.0
transitions; earlier source identities remain intact.

The maintainer reviews contributions before they enter the formal dataset.
Editorial acceptance is followed by a checked publication step; it does not
write to Git or automatically confirm a finding. Use the
[publication workflow](publication-workflow.md) to keep reports, notes, credits,
references and downloads aligned.

Reader bundles contain the exact reviewed article PDF, the current report PDF
and explicitly approved published revision submissions. Original articles retain
their authors' copyright and source terms. Private uploads, internal logs and
operational state never enter a reader bundle by directory discovery. Full
scientific records and provenance remain in the versioned dataset.
