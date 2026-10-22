# RefLoRA: Refactored Low-Rank Adaptation for Efficient Fine-Tuning of Large Models



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Theorem 4 reverses a negative-bound extremum and does not establish universally stronger balanced descent; the exact quadratic example confirms this failure. GD-to-AdamW scope and nonunique-surrogate branches remain local qualifications, with the balanced-factor formula preserved.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: The balanced factor maximizes the negative lower bound

Assessment: supported; impact: major



Source: Theorem 4, p.6; Appendix B.5, p.20.



### Source claim (paraphrase)

Theorem 4 says the balanced S minimizes a negative descent lower bound and uses it to explain improved descent.



### Analysis

The positive trace sum \(g(S)=\operatorname{tr}(XS)+\operatorname{tr}(YS^{-1})\) is minimized at the balanced \(S_b\). Multiplication by \(-\eta\|G\|_2^2\) reverses the extremum: the negative bound is maximized there, not minimized. In the admissible rank-one quadratic with \(A=B=e_1\), \(\eta=0.01\), the bound is \(-0.02\) at \(s=1\) and \(-0.0425\) at \(s=4\). The exact post-step losses from \(0.5\) are \(0.480298005\) and \(0.458498880\), so balancing need not give the larger one-step decrease.



### Finding and scope

Theorem4 reverses the extremum of its signed descent bound. The balanced factorization does not universally give the larger exact one-step loss decrease.



### Proposed correction

Correct the minimum to a maximum and remove or separately prove the stronger descent conclusion. The balanced-factor formula itself remains valid.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: The GD invariance theorem does not cover AdamW

Assessment: supported; impact: minor



Source: Theorem 6, p.7; Appendix B.6; reflora.py optimizer hooks.



### Source claim (paraphrase)

Theorem 6 proves a balanced gradient-descent factorization invariance.



### Analysis

Equivalent factors \((1,1)\) and \((2,1/2)\) give equal SGD weight change \(-0.0199\) in the scalar example, but initial AdamW normalization gives about \(-0.0199\) and \(-0.0249\) at learning rate \(0.01\). Coordinatewise adaptive normalization and optimizer state do not automatically respect the GD factor transformation. This is a scope boundary, not a counterexample to the GD theorem.



### Finding and scope

The invariance theorem concerns the specified gradient-descent update; current adaptive-optimizer integration does not inherit that property automatically. No contradiction to the restricted GD theorem is asserted.



### Proposed correction

State AdamW as a separate empirical algorithm. A general adaptive-state invariance proof remains unavailable.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: Different surrogate optima need a consistent branch

Assessment: supported; impact: minor



Source: Theorem 3, pp.4–5; linkage to Theorem 6 and default balanced rule.



### Source claim (paraphrase)

Theorem 3 admits multiple small-step surrogate minimizers, while Theorem 6 uses balanced factors.



### Analysis

For \(A=e_1,B=e_2,G=e_1e_1^\top,L=1,\eta=0.1\), the surrogate is \((s+1/s-10)^2\). Both \(s=5+\sqrt{24}\) and \(s=5-\sqrt{24}\) are global zero minima, but yield weight changes about \(-0.98989795e_1e_1^\top\) and \(-0.01010205e_1e_1^\top\). Arbitrary minimizer selection does not define a unique update. The default fixed balanced branch is not contradicted.



### Finding and scope

The optimizer-set statement does not select a unique update when different allowed surrogate minimizers are chosen. The default fixed balanced branch remains a countercontrol.



### Proposed correction

Specify the balanced or equivalence-consistent branch when combining the theorems; no default-algorithm error is inferred from nonuniqueness.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- No new author-code execution, model spending, training, author contact or complete benchmark replication.

- Historical numerical results are retained evidence rather than current reruns.

- Local counterexamples do not invalidate every empirical result; missing historical run attribution remains unresolved.
