# ICML publication and research fields

Date: 25 October 2026 (America/Chicago)

Issue: https://github.com/chineseschrodingercat/elvia/issues/18

The maintainer explicitly authorized publication of the four completed ICML
batches B001–B004, comprising report numbers 0001–0400. This task checks format,
source identity, titles, fields and public presentation without repeating the
scientific assessment. Existing AI findings remain pending independent human
review. No author contact, author-code execution or paid service is involved.

## Preserved inputs and public copies

The original archive remains outside Git. A publication manifest records the
exact selected paper IDs, source/report hashes, titles and source topics.
Source provenance binds each inspected PDF to its retained bytes. The original
report, findings and coverage remain the scientific input; the importer does not
infer a new severity from unresolved subitems or hypothetical impact wording.

Public copies remove host paths and internal workflow identifiers. A constrained
Pandoc reader parses report TeX as data, without TeX compilation, filters or
resource fetching. Known font/URL-layout template commands are omitted from a
temporary parsing copy; active input/execution commands in report content remain
rejected. Unknown nodes and parser warnings fail. A regression preserves leading
table digits that Pandoc 2.12 otherwise loses in a styled tabularx column.

Complete report text remains in the initial case HTML and complete Copy for AI.
Code is displayed literally, outside mathematical rendering. Document equation
labels remain visible as named references; mathematical operators are preserved.
Public PDFs are separately typeset from the same public transcription. Retained
original report hashes distinguish this layout copy from the archive original.

## Multiple collections

The builder accepts a sequence of record directories. It validates every dataset
and complete revision chain separately, rejects duplicate cross-collection case
IDs and binds each catalog and export to its own dataset root. The production
builder selects NeurIPS 2025 and ICML 2025 explicitly. Reader libraries contain
only explicitly mapped publication files; private uploads are never discovered.

ICML citations use real PMLR URLs where no DOI was supplied. Missing DOI values
remain null. Publisher identity, software checks and report publication are
separate from scientific confirmation.

## Research fields

The maintainer approved one principal field per paper: Mathematics, Biological
science, Computer science, Chemistry or Others. General ML/algorithms/ML theory
use Computer science. Direct biological objects, chemical systems and principal
mathematical problems use their corresponding fields. Other principal subjects
use Others; a conference name alone does not determine a field.

`research-fields.json` catalogs bind each assignment and short rationale to a
record revision and canonical hash. Same-revision drift fails. New or missing
assignments default to Others. Changing discovery classification does not rewrite
a scientific snapshot. Field selection composes with existing filters, resets
pagination and persists in shareable URLs and contribution context.

## Release verification

Run the existing project checks, both collection validators, the NeurIPS curated
prose/math checker and the ICML retained-format checker. The latter checks all
explicit mathematical expressions without imposing a new editorial/scientific
review on the retained report prose. Build the public library, inspect PDF layout,
verify all 700 cases and ZIP identities, preserve the existing 300 snapshots and
600 PDF members, and load the fixed-file Atlas manifest through the actual mount.

Final CI, stopped-writer backup/restore rehearsal, operational preservation and
canonical public acceptance are recorded in Issue #18. Prepared outputs and local
checks alone do not establish deployment.
