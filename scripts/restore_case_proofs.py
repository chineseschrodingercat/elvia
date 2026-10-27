"""Recover complete argument units from the retained, source-bound reports.

This is a presentation editor. It neither reviews a paper nor changes a finding.
Only reports with an exact numbered-section/finding correspondence are handled
automatically; different section counts require an explicit reviewed mapping.
"""

from __future__ import annotations

import hashlib
import re

PROBLEM = re.compile(
    r"^(?P<hash>#{1,6}\s*)?(?:\d+(?:\.\d+)*[.:]?\s+)?"
    r"(?P<kind>Problem|P|F)\s*(?P<number>\d+)(?P<letter>[a-z]?)(?!\w)"
    r"(?P<tail>.*)",
    re.I | re.S,
)
HEADING = re.compile(r"^(#{1,6})\s+(.*)", re.S)
GLOBAL = re.compile(
    r"^(?:\d+(?:\.\d+)*[.:]?\s*)?(?:Supporting checks|Sources\b|"
    r"References\b|Consulted (?:sources|references)|Conclusion\b|"
    r"Overall (?:assessment|outcome|dependence)|State table|"
    r"(?:Results|Other|Remaining) (?:checked|checks|claims)|"
    r"Checks (?:that|retained)|Independent checks|Retained evidence|"
    r"Separate clarifications|"
    r"Empirical (?:interpretation|scope)|Repair status|"
    r"Scientific (?:decision|adjudication)|Scope and limitations)",
    re.I,
)
SCOPE = re.compile(
    r"^(?:\d+(?:\.\d+)*[.:]?\s*)?(?:Counterevidence|Alternative|"
    r"What survives|Surviving|Limitations?|Scope|Boundaries|"
    r"Supported impact|Dependency and severity|Interpretation|"
    r"Remaining (?:work|verification))",
    re.I,
)
REPAIR_HEADING = re.compile(
    r"^(?:\d+(?:\.\d+)*[.:]?\s*)?(?:What (?:a|the) repair|"
    r"(?:A |The )?(?:proposed |replacement |new )?(?:replacement algorithm|"
    r"repair(?:s)?\b)|Proposed (?:correction|replacement)|"
    r"Correction and remaining|Full case repair|Verified (?:repair|correction)|"
    r"Local repair|"
    r"A corrected (?:algorithm|estimator|theorem)|Repair status)",
    re.I,
)
SETUP = re.compile(
    r"definitions|mathematical setting|mathematical model|necessary (?:model|notation)|"
    r"assumptions used|definitions and (?:dependencies|assumptions)",
    re.I,
)
CLAIM_HEADING = re.compile(
    r"^(?:\d+(?:\.\d+)*[.:]?\s*)?(?:Original claim|Source claim|"
    r"Claim(?:,| and|$)|Claim under|Claims and assumptions)",
    re.I,
)


def _problem_match(text: str) -> re.Match[str] | None:
    probe = text
    if probe.startswith("Equation reference:") and "Problem" in probe:
        probe = probe[probe.index("Problem") :]
    match = PROBLEM.match(probe)
    if match is None:
        return None
    if match["kind"].casefold() != "problem" and not match["hash"]:
        return None
    if not match["hash"] and not re.match(
        r"^(?:[:.(\[–—-]|continued\b)", match["tail"].strip(), re.I
    ):
        return None
    return match


def problem_sections(report: list[str]) -> list[dict]:
    """Identify native argument starts; repeated conclusions are never starts."""
    sections: list[dict] = []
    seen: set[tuple[int, str]] = set()
    for index, text in enumerate(report):
        match = _problem_match(text)
        if match is None:
            continue
        identity = (int(match["number"]), match["letter"].casefold())
        if identity in seen:
            if sections and identity == (
                sections[-1]["number"],
                sections[-1]["letter"],
            ):
                sections[-1]["continued"].append(index)
            continue
        seen.add(identity)
        heading = HEADING.match(text)
        sections.append(
            {
                "number": identity[0],
                "letter": identity[1],
                "start": index,
                "depth": len(heading[1]) if heading else 1,
                "continued": [],
            }
        )
    for position, section in enumerate(sections):
        end = (
            sections[position + 1]["start"]
            if position + 1 < len(sections)
            else len(report)
        )
        # A peer heading closes the native argument unit. Headings nested
        # inside it remain attached, while a continued native problem does not
        # close its own argument. This keeps later report-wide checks, sources
        # and status tables from being attributed to the final finding.
        for index in range(section["start"] + 1, end):
            heading = HEADING.match(report[index])
            if (
                heading
                and len(heading[1]) <= section["depth"]
                and index not in section["continued"]
            ):
                end = index
                break
        section["end"] = end
    return sections


def numbered_mapping(report: list[str], problems: list[dict]) -> list[dict] | None:
    sections = problem_sections(report)
    if [(s["number"], s["letter"]) for s in sections] != [
        (index, "") for index in range(1, len(problems) + 1)
    ]:
        return None
    return sections


