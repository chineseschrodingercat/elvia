"""Prepare readable publication copies without internal review/build narration.

This module edits no scientific records. Its CLI writes an auditable candidate
plan to a new output directory. Paragraph edits are bound to original indices
and SHA-256 values; callers decide when to apply and rebind publication files.
Scientific reasoning, source citations, code and limitations are retained.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import runpy
from collections import Counter
from functools import cache
from pathlib import Path

HEADING = re.compile(r"^(#{1,6})\s+(.+)$")
WORKFLOW_HEADING = re.compile(
    r"provenance|reproducib|\broles?\b|execution|\bcommands?\b|"
    r"\bartifacts?\b|actual work|actual files|operations|production status|"
    r"handoff|delivery|actual evidence|reviewer evidence|"
    r"verification and decision status|acceptance correction note",
    re.I,
)
EXCLUDED_HEADING = re.compile(
    r"\bproblem\s*\d|counterevidence|alternative|source identity|"
    r"source claim|definitions|\bproof\b|\btheorem\b|\blemma\b|"
    r"unresolved|surviving|bounded reproducibility|empirical|"
    r"experiment provenance|remaining limits|negative result|"
    r"scoped correction|interpretation limits|static.source correspondence",
    re.I,
)
MATH = re.compile(r"\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]")
REFERENCE = re.compile(
    r"^(?:\[S?\d+\]|S\d+[.:]|E\d+[.:]|\d+\s+[A-Z]|https?://)|"
    r"\b(?:arXiv:\d|PMLR\s+\d|Proceedings of|Journal of|JMLR\s+\d)",
    re.I,
)
WORKFLOW_MARKER = re.compile(
    r"provenance(?:\.json|/checkpoint)|artifact_integrity|"
    r"\b(?:TeX|report) compiler\b|compiler (?:log|record|diagnostic|identity)|"
    r"\bLumen\b|\bbatch token\b|\btask packet\b|"
    r"\bmodel visibility\b|\bparent assistant\b|\bnative auxiliary\b|"
    r"\bauxiliary agents?\b|\bAI (?:roles?|reviewer|subagents?)\b|"
    r"\bprimary (?:assistant|AI reviewer)\b|"
    r"\bcontroller (?:acceptance|file|promotion|receipt)|by the controller|"
    r"\breport (?:PDF|TeX|pages)\b|\bcompiled (?:report|PDF|TeX)\b|"
    r"\bselected.model\b|\bruntime model\b|\bbuild\.json\b",
    re.I,
)
ROLE = re.compile(
    r"^(?:roles?[.:]|AI roles?[.:]|(?:the )?(?:primary (?:AI )?(?:reviewer|assistant)|"
    r"parent(?: assistant)?|native auxiliaries|native auxiliary agents?|"
    r"auxiliary agents?|AI reviewer|two .*? agents?|three .*? agents?|"
    r"separate .*? AI units?|reviewer roles?))|"
    r"\b(?:actual model visibility|formally selected|selected.model label|"
    r"runtime model|not human acceptance|AI artifact check|"
    r"human user supplied|user supplied the assignment)\b",
    re.I,
)
MODEL_NARRATION = re.compile(
    r"GPT[- ]6\s+Astra|(?:selected|task.selected)[- /]?model (?:field|label)|"
    r"(?:task.selected|exposed)(?: task)?[- /]?(?:parent )?(?:model|label|identity)|"
    r"runtime model\s*(?:[:;]|label|identity|identifier)|"
    r"model visibility|conversation (?:URL|linkage)|"
    r"(?:native auxiliary|auxiliary)(?: reviewer| agent)|"
    r"(?:parent|primary) AI|AI support agents?|AI subagents?|"
    r"\b6 Pro\b|selected task(?:.model)? label|actual visible model|"
    r"visible UI model|model.selector observation|"
    r"(?:selected|requested|exposed) (?:task |parent )?label",
    re.I,
)
EXPLICIT_REVIEW_ROLE = re.compile(
    r"\bnative auxiliar(?:y|ies)\b|\bprimary assistant\b|"
    r"\bAI (?:sub.agent|checker)\b",
    re.I,
)
BUILD = re.compile(
    r"\b(?:report PDF|report TeX|final TeX|self.contained TeX|"
    r"companion PDF|report pages|compiler (?:logs?|records?|diagnostics?|identity)|"
    r"(?:report|TeX|PDF) compilation|compilation (?:logs?|records?|receipts?)|"
    r"TeX compiler|"
    r"HTML renderer|PDF renderer|rendering receipt|visual.QA record|"
    r"artifact.integrity|compiled.source|source and output hashes|"
    r"build\.json|provenance\.json|provenance/checkpoint|"
    r"required artifacts|artifact inventory|machine.readable coverage|"
    r"initial.review and proposal build history|TeX engine|"
    r"TeX (?:was not compiled|is self.contained))\b",
    re.I,
)
INTERNAL_FILES = re.compile(
    r"\b(?:verification|sources)/\d{4}/|verification directory|"
    r"(?:numeric|assigned) (?:verification|source|staging) directory|"
    r"\b(?:coverage|findings|provenance|checkpoint|artifact_integrity)\.json\b|"
    r"input_check\.json|independent_check_execution\.json|"
    r"source_download\.json|acquisition (?:records|receipts|manifests)|"
    r"archive CRC|member mappings|source/member identities|"
    r"byte.level recheck|path lengths|source and output hashes",
    re.I,
)
PDF_HASH = re.compile(
    r"(?:source|original|reviewed|decisive evaluator|exact source)\s+"
    r"(?:PDF\s+)?(?:SHA[- ]?256|hash)|\bpacket SHA[- ]?256|"
    r"^The (?:unchanged source manifest|exact source PDF)",
    re.I,
)
TASK = re.compile(
    r"^(?:batch token|task(?: file)?\s*(?::|\[|B00[1-4]\b)|review context:)|"
    r"\[internal (?:task|identifier omitted)\]|"
    r"conversation linkage|scientific contract \d{4}-\d{2}-\d{2}",
    re.I,
)
OPERATIONS = re.compile(
    r"\bLumen\b|\btask.packet\b|\btask packet\b|"
    r"\btask and batch token\b|\bbatch token\b|"
    r"\btransport acknowledgement\b|"
    r"\b(?:direct|native) PDF (?:reader|read)\b|"
    r"\b(?:report|delivery|completion)[_. ](?:validation|hashes|receipts?)\b|"
    r"\b(?:artifact.check|build_report\.py|completion_validation\.json)\b",
    re.I,
)
SCOPE = re.compile(
    r"not (?:performed|reproduced|established|executed|available|verified)|"
    r"unavailable|inaccessible|unresolved|not establish|does not establish|"
    r"not evidence|no (?:author code|training|human review)|"
    r"scientific (?:adjudication|review).*pending|"
    r"not.*(?:experiment|historical)|\bretains? (?:the |its )?rate\b",
    re.I,
)
SCIENTIFIC_SCOPE = re.compile(
    r"unverified|not (?:independently|verified|performed|reproduced|executed|"
    r"rederived|audited|inspected|searched|available)|"
    r"(?:no|not)\b[^.!?]*(?:author.code|trained|training|empirical|dataset|"
    r"weight|checkpoint|cache.test|historical|errat|later.version|raw.data)|"
    r"does not establish|not establish|cannot (?:establish|infer)|"
    r"does not (?:prove|imply)|partial (?:check|coverage)|"
    r"not (?:exhaustive|full|complete)|only selected|"
    r"rejected[^.!?]*(?:Major|Minor)|(?:Major|Minor)[^.!?]*not retained",
    re.I,
)
SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+(?=[A-Z>])")


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _heading(text):
    match = HEADING.match(text.strip())
    return (len(match[1]), match[2]) if match else None


def _workflow_heading(text):
    info = _heading(text)
    return bool(
        info
        and WORKFLOW_HEADING.search(info[1])
        and not EXCLUDED_HEADING.search(info[1])
    )


def _command_only(text):
    if not text.startswith("Code:\n"):
        return False
    lines = [line.strip() for line in text[6:].splitlines() if line.strip()]
    return bool(lines) and all(
        re.match(
            r"^(?:[>$]\s*)?(?:tectonic|(?:pdf|xe|lua)latex|pdfinfo|pdftoppm|"
            r"pdftotext|Get-FileHash|sha256sum|Get-Item|ls\b|dir\b|"
            r"python(?:\s+-[^ ]+)*\s+(?:verification|sources)/\d{4}/)",
            line,
            re.I,
        )
        for line in lines
    )


def _operation_only_block(text):
    """Recognize reviewed shell invocations/artifact lists, never program bodies."""
    if not text.startswith("Code:\n"):
        return False
    lines = [line.strip() for line in text[6:].splitlines() if line.strip()]
    return bool(lines) and all(
        re.match(
            r"^(?:#|[>$]|& |python\b|pdfto(?:text|ppm|html)\b|"
            r"Get-FileHash\b|tectonic\b|pdfinfo\b|"
            r"(?:PDF|Publisher PDF|Original|SHA-256|Pinned .+ code commit|"
            r"Pinned public code commit|Batch token|Source PDF|Extraction|"
            r"Visual evidence|Independent check|Check output|"
            r"Replay source verification|Extract source|Render report)"
            r"[^:=]*(?:[:=]|$)|[0-9a-f]{40,70}$|"
            r"\[internal identifier omitted\]$|\[local archive path omitted\]$|"
            r"[.'\"<]*(?:sources|papers|verification|reports|\.{3})(?:[/\\])|"
            r"\(N =)",
            line,
            re.I,
        )
        for line in lines
    )


def _sentence_reason(text, workflow):
    if TASK.search(text):
        return "internal task/controller metadata"
    if MODEL_NARRATION.search(text):
        return "review-model and internal role metadata"
    if EXPLICIT_REVIEW_ROLE.search(text):
        return "explicit internal review-role narration"
    if ROLE.search(text) and (
        workflow
        or re.search(
            r"^AI roles?[.:]|^Roles?[.:]|parent assistant|"
            r"runtime model\s*(?:[:;]|label|identity|identifier)|"
            r"selected.model label|not human acceptance|AI artifact check",
            text,
            re.I,
        )
    ):
        return "review-agent and workflow narration"
    if BUILD.search(text) and (
        workflow
        or re.search(
            r"report|TeX|compiler|HTML renderer|provenance|Lumen|"
            r"initial.review|artifact|final.source|compiled.source",
            text,
            re.I,
        )
    ):
        return "report build/file bookkeeping"
    if OPERATIONS.search(text):
        return "internal tool/build operation log"
    if workflow and INTERNAL_FILES.search(text):
        return "internal evidence-directory inventory"
    if workflow and PDF_HASH.search(text):
        return "report/source hash bookkeeping"
    if workflow and re.search(
        r"\b(?:source snapshots?|their hashes|compile|visually inspected|"
        r"rendered with|software was installed|software installation|"
        r"earlier attempts|final archives|unchanged archives|"
        r"original archives|member mappings|model/API money)\b",
        text,
        re.I,
    ):
        return "review/build operation log"
    return None


def _clean_body(text, workflow):
    if text.startswith("Code:\n"):
        return (
            text,
            None,
            ["operational command block retained for explicit review"]
            if _command_only(text)
            else [],
        )
    if (
        re.search(r"workflow attribution", text, re.I)
        and "Scientific Agent Skills" in text
    ) or re.match(r"Controller build revision[.:]", text, re.I):
        return None, "internal workflow attribution/build history", []
    if re.match(r"^(?:\[S?\d+\]|[SE]\d+\s*[-–—.:])", text, re.I):
        return text, None, []
    original_text = text
    text = _neutralize_review_phrasing(text)
    protected = []

    def protect(match):
        protected.append(match[0])
        return "ELVIAPROTECTEDMATH" + str(len(protected) - 1) + "END"

    hidden = MATH.sub(protect, text)
    sentences = SENTENCE_BOUNDARY.split(hidden)
    sentences = [
        re.sub(
            r"ELVIAPROTECTEDMATH(\d+)END",
            lambda match: protected[int(match[1])],
            sentence,
        )
        for sentence in sentences
    ]
    kept, reasons, review = [], [], []
    for sentence in sentences:
        reason = _sentence_reason(sentence, workflow)
        if reason:
            if SCIENTIFIC_SCOPE.search(sentence):
                kept.append(sentence)
                review.append("scientific boundary mixed with workflow narration")
            elif MATH.search(sentence):
                kept.append(sentence)
                review.append("mathematical sentence also contains workflow narration")
            elif REFERENCE.search(sentence) and not TASK.search(sentence):
                kept.append(sentence)
                review.append("citation mixed with workflow narration")
            elif SCOPE.search(sentence) and not (
                BUILD.search(sentence) or ROLE.search(sentence) or TASK.search(sentence)
            ):
                kept.append(sentence)
                review.append("scientific scope mixed with internal-file inventory")
            else:
                reasons.append(reason)
        else:
            kept.append(sentence)
    if not reasons:
        return (
            text,
            "neutralize explicit review-role phrasing"
            if text != original_text
            else None,
            review,
        )
    value = " ".join(kept).strip()
    if workflow and value in {"", ".", ";", ":"}:
        value = ""
    return value or None, "; ".join(sorted(set(reasons))) or None, review


def _neutralize_review_phrasing(text):
    """Only substitute an explicit review actor, preserving the checked claim."""
    verbs = (
        r"checked|computed|recomputed|recalculated|verified|inspected|read|"
        r"rederived|traced|replayed|transcribed|enumerated|derived|evaluated|"
        r"rendered|ran|executed|performed|compared|rechecked|reviewed|"
        r"normalized|parsed|confirmed|visually checked"
    )
    pieces = re.split(r"(\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\])", text)
    for index in range(0, len(pieces), 2):
        value = pieces[index]
        value = re.sub(
            r"\b(?:The |the )?parent(?: assistant| AI)?(?= (?:independently )?(?:"
            + verbs
            + r")\b)",
            "The independent check",
            value,
        )
        value = re.sub(
            r"\b[Pp]arent[- ](?:authored|written|owned)\b",
            "Independently authored",
            value,
        )
        value = re.sub(
            r"\b[Pp]arent (?=normalization|calculations|static reads)",
            "Independent ",
            value,
        )
        value = re.sub(
            r"\bcontroller (?:acquisition )?receipt\b",
            "source-acquisition record",
            value,
            flags=re.I,
        )
        value = re.sub(
            r"\bcontroller (?:file )?acceptance\b",
            "publication status",
            value,
            flags=re.I,
        )
        value = re.sub(r"\buser/controller\b", "maintainer", value, flags=re.I)
        value = re.sub(
            r"\bController calibration revision\b", "Calibration revision", value
        )
        pieces[index] = value
    return "".join(pieces)


def _hash_display(span):
    """Recognize only the reviewed TeX typesetting of an artifact digest."""
    if not span.startswith(r"\["):
        return False
    body = span[2:-2]
    body = re.sub(r"\\(?:begin|end)\{gathered\}", "", body)
    pieces = re.findall(r"\\texttt\{([0-9a-f]+)\}", body, re.I)
    remainder = re.sub(r"\\texttt\{[0-9a-f]+\}", "", body, flags=re.I)
    remainder = remainder.replace(r"\\", "").strip(" .\r\n\t")
    return bool(pieces) and not remainder and 55 <= len("".join(pieces)) <= 70


def reviewed_table():
    return json.loads(
        Path(__file__).with_name("report_cleanup_reviewed.json").read_text("utf-8")
    )["cases"]


def clean_paragraphs(paragraphs, *, case_id=None, reviewed=None):
    """Return conservative, SHA-bound edits using the original paragraph indices.

    Equations/full independent-check programs are kept byte-for-byte. Mixed
    paragraphs which cannot be safely separated are retained and flagged. No
    findings, impact labels, source versions, citations or review state are inferred.
    """
    if not all(isinstance(text, str) and text.strip() for text in paragraphs):
        raise ValueError("report paragraphs must be nonempty strings")
    if reviewed is None:
        reviewed = reviewed_table().get(case_id, []) if case_id else []
    approved = {row["index"]: row for row in reviewed}
    if len(approved) != len(reviewed):
        raise ValueError("duplicate reviewed paragraph index")
    for index, row in approved.items():
        if (
            not 0 <= index < len(paragraphs)
            or digest(paragraphs[index]) != row["before_sha256"]
        ):
            raise ValueError("reviewed paragraph does not match its frozen source")
    staged, edits, review, applied = list(paragraphs), [], [], []
    removed_hashes, removed_commands, removed_inventories = [], set(), set()
    code_prefix_cleaned = {}
    workflow_level = None
    workflow_headers = []
    for index, text in enumerate(paragraphs):
        info = _heading(text)
        if info:
            if workflow_level is not None and info[0] <= workflow_level:
                workflow_level = None
            if index in approved:
                row = approved[index]
                value = text if row.get("mode") == "keep" else row["after"]
                if value is not None and not _heading(value):
                    raise ValueError(
                        "reviewed heading must remain a heading or be null"
                    )
                staged[index] = value
                applied.append(
                    {
                        "index": index,
                        "before_sha256": digest(text),
                        "after": value,
                        "kind": row["kind"],
                    }
                )
                if value != text:
                    edits.append(
                        {
                            "index": index,
                            "before_sha256": digest(text),
                            "before": text,
                            "after": value,
                            "reason": row["kind"],
                        }
                    )
                continue
            if _workflow_heading(text):
                workflow_level = info[0]
                workflow_headers.append(index)
            continue
        if index in approved:
            row = approved[index]
            value = text if row.get("mode") == "keep" else row["after"]
            reason = row["kind"]
            ambiguous = []
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError("reviewed replacement must be readable or null")
            for span in row.get("allowed_removed_math_spans", []):
                if (
                    not _hash_display(span)
                    or span not in text
                    or not re.search(r"SHA-256|PDF hash", text, re.I)
                ):
                    raise ValueError("only an artifact hash display may be exempted")
                removed_hashes.append(span)
            if reason == "remove_operational_command":
                if value is not None or not _command_only(text):
                    raise ValueError(
                        "reviewed command removal is not an operation-only block"
                    )
                removed_commands.add(index)
            elif reason == "remove_operational_block":
                if not _operation_only_block(text) or (
                    value is not None and value.startswith("Code:\n")
                ):
                    raise ValueError("reviewed artifact block contains scientific code")
                removed_inventories.add(index)
            elif reason == "remove_operational_code_prefix":
                if not isinstance(value, str) or not value.startswith("Code:\nResult:"):
                    raise ValueError(
                        "operation prefix cleanup must preserve its result"
                    )
                prefix, marker, tail = text.partition("\nResult:")
                if (
                    not marker
                    or not _operation_only_block(prefix)
                    or value != "Code:" + marker + tail
                ):
                    raise ValueError(
                        "operation prefix cleanup changed scientific result"
                    )
                code_prefix_cleaned[index] = value
            elif reason == "remove_operational_code_lines":
                if not isinstance(value, str) or not value.startswith("Code:\n"):
                    raise ValueError("operation line cleanup must retain code results")
                lines = text[6:].splitlines(keepends=True)
                removed_lines = row.get("removed_lines", [])
                if (
                    not removed_lines
                    or len(set(removed_lines)) != len(removed_lines)
                    or not all(0 <= n < len(lines) for n in removed_lines)
                    or not _operation_only_block(
                        "Code:\n" + "".join(lines[n] for n in sorted(removed_lines))
                    )
                    or value
                    != "Code:\n"
                    + "".join(
                        line for n, line in enumerate(lines) if n not in removed_lines
                    )
                ):
                    raise ValueError("operation line cleanup changed scientific result")
                code_prefix_cleaned[index] = value
            applied.append(
                {
                    "index": index,
                    "before_sha256": digest(text),
                    "after": value,
                    "kind": reason,
                }
            )
        else:
            value, reason, ambiguous = _clean_body(text, workflow_level is not None)
        staged[index] = value
        if value != text:
            edits.append(
                {
                    "index": index,
                    "before_sha256": digest(text),
                    "before": text,
                    "after": value,
                    "reason": reason,
                }
            )
        for why in ambiguous:
            review.append(
                {
                    "index": index,
                    "before_sha256": digest(text),
                    "text": text,
                    "reason": why,
                }
            )

    for index in workflow_headers:
        level = _heading(paragraphs[index])[0]
        end = next(
            (
                i
                for i in range(index + 1, len(paragraphs))
                if _heading(paragraphs[i]) and _heading(paragraphs[i])[0] <= level
            ),
            len(paragraphs),
        )
        remaining = [text for text in staged[index + 1 : end] if text is not None]
        if not remaining:
            value = None
        else:
            if all(REFERENCE.search(text) for text in remaining):
                value = "#" * level + " References"
            elif all(
                SCOPE.search(text) and not MATH.search(text) for text in remaining
            ):
                value = "#" * level + " Scope and limitations"
            elif all(
                REFERENCE.search(text) or SCOPE.search(text) for text in remaining
            ):
                value = "#" * level + " Scope and references"
            else:
                value = "#" * level + " Supporting checks"
        if value != paragraphs[index]:
            staged[index] = value
            edits.append(
                {
                    "index": index,
                    "before_sha256": digest(paragraphs[index]),
                    "before": paragraphs[index],
                    "after": value,
                    "reason": "remove empty workflow heading"
                    if value is None
                    else (
                        "retain scientific/reference content "
                        "under a reader-facing heading"
                    ),
                }
            )
    result = [text for text in staged if text is not None]
    original_math = [match[0] for text in paragraphs for match in MATH.finditer(text)]
    exempt = Counter(removed_hashes)
    scientific_math = []
    for span in original_math:
        if exempt[span]:
            exempt[span] -= 1
        else:
            scientific_math.append(span)
    if any(exempt.values()):
        raise ValueError("reviewed hash display is not present in the original")
    cleaned_math = [match[0] for text in result for match in MATH.finditer(text)]
    if scientific_math != cleaned_math:
        raise ValueError("cleanup changed mathematical source spans")
    protected_code = [
        code_prefix_cleaned.get(i, text)
        for i, text in enumerate(paragraphs)
        if text.startswith("Code:\n")
        and i not in removed_commands
        and i not in removed_inventories
    ]
    if protected_code != [text for text in result if text.startswith("Code:\n")]:
        raise ValueError("cleanup removed a scientific check program")
    return {
        "paragraphs": result,
        "edits": sorted(edits, key=lambda row: row["index"]),
        "removed_indices": sorted(ed["index"] for ed in edits if ed["after"] is None),
        "replaced": sorted(ed["index"] for ed in edits if ed["after"] is not None),
        "review": review,
        "reviewed": applied,
        "preserved_math": len(scientific_math),
        "removed_hash_displays": len(removed_hashes),
        "removed_operational_commands": len(removed_commands),
        "removed_operation_inventory_blocks": len(removed_inventories),
        "code_results_prefix_cleaned": len(code_prefix_cleaned),
        "preserved_code_blocks": len(protected_code),
    }


def render_icml_tex_legacy(paragraphs):
    """Reproduce the retained pre-formatting TeX for source identity checks."""
    tex_text = runpy.run_path(
        str(Path(__file__).with_name("import_review_collection.py"))
    )["tex_text"]
    return "\n".join(
        [
            r"\documentclass[10pt]{article}",
            r"\usepackage[margin=20mm]{geometry}",
            r"\usepackage{amsmath,amssymb,fontspec,unicode-math,xurl,hyperref}",
            r"\IfFontExistsTF{DejaVu Serif}{\setmainfont{DejaVu Serif}}"
            r"{\setmainfont{Latin Modern Roman}}",
            r"\setmathfont{latinmodern-math.otf}",
            r"\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}\sloppy",
            r"\begin{document}",
            *[
                (
                    r"{\ttfamily\footnotesize "
                    + "".join(tex_text(c) for c in text[6:]).replace("\n", "\\\\\n")
                    + "}"
                    + r"\par"
                )
                if text.startswith("Code:\n")
                else tex_text(text) + r"\par"
                for text in paragraphs
            ],
            r"\end{document}",
            "",
        ]
    )


def _report_front_matter(paragraphs):
    """Read explicit report header fields; infer no author, title or date."""
    fields, indices = {}, {}
    for index, text in enumerate(paragraphs):
        if index >= 16 or _heading(text):
            break
        match = re.fullmatch(r"(Title|Author|Date):\s*([\s\S]*)", text, re.I)
        if match:
            name, value = match[1].lower(), match[2].strip()
            if name in fields:
                raise ValueError("duplicate report front-matter field")
            fields[name], indices[index] = value, name
    return fields, indices


@cache
def _citation_renderer():
    return runpy.run_path(str(Path(__file__).with_name("icml_report_text.py")))[
        "render_latex_citation"
    ]


def _normalize_retained_citations(text):
    if text.startswith("Code:\n"):
        return text, 0, False
    pattern = re.compile(
        r"\[Retained (?:latex|tex):\s*"
        r"(\\cite\s*(?:\[[^\[\]]*\]\s*)?\{[^{}]*\})\s*\]"
    )
    count = 0

    def replace(match):
        nonlocal count
        rendered = _citation_renderer()(match[1])
        if rendered is None:
            return match[0]
        count += 1
        return rendered

    pieces = re.split(r"(\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\])", text)
    unknown = False
    for index in range(0, len(pieces), 2):
        pieces[index] = pattern.sub(replace, pieces[index])
        unknown = unknown or bool(
            re.search(r"\[Retained (?:latex|tex):", pieces[index])
        )
    return "".join(pieces), count, unknown


def format_report_paragraphs(paragraphs, *, case_id=None, overrides=()):
    """Apply only reviewed sparse overlays and remove empty report-header fields."""
    if not all(isinstance(text, str) and text.strip() for text in paragraphs):
        raise ValueError("report paragraphs must be nonempty strings")
    selected = [
        row
        for row in overrides
        if case_id is None or row.get("case", case_id) == case_id
    ]
    approved = {row["index"]: row for row in selected}
    if len(approved) != len(selected):
        raise ValueError("duplicate formatting override paragraph index")
    staged = list(paragraphs)
    reasons = {}
    review, citations = [], 0
    for index, row in approved.items():
        if (
            not 0 <= index < len(paragraphs)
            or row.get("before") != paragraphs[index]
            or row.get("before_sha256") != digest(paragraphs[index])
        ):
            raise ValueError("formatting override does not match its frozen source")
        after = row["after"]
        if after is not None and (not isinstance(after, str) or not after.strip()):
            raise ValueError("formatting override must be readable or null")
        staged[index] = after
        reasons[index] = row.get("reason", "reviewed publication-copy overlay")
    for index, text in enumerate(staged):
        if text is None:
            continue
        normalized, count, unknown = _normalize_retained_citations(text)
        citations += count
        if normalized != text:
            staged[index] = normalized
            reasons[index] = "normalize retained citation keys and explicit page notes"
        if unknown:
            review.append(
                {
                    "index": index,
                    "before_sha256": digest(paragraphs[index]),
                    "text": text,
                    "reason": "unrecognized retained LaTeX wrapper; kept for review",
                }
            )
    retained = [(i, text) for i, text in enumerate(staged) if text is not None]
    _, metadata = _report_front_matter([text for _, text in retained])
    for retained_index, name in metadata.items():
        index, text = retained[retained_index]
        if not text.partition(":")[2].strip():
            staged[index] = None
            reasons[index] = f"omit empty {name} header field"
    result = [text for text in staged if text is not None]
    before_math = [m[0] for text in paragraphs for m in MATH.finditer(text)]
    after_math = [m[0] for text in result for m in MATH.finditer(text)]
    if before_math != after_math:
        raise ValueError("formatting overlay changed mathematical source spans")
    before_code = [text for text in paragraphs if text.startswith("Code:\n")]
    after_code = [text for text in result if text.startswith("Code:\n")]
    if before_code != after_code:
        raise ValueError("formatting overlay changed a scientific code block")
    edits = [
        {
            "index": index,
            "before_sha256": digest(text),
            "before": text,
            "after": staged[index],
            "reason": reasons[index],
        }
        for index, text in enumerate(paragraphs)
        if staged[index] != text
    ]
    return {
        "paragraphs": result,
        "edits": edits,
        "removed_indices": [row["index"] for row in edits if row["after"] is None],
        "replaced": [row["index"] for row in edits if row["after"] is not None],
        "review": review,
        "reviewed": [dict(row) for row in selected],
        "preserved_math": len(before_math),
        "preserved_code_blocks": len(before_code),
        "normalized_citation_wrappers": citations,
        "scientific_math_before_sequence_sha256": digest(
            json.dumps(before_math, ensure_ascii=False)
        ),
        "scientific_math_after_sequence_sha256": digest(
            json.dumps(after_math, ensure_ascii=False)
        ),
        "scientific_code_before_sequence_sha256": digest(
            json.dumps(before_code, ensure_ascii=False)
        ),
        "scientific_code_after_sequence_sha256": digest(
            json.dumps(after_code, ensure_ascii=False)
        ),
    }


def render_icml_tex(paragraphs):
    """Render explicit header metadata and real section levels without prose edits."""
    tex_text = runpy.run_path(
        str(Path(__file__).with_name("import_review_collection.py"))
    )["tex_text"]
    fields, metadata = _report_front_matter(paragraphs)
    has_title = bool(fields.get("title"))
    preamble = render_icml_tex_legacy([]).split(r"\begin{document}", 1)[0]
    declarations = []
    if has_title:
        declarations = [
            r"\title{" + tex_text(fields["title"]) + "}",
            r"\author{" + tex_text(fields.get("author", "")) + "}",
            r"\date{" + tex_text(fields.get("date", "")) + "}",
        ]
    body = [r"\maketitle"] if has_title else []
    commands = (
        "section",
        "subsection",
        "subsubsection",
        "paragraph",
        "subparagraph",
        "subparagraph",
    )
    for index, text in enumerate(paragraphs):
        if index in metadata:
            if has_title or not fields[metadata[index]]:
                continue
        if text.startswith("Code:\n"):
            body.append(
                r"{\ttfamily\footnotesize "
                + "".join(tex_text(c) for c in text[6:]).replace("\n", "\\\\\n")
                + "}"
                + r"\par"
            )
        elif info := _heading(text):
            level, title = info
            contents = tex_text(title)
            if level == 6:
                contents = r"\normalfont\itshape " + contents
            rendered = "\\" + commands[level - 1] + "*{" + contents + "}"
            body.append(rendered + (r"\mbox{}\par" if level >= 4 else ""))
        else:
            body.append(tex_text(text) + r"\par")
    return (
        preamble
        + "\n".join(declarations + [r"\begin{document}"] + body)
        + "\n"
        + r"\end{document}"
        + "\n"
    )


def _load_format_overrides(overrides):
    if overrides is None:
        return []
    if isinstance(overrides, (str, Path)):
        overrides = json.loads(Path(overrides).read_text("utf-8"))
    if isinstance(overrides, dict):
        overrides = overrides["overrides"]
    if not isinstance(overrides, list):
        raise ValueError("formatting overrides must be a list of frozen rows")
    return overrides


def build_format_plan(root, output, *, overrides=None):
    """Write formatting candidates against current reports; never run the cleaner."""
    root, output = Path(root), Path(output)
    rows = _load_format_overrides(overrides)
    grouped = {}
    for row in rows:
        grouped.setdefault(row["case"], []).append(row)
    plan = {
        "format_version": 1,
        "scope": "Report template formatting and explicitly reviewed sparse overlays.",
        "cases": {},
        "counts": {},
    }
    totals = Counter()
    output.mkdir(parents=True, exist_ok=False)
    seen = set()
    for collection in ("icml2025", "neurips2025"):
        dataset = root / "studies" / collection
        notes = json.loads((dataset / "case-notes.json").read_text("utf-8"))["cases"]
        for source in sorted((dataset / "evidence").glob("*/report.tex")):
            case = source.parent.name
            original = source.read_text("utf-8")
            totals["reports_scanned"] += 1
            item = {
                "collection": collection,
                "source_tex_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "changed": False,
                "review": [],
            }
            if collection == "neurips2025":
                if case in grouped:
                    raise ValueError(
                        "NeurIPS report overrides are outside formatting scope"
                    )
                totals["standard_reports_unchanged"] += 1
            else:
                paragraphs = notes[case]["report"]
                if original not in {
                    render_icml_tex_legacy(paragraphs),
                    render_icml_tex(paragraphs),
                }:
                    raise ValueError(
                        f"{case}: report does not match its frozen paragraphs"
                    )
                item.update(
                    format_report_paragraphs(
                        paragraphs, case_id=case, overrides=grouped.get(case, [])
                    )
                )
                rendered = render_icml_tex(item["paragraphs"])
                text = "\n\n".join(item["paragraphs"]) + "\n"
                item.update(
                    source_text_sha256=hashlib.sha256(
                        source.with_suffix(".txt").read_bytes()
                    ).hexdigest(),
                    report_paragraphs_sha256=digest(
                        json.dumps(paragraphs, ensure_ascii=False)
                    ),
                    original_paragraph_sha256=[digest(text) for text in paragraphs],
                    changed=bool(item["edits"]) or rendered != original,
                    tex_changed=rendered != original,
                    formatting_only=True,
                )
                seen.add(case)
                if item["changed"]:
                    destination = output / "candidates" / case
                    destination.mkdir(parents=True)
                    (destination / "report.tex").write_text(
                        rendered, encoding="utf-8", newline="\n"
                    )
                    (destination / "report.txt").write_text(
                        text, encoding="utf-8", newline="\n"
                    )
                totals["reports_changed"] += item["changed"]
                totals["tex_only_reports"] += item["changed"] and not item["edits"]
                totals["paragraphs_removed"] += len(item["removed_indices"])
                totals["paragraphs_replaced"] += len(item["replaced"])
                totals["math_spans_preserved"] += item["preserved_math"]
                totals["scientific_code_blocks_preserved"] += item[
                    "preserved_code_blocks"
                ]
                totals["reviewed_overrides"] += len(item["reviewed"])
                totals["citation_wrappers_normalized"] += item[
                    "normalized_citation_wrappers"
                ]
                totals["review_cases"] += bool(item["review"])
                totals["review_paragraphs"] += len(item["review"])
            plan["cases"][case] = item
    unknown = set(grouped) - seen
    if unknown:
        raise ValueError(
            "unknown formatting override case: " + ", ".join(sorted(unknown))
        )
    plan["counts"] = dict(totals)
    (output / "plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return plan


def build_plan(root, output):
    """Scan the two maintained collections and write candidates only to NEW output."""
    root, output = Path(root), Path(output)
    output.mkdir(parents=True, exist_ok=False)
    plan = {
        "format_version": 1,
        "scope": (
            "Publication prose only; no scientific reassessment "
            "or author-code execution."
        ),
        "cases": {},
        "counts": {},
    }
    totals = Counter()
    for collection in ("icml2025", "neurips2025"):
        dataset = root / "studies" / collection
        notes = json.loads((dataset / "case-notes.json").read_text("utf-8"))["cases"]
        for source in sorted((dataset / "evidence").glob("*/report.tex")):
            case = source.parent.name
            original = source.read_text("utf-8")
            rows = notes.get(case, {}).get("report")
            totals["reports_scanned"] += 1
            if rows is None:
                unexpected = bool(
                    re.search(
                        r"native auxiliary|parent assistant|model visibility|"
                        r"batch token|Lumen",
                        original,
                        re.I,
                    )
                )
                item = {
                    "collection": collection,
                    "source_tex_sha256": hashlib.sha256(
                        source.read_bytes()
                    ).hexdigest(),
                    "changed": False,
                    "format": "structured scientific report",
                    "review": ["unexpected workflow marker in standard report"]
                    if unexpected
                    else [],
                }
                totals["standard_reports_unchanged"] += 1
            else:
                if render_icml_tex_legacy(rows) != original:
                    raise ValueError(
                        f"{case}: transcription does not reproduce retained report TeX"
                    )
                item = clean_paragraphs(rows, case_id=case)
                item.update(
                    collection=collection,
                    source_tex_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                    source_text_sha256=hashlib.sha256(
                        source.with_suffix(".txt").read_bytes()
                    ).hexdigest(),
                    report_paragraphs_sha256=digest(
                        json.dumps(rows, ensure_ascii=False)
                    ),
                    original_paragraph_sha256=[digest(text) for text in rows],
                    changed=bool(item["edits"])
                    or render_icml_tex(item["paragraphs"]) != original,
                )
                if item["changed"]:
                    destination = output / "candidates" / case
                    destination.mkdir(parents=True)
                    (destination / "report.txt").write_text(
                        "\n\n".join(item["paragraphs"]) + "\n",
                        encoding="utf-8",
                        newline="\n",
                    )
                    (destination / "report.tex").write_text(
                        render_icml_tex(item["paragraphs"]),
                        encoding="utf-8",
                        newline="\n",
                    )
                totals["reports_changed"] += item["changed"]
                totals["paragraphs_removed"] += len(item["removed_indices"])
                totals["paragraphs_replaced"] += len(item["replaced"])
                totals["math_spans_preserved"] += item["preserved_math"]
                totals["non_scientific_hash_displays_removed"] += item[
                    "removed_hash_displays"
                ]
                totals["operational_command_blocks_removed"] += item[
                    "removed_operational_commands"
                ]
                totals["scientific_code_blocks_preserved"] += item[
                    "preserved_code_blocks"
                ]
                totals["operation_inventory_blocks_removed"] += item[
                    "removed_operation_inventory_blocks"
                ]
                totals["scientific_results_with_operation_prefix_removed"] += item[
                    "code_results_prefix_cleaned"
                ]
                totals["reviewed_replacements"] += len(item["reviewed"])
                totals["review_cases"] += bool(item["review"])
                totals["review_paragraphs"] += len(item["review"])
            plan["cases"][case] = item
    plan["counts"] = dict(totals)
    (output / "plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return plan


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--formatting-only", action="store_true")
    parser.add_argument("--overrides", type=Path)
    args = parser.parse_args()
    result = (
        build_format_plan(args.root, args.output, overrides=args.overrides)
        if args.formatting_only
        else build_plan(args.root, args.output)
    )
    print(json.dumps(result["counts"]))
