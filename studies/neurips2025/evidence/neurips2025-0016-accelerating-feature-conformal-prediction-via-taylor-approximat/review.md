# Accelerating Feature Conformal Prediction via Taylor Approximation



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The multidimensional pooled-score extension, unrestricted shortest-layer selection and printed RAPS rank direction do not inherit the claimed coverage guarantees; explicit exchangeable constructions show the failures. Local gradient/shape/indexing and reporting faults are Minor where historical result effects are unestablished. Scalar fixed-score conformal validity remains intact.



## Scope

All twenty original concerns and their current paper passages checked, including positive scalar fixed-score rank guarantee and distinct multidimensional/selected-layer extensions. Current pinned implementation branches read; no author or old verifier code executed.



## Problem 1: Coordinate pooling does not give coordinatewise or joint coverage

Assessment: supported; impact: major



Source: Current paper, Remark 1 and Eqs. (9)–(11), pp. 5–6; vector coverage Eq. (13), p. 8; segmentation description, p. 9.



### Source claim (paraphrase)

Pooled coordinate calibration inherits coordinatewise and whole-vector coverage.



### Analysis

Take \(n=99\), \(d=11\), \(\alpha=0.1\), and deterministic IID vectors \(Y=(0,\ldots,0,1)\). Let \(h(X)=0\) and \(g(v)=v\), so predictions are zero but all Jacobian row norms are one. Pooling the coordinate scores gives \(990\) zeros and \(99\) ones. Even the finite-rank index \(\lceil1090\cdot0.9\rceil=981\) selects zero. Thus the last coordinate and the whole-vector event have coverage zero, while coordinate-average coverage is \(10/11>90\%\).



### Finding and scope

Exchangeability across sample vectors does not imply exchangeability of their coordinates. The example refutes fixed-coordinate and simultaneous-vector guarantees, but preserves the weaker average-coordinate interpretation and the scalar rank proof.



### Proposed correction

Calibrate each preselected coordinate from its \(n\) sample scores, or calibrate a per-vector maximum score for simultaneous coverage. Specify which event is intended.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: The computed gradient is for the output sum

Assessment: supported; impact: minor



Source: FastFeatureCP/conformal/helper.py



### Source claim (paraphrase)

The backward operation supplies each output’s required gradient norm.



### Analysis

An all-ones backward vector gives the gradient of the sum of outputs. For \(g(v)=(v,-v)\), this gradient is zero while each separate Jacobian row has norm one.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: Interval construction hardcodes ten outputs

Assessment: supported; impact: minor



Source: FastFeatureCP/conformal/icp.py



### Source claim (paraphrase)

The interval method infers output dimension and returns one interval per output.



### Analysis

The code uses y_test.shape[\(0\)], which counts samples, where output dimension is needed, and allocates \((n_{\rm test},10,2)\). Three scalar test samples therefore get ten intervals each, while two-dimensional outputs cause incompatible flattened shapes.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: Shortest-layer selection breaks the fixed-score guarantee

Assessment: supported; impact: major



Source: Current paper, Table 2 caption, p. 7, and evaluation rule, p. 8; author FastFeatureCP/main.py, lines 99–111 and result selection.



### Source claim (paraphrase)

The shortest empirically selected layer retains the fixed-score conformal guarantee.



### Analysis

Use one calibration sample and target coverage \(1/2\). Let \(X\in\{A,B\}\) be equiprobable, \(Y\sim U(0,1)\), and \(f=0\). Two fixed-layer scales are \((1,100)\) and \((100,1)\) on \((A,B)\). Each fixed layer has exact marginal coverage \(1/2\). Selecting the shorter interval gives coverage \(\frac12\cdot\frac12+\frac12\cdot\frac1{200}=0.2525\).

These scales can arise in one network: take \(T(x,z)=(x,a(x)z)\), \(g(x,u)=b(x)u\), with \(z=0\), \(a(A)=0.01,a(B)=100,b(A)=100,b(B)=1\). The relevant gradient norms are \(ab\) and \(b\), exactly the two scales. Conditional on the calibration group, the same layer is no wider at every test point, so choosing by any nonempty finite test set's mean length has the same failure.



### Finding and scope

This refutes unconditional inheritance of the fixed-layer rank guarantee. The \(25.25\%\) value is for this explicit one-calibration-sample construction, not a reproduction of the paper's datasets or nominal \(90\%\) experiment.



### Proposed correction

