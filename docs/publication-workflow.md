# From a contribution to a published case note

The recommended workflow is **review, prepare, preview, publish**. The website
already stores submissions, attachments, reviewer decisions and amendments.
Publication into the scientific Atlas remains an offline maintainer step;
there is no one-click publishing control in the current admin interface.

## 1. Review the submitted files

Both contribution routes require an uploaded report PDF or complete LaTeX file,
up to 20 MiB. Each form provides its own detailed LaTeX template and matching PDF.
First reports also require the original article PDF and, when applicable, the
main original supplement as a separate single PDF. Together they may total
50 MiB; either PDF can use that budget alone.
Later reports identify existing problem numbers and distinguish new findings
inside the report without repeating the source uploads. Optional verification
code is one ZIP or up to ten files, no more than 5 MiB in total/unpacked size.
The website records the files and basic metadata, retaining every submitted
version. The generated submission archive is automatic; no report ZIP preparation
is required. Intake does not compile uploaded LaTeX or execute uploaded code.

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

## 5. Confirm integration before the next reviewer

One active contribution reserves a paper across the Atlas, task and new-paper
routes. Drafts, requested changes, submissions and editorial acceptance retain
the reservation. Releasing a draft or declining it reopens the paper. Acceptance
alone does not. Known DOI/arXiv aliases and published source URLs share a key.

After publishing the accepted content, open the accepted contribution as an admin
or maintainer and use **Verify integration and reopen this paper**. Supply the
published case ID, deployed revision number and an integration note, and confirm
that the accepted changes are included. The server checks source identity and,
for an existing Atlas case, a strictly newer revision. It records the published
context hash and the staff declaration before releasing the reservation. These
software checks do not establish scientific correctness or human independence.

New amendments to final versions use this same browser revision route. Historical
amendment requests and their decisions remain readable and actionable.

## Next interface improvement

A maintainer publishing workbench can turn steps 2–4 into a form with a source
selector, per-problem edits, a change comparison, a public-file checklist and a
preview. Publication should remain a separate explicit action after review.
This is a proposed next feature, not an implemented admin button. Until then,
the maintainer can supply approved edits for a checked source update using the
same template and release process.

The report and paper size limits are silent during normal submission; an oversized
file receives actionable compression guidance. The code limit remains visible.
AI configuration is free text: recommended settings are Astra 6 Max, Claude Opus
5.5 xhigh and Gemini Argon 4 high, not an allowlist. Signed-in submission and draft
pages prominently encourage ChatGPT, Claude or Gemini assistance and explicitly
welcome fully manual reviews. Accurate provenance remains required.
