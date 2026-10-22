# Public service and maintenance boundaries

Date: 2026-10-22

The maintainer authorizes the public website, reading improvements and a clean
public source repository.
Hosting uses the existing computer with automatic startup.

Develop and verify source changes in an isolated checkout. Live accounts,
attachments, provider credentials and backups remain outside Git. Ordinary
interface updates do not reset accounts or migrate operational data.

The active collection retains its published version-1 snapshots. Scientific
updates append revisions. Citation metadata and named credit bind to the relevant
snapshot. Reader downloads use an explicit file list and verified PDF identities.

Publication starts a new repository from the maintained source and current
collection. The former repository is retained as the private
`elvia-internal-archive`; its commits, branches and Issues are not imported into
the public repository. This preserves development history without publishing
private material or rewriting that history. Future changes use the public
repository's normal branch, review and regression workflow.
