# Reading and maintaining case notes

Each case uses one shared presentation:

1. Publication, assessment, independent-review status and paper title.
2. Contribution availability and one revision entry, followed by the article reference.
3. Two whole-note citation actions and one citation-formats/full-context disclosure.
4. Key findings, using existing concise problem summaries in display order.
5. Numbered problems with a native **Evidence and reasoning** disclosure containing
   **Problem statement**, **Proof** or **Verification**, and
   **Possible revision**.
6. A closed **Supporting record & provenance** disclosure with work status,
   contributor credit, current version and original claim/scope.
7. One full-width **Download report files (.zip)** link.

The overview has no contents navigation or repeated contribution panel. Problems
have no repeated citation or contribution controls. Each problem spans the same
desktop width as Key findings, whose lower separator is a thick black rule.
Source page and theorem/lemma/equation locators belong in the statement itself;
there is no standalone Sources block or redundant Statement subheading.
Method paragraphs remain in the proof or
verification argument. Possible revision uses the report's existing proposal;
an absent proposal is displayed as **Not available**.

No Issue Found and scope-clarification notes use bounded outcome summaries and
Review scope rather than artificial problems. A new contribution does not
require a new page layout; the renderer applies the same structure to validated
content. Complete results, limitations and repair history remain in the records,
full context and downloadable reports.

## Content and identity

Each collection's `case-notes.json` supplies structured narratives for its
records. Each entry names the record revision and canonical snapshot
hash. The builder verifies problem IDs, evidence references and correction
eligibility. New or unmatched revisions use recorded fields until their specific
narrative is prepared.

The optional `statement-presentations.json` supplies carefully edited original
claims, bound to the same record revision and to canonical record, report and
problem hashes. It identifies mathematical objects, parameter domains,
hypotheses, quantifiers and conclusions, including the exact local step if a
finding concerns a proof. Its basis records the retained claim/analysis/report
paragraphs used and, when needed, physical pages and the hash of the exact
reviewed article PDF. Never replace a source hypothesis with a counterexample's
special choice or a proposed repair. Same-revision source drift fails the build;
a new scientific revision does not inherit the old statement presentation.

The builder prepares one derived `statement` for the static and dynamic readers.
Without an override, it preserves the original claim and only supplements it
with explicitly identified original-source conditions. Ambiguous legacy
assumptions stay with the proof or verification; they can describe a witness.
The complete AI context includes both the displayed statement and the unchanged
original claim and argument. Original reports and reader ZIPs remain intact.

An optional `brief` array on a note or problem supplies presentation points:
at most three nonempty points and 80 words in total. These are concise summaries
of existing findings and their material boundaries, not new scientific decisions.
Short findings can be shown directly. Complete proof and verification paragraphs remain in the initial HTML's
reasoning disclosures, independently of their expanded state. Original result
paragraphs, case-wide limitations and evidence stances remain in the retained
records and full context.

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
`node scripts/check_review_notes.cjs studies/neurips2025/records`. The strict
collection format checks also render every curated statement's mathematics.
Check the
rendered article header, main arguments, supporting disclosure, download,
search/pagination, keyboard focus and narrow-screen reading. Preview builds use
loopback; production publication follows the checked release process.
