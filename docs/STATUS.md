# Project status

The public website is [elvia-atlas.org](https://elvia-atlas.org/). It hosts the
homepage, 300-paper NeurIPS 2025 Atlas and contribution workspace. Windows starts
the service after boot; the computer must remain awake and connected.

## Current collection

- 300 first-edition scientific records.
- 104 Major, 177 Minor, 3 Needs Evidence and 16 No Issue Found assessments.
- 284 detailed notes with 1,088 problem sections.
- Independent scientific decisions remain pending.

## Reading update — 22 October 2026

The current update adds a dedicated password-reset completion page, verified
article citations with DOI links, clearer assessment/status typography, concise
supporting information and PDF reader bundles.

Local verification: 235 core tests passed (2 Windows symlink privilege skips),
201 isolated website backend tests passed, and 106 Node tests passed. The
collection checker covered 20,819 mathematical expressions without errors.
Locked dependency sync, lint/format checks, both record validators, package build
and fresh installed-wheel offline smoke passed.

All 300 article PDFs and 300 report PDFs parsed successfully. All 300 reader ZIPs
contain exactly the two intended PDFs with verified identities and valid CRCs.
Report layout checks found no remaining missing glyphs or overfull boxes; selected
reports and the desktop reading views were inspected visually. Scientific record
and evidence source bytes remain unchanged.

The [public repository](https://github.com/chineseschrodingercat/elvia) starts
with a clean snapshot of the maintained source and current collection. Earlier
development history remains in a separate private archive. Operational data,
credentials, private submissions and generated reader PDFs are outside Git.
[Issues](https://github.com/chineseschrodingercat/elvia/issues) track current
work, and [Actions](https://github.com/chineseschrodingercat/elvia/actions)
records the checks for each public commit.

## Operations

Code and generated site files are separate from protected account/attachment
state. The automatic startup task has been exercised with manual start/stop and
process recovery; an actual computer reboot has not been observed in validation.
There is no configured off-machine disaster-recovery service.

See [website operations](../website/README.md),
[publication workflow](publication-workflow.md) and [project direction](ROADMAP.md).
