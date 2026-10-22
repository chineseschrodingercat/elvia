# From a contribution to a published case note

The recommended workflow is **review, prepare, preview, publish**. The website
already stores submissions, attachments, reviewer decisions and amendments.
Publication into the scientific Atlas remains an offline maintainer step;
there is no one-click publishing control in the current admin interface.

## 1. Review the submitted files

Open or download the contribution's report and relevant supporting files from
its workspace. Compare the proposed changes with the current case note and the
original paper. Record which points are accepted, rejected or still unresolved.
Keep the original submission intact. Do not execute submitted code as part of
ordinary document review.

## 2. Prepare one structured draft

Prepare the accepted content in the existing case-note structure, rather than
editing HTML or pasting a formatted PDF into the website:

- Case identity and source version.
- A short current summary and supported impact assessment.
- Each problem's source location, claim, assumptions, analysis, result/scope and
  applicable correction.
- Evidence references, including counterevidence and unresolved points.
- Contributor display name, contribution role and version.
- Current report PDF and the explicit list of submission files approved for
  public download.

For an existing case, create revision N+1 and retain N. For a new case, create
revision 1 after verifying source identity and the contribution's scope. A
separate new-paper identity must not be merged by title similarity alone.

## 3. Preview the changes

Generate the record, narrative, reference/credit catalog and report together.
Validate their shared case ID, revision, source identity and evidence references.
Build a local preview and inspect the changed paragraphs beside the previous
version. Check that the PDF says the same thing as the case note, and inspect
the exact ZIP file list.

The shared renderer supplies headings, spacing, citations, badges and downloads.
The contributor does not have to reproduce the site's design. The maintainer
still approves the scientific wording; formatting cannot establish correctness.

## 4. Publish one checked release

Commit the new snapshot, registered artifacts and updated current catalogs in
one focused change. Pass local and remote checks, build the public reader
library, then deploy and verify the public case. Public file manifests never
search the private upload directory.

The initial report is version 1. Its bundle contains `original article.pdf` and
`report.pdf`. Later approved submissions are named `revision 2.pdf`,
`revision 3.pdf`, and, when present, `revision 2 attachment 1.ext`. The current
`report.pdf` is the maintained report for the currently displayed version.

## Next interface improvement

A maintainer publishing workbench can turn steps 2–4 into a form with a source
selector, per-problem edits, a change comparison, a public-file checklist and a
preview. Publication should remain a separate explicit action after review.
This is a proposed next feature, not an implemented admin button. Until then,
the maintainer can supply approved edits for a checked source update using the
same template and release process.