def _body_after_problem_heading(text: str) -> str:
    """Retain an inline scientific paragraph after a parenthesized title."""
    match = _problem_match(text)
    if match is None or match["hash"]:
        return ""
    tail = match["tail"].strip()
    if not tail.startswith("("):
        return ""
    depth = 0
    for index, char in enumerate(tail):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return tail[index + 1 :].lstrip(" .:–—-\n")
    return ""


def shared_setup(report: list[str], before: int) -> list[tuple[int, str]]:
    first_problem = next(
        (index for index, text in enumerate(report) if _problem_match(text)), before
    )
    before = min(before, first_problem)
    active = False
    rows = []
    for index, text in enumerate(report[:before]):
        heading = HEADING.match(text)
        if heading:
            active = bool(SETUP.search(heading[2]))
        elif active and text.strip():
            # A mixed "scope, definitions and checks" section may start with
            # a coverage table. Recover mathematical setup, not that inventory.
            if re.search(r"\s\|\s", text):
                continue
            if re.search(r"\\\(|\\\[", text) or re.match(
                r"^(?:Equation reference:\s*\S+\.\s*)?"
                r"(?:Let|Write|Assume|Consider|Throughout|"
                r"For (?:the|one|a|each|fixed))\b",
                text,
                re.I,
            ):
                rows.append((index, text))
    return rows


def restore_section(report: list[str], section: dict) -> dict:
    """Keep whole scientific paragraphs and their order, with auditable roles."""
    result = {
        "statement": [],
        "proof": [],
        "scope": [],
        "setup": [text for _, text in shared_setup(report, section["start"])],
        "source_indices": [],
        "scope_indices": [],
        "excluded_repair": [],
    }
    mode = "proof"
    repair_depth = None
    for index in range(section["start"], section["end"]):
        text = report[index]
        if index == section["start"] or index in section["continued"]:
            text = _body_after_problem_heading(text)
            if not text:
                continue
        heading = HEADING.match(text)
        if heading:
            label = heading[2]
            depth = len(heading[1])
            if REPAIR_HEADING.search(label):
                mode, repair_depth = "repair", depth
            elif repair_depth is not None and depth > repair_depth:
                pass
            else:
                repair_depth = None
                mode = (
                    "statement"
                    if CLAIM_HEADING.search(label)
                    else "scope"
                    if SCOPE.search(label)
                    else "proof"
                )
            continue
        if not text.strip():
            continue
        if mode == "repair":
            result["excluded_repair"].append(index)
            continue
        result[mode].append(text)
        result["scope_indices" if mode == "scope" else "source_indices"].append(index)
    return result


def _unique(paragraphs: list[str]) -> list[str]:
    seen = set()
    result = []
    for paragraph in paragraphs:
        key = re.sub(r"\s+", " ", paragraph).strip()
        if key and key not in seen:
            result.append(paragraph)
            seen.add(key)
    return result


def restored_fields(problem: dict, restored: dict) -> dict:
    """Use native scientific exposition without discarding existing limits.

    A source-specific condition is kept in the Statement even when the native
    report places its admissibility check within the proof. Unknown historical
    observations remain Verification; a concrete supported argument is Proof.
    """
    native_statement = restored["statement"]
    native_proof = restored["proof"]
    if not native_proof and native_statement:
        # Some reports put the entire trace under "Claim and check". Preserve
        # that full argument in Proof instead of leaving Proof empty or using
        # the older compressed catalogue text in its place.
        native_proof, native_statement = native_statement, []
    statement = _unique(restored["setup"] + native_statement)
    if not native_statement:
        statement = _unique(statement + problem.get("claim", []))
    conditions = _unique(
        [
            re.sub(r"^Assumptions?:\s*", "", condition, flags=re.I)
            for condition in problem.get("assumptions", [])
            if not re.match(r"^Author code executed:", condition, re.I)
        ]
    )
    combined = " ".join(statement)
    conditions = [condition for condition in conditions if condition not in combined]
    if conditions:
        # Keep mathematical qualifications verbatim while converting their
        # list presentation to a connected paragraph. This is never used as a
        # substitute for the native argument restored below.
        statement.append(
            " ".join(condition.rstrip(".;") + "." for condition in conditions)
        )
    proof = _unique(native_proof)
    scope = _unique(restored["scope"] + problem.get("result", []))
    if not proof:
        # No new proof is fabricated when an extraction has no argument unit.
        proof = list(problem.get("analysis", []))
    heading = (
        "Proof"
        if problem.get("assessment") == "supported"
        and problem.get("severity") in {"major", "minor"}
        else "Verification"
    )
    return {
        "claim": statement,
        "assumptions": [],
        "analysis": proof,
        "analysis_heading": heading,
        "result": scope,
    }


def paragraph_binding(report: list[str], indices: list[int]) -> list[dict]:
    return [
        {
            "index": index,
            "sha256": hashlib.sha256(report[index].encode("utf-8")).hexdigest(),
        }
        for index in indices
    ]
