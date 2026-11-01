"""Loss-sensitive, Math-only presentation compatibility for retained report TeX.

Run after the unchanged source cleanup/equality gates.  This module only rewrites
explicit math using enumerated, content-preserving TeX rules, plus frozen source-
bound presentation overrides.  It never executes or compiles the input.  The web
renderer and its strict KaTeX gate remain unchanged.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from decimal import Decimal
from functools import cache
from pathlib import Path

_COMMAND = re.compile(r"\\([A-Za-z]+|.)", re.S)
_ACCENTS = {
    "bar",
    "overline",
    "underline",
    "hat",
    "widehat",
    "tilde",
    "widetilde",
    "vec",
    "dot",
    "ddot",
    "breve",
    "check",
    "acute",
    "grave",
    "mathring",
}
_UNARY = _ACCENTS | {
    "mathbb",
    "mathbf",
    "mathrm",
    "mathit",
    "mathsf",
    "mathtt",
    "mathcal",
    "mathfrak",
    "mathscr",
    "operatorname",
    "boldsymbol",
    "bm",
}
_TEXT = {
    "text",
    "hbox",
    "mbox",
    "textrm",
    "textnormal",
    "texttt",
    "textsf",
    "textbf",
    "textit",
    "textup",
    "textmd",
    "textsc",
    "emph",
}
_VRULE = re.compile(
    r"\\vrule\s+height\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))([a-z]+)"
    r"\s+depth\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))([a-z]+)"
    r"\s+width\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))([a-z]+)"
)
_HEX = re.compile(r"[0-9a-fA-F]{64}")


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _skip_space(text, index):
    while index < len(text) and text[index].isspace():
        index += 1
    return index


def _verbatim_end(text, command):
    index = command.end()
    if text[index : index + 1] == "*":
        index += 1
    if index >= len(text) or text[index].isspace():
        raise ValueError("Invalid literal TeX delimiter")
    end = text.find(text[index], index + 1)
    if end < 0:
        raise ValueError("Unclosed literal TeX text")
    return end + 1


def _group_end(text, opening):
    if opening >= len(text) or text[opening] != "{":
        raise ValueError("Expected a braced TeX argument")
    depth, index = 1, opening + 1
    while index < len(text):
        if text[index] == "\\":
            match = _COMMAND.match(text, index)
            index = (
                _verbatim_end(text, match)
                if match and match[1] in {"verb", "Verb"}
                else match.end()
                if match
                else index + 1
            )
            continue
        if text[index] == "%":
            end = text.find("\n", index)
            index = len(text) if end < 0 else end + 1
            continue
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    raise ValueError("Unclosed TeX group in mathematical presentation")


def _argument(text, index):
    opening = _skip_space(text, index)
    if opening >= len(text) or text[opening] != "{":
        return None
    end = _group_end(text, opening)
    return opening, end, text[opening + 1 : end - 1]


def _atom_end(text, index):
    """Consume a known one-argument command, its full argument, or one atom."""
    index = _skip_space(text, index)
    if index >= len(text):
        raise ValueError("Missing mathematical command argument")
    if text[index] == "{":
        return _group_end(text, index)
    match = _COMMAND.match(text, index)
    if match:
        end = match.end()
        if match[1] == "operatorname" and text[end : end + 1] == "*":
            end += 1
        return _atom_end(text, end) if match[1] in _UNARY else end
    if text[index] in "}^_":
        raise ValueError("Missing mathematical atom")
    return index + 1


def _delimiter_at(text, index):
    if text[index : index + 2] not in (r"\(", r"\)", r"\[", r"\]"):
        return None
    preceding, cursor = 0, index - 1
    while cursor >= 0 and text[cursor] == "\\":
        preceding += 1
        cursor -= 1
    return text[index : index + 2] if preceding % 2 == 0 else None


def math_parts(text):
    """Read complete outer spans, retaining valid nested text-box math as data."""
    start, stack, parts, index = 0, [], [], 0
    while index < len(text) - 1:
        token = _delimiter_at(text, index)
        if token is None:
            index += 1
            continue
        if token in (r"\(", r"\["):
            if not stack:
                parts.append((False, text[start:index]))
                start = index
            stack.append(token)
        elif not stack or token != (r"\)" if stack[-1] == r"\(" else r"\]"):
            raise ValueError("Unmatched or mismatched mathematical delimiter")
        else:
            stack.pop()
            if not stack:
                parts.append((True, text[start : index + 2]))
                start = index + 2
        index += 2
    if stack:
        raise ValueError("Unclosed mathematical delimiter")
    parts.append((False, text[start:]))
    return parts


def _decimal(value):
    return format(value.normalize(), "f") if value else "0"


def _tex(text, mode, rules):
    output, index = [], 0
    while index < len(text):
        if text[index] == "%":
            end = text.find("\n", index)
            end = len(text) if end < 0 else end + 1
            output.append(text[index:end])
            index = end
            continue
        if text[index] == "{":
            end = _group_end(text, index)
            output.append("{" + _tex(text[index + 1 : end - 1], mode, rules) + "}")
            index = end
            continue
        if mode == "text" and text.startswith(r"\(", index):
            closing = text.find(r"\)", index + 2)
            if closing < 0:
                raise ValueError("Unclosed inline math inside a text box")
            inner = text[index + 2 : closing]
            if r"\(" in inner or r"\[" in inner:
                raise ValueError("Unsupported deeper nesting of text-box math")
            output.append("$" + _tex(inner, "math", rules) + "$")
            rules["text_box_inline_math_delimiters"] += 1
            index = closing + 2
            continue
        if mode == "text" and text[index] == "$":
            closing = index + 1
            while closing < len(text):
                if text[closing] == "\\":
                    match = _COMMAND.match(text, closing)
                    closing = match.end() if match else closing + 1
                    continue
                if text[closing] == "$":
                    break
                closing += 1
            if closing == len(text):
                raise ValueError("Unclosed dollar math inside a text box")
            output.append("$" + _tex(text[index + 1 : closing], "math", rules) + "$")
            index = closing + 1
            continue
        match = _COMMAND.match(text, index)
        if match is None:
            output.append(text[index])
            index += 1
            continue
        name, end = match[1], match.end()
        if name in {"verb", "Verb"}:
            stop = _verbatim_end(text, match)
            output.append(text[index:stop])
            index = stop
            continue
        argument = _argument(text, end)
        if mode == "text" and name in {"ttfamily", "normalfont"}:
            wrapper = "texttt" if name == "ttfamily" else "textnormal"
            output.append("\\" + wrapper + "{" + _tex(text[end:], mode, rules) + "}")
            rules["scoped_text_font_declaration"] += 1
            break
        if name in _TEXT and argument:
            _, stop, body = argument
            command = "text" if name == "mbox" else name
            if name == "mbox":
                rules["math_text_box_alias"] += 1
            output.append("\\" + command + "{" + _tex(body, "text", rules) + "}")
            index = stop
            continue
        if name in {"rlap", "llap", "clap"} and argument:
            _, stop, body = argument
            nested = _COMMAND.match(body, _skip_space(body, 0))
            inner = (
                _argument(body, nested.end())
                if nested and nested[1] == "ensuremath"
                else None
            )
            if inner and not body[inner[1] :].strip():
                output.append(
                    "\\math" + name + "{" + _tex(inner[2], "math", rules) + "}"
                )
                rules["math_overlay_ensuremath"] += 1
                index = stop
                continue
        if name == "ensuremath" and argument:
            _, stop, body = argument
            inner = _tex(body, "math", rules)
            output.append("{" + inner + "}" if mode == "math" else "$" + inner + "$")
            rules["ensuremath_in_known_mode"] += 1
            index = stop
            continue
        if (
            mode == "text"
            and name in {"path", "nolinkurl", "seqsplit"}
            and argument
            and _HEX.fullmatch(argument[2])
        ):
            _, stop, body = argument
            output.append(
                "{" + body + "}" if name == "seqsplit" else r"\texttt{" + body + "}"
            )
            rules["literal_digest_typography"] += 1
            index = stop
            continue
        if mode == "math" and name in _ACCENTS:
            following = _skip_space(text, end)
            inner = _COMMAND.match(text, following)
            if inner and inner[1] in _UNARY:
                stop = _atom_end(text, following)
                output.append(
                    match[0] + "{" + _tex(text[following:stop], "math", rules) + "}"
                )
                rules["brace_compound_accent_argument"] += 1
                index = stop
                continue
        if mode == "math" and name == "vrule":
            rule = _VRULE.match(text, index)
            if (
                rule
                and rule[2] == rule[4] == rule[6]
                and rule[2] in {"ex", "em", "pt", "mu"}
            ):
                height, depth, width = (Decimal(rule[n]) for n in (1, 3, 5))
                if height + depth < 0 or width < 0:
                    raise ValueError("Negative rule geometry cannot be converted")
                unit = rule[2]
                raise_by = "[" + _decimal(-depth) + unit + "]" if depth else ""
                output.append(
                    r"\rule"
                    + raise_by
                    + "{"
                    + rule[5]
                    + unit
                    + "}{"
                    + _decimal(height + depth)
                    + unit
                    + "}"
                )
                rules["explicit_rule_geometry"] += 1
                index = rule.end()
                continue
        if mode == "math" and name == "lhook":
            arrow = re.match(r"\s*\\joinrel\s*\\longrightarrow\b", text[end:])
            if arrow:
                output.append(r"\xhookrightarrow{}")
                rules["long_hook_arrow_alias"] += 1
                index = end + arrow.end()
                continue
        output.append(match[0])
        index = end
    return "".join(output)


def _row_tags(text):
    """Recognize literal outer tag commands, never row breaks or quoted text."""
    tags, index = [], 0
    while index < len(text):
        if text[index] == "%":
            end = text.find("\n", index)
            index = len(text) if end < 0 else end + 1
            continue
        if text[index] == "{":
            index = _group_end(text, index)
            continue
        command = _COMMAND.match(text, index)
        if command is None:
            index += 1
            continue
        end = command.end()
        if command[1] in {"verb", "Verb"}:
            index = _verbatim_end(text, command)
            continue
        if command[1] == "tag":
            starred = text[end : end + 1] == "*"
            argument = _argument(text, end + int(starred))
            if not argument or not re.fullmatch(r"[A-Za-z0-9.:+-]+", argument[2]):
                return []  # Leave unfamiliar tags to the unchanged strict gate.
            tags.append((index, argument[1], argument[2], starred))
            index = argument[1]
        else:
            index = end
    return tags


def _normalize_math(text, rules):
    # Pandoc lowers align to aligned while retaining each source row's tag.
    # KaTeX allows one outer tag, so keep all labels visibly on their own rows.
    tags = _row_tags(text) if text.lstrip().startswith(r"\begin{aligned}") else []
    if len(tags) > 1 and text.lstrip().startswith(r"\begin{aligned}"):
        parts, start = [], 0
        for opening, stop, label, starred in tags:
            rules["aligned_row_label_preserved"] += 1
            label = label if starred else "(" + label + ")"
            parts.extend((text[start:opening], r"\qquad\text{" + label + "}"))
            start = stop
        text = "".join(parts) + text[start:]
    return _tex(text, "math", rules)


@cache
def _overrides():
    path = Path(__file__).with_name("math2025-presentation-overrides.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("format_version") != 1:
        raise ValueError("Unsupported mathematical presentation override version")
    return data["cases"]


def format_publication_text(
    text, *, case_id=None, source_report_sha256=None, audit=None
):
    """Normalize explicit math and append a frozen before/after audit if changed."""
    if not isinstance(text, str):
        raise TypeError("Publication text must be a string")
    if text.startswith("Code:\n"):
        return text
    original, rules, override_reason = text, Counter(), None
    for row in _overrides().get(case_id, []):
        if row["before_sha256"] != digest(row["before"]):
            raise ValueError("Presentation override has an invalid frozen text hash")
        if text != row["before"]:
            continue
        if source_report_sha256 != row["report_tex_sha256"]:
            raise ValueError(
                "Presentation override does not match its source report hash"
            )
        text, override_reason = row["after"], row["reason"]
        rules["reviewed_source_bound_notation"] += 1
        break
    parts = math_parts(text)
    result = "".join(
        span[:2] + _normalize_math(span[2:-2], rules) + span[-2:] if is_math else span
        for is_math, span in parts
    )
    after_parts = math_parts(result)
    before_math = [span for flag, span in parts if flag]
    after_math = [span for flag, span in after_parts if flag]
    if len(before_math) != len(after_math):
        raise ValueError(
            "Presentation conversion changed the outer math expression count"
        )
    # All transformations above are a closed set. Unknown macros survive and
    # must still pass the unchanged strict KaTeX/publication checker afterward.
    if result != original and audit is not None:
        audit.append(
            {
                "before_sha256": digest(original),
                "after_sha256": digest(result),
                "before": original,
                "after": result,
                "rules": dict(rules),
                "source_report_sha256": source_report_sha256,
                "outer_math_spans_before_normalization": len(before_math),
                "outer_math_spans_after_normalization": len(after_math),
                "pre_compatibility_math_sequence_sha256": digest(
                    json.dumps(before_math, ensure_ascii=False)
                ),
                "post_compatibility_math_sequence_sha256": digest(
                    json.dumps(after_math, ensure_ascii=False)
                ),
                "pre_compatibility_sequence_basis": "after frozen notation override"
                if override_reason
                else "original text",
                **(
                    {"reviewed_override_reason": override_reason}
                    if override_reason
                    else {}
                ),
            }
        )
    return result


def format_publication_data(
    value, *, case_id=None, source_report_sha256=None, audit=None, location=""
):
    """Apply the formatter to report/problem data while preserving its structure."""
    if isinstance(value, str):
        rows = []
        result = format_publication_text(
            value,
            case_id=case_id,
            source_report_sha256=source_report_sha256,
            audit=rows,
        )
        if audit is not None:
            audit.extend({"location": location, **row} for row in rows)
        return result
    if isinstance(value, list):
        return [
            format_publication_data(
                item,
                case_id=case_id,
                source_report_sha256=source_report_sha256,
                audit=audit,
                location=f"{location}[{i}]",
            )
            for i, item in enumerate(value)
        ]
    if isinstance(value, dict):
        return {
            key: format_publication_data(
                item,
                case_id=case_id,
                source_report_sha256=source_report_sha256,
                audit=audit,
                location=f"{location}.{key}" if location else key,
            )
            for key, item in value.items()
        }
    return value


def _tex_whitespace(text):
    """Whitespace/comments only; escaped percent signs remain meaningful data."""
    index = 0
    while index < len(text):
        if text[index].isspace():
            index += 1
        elif text[index] == "%":
            end = text.find("\n", index)
            index = len(text) if end < 0 else end + 1
        else:
            return False
    return True


def _pdf_single_aligned_tag(tex, label):
    """Move one trailing outer-aligned tag to its enclosing display, byte intact."""
    stack, tags, outer_start, outer_end, index = [], [], None, None, 0
    while index < len(tex):
        if tex[index] == "%":
            end = tex.find("\n", index)
            index = len(tex) if end < 0 else end + 1
            continue
        if tex[index] == "{":
            index = _group_end(tex, index)
            continue
        command = _COMMAND.match(tex, index)
        if command is None:
            index += 1
            continue
        name, end = command[1], command.end()
        if name in {"verb", "Verb"}:
            index = _verbatim_end(tex, command)
            continue
        argument = _argument(tex, end + int(tex[end : end + 1] == "*"))
        if name in {"begin", "end"}:
            argument = _argument(tex, end)
            if argument is None:
                return tex
            environment = argument[2]
            if name == "begin":
                if not stack:
                    if outer_start is not None or environment != "aligned":
                        return tex
                    outer_start = (index, argument[1])
                stack.append(environment)
            else:
                if not stack or stack[-1] != environment:
                    return tex
                stack.pop()
                if not stack:
                    outer_end = (index, argument[1])
            index = argument[1]
            continue
        if name == "tag":
            if argument is None:
                return tex
            tags.append((index, argument[1], argument[2], tuple(stack)))
            index = argument[1]
            continue
        index = end
    if stack or outer_start is None or outer_end is None or len(tags) != 1:
        return tex
    start, stop, actual_label, environments = tags[0]
    if (
        actual_label != label
        or environments != ("aligned",)
        or not _tex_whitespace(tex[: outer_start[0]])
        or not _tex_whitespace(tex[outer_end[1] :])
        or not _tex_whitespace(tex[stop : outer_end[0]])
    ):
        return tex
    # Place it before trailing comments, preserving its original * and label.
    return (
        tex[:start] + tex[stop : outer_end[1]] + tex[start:stop] + tex[outer_end[1] :]
    )


def _pdf_math_typography(tex, kind):
    """Known PDF glyph/font aliases, with math and literal text kept distinct."""
    replacements = {
        "game_exact_glyph": (
            "Game",
            r'\mathord{\text{\fontspec{DejaVu Serif}\char"2141}}',
        ),
        "triangledown_exact_glyph": (
            "triangledown",
            r'\mathord{\text{\fontspec{DejaVu Serif}\char"25BF}}',
        ),
        "setminus_typography": ("setminus", r"\smallsetminus"),
    }
    if kind not in replacements and kind != "operator_gamma_math_font":
        raise ValueError("Unknown reviewed PDF typography rule")
    output, count, index = [], 0, 0
    while index < len(tex):
        if tex[index] == "%":
            end = tex.find("\n", index)
            end = len(tex) if end < 0 else end + 1
            output.append(tex[index:end])
            index = end
            continue
        command = _COMMAND.match(tex, index)
        if command is None:
            output.append(tex[index])
            index += 1
            continue
        name, end = command[1], command.end()
        if name in {"verb", "Verb"}:
            stop = _verbatim_end(tex, command)
            output.append(tex[index:stop])
            index = stop
            continue
        argument = _argument(tex, end)
        if name in _TEXT and argument:
            output.append(tex[index : argument[1]])
            index = argument[1]
            continue
        if (
            kind == "operator_gamma_math_font"
            and name == "operatorname"
            and argument
            and argument[2] == r"R\Gamma"
        ):
            output.append(r"\operatorname{R\symit{\Gamma}}")
            count += 1
            index = argument[1]
            continue
        if kind in replacements and name == replacements[kind][0]:
            output.append(replacements[kind][1])
            count += 1
        else:
            output.append(command[0])
        index = end
    return "".join(output), count


def _pdf_apply_rules(source, rules):
    preamble, separator, body = source.partition(r"\begin{document}")
    if not separator:
        raise ValueError("Reviewed PDF source has no document boundary")
    applied = []
    for rule in rules:
        kind, count, parts = rule["kind"], 0, []
        for is_math, span in math_parts(body):
            if not is_math:
                parts.append(span)
                continue
            tex = span[2:-2]
            if kind == "single_aligned_tag":
                transformed = (
                    _pdf_single_aligned_tag(tex, rule["label"])
                    if span.startswith(r"\[")
                    else tex
                )
                count += int(transformed != tex)
            else:
                transformed, changed = _pdf_math_typography(tex, kind)
                count += changed
            parts.append(span[:2] + transformed + span[-2:])
        if count != rule["expected_occurrences"]:
            raise ValueError("Reviewed PDF rule does not match its frozen occurrences")
        body = "".join(parts)
        applied.append({**rule, "actual_occurrences": count})
    return preamble + separator + body, applied


@cache
def _pdf_catalog():
    path = Path(__file__).with_name("math2025-pdf-presentation.json")
    catalog = json.loads(path.read_text(encoding="utf-8"))
    if catalog.get("format_version") != 1:
        raise ValueError("Unsupported reviewed PDF presentation catalog")
    before, after = {}, {}
    for case_id, row in catalog["cases"].items():
        for field in ("before_sha256", "after_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", row[field]):
                raise ValueError("Invalid reviewed PDF source hash")
        if row["before_sha256"] in before or row["after_sha256"] in after:
            raise ValueError("Duplicate reviewed PDF source binding")
        entry = {"case_id": case_id, **row}
        before[row["before_sha256"]] = entry
        after[row["after_sha256"]] = entry
    return before, after


def apply_pdf_presentation(source):
    """Apply only the nine reviewed, whole-safe-TeX-hash-bound PDF repairs."""
    before, _ = _pdf_catalog()
    row = before.get(digest(source))
    if row is None:
        return source
    result, _ = _pdf_apply_rules(source, row["rules"])
    if digest(result) != row["after_sha256"]:
        raise ValueError("Reviewed PDF typography result differs from its frozen hash")
    return result


def pdf_presentation_audit(source):
    """Describe the actual reviewed rules for pre- or post-rendered safe TeX."""
    before, after = _pdf_catalog()
    source_hash = digest(source)
    row = before.get(source_hash) or after.get(source_hash)
    if row is None:
        return {
            "format_version": 1,
            "changed": False,
            "before_sha256": source_hash,
            "after_sha256": source_hash,
            "rules": [],
        }
    if source_hash == row["before_sha256"]:
        apply_pdf_presentation(source)  # Validate rule counts and the result hash.
    return {
        "format_version": 1,
        "changed": True,
        "case_id": row["case_id"],
        "before_sha256": row["before_sha256"],
        "after_sha256": row["after_sha256"],
        "rules": [
            {**rule, "actual_occurrences": rule["expected_occurrences"]}
            for rule in row["rules"]
        ],
    }


def render_publication_tex(paragraphs, *, renderer):
    """Use the existing report template plus the Math-only package dependency.

    mathtools supplies the exact math-overlay and extensible hook-arrow commands
    also supported by the pinned KaTeX renderer. Load it before unicode-math.
    The shared renderer and previous publication collections are not modified.
    """
    source = renderer(paragraphs)
    preamble, separator, body = source.partition(r"\begin{document}")
    if not separator:
        raise ValueError("The publication renderer returned no document boundary")
    packages = r"\usepackage{amsmath,amssymb,fontspec,unicode-math,xurl,hyperref}"
    if preamble.count(packages) != 1:
        raise ValueError("Math template package list changed; review dependencies")
    preamble = preamble.replace(
        packages,
        r"\usepackage{amsmath,amssymb,mathtools,fontspec,unicode-math,xurl,hyperref}",
        1,
    )
    return apply_pdf_presentation(preamble + separator + body)
