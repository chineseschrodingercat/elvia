# What is Your Data Worth to GPT? LLM-Scale Data Valuation with Influence Functions



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The LogIX release can mutate cached EKFAC eigenvalues between identical queries and derive all layers’ default damping from the first layer. These affect the specified preconditioner, while benchmark impact remains unquantified.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Repeated queries mutate cached curvature eigenvalues

Assessment: supported; impact: minor



Source: Sections 2–3, PDF pp.3–5; Appendix C, PDF p.31; Appendix E, PDF pp.33–34; official supplement logix/analysis/influence_function_utils.py, precondition_kfac, lines 27–36



### Source claim (paraphrase)

For fixed cached eigenvalues \(D\) and explicit damping \(\lambda\), the influence preconditioner should use \((D+\lambda)^{-1}\) without changing the stored curvature.



### Analysis

In the same-device branch, the temporary tensor aliases the cache and damping is added in place. For a scalar eigenvalue and query gradient both equal to \(1\), with \(\lambda=0.1\), successive identical calls therefore return \(1/1.1\), \(1/1.2\), and \(1/1.3\), rather than the fixed value \(1/1.1\). Positive curvature, matching dimensions and same-device storage suffice; singularity is unnecessary.



### Finding and scope

The routine’s output can depend on prior query count. Whether the published experiments exercised that aliasing path is unresolved.



### Proposed correction

Keep \(D\) immutable and form \(D+\lambda\) out of place, or clone before an in-place update. This removes query-count dependence at this interface.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Default damping depends on layer enumeration order

Assessment: supported; impact: minor



Source: Appendix C, PDF p.31, damping definition; official supplement logix/analysis/influence_function_utils.py, precondition_kfac module loop



### Source claim (paraphrase)

Appendix C describes damping based on \(0.1\) times the mean eigenvalue. The release initializes the shared damping variable inside its module loop only while it is unset.



### Analysis

For scalar layers with eigenvalues \(1\) and \(100\), per-layer damping is \(0.1\) and \(10\). Processing the small layer first instead uses \(0.1\) for both; reversing the order uses \(10\) for both. The small layer’s output changes from \(1/1.1\) to \(1/11\) under a pure dictionary-order change. This is separate from cache mutation because the factorized branch creates fresh tensors.



### Finding and scope

The default preconditioner is not determined solely by each layer’s statistics and the declared damping policy.



### Proposed correction

Create a fresh \(\lambda_m=0.1\operatorname{mean}(D_m)\) for each layer, while preserving a user-supplied fixed value when provided. Do not overwrite the shared user option inside the loop.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
