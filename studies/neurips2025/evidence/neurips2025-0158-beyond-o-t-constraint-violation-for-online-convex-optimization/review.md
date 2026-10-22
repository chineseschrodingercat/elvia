# Beyond Õ(√T) Constraint Violation for Online Convex Optimization with Adversarial Constraints



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The smooth small-loss bound lacks a domain/self-bounding hypothesis: an exact one-round convex loss satisfies local nonnegativity and smoothness but violates the displayed regret constant. The expert and covering arguments are separate and remain unrefuted.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Local nonnegativity does not imply the small-loss bound

Assessment: supported; impact: major



Source: Theorem 4, Eq.(22), PDF p.9; Assumptions 1,4, PDF pp.2,9; Eq.(5), PDF p.4



### Source claim (paraphrase)

For nonnegative convex \(M\)-smooth losses on a closed decision set of diameter \(D\), Eq.(22) bounds regret by \(4D\sqrt{M\sum_t l_t(u)}+4D^2M\).



### Analysis

Take \(\mathcal X=[0,1]\), \(D=T=x_1=1\), comparator \(u=0\), and \(l(x)=x/2+x^2/200\). On the stated domain, \(0\le l\le0.505<1\), while \(l^{\prime\prime}=M=0.01\) exactly. The comparator loss is zero, so the claimed right side is \(0.04\), but the first-round regret is \(0.505\). The nonzero gradient \(0.51\) avoids step-size singularity; no update can undo an already incurred first loss. Setting the ordinary cost to zero and constraint penalty to this loss gives the same violation of the explicit constraint-only illustration. The polynomial is globally smooth but is not globally nonnegative.



### Finding and scope

The local-domain theorem and explicit constant fail. This does not directly refute the expert/covering route or establish a contrary asymptotic rate for every smooth extension.



### Proposed correction

Add \(\|\nabla l_t(x)\|^2\le2Ml_t(x)\), for example through a globally nonnegative smooth extension. Adaptive projection then gives \(R\le2D\sqrt{M(R+L)}\), whence \(R\le4D^2M+2D\sqrt{ML}\), restoring the more conservative printed constants. Weighted Cauchyâ€“Schwarz supplies the corresponding self-bound for nonnegative surrogates.

This domain omission is inherited from the cited older monograph wording; its later edition explicitly assumes self-boundedness. No paper-specific author adoption is established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
