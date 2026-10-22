# Datasets, Documents, and Repetitions: The Practicalities of Unequal Data Quality



Preliminary assessment: No Issue Found

Independent scientific review: pending. Author adoption: not requested.



The appendix's probabilistic rule has the advertised expected copy count. Exact per-group deduplication is a stronger property that is not required by that description. No issue is established in this scope.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Expected copy count is distinct from exact deduplication

Assessment: not_issue; impact: no_issue_found



Source: Figure 5 and Listing 1, PDF p. 7; Appendix J.1, PDF p. 17.



### Source claim (paraphrase)

The appendix retains each qualifying duplicate independently with probability \(1/c\), explicitly describing a probabilistic rule.



### Analysis

For target allocation \(m\), \(K\sim\operatorname{Binomial}(cm,1/c)\), giving \(\mathbb EK=m\) and \(\operatorname{Var}K=m(1-1/c)\). At \(c=2,m=1\), probabilities for \(K=0,1,2\) are \(1/4,1/2,1/4\). Thus the algorithm gives one expected copy, not exactly one in each group.



### Finding and scope

The probabilistic algorithm is internally consistent under its appendix description. No experiment is shown to rely on a deterministic one-copy guarantee, so this remains a scope clarification.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- Local contradictions and specification differences do not establish the magnitude or direction of changes to the published benchmark scores.

- No author contact or adoption; novelty and complete historical-run provenance are unestablished.
