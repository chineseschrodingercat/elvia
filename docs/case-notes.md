# Reading and maintaining case notes

Each case uses one shared presentation:

1. Publication, assessment and paper title.
2. An MLA-style article reference with a verified DOI.
3. Numbered problems: source claim and location, conditions, worked analysis,
   finding and scope, and an applicable proposed correction.
4. A closed **Supporting record & provenance** disclosure with work status,
   contributor credit, current version, original claim/scope and complete
   supporting evidence and counterevidence.
5. One prominent reader ZIP download.

No Issue Found and scope-clarification notes use brief outcome-aware summaries.
An absent correction is omitted. A new contribution does not require a new page
layout; the renderer applies the same structure to its validated content.

## Content and identity

`studies/neurips2025/case-notes.json` supplies structured narratives for the
current collection. Each entry names the record revision and canonical snapshot
hash. The builder verifies problem IDs, evidence references and correction
eligibility. New or unmatched revisions use recorded fields until their specific
narrative is prepared.

`reader-catalog.json` holds verified publication metadata and contributor credit,
bound to the same snapshot. The citation uses MLA ninth-edition conventions:
inverted first author, et al. for three or more authors, quoted article title,
italicized container, volume, year, pages and DOI. Metadata comes from official
proceedings pages/BibTeX. Where a proceedings author entry is incomplete or
duplicated, the retained paper's author line is the recorded correction source.

Scientific record hashes, source versions and full evidence remain available in
the dataset. They are not repeated as technical fields in the reading interface.
The article PDF in a download is the exact reviewed version; its version can
differ from the final proceedings reference.

## Review and publication

Read the contribution and source passages before editing the structured note.
Check equations, quantifiers, source locators, attribution and impact. Preserve
counterevidence and unresolved findings. Use a new scientific revision for
substantive changes; presentation alone does not re-adjudicate a finding.

See [publication workflow](publication-workflow.md) for the maintainer process and
[reader bundles](reader-bundles.md) for current reports and approved attachments.

## Verification

Run the Python suite, Node UI tests and
`node scripts/check_review_notes.cjs studies/neurips2025/records`. Check the
rendered article header, main arguments, supporting disclosure, download,
search/pagination, keyboard focus and narrow-screen reading. Preview builds use
loopback; production publication follows the checked release process.
