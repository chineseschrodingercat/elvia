"""Collect explicit archived limits without interpreting scientific claims.

Only fields explicitly naming limitations, missing work/materials, unresolved
reasons or counterevidence are eligible. A generic ``scope``, a claim/result,
an acceptance flag or a historical metadata subtree is not a limitation.
Strings remain unchanged apart from surrounding whitespace and structural
labels. Call the publishing layer's privacy/math normalization before release.
"""

from __future__ import annotations

ALIASES = {
    "limitations": "Limitations",
    "limits": "Limits",
    "limit": "Limit",
    "review_limits": "Review limits",
    "scope_limit": "Scope limit",
    "scope_limits": "Scope limits",
    "scope_limitations": "Scope limitations",
    "independent_check_limits": "Independent check limits",
    "unresolved_limits": "Unresolved limits",
    "unchecked_scope": "Unchecked scope",
    "not_exhaustively_inspected": "Not exhaustively inspected",
    "missing_materials": "Missing materials",
    "materials_missing": "Missing materials",
    "missing_evidence": "Missing evidence",
    "unavailable": "Unavailable material",
    "work_not_performed": "Work not performed",
    "not_performed": "Not performed",
    "not_claimed": "Not claimed",
    "not_verified": "Not verified",
    "not_established": "Not established",
    "not_supported": "Not supported",
    "not_inferred": "Not inferred",
    "unresolved_historical_impact": "Unresolved historical impact",
    "unresolved": "Unresolved",
    "unresolved_claims": "Unresolved claim",
    "unresolved_concerns": "Unresolved concern",
    "unresolved_items": "Unresolved item",
    "unresolved_questions": "Unresolved question",
    "counterevidence": "Counterevidence",
    "counterevidence_preserved": "Counterevidence",
    "source_counterevidence": "Source counterevidence",
    "mathematical_counterevidence": "Mathematical counterevidence",
    "strongest_counterevidence": "Strongest counterevidence",
    "strongest_counterreading": "Strongest counterreading",
    "counterreading": "Counterreading",
    "counterevidence_and_limits": "Counterevidence and limits",
    "counterevidence_and_scope": "Counterevidence and scope",
    "counterevidence_and_alternatives": "Counterevidence and alternatives",
    "counterevidence_and_alternative_readings": (
        "Counterevidence and alternative readings"
    ),
    "alternatives_and_counterevidence": "Alternatives and counterevidence",
    "alternative_and_counterevidence": "Alternative and counterevidence",
    "alternative_readings_and_counterevidence": (
        "Alternative readings and counterevidence"
    ),
    "alternatives_counterevidence": "Alternatives and counterevidence",
    "counterevidence_and_survivors": "Counterevidence and surviving claims",
    "scope_and_unresolved": "Scope and unresolved questions",
    "scope_and_surviving_evidence": "Scope and surviving evidence",
}
_HISTORICAL = {
    "history",
    "previous",
    "predecessor",
    "predecessors",
    "superseded",
    "initial_review_artifact_metadata",
    "previous_findings",
    "previous_coverage",
}
_CONTAINERS = {
    "problems",
    "findings",
    "items",
    "ledger",
    "sections",
    "coverage",
    "claims",
    "claims_checked",
    "entries",
    "checks",
    "unresolved",
    "unresolved_claims",
    "unresolved_concerns",
    "unresolved_items",
    "unresolved_questions",
}
_TEXT_WRAPPERS = {
    "text",
    "description",
    "reason",
    "why_unresolved",
    "why_not_confirmed",
    "summary",
    "note",
    "details",
    "question",
    "needed_evidence",
}
_EMPTY = {"", "none", "n/a", "not applicable", "true", "false", "yes", "no"}


def _explicit_text(value):
    if isinstance(value, str):
        if value.strip().casefold() not in _EMPTY:
            yield value.strip()
    elif isinstance(value, list):
        for item in value:
            yield from _explicit_text(item)
    elif isinstance(value, dict):
        # An unresolved finding is an object, not a string: select its stated
        # reason/description, never its original claim, verdict or pass flags.
        for key, item in value.items():
            if key in _TEXT_WRAPPERS:
                yield from _explicit_text(item)


def collect_limits(findings, coverage) -> list[str]:
    """Return ordered, explicitly labeled archived limits; infer no new ones."""
    result, seen = [], set()

    def collect(value, context="", container=""):
        if isinstance(value, list):
            for item in value:
                child_context = context
                if isinstance(item, dict) and container in _CONTAINERS:
                    parts = [item.get("id"), item.get("title") or item.get("name")]
                    label = " — ".join(
                        part.strip()
                        for part in parts
                        if isinstance(part, str) and part.strip()
                    )
                    child_context = label or context
                collect(item, child_context, container)
        elif isinstance(value, dict):
            for key, item in value.items():
                if key in _HISTORICAL:
                    continue
                if key in ALIASES:
                    prefix = (context + " — " if context else "") + ALIASES[key] + ": "
                    for text in _explicit_text(item):
                        entry = prefix + text
                        identity = " ".join(entry.split())
                        if identity not in seen:
                            seen.add(identity)
                            result.append(entry)
                collect(item, context, key)

    collect(findings)
    collect(coverage)
    return result
