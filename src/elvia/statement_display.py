"""Conservative statement excerpts from already retained, source-bound prose.

This module does not reconstruct a theorem from its proof or counterexample.
The caller validates the note's record/source binding. A curated ``statement``
is a complete presentation override; otherwise only explicitly headed source
statements can supplement the unchanged claim. Ambiguous report structure is
left for curation. No TeX is executed, expanded or interpreted as a document.
"""

import re
from collections.abc import Mapping

_SOURCE_TITLES = {
    "original claim",
    "original claims",
    "original statement",
    "original hypotheses",
    "original assumptions",
    "original conditions",
    "original claim and assumptions",
    "original claim and hypotheses",
    "original statement and hypotheses",
    "source claim",
    "source claims",
    "source statement",
    "source hypotheses",
    "source assumptions",
    "source conditions",
    "source claim and assumptions",
    "source claim and hypotheses",
    "source claim and location",
    "source claims and locations",
    "claim in the source",
    "claim and location",
    "location and claim",
}
_OTHER_ROLES = {
    "analysis",
    "proof",
    "verification",
    "counterexample",
    "witness",
    "repair",
    "proposed correction",
    "possible revision",
    "finding and scope",
}
_UNSAFE_CONTEXT = re.compile(
    r"\b(?:counterexamples?|witness(?:es)?|checks?|verification|analysis|proof|"
    r"repairs?|corrections?|revisions?|examples?|counterevidence|scope|impact)\b",
    re.I,
)
_TEX_HEADING = re.compile(
    r"\\(section|subsection|subsubsection|paragraph|subparagraph)\*?"
    r"\s*\{([^{}\n]+)\}\s*"
)
_DEPTHS = {
    "section": 1,
    "subsection": 2,
    "subsubsection": 3,
    "paragraph": 4,
    "subparagraph": 5,
}
_PROBLEM = re.compile(
    r"^(?P<kind>Problem|Finding|P|F)\s*(?P<number>\d+)"
    r"(?P<letter>[a-z]?)(?!\w)(?P<tail>.*)",
    re.I | re.S,
)


def _paragraphs(value):
    if not isinstance(value, (list, tuple)):
        return []
    return [text.strip() for text in value if isinstance(text, str) and text.strip()]


def _unique(values):
    result, seen = [], set()
    for text in values:
        key = " ".join(text.split())
        if key not in seen:
            seen.add(key)
            result.append(text)
    return result


def _title(text):
    text = re.sub(r"^\d+(?:\.\d+)*[.):]?\s+", "", text.strip())
    text = re.sub(r"\s*\(paraphrase\)\s*$", "", text, flags=re.I)
    return " ".join(text.rstrip(" .:").casefold().split())


def _heading(text):
    markdown = re.fullmatch(r"(#{1,6})\s+([^\n]+)", text)
    if markdown:
        return len(markdown[1]), markdown[2].rstrip(" #")
    tex = _TEX_HEADING.fullmatch(text)
    if tex:
        return _DEPTHS[tex[1]], tex[2]
    if _title(text) in _SOURCE_TITLES | _OTHER_ROLES:
        return 6, text
    return None


def _marker(text):
    heading = _heading(text)
    match = _PROBLEM.match(heading[1] if heading else text)
    if match is None:
        return None
    if not heading and (
        match["kind"].casefold() not in {"problem", "finding"}
        or not re.match(r"^\s*[:.(\[–—-]", match["tail"])
    ):
        return None
    return (int(match["number"]), match["letter"].casefold()), (
        heading[0] if heading else 1
    )


def _identity(value):
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"(?:Problem|Finding|P|F)\s*(\d+)([a-z]?)", value, re.I)
    return (int(match[1]), match[2].casefold()) if match else None


def _raw_structure(text):
    return re.match(r"(?:Retained (?:latex|tex):|\\(?:begin|end)\s*\{)", text)


