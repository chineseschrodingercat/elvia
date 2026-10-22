# Differentiable Hierarchical Visual Tokenization



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The lattice-rank derivation of the central complexity surrogate counts dependent cycle edges as rank steps. The fixed-partition Gaussian mean statement remains valid. A known, author-acknowledged stabilization constant changes the selection objective.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Cycle edges are not independent partition-rank steps

Assessment: supported; impact: major



Source: Appendix B.2, Eq.(B.5), PDF p.25; main Eq.(4), PDF p.4



### Source claim (paraphrase)

The derivation identifies top rank with the internal edge count, \(r(\top)=|E|\), to motivate inverse-volume degrees of freedom.



### Analysis

A connected four-neighbor \(2\times2\) grid has \(4\) vertices and \(4\) edges. A connected-partition chain merges four singleton blocks into one in exactly \(3\) cover steps. In general every cover merges two adjacent connected blocks: merging more would allow an intermediate adjacent-pair merge. Thus \(r(\pi)=|V|-|\pi|\) and \(r(\top)=|V|-1\), not \(|E|\) on cyclic grids. Counting all atoms counts dependencies. Even the corrected reciprocal rank is not automatically statistical degrees of freedom: fixed scalar region-mean fitting has projection trace \(|\pi|\).



### Finding and scope

The formal lattice step supporting the central complexity surrogate is false. A shape-sensitive penalty may still be useful as a heuristic; its hierarchy and reported scores are not numerically refuted.



### Proposed correction

Give the correct lattice rank. Treat inverse edge volume as a structural regularizer unless a separate statistical argument supports it; substituting \(|S|-1\) alone does not establish AIC/BIC validity.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: Fixed-partition mean fitting is not a partition-selection equivalence

Assessment: not_issue; impact: minor



Source: Appendix B.1, Eqs.(B.2)â€“(B.4), PDF p.24



### Source claim (paraphrase)

The passage fixes the partition when identifying Gaussian mean estimation with squared-error minimization.



### Analysis

That fixed-partition claim is valid. A stronger reading with separately fitted regional variances would be false: image rows \((0,1)\), \((5,-4)\) give horizontal SSE \(41\) versus vertical SSE \(25\), while profiled negative log likelihoods differ as \(\log(81/16)\) versus \(\log(625/16)\), favoring horizontal. These positive-variance connected candidates do not refute the narrower actual claim. Common known isotropic variance makes negative log likelihood affine in SSE; one fitted common isotropic variance makes it monotone in SSE.



### Finding and scope

Scope clarification only. No confirmed error is attributed to the valid fixed-partition mean result.



## Problem 3: Positive iota changes the model-selection objective

Assessment: supported; impact: minor



Source: dht/tok/infocrit.py, gaussian_2nll; tokenizer.py default iota; GitHub issue 2



### Source claim (paraphrase)

The release calls \(\iota\) a numerical stability constant but evaluates \(m_S\log(\prod_j2\pi v_{S,j}+\iota)\), with tokenizer default \(5\).



### Analysis

For positive \(z\), \(\log(z+\iota)-\log z=\log(1+\iota/z)\), a variance-dependent change rather than a common constant. Scale the preceding image by \(1/100\): horizontal variances are \(0.000025,0.002025\), vertical \(0.000625,0.000625\). Equal masses and region counts cancel complexity differences. At \(\iota=0\), horizontal has the smaller log-product; at \(\iota=1\) or \(5\), vertical does. This is a controlled candidate-score reversal, not proof the greedy hierarchy encounters both candidates.



### Finding and scope

Known objective-changing behavior is reproduced analytically. Issue 2, opened 14 August 2026, received a 21 September author/member acknowledgment; historical training settings and benchmark changes remain unverified.



### Proposed correction

If intended as a granularity heuristic, document \(\iota\) and exact settings. For a positive-variance Gaussian likelihood, sum coordinate log variances directly in log space; a nonpositive-variance model still needs an explicit statistical convention.

Objective-changing behavior was already acknowledged by an author/member in issue 2; no adoption of the proposed log-space alternative is established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
