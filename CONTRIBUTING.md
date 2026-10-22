# Contributing to ELVIA

For scientific contributions, use the [contribution workspace](https://elvia-atlas.org/contribute.html).
Submit a specific source passage, your analysis and relevant evidence. You can
add a first report, review an existing note or propose an amendment. See the
[publication workflow](docs/publication-workflow.md) for how accepted work becomes
a versioned case note.

For software and documentation, open or choose a
[GitHub Issue](https://github.com/chineseschrodingercat/elvia/issues), describe the
change and submit a focused pull request. Minhao Liu is the sole maintainer.
Software vulnerabilities use [SECURITY.md](SECURITY.md).

Use Python 3.12 or newer and `uv sync --locked`. Follow the checks in
[README](README.md). Start behavior changes with a meaningful failing regression
test. Prose and configuration changes need relevant checks, not artificial tests.
Report actual validation results and material limitations.

Scientific records use new immutable revisions. Preserve source identity,
counterevidence, failed attempts and scope. Editorial acceptance, scientific
decisions, repair verification and author adoption are separate states.
Use clearly synthetic identities in software tests.

Update dependencies deliberately with `uv lock --upgrade-package PACKAGE`,
review the lockfile and rerun checks. Retain pinned GitHub Actions revisions.
Keep credentials, live accounts, private attachments and operational databases
out of source changes.

Original contributions use the path-specific licenses in [NOTICE](NOTICE.md).
Retain third-party attribution and license terms. No CLA is currently required.
