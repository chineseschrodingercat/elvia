"""Readable source locators; archival offsets remain in the retained record."""

import re

_PAGE_FIELDS = {
    "pdf": "PDF pages",
    "printed": "printed pages",
    "physical": "physical pages",
    "physical pdf": "physical PDF pages",
    "": "pages",
    "primary pdf": "primary PDF pages",
    "publisher pdf": "publisher PDF pages",
    "author v2 pdf": "author v2 PDF pages",
    "dependency": "dependency pages",
    "related": "related pages",
    "counterevidence": "counterevidence pages",
    "proof": "proof pages",
    "statement": "statement pages",
    "reference": "reference pages",
    "reference printed": "reference printed pages",
}
_FIELD_PATTERN = (
    r"printed pages same|pdf sha256|"
    r"(?:(?:physical pdf|primary pdf|publisher pdf|author v2 pdf|reference printed|"
    r"pdf|printed|physical|dependency|related|counterevidence|proof|statement|"
    r"reference) )?pages?|"
    r"author tex lines?\. [a-z0-9 _-]+|"
    r"(?:(?:related older tex|source code|source tex|author tex|tex|source|text|"
    r"exact step|decisive) )?lines?(?: (?:1|one) based)?|"
    r"(?:source |tex )?files?|reference pdf|version|tex labels?|"
    r"claim locations?|source locations?|paper location|precise anchors?|"
    r"exact locators?|"
    r"source references?|dependent results|dependency proposition|reference equations?|"
    r"labels?|anchors?|primary|locators?|locations?|claims?|items?|statements?|"
    r"objects?|"
    r"details|headings?|failed step|paragraphs?|"
    r"sections?|lemmas?|theorems?|propositions?|equations?|definitions?|remarks?|"
    r"tables?|figures?|appendix|proof|application|code|source|supplement|"
    r"author supplement"
)
_FIELDS = re.compile(r"(?<![\w./+-])(?P<field>" + _FIELD_PATTERN + r")\s*:\s*", re.I)
_FILE = re.compile(r"[^\s;,]+\.(?:tex|py|c|cpp|h|hpp|jl|m|js|ts|rs|r|sh|pdf)\b", re.I)
_NUMBER_LIST = r"\d+(?:\s*[-–]\s*\d+)?(?:\s*[,;]\s*\d+(?:\s*[-–]\s*\d+)?)*"


def _pages(values):
    """Merge only explicitly listed numeric page intervals."""
    ranges = []
    for value in values:
        if not re.fullmatch(
            r"\d+(?:\s*[-–]\s*\d+)?(?:\s*[,;]\s*\d+(?:\s*[-–]\s*\d+)?)*", value
        ):
            return "; ".join(dict.fromkeys(values))
        for item in re.split(r"\s*[,;]\s*", value):
            ends = re.split(r"\s*[-–]\s*", item)
            start, end = int(ends[0]), int(ends[-1])
            if start > end:
                return "; ".join(dict.fromkeys(values))
            ranges.append((start, end))
    merged = []
    for start, end in sorted(set(ranges)):
        if merged and start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    return "; ".join(
        str(start) if start == end else f"{start}–{end}" for start, end in merged
    )


def source_location(value):
    """Render bounded importer fields without inventing source correspondences.

    Consecutive page fields combine, but a claim/anchor starts a new group. A
    named code or TeX file retains its lines; unbound extraction offsets do not
    become article text lines. Unstructured locators keep their wording.
    """
    text = " ".join(str(value or "").split()).strip()
    matches = list(_FIELDS.finditer(text))
    if not matches:
        return text or "Not available"
    prefix = text[: matches[0].start()].strip(" ;,.")
    if prefix.lower() in {"source", "source."}:
        prefix = ""
    fields = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        fields.append(
            (
                match["field"].lower(),
                text[match.end() : end].strip(" ;,."),
                match["field"],
            )
        )
    parts = [{"text": prefix}] if prefix else []
    named_file = parts[0] if prefix and _FILE.search(prefix) else None
    source_prefix = "" if prefix else "Article "
    file_run = 0

    def append_text(item):
        if item and (not parts or parts[-1].get("text") != item):
            parts.append({"text": item})

    def append_range(label, item):
        if parts and parts[-1].get("label") == label:
            parts[-1]["values"].append(item)
        else:
            parts.append({"label": label, "values": [item]})

    for field, item, original_field in fields:
        if not item:
            continue
        is_file = bool(re.fullmatch(r"(?:source |tex )?files?", field)) or field in {
            "source",
            "code",
            "reference pdf",
        }
        file_run = file_run + 1 if is_file else 0
        if field == "printed pages same" and item.lower() in {"true", "false"}:
            continue
        if field == "pdf sha256" and re.fullmatch(r"[a-f0-9]{64}", item, re.I):
            continue
        page = re.fullmatch(r"(?:(.*?) )?pages?", field)
        if page and (page.group(1) or "") in _PAGE_FIELDS:
            kind = page.group(1) or ""
            label = _PAGE_FIELDS[kind]
            if kind.startswith(("reference", "publisher", "author")):
                label = label[0].upper() + label[1:]
            else:
                label = source_prefix + label
            append_range(label, item)
            continue
        if is_file:
            append_text("Reference PDF: " + item if field == "reference pdf" else item)
            if field == "reference pdf" or re.search(r"\bsupplement", item, re.I):
                source_prefix = ""
            # Consecutive file arrays do not establish which file owns later lines.
            named_file = parts[-1] if _FILE.search(item) and file_run == 1 else None
            continue
        nested_tex = re.fullmatch(
            r"author tex lines?\. ([a-z0-9 _-]+)", original_field, re.I
        )
        if nested_tex or re.fullmatch(
            r"(?:(?:related older tex|source code|source tex|author tex|tex|source|"
            r"text|exact step|decisive) )?lines?(?: (?:1|one) based)?",
            field,
        ):
            if named_file is not None:
                named_file.setdefault("lines", []).append(item)
            elif field.startswith(("source line", "exact step", "decisive")):
                # Drop only the numeric offset, never unrecognized following prose.
                remainder = re.sub(r"^" + _NUMBER_LIST, "", item).strip(" ;,.")
                append_text(remainder)
            else:
                label = (
                    "TeX lines"
                    if "tex" in field
                    else "Code lines"
                    if "code" in field
                    else "Text lines"
                )
                if field.startswith("related older"):
                    label = "Earlier TeX lines"
                if nested_tex:
                    label = "TeX lines (" + nested_tex[1] + ")"
                append_range(label, item)
            continue
        if re.fullmatch(
            r"sections?|lemmas?|theorems?|propositions?|equations?|definitions?|"
            r"remarks?|tables?|figures?|appendix|reference equations?|"
            r"dependency proposition",
            field,
        ):
            label = field[0].upper() + field[1:]
            append_text(
                item if item.lower().startswith(field + " ") else label + " " + item
            )
        elif field.startswith("tex label"):
            append_text("TeX label " + item)
        elif field in {
            "proof",
            "application",
            "supplement",
            "author supplement",
            "version",
        }:
            append_text(field.capitalize() + ": " + item)
            if field in {"supplement", "author supplement", "version"}:
                source_prefix = ""
                named_file = parts[-1] if _FILE.search(item) else None
        else:
            append_text(item)
    rendered = []
    for part in parts:
        if "label" in part:
            rendered.append(part["label"] + ": " + _pages(part["values"]))
        else:
            item = part["text"]
            if part.get("lines"):
                item += ", lines " + _pages(part["lines"])
            rendered.append(item)
    return "; ".join(rendered) or "Not available"
