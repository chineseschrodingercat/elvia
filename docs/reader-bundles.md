# Citations and reader bundles

The reader view uses each dataset's `reader-catalog.json` for verified
bibliographic fields and named contributor credit. Entries bind to the current
canonical record hash and revision. Missing DOIs remain null and use the actual
publisher source URL. Stale entries cannot silently change a
scientific snapshot.

The current public library explicitly combines 400 ICML and 300 NeurIPS cases.
ICML public reports are formatted copies of the completed reports; the source
notes retain the original archive hashes. Complete transcriptions, including
code and named equation references, remain available in each reading page.

Public PDFs are stored in a separate publication library, outside Git and the
private account/attachment database. `reader-files.json` identifies the exact
article PDF, current report PDF, report-source hash and any explicitly published
revision files for each case. The builder checks every selected file before
creating its ZIP. It rejects changed bytes, stale revisions and escaping paths.

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

## What readers receive

- `original article.pdf`: the exact inspected source version.
- `report.pdf`: the current maintained report.
- Approved later submissions, when present: `revision 2.pdf`, with simply named
  attachments if needed.

No JSON records, manifests, hashes, internal logs or tooling are added as ZIP
members. Original articles retain their own copyright and source terms. The ZIP
comment retains attribution; ELVIA's licenses do not relicense the article.
The complete scientific dataset remains available in the source repository.