Select the layer using data independent of final calibration/test data, freeze it, then calibrate anew; conditional exchangeability restores the fixed-score rank argument.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 5: Zero scales require a complete score rule

Assessment: supported; impact: minor



Source: FastFeatureCP/conformal/icp.py



### Source claim (paraphrase)

The score and interval rules are defined at zero gradient.



### Analysis

Positive residual/zero scale gives infinity; zero/zero gives NaN; inversion can encounter zero times infinity. Masked division without initialized output also leaves skipped positions unspecified.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 6: The infinity quantile is truncated

Assessment: supported; impact: minor



Source: FastFeatureCP/conformal/icp.py



### Source claim (paraphrase)

The finite-sample conformal quantile is implemented including its infinity case.



### Analysis

When \(\lceil(n+1)(1-\alpha)\rceil>n\), finite-sample conformal calibration needs the infinity atom. With \(n=4,\alpha=0.1\), returning the largest finite score gives continuous exchangeable coverage \(4\)/\(5\) rather than 0.9.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 7: Localized weights and normalization are incomplete

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 21; FastFeatureLCP/conformal/icp.py



### Source claim (paraphrase)

The localized weights define the stated probability distribution and coverage procedure.



### Analysis

Printed raw-distance weights favor distant samples; adding a unit infinity atom to already normalized weights gives mass two. The code instead uses exponential distance decay. A local guarantee needs one explicitly normalized rule.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 8: The weighted quantile is one index too low

Assessment: supported; impact: minor



Source: FastFeatureLCP/conformal/icp.py



### Source claim (paraphrase)

The weighted empirical quantile selects the first cumulative threshold crossing.



### Analysis

Subtracting one after the cumulative-weight threshold selects the preceding score. Scores \(1\)–\(19\) with equal weights and \(\alpha=0.1\) yield \(17\) rather than \(18\), with expected exchangeable coverage \(17/20=85\%\) for that rule.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 9: CQR calibration levels disagree

Assessment: supported; impact: minor



Source: Paper pp. 20; FastFeatureCQR/conformal/icp.py



### Source claim (paraphrase)

The CQR paper and release use the same calibration level.



### Analysis

The maximum of the two-sided normalized errors already defines one score. Paper level \(1-\alpha/2\) versus source \(1-\alpha\) selects order statistics \(95\) and \(90\) at \(n=99,\alpha=0.1\).



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 10: RAPS pseudocode reverses quantile order

Assessment: supported; impact: major



Source: Current paper, Algorithm 5, steps 3–4, p. 22; author FastFeatureRAPS/conformal.py, line 225 uses the upper quantile instead.



### Source claim (paraphrase)

The RAPS order-statistic direction gives the upper conformal threshold.



### Analysis

Algorithm 5 requests the \(k=\lceil(1-\alpha)(n+1)\rceil\)-th largest score. At \(n=99,\alpha=0.1\), this is the tenth smallest, instead of the ninetieth smallest. Take \(K=100\), \(h(X)=0\), \(g(v)=\operatorname{softmax}(cv)\), with \(c=K/\sqrt{K-1}\). Every class probability is \(1/K\), and each Jacobian row has norm \(1/\sqrt K=0.1\), so the example does not rely on a zero gradient. Set \(\delta=0\) and \(k_{\mathrm{reg}}=100\), making the nonnegative rank penalty inactive. Break prediction ties by one fixed class order. A random permutation of one sample per class gives an exchangeable sequence. Enumerating its possible held-out test classes while retaining the algorithm’s extra-one set-size rule gives coverage \(11/100\) for the printed reverse order and \(91/100\) for ascending order. The current source uses an upper np.quantile and does not implement the printed reversal; \(11\%\) is not attributed to the published experiment.



### Finding and scope

The printed direction defeats the intended coverage guarantee. The author code uses an upper-tail quantile rather than this reversed order, so \(11\%\) is not assigned to the published classification tables.



### Proposed correction

Use the required ascending upper order statistic and specify its finite-sample, tie and prediction-set inversion rules together.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 11: The feature norms differ across methods

Assessment: supported; impact: minor



Source: Paper pp. 5; FastFeatureCP/main.py; conformal/icp.py



### Source claim (paraphrase)

FCP and FFCP compare the same feature perturbation norm.



### Analysis

Default FCP uses infinity-norm perturbations while FFCP uses Euclidean gradient norms. The linearized radius uses the dual norm: \(a=(1,1)\), residual \(1\) gives \(1/2\) versus \(1/\sqrt2\), so the two comparisons differ.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 12: The efficiency proof lacks a sample-to-test step

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 16



