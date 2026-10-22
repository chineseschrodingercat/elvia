# Rethinking Approximate Gaussian Inference in Classification



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The exponential Dirichlet safeguard can be non-real, the current concentration uses a different final denominator, and an appendix variance lower bound fails for negative correlations. These bounded findings leave the main normCDF/sigmoid predictive construction and benchmark rankings unrefuted.



## Scope

Rapid claim-focused reading of current author-paper passages and relevant released source. Direct mathematical or static-source reasoning is stated below. No author program, inherited verifier, model inference or benchmark was executed.



## Problem 1: The positivity safeguard fails for the exponential branch

Assessment: supported; impact: minor



Source: Latest arXiv v4, Section 4.1, Eq.(27), PDF pp.6–7; Appendix E.2.2 exponential specialization



### Source claim (paraphrase)

The Dirichlet construction uses \(A=\sum_ca_c,S=\max(A,1)\), \(L=[\prod_c(a_cS-b_c)/(b_c-a_c^2)]^{1/C}\), and \(\gamma=La/A\), asserting that the safeguard ensures positivity.



### Analysis

For independent Gaussian coordinates with variances \((\log3,\log(3/2))\) and means equal to minus half those variances, exact exponential moments give \(a=(1,1),b=(3,3/2),A=S=2\). Both variances are positive and all moments finite. The ratios are \(-1/2\) and \(1\), so \(L=\sqrt{-1/2}\) is not real. No singularity, underflow or approximate sigmoid integral is involved.

For exact bounded activations \(0<Q_c<1\) with positive variance, \(b_c<a_c\), so the same safeguard does give positive numerators. The current implementation also clips moment ratios before taking logarithms, preventing a non-real result but adding a separate regularization. That is not a proof of the unrestricted exponential formula.



### Finding and scope

Restrict the exponential Dirichlet domain or specify the additional regularization. The main bounded-activation predictive construction and empirical comparisons are not refuted.



### Proposed correction

The supplied sufficient domain is \(a_c>0,b_c>a_c^2,S>\max_cb_c/a_c\). Every factor is then positive, making \(La/A\) well-defined. This establishes existence on that domain, not approximation accuracy.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Problem 2: The current concentration uses the floored normalization twice

Assessment: supported; impact: minor



Source: Latest arXiv v4 Eq.(27) and Appendix E.2.4; current author probit/utils/predictive.py, get_mom_dirichlet_approximation, lines 446–471



### Source claim (paraphrase)

The formula returns \(La/A\); the current source returns \(La/S\), so when \(A<1\) the total concentration is scaled by \(A\).



### Analysis

For two independent Gaussian coordinates with \(\mu=-2\log3,v=24/\pi\), the stated sigmoid-moment approximations give \(a_c=1/4,b_c=5/32\). Thus \(A=1/2,S=L=1\), with positive unclipped moment ratios. The manuscript gives \(\gamma=(1/2,1/2)\), while the source gives \((1/4,1/4)\). Both means are \((1/2,1/2)\), but component variances are \(1/8\) versus \(1/6\), and expected entropies are \(2\log2-1\) versus \(\pi/2+\log2-2\). The discrepancy affects concentration-dependent uncertainty, not the unchanged mean predictive.



### Finding and scope

The current public function differs from the formula on valid inputs. The source predates the final paper; its attribution to the original uncertainty rankings is unresolved.



### Proposed correction

Keep \(S\) inside scalar moment ratios but divide the final vector by \(A\), the already-computed sum of first moments. This restores formula correspondence on its valid domain, subject to separately declared clipping.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Problem 3: Negative lognormal covariances defeat an unrestricted variance bound

Assessment: supported; impact: minor



Source: Latest arXiv v4, Appendix K.1, Eq.(111), PDF p.34



### Source claim (paraphrase)

The explanatory bound uses \(\operatorname{Var}(\sum_ie^{X_i})\geq\operatorname{Var}(e^{X_j})\) for general multivariate Gaussian logits.



### Analysis

Let \(\mu=(0,0)\) and covariance have diagonal \(\log(4/3)\) and off-diagonal \(\log(4/5)\). Its eigenvalues are \(\log(16/15),\log(5/3)>0\). Individual lognormal variances are \(4/9\), covariance is \(-4/15\), and sum variance is \(2(4/9)+2(-4/15)=16/45<4/9\). Positive-definite Gaussian covariance therefore does not supply the displayed lower bound.



### Finding and scope

The appendix needs a covariance restriction. Diagonal and nonnegatively correlated cases retain the bound, and the exact individual exponential moments remain valid.



### Proposed correction

Retain the full variance sum including cross-covariances, or require nonnegative off-diagonal Gaussian covariances so that all lognormal cross terms are nonnegative.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- Exact calculations and static-source findings do not remeasure published experiments or establish the historical experiment-generating revision.
