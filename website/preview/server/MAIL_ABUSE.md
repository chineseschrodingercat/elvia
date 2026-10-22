# Automatic-mail abuse controls

These conservative defaults are for the single-maintainer ELVIA deployment.
They bound ELVIA's automatic registration-code and password-reset attempts. They
are not a provider billing hard cap: other clients or a stolen provider credential
can consume the provider account separately. Provider dashboards and alerts remain
separate operator controls. Browsing, reading Atlas records and existing signed-in
sessions do not consume the authentication request budget.

| Scope | Limit |
| --- | --- |
| Same normalized recipient, code and reset combined | 60 seconds between reservations; 5 per rolling hour; 10 per rolling day |
| All automatic mail, both purposes combined | 20 per rolling hour; 80 per rolling day; 1,000 per UTC calendar month |
| Existing password-reset account limit | 5 per rolling day, retained independently |
| Authentication requests, all identities | 120 per rolling 15 minutes; 500 per rolling day |
| Authentication requests, same operation and normalized identity | 12 per rolling 15 minutes; 40 per rolling day |
| Concurrent authentication handlers | 4 |
| Concurrent SMTP deliveries, both purposes combined | 2 |
| Older in-memory endpoint limit key count | 2,048, with no eviction of live keys |

The shared mail-request identity budget covers code requests and recovery
requests, including unknown recovery identities. Login and registration use
separate operation namespaces. Forgotten-password traffic cannot spend the
same account's login allowance. Recovery completion has its own namespace and
never uses a reset token as a stored key. All throttled recovery requests retain
the same HTTP 202 body as eligible, unknown, disabled-mail or busy requests.

The existing email normalization is retained: trim and case normalization only.
No dot removal, plus-alias folding or rewrite of institutional addresses is added.
Budget identities are HMAC-SHA256 values keyed by the existing private email
verification key. No raw email, login, IP, verification code, password or reset
link is added to the budget tables or status output.

Reservations use the same SQLite `BEGIN IMMEDIATE` transaction as code/reset
creation. Global and recipient checks precede invalidation of any earlier code
or reset link. Throttling therefore preserves the previous valid code/link and
does not change passwords, roles, provider links, suspensions or account sessions.
An attempted SMTP delivery consumes the reservation even when transport fails;
there is no automatic retry/refund loop. SMTP runs outside the database write
transaction, within the two shared delivery slots. Recovery remains asynchronous.

The additive tables are `abuse_mail_reservations` and `abuse_requests`: the
existing 22 application tables remain and the new total is 24. Mail rows retain
the current UTC month plus a rolling day across its boundary, with a hard maximum
of 1,100 rows. Request rows expire after a rolling day, with a maximum of 512;
the 500/day admission limit normally keeps this lower. Denied requests create
no new key or reservation. Restarting the service does not clear these budgets.

The maintained stopped-writer snapshot/restore helper copies the entire database
and private email key, then clears only the four existing transient-auth tables.
It therefore preserves both abuse budgets and their HMAC key. A synthetic round
trip verifies exact rowids/content and an effective cooldown after restore.
Restoring a historical snapshot can rewind any local accounting; use current
same-data code rollback for ordinary release rollback, not an old database merely
to restore sending allowance.

The separately preserved Phase 3 encrypted-transfer toolkit pins the old 22-table
schema. It intentionally refuses this 24-table state until its schema catalog and
compatibility rehearsal receive a separate review. This release does not update
that toolkit or establish real server migration readiness.

Tests use isolated databases, fake SMTP and blocked external/provider connections.
They cover recipient/global bounds, restart persistence, concurrent reservations,
unknown recovery identities, failed delivery accounting, bounded HMAC key storage,
shared worker limits, preservation of valid codes/reset links and login isolation.
Provider configuration, real delivery, received SPF/DKIM/DMARC and inbox placement
are separate acceptance checks.
