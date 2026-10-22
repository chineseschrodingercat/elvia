# Optimistic Query Routing in Clustering-based Approximate Maximum Inner Product Search



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



A single-draw quantile is not a fixed-shard maximum guarantee. A covariance sketch can also lose the original quantile coverage, while normalized-centroid optimism needs a sign condition.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: A single-draw quantile does not bound a fixed maximum

Assessment: supported; impact: minor



Source: Introduction, PDF p.3; Section 2.1, PDF p.4, paragraph after Problem 1



### Source claim (paraphrase)

Section 2.1 constrains one draw from the shard but describes its threshold as a probabilistic bound on every shard value.



### Analysis

Use query \((1,0)\), ninety-nine points \((0,j)\), \(1\leq j\leq99\), and one point \((100,0)\). Mean score is \(1\), variance \(99\), and maximum \(100\). At \(\delta=0.8\), threshold \(1\) already covers \(0.99\) of one-draw scores, above the required \(0.9\), yet the fixed maximum is still \(100\). Even \(1+3\sqrt{99}\) is below that maximum without violating the one-draw lemma.



### Finding and scope

The confidence interpretation is too strong. The quantile-ranking objective remains mathematically valid.



### Proposed correction

Describe a single-point upper quantile. For a fixed shard of size \(n\), the deterministic moment bound is \(\max s_i\leq m+\sqrt{(n-1)v}\); a future maximum has a different probability law.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Two-sided sketch error does not preserve one-sided coverage

Assessment: supported; impact: minor



Source: Section 2.3, PDF pp.5–6; Definition 1, Eq.(8), Lemma 2 and Algorithm 1



### Source claim (paraphrase)

The router substitutes a masked covariance sketch into the exact-covariance quantile score. Lemma 2 controls approximation error, not covariance domination.



### Analysis

Take orthonormal vectors \(u=(1,1,0,0)/\sqrt2\), \(q=(0,0,1,1)/\sqrt2\), \(r=(1,-1,0,0)/\sqrt2\), \(s=(0,0,1,-1)/\sqrt2\). For each group \((n,a)=(7,\sqrt{18/5})\) or \((18,-7/\sqrt{90})\), set \(\theta_j=2\pi j/n\), \(0\leq j<n\), and \[x_{n,j}=a q+\sqrt{18/5}\cos\theta_j\,u+\sqrt{2/5}\sin\theta_j\,r+\sqrt{6/5}\cos(2\theta_j)\,s.\] Finite trigonometric sums give mean zero and covariance with diagonal ones and correlation blocks \(4/5\), \(2/5\). Its eigenvalues along \(u,q,r,s\) are \(9/5,7/5,1/5,3/5\). The rank-one masked sketch is \(I+(4/5)uu^\top\), so query variance is \(1\) instead of \(7/5\). At \(\delta=1/2\), threshold \(\sqrt3\) lies below the seven positive scores \(\sqrt{18/5}\), covering only \(18/25=0.72<0.75\). Exact threshold \(\sqrt{21/5}\) covers all points. The sketch’s spectral error still satisfies Lemma 2; two-sided approximation does not imply covariance domination.



### Finding and scope

The exact quantile guarantee cannot be inherited automatically. No separately stated universal sketch-coverage theorem or benchmark recall is refuted.



### Proposed correction

Inflate the quadratic form by \(D_{\max}\max(\lambda_{t+1},0)\|q\|^2\), where \(\lambda_{t+1}\) is the largest discarded normalized residual eigenvalue. This upper-bounds omitted positive variance and restores the one-draw guarantee under the original lemma’s assumptions.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: Normalized-centroid optimism requires nonnegative score

Assessment: supported; impact: minor



Source: Section 1, PDF p.3, normalized-mean motivation



### Source claim (paraphrase)

The introductory argument infers an increased score merely from a centroid norm at most one.



### Analysis

Unit points \((-1/2,\pm\sqrt3/2)\) have centroid \((-1/2,0)\). Query \((1,0)\) gives score \(-1/2\), which becomes \(-1\) after centroid normalization. Division by a norm below one raises a nonnegative score but lowers a negative one.



### Finding and scope

The positive-score intuition survives with its sign condition. A zero centroid also needs a convention.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