def _source_sections(paragraphs):
    """Read explicit role blocks, never the next proof or a nested repair block."""
    result, ancestors = [], []
    active = False
    for text in paragraphs:
        if _marker(text):
            break
        heading = _heading(text)
        if heading:
            depth, title = heading
            while ancestors and ancestors[-1][0] >= depth:
                ancestors.pop()
            blocked = bool(_UNSAFE_CONTEXT.search(title)) or any(
                parent[1] for parent in ancestors
            )
            ancestors.append((depth, blocked))
            active = not blocked and _title(title) in _SOURCE_TITLES
        elif _raw_structure(text):
            # A retained raw environment has no proven statement/problem boundary.
            break
        elif active:
            result.append(text)
    return result


def _report_section(problem, note):
    """Require a unique exact finding identity and complete numbered mapping."""
    if not isinstance(note, Mapping):
        return []
    members = note.get("problems")
    if not isinstance(members, list) or not problem.get("id"):
        return []
    matches = [
        index
        for index, item in enumerate(members)
        if isinstance(item, Mapping) and item.get("id") == problem["id"]
    ]
    if len(matches) != 1:
        return []
    position = matches[0]
    bound = members[position]
    if any(
        problem.get(key) != bound.get(key) for key in ("claim", "source_finding_id")
    ):
        return []
    expected = []
    for item in members:
        if not isinstance(item, Mapping):
            return []
        # An explicit source identity must not silently fall back to UI order.
        identity = _identity(item.get("source_finding_id", item.get("id")))
        if identity is None or identity in expected:
            return []
        expected.append(identity)
    report = _paragraphs(note.get("report"))
    if any(_raw_structure(text) for text in report):
        return []
    starts = [
        (index, marker)
        for index, text in enumerate(report)
        if (marker := _marker(text)) is not None
    ]
    if [marker[0] for _, marker in starts] != expected:
        return []
    start, (_, depth) = starts[position]
    ancestors = []
    for text in report[:start]:
        heading = _heading(text)
        if heading:
            while ancestors and ancestors[-1][0] >= heading[0]:
                ancestors.pop()
            ancestors.append(heading)
    if _heading(report[start]):
        ancestors = [heading for heading in ancestors if heading[0] < depth]
    if any(_UNSAFE_CONTEXT.search(title) for _, title in ancestors):
        return []
    end = starts[position + 1][0] if position + 1 < len(starts) else len(report)
    for index in range(start + 1, end):
        heading = _heading(report[index])
        if heading and heading[0] <= depth:
            end = index
            break
    return report[start + 1 : end]


def verification_assumptions(problem):
    """Keep unclassified legacy conditions available to the proof renderer.

    Some importers populated ``assumptions`` from a witness or a check. Moving
    them to the original statement would assert an unsupported source role.
    Return their complete paragraphs so the caller can preserve them in Proof.
    """
    if problem.get("assumptions_role") == "source":
        return []
    return _paragraphs(problem.get("assumptions"))


def statement_paragraphs(problem, note=None):
    """Return faithful paragraphs; leave incomplete or ambiguous claims intact.

    ``statement`` is a curated source-bound override, including its conditions.
    Legacy ``claim`` paragraphs remain unchanged when no override is present.
    Only ``assumptions_role='source'`` confirms standalone assumptions as source
    premises. Other assumptions remain available through verification_assumptions.
    Whole source-role paragraphs may be recovered from this finding's analysis,
    or from the note's report when its numbered correspondence is unambiguous.
    """
    override = _paragraphs(problem.get("statement"))
    if override:
        return _unique(override)
    source_assumptions = (
        _paragraphs(problem.get("assumptions"))
        if problem.get("assumptions_role") == "source"
        else []
    )
    return _unique(
        source_assumptions
        + _paragraphs(problem.get("claim"))
        + _source_sections(_paragraphs(problem.get("analysis")))
        + _source_sections(_report_section(problem, note))
    )
