# Decision 0011: publish the accepted Math 2025 collection

Issue: https://github.com/chineseschrodingercat/elvia/issues/27

## Authorized scope

The maintainer authorized publication of the existing independently checked Math 2025 analyses. The selected roster contains 514 integrity-accepted articles from the frozen 887-work membership. Initial-review readiness and acceptance readiness are not publication eligibility. The importer requires the controller's accepted count, unique IDs and integrity bindings to agree.

The new `studies/math2025` collection is separate from the existing 400 ICML and 300 NeurIPS cases. Existing scientific snapshots and published revisions remain unchanged. The combined Atlas contains 1,214 cases, with the new cases classified under Mathematics.

## Source and acceptance identity

For each selected article, check the acceptance receipt hash and every one of seven core files against both the immutable accepted snapshot and the current archive: article PDF, source manifest, report TeX, report PDF, findings, coverage and provenance. Missing or altered accepted inputs block publication. Only explicitly selected additional scientific evidence enters downloads.

Journal membership identifies a work. The canonical article entry in its source manifest identifies the actual inspected version and PDF hash. The importer preserves preprint revisions, repository versions and limits on equivalence to a journal version. It does not substitute the frozen membership workbook's acquisition placeholder for an inspected source version. The collection year denotes the authorized membership, not an assertion that every inspected manuscript was written or issued in that year.

## Scientific state and public presentation

This import is a publication conversion, not a new scientific review. Existing paper-level classifications take precedence over unresolved subitems. Heterogeneous classification fields use a reviewed mapping bound to the exact findings and report source hashes. The highest supported impact is not inferred from hypothetical uses of the word Major.

Independent AI acceptance does not become human adjudication. All imported records retain pending human scientific decisions, empty human-review lists and no author adoption request. Complete arguments, assumptions, counterevidence, rejected interpretations and remaining uncertainty remain in the maintained report and evidence. Exact matching numbered report sections may supply the full detailed argument; no missing proof is invented.

Raw LaTeX is parsed as data with a strict adapter. Only the maintained public transcription is compiled. The public dataset and download library exclude conversations, task tokens, credentials and private host paths. Portable scientific references and original source hashes remain available. Source articles retain their original copyright and publication terms.

The conversion preserves the source mathematical spans before applying explicit, audited public typography rules. The PDF typography catalog binds complete generated TeX hashes for nine reports: three equation-label placements, three set-difference glyph renderings, and three font-specific symbols. These changes preserve the scientific expressions and report arguments. Unchanged unpublished PDF renderings may be reused only after matching the original article bytes, registered report source, formatted compilation source and prior PDF bytes, with the new record digest bound explicitly.

## Release boundary

Validate all 514 records and presentation bindings, all explicit mathematical expressions, reader PDF identities and selected evidence references. Build in a new release location, verify existing 700 records and bundles, and run required repository checks and CI at the final merged head. Deployment uses a stopped-writer backup and a separate restore rehearsal, preserving operational database rows, identifiers, schema and protected configuration files. Storage cleanup and cloud archival are separate decisions; publication does not authorize deletion of the raw archive or runtime history.
