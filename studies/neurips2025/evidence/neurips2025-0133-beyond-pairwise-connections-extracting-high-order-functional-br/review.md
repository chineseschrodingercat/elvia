# Beyond Pairwise Connections: Extracting High-Order Functional Brain Network Structures under Global Constraints



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The written covariance and conditional-variance arguments are false in their stated domains; the expressivity proof has separate gaps. Both released binarizers force complete graphs, and evaluation limitations require distinct known-label/unseen-row/window treatments.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: Equal covariance does not make every bivariate-distribution edge rule equal

Assessment: supported; impact: major



Source: Theorem 1 and Corollary 1, PDF p. 5; Appendix C, PDF p. 25.



### Source claim (paraphrase)

Claim and location (paraphrase). Theorem 1 and Corollary 1, p.5, consider dimension at least three, equality of all second-order lagged moments used by the edge rule, and at least one differing cumulant of order at least three. They conclude that every pairwise generator from the preceding bivariate-distribution definition returns the same adjacency. Appendix C, p.25, supplies the proof.



### Analysis

At every time independently, process \(A\) is \((U,V,UV)\) for independent fair Rademacher variables \(U,V\). Process \(B\) has independent coordinates each taking \(-\sqrt2,0,\sqrt2\) with probabilities \((1/4,1/2,1/4)\). Both are bounded, stationary, centered, have covariance \(I_3\), and have zero nonzero-lag covariances. Their third joint cumulants are \(1\) and \(0\).

The permitted bivariate edge functional \(\mathbb E[X_1^4X_2^2]\) is \(1\) for \(A\) and \(2\) for \(B\). Thresholding it at \(3/2\) gives different binary edges. Equal second moments therefore do not make every bivariate-distribution edge rule equal. Restricting the rule to covariance, or matching full bivariate laws, restores the corresponding restricted implication.



### Finding and scope

The theorem's universal bivariate-rule conclusion is false. This narrows its impossibility claim while preserving the motivation that some higher-order interactions are invisible to pairwise information.



### Proposed correction

Restrict the rule to matched second-order inputs, or strengthen the premise to equality of the full bivariate laws used by each rule. Equal-pair-law XOR examples still establish a restricted higher-order non-identifiability result.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 2: Positive conditional variance does not imply different marginal distributions

Assessment: supported; impact: major



Source: Appendix B, Lemma 2, PDF pp. 24–25; Theorem 3.



### Source claim (paraphrase)

Claim and location (paraphrase). Appendix B, pp. 24–25, Lemma 2 states that \(\operatorname{Var}(X\mid Y)>0\) almost surely implies \(X\) and \(Y\) are not equal in distribution. Theorem 3 applies this along project, group, subject, and sample levels and concludes all six pairs of graph distributions differ.



### Analysis

Independent \(X,Y\sim\operatorname{Bernoulli}(1/2)\) have the same marginal law, yet \(\operatorname{Var}(X\mid Y)=1/4>0\) almost surely. Equal distributions do not imply equality on each outcome. Likewise, take four independent Bernoulli edge indicators for two-node graphs at the hierarchy levels. Every parent-conditioned edge variance is \(1/4\), but all four graph laws coincide. Neither the lemma nor all six claimed pairwise distinctions follow.



### Finding and scope

The formal distributional-distinction argument is false. Different semantic hierarchy levels or empirically different fitted graphs do not repair that universal implication.



### Proposed correction

State conditional nondeterminism as the consequence of positive conditional variance; provide assumptions or statistics distinguishing marginal laws before asserting distributional separation.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 3: The higher-order expressivity proof contains independent invalid steps and does not prove optimization convergence

Assessment: supported; impact: major



Source: Theorem 2, PDF p. 6; Section 7, PDF p. 10; Appendix D, Theorem 4 and Lemmas 3–5, PDF pp. 26–27.



### Source claim (paraphrase)

Claim/location (paraphrase). Theorem 2, p.6, and Theorem 4, Appendix D, pp. 26–27, claim arbitrarily small classification risk for measurable higher-order rules and a class-separable measurable label map. The sentence following Theorem 2, and Section 7 on p.10, additionally attribute convergence of GCM to that theorem. Appendix D uses Lemmas 3–5.



