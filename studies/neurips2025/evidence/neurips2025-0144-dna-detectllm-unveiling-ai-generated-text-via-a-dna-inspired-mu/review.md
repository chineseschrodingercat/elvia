# DNA-DetectLLM: Unveiling AI-Generated Text via a DNA-Inspired Mutation-Repair Paradigm



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current released repair routine ignores the requested order, and its cross-entropy direction differs from the paper. The probability-order intuition is qualified as typical and is not counted as a current error.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The released repair routine ignores the requested order

Assessment: supported; impact: minor



Source: Section 3.6 and Figure 3, PDF p. 5; Table 1, PDF p. 7; Appendix G, Table 10, PDF p. 24.



### Source claim (paraphrase)

Paraphrase. Section 3.6 distinguishes sequential, high-to-low, low-to-high, and random repair orders. Figure 3 illustrates their different trajectories; the lower panel of Table 1 and Appendix G, Table 10 report different detection results for the order variants pp. 5, 7, 24. Their meaning requires the repaired token sequence to depend on the chosen order.

The matching implementation is auc_perplexity in dna_detectllm/metrics.py, lines 53–210. Its active order-selection block is at lines 79–87 and the repair loop begins at line 89. The conference supplement and the pinned GitHub copy have identical bytes for this file. compute_anomaly_level calls this routine with repair_order="h2l"; the default compute_score instead calls sum_perplexity.



### Analysis

The function computes/shuffles sorted_indices according to the requested order, but the active update loop iterates unchanged change_indices. Its returned trajectory is therefore independent of every accepted order string for fixed inputs. Distinct order-ablation results cannot be reproduced by changing this parameter alone in the supplied routine.



### Finding and scope

This is a supported local finding within the stated source/formulation scope. Its effect on the paper's aggregate experimental results remains unmeasured.



## Problem 2: The paper and code assign opposite directions to cross entropy

Assessment: supported; impact: minor



Source: Eq. (1), PDF pp. 3–4; Section 4.1, PDF p. 6 (model roles).



### Source claim (paraphrase)

Eq. (1), PDF pp. 3–4, places reference-model probabilities from \(M_1\) outside the logarithm and observer-model probabilities from \(M_2\) inside it. Section 4.1, PDF p. 6, assigns those roles to Falcon-7B-Instruct and Falcon-7B. Interpreting the omitted vocabulary sum charitably gives cross entropy \(H(P,Q)=-\sum_iP_i\log Q_i\); the finding does not count the omitted sum as an error.



### Analysis

The released helper receives observer then reference distributions and computes \(H(Q,P)\), while the numerator retains reference probabilities. Cross entropy is asymmetric: for \(P\ne Q\), those expressions need not agree and can rank detector scores differently. Reversing model names only inside the denominator does not restore the full stated role contract.

For example, \(P=(0.9,0.1)\), \(Q=(0.5,0.5)\) give \(H(P,Q)=\log 2\approx0.69315\), while \(H(Q,P)=-\tfrac12\log(0.09)\approx1.20397\). With the same reference numerator these are different scores. This is an arithmetic witness to the direction mismatch, not a benchmark rerun.



### Finding and scope

This is a supported local finding within the stated source/formulation scope. Its effect on the paper's aggregate experimental results remains unmeasured.



## Problem 3: Probability order does not universally determine repair-score order

Assessment: not_issue; impact: no_issue_found



Source: Section 3.6, PDF p. 5 (probability-order intuition).



### Source claim (paraphrase)

Paraphrase. Section 3.6 associates high observed-token probability with smaller repair changes and describes high-probability repairs first as producing a higher trajectory score p. 5. The preceding discussion uses typically, so this analysis distinguishes an empirical tendency from a universal implication. The latter is not valid under the stated definitions. The result below is a scope clarification, not a refutation of the empirical curves.



### Analysis

Take valid four-token distributions \((0.40,0.50,0.05,0.05)\) and \((0.30,0.31,0.20,0.19)\), observing the first token in each. Their repair log changes are \(\log(0.50/0.40)\approx0.22314\) and \(\log(0.31/0.30)\approx0.03279\), so the higher observed probability gives the larger change. A uniform observer holds the denominator fixed. This excludes a universal ordering but is compatible with the source’s explicit typical-behavior qualification and empirical curves; it is not counted as a current error.



### Finding and scope

No current error is established by the universal interpretation. The source explicitly qualifies the probability-order explanation as typical and presents repair-order behavior empirically. The counterexample limits a stronger universal claim that is not required by that qualified wording.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
