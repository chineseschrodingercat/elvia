# LogicTree: Improving Complex Reasoning of LLMs via Instantiated Multi-step Synthetic Logical Data



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Matching an attached symbolic expression cannot certify the meaning of its English sentence. The paper’s own post-filter judgments acknowledge remaining inconsistency; no actual erroneous dataset row is established here.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: String identity does not establish semantic equivalence

Assessment: supported; impact: minor



Source: Section 3.3, PDF p.5; Appendix B.5, PDF p.18, Table 8



### Source claim (paraphrase)

Section 3.3 compares generated formula strings with source formulas and then describes the natural-language reasoning as validated.



### Analysis

The valid symbolic tree is \(P\to Q,P\vdash Q\). Let the English first premise instead mean \(Q\to P\), while attaching the expected string \(P\to Q\). Every formula-string comparison passes. The valuation \(P=\mathrm{true},Q=\mathrm{false}\) satisfies the actual English premises and falsifies the conclusion. This is a constructed failure of certification, not an observed training row. Appendix B.5 separately reports consistency judgments of \(97.6\%\) and \(96.8\%\).



### Finding and scope

The gate does not supply a universal semantic-validity guarantee. The source already presents quality improvement and residual fallibility.



### Proposed correction

A sound symbolic tree yields a valid English conclusion if every instantiated statement is semantically equivalent to its formula. String matching does not prove that additional premise; no corrected dataset is established.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
