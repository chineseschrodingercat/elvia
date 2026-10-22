# Visual Jenga: Discovering Object Dependencies via Counterfactual Inpainting



Preliminary assessment: No Issue Found

Independent scientific review: pending. Author adoption: not requested.



No substantive implementation or empirical contradiction was established. The conditional-probability comparison and feature score have mathematical scope limits consistent with the paper’s explicit co-occurrence-based heuristic and lack of causal reasoning.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Conditional asymmetry does not identify a physical cause

Assessment: not_issue; impact: minor



Source: Section 3.1, Eq.(1), PDF p.4; Limitations, PDF p.9



### Source claim (paraphrase)

The asymmetry \(P(A\mid B)\ll P(B\mid A)\) motivates a directional dependency heuristic.



### Analysis

For positive joint probability, \(P(A\mid B)/P(B\mid A)=P(A)/P(B)\). Independent events with marginals \(0.01\) and \(0.9\) have joint \(0.009\), giving the large conditional asymmetry despite independence. The same identity holds under a common fixed context. The curated benchmark additionally selects physical-support pairs, and the paper explicitly describes its approach as statistical co-occurrence without causal reasoning.



### Finding and scope

The comparison alone is not causal identification. This scoped limitation does not contradict the qualified heuristic or its reported benchmark arithmetic.



## Problem 2: Mean similarity does not uniquely specify distributional peakedness

Assessment: not_issue; impact: minor



Source: Section 3.3(ii), Eq.(2), PDF p.5



### Source claim (paraphrase)

The product of mean CLIP/DINO similarities is motivated by peakedness of the inpainting distribution.



### Analysis

In both feature spaces take original unit vector \((1,0)\) and candidate outputs \((0.6,0.8)\), \((0.6,-0.8)\), with area fraction \(1\). Both rescaled similarities are \(0.8\). A point mass and an equal two-point mixture have entropy \(0\) and \(\log2\), but score \(1-0.8^2=0.36\) in both cases. Real-image realizability of these simultaneous embeddings is unestablished.



### Finding and scope

The score measures deviation from the original crop and need not identify entropy. Its empirical utility is not contradicted.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
