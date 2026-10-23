# Public research discovery and reusable context

Date: 2026-10-23. Work and deployment evidence: [Issue #12](https://github.com/chineseschrodingercat/elvia/issues/12).

## Scientific boundary

The authoritative collection is unchanged. Presentation summaries, lexical search,
citation exports and AI context packets derive from validated public records and
revision-matched notes. They retain source versions, bounded evidence, limitations
and independent-review status. A reference case is a readable example, not an
independent endorsement. The paper authors and the explicitly credited analysis
author are different bibliographic objects. Missing report authors stay absent.

Copy for AI copies only the selected public context to the reader's clipboard.
It never sends a draft to a model or purchases inference. Short and full packets
retain the scientific scope, original source, record revision, canonical snapshot
hash and a link back to the public evidence. The latest HTML permalink can change;
the revision-specific exported record identifies the cited snapshot.

## Discovery controls

The maintained robots file distinguishes search crawlers, user-requested fetchers
and training-related crawlers. It preserves the existing public-access policy;
all groups exclude `/api/`. Account/query pages and errors retain noindex headers.
Robots is not an access-control mechanism. Authentication and authorization still
protect account state and unpublished submissions.

- OAI-SearchBot, Claude-SearchBot and PerplexityBot serve discovery.
- ChatGPT-User, Claude-User and Perplexity-User serve user-requested retrieval;
  their visits are not proof of search inclusion.
- GPTBot and ClaudeBot have separate training-related controls.
- Google-Extended includes specified Gemini training/grounding uses; it does not
  control Google Search ranking or Search generative AI inclusion.

Official references: [OpenAI bots](https://developers.openai.com/api/docs/bots),
[Anthropic crawlers](https://privacy.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler),
[Perplexity crawlers](https://docs.perplexity.ai/docs/resources/perplexity-crawlers),
[Google AI guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide).

Live checks on 2026-10-23 established Google ownership, successful sitemap reading
(307 URLs before this release), an indexed conformal-prediction case and a successful
Google Inspection Tool smartphone fetch. The Search generative AI setting inherited
**Include**. Index coverage was still processing and crawl statistics had no data;
neither is a zero-traffic finding. Cloudflare's seven-day AI crawler table showed
58 allowed OAI-SearchBot requests, 5 ChatGPT-User, 2 PerplexityBot and 2 BingBot;
the named search/user/training crawler blocking switches were off. Anthropic
crawlers had no observed requests. Counts are dated observations, not guarantees.

The research web tool still rejected direct opens while a search returned the
homepage. This channel-specific error cannot be assigned an HTTP cause without
the tool's request details. Do not weaken security or claim universal crawler
access based on a spoofed user agent. Consult actual crawler analytics and URL
inspection when diagnosing future failures.

## Public reading availability

Successful canonical public static reads use browser freshness of five minutes,
shared-cache freshness of one hour and a maximum one-day stale-if-error window.
These stable URLs are deliberately not marked immutable. Query routes, all APIs,
account pages, errors and session-setting responses remain `no-store`. Contribution
availability is fetched independently from its uncached API; a cached page must
never imply an available reservation if the live check fails.

Cloudflare must have a narrow cache eligibility rule for public reading paths;
HTML is not cached by default. Respect origin headers, do not force-cache errors,
cookies or private data, and purge affected public URLs after each deployment.
Warm CDN entries reduce dependence on the PC during brief interruptions. They
do not guarantee cold-cache availability or surviving an entire-PC outage.

A free independent static origin remains a possible later architecture. It needs
an explicit verified asset allowlist, routing of the account/API paths to the PC,
and support for public PDF bundle sizes. This release first uses the existing
free CDN and tests a controlled origin interruption; no paid service is added.

## Maintenance

The local search uses a small explicit synonym vocabulary, token weighting and
matched-field explanations. It does not call an embedding/model service. Test
question phrases against the actual collection and keep no-match behavior honest.
Both generic Atlas and website presentation assets must load the same helper.

The public template guide compares the two existing templates and includes clearly
fictional examples. The upload forms retain only their applicable template pair.
Public reference-case links are checked against the unchanged record/problem IDs.
Sitemap case lastmod uses the actual record timestamp, not the build clock.

Release verification must cover copy/download semantics, clipboard fallback,
escaping, citation identity, canonical/hash consistency, narrow screens and the
reading-to-contribution handoff, followed by the full required checks and CI.