### Analysis

The printed sampler first places its edge parameter \(A\) in \((0,1)\). For standard Gumbel noise \(M\), the desired off-edge event satisfies \(\Pr(\operatorname{sigmoid}((A+M)/\tau)<1/4)=\exp[-\exp(A+\tau\log3)]\le e^{-1}<0.368\). Increasing the earlier raw parameter cannot make that event arbitrarily probable after the intervening sigmoid.

A separate lemma claims any continuous injective node map has an injective tagged sum. The identity map with distinct one-hot tags gives equal sums for feature triples \((0,2,0)\) and \((1,1,0)\), despite different tagged inputs. Finally, a continuous MLP cannot uniformly approximate the measurable step \(\mathbf1\{x_1\ge0\}\) below error \(1/2\) on the whole cube. These invalidate the supplied expressivity argument; representational existence would not establish optimizer convergence in any event.



### Finding and scope

The supplied proof establishes neither its unrestricted expressivity statement nor optimization convergence. Suitable restricted or alternative constructions may still be possible; this is not a claim that higher-order learning is impossible.



### Proposed correction

A revised proof must use a sampler capable of the stated graph approximation, an explicitly suitable tagged encoder, and a valid probability/risk approximation argument. Treat optimizer convergence separately from representational existence.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 4: Both released binarizers return all-ones graphs; the released loss also omits the stated sparsity term

Assessment: supported; impact: minor



Source: Section 5, Eq. (3), PDF p. 6; BBA ablation, PDF pp. 8–9; Algorithm 2, PDF p. 27; current models.py and official supplementary code/models.py.



### Source claim (paraphrase)

Claim/location (paraphrase). Section 5, p.6, Eq. (3), Algorithm 2, p.27, and the BBA ablation discussion, pp.8–\(9\), require selection of a bounded number of high-scoring edges. The method’s loss is \(L=L_1+\alpha L_2+\beta R\) with an \(\ell_1\) sparsity term. The relevant released functions are in the current models.py and in the official supplemental code/models.py.



### Analysis

Both released binarizers scatter scalar \(1\) into sorted_indices, a permutation of all \(N^2\) matrix positions, while leaving the computed top-k mask unused. Every forward adjacency is therefore the all-ones matrix, including its diagonal. A straight-through estimator can still return a nonzero surrogate gradient, which does not change that constant forward graph. The active loss separately omits the stated sparsity term. The historical table/figure-producing program remains unidentified.



### Finding and scope

The release cannot produce sample-dependent sparse hard graphs through these functions. This is a substantial release defect, but published-figure provenance and central empirical damage are not established, so its impact label is Minor.



### Proposed correction

For the intended undirected loop-free forward graph, select a rank mask on strict-upper-triangle scores, mirror it and zero the diagonal. Explicitly define the edge budget, backward estimator and actual regularization objective; a one-line scatter edit alone is incomplete.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 5: Evaluation requires explicit separation of known-label group analysis, unseen graph parameters, and possible duplicate windows

Assessment: supported; impact: minor



Source: Section 6.2, PDF p. 8; Section 8, PDF p. 10; released graph lookup and window-split construction.



### Source claim (paraphrase)

The source distinguishes group-conditioned structure analysis from held-out classification, while the release allocates graph rows and selected window identities before its split.



### Analysis

Three evaluation scopes differ. True-label group routing is explicitly acknowledged by the authors and supports class-conditioned exploration. Held-out sample/subject lookup rows receive no training gradient without an inductive graph generator. With-replacement window selection can duplicate one original window under different new IDs on opposite split sides. The all-ones bug masks some graph differences, and no published leakage percentage is measured.



### Finding and scope

Known-label routing is a preserved author-acknowledged clarification; held-out-row interpretation and possible duplicate-window leakage are bounded additional release concerns.



### Proposed correction

Keep label-conditioned group structure exploration separate from label-blind classification. Specify an inductive or adaptation protocol for unseen graph rows and split by preserved original-window identities to prevent duplicate-window overlap.

A local correction or qualification is proposed where specified; author adoption is not established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
