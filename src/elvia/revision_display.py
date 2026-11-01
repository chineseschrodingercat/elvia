"""Display existing problem-bound repair proposals without inventing a solution."""

import re

_BOILERPLATE = (
    "A proposed correction is retained where stated; independent verification "
    "and author adoption remain unestablished."
)

_PROPOSAL = re.compile(
    r"\b(?:repair|correction|revision|fix)\s+"
    r"(?:is\s+to|would\s+be\s+to|consists?\s+of|"
    r"requires?\s+(?:adding|replacing|restricting|correcting|changing|removing|"
    r"retaining|specifying|stating|inserting|recomputing|renormalizing|swapping)|"
    r"(?:must|should|needs?\s+to)\s+(?:add|replace|restrict|correct|change|remove|"
    r"retain|specify|state|insert|recompute|renormalize|swap)|"
    r"(?:could|may|can|would)\s+(?:replace|restrict|add|remove|change|retain|"
    r"state|specify|evaluate|correct|bound|require|insert|distinguish|exclude)|"
    r"(?:can\s+be|is)\s+(?:obtained|achieved|made)\s+by|using|by)\b"
    r"|\b(?:repair|correction|revision|fix)"
    r"(?:\s+and\s+(?:limits?|scope|counterevidence|impact)|\s+boundary)?"
    r"\s*(?:is\s+proved\s*)?[:.]\s*"
    r"(?:use|choose|replace|restrict|add|remove|change|retain|state|specify|"
    r"evaluate|correct|bound|prove|recompute|require|insert|distinguish|exclude|"
    r"supply|assume|define|normalize|separate|delete|count|introduce)\b"
    r"|\b(?:changing|replacing|restricting|adding|removing|correcting|inserting|"
    r"separating|imposing|renormalizing|reversing|swapping|strengthening|weakening)"
    r"\b[^.]{0,450}"
    r"\b(?:is\s+(?:a\s+)?(?:plausible\s+)?(?:local\s+)?repair|"
    r"repairs?|corrects?|restores?|removes?\s+the\s+"
    r"(?:(?:first|second|third|demonstrated)\s+)?(?:obstruction|contradiction)|"
    r"preserves?\s+the\s+claimed)\b"
    r"|\b(?:delete|remove)\s+(?:that|this|the\s+(?:printed|displayed|unsupported))"
    r"\s+(?:claim|assertion|statement)\b"
    r"|\breplace\s+(?:Eq\.?|Equation|Lemma|Theorem|Proposition|"
    r"the\s+(?:printed|displayed|original)\s+(?:formula|identity|claim|statement))"
    r"[^.]{0,180}\b(?:with|by)\b"
    r"|\breplace\s+(?:the|that|this)\s+[^.]{0,60}"
    r"\b(?:formula|identity|equality|assertion|statement|condition|coefficient|"
    r"sign|term|factor|exponent|bound)\s+(?:with|by)\b"
    r"|\binsert\b[^.]{0,100}\bin\s+(?:that|the\s+printed|the\s+displayed)\s+"
    r"(?:formula|identity|equation)\b"
    r"|\b(?:should|must)\s+be\s+(?:replaced|restricted|corrected|rewritten)\s+"
    r"(?:by|with|to|as)\b"
    r"|\b(?:formula|representation|statement|display)\s+(?:must|should)\s+read\b"
    r"|\b(?:gives?|yields?|proves?|obtain(?:s)?)\s+the\s+corrected\s+"
    r"(?:local\s+)?(?:formula|identity|statement|system|equation|bound|estimate|"
    r"expression)\b"
    r"|\b(?:the\s+)?correct(?:ed)?\s+(?:local\s+)?"
    r"(?:formula|identity|statement|system|equation|"
    r"bound|estimate|expression)\s+(?:is|reads|becomes)\b"
    r"|\bthe\s+replacement\s+is\s*(?:\\\[|\\\(|[0-9])",
    re.I,
)

_GERUND = re.compile(
    r"^(?:changing|replacing|restricting|adding|removing|correcting|inserting|"
    r"separating|imposing|renormalizing|reversing|swapping|strengthening|weakening)"
    r"\b",
    re.I,
)
_NEGATED = re.compile(r"\b(?:not|cannot|never|insufficient|fails?\s+to)\b", re.I)
_DENIAL = re.compile(
    r"\b(?:does?\s+not\s+(?:claim|establish|show)|no\s+claim|cannot\s+conclude|"
    r"without\s+claiming)\b[^.]{0,100}$",
    re.I,
)


def _has_proposal(value):
    for match in _PROPOSAL.finditer(value):
        if _GERUND.match(match.group()) and _NEGATED.search(match.group()):
            continue
        before = value[max(0, match.start() - 120) : match.start()]
        if _DENIAL.search(before) or re.search(r"\b(?:no|not\s+a)\s*$", before, re.I):
            continue
        if re.search(r"\b(?:state|specify)$", match.group(), re.I) and re.match(
            r"\s+(?:a|an)\s+(?:defensible|appropriate|suitable)\b",
            value[match.end() :],
            re.I,
        ):
            continue
        return True
    return False


def possible_revision(problem):
    """Prefer the explicit proposal, then exact action-bearing report paragraphs.

    The fallback searches only this problem's already retained analysis/result,
    never a different finding or the case-level repair. Whole paragraphs preserve
    stated scope and uncertainty. A mere mention of repair is not a proposal.
    """
    explicit = (problem.get("repair") or {}).get("paragraphs") or []
    explicit = [
        value
        for value in explicit
        if isinstance(value, str) and value.strip() and value.strip() != _BOILERPLATE
    ]
    if explicit:
        return list(explicit)
    narrative, recorded = [], []
    values = [*problem.get("analysis", []), *problem.get("result", [])]
    for index, value in enumerate(values):
        if re.search(
            r"\b(?:two|three|four|several|the following)\s+"
            r"(?:definitions|revisions|changes|corrections|repairs|alternatives|options)"
            r"\s+(?:remove|avoid|repair|resolve|correct)\b",
            value,
            re.I,
        ):
            group = []
            following = index + 1
            while following < len(values) and re.match(
                r"^\s*\d+[.)]\s+", values[following]
            ):
                group.append(values[following])
                following += 1
            if group:
                narrative.extend([value, *group])
                for boundary in values[following : following + 2]:
                    if not boundary.startswith("Recorded evidence:"):
                        narrative.append(boundary)
        if not _has_proposal(value):
            continue
        if value.startswith("Recorded evidence:"):
            recorded.append(re.sub(r"^Recorded evidence:\s*(?:Check\.\s*)?", "", value))
        else:
            narrative.append(value)
    return list(dict.fromkeys(narrative or recorded))
