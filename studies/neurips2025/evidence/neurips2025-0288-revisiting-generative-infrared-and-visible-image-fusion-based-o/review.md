# Revisiting Generative Infrared and Visible Image Fusion Based on Human Cognitive Laws



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The semantic transport justification fails on regular finite models. A Gaussian bound lacks a real domain restriction; released preprocessing and empirical-scope statements have separate local discrepancies.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Marginal transport improvement does not establish semantic gain

Assessment: supported; impact: major



Source: Theorem 1, Eq. (4); Appendix A.1



### Source claim (paraphrase)

The theorem chains input information bounds into a claimed semantic-information improvement from marginal Wasserstein alignment.



### Analysis

Let independent fair bits \(C,U\) form \(X=Y=(C,U)\), and \(Z=U\oplus E\) with independent crossover \(E\sim\operatorname{Bernoulli}(1/4)\). A decoder reading only the nuisance bit has positive probabilities and globally Lipschitz negative log probabilities after clipped linear extension. Equal marginals give optimal transport reduction \(\Delta=0\). Yet \(I(Z;C)=0\), \(I(Z;X,Y)=r=\log2-h(1/4)>0\), and admissible residual bound \(\varepsilon=r\) makes the printed chain \(0\ge0\ge r\), false. Independently, let \(X=C\) be a fair bit, \(Y=0\), and decoder probability \(q(Z=1\mid x)=1/4+x/2\). Optimal transport maps \(X\) to zero, reducing Wasserstein distance \(1/\sqrt2\to0\), but the rerun encoder’s task information drops \(r\to0\). Regularity holds and no task-sufficiency premise excludes this.



### Finding and scope

The chain omits a necessary residual term, and even restoring it does not prove that marginal alignment preserves or improves semantics. Transport can remain an empirically useful heuristic.



### Proposed correction

For \(W=(T(X),Y)\) and \(C\to W\to Z_T\), the valid identity is \(I(Z_T;C)=I(Z_T;W)-I(Z_T;W\mid C)\). An upper residual bound gives its corresponding lower bound only; a transport-gain theorem needs task-sufficiency and joint-law control.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: The Gaussian information bound lacks its real-valued domain

Assessment: supported; impact: minor



Source: Theorem 2, Eq. (10); Appendix A.2



### Source claim (paraphrase)

The bound contains \(-\log(1-\operatorname{Var}(\mu_i)/\sigma_i^2)\) without requiring the ratio below one.



### Analysis

Choose independent \(\mu\sim N(0,2)\), \(R=\epsilon\sim N(0,1)\), \(\sigma=1\). The joint covariance is positive definite, its normalized cross-covariance matrix is zero and satisfies the stated diagonal domination, but the ratio is \(2\). Actual information is zero, while the printed real logarithm is \(\log(-1)\). Also \(M\preceq\operatorname{diag}(M_{ii})\) forces exact diagonality, since their positive-semidefinite difference has zero trace. Independent encoder noise plus joint Gaussianity makes zero covariance imply independence; heteroscedastic non-Gaussian encoders need not satisfy that idealization.



### Finding and scope

A missing positivity restriction makes the formula undefined on its claimed domain. No real-valued too-small bound or actual learned-encoder violation is asserted.



### Proposed correction

Require \(0\preceq M\preceq D\prec I\) and ratios \(r_i<1\). Gaussian information \(-\log\det(I-M)/2\) and determinant monotonicity then give the restricted logarithmic bound; ratios at least one require an explicit vacuous convention.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: Training and evaluation feed different modality order to one encoder

Assessment: supported; impact: minor



Source: Algorithm 1/2; datasets/dataset.py; models/ddm.py, Net.forward; models/decom.py



### Source claim (paraphrase)

The dataset returns visible then infrared; training aligns infrared and passes aligned-infrared then visible, while evaluation forwards the original order without alignment.



### Analysis

For constant visible \(1\) and infrared \(0\), balanced transport helper \(.8(PY)+.2X\) yields aligned infrared \(.8\). Encoder inputs become \((.8,1)\) in training and \((1,0)\) at evaluation. An allowed first convolution selecting its second channel gives outputs \(1\) and \(0\), proving no architectural equivalence. The later decoder cannot retroactively change encoded skip features. Omitting alignment appears in inference pseudocode and may be deliberate; the channel reversal is an additional discrepancy.



### Finding and scope

Current source paths supply materially different conditioning to the same unconstrained encoder. No checkpoint quality change is quantified.



### Proposed correction

Define one intended modality order/preprocessing path and identify the path used by experimental checkpoints before evaluating a correction.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 4: Universal superiority exceeds the reported metric tables

Assessment: supported; impact: minor



Source: Quantitative comparison tables and corresponding discussion



### Source claim (paraphrase)

The text extends superiority to all fusion metrics.



### Analysis

The published headers specify metric directions. On MFNet, HCLFuse is best in only \(5\) of \(12\) displayed metrics including ties; for example CC \(0.5454\) is below DDFM \(0.6082\), and PIQE \(24.135\) is worse than CCF \(20.218\), where smaller is better. On FMB it is best in \(8\) of \(12\). The segmentation mean \(89.72\) is consistent with its displayed class averages, a retained positive control.



### Finding and scope

Metric-specific trade-offs contradict a universal ordering, without disputing the table measurements.



### Proposed correction

Describe superiority only on the supported metrics and retain competing strengths.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 5: Averaging does not establish statistical significance

Assessment: supported; impact: minor



Source: Checklist question 7



### Source claim (paraphrase)

The checklist infers statistical significance from averaging many dataset tests.



### Analysis

For \(1000\) paired bounded scores, take baseline \(.5\) throughout and method scores \(.601\) on half and \(.401\) on half. Mean gain is \(.001\), but exactly half the differences are positive, giving two-sided sign-test \(p=1\); the paired t statistic is about \(.316\). Thus many averaged observations do not by themselves prove significance. This example is a logical diagnostic, not the paper’s scores.



### Finding and scope

Actual significance remains undetermined without raw paired data and a valid inferential design.



### Proposed correction

Keep the descriptive means or supply paired uncertainty/testing aligned to independent scene/sequence units and checkpoint variation.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
