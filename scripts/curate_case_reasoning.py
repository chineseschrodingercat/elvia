"""Curate presentation prose without changing records, findings or full reports.

The deterministic pass removes field inventories and groups substantive archived
checks. Reviewed mathematical rewrites bind to their original visible fields.
The complete report and evidence mappings remain separately available.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import tempfile
from collections import Counter
from functools import lru_cache
from pathlib import Path

VISIBLE = (
    "claim",
    "assumptions",
    "analysis",
    "result",
    "brief",
    "repair",
    "analysis_heading",
)
PROTECTED = re.compile(r"\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]|`[^`]*`")
SOURCE_LITERAL = re.compile(
    PROTECTED.pattern + r"|https?://[^\s]+|"
    r"\b[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+\((?:[^()\n]|\([^()\n]*\))*\)|"
    r"(?:[\w.-]+/)+[^\s;,]+|"
    r"\b(?:p|pp|page|pages)\.?\s+\d+(?:[–-]\d+)?|"
    r"\b[\w.^+-]+\.(?:py|ipynb|cpp|cu|sh|yaml|yml|json|txt|md|pdf)\b"
)
NUMBER_PREFIX = re.compile(
    r"\b(and|with|for|at|only|from|to|by|of|than|is|has|gives|equals|about|"
    r"approximately|top|threshold|nominal)(?=[+-]?(?:\d|\.\d))",
    re.I,
)
NUMBER_SUFFIX = re.compile(
    r"(?<=\d)(?=studies\b|study\b|samples?\b|rows?\b|memberships?\b|"
    r"reproduces\b|trials?\b|seeds?\b|directions?\b|random\b|per\b|"
    r"corrected\b|percentage\b|modes?\b|iid\b|argument\b|not\b|points?\b|"
    r"equal\b|images?\b|percent\b|wrong\b|history\b|mean\b|accuracy\b|"
    r"exact\b|independent\b|papers?\b|words?\b|records?\b|processed\b|"
    r"skipped\b|metric\b|benchmarks?\b|resizing\b|codebooks?\b|parallel\b|"
    r"output\b|perclaim\b|though\b|shot\b|count\b|attempts?\b|bits?\b|"
    r"teammates?\b|mismatch\b|source\b|weighted\b|macro\b|aggregate\b|"
    r"questions?\b|runs?\b|elapsed\b|hours?\b|total\b)",
    re.I,
)
SCIENTIFIC_COMPOUNDS = frozenset(
    {
        "underparameterized",
        "overparameterized",
        "nonidentifiability",
        "nonmartingales",
        "subprobability",
        "nonanswerability",
        "noncomparability",
    }
)
ENGLISH_FUNCTION_WORDS = frozenset(
    "a an and are as at be been but by can do for from had has have he if in "
    "is it its may me my no not of on or our so than that the their then there "
    "these they this to up us was we were will with you".split()
)
COMPACT_NUMERIC_INDEX = re.compile(
    r"(?:[A-Za-z]|alpha|beta|gamma|delta|epsilon|varepsilon|eta|zeta|theta|"
    r"kappa|lambda|mu|nu|xi|rho|sigma|tau|phi|psi|omega|pi|Delta|Gamma|"
    r"Sigma|Omega|Theta|Lambda)\d+"
)
REFERENCE = re.compile(
    r"^(?:(?:papers|sources|verification|reports|evidence)/|https?://|"
    r"(?:E|S|R)\d+(?:\b|:)|(?:paper|source|check|calc|code|input|output)[\w.-]*"
    r"\.(?:json|py|txt|png|pdf|md)(?:\b|#)|[a-f0-9]{40,64}$)",
    re.I,
)
METADATA = re.compile(
    r"(?:^Evidence bindings\b|^Evidence (?:refs|references)\b|"
    r"\b(?:sha ?256|bytes|full path|path length|performer|agent ref|"
    r"performed by|performed at|checked at|token|hash binding references|"
    r"evidence refs?|check references?|source references?|source pages?|"
    r"source pdf|additional sources\. path|additional sources\. sha256|"
    r"adjudication status|author adoption|assessment unchanged|parent integrated|"
    r"new recovery work|work type|problem id|finding id)\b)",
    re.I,
)
STATE = re.compile(
    r"^(?:true|false|null|none|pending|not_requested|not requested|unknown|"
    r"retained|accepted|supported|"
    r"assessment_confirmed|verified_with_stated_scope|"
    r"Major|Minor|Needs Evidence|No Issue Found)(?:\.)?$",
    re.I,
)
COUNTER = re.compile(
    r"counterevidence|counterreading|alternative|surviv|limitation|boundary|"
    r"remaining work|not established|what survives|scope|limits",
    re.I,
)
REPAIR = re.compile(r"^(?:Correction|Repair|Remedy)(?:\.|\b)", re.I)
SCIENTIFIC_SCOPE = re.compile(
    r"not |no |unknown|unverified|unresolved|unavailable|only|partial|"
    r"within|finite|analytic|algebra|static|not.*(?:run|prove)|remains",
    re.I,
)
FIELD_ROOT = re.compile(
    r"^(?:Status|Outcome|Inspection outcome|Classification|Evidence|"
    r"Evidence bindings|Evidence refs|Evidence references|Check|"
    r"Complete check|Check type|Counterexample|Counterevidence|Counterreading|"
    r"Witness|Values|Primary result|Decisive evidence|Result|Impact|"
    r"Supported impact|Core dependency|Dependency|Suspect step|Assumptions?|"
    r"Assumptions? verified|Assumptions? checked|Methods?|Repair|Correction|"
    r"Remedy|Remaining work|Limitation|Limitations|Limits|Scope|Boundary|"
    r"Survives|What survives|Alternative|Alternative reading|Alternative readings|"
    r"Alternative explanation|Alternatives counterevidence|Severity|"
    r"Severity rationale|Severity calibration|Independent check|"
    r"Independent verification|Independent acceptance check|Acceptance check|"
    r"Focused check|Focused acceptance|Recovery verification|Adoption|"
    r"Author adoption|Adjudication status|Archived judgment|Problem id|Finding id)"
    r"(?:\.|$)",
    re.I,
)
REFERENCE_EXTENSIONS = (
    r"(?:pyi?|jsonl?|txt|md|pdf|png|jpe?g|svg|ipynb|csv|tsv|npy|npz|"
    r"ya?ml|sh|c|cpp|h|hpp|cu|rs|zip|diff|patch|log|tex|gz)"
)
REFERENCE_TOKEN = re.compile(
    r"(?:https?://[^\s]+|(?:[\w.()@+-]+/)*[\w.()@+-]+\."
    + REFERENCE_EXTENSIONS
    + r"(?:[#][^\s]*|:[A-Za-z0-9_,.–/-]+)?|"
    r"(?:papers|verification|sources|reports|evidence)/[\w.()@+/-]+/?)",
    re.I,
)
REFERENCE_PREFIX = re.compile(
    r"^(?:Evidence(?: (?:refs|references|files|bindings))?"
    r"(?:[.] [A-Za-z][A-Za-z .-]*)?|Source(?: files?)?|Check references?|"
    r"Artifact|Path|SHA256|Hash|File):\s*",
    re.I,
)


def visible_digest(problem):
    value = {key: problem[key] for key in VISIBLE if key in problem}
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode()
    ).hexdigest()


def sentence(text):
    text = text.strip()
    if text and not re.search(r"[.!?]$", text) and not text.endswith(r"\]"):
        text += "."
    return text


def source_words(report):
    return Counter(re.findall(r"[A-Za-z]{2,}", " ".join(report)))


def pure_reference(raw):
    """Recognize whole locator lists, never scientific sentences or code."""
    if raw.lstrip().startswith(("Code:", "```")):
        return False
    value = re.sub(r"^Recorded evidence:\s*", "", raw.strip())
    value = REFERENCE_PREFIX.sub("", value)
    pieces = re.split(r"\s*[,;]\s*|(?<=\.)\s+(?=[\w./])", value)
    return bool(pieces) and all(
        REFERENCE_TOKEN.fullmatch(piece.strip().strip("`'\"").rstrip("."))
        for piece in pieces
    )


def plain_row(raw):
    """Return (role, scientific text), or None for an inventory/status row."""
    raw = re.sub(r"^Recorded evidence:\s*", "", raw.strip())
    if pure_reference(raw):
        return None
    match = re.match(r"^([^:]{1,150}):\s*(.*)$", raw, re.S)
    if not match:
        return "check", raw
    prefix, value = match.groups()
    value = value.strip()
    if prefix.casefold() == "mode" and value.casefold() in {"recovery", "acceptance"}:
        return None
    if prefix.casefold() in {"adoption status", "disposition", "result"}:
        if STATE.fullmatch(value):
            return None
    if prefix.casefold() == "kind" and re.fullmatch(r"[a-z]+(?:_[a-z]+)+", value):
        return "check", value.replace("_", " ")
    if prefix.endswith("Verified dimensions"):
        if re.fullmatch(r"[A-Za-z]+(?:_[A-Za-z0-9]+)+", value) or value.casefold() in {
            "counterevidence",
            "assumptions",
            "severity",
            "correction scope",
            "core dependency",
            "source claim and location",
        }:
            return None
    if not FIELD_ROOT.match(prefix):
        return "check", raw
    if re.search(
        r"(?:^|\. )(?:Phase|Disposition|Assessment retained|Checked|"
        r"Checks completed|Verified dimensions)$",
        prefix,
        re.I,
    ) and (STATE.fullmatch(value) or re.fullmatch(r"[a-z]+(?:_[a-z0-9]+)+", value)):
        return None
    if re.search(
        r"\. Checks\. (?:Claim location|Assumptions|Decisive evidence|"
        r"Counterevidence|Core dependency|Severity|Correction scope)$",
        prefix,
        re.I,
    ):
        if re.fullmatch(r"true|false", value, re.I):
            return None
    if re.search(
        r"(?:^|\. )(?:Source files hash checked|File count|Hashed files)$", prefix, re.I
    ):
        if re.fullmatch(r"\d+", value):
            return None
    if re.search(r"(?:^|\. )Result$", prefix, re.I) and re.fullmatch(
        r"accepted within stated local scope|assessment_confirmed|"
        r"verified_with_stated_scope",
        value,
        re.I,
    ):
        return None
    # A reference's free-text location can describe the scientific method.
    # File/line pointers are kept in the separately frozen evidence inventory.
    if re.fullmatch(r"Evidence refs?\. Location", prefix, re.I):
        if re.search(
            r"calculation|derivation|analytic|algebraic|symbolic|numerical", value, re.I
        ):
            return "check", value
    if re.search(r"author adoption|^adoption$", prefix, re.I):
        return None if STATE.fullmatch(value) else ("counter", value)
    if METADATA.search(prefix) or not value:
        return None
    leaf = prefix.rsplit(". ", 1)[-1]
    if re.fullmatch(r"true|false|null|none", value, re.I):
        return "counter", leaf + ": " + value
    if leaf.casefold() in {"status", "outcome", "inspection outcome", "classification"}:
        if STATE.fullmatch(value) or re.fullmatch(r"[a-z]+(?:_[a-z0-9]+)+", value):
            return None
    if prefix.casefold() in {"evidence", "evidence refs", "evidence references"}:
        if re.fullmatch(
            r"(?:(?:papers|sources|verification|reports|evidence)/[^\s;,]+|"
            r"https?://[^\s;,]+|[ESR]\d+(?::[\w.-]+)?|[a-f0-9]{40,64})"
            r"(?:\s*[,;]\s*(?:(?:papers|sources|verification|reports|evidence)/"
            r"[^\s;,]+|[ESR]\d+(?::[\w.-]+)?))*",
            value,
            re.I,
        ):
            return None
        if re.fullmatch(
            r"[ESR]\d+:(?:(?:PDF|Section|Appendix|Figure|Table|Eq|Algorithm|"
            r"pp?\.?)\s*[\dA-Za-z.,;() /–-]+)+",
            value,
        ):
            return None
    if REPAIR.search(prefix):
        if re.search(
            r"statement|proposal|^remedy$|^repair$|^correction$", prefix, re.I
        ):
            return "repair", value
        if re.search(r"scope|limit|verification|status", prefix, re.I):
            return "scope", value
        if SCIENTIFIC_SCOPE.search(value):
            return "scope", value
        return "scope", leaf + ": " + value
    if COUNTER.search(prefix):
        return "counter", value
    if re.search(r"severity|calibration|core dependency|^dependency$", prefix, re.I):
        value = re.sub(r"^(?:Major|Minor)(?: retained)?\s*[:;]\s*", "", value)
        return "scope", value
    if re.search(
        r"^(?:Witness|Counterexample|Values|Primary result|Decisive evidence)\.", prefix
    ):
        return "check", leaf + ": " + value
    if ". " in prefix and len(value.split()) <= 3:
        descriptor = prefix.split(". ", 1)[1]
        return "check", descriptor + ": " + value
    return "check", value


def distinct(values):
    seen, result = set(), []
    for value in values:
        value = sentence(value)
        # Upper/lowercase tokens can denote distinct labels or variables.
        key = re.sub(r"\s+", " ", value)
        if key and key not in seen:
            seen.add(key)
            result.append(value)
    return result


def normalize_location(text):
    """Space known prose locators without touching file/URL/code identifiers."""
    protected = re.compile(
        PROTECTED.pattern + r"|https?://\S+|(?:[\w.-]+/)+[\w./:#-]+|"
        r"\b[\w.-]+\.(?:py|ipynb|cpp|cu|sh|yaml|yml|json|txt|md|pdf)\b"
    )
    pieces, start = [], 0
    for match in protected.finditer(text):
        pieces.append((False, text[start : match.start()]))
        pieces.append((True, match[0]))
        start = match.end()
    pieces.append((False, text[start:]))
    output = []
    for keep, value in pieces:
        if not keep:
            value = re.sub(
                r"(?<=\d)(?=(?:Table|Figure|Section|Algorithm|Appendix|printed|physical))",
                " ",
                value,
            )
            value = re.sub(
                r"\b(Section|Table|Figure|Algorithm|Appendix|Lemma|Theorem|Corollary)(?=\d)",
                r"\1 ",
                value,
            )
            value = re.sub(r"\b(PDF)pp?(?=\d)", r"\1 pp. ", value)
            value = re.sub(
                r"\b(pp?|pages?)[.]?(?=\d)",
                lambda m: "pp. " if m[1].lower() in {"pp", "pages"} else "p. ",
                value,
            )
            value = re.sub(r"\b(physical|printed)\s*(?=\d)", r"\1 p. ", value)
        output.append(value)
    return "".join(output)


@lru_cache(maxsize=4)
def _source_context(report):
    report_text = " ".join(report)
    words = re.findall(r"[A-Za-z]+", PROTECTED.sub(" ", report_text))
    vocabulary = {word.casefold() for word in words}
    phrases = {}
    for index in range(len(words)):
        for count in range(2, min(9, len(words) - index + 1)):
            selected = words[index : index + count]
            key = "".join(selected).casefold()
            if 14 <= len(key) <= 80:
                phrases.setdefault(key, set()).add(tuple(map(len, selected)))
    formulas = []
    for span in re.findall(r"\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]", report_text):
        span = decimal_powers(span)
        body = span[2:-2]
        # Scripted terms retain the exact source TeX even when the archived
        # sentence includes only a subexpression of a larger display.
        for match in re.finditer(
            r"(?:\\(?:mathbb|mathsf|mathrm|mathbf)\s+)?(?:\\[A-Za-z]+|[A-Za-z])(?:[_^](?:\{[^{}]{1,40}\}|\\[A-Za-z]+|[A-Za-z0-9+-]))+",
            body,
        ):
            if re.match(r"\.\d", body[match.end() :]):
                continue
            term = match[0]
            spelling = _formula_plain(term)
            if spelling and len(spelling) >= 3:
                formulas.append((spelling, r"\(" + term + r"\)"))
        plain = _formula_plain(body)
        if plain is None:
            continue
        explicit_variable = (
            re.fullmatch(r"[A-Za-z]{1,3}", plain) and plain not in {"a", "A", "i", "I"}
        ) or re.fullmatch(
            r"\\(?:alpha|beta|gamma|delta|epsilon|theta|kappa|lambda|mu|nu|rho|sigma|tau|phi|psi|omega)",
            body,
        )
        if explicit_variable or (
            len(plain) >= 3
            and re.search(r"[A-Za-z]", plain)
            and re.search(r"[_^()=<>]", plain)
        ):
            formulas.append((plain, span))
    expanded = []
    for plain, span in formulas:
        spellings = {plain}
        compact = plain.replace("_", "")
        if not COMPACT_NUMERIC_INDEX.fullmatch(compact):
            spellings.add(compact)
        parenthesized = _formula_plain(re.sub(r"\^\{([^{}]+)\}", r"^(\1)", span[2:-2]))
        if parenthesized:
            spellings.add(parenthesized)
            compact = parenthesized.replace("_", "")
            if not COMPACT_NUMERIC_INDEX.fullmatch(compact):
                spellings.add(compact)
        spellings.update(value.replace("epsilon", "eps") for value in tuple(spellings))
        expanded.extend(
            (value, span)
            for value in spellings
            if value.casefold() not in ENGLISH_FUNCTION_WORDS
        )
    return vocabulary, phrases, expanded


def _formula_plain(body):
    """A deliberately small, non-executing spelling map, never a math parser.

    Unsupported commands are rejected. All restored formulas are copied from
    the retained report; no missing relation or numerical value is inferred.
    """
    names = {
        "alpha",
        "beta",
        "gamma",
        "delta",
        "epsilon",
        "theta",
        "kappa",
        "lambda",
        "mu",
        "nu",
        "rho",
        "sigma",
        "tau",
        "phi",
        "psi",
        "omega",
        "Delta",
        "Gamma",
        "Sigma",
        "Omega",
        "Theta",
        "Lambda",
        "log",
        "exp",
        "sin",
        "cos",
        "tan",
        "tanh",
        "min",
        "max",
        "sup",
        "inf",
        "lim",
        "det",
        "rank",
    }
    operators = {
        "leq": "<=",
        "le": "<=",
        "geq": ">=",
        "ge": ">=",
        "ne": "!=",
        "neq": "!=",
        "cdot": "*",
        "times": "*",
        "top": "T",
    }
    fonts = {"mathrm", "mathsf", "mathbb", "mathbf", "mathcal", "operatorname", "rm"}

    def command(match):
        name = match[1]
        if name in names:
            return name
        if name in operators:
            return operators[name]
        if name in fonts or name in {"left", "right", "quad", "qquad"}:
            return ""
        if name == "varepsilon":
            return "epsilon"
        return match[0]

    plain = re.sub(r"\\([A-Za-z]+)", command, body)
    plain = re.sub(r"\\[,;! ]", "", plain)
    plain = re.sub(r"[{}\s]", "", plain)
    if "\\" in plain or not re.fullmatch(r"[A-Za-z0-9_^()+*/=<>!.,|+-]+", plain):
        return None
    return plain


def _source_token_lengths(token, vocabulary):
    """Return the unique shortest source-word spelling, adding spaces only."""
    lower = token.casefold()
    if lower in vocabulary or lower in SCIENTIFIC_COMPOUNDS or len(lower) > 100:
        return None
    # Single letters are deliberately excluded: a model/gene identifier must
    # not be carved into arbitrary letters to force a dictionary match.
    best = {len(lower): (0, 1, ())}
    for start in range(len(lower) - 2, -1, -1):
        choices = []
        for end in range(start + 2, min(len(lower), start + 45) + 1):
            if lower[start:end] in vocabulary and end in best:
                count, ways, lengths = best[end]
                choices.append((count + 1, ways, (end - start,) + lengths))
        if choices:
            minimum = min(choice[0] for choice in choices)
            shortest = [choice for choice in choices if choice[0] == minimum]
            ways = min(2, sum(choice[1] for choice in shortest))
            best[start] = (minimum, ways, shortest[0][2])
    selected = best.get(0)
    if selected and selected[1] == 1 and 2 <= selected[0] <= 12:
        return selected[2]
    return None


def decimal_powers(text):
    """Brace a complete literal decimal exponent; never split its value."""
    return re.sub(r"\^([+\-]?(?:\d+(?:\.\d+)?|\.\d+))(?![\w.])", r"^{\1}", text)


def literal_math(text, greek_names=None, blocked_spellings=()):
    """Typeset explicit, unambiguous single-symbol powers without changing them.

    A fused symbol such as ``dc`` and a bare fractional exponent remain for
    source review. This pass only changes the typography of an existing power.
    """
    greek = {
        "alpha",
        "beta",
        "gamma",
        "delta",
        "epsilon",
        "theta",
        "kappa",
        "lambda",
        "mu",
        "nu",
        "rho",
        "sigma",
        "tau",
        "phi",
        "psi",
        "omega",
        "Delta",
        "Gamma",
        "Sigma",
        "Omega",
        "Theta",
        "Lambda",
    }
    if greek_names is not None:
        greek.intersection_update(greek_names)
    bases = "|".join(sorted(greek, key=len, reverse=True)) + "|[A-Za-z]"
    pattern = re.compile(
        r"(?<![\w.\\])(" + bases + r")"
        r"(_(?:\{[A-Za-z0-9]+\}|[A-Za-z0-9]))?"
        r"\^(\{[A-Za-z0-9 +*\-]+\}|[+\-]?\d+(?:\.\d+)?)(?![\w/^])(?!\.\d)"
    )

    def replace(match):
        if match[0] in blocked_spellings:
            return match[0]
        base, subscript, exponent = match.groups()
        base = "\\" + base if base in greek else base
        if subscript:
            value = subscript[1:]
            subscript = "_" + (value if value.startswith("{") else "{" + value + "}")
        else:
            subscript = ""
        if not exponent.startswith("{"):
            exponent = "{" + exponent + "}"
        return r"\(" + base + subscript + "^" + exponent + r"\)"

    parts, start = [], 0
    for protected in SOURCE_LITERAL.finditer(text):
        parts.extend(
            [pattern.sub(replace, text[start : protected.start()]), protected[0]]
        )
        start = protected.end()
    parts.append(pattern.sub(replace, text[start:]))
    return "".join(parts)


def source_presentation(text, report, vocabulary=None, word_spacing=None):
    """Restore only source-attested spaces and exact simple formula spellings."""
    if text.lstrip().startswith("Code:"):
        return text
    local_vocabulary, phrases, formulas = _source_context(tuple(report))
    vocabulary = local_vocabulary if vocabulary is None else vocabulary
    ambiguous_spellings = set()

    def prose(value):
        value = NUMBER_SUFFIX.sub(" ", NUMBER_PREFIX.sub(r"\1 ", value))

        def spaced(match):
            token = match[0]
            choices = phrases.get(token.casefold(), set())
            if token.casefold() in SCIENTIFIC_COMPOUNDS:
                return token
            if word_spacing and token in word_spacing:
                return word_spacing[token]
            if token.casefold() in vocabulary:
                return token
            lengths = (
                next(iter(choices))
                if len(choices) == 1
                else _source_token_lengths(token, vocabulary)
            )
            if lengths is None:
                return token
            result, position = [], 0
            for size in lengths:
                result.append(token[position : position + size])
                position += size
            return " ".join(result)

        value = re.sub(r"[A-Za-z]{14,}", spaced, value)
        # One substitution pass prevents overlapping source formulas from
        # nesting delimiters inside a formula inserted earlier in the loop.
        candidates = {}
        for plain, span in formulas:
            candidates.setdefault(plain, []).append(span)
        by_plain = {}
        for plain, spans in candidates.items():
            identities = {re.sub(r"[{}\s]", "", span) for span in spans}
            if len(identities) == 1:
                by_plain[plain] = spans[0]
            else:
                ambiguous_spellings.add(plain)
        if by_plain:
            pattern = (
                r"(?<![\w'’])(?:"
                + "|".join(
                    re.escape(plain)
                    + (r"(?![\w'’.^])" if plain.isalpha() else r"(?![\w'’^])")
                    + r"(?!\.\d)"
                    for plain in sorted(by_plain, key=len, reverse=True)
                )
                + r")"
            )
            value = re.sub(pattern, lambda m: by_plain[m[0]], value)
        return value

    result, start = [], 0
    for match in SOURCE_LITERAL.finditer(text):
        result += [prose(text[start : match.start()]), match[0]]
        start = match.end()
    result.append(prose(text[start:]))
    source_greek = set(re.findall(r"\\([A-Za-z]+)\b", " ".join(report)))
    joined = literal_math("".join(result), source_greek, ambiguous_spellings)
    return re.sub(r"\\\)([ \t]*[+*/=<>!|\-][ \t+*/=<>!|\-]*)\\\(", r"\1", joined)


def clean_rows(rows):
    groups = {"check": [], "counter": [], "scope": [], "repair": []}
    inventory = []
    for raw in rows:
        parsed = plain_row(raw)
        if parsed is None:
            inventory.append(raw)
        else:
            role, text = parsed
            groups[role].append(text)
    return {key: distinct(value) for key, value in groups.items()}, inventory


def generic_problem(problem, report, vocabulary=None, word_spacing=None):
    result = copy.deepcopy(problem)
    if problem.get("analysis_heading") == "Reasoning and counterevidence":
        result["source_location"] = normalize_location(result["source_location"])
        return result, []
    grouped, removed = clean_rows(problem["analysis"])
    result["analysis_heading"] = "Reasoning and counterevidence"
    paragraphs = [
        " ".join(grouped[key]) for key in ("check", "counter", "scope") if grouped[key]
    ]
    if paragraphs:
        result["analysis"] = paragraphs
    else:
        result["analysis"] = [" ".join(problem.get("brief", problem["result"]))]
    for key in ("claim", "assumptions"):
        cleaned = []
        for value in problem[key]:
            value = re.sub(
                r"^(?:Recorded check|Recorded inspection subject|"
                r"Recorded report material):\s*",
                "",
                value,
            )
            cleaned.append(sentence(value))
        result[key] = distinct(cleaned)
    findings, _ = clean_rows(problem["result"])
    values = findings["check"] + findings["counter"] + findings["scope"]
    if values:
        result["result"] = [" ".join(values)]
    if result.get("repair"):
        result["repair"]["paragraphs"] = distinct(
            result["repair"]["paragraphs"] + grouped["repair"]
        )
    for key in ("claim", "assumptions", "analysis", "result", "brief"):
        if key in result:
            result[key] = [
                source_presentation(text, report, vocabulary, word_spacing)
                for text in result[key]
            ]
    if result.get("repair"):
        result["repair"]["paragraphs"] = [
            source_presentation(text, report, vocabulary, word_spacing)
            for text in result["repair"]["paragraphs"]
        ]
    result["source_location"] = normalize_location(result["source_location"])
    return result, removed


def apply_reviewed(problem, reviewed, report=()):
    for source in reviewed.get("source_report_paragraphs", []):
        index = source["index"]
        if (
            not isinstance(index, int)
            or not 0 <= index < len(report)
            or hashlib.sha256(report[index].encode("utf-8")).hexdigest()
            != source["sha256"]
        ):
            raise ValueError("reviewed proof source paragraph does not match")
    if visible_digest(problem) == reviewed["before_sha256"]:
        result, _ = generic_problem(problem, report)
        result.update(copy.deepcopy(reviewed["fields"]))
        return result
    if all(
        problem.get(key) == value
        for key, value in reviewed["fields"].items()
        if key != "source_location"
    ):
        result = copy.deepcopy(problem)
        result.update(copy.deepcopy(reviewed["fields"]))
        return result
    raise ValueError("reviewed reasoning does not match original visible fields")


def apply_literal_tokens(problem, rows, report):
    """Apply reviewed source-SHA-bound tokens to latest prose, never old arrays."""
    result, receipt = copy.deepcopy(problem), []
    for row in rows:
        source = report[row["source_report_index"]]
        if (
            hashlib.sha256(source.encode()).hexdigest()
            != row["source_paragraph_sha256"]
        ):
            raise ValueError("literal source paragraph does not match")
        assignment, after = row["source_assignment"], row["after_source_TeX"]
        if not after.startswith(r"\(") or not after.endswith(r"\)"):
            raise ValueError("literal replacement must be source math")
        body = re.sub(r"\s+", "", after[2:-2])
        witness = re.sub(r"\s+", "", assignment)
        if body != witness or witness not in re.sub(r"\s+", "", source):
            raise ValueError("literal replacement is not the exact source assignment")
        field = re.fullmatch(
            r"(claim|assumptions|analysis|result|brief|repair\.paragraphs)(?:\[\d+\])?",
            row["field_path"],
        )
        if not field:
            raise ValueError("literal replacement field is outside visible prose")
        key = field[1]
        container = result.get("repair") if key == "repair.paragraphs" else result
        key = "paragraphs" if key == "repair.paragraphs" else key
        values = container.get(key, []) if container else []
        token = row["before_token"]
        pattern = re.compile(r"(?<![\w])" + re.escape(token) + r"(?![\w])")
        total = 0
        for position, value in enumerate(values):
            pieces, start = [], 0
            for keep in SOURCE_LITERAL.finditer(value):
                prose, count = pattern.subn(
                    lambda match, replacement=after: replacement,
                    value[start : keep.start()],
                )
                total += count
                pieces.extend([prose, keep[0]])
                start = keep.end()
            prose, count = pattern.subn(
                lambda match, replacement=after: replacement, value[start:]
            )
            total += count
            pieces.append(prose)
            values[position] = "".join(pieces)
        receipt.append(
            {
                "field": row["field_path"],
                "before": token,
                "after": after,
                "count": total,
            }
        )
    return result, receipt


def finish_visible_math(value):
    if value.lstrip().startswith("Code:"):
        return value
    pieces, start = [], 0
    for span in SOURCE_LITERAL.finditer(value):
        pieces.append(
            NUMBER_SUFFIX.sub(
                " ", NUMBER_PREFIX.sub(r"\1 ", value[start : span.start()])
            )
        )
        pieces.append(
            decimal_powers(span[0]) if span[0].startswith((r"\(", r"\[")) else span[0]
        )
        start = span.end()
    pieces.append(NUMBER_SUFFIX.sub(" ", NUMBER_PREFIX.sub(r"\1 ", value[start:])))
    return "".join(pieces)


def curate_catalog(catalog, reviewed, *, reviewed_only=False):
    result, inventory = copy.deepcopy(catalog), []
    for case_id, entry in reviewed.get("case_quotes", {}).items():
        note = result["cases"][case_id]
        if (
            note.get("revision") != entry["revision"]
            or note.get("record_sha256") != entry["record_sha256"]
        ):
            raise ValueError("source quote does not match its source revision")
        after = entry["after"]
        if (
            not isinstance(after, list)
            or not after
            or any(
                not isinstance(quote, dict)
                or any(
                    not isinstance(quote.get(key), str) or not quote[key].strip()
                    for key in ("text", "locator", "source_identity", "source_sha256")
                )
                or quote["source_sha256"] != entry["source_pdf_sha256"]
                for quote in after
            )
        ):
            raise ValueError("source quote does not match its original PDF")
        if note.get("source_quotes") not in (entry.get("before"), after):
            raise ValueError("source quote does not match its original text")
        # Verbatim quotations and source digests bypass prose normalization.
        note["source_quotes"] = copy.deepcopy(after)
    for case_id, entry in reviewed.get("case_briefs", {}).items():
        note = result["cases"][case_id]
        if (
            note.get("revision") != entry["revision"]
            or note.get("record_sha256") != entry["record_sha256"]
        ):
            raise ValueError("case overview does not match its source revision")
        if note.get("brief") not in (entry.get("before"), entry["after"]):
            raise ValueError("case overview does not match its source text")
        if (
            not isinstance(entry["after"], list)
            or not entry["after"]
            or not all(isinstance(value, str) for value in entry["after"])
        ):
            raise ValueError("case overview must contain reviewed prose")
        note["brief"] = copy.deepcopy(entry["after"])
    word_spacing = reviewed.get("word_spacing", {})
    for original, spaced in word_spacing.items():
        if not original.isalpha() or spaced.replace(" ", "") != original:
            raise ValueError(
                "reviewed word spacing must preserve every original letter"
            )
    literal_rows = {}
    for row in reviewed.get("literal_tokens", []):
        literal_rows.setdefault((row["case"], row["id"]), []).append(row)
    vocabulary = frozenset(
        word.casefold()
        for note in catalog["cases"].values()
        for word in re.findall(
            r"[A-Za-z]+", PROTECTED.sub(" ", " ".join(note.get("report", [])))
        )
    )
    for case_id, note in result["cases"].items():
        for index, problem in enumerate(note.get("problems", [])):
            entry = reviewed.get("cases", {}).get(case_id, {}).get(problem["id"])
            if entry:
                updated = apply_reviewed(problem, entry, note.get("report", []))
                removed = [s for s in problem["analysis"] if plain_row(s) is None]
            elif reviewed_only and not literal_rows.get((case_id, problem["id"])):
                continue
            elif reviewed_only:
                updated, removed = copy.deepcopy(problem), []
            else:
                updated, removed = generic_problem(
                    problem, note.get("report", []), vocabulary, word_spacing
                )
            updated, literal_receipt = apply_literal_tokens(
                updated,
                literal_rows.get((case_id, problem["id"]), []),
                note.get("report", []),
            )
            for key in ("claim", "assumptions", "analysis", "result", "brief"):
                if key in updated:
                    updated[key] = [
                        finish_visible_math(value) for value in updated[key]
                    ]
            if updated.get("repair"):
                updated["repair"]["paragraphs"] = [
                    finish_visible_math(value)
                    for value in updated["repair"]["paragraphs"]
                ]
            note["problems"][index] = updated
            updated["source_location"] = normalize_location(updated["source_location"])
            inventory.append(
                {
                    "case": case_id,
                    "id": problem["id"],
                    "removed": removed,
                    "literal_replacements": literal_receipt,
                }
            )
    return result, inventory


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument(
        "--reviewed",
        type=Path,
        default=Path(__file__).with_name("case_reasoning_reviewed.json"),
    )
    parser.add_argument("--reviewed-only", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text("utf-8"))
    reviewed = json.loads(args.reviewed.read_text("utf-8"))
    result, inventory = curate_catalog(
        catalog, reviewed, reviewed_only=args.reviewed_only
    )
    if args.output or args.write:
        destination = args.catalog if args.write else args.output
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=destination.parent,
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(json.dumps(result, ensure_ascii=True, indent=2) + "\n")
            temporary_path = Path(temporary.name)
        temporary_path.replace(destination)
    if args.inventory:
        args.inventory.write_text(
            json.dumps(inventory, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(
        json.dumps(
            {
                "problems": len(inventory),
                "inventory_rows_removed": sum(len(row["removed"]) for row in inventory),
            }
        )
    )


if __name__ == "__main__":
    main()
