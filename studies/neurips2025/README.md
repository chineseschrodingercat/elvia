# NeurIPS 2025 collection

The active Atlas contains 300 papers with claim-focused, AI-assisted analyses.
Each note records the source version, passage examined, working, counterevidence
and scope. Independent scientific decisions remain pending.

| Current assessment | Papers |
| --- | ---: |
| Major | 104 |
| Minor | 177 |
| Needs Evidence | 3 |
| No Issue Found | 16 |

Major requires demonstrated central-claim damage or a substantial invalid
derivation. Minor covers local defects without that established impact.
Unsettled subitems remain visible without increasing the highest supported
assessment. The collection is not a representative sample or a venue error rate.

The 16 No Issue Found assessments comprise twelve no-issue-in-scope outcomes and
four scope clarifications. The remaining inspection outcomes are 279 candidate
issues, two attributed known-issue reproductions and three needs-evidence records.
All 300 initial scientific decisions are pending with empty human-review lists.

## Contents

| Path | Purpose |
| --- | --- |
| `records/` | Versioned scientific snapshots; the initial report is revision 1 |
| `source/` | Source identity and inspection notes |
| `evidence/<case>/review.md` | Curated claim, reasoning and bounded finding |
| `evidence/<case>/verification.json` | Per-problem assessments and source checks |
| `evidence/<case>/report.tex` | Maintained report source |
| `case-notes.json` | Snapshot-bound narratives for 284 substantive or unsettled notes |
| `reader-catalog.json` | Verified references, DOI links and contributor credit |

Source inspection covers the implicated passages and relevant retained released
materials. Historical execution results are attributed as historical; building
this collection does not run author code, train models or reproduce experiments.
Corrected older defects are distinguished from current findings. Unknown original
retrieval times remain null.

The website provides simple PDF reader bundles separately from the source tree.
Generated reports and retained article PDFs are outside Git. The article PDF
must match the inspected source identity; all publication files are selected
explicitly. Full registered evidence remains in this dataset.

```console
uv run --no-sync elvia validate studies/neurips2025/records
node scripts/check_review_notes.cjs studies/neurips2025/records
uv run --no-sync python -m website.build --output atlas-output
```

Use a fresh output path. Source previews do not include PDF reader downloads
unless a verified public reader library is supplied. Future scientific changes
append immutable revisions. See [publication workflow](../../docs/publication-workflow.md).

Original ELVIA scientific content: Minhao Liu, CC BY 4.0. Attribute ELVIA,
link [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) and indicate changes.
Third-party papers retain their own copyright and source terms. See [NOTICE](../../NOTICE.md).
