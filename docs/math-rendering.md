# Mathematical notation in the Atlas

The Atlas typesets inline and display mathematics locally. Equations use KaTeX's
TeX fonts, with fractions, sums, subscripts, matrices and mathematical alphabets.
HTML provides visual layout and MathML supplies the accessible representation.
Case summaries, claims, domains, assumptions, analysis, evidence, limitations and
repairs use the same renderer. The active Atlas no longer shows the synthetic
worked example.

## Evidence and presentation

Existing scientific snapshots and downloaded evidence remain unchanged. The reviewed
`src/elvia/web/math-notation.json` sidecar maps exact original strings to prose
with explicit `\(...\)` inline and `\[...\]` display expressions. Each case is bound
to its revision and SHA-256 of canonical JSON (`sort_keys=True`, compact
separators, `ensure_ascii=True`, UTF-8). The builder fails before creating output
if a mapped revision has changed. Later revisions and unknown cases never inherit
an older mapping. Only selected cases' mappings enter the derived `data.json`.

For new records, explicit delimiters work directly in displayed prose; bare
ASCII notation is deliberately not guessed. Keep machine identifiers, paths,
hashes, URLs and program code literal. New notation for an existing frozen record
belongs in the sidecar, with an independent notation check against its original
text. That check is not scientific peer review. Existing Markdown and JSON
downloads remain source material; the browser's case note is the typeset view.
When substantive reasoning or impact is revised, create an additive record and
new artifact paths as specified in ADR 0009. Do not overwrite a predecessor to
correct its typography.

Untrusted prose enters the DOM as text. Only delimited expressions go to KaTeX,
with `trust: false`, strict parsing, bounded macro expansion and size, and a fresh
macro scope for each expression. Rendering failure preserves the original text
and shows a readable fallback notice. Search continues to use original evidence
text. No evidence program is executed by the viewer.

## Pinned offline assets

- [KaTeX 0.19.0 official release](https://github.com/KaTeX/KaTeX/releases/tag/v0.19.0),
  source commit `6ea2dc97188f0cc282e05a9690418ae7fe5457ba`.
- Official `katex.zip` SHA-256:
  `012b5e160d6d0eeeedf68aff641b22711c0d834b89c7c37d2e407325409ba17b`,
  verified against the GitHub release asset digest.
- Unmodified minified JavaScript, stylesheet, all 60 referenced font files and
  the complete MIT license live under `src/elvia/web/vendor/katex/`.
- `assets.json` records every asset's SHA-256 and upstream identity. Its SHA-256
  is pinned in `site.py`; every listed byte is verified before output creation.
  The complete CSS font closure is bundled in wheels and static exports.

The client uses no CDN, remote font service or network math API. Script and font
sources remain restricted to the local origin by the Content Security Policy.
KaTeX's own DOM construction supplies equation layout. See its official
[options](https://katex.org/docs/options) and [security guidance](https://katex.org/docs/security).

## Verification

Run the usual locked Python checks and installed-wheel offline smoke, then
`node --test tests/math-rendering.test.cjs` with Node.js 22 or later. Node is a
test tool only; there is no npm dependency installation, build step or runtime
requirement for the Python CLI. CI runs these tests with the runner's installed
Node in the existing `quality` job. They parse every reviewed equation with the
actual vendored renderer and exercise delimiter handling, fallback and hostile
input. Python tests check identity binding, unchanged records, offline asset
closure and corruption failure before mutation.

The active collection also runs `node scripts/check_review_notes.cjs studies/neurips2025/records`.
This checks explicit formulas with the pinned renderer and flags common
unmarked algebra, doubled delimiters, word/number collisions and internal-file
dependencies. It is a content-review aid, not a complete recognizer of mathematics
or a proof of scientific correctness. A successful parser check alone cannot
establish that all mathematical prose has been marked or that it is readable.

Also inspect every current case in a browser, on desktop and a narrow viewport.
Check that inline symbols align with prose, display equations scroll inside
their containers, MathML is present, fonts load locally, and there are no math
fallbacks or console errors. Check filters, keyboard dismissal, permalinks and
evidence downloads. Unit and source checks alone cannot establish visual layout.
