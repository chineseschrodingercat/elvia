# File submissions and serialized paper revisions

Date: 2026-10-23. Tracking: [Issue #8](https://github.com/chineseschrodingercat/elvia/issues/8).

The contribution form opens in a new tab. Both first contributors and later
review/revision contributors upload one report PDF or complete UTF-8 LaTeX file,
up to 20 MiB. Scientific findings, severity, evidence and limits stay in the report;
they are not retyped into individual web fields. Each route displays only its
matching LaTeX template and a PDF compiled from that same source. Detailed report
requirements appear immediately above the upload. AI assistance is encouraged
with accurate disclosure and contributor verification, not assumed correctness.

First submissions also require the original article PDF and the main original
supplementary document as a separate single PDF when applicable. Their latest
files share a 50 MiB total limit, whether one or both are present. Replacements
count instead of the file being replaced; historical versions remain retained. Later revisions retain the published paper identity, revision
and source materials. Existing problem numbers can be selected as an optional
index; responses and new problems are explained inside the uploaded report.

Optional verification code has its own slot: one standard ZIP or 1–10 source-code
and text support files, with a shared 5 MiB raw/unpacked limit. Loose files are
archived automatically without altering their bytes. There is no prescribed code
folder layout. Files support drag/drop and browsing. Uploaded code and LaTeX are
never executed or compiled by intake. Format checks cannot establish scientific
completeness; editorial review still checks the report against the requirements.

The operational SQLite migration adds `report_schema`, `paper_claims`,
`paper_integrations` and `contribution_files`. The latter retains versioned report,
original-supplement and verification-code attachments; article PDFs retain the
existing source-file store. Immutable submission records bind each attachment ID.
Every retained version counts toward the storage ceiling and keeps its existing
owner/assigned-reviewer/staff access boundaries. Generated submission archives
retain compatibility with the existing version history and credit records.

A partial unique index and immediate write transactions enforce one active claim
per canonical paper identity. Known DOI/arXiv aliases and URLs in the published
catalog share that identity. Arbitrary unknown publisher URLs cannot be inferred
to identify the same paper without metadata; use canonical DOI/arXiv URLs when
possible. Drafts, requested changes, submissions and acceptance hold the paper.
Released drafts and declined submissions reopen it. Acceptance requires a staff
integration record pointing to a deployed matching case and, for existing cases,
a newer immutable scientific revision. The context hash and staff declaration
are retained. The website never edits scientific JSON. Unfinished file submissions
cannot be frozen by a premature final decision. Historical amendment requests
remain readable and actionable; new changes use the same reservation route.

Migration is additive and idempotent. Existing active claims are backfilled;
overlaps fail atomically instead of discarding work. Rehearse on a verified
stopped-writer snapshot, verify a separate migrated backup/restore and preserve
all prior table rows, provider configuration and keys. Do not restore an older
database over newer submissions when rolling back code.

Public case pages and the Atlas list show availability without contributor names,
private contribution IDs or report contents. A failed status read never claims
a paper is available; creation rechecks availability transactionally.

The report and paper size limits are silent during normal submission; an oversized
file receives actionable compression guidance. The code limit remains visible.
AI configuration is free text: recommended settings are Astra 6 Max, Claude Opus
5.5 xhigh and Gemini Argon 4 high, not an allowlist. Signed-in submission and draft
pages prominently encourage ChatGPT, Claude or Gemini assistance and explicitly
welcome fully manual reviews. Accurate provenance remains required.
