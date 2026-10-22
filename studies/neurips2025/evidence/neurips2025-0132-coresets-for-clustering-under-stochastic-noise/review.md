# Coresets for Clustering Under Stochastic Noise



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Two explicit counterexamples refute the printed approximation-transfer and stochastic-noise bounds. Further proof gaps and clean-data/weighting implementation issues are kept distinct from unresolved baseline-guarantee effects.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The asymmetric relative-error definition does not imply the square approximation-ratio bound

Assessment: supported; impact: major



Source: arXiv v1 Eq. (5), PDF p. 7; Theorem 3.1, p. 8; Theorem 4.1, p. 12; proof Eq. (9), p. 13.



### Source claim (paraphrase)

Eq. (5), PDF p. 7, and the proof supporting Theorem 3.1 use the relative-error definition \(e=\sup_C|f_P(C)-f_S(C)|/f_S(C)\) to claim an approximation-transfer factor \((1+e)^2\). The weighted subset may have nonnegative weights and \(e\in(0,1)\).



### Analysis

Let \(P\) contain nineteen zeros and one one, and let \(S\) put weight \(10\) at each support point \(0,1\). For center \(c\), costs are \(f_P(c)=20c^2-2c+1\) and \(f_S(c)=20c^2-20c+10\). With \(u=c-1/2\), the ratio \(18|u|/(20u^2+5)\) has supremum \(e=0.9\). The \(S\)-optimal center \(1/2\) has \(P\)-cost \(5\), while \(\operatorname{OPT}_P=19/20\). Its ratio \(100/19\approx5.263\) exceeds \((1+0.9)^2=3.61\), even with no noise.



### Finding and scope

The square-factor transfer claim is false for an admissible weighted subset. The error definition gives factors one minus and one plus the error, rather than reciprocal one-plus-error bounds.



### Proposed correction

For \(e<1\), retain \((1-e)f_S\le f_P\le(1+e)f_S\). Comparing an approximately optimal coreset solution with the true optimum then gives the valid transfer factor \((1+e)/(1-e)\), multiplied by the coreset solution's approximation factor.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 2: Admissible independent noise makes the current relative-error bound infinite with probability \(16\%\)

Assessment: supported; impact: major



Source: arXiv v1 Lemma 4.2, PDF p. 12; proof pp. 14–15 (conference Lemma C.2).



### Source claim (paraphrase)

Lemma 4.2, PDF p. 12, claims a finite relative-error bound with probability greater than \(0.9\) under independent centered unit-variance Bernstein noise, without restricting the noise to a Gaussian law. Its proof supports Theorem 3.1.



### Analysis

Set \(P=\{-a,a\}\), \(a=\sqrt5/2\), and corrupt both points independently with noise taking \(-a,0,a\) with probabilities \((0.4,0.2,0.4)\). This noise is centered, has variance \(1\), is bounded and satisfies the Bernstein moment condition. The event that the two noises are respectively \(a,-a\) has probability \(0.16\) and collapses the noisy dataset to \(\{0,0\}\).

On that event, for every \(c\ne0\), \(f_{\widehat P}(c)=2c^2\) and \(f_P(c)=2c^2+5/2\). Hence \(|f_{\widehat P}-f_P|/f_{\widehat P}=5/(4c^2)\to\infty\) as \(c\to0\). The finite-bound success probability is at most \(0.84<0.9\), even though the clean optimum \(5/2\) exceeds the total noise variance \(2\).



### Finding and scope

Current Lemma 4.2 is false on its stated noise domain; a convention at a zero denominator cannot repair divergence through positive denominators. Guarantees depending on that lemma need a replacement argument or stronger assumptions.



### Proposed correction

A sufficient extra condition is \(q=\sqrt{R/\operatorname{OPT}_P}<1\), where \(R=\sum_p\|\xi_p\|_2^2\). The distance-vector triangle inequality gives \((1-q)^2f_P\le f_{\widehat P}\le(1+q)^2f_P\), hence error at most \((1-q)^{-2}-1\). This conditional replacement does not recover the unrestricted theorem.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 3: Gaussian fourth moments and conditional normality are used under a non-Gaussian model

Assessment: supported; impact: minor



Source: arXiv v1 Claim 4.4, PDF pp. 13–14, Eq. (11); Claim 5.6 and Lemma 5.7, pp. 17–19.



### Source claim (paraphrase)

Claim 4.4's proof, Eq. (11), PDF p. 14, uses Gaussian chi-square variance to bound the sum of squared noises under the broader Bernstein model. Claim 5.6 and Lemma 5.7 also invoke Gaussian conditional distributions.



### Analysis

A centered unit-variance Laplace variable has \(\mathbb E\xi^4=6\), so \(\operatorname{Var}(\xi^2)=5\), exceeding the Gaussian value \(2\) and the relaxed printed bound \(3\). A one-variable sum remains Laplace, not Gaussian. However, the intermediate Claim 4.4 probability conclusion can instead follow from \(R\ge0\), \(\mathbb ER=\theta nd\), and Markov's inequality, which gives \(\Pr(R\le60\theta nd)\ge59/60>0.95\). The invalid proof step does not by itself falsify that conclusion.



### Finding and scope

