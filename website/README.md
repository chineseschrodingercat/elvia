# ELVIA website

This directory is the maintained source of the homepage, contribution service and
current Atlas presentation.

The production service is publicly available at https://elvia-atlas.org/.
The maintained checkout is `D:/ELVIA`; operational state is protected separately
under `D:/ELVIA-runtime/production/`.

## Boundaries

- `preview/server/` contains account, permission, submission and authentication logic.
- `preview/site/` contains the current user interface; `site/atlas/` is generated.
- `atlas-assets/` preserves the current Atlas navigation, pagination and styling.
- `preview/tests/` exercises supported behavior with synthetic state.
- `ops/` holds the maintained backup and boot controls. Provider setup helpers
  accept private operational paths; obsolete prototype launchers are retired.

Runtime secrets, provider files, SQLite, attachment BLOBs, backups and connection
metadata live outside this source tree. Keep one authoritative operational writer.
The formal JSON dataset is separate and is never edited by a website endpoint.
The application has no GitHub publishing integration or configured GitHub token.

## File reports and paper reservations

Use the [contribution guide](https://elvia-atlas.org/participate.html) for first
reports and revisions. Both require a report PDF or complete UTF-8 LaTeX file,
up to 20 MiB. First reports also require the article PDF and its main supplementary
PDF when applicable, sharing one 50 MiB combined budget. Verification code is optional: one ZIP or
1–10 source-code/support files, at most 5 MiB in total/unpacked size. Each route
shows only its own LaTeX/PDF template. Publication and reservation release follow
[the publication workflow](../docs/publication-workflow.md).

The version-1 operational migration adds four tables without changing old rows.
It backfills paper reservations and rejects overlapping legacy active claims.
Before rollout, snapshot the stopped writer, verify the backup and rehearse the
migration on a separate restored copy. Confirm that the previous 27 application
tables plus SQLite sequence retain identical rows, protected settings/keys retain
their hashes, and the resulting 31 application tables pass integrity checks.

## Current authentication

Registration opens contribution choices; reviewer access has a separate
application with optional subject selection and institution suggestions from
ROR. My work shows submitted, under-review and decision stages. Opening an
individual staff application starts its review; listing the queue does not.
The configured SMTP service sends each new stage update through the persistent
application_notifications queue. Service entrypoints start its worker; tests
construct state without starting delivery. Retries preserve per-applicant order
and use a stable Message-ID. A provider acceptance followed by a process crash
can still result in redelivery. Migration creates only the empty outbox table
and never sends retrospective updates. See [the onboarding decision](../docs/decisions/0007-contributor-onboarding.md).

Institutional email registration, password recovery, explicitly linked staff Google
sign-in, session/CSRF/ownership checks, and role isolation are implemented. The
owner's verified alias and original maintainer login resolve to one account;
retired identities cannot authenticate separately or count as an independent
reviewer. Preserve all 32 application tables, the SQLite sequence and the existing
verification/HMAC key when transferring state. Existing sessions and pending
authentication challenges expire during an actual relocation; durable budgets
and locks do not.

Ten failed password attempts within a rolling hour lock the verified source for
60 minutes. The fifth failure shows five attempts remaining. A same-page busy
guard prevents accidental duplicate submission. Mail budgets and file/ZIP checks
remain distinct controls.

## Release process

Prepare and test a new code release separately from the active data. Build the
Atlas from validated formal records, verify generated hashes, create a consistent
backup, deploy compatible code, and check the actual public URL. Keep the previous
compatible code release until acceptance succeeds. Schema rollback requires
reconciliation of newer data; restoring an old database is not a code rollback.

The [maintenance decision](../docs/decisions/0001-public-maintenance.md) records the
current deployment boundaries. Same-PC snapshots are rollback copies,
not off-machine disaster recovery. Formal promotion remains an offline maintainer
operation under the existing record protocol, with explicit source identity,
licensing and AI/human provenance checks. Editorial acceptance does not itself
create an independently adjudicated scientific record.

## Build and test

```console
uv sync --locked
uv run --no-sync python -m website.build --output NEW_SITE --reader-library PUBLIC_LIBRARY
uv run --no-sync pytest -q
uv run --no-sync python website/preview/tests/run_private_auth_backend.py local all
node --test tests/*.test.cjs website/preview/tests/*.test.*
```

Use a new output directory for each Atlas build (`--output NEW_PATH`). The build
validates the 700 authoritative records across both collections, applies the maintained presentation and
hashes every served file. See [reader bundles](../docs/reader-bundles.md) to
prepare the PDF library. Omit it only for a source preview without ZIP downloads. Current regression tests use temporary synthetic state
and block real mail/OAuth traffic.

## Production and automatic recovery

`runtime.py` uses Waitress on **127.0.0.1:8799 only**, behind the existing dedicated
Cloudflare Tunnel. The PC and its local programs are the trusted origin boundary.
Do not expose that listener on a LAN or route another hostname or Worker relay to
it. The canonical Host, HTTPS metadata, request size, origin, CSRF and application
permissions are checked independently. Network addresses inform abuse limits;
roles never come from forwarded headers.

Store operational files outside Git under the owner's protected
`D:/ELVIA-runtime/production/` directory. Use a physical directory visible to the
boot task; the initial user-profile location was not visible in its S4U session.
`data/` holds SQLite and provider
settings. `config.json` contains `data_dir`, `turnstile_sitekey`, `turnstile_secret`,
`cloudflared` and `tunnel_token_file`. Configure a Managed Turnstile widget for
`elvia-atlas.org`, with pre-clearance off. Credential and mail requests require
server-side verification of its hostname and action. Attachment bytes across all
retained versions have a transactional 200,000,000,000-byte ceiling plus a 2 GB
free-space reserve and transaction headroom.

Run `ops/Install-Autostart.ps1 -Configuration ABSOLUTE_PRIVATE_CONFIG -Start` once
to register **ELVIA Website**. Windows may require an elevated PowerShell for
registration. The task starts 30 seconds after boot under the maintainer's limited
S4U identity, without an interactive login or stored Windows password. Its
supervisor owns both components and their descendants in Windows Job Objects,
restarts exited processes, prevents duplicate instances and bounds logs. The
Cloudflare connector reconnects after network interruptions.

For updates run `ops/Stop-Website.ps1` (disable recovery, then stop), apply the
checked code and locked environment, switch the validated Atlas if needed, then
run `ops/Start-Website.ps1`. Schema changes additionally need a migration and a
restore check. Inspect the task result, `logs/service.log`, `status.json`, local
connector readiness at `http://127.0.0.1:8800/ready`, and the public URL. A manual
task start is not an observed reboot; report these separately.

## Back up and restore

Stop the task before snapshotting so SQLite and provider configuration are
consistent. Use `python -m website.ops.workspace_backup snapshot --data-dir DATA
--destination NEW_SNAPSHOT --offline`, followed by `verify --snapshot SNAPSHOT`.
`restore-copy --snapshot SNAPSHOT --destination NEW_DATA` verifies hashes, SQLite
integrity and foreign keys, copies into a new protected directory, and expires
sessions, email challenges, OAuth states and recovery tokens. It preserves all
accounts, roles, aliases, linked identities and contribution history. Never
restore an old database over newer submissions. Keep the latest verified backup
until its replacement is verified; no encrypted off-machine backup is claimed.

The report and paper size limits are silent during normal submission; an oversized
file receives actionable compression guidance. The code limit remains visible.
AI configuration is free text: recommended settings are Astra 6 Max, Claude Opus
5.5 xhigh and Gemini Argon 4 high, not an allowlist. Signed-in submission and draft
pages prominently encourage ChatGPT, Claude or Gemini assistance and explicitly
welcome fully manual reviews. Accurate provenance remains required.
