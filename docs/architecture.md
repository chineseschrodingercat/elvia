# Architecture

ELVIA combines a Python record toolkit with a maintained website and contribution
service. Scientific JSON and private operational SQLite have separate authority.
`jsonschema` checks a packaged schema; standard-library tools handle CLI, exact
arithmetic, hashes, files and SQLite. Python 3.12 is the compatibility floor.

| Module | Responsibility |
| --- | --- |
| `records.py` | Bundled schema and workflow/path/hash validation; located errors, no writes |
| `storage.py` | Canonical discovery, predecessor checks and exclusive immutable snapshot publication |
| `demo.py` | Original synthetic source, exact arithmetic, evidence and pending record |
| `index.py` | Validate first, stage a SQLite transaction, atomically replace a disposable index |
| `export.py` | Validate first; publish into a new directory with byte-preserved JSON, artifacts, full views and hashes |
| `reader.py` | Snapshot-bound citations, credits and explicitly selected PDF reader bundles |
| `site.py`, `website/build.py` | Validated Atlas generation and maintained public presentation |
| `website/runtime.py`, `website/supervisor.py` | Public ingress, application runtime and automatic recovery |
| `cli.py`, `__main__.py` | argparse commands, console/module entry points and concise nonzero failures |

The dataset root is the parent of `records/`. Source, evidence and run outputs
are referenced by portable relative paths and SHA-256. Canonical snapshots use
`records/<case_id>.r<revision>.json`; other JSON artifacts live elsewhere.
Load checks every requested snapshot and required predecessors. A single-file
index returns one requested row; its historical artifacts are still protected.
A single-file export includes its full predecessor chain for portable validation.

Storage writes a complete flushed temporary file and publishes an exclusive hard
link; unsupported filesystems fail rather than fall back to partial writes.
Index replacement protects resolved records/artifacts and rejects existing
non-SQLite files. Exports reject collisions before creating a fresh output
directory; on failure, cleanup removes only that newly owned directory. Export
views can be visible during writing; whole-directory atomic publication is not
claimed. Exports stage payloads before publication.

The local trust boundary assumes artifacts/directories are not maliciously
replaced concurrently. Hash checking is not code execution isolation or reviewer
authentication. Declaration gates do not establish scientific correctness.
See [record format](record-format.md) for exact API/field semantics and
[the maintenance decision](decisions/0001-public-maintenance.md) for consequential design choices.
