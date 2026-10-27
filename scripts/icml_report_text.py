"""Retain report text through Pandoc's LaTeX reader, without compiling TeX.

Pandoc 2.12 has no native --sandbox. This adapter supplies only stdin, uses an
empty working/resource/data directory, enables no filters or citation processor,
and rejects active file, execution and dynamic-control commands before parsing.
JSON output retains links/images as data and does not fetch their resources.
This is a constrained reader invocation, not an OS network isolation guarantee.
Unknown AST nodes and parser warnings fail instead of silently dropping content.
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

_LITERAL_ENVIRONMENTS = {
    "verbatim",
    "verbatim*",
    "Verbatim",
    "Verbatim*",
    "BVerbatim",
    "LVerbatim",
    "lstlisting",
    "minted",
    "comment",
}
_FORBIDDEN = {
    "input",
    "include",
    "includeonly",
    "inputiffileexists",
    "iffileexists",
    "openin",
    "openout",
    "read",
    "readline",
    "write",
    "write18",
    "immediate",
    "directlua",
    "special",
    "csname",
    "endcsname",
    "catcode",
    "scantokens",
    "expandafter",
    "edef",
    "xdef",
    "gdef",
    "def",
    "let",
    "futurelet",
    "lstinputlisting",
    "verbatiminput",
    "inputminted",
    "bibliography",
    "addbibresource",
    "includegraphicsfromurl",
    "usepgflibrary",
}
_COLUMN_LAYOUT = r">{\raggedright\arraybackslash}"
_FONT_DEFINITIONS = {"ot1lmr.fd", "omllmm.fd", "omslmsy.fd", "t1lmtt.fd"}
_LAYOUT_CONDITIONALS = {
    "upquote.sty": (r"\usepackage{upquote}", ""),
    "microtype.sty": (
        r"\usepackage[]{microtype}\UseMicrotypeSet[protrusion]{basicmath}",
        "",
    ),
    "parskip.sty": (
        r"\usepackage{parskip}",
        r"\setlength{\parindent}{0pt}\setlength{\parskip}{6pt plus 2pt minus 1pt}",
    ),
    "xurl.sty": (r"\usepackage{xurl}", ""),
    "bookmark.sty": (r"\usepackage{bookmark}", r"\usepackage{hyperref}"),
    "footnotehyper.sty": (r"\usepackage{footnotehyper}", r"\usepackage{footnote}"),
}


def _braced_end(text, start):
    depth = 0
    for index in range(start, len(text)):
        if text[index] in "{}" and (index == 0 or text[index - 1] != "\\"):
            depth += 1 if text[index] == "{" else -1
            if depth == 0:
                return index + 1
    raise ValueError("Unclosed literal LaTeX argument")


def _checked_source(text, *, literal_values=None):
    """Validate active controls and remove one known lossy table layout prefix."""
    output = []
    index = 0
    math_spans = [
        match.span()
        for match in re.finditer(
            r"\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]|\$\$[\s\S]*?\$\$|"
            r"(?<!\\)\$(?:[^$\\]|\\.)*?\$",
            text,
        )
    ]
    document = re.search(r"\\begin\s*\{document\}", text)
    while index < len(text):
        if text[index] == "%":
            end = text.find("\n", index)
            end = len(text) if end < 0 else end + 1
            output.append(text[index:end])
            index = end
            continue
        if text.startswith("^^", index):
            raise ValueError("unsafe TeX character-code expansion")
        if text.startswith(_COLUMN_LAYOUT, index):
            # Pandoc 2.12 otherwise consumes a leading digit in each such cell.
            index += len(_COLUMN_LAYOUT)
            continue
        if text[index] != "\\":
            output.append(text[index])
            index += 1
            continue
        command = re.match(r"\\([A-Za-z]+|.)", text[index:], re.S)
        if command is None:
            output.append(text[index])
            index += 1
            continue
        name = command[1]
        end = index + len(command[0])
        in_preamble = document is not None and index < document.start()
        if name == "def":
            list_style = re.match(
                r"\s*\\labelenumi\s*\{\\arabic\{enumi\}\.\}", text[end:]
            )
            if list_style:
                index = end + list_style.end()
                continue
        if in_preamble and name == "def":
            layout = re.match(r"\s*\\UrlBreaks\s*\{", text[end:])
            if layout:
                start = end + layout.end() - 1
                close = _braced_end(text, start)
                body = re.sub(r"\s+", "", text[start + 1 : close - 1])
                if re.fullmatch(r"(?:\\do(?:\\.|[A-Za-z0-9]))*", body):
                    index = close
                    continue
        if in_preamble and name == "input":
            font = re.match(r"\s*\{([^{}]+)\}", text[end:])
            if font and font[1] in _FONT_DEFINITIONS:
                index = end + font.end()
                continue
        if in_preamble and name == "IfFileExists":
            arguments, cursor = [], end
            for _ in range(3):
                opening = re.match(r"\s*\{", text[cursor:])
                if opening is None:
                    break
                start = cursor + opening.end() - 1
                cursor = _braced_end(text, start)
                arguments.append(text[start + 1 : cursor - 1])
            if len(arguments) == 3 and arguments[0] in _LAYOUT_CONDITIONALS:

                def clean(value):
                    return re.sub(r"\s+", "", re.sub(r"%[^\n]*", "", value))

                expected = _LAYOUT_CONDITIONALS[arguments[0]]
                if tuple(map(clean, arguments[1:])) == tuple(map(clean, expected)):
                    index = cursor
                    continue
        if name in {"verb", "Verb"}:
            if end < len(text) and text[end] == "*":
                end += 1
            if end >= len(text) or text[end].isspace():
                raise ValueError("Invalid verbatim delimiter")
            close = text.find(text[end], end + 1)
            if close < 0:
                raise ValueError("Unclosed verbatim text")
            output.append(text[index : close + 1])
            index = close + 1
            continue
        if name == "begin":
            environment = re.match(r"\s*\{([^{}]+)\}", text[end:])
            if environment:
                env = environment[1]
                if env.casefold().startswith("filecontents"):
                    raise ValueError("forbidden file-writing LaTeX environment")
                if env in _LITERAL_ENVIRONMENTS:
                    closing = re.search(
                        r"\\end\s*\{" + re.escape(env) + r"\}", text[end:]
                    )
                    if closing is None:
                        raise ValueError("Unclosed literal LaTeX environment")
                    close = end + closing.end()
                    output.append(text[index:close])
                    index = close
                    continue
        if name.casefold() in _FORBIDDEN:
            raise ValueError(f"forbidden active LaTeX command: \\{name}")
        if name in {"url", "nolinkurl", "path", "href"}:
            argument = re.match(r"\s*\{", text[end:])
            if argument:
                opening = end + argument.end() - 1
                close = _braced_end(text, opening)
                if (
                    literal_values is not None
                    and name in {"path", "nolinkurl"}
                    and not any(start <= index < stop for start, stop in math_spans)
                ):
                    # Pandoc 2.12 silently discards \path. Keep its literal data
                    # outside TeX interpretation and restore code formatting later.
                    marker = f"ELVIALITERALPATH{len(literal_values):05d}TOKEN"
                    while marker in text:
                        marker += "X"
                    value = text[opening + 1 : close - 1]
                    literal_values[marker] = re.sub(r"\\([_%#&{}$])", r"\1", value)
                    output.append(marker)
                else:
                    output.append(text[index:close])
                index = close
                continue
        output.append(text[index:end])
        index = end
    return "".join(output)


def render_latex_citation(text):
    """Render only literal cite keys and an explicitly supplied single-page note."""
    match = re.fullmatch(r"\\cite\s*(?:\[([^\[\]]*)\]\s*)?\{([^{}]*)\}", text.strip())
    if match is None:
        return None
    keys = [key.strip() for key in match[2].split(",")]
    if not keys or any(not re.fullmatch(r"[A-Za-z0-9_:.+/-]+", key) for key in keys):
        return None
    labels = list(keys)
    if match[1] is not None:
        page = re.fullmatch(r"p\.\s*~?\s*(\d+)", match[1].strip())
        if page is None:
            return None
        labels.append("p. " + page[1])
    return "[" + ", ".join(labels) + "]"


def _inlines(nodes):
    values = []
    for node in nodes:
        kind, content = node["t"], node.get("c")
        if kind == "Str":
            value = content
        elif kind in {"Space", "SoftBreak"}:
            value = " "
        elif kind == "LineBreak":
            value = "\n"
        elif kind in {"Emph", "Strong", "Underline", "SmallCaps"}:
            value = _inlines(content)
        elif kind in {"Superscript", "Subscript", "Strikeout"}:
            marker = {"Superscript": "^", "Subscript": "_", "Strikeout": "~~"}[kind]
            value = marker + "{" + _inlines(content) + "}"
        elif kind == "Span":
            value = _inlines(content[1])
        elif kind == "Quoted":
            left, right = ("‘", "’") if content[0]["t"] == "SingleQuote" else ("“", "”")
            value = left + _inlines(content[1]) + right
        elif kind == "Math":
            delimiters = {"InlineMath": (r"\(", r"\)"), "DisplayMath": (r"\[", r"\]")}
            if content[0]["t"] not in delimiters:
                raise ValueError("Unsupported Pandoc math type: " + content[0]["t"])
            left, right = delimiters[content[0]["t"]]
            value = left + content[1] + right
        elif kind == "Code":
            value = "`" + content[1] + "`"
        elif kind in {"Link", "Image"}:
            label = _inlines(content[1])
            url, title = content[2]
            value = ("[Image: " + label + "]") if kind == "Image" else label
            if url and url != label:
                value += " (" + url + ")"
            if title:
                value += " [" + title + "]"
        elif kind == "Note":
            value = " [Footnote: " + "\n".join(_blocks(content)) + "]"
        elif kind == "Cite":
            value = _inlines(content[1])
            keys = [item["citationId"] for item in content[0]]
            absent = [key for key in keys if key not in value]
            if absent:
                value += " [citation keys: " + "; ".join(absent) + "]"
        elif kind == "RawInline":
            citation = None
            if content[0] in {"latex", "tex"}:
                _checked_source(content[1])
                citation = render_latex_citation(content[1])
            value = (
                citation
                if citation is not None
                else "[Retained " + content[0] + ": " + content[1] + "]"
            )
        else:
            raise ValueError("Unsupported Pandoc inline: " + kind)
        values.append(value)
    return "".join(values)


def _table_rows(rows):
    result = []
    for _attributes, cells in rows:
        values = []
        for _attr, _align, rowspan, colspan, blocks in cells:
            text = "\n".join(_blocks(blocks))
            if rowspan != 1 or colspan != 1:
                text = f"[rowspan={rowspan}, colspan={colspan}] " + text
            values.append(text)
        result.append(" | ".join(values))
    return result


def _table(content):
    if len(content) != 6:
        raise ValueError("Unsupported Pandoc table representation")
    _attr, caption, _columns, head, bodies, foot = content
    result = _blocks(caption[1])
    if caption[0] is not None:
        short = _inlines(caption[0])
        if short and short not in result:
            result.insert(0, short)
    result.extend(_table_rows(head[1]))
    for _attr, _row_heads, intermediate, rows in bodies:
        result.extend(_table_rows(intermediate))
        result.extend(_table_rows(rows))
    result.extend(_table_rows(foot[1]))
    return result


def _blocks(nodes):
    values = []
    for node in nodes:
        kind, content = node["t"], node.get("c")
        if kind in {"Plain", "Para"}:
            values.append(_inlines(content))
        elif kind == "Header":
            values.append("#" * content[0] + " " + _inlines(content[2]))
        elif kind == "CodeBlock":
            language = ", ".join(content[0][1])
            if language:
                values.append("Code language: " + language)
            values.append("Code:\n" + content[1])
        elif kind == "RawBlock":
            if content[0] in {"latex", "tex"}:
                _checked_source(content[1])
            values.append("Retained " + content[0] + ":\n" + content[1])
        elif kind == "Div":
            values.extend(_blocks(content[1]))
        elif kind == "BlockQuote":
            values.extend(
                "> " + text.replace("\n", "\n> ") for text in _blocks(content)
            )
        elif kind == "LineBlock":
            values.append("\n".join(_inlines(line) for line in content))
        elif kind in {"BulletList", "OrderedList"}:
            start, items = (
                (1, content) if kind == "BulletList" else (content[0][0], content[1])
            )
            for number, item in enumerate(items, start):
                prefix = "- " if kind == "BulletList" else f"{number}. "
                values.append(prefix + "\n  ".join(_blocks(item)))
        elif kind == "DefinitionList":
            for term, definitions in content:
                values.append(_inlines(term))
                for definition in definitions:
                    values.extend("  " + text for text in _blocks(definition))
        elif kind == "Table":
            values.extend(_table(content))
        elif kind == "HorizontalRule":
            values.append("---")
        elif kind == "Null":
            continue
        else:
            raise ValueError("Unsupported Pandoc block: " + kind)
    return [value for value in values if value.strip()]


def _metadata(node):
    kind, content = node["t"], node.get("c")
    if kind == "MetaInlines":
        return [_inlines(content)]
    if kind == "MetaBlocks":
        return _blocks(content)
    if kind == "MetaString":
        return [content]
    if kind == "MetaBool":
        return [str(content).lower()]
    if kind == "MetaList":
        return [text for item in content for text in _metadata(item)]
    if kind == "MetaMap":
        return [
            key + ": " + "\n".join(_metadata(value)) for key, value in content.items()
        ]
    raise ValueError("Unsupported Pandoc metadata: " + kind)


def report_paragraphs(tex_path, pandoc="pandoc") -> list[str]:
    """Return complete readable paragraphs; never compile or execute the report."""
    source = Path(tex_path).read_text(encoding="utf-8-sig")
    literal_values = {}
    checked = _checked_source(source, literal_values=literal_values)
    with tempfile.TemporaryDirectory(prefix="elvia-report-text-") as temporary:
        result = subprocess.run(
            [
                str(pandoc),
                "--from=latex",
                "--to=json",
                "--fail-if-warnings",
                "--data-dir=" + temporary,
                "--resource-path=" + temporary,
            ],
            input=checked,
            text=True,
            encoding="utf-8",
            capture_output=True,
            cwd=temporary,
            timeout=60,
            check=False,
        )
    if result.returncode:
        raise ValueError(
            f"Pandoc report conversion failed ({result.returncode}): "
            + result.stderr.strip()
        )
    if result.stderr.strip():
        raise ValueError("Pandoc report conversion warning: " + result.stderr.strip())
    try:
        ast = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("Pandoc report conversion returned invalid JSON") from exc
    if not isinstance(ast, dict) or not isinstance(ast.get("blocks"), list):
        raise ValueError("Pandoc report conversion returned an invalid document")
    paragraphs = []
    for key, value in ast.get("meta", {}).items():
        paragraphs.extend(key.capitalize() + ": " + text for text in _metadata(value))
    paragraphs.extend(_blocks(ast["blocks"]))
    for index, text in enumerate(paragraphs):
        for marker, value in literal_values.items():
            while marker in text:
                position = text.index(marker)
                # A surrounding \texttt may already supply the code delimiters.
                in_code = text[:position].count("`") % 2
                replacement = value if in_code else "`" + value + "`"
                text = text[:position] + replacement + text[position + len(marker) :]
        paragraphs[index] = text
    if not paragraphs:
        raise ValueError("Pandoc report conversion returned no report text")
    return paragraphs
