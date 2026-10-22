# Confusion-Driven Self-Supervised Progressively Weighted Ensemble Learning for Non-Exemplar Class Incremental Learning



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



A fixed expert cap disagrees with the \(1/K\) formula and can erase the sole eligible class expert. The current shared-prefix path also leaves stem parameters and BatchNorm state mutable.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: A fixed \(0.2\) expert cap disagrees with Eq. (5) and can make class normalization undefined

Assessment: supported; impact: minor



Source: Section 3.4, Eq. (5), PDF pp. 6–7; released expert-weight cap and class-normalization implementation.



### Source claim (paraphrase)

Paraphrase preserving the relevant domain: Section 3.4, pp. 6–7, assigns newly introduced experts weight \(\alpha\), increases it by \(\beta\) per subsequent task, and caps each non-base weight at \(1/K\). Equation (5) gives, for active experts,

\[ w_i(t)=\min\{\alpha+\beta(t-i),1/K\}\quad(i>0),\qquad w_0(t)=1-\sum_{i=1}^{\min(t,K-1)}w_i(t). \]



### Analysis

For \(K=3\), the stated saturated expert weights are \((1/3,1/3,1/3)\), but a fixed \(0.2\) cap gives \((0.6,0.2,0.2)\). For \(K=6\), five non-base weights of \(0.2\) leave base weight zero, so a class eligible only for the base expert encounters normalization \(0/0\). These permitted settings show a local cap mismatch, not failure of every default run.

The explicit legal schedule uses \(K=6\), initial weight \(0.10\), increment \(0.05\), and \(40\) base classes followed by \(20\) tasks of \(3\) classes. At task \(7\), the five non-base weights reach \(0.2\), making the base residual zero. Under the paper cap \(1/6\), the residual is at least \(1/6\). The default \(K=5\) cap agrees with the formula.



### Finding and scope

The general expert-count release can become undefined, but the main five-expert configuration passes this specific cap control.



### Proposed correction

Use cap \(1/K\), with initial weights also in \([0,1/K]\) and nonnegative increments. At most \(K-1\) non-base weights then leave residual at least \(1/K>0\), preserving positive class denominators through the always-eligible base expert.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 2: The released shared, frozen ResNet prefix can change during later-expert training

Assessment: supported; impact: minor



Source: Section 3.2, PDF p. 5; Section 4.1, PDF p. 8; Appendix C.3 and Table 9, PDF pp. 23–24; released clover.py sharing loop.



### Source claim (paraphrase)

Section 3.2, PDF p. 5, states a shared encoder frozen after the first task. Section 4.1 and Appendix C.3, PDF pp. 8 and \(23\)–\(24\), describe sharing its first layers. Released clover.py, lines 74–81 and \(211\)–\(229\), chooses parameter names \(\texttt{conv1\_starting}\) and \(\texttt{bn1\_starting}\), aliases selected parameters and disables their gradients. The actual network stem in resnet_linear_turbo.py is named \(\texttt{conv1}\) and \(\texttt{bn1}\). Each training epoch also calls model.train().



### Analysis

The requested stem names do not match the actual \(\texttt{conv1}\) and \(\texttt{bn1}\) parameters, leaving those parameters trainable. Even corrected parameter aliases omit BatchNorm running-mean and variance buffers, which model.train() updates. Freezing gradients therefore does not preserve the claimed single shared frozen encoder function.



### Finding and scope

Stem-name mismatch and mutable BatchNorm state defeat the claimed released prefix invariant; corrected benchmark accuracy and historical checkout correspondence remain unknown.



### Proposed correction

Share the actual prefix modules, freeze their parameters, and restore the frozen BatchNorm modules to evaluation mode after each general training-mode call. Parameter flags alone do not freeze buffers.

A local correction or qualification is proposed where specified; author adoption is not established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