### Source claim (paraphrase)

The efficiency proof establishes the independent-test expectation comparison.



### Analysis

The argument mixes an empirical quantile, a same-dataset average and an independent test expectation without a complete conditioning/independence step. This is a proof gap, not a counterexample to the full theorem.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 13: The diagnostic omits a scale-dependent regularity constant

Assessment: supported; impact: minor



Source: Paper pp. 18



### Source claim (paraphrase)

The empirical score-concentration diagnostic verifies the regularity condition independent of units.



### Analysis

Use the reparameterization \(h_c=ch\), \(g_c(v)=g(v/c)\), with \(c>0\). Predictions remain unchanged; a gradient scale \(s\) becomes \(s/c\), scores \(R\) and their quantile \(q\) become \(cR\) and \(cq\), and the interval radius remains \(sq\). Absolute score concentration nevertheless changes with \(c\). The current Appendix B.2 explicitly ignores the Hölder/Lipschitz factor while comparing concentration, so that comparison alone cannot verify the complete dimensional inequality in Theorem A.1. This limits the assumption diagnostic, not the conformal interval’s invariance.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 14: Five displayed coverages are below target

Assessment: supported; impact: minor



Source: Paper pp. 8, 7



### Source claim (paraphrase)

Every reported empirical coverage exceeds \(90\) percent.



### Analysis

FB \(2\), MEPS \(20\), MEPS \(21\), BIO and BIKE show \(89.868\), \(89.615\), \(89.745\), \(89.875\) and \(89.624\) percent, below 90. This refutes the descriptive universal sentence; a marginal theorem does not demand every finite observed coverage exceed target.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 15: Equivalent-layer tables conflict

Assessment: supported; impact: minor



Source: Paper pp. 7–8



### Source claim (paraphrase)

Layer \(4\) is equivalent to the Split-CP entries and selected values match the layer table.



### Analysis

Layer \(4\) is called equivalent to Split CP, yet all eleven corresponding lengths differ. Some alleged best-layer values are also below every listed candidate. Different runs could explain the discrepancy but require provenance.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 16: SSCP summaries exceed displayed comparisons

Assessment: supported; impact: minor



Source: Paper pp. 25



### Source claim (paraphrase)

FFCP is shorter in every SSCP comparison and all speed ratios lie in the stated range.



### Analysis

BIO FFCP length \(1.66\) exceeds SSCP \(1.53\) by \(8.50\%\); MEPS \(19\) timing ratio \(10.86/0.14\simeq77.57\) exceeds the stated \(2\)–\(50\) range. Other favorable comparisons remain.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 17: Response grouping is not conditioning on inputs

Assessment: supported; impact: minor



Source: Paper pp. 21, 23; FastFeatureCP/main.py



### Source claim (paraphrase)

The grouping evaluates the described conditional-on-input coverage.



### Analysis

The implementation groups by true \(Y\) quantiles, yielding a response-stratified diagnostic rather than conditional-on-\(X\) coverage. Lowest versus highest group aggregation is also inconsistently described.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 18: FCP length and coverage describe different sets

Assessment: supported; impact: minor



Source: FastFeatureCP/main.py



### Source claim (paraphrase)

The reported FCP length and coverage correspond to the same output prediction set.



### Analysis

Length comes from an output-space enclosure while coverage comes from feature membership. An enclosure may contain additional outputs, so the two events are not interchangeable and are not paired like CP/FFCP output intervals.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 19: A segmentation import is absent

Assessment: supported; impact: minor



Source: FastFeatureCP_seg/main_fcn.py



### Source claim (paraphrase)

The segmentation entry imports an available local module.



### Analysis

The author entry imports conformal.icp_pixelquantile, which is missing in that snapshot. Installing external dependencies alone cannot resolve a missing local module.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 20: Other commands and explanations need correction

Assessment: supported; impact: minor



Source: Repository README and CQR/RAPS entry points; classification helper's float-temperature branch; official PDF: Table 3 caption and appendix experiment settings.



### Source claim (paraphrase)

The documented commands, gradient explanation and repeated-run settings match the release.



### Analysis

README names missing main_CQR.py instead of main_FFCQR.py and a wrong RAPS directory. A nondefault float-temperature branch uses detach.cpu() incorrectly; actual seed lists and gradient direction also need reconciliation.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- No new author-code execution, training, empirical replication or contact.

- Historical verification outputs were inspected but not rerun.

- Missing run provenance and unresolved empirical interpretations remain explicit.
