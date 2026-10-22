# Model Inversion with Layer-Specific Modeling and Alignment for Data-Free Continual Learning



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The released feature compensation fails to restore its target mean. The contrastive selection objective and temperature argument also differ, while the evidence-term concern is limited to changing synthetic marginals.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The feature compensation rescales the target mean instead of restoring it

Assessment: supported; impact: minor



Source: Section 3.3, PDF pp. 5–6; released CLIP/inversion/cont_model.py, contrastive_selection.



### Source claim (paraphrase)

Section 3.3, PDF pp. 5–6, motivates alignment of synthetic and real features. Released CLIP/inversion/cont_model.py, contrastive_selection, lines 177–188, and the corresponding ResNet compensation around lines 545–556 target a prescribed mean \(\mu\) and standard deviation \(\sigma\). For selected mean \(\bar z\) and standard deviation \(s\), they use \(b=\mu-\bar z\), \(a=\sigma/(s+10^{-8})\), and \(z_i^{\rm code}=(z_i+b)a\).



### Analysis

The mean of that expression is \((\bar z+\mu-\bar z)a=\mu a\), rather than \(\mu\). For selected features \((10,18,26)\), mean \(18\), sample standard deviation \(8\), and targets \(\mu=10\), \(\sigma=4\), the result is approximately \((1,5,9)\), with mean \(5\) and standard deviation \(4\). Centering first and restoring the mean after scaling gives \((6,10,14)\). The stabilizing epsilon changes the approximation slightly but not the mean-restoration defect.



### Finding and scope

The compensation’s empirical mean is algebraically wrong for nonzero target mean and nonunit scale, but downstream accuracy effects and publication-run lineage are not established.



### Proposed correction

Center the selected sample, rescale its residuals, and add the target mean after scaling. Any reported finite implementation checks are historical; benchmark effects are unmeasured.

A local correction or qualification is proposed where specified; author adoption is not established.

The existing local proposal is retained; no author correction of the cited current formula or release path was identified.



## Problem 2: The contrastive loss, selection ranking, and temperature explanation use different objectives

Assessment: supported; impact: minor



Source: Section 3.3, Eq. (6), PDF p. 6; Algorithm 2; Appendix D.3, Eq. (28), PDF p. 21; current CLIP/inversion/cont_model.py, lines 54–79.



### Source claim (paraphrase)

Section 3.3, PDF p. 6, Eq. (6), defines the negative contrastive objective as

\[ L_{\rm cont}(x,S)=\log\frac1{|S|}\sum_{y\in S} \exp\{\cos(f(x),f(y))\},\qquad x\notin S. \]

The prose selects by mean cosine similarity, the named equation uses log-mean-exponentiated similarity, and Appendix D.3 argues that temperature does not change rankings. The current selection code uses the former, while its training code includes self-pairs excluded in the equation.



### Analysis

For selected unit vectors \(e_1,e_2\), choose unit candidates \(A=(0.7,-0.7,\sqrt{0.02})\) and \(B=(0.1,0.1,\sqrt{0.98})\). Their mean cosines are \(0\) and \(0.1\), while their log-mean-exponential scores are \(\log\cosh(0.7/T)\) and \(0.1/T\). The first exceeds the second at \(T=1\), but is smaller for sufficiently large \(T\). Mean cosine, log-mean-exponential and diagonal-inclusive objectives therefore need not induce the same ranking.

At \(T=1\), the log-mean-exponential scores are \(0.2272702294\) for \(A\) and \(0.1\) for \(B\); at \(T=4\), they are \(0.0152349749\) and \(0.025\), reversing the preferred candidate. For two orthogonal unit features, diagonal-excluded loss is \(0\), while the current diagonal-inclusive loss is \(\log((e+1)/2)\approx0.6201145070\). These are distinct objectives, not a universal additive shift.



### Finding and scope

Valid unit-vector examples reverse the stated rankings and expose different self-pair treatment; the method’s empirical benefit is not disproved.

The current contrastive training function additionally constructs Adam, whereas the paper’s contrastive-MLP protocol specifies SGD. This protocol discrepancy is retained without assigning a measured benchmark effect.



### Proposed correction

Either implement log-mean-exp selection with self-exclusion in training and acknowledge temperature-dependent ranking, or explicitly distinguish the existing mean-cosine selection from a self-including training objective. Choosing the intended alternative requires author intent and experimental provenance.

The existing local proposal is retained; no author correction of the cited current formula or release path was identified.



## Problem 3: A real-data evidence density is not constant under a changing synthetic marginal

Assessment: supported; impact: minor



Source: Eq. (3), PDF p. 4; Appendix B, Eq. (19), PDF p. 16; full-model objective Eqs. (5)/(22), PDF pp. 5/17.



### Source claim (paraphrase)

Eq. (3), PDF p. 4, and its detailed derivation in Appendix B, Eq. (19), PDF p. 16, use Bayes’ rule to obtain

\[ \begin{aligned} D_{\rm KL}(p_s(o_{l-1}\mid o_l)\Vert p_r(o_{l-1}\mid o_l)) ={}&D_{\rm KL}(p_s(o_{l-1}\mid o_l)\Vert p_r(o_{l-1}))\\ &-\mathbb E_{p_s(o_{l-1}\mid o_l)}\log p_r(o_l\mid o_{l-1}) +\log p_r(o_l). \end{aligned} \]



### Analysis

An evidence density can be constant with respect to parameters in a frozen-target PMI subproblem yet depend on the synthetic marginal when that distribution changes. Dropping it is justified only for the former optimization. The following two-state construction addresses the latter scope, not every frozen-layer update.

Let one deterministic identity layer act on \(\{0,1\}\), with real marginal \(r=(0.9,0.1)\) and positive synthetic marginal \(q\). The original joint objective is \(D_{\rm KL}(q\Vert r)\), minimized at \(q=r\). The inverse-conditionals are identical point masses, so their prior term \(-\log r_z\) cancels evidence \(+\log r_z\). Dropping the averaged evidence leaves \[\widetilde J(q)=\sum_zq_z\log q_z-2\sum_zq_z\log r_z,\] whose minimizer is \(q_z\propto r_z^2\), namely \[(0.9878048780,0.0121951220)\]. This differs from \(r\) even though the conditional-independence approximation is exact. The later Gaussian surrogate and fixed-target PMI subproblem are not disproved by this discrete diagnostic.



### Finding and scope

Supported derivation-scope qualification; no universal claim that the complete continual-learning method fails is established.



### Proposed correction

For a theoretical joint objective, retain the full averaged evidence term, or explicitly state and enforce a fixed marginal over the targets. Restoring it in this example cancels the spurious cross-entropy contribution and recovers \(D_{\rm KL}(q\Vert r)\), with minimizer \(q=r\). That restoration follows exactly from Bayes’ rule and the displayed calculation.

A local correction or qualification is proposed where specified; author adoption is not established.

The existing local proposal is retained; no author correction of the cited current formula or release path was identified.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
