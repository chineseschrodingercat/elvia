# Spurious-Aware Prototype Refinement for Reliable Out-of-Distribution Detection



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The theoretical explanation repeatedly removes spurious variance by centering at a mean, and its normalized ID/OOD assumptions force the core component to vanish. These are substantial defects in the stated distance derivation; the empirical detector and reported benchmark scores are not remeasured.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Centering at a group mean does not remove spurious variance

Assessment: supported; impact: major



Source: Appendix A.0.6, Case 2, and A.0.7, PDF pp.19–20



### Source claim (paraphrase)

The minority-to-majority ID formula omits spurious variance; the matched-group ID formula retains only core and irrelevant variance. The later OOD formula adds core variance and asserts strictly larger expected distance.



### Analysis

For a random vector \(X\) and deterministic prototype \(p\), \[\mathbb E\|X-p\|^2=\operatorname{tr}\operatorname{Cov}(X)+\|\mathbb EX-p\|^2.\] Orthogonal subspaces remove cross terms, not fluctuations within each subspace. Therefore the minority-to-majority identity needs \(\operatorname{tr}\Sigma_{1-c}^{\rm sp}\), while matched ID distance is \(\operatorname{tr}\Sigma_g^{\rm sp}+\operatorname{tr}\Sigma_c^{\rm core}+\operatorname{tr}\Sigma^{\rm irr}\).

A normalized ID witness uses spurious basis \(e_1\), core basis \(e_2\), class-zero core \(3/5\) and class-one core \(-3/5\). Set \(P_0^{\rm sp}\) on \(4/5,-4/5\) with probabilities \(3/4,1/4\), and reverse those probabilities for \(P_1^{\rm sp}\). A majority proportion \(9/10\) is admissible. Every feature has unit norm, and core sign determines class. Class-zero population prototypes are \((2/5,3/5)\) and \((-2/5,3/5)\); both spurious variances equal \(12/25\). Minority-to-majority distance is \(28/25\), whereas the printed formula gives \(16/25\). Minority-to-own distance is \(12/25\), whereas the printed formula gives \(0\). These are means of normalized features, as defined by the appendix; renormalizing the prototypes would change the model.

In the raw-coefficient interpretation, matched OOD has zero core and unchanged nuisance marginals, so its expected distance is \(\operatorname{tr}\Sigma_g^{\rm sp}+\|\mu_c^{\rm core}\|^2+\operatorname{tr}\Sigma^{\rm irr}\). Its difference from matched ID is \[\|\mu_c^{\rm core}\|^2-\operatorname{tr}\Sigma_c^{\rm core}.\] Thus positivity requires a signal-to-variance condition. The earlier OOD formula in Case 1 on p.19 has the correct variance structure.



### Finding and scope

The repeated identities and unconditional separation argument are false as written. Group means can remove a spurious mean-mismatch term, but cannot eliminate its variance. The normalized ID witness does not purport to satisfy the incompatible joint OOD assumptions discussed separately; a matched-prototype expectation also does not certify the detector’s minimum-over-prototypes score or AUROC.



### Proposed correction

Retain all covariance traces in the population-distance identities and require \(\|\mu_c^{\rm core}\|^2>\operatorname{tr}\Sigma_c^{\rm core}\) for a positive matched expected gap in a coherent raw-feature model. Group recovery, random estimated prototypes and detection-error guarantees need separate arguments.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: The joint normalized model excludes a nonzero core

Assessment: supported; impact: major



Source: Appendix A.0.1 and A.0.3–A.0.4, PDF pp.17–18



### Source claim (paraphrase)

ID embeddings are normalized. Near-OOD embeddings retain the same spurious and irrelevant coefficient marginals but have neither core nor external components.



### Analysis

Under the stated orthogonality, unit norms give \[\mathbb E\|\alpha\|^2+\mathbb E\|\beta\|^2+\mathbb E\|\gamma\|^2=1,\qquad \mathbb E\|\alpha\|^2+\mathbb E\|\gamma\|^2=1.\] The common nuisance marginals therefore imply \(\mathbb E\|\beta\|^2=0\), so \(\beta=0\) almost surely. Neither independence nor samplewise ID/OOD coupling is required. A nondegenerate core cannot coexist with these assumptions. In the preceding ID witness, deleting the core leaves norm \(4/5\); renormalization changes spurious mean magnitude from \(2/5\) to \(1/2\), and variance from \(12/25\) to \(3/4\). It therefore does not preserve the assumed marginals.



### Finding and scope

The idealized joint distribution underlying the separation explanation is incompatible with a nonzero core under unit normalization. Allowing an external component could supply the missing norm, but the analyzed near-OOD case expressly sets that component to zero. This does not show that actual normalized SPROD features lack class information.



### Proposed correction

Explicitly analyze raw features without claiming that this preserves the normalized detector model, or formulate a normalized OOD model with changed nuisance moments and recompute the distance terms. Neither alteration alone proves the detector’s empirical ranking.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.

- The current author repository contains no executable implementation; benchmark features and detection scores were not independently inspected.
