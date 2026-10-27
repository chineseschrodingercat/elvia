"""Source-section restoration must not attach another finding or a repair."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def module():
    path = Path(__file__).parents[1] / "scripts" / "restore_case_proofs.py"
    spec = importlib.util.spec_from_file_location("restore_case_proofs", path)
    value = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(value)
    return value


def test_native_sections_keep_continued_proof_and_stop_before_global_record():
    report = [
        "# Definitions and assumptions",
        r"Let \(x>0\) and \(f(x)=x^2\).",
        "# 3. Problem 1: the asserted identity fails",
        r"At \(x=2\), the left side is \(4\).",
        "# Problem 1 continued",
        r"The right side is \(2\), so the asserted equality is false.",
        "## Counterevidence and scope",
        "The separate linear identity is unaffected.",
        "# Supporting checks",
        "Compiler completed and an internal role accepted the output.",
    ]
    value = module()
    sections = value.problem_sections(report)
    assert len(sections) == 1
    assert sections[0]["number"] == 1
    restored = value.restore_section(report, sections[0])
    assert restored["proof"] == [report[3], report[5]]
    assert restored["scope"] == [report[7]]
    assert restored["setup"] == [report[1]]
    assert "Compiler" not in " ".join(restored["proof"])


def test_section_math_bars_are_not_mistaken_for_summary_table_rows():
    value = module()
    report = [
        r"Equation reference: eq:bad. Problem 1 (A norm bound fails). Let \(A=1\).",
        r"Then \(\|A\|=1\), whereas the asserted bound is \(0\).",
        "# Conclusion",
        "Problem 1 | Major | Pending",
    ]
    sections = value.problem_sections(report)
    assert len(sections) == 1
    assert value.restore_section(report, sections[0])["proof"] == [
        r"Let \(A=1\).",
        report[1],
    ]


def test_explicit_repair_section_is_not_restored_as_falsification_proof():
    value = module()
    report = [
        "# Problem 1: a displayed estimate is false",
        r"The admissible input \(x=0\) gives \(1\le 0\).",
        "## A proposed replacement algorithm",
        "Use an unrelated new estimator instead.",
        "## Counterevidence",
        "The defect does not affect the separate exact identity.",
    ]
    restored = value.restore_section(report, value.problem_sections(report)[0])
    assert restored["proof"] == [report[1]]
    assert restored["scope"] == [report[5]]
    assert restored["excluded_repair"] == [3]


def test_mismatched_report_and_finding_counts_do_not_get_sequentially_bound():
    value = module()
    report = [
        "# Problem 1: theory",
        "A complete theoretical check.",
        "# Problem 2: evaluation",
        "The evaluation loop does not execute actions.",
        "# Problem 3: training",
        "The trainer is absent.",
    ]
    problems = [{"id": f"p{i}"} for i in range(1, 6)]
    assert value.numbered_mapping(report, problems) is None


def test_dependency_in_a_source_heading_does_not_hide_the_decisive_check():
    value = module()
    report = [
        "# Problem 1: the released head can mix positions",
        "## Source correspondence and explicit dependency",
        r"Take \(W=\left(\begin{smallmatrix}0&1\\0&0\end{smallmatrix}\right)\).",
        r"Then the first output changes when only \(z_2\) changes.",
        "## Counterevidence and bounded consequence",
        "The fitted off-block entries might be zero; this is not guaranteed.",
    ]
    restored = value.restore_section(report, value.problem_sections(report)[0])
    assert restored["proof"] == report[2:4]
    assert restored["scope"] == [report[5]]


def test_full_trace_under_claim_and_check_is_not_replaced_by_old_summary():
    value = module()
    report = [
        "# Problem 1: the branch reverses the response",
        "## Claim and check",
        "For input zero the code enters the inclusion branch.",
        "Soundness rejects the nonmember, so an honest response is rejected.",
    ]
    restored = value.restore_section(report, value.problem_sections(report)[0])
    fields = value.restored_fields(
        {
            "claim": ["The verifier rejects an honest nonmembership response."],
            "analysis": ["Old terse check."],
            "assessment": "supported",
            "severity": "major",
        },
        restored,
    )
    assert fields["analysis"] == report[2:]
    assert fields["analysis_heading"] == "Proof"
