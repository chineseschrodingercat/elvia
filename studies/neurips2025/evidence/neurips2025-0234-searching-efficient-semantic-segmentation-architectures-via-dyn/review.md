# Searching Efficient Semantic Segmentation Architectures via Dynamic Path Selection



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The variational input-information expression is not an unconditional upper bound. Maximizing it over the conditional model can diverge while worsening conditional fit. The printed stage rule separately advances on decreasing loss and misses an exact plateau.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: The variational expression needs an upper-bound condition

Assessment: supported; impact: major



Source: Section 3.1, Eq.(8), p.5; multi-scale Eq.(9)



### Source claim (paraphrase)

The paper claims \(I(X;Z)\le U(q)=\mathbb E_{XZ}\log q(Z|X)-\mathbb E_X\mathbb E_Z\log q(Z|X)\) for a normalized neural conditional without a fitting condition.



### Analysis

Let independent bits \(A\) be fair and \(N\) have probability \(1/4\) of one; set \(X=(A,N)\), deterministic feature \(Z=A\mathbin{\mathrm{xor}}N\). Then \(I(X;Z)=H(Z)=\log2\), while valid zero-logit conditional \(q(z|x)=1/2\) gives \(U=0\). With \(P=P_{XZ},Q=P_XP_Z,R=P_Xq\), direct cancellation yields \[U(q)-I(X;Z)=D_{\mathrm{KL}}(Q\|R)-D_{\mathrm{KL}}(P\|R).\] Thus the missing condition is the corresponding nonnegative KL difference. A full-support binary joint with masses \((3/8,1/8;1/8,3/8)\) also has positive MI and zero surrogate under constant conditional, so zero joint probabilities are not essential.



### Finding and scope

The unconditional bound and resulting guaranteed bottleneck relation are invalid. Empirical architecture ranking can still be useful. This caveat is already explicit in original CLUB, Theorem 3.2.



### Proposed correction

State the inequality only when \(D_{\mathrm{KL}}(P\|R)\le D_{\mathrm{KL}}(Q\|R)\), with required finiteness. Fitting the conditional can help but does not by itself guarantee this condition or tightness.

The original CLUB literature already states the needed condition; no author correction to this paper’s unqualified equation is established.



## Problem 2: Maximizing the bound is not conditional fitting

Assessment: supported; impact: major



Source: Section 3.1, paragraph after Eq.(8); Algorithm 2, p.13, lines 13–15



### Source claim (paraphrase)

The conditional estimator parameters ascend the positive-minus-negative log-conditional expression, described as fitting/tightening the bound.



### Analysis

On the same deterministic distribution, choose \(q_a(Z=A|X)=\sigma(a)\), ignoring \(N\). Joint matching probability is \(3/4\), product matching probability \(1/2\), so \(U(a)=a/4\), with derivative \(1/4\) and no finite maximizer. Actual conditional likelihood is \(L(a)=3\log\sigma(a)/4+\log(1-\sigma(a))/4\), uniquely maximized at \(a=\log3\); it tends to \(-\infty\) as the printed objective increases unboundedly. In the full-support noisy binary control, the same family is well specified and the same failure holds, so misspecification is not the explanation.



### Finding and scope

The printed ascent cannot be interpreted as conditional maximum likelihood or general tightening. The official supplement provides final-model evaluation, not the search/estimator implementation, so historical execution attribution remains unknown.



### Proposed correction

For fixed encoder/distribution, maximize joint conditional log likelihood \(\mathbb E_P\log q_\phi\), equivalent to minimizing \(D_{\mathrm{KL}}(P\|P_Xq_\phi)\), then evaluate the surrogate separately. This restores fitting, not unconditional bound validity or architecture-ranking consistency.

Original CLUB Eq.(16) and Algorithm 1 use conditional likelihood fitting; adoption of that procedure in this paper’s unavailable search code is not established.



## Problem 3: The stage rule reverses loss improvement and misses plateaus

Assessment: supported; impact: minor



Source: Section 3.2, p.7; Algorithm 3, p.14, lines 36 and 40–42



### Source claim (paraphrase)

Stage II stores raw loss but transitions when its mean forward difference is below \(\epsilon\operatorname{std}(W)\), using a strict comparison.



### Analysis

A full \(20\)-point window \((1,0.99,\ldots,0.81)\) has forward difference \(-0.01\) and positive threshold approximately \(2.3065\times10^{-6}\) at \(\epsilon=4\times10^{-5}\); the literal rule transitions during steady improvement. A constant window has both quantities zero, so strict \(0<0\) fails and no transition occurs. Restoring only a nonnegative guard does not fix raw-loss sign. Higher variance also raises the threshold, easing the comparison when improvement is held fixed.



### Finding and scope

The literal pseudocode conflicts with its saturation description. A hidden sign/guard correction may make the actual implementation different; no segmentation failure is asserted.



### Proposed correction

Use benefit-oriented values, including negative loss, and a complete stage-specific window. A rule \(0\le\Delta\le\epsilon_{\rm abs}+\epsilon_{\rm rel}\operatorname{std}(W)\), \(\epsilon_{\rm abs}>0\), handles the displayed controls. Reset histories and define deterioration/final-stage policies; no general optimization theorem follows.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.
