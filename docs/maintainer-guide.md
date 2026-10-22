# Maintainer guide

Minhao Liu is the sole maintainer. Read [STATUS](STATUS.md) and the relevant
GitHub Issue. Develop in an isolated checkout; keep live accounts, attachments,
provider credentials and backups outside source control.

## Validate and build

Use the locked development sequence in [README](../README.md), including the
Python, Node and isolated website backend suites. Validate the active collection
and run its mathematical presentation checker before building the Atlas.

`python -m website.build --output NEW_PATH --reader-library PUBLIC_LIBRARY`
builds the production reading view. The public library contains only explicitly
selected publication files. A build without it is a source preview and does not
offer a reader ZIP download. See [reader bundles](reader-bundles.md).

The source distribution includes the 300 records and maintained text/TeX sources.
The wheel includes schemas, Atlas software, original font files and their notices.
Neither package includes live state, private uploads, generated reader PDFs,
preview builds or machine-specific tools.

## Installed-wheel offline check

After `uv sync --locked` and `uv build`, use a fresh environment. In Git Bash:

```bash
uv export --locked --no-dev --no-emit-project --format requirements-txt --output-file wheel-requirements.txt
uv venv --python 3.13 wheel-venv
wheel_python=wheel-venv/bin/python
if [ -f wheel-venv/Scripts/python.exe ]; then
  wheel_python=wheel-venv/Scripts/python.exe
fi
uv pip sync --python "$wheel_python" wheel-requirements.txt
uv pip install --python "$wheel_python" --no-deps dist/*.whl
"$wheel_python" scripts/offline_smoke.py
```

The smoke test runs outside the source tree with sockets blocked and API-key
environment values removed. It validates bundled schema/assets and the minimal
original software fixture. Do not commit the environment or dependency export.

## Publish scientific updates

Follow [publication workflow](publication-workflow.md). Review the original
contribution, prepare structured changes, inspect the rendered comparison and
publish a new snapshot. Preserve every published predecessor and referenced file.
Update the current narrative, citation/credit catalog and PDF manifest together.
Never edit an old hash just to make validation pass.

Batch import, revision and source-refresh scripts preserve explicit source
identity and require reviewed inputs. They are maintenance tools, not a website
publishing button or substitutes for individual scientific decisions. The
current contribution application does not have a GitHub token or write to Git.

## Deploy and recover

Use [website operations](../website/README.md) for the Windows boot task,
supervisor, Cloudflare connection, backup and release procedure. Stop recovery
before switching a release, then restart and verify the public URL. A compatible
code rollback does not restore an older operational database.

Keep JSON and registered artifacts together in backups. Derived indexes can be
rebuilt. Restore missing evidence from verified copies; scientific content changes
require a new revision. Windows symlink tests may be skipped when the required
privilege is absent; report that explicitly.

## Dependencies and integration

Use `uv lock --upgrade-package PACKAGE` for a deliberate dependency update.
Review the lockfile and repeat relevant checks. GitHub Actions stay pinned to
official full commit SHAs with read-only permissions and bounded jobs.

The five stable checks are `quality`, `test (ubuntu-latest, 3.12)`,
`test (ubuntu-latest, 3.13)`, `test (windows-latest, 3.12)` and
`test (windows-latest, 3.13)`. Require all green at the final integration commit.
Do not claim remote checks, repository enforcement or deployment before verifying
them. Do not force-push or purchase services as part of routine maintenance.
