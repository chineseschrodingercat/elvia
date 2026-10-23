# Contributor onboarding and reviewer application progress

Date: 2026-10-23
Tracking: [Issue #16](https://github.com/chineseschrodingercat/elvia/issues/16)

Ordinary registration opens contribution choices. Explicit same-origin report
destinations retain their context. An account can submit its own first report;
reviewer access remains a separate application with the existing authorization
checks. Required markers are larger, red and starred.

The application offers 28 position choices, including Graduate student for
master's and doctoral students. Independent researcher is removed. Existing
stored profiles remain readable. A versioned, locally maintained catalogue
contains 496 research subjects and methods across ten broad groups. Expertise is
optional, searchable and limited to five selections including Other; a custom
Other entry remains possible. The backend validates the same limit and catalogue.
The research-profile control offers eleven services/types and a full URL, with a
custom service name for Other.

Institution suggestions use the public ROR v2 query API through the server.
Only institution search text is sent; no account information is included.
Requests are debounced, bounded in concurrency, response size and duration, and
cached with a bounded in-memory cache. Manual entry works when there is no match
or the provider is unavailable. ROR's [query documentation](https://ror.readme.io/docs/api-query)
recommends this endpoint for form suggestions. The public Contact page uses the
existing contact@elvia-atlas.org address and is linked in page headers and the
sitemap.

Applications move from pending (displayed as Submitted) to under_review when
authorized staff explicitly opens that application's details. Loading the queue
does not change any application. Approval, requests for information and declines
remain distinct outcomes. Submitted applicants see a 1–3 day estimate and a
prominent, accessible progress list. Open applicant pages refresh every 30
seconds and when the page becomes visible. Requested changes can be resubmitted;
pending applications cannot be repeatedly resubmitted. History is retained, and
the current progress display starts at the latest submission.

One additive table, application_notifications, records outgoing stage messages
in the same transaction as each transition and its event. Existing tables and
application rows are not rewritten. Only newly recorded transitions create mail;
deployment does not send retrospective messages for existing applications.
Notifications use the existing configured SMTP service and the applicant's
verified address. Sending is outside request/database transactions, with bounded
leases, retry backoff and per-applicant ordering. Repeated opens or identical
decisions do not create duplicate notifications. SMTP cannot provide exactly-once
delivery: a crash after provider acceptance but before the local receipt can
retry the same stable Message-ID. Tests capture all mail locally.

Before rollout, verify a stopped-writer snapshot and rehearse restore/migration
in a new protected directory. Compare all existing rows and schema objects,
protected configuration and keys; the only permitted storage addition is the
empty notification table. Keep the old code and reading release for recovery.
Rolling back code never restores an older operational database. Scientific
records, scientific decision requirements and reviewer independence are unchanged.
