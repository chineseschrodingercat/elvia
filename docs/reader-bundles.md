# Citations and reader bundles

The reader view uses each dataset's `reader-catalog.json` for verified
bibliographic fields and named contributor credit. Entries bind to the current
canonical record hash and revision. Missing DOIs remain null and use the actual
publisher source URL. Stale entries cannot silently change a
scientific snapshot.

The current public library explicitly combines 400 ICML and 300 NeurIPS cases.
ICML public reports are formatted copies of the completed reports; the source
notes retain the original archive hashes. Detailed scientific reasoning remains
available in each reading page and the complete report files.

Public PDFs are stored in a separate publication library, outside Git and the
private account/attachment database. `reader-files.json` identifies the exact
article PDF, current report PDF, report-source hash, explicitly published
scientific evidence and any later revision files for each case. The builder
checks every selected file before creating its ZIP. It rejects changed bytes,
stale revisions, escaping paths, conflicting member names and references without
an actual ZIP member.

## Prepare the initial library

Use a reviewed JSON mapping from each case ID to its retained article PDF path.
The command verifies every article against the authoritative record, then
compiles the registered report source with Tectonic's untrusted-input restrictions:

```console
uv run --no-sync python -m website.reader_library --records studies/neurips2025/records --article-index ARTICLE_INDEX.json --output NEW_PUBLIC_LIBRARY --tectonic TECTONIC_EXECUTABLE
uv run --no-sync python -m website.build --reader-library NEW_PUBLIC_LIBRARY --output NEW_SITE
```

Use new output directories. Inspect compilation logs and rendered PDFs before
deployment. Tectonic 0.17.0 was used for the current reader release. Layout-only
copies wrap long equations and identifiers and use a complete mathematical font;
the maintained scientific source remains byte-identical.

The library initializer creates no contributor revisions. To publish an accepted
revision, select its files explicitly, associate them with the actual scientific
revision and mark them published only after the maintainer has reviewed them.
Rebuild the current report from that revision's registered source. Never point
the publication library at private upload storage or auto-publish all attachments.

## Add retained scientific evidence

Prepare an explicit, reviewed private evidence index for every selected case.
The preparation command reads only listed files or listed ZIP members. It does
not discover attachments, execute scientific programs, fetch datasets or change
the scientific record. Reuse the accepted PDFs without recompiling them:

```console
uv run --no-sync python -m website.reader_evidence --records studies/icml2025/records --records studies/neurips2025/records --pdf-library ACCEPTED_PUBLIC_LIBRARY --evidence-index REVIEWED_PRIVATE_INDEX.json --output NEW_PUBLIC_LIBRARY --receipt PRIVATE_SOURCE_RECEIPT.json
```

Each private case selection has `references`, `aliases` and `evidence` lists.
Each evidence entry explicitly selects `source_path`, or `source_archive` and
`source_member`, with the original `source_sha256`, safe `archive_name`,
`references`, `published: true` and `transformation`. A reviewed scientific copy
also supplies `public_source_path` and its public `sha256`. Preparation verifies
the actual retained bytes, not just the declared hash. The private receipt keeps
physical source locators outside the public library for independent verification.

The public sidecar contains no physical source paths. An evidence entry records
its content-addressed library `path`, public `sha256`, original `source_sha256`,
`archive_name`, references and transformation description. `verbatim` requires
identical source and public bytes. `sanitized-scientific-copy` identifies an
explicitly reviewed copy that omits operational metadata while preserving its
scientific content. This is not permission to omit scientific limitations,
failed checks, negative results or model/version identities.

Aliases associate original report locators with actual members. For example,
`papers/0268/0268.pdf#page=19` can point to `original article.pdf`; page anchors
do not require duplicate PDF bytes. A reference to multiple inspected versions
must label each target with its actual `source_version`. Missing materials are
declared separately with their reason and scope; an unavailable declaration does
not satisfy a required evidence reference. A release must resolve required
references to actual retained members rather than invent replacement evidence.

Scientific source ZIPs may be explicitly selected as attachments. Their members
are checked without extraction or execution. Credentials, private host paths,
links and ambiguous member names are rejected. Remove incidental caches only
through an explicitly described scientific copy, retaining scientific member
bytes and applicable third-party terms.

## What readers receive

The case-note presentation catalog may supply `source_quotes` with verbatim
`text`, a PDF `locator`, `source_identity` and `source_sha256`. Quotes must match
the original article hash and the note's record revision/digest. Missing or empty
quotes display the source location alone. Extraction difficulty does not justify
presenting a reviewer paraphrase as a quotation. A quote-only note is allowed for
a No Issue Found or scope-clarification record without inventing a problem.

Readers see one article abstract and complete statement/argument/scope sections
for actual problems. Downloaded evidence preserves the underlying report and
scientific repair history even though correction instructions and duplicate
evidence dumps are excluded from the reading layout.

- `original article.pdf`: the exact inspected source version.
- `report.pdf`: the current maintained report.
- Explicitly selected calculation programs, result files, source excerpts,
  inspected source versions, source images and scientific notes.
- `evidence-manifest.json`: exact member hashes, original-source hashes,
  transformations and reference-to-member mappings.
- Approved later submissions, when present: `revision 2.pdf`, with simply named
  attachments if needed.

Internal task/conversation logs, private account files, compilation records and
credentials are excluded. A scientific calculation script or JSON result is
evidence and can be included after explicit selection. Original articles and
third-party source files retain their own copyright and terms. The ZIP comment
retains attribution; ELVIA's licenses do not relicense those materials.
