# Bundled font sources

The Atlas self-hosts two unmodified Adobe variable fonts. Browsers use only these
local WOFF2 files; no font service, external stylesheet or network font request is
needed. Source Serif 4 supplies headings; Source Sans 3
supplies body text and controls. Both upright fonts support weights 200–900.
Italic faces are not bundled, and CSS disables synthetic styles.

| File under `src/elvia/web/` | Upstream repository and pinned commit | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `SourceSerif4Variable-Roman.otf.woff2` | `adobe-fonts/source-serif` at `80d3f8894c09c937bebfa9011247d2e1c79fd6f4` | 426716 | `f146ee102dddcc5bc7a2cf4af5bcf129832195941b92bd0a512626f390688c1e` |
| `SourceSans3VF-Upright.otf.woff2` | `adobe-fonts/source-sans` at `87b37a2daaed80fcb8e8ccb0085c4d72ddade12e` | 164736 | `f9e4eac0e8f8ffdae91cf6eff3962b96e81417cba5c728bc1c89efe9510e7653` |
| `LICENSE-SourceSerif4.txt` | Source Serif upstream `LICENSE.md`, same pinned commit | 4491 | `c21d7293d87b6d7ab1d0229a2f55b77f33a7613a6a4e66f6693d68d7d8d09464` |
| `LICENSE-SourceSans3.txt` | Source Sans upstream `LICENSE.md`, same pinned commit | 4486 | `56af9b9c6715597e458284a474dc118a50a4150e9d547c70f7b4a33c3e6a9328` |

Original binary URLs:

- [Source Serif 4 Roman OTF WOFF2](https://raw.githubusercontent.com/adobe-fonts/source-serif/80d3f8894c09c937bebfa9011247d2e1c79fd6f4/WOFF2/VAR/SourceSerif4Variable-Roman.otf.woff2)
- [Source Sans 3 upright OTF WOFF2](https://raw.githubusercontent.com/adobe-fonts/source-sans/87b37a2daaed80fcb8e8ccb0085c4d72ddade12e/WOFF2/VF/SourceSans3VF-Upright.otf.woff2)

Full upstream copyright and SIL Open Font License 1.1 notices, copied byte for
byte, are [Source Serif's license](https://raw.githubusercontent.com/adobe-fonts/source-serif/80d3f8894c09c937bebfa9011247d2e1c79fd6f4/LICENSE.md)
and [Source Sans's license](https://raw.githubusercontent.com/adobe-fonts/source-sans/87b37a2daaed80fcb8e8ccb0085c4d72ddade12e/LICENSE.md).
The upstream copyright notices reserve the font name “Source”. ELVIA does not
modify, rename, subset, convert or claim authorship of the font software.

KaTeX's own math fonts supply equations; see [math rendering](math-rendering.md).
The wheel and each static Atlas contain both Adobe binaries and both complete notices.
The builder checks the four pinned hashes before creating its target directory;
the generated manifest then hashes all shipped assets. Its explicit allowlist prevents
unrelated package or local files from entering the static export. The README's
editable workflow SVG is original ELVIA documentation under Apache-2.0; its text
uses local font fallbacks when viewed separately.
