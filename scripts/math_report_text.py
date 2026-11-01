"""Read accepted mathematical reports as data, without compiling their TeX.

The existing report reader owns the active-command checks and loss-sensitive
Pandoc AST conversion.  This adapter accepts the in-memory source used by the
Math importer and handles the explicit Figure node introduced by newer Pandoc
versions.  Warnings, malformed nodes and unrecognized AST kinds still fail.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
from pathlib import Path

_READER_PATH = Path(__file__).with_name("icml_report_text.py")
_SPEC = importlib.util.spec_from_file_location("_elvia_math_base_reader", _READER_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError("The existing loss-sensitive report reader is unavailable")
_reader = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_reader)


def _source_text(tex: str | os.PathLike[str]) -> str:
    """Strings are source text; explicit path objects request a UTF-8 file read."""
    if isinstance(tex, os.PathLike):
        return Path(tex).read_text(encoding="utf-8-sig")
    if not isinstance(tex, str):
        raise TypeError("A report must be TeX source text or an explicit path object")
    return tex.removeprefix("\ufeff")


def _compatible_ast(value):
    """Lower a modern Figure to a Div while preserving all caption/body text."""
    if isinstance(value, list):
        return [_compatible_ast(item) for item in value]
    if not isinstance(value, dict):
        return value
    if value.get("t") == "Figure":
        content = value.get("c")
        if not isinstance(content, list) or len(content) != 3:
            raise ValueError("Unsupported Pandoc figure representation")
        attributes, caption, body = content
        if not isinstance(caption, list) or len(caption) != 2:
            raise ValueError("Unsupported Pandoc figure caption")
        short, long = caption
        if not isinstance(body, list) or not isinstance(long, list):
            raise ValueError("Unsupported Pandoc figure content")
        blocks = list(body)
        if short is not None:
            if not isinstance(short, list):
                raise ValueError("Unsupported Pandoc short figure caption")
            blocks.append({"t": "Para", "c": short})
        blocks.extend(long)
        return _compatible_ast({"t": "Div", "c": [attributes, blocks]})
    return {key: _compatible_ast(item) for key, item in value.items()}


def report_paragraphs(tex: str | os.PathLike[str], pandoc="pandoc") -> list[str]:
    """Return complete readable paragraphs from source text or an explicit Path.

    Only stdin is passed to Pandoc.  It receives no source directory, filters,
    bibliography or author program.  The checked reader rejects file access and
    dynamic/execution commands before the parser starts; unknown raw TeX stays
    visible as data.  This is not an OS-level network isolation guarantee.
    """
    source = _source_text(tex)
    literal_values: dict[str, str] = {}
    checked = _reader._checked_source(source, literal_values=literal_values)
    with tempfile.TemporaryDirectory(prefix="elvia-math-report-text-") as temporary:
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
    ast = _compatible_ast(ast)
    paragraphs = []
    for key, value in ast.get("meta", {}).items():
        paragraphs.extend(
            key.capitalize() + ": " + text for text in _reader._metadata(value)
        )
    paragraphs.extend(_reader._blocks(ast["blocks"]))
    for index, text in enumerate(paragraphs):
        for marker, value in literal_values.items():
            while marker in text:
                position = text.index(marker)
                in_code = text[:position].count("`") % 2
                replacement = value if in_code else "`" + value + "`"
                text = text[:position] + replacement + text[position + len(marker) :]
        paragraphs[index] = text
    if not paragraphs:
        raise ValueError("Pandoc report conversion returned no report text")
    return paragraphs
