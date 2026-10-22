# TP-MDDN: Task-Preferenced Multi-Demand-Driven Navigation with Autonomous Decision-Making



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Under the natural finite-navigable-grid normalization, zero obstacle preference conflates a safe minimum with threshold exclusion. Constant distance ranges also leave the stated formulas undefined. The impact on actual navigation remains conditional on implementation conventions.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: A normalized minimum does not encode the raw obstacle threshold

Assessment: supported; impact: minor



Source: Section 3.1.3, Calculation of Affordance Map and Eq.(3), PDF p.7; Section 4.1 threshold, p.7



### Source claim (paraphrase)

For threshold-admissible navigable points the obstacle preference is min–max normalized, but Eq.(3) uses its zero value as the final exclusion mask. Target-distance normalization also divides by its range without a stated tie rule.



### Analysis

Let the already processed obstacle cloud be \(O=\{(0,0)\}\), target \(T=(1,0)\), candidates \(n_1=(1/2,0)\), \(n_2=(3/4,0)\), and threshold \(\tau_o=1/4\). Both are safe under the stated raw-distance threshold. Their obstacle distances are \((1/2,3/4)\), hence normalized preferences \((0,1)\); their inverse target preferences are \((0,1)\). Eq.(3) returns \((0,1)\), whereas a raw-distance mask followed by the stated clipping returns \((0.1,1)\). Every safe minimum is similarly excluded when \(d_{\max}>d_{\min}\ge\tau_o\).

Valid geometry also gives undefined ranges. Candidates \((\pm1/2,0)\) around the same obstacle have constant safe obstacle distance and yield \(0/0\). Alternatively, the original candidates with target \((5/8,0)\) have equal target distances \(1/8\), so semantic normalization yields \(0/0\).



### Finding and scope

The literal formulas need a normalization and tie convention. If excluding safe minima is intentional, it is an additional preference rule; normalization over a larger set containing obstacles could remove the first example. No route or success-rate change is established.



### Proposed correction

Separate the mask \(s(n)=\mathbf1\{d_o(n)\ge\tau_o\}\) from preference. Let \(q\) be inverse target normalization with an explicit common value when distances tie, and set \(\widehat a_f=s\,\operatorname{clip}(q,0.1,1)\). The positive clipped factor makes zero equivalent to raw threshold exclusion. This restores only that property, not collision-free planning.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.

- The actual navigation implementation and any unpublished normalization or constant-range guards were not inspected.