The displayed Gaussian moment argument is invalid under the broader noise class, but the cited intermediate probability conclusion has a distribution-free Markov proof; this local proof correction is Minor.



### Proposed correction

Replace the Gaussian-specific proof of the stated intermediate norm bound by Markov’s inequality using \(\mathbb ER=\theta nd\). Recalculate other bounds for the actual noise class rather than assuming conditional normality.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 4: Two arguments for the new metric use invalid inequalities

Assessment: supported; impact: minor



Source: arXiv v1 proof of Lemma 5.4, PDF p. 23; Claim A.2 and proof Eq. (17), p. 41.



### Source claim (paraphrase)

The two proofs use a near-optimal-set ratio bound and a union-optimum/containment implication under their stated overlap assumptions.



### Analysis

For \(S=\widehat P=\{-1,1\}\), \(\alpha=2\), and center \(0\), all approximation ratios equal one. Lemma 5.4's displayed intermediate estimate would require \(0\le1/2-1=-1/2\). Separately, for disjoint sets \(\{-3,-1\}\) and \(\{1,3\}\), the one-center optima sum to \(4\), but their union optimum is \(20\); the stated overlap setup does not justify the proof's \(20\le4\) step. These are two invalid arguments, not complete counterexamples to every final new-metric theorem.

For the union example, set \(\alpha=17\) and \(\alpha^{\prime}=1\). Each component’s optimal mean has ratio \(17\) on the other component, satisfying both stated overlap conditions. At center \(5/2\), the union ratio \(9/4\) lies below the claimed near-optimal threshold \(13/5\), but the first component ratio is \(85/4>17\), also falsifying the asserted containment.



### Finding and scope

The specified intermediate inequalities are false. Their effect on all final new-metric guarantees has not been established, so the finding is kept as a bounded Minor proof defect rather than a blanket theorem rejection.



## Problem 5: The released proposed construction uses clean data to choose which noisy points to retain

Assessment: supported; impact: minor



Source: arXiv v1 Algorithm 1, PDF p. 12; observation-only scope p. 7; implementation p. 27; current algorithms.py our_coreset.



### Source claim (paraphrase)

Algorithm 1 constructs from noisy observations, and p. 7 explicitly excludes clean-data access. Current algorithms.py fits KMeans to X_noise but computes the construction distances with clean X before trimming.



### Analysis

Hold observations \(\widehat X=(0,1,2,3,4)\) fixed, with one fitted center \(2\). Clean inputs \(X_A=(0,1,2,3,4)\) and \(X_B=(0,1,2,3,100)\) give clean distances \((2,1,0,1,2)\) and \((2,1,0,1,98)\). The stated radius rule retains all five noisy points in the first case and discards the last in the second. Thus unobserved clean inputs can change a construction intended to depend only on the identical observations. Its historical benchmark impact remains unidentified.



### Finding and scope

Identical observations can produce different retained sets when only the unavailable clean input changes; the published-run identity and empirical effect remain unknown.



### Proposed correction

Compute construction radii and retained indices from noisy observations only; reserve clean data for final evaluation and keep it out of the construction interface.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 6: Sampled points receive weights indexed by their new row rather than their source cluster

Assessment: supported; impact: minor



Source: arXiv v1 Algorithm 1, PDF p. 12; implementation p. 27; algorithms.py our_coreset weight assignment.



### Source claim (paraphrase)

Algorithm 1 and Appendix G.1 require a point sampled from cluster \(i\) to receive weight \(|P_i'|/|S_i|\). Released code/algorithms.py builds S_indices and a new sampled array, but uses labels indexed by the new row number rather than by its selected source index.



### Analysis

If sampled output row \(j\) came from source row \(s_j\), its weight must use the cluster label of \(s_j\). The label of source row \(j\) may belong to a different cluster, so indexing the old label array by the new row number can assign another cluster's weight. When every point is retained in original order the indices agree, explaining that matching control.



### Finding and scope

The current index mismatch assigns weights from another cluster; a global mass check can miss it and actual benchmark distortion is unmeasured.



### Proposed correction

Use the cluster label at each sampled source index, consistently for numerator and sample count, when assigning its output weight.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 7: The baseline uses with-replacement importance weights after without-replacement sampling

Assessment: supported; impact: minor



Source: arXiv v1 implementation of CN, PDF p. 27; current algorithms.py get_coreset.



### Source claim (paraphrase)

The released baseline samples without replacement but assigns weights derived from with-replacement draw probabilities. The concern is the resulting estimator, not an asserted failure of every coreset guarantee.



### Analysis

Without-replacement inclusion probability \(\pi_i\) generally differs from \(mp_i\), so weighting by \(1/(mp_i)\) does not yield the usual unbiased estimator. At \(m=n\), every point is included with probability one, but unequal \(p_i\) still produce unequal weights and distort the full empirical measure. This proves the sampling/weighting mismatch, while the effect on a particular high-probability coreset guarantee remains unresolved.



### Finding and scope

Supported implementation/statistical distinction; effect on the cited baseline guarantee is unresolved.



### Proposed correction

Use with-replacement draws with multiplicity-aware weights, or a specified without-replacement design with inclusion weights \(1/\pi_i\). A full-population shortcut should return unit weights.

A local correction or qualification is proposed where specified; author adoption is not established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
