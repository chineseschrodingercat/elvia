# Search discovery

The public entry is https://elvia-atlas.org/. Search discovery connects readers
to useful scientific content and participation routes; it does not certify an
analysis or guarantee a ranking.

## Pages and reader intent

| Reader's question | Example searches to evaluate | Entry page |
| --- | --- | --- |
| What does this particular paper establish? | Exact paper title plus analysis, assumptions, proof, limitations or reproducibility | `/atlas/cases/{case_id}.html` |
| Is there a place to examine scientific claims? | scientific claim verification platform; post-publication research analysis; research evidence atlas | `/` and `/project.html` |
| Where can I contribute a focused check? | contribute to research verification; PhD student research review; open science contribution | `/participate.html` |
| Which platform fits the work I want to do? | research review platforms; post-publication peer review tools; platforms like PubPeer or OpenReview | `/research-review-platforms.html` |
| What examples exist for this method? | A method or theorem actually present in a case plus assumptions, proof check or evidence | Atlas search and the relevant case |

These are hypotheses about intent, not measured search volumes or evidence of
ranking potential. Use a method's name only when the published case supports it.
The platform guide describes different purposes using linked primary sources;
it does not imply partnership, endorsement or superiority.

## Crawlable publication

The homepage links to the Atlas, project explanation and two public guides. The
Atlas has ordinary title links and a complete HTML title directory. Each case
has its own HTML page with the current citation, scientific argument, supporting
record, revision and optional verified reader download. The scientific prose is
present before JavaScript runs; the bundled renderer progressively typesets math.
Older `#case=...` and `case.html?case=...` reading links remain supported.

The stable case identifier is retained in the URL so a title correction does not
break a shared address. The page shows its current revision; an immutable record
and its predecessors remain in the dataset. Canonical links identify the public
HTTPS address. `/sitemap.xml` lists the six public information pages, the Atlas
and the 300 current case pages. New builds derive that list from the records.
`/robots.txt` advertises the sitemap.

Account and password-completion pages retain `noindex`. Account-related query
routes, APIs and errors also receive `X-Robots-Tag: noindex, nofollow`. They are
absent from the sitemap. Account pages remain crawlable so a crawler can observe
the exclusion; the API is also disallowed in robots.txt. These directives are
separate from authentication and access checks. Generic offline Atlas builds
stay unindexed unless a public base URL is explicitly supplied.

## GitHub repository discovery

GitHub's default repository search matches the name, description and Topics.
README text participates when the search explicitly uses `in:readme`; improving
the README alone therefore does not address ordinary repository searches. See
[GitHub's search documentation](https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories).

The About description now states research verification, post-publication peer
review, scientific claims, paper correction, errata and reproducibility. Seven
accurate Topics describe those purposes. The README starts with routes for
scientific contributors and software contributors. These changes improve the
information available for matching; they do not guarantee a Best match rank.

For comparable follow-up checks, use Repositories, Best match, page one, and the
same non-brand queries: `paper correction`, `paper errata`, `research verification`,
`post publication peer review`, `research reproducibility`, `scientific claims`,
`论文纠错`, and `论文 复现`. Record the date, session state, returned count, inspected
entries and observed position. Separate the repository from website search
results. A later index update and a better rank are distinct outcomes.

## Search Console and iteration

The production homepage retains Google's public ownership-verification meta tag.
Use the maintainer's Search Console resource for `https://elvia-atlas.org/`, submit
`https://elvia-atlas.org/sitemap.xml`, and inspect the homepage, Atlas and selected
case/guide URLs. Record the actual verification, sitemap and indexing-request
results in the Issue. A successful submission is not confirmed indexing.

After Search Console has accumulated data, compare impressions, clicks, queries,
landing pages and indexing exclusions. Develop further method guides only where
the actual cases and reader queries support a useful explanation. Improve titles,
descriptions and contextual links based on those observations. Do not create
duplicate keyword pages, unsupported claims or manufactured endorsements.

Primary references checked October 22, 2026:

- [Google: build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [Google: prevent indexing with noindex](https://developers.google.com/search/docs/crawling-indexing/block-indexing)
- [PubPeer](https://pubpeer.com/static/about), [OpenReview](https://openreview.net/about)
  and [The Turing Way](https://book.the-turing-way.org/).
