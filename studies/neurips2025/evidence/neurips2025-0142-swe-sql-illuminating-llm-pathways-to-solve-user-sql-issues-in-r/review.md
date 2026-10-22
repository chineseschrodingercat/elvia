# SWE-SQL: Illuminating LLM Pathways to Solve User SQL Issues in Real-World Applications



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Released SQL comparison and normalization discard valid semantic distinctions. A later normalization update fixes some whitespace cases but leaves literal DISTINCT removal; average-tries reporting needs clarification rather than a presumed numeric correction.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The result comparator loses semantic distinctions and rejects correct empty results

Assessment: supported; impact: minor



Source: Appendices C–D, PDF p. 25; released PostgreSQL utility preprocess_results, lines 10–29, and ex_baselines, lines 92–134.



### Source claim (paraphrase)

Appendices C–D, PDF p. 25, describe functional SQL evaluation. The released PostgreSQL utility preprocess_results, lines 10–29, and ex_base, lines 86–132, discard duplicates/time-of-day and reject empty answers. Required ordering is also not enforced by set comparison.



### Analysis

Set comparison equates the row sequences \(((1),(1))\) and \(((1))\), losing multiplicity and any required order. Rejecting either empty list rejects two identical valid empty answers. Formatting timestamps as dates equates same-day values \(22\) hours apart. These are distinct valid-answer contracts that a general semantic comparator must preserve; their frequency in the final task tests is unknown.



### Finding and scope

This is a supported local finding within the stated source/formulation scope. Its effect on the paper's aggregate experimental results remains unmeasured.



## Problem 2: Removing DISTINCT with text operations changes valid SQL values and query structure

Assessment: supported; impact: minor



Source: Released PostgreSQL utility remove_distinct, lines 32–61; retained conference and current-source versions.



### Source claim (paraphrase)

The conference remove_distinct, lines 32–61 of the PostgreSQL utility, splits each complete SQL string on whitespace, removes tokens equal to distinct, and joins the remainder with single spaces. The current version instead uses a case-insensitive regular expression replacing every whole-word occurrence of DISTINCT with an empty string. The authors’ README explicitly announces an evaluation-code update to this function on \(8\) January 2026.



### Analysis

The current helper applies a case-insensitive whole-word regular expression to the entire SQL string. Thus the valid statement SELECT 'DISTINCT' AS value is changed into SELECT '' AS value. This changes a string value, rather than a SQL keyword. The former split/join behavior that collapsed double spaces or moved a statement into a line comment has been fixed and is excluded from the current defect. Actual benchmark incidence remains unknown.



### Finding and scope

This is a supported local finding within the stated source/formulation scope. Its effect on the paper's aggregate experimental results remains unmeasured.



## Problem 3: The denominator and stopping rule for Table 4’s average tries require clarification

Assessment: needs_evidence; impact: needs_evidence



Source: Section 4, PDF p. 5; Section 6.4, Table 4, PDF p. 9.



### Source claim (paraphrase)

Section 4, PDF p. 5, describes SIX-GYM as containing approximately \(3301\) generated training instances. Section 6.4 and Table 4, p. 9, compare trajectory generation on SIX-GYM. The Reject + f-Plan row has at most five tries, \(2560\) successful trajectories, and an average of \(1.7\) tries. The same table values remain in arXiv v4. The table itself does not explicitly specify its average’s denominator.

Suppose average tries means the mean over all \(3301\) tasks; each successfully solved task consumes at least one try; and each final failure exhausts all five allowed tries. These are an explicit interpretation being tested, not assumptions asserted as supported facts about the run.



### Analysis

Assume the mean covers all \(3301\) tasks, every one of \(2560\) successes takes at least one try, and each of \(741\) failures exhausts five tries. The mean must then be at least \((2560+5\cdot741)/3301\approx1.89791\), inconsistent with \(1.7\). A success-only denominator, early aborts or another averaging unit removes this contradiction. The table does not establish the assumptions, so no incorrect entry or replacement value is asserted.



### Finding and scope

Reporting ambiguity requiring denominator/stopping-rule evidence; no incorrect table entry or replacement number is established.



### Proposed correction

Specify the averaging unit, total attempts, success count and terminal-failure behavior.

A local correction or qualification is proposed where specified; author adoption is not established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
