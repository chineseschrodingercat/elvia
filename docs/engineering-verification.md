# Engineering verification

Verification covers software behavior, source-file identity, mathematical
typesetting and package completeness. Scientific conclusions retain the review
status recorded in each case.

## Required checks

- Locked dependency synchronization, Ruff lint and formatting.
- Python regression suite and isolated website backend suite.
- Node tests for reading, mathematical rendering, account flows and permissions.
- Validation of the active collection and the minimal synthetic software fixture.
- Strict mathematical presentation checks over all current notes.
- Source/wheel builds, archive inspection and installed-wheel offline smoke.
- Browser checks of affected pages and actual public URLs after deployment.
- All five CI jobs at the final integration commit.

## Reader downloads

Article PDFs are checked against the reviewed record's SHA-256. Report PDFs are
compiled from the current registered LaTeX source with shell execution disabled.
Compilation logs and PDF inspection check missing glyphs, clipping and long
equations. ZIP checks verify the exact simple filename list and file bytes.
Only explicitly published contributor revisions can join a reader package.

The current citation catalog covers every case and is bound to its snapshot.
References use official proceedings metadata, with author-line corrections
verified against retained papers where necessary.

[STATUS](STATUS.md) records the latest completed release checks and limitations.

## 22 October 2026 reading update

Local results are recorded in [STATUS](STATUS.md). An initial reader-catalog
check caught two empty upstream author fields; these were corrected before the
full suite passed. PDF QA caught long expressions/paths and two missing
set-difference glyphs. Formatting-only compilation copies fixed wrapping and
glyph selection while preserving the registered scientific TeX sources.

The source package includes the citation catalog and maintained compilation
helper, excludes generated PDFs and operational state, and no longer includes
retired planning documents or the one-time first-edition conversion helper.
Current regression fixtures remain part of software verification.
