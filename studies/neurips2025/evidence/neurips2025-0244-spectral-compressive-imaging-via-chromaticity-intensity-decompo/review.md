# Spectral Compressive Imaging via Chromaticity-Intensity Decomposition



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current PAN-equivalence argument lacks quantitative response/spectral assumptions. Released top-k attention remains dense and quadratic, and test PSNR controls checkpoint saving. Actual sensor residuals and historical benchmark consequences are unresolved.



## Scope

Rapid claim-focused reading of current author-paper passages and relevant released source. Direct mathematical or static-source reasoning is stated below. No author program, inherited verifier, model inference or benchmark was executed.



## Problem 1: Normalized smooth spectra do not imply a common PAN factor

Assessment: supported; impact: minor



Source: Latest arXiv v2, Appendix A.3, Proposition A.1 and Eqs.(31)–(39), PDF p.20; proceedings corresponding pp.19–20



### Source claim (paraphrase)

The PAN/intensity argument obtains \(I_{{\rm PAN},p}=I_p\int q(\lambda)C_p(\lambda)d\lambda\), then treats the integral as approximately spatially constant from normalized smooth chromaticity and a qualitative broadband response.



### Analysis

On \([0,1]\), take \(L=1,s=1-(1-a)\lambda\), spectra \(X_+=a\lambda^n,X_-=a(1-\lambda)^n\), and reflectances \(R_\pm=X_\pm/s\). For \(0<a<1\), these reflectances are smooth and in \([0,1]\), and both intensities are \(a/(n+1)\). Their factors are \[k_+=a+\frac{1-a}{n+2},\qquad k_-=1-\frac{1-a}{n+2}.\] With \(a=1/10,n=8\), they are \(19/100\) and \(91/100\); equal intensities produce PAN ratio \(91/19\). The best common positive calibration has worst relative intensity error \((k_--k_+)/(k_-+k_+)=36/55\).

The approximation has no stated tolerance, so a nonzero difference alone is not a refutation of a calibrated apparatus. The family demonstrates that no uniformly small error follows from the written qualitative premises. Flat response or common chromaticity rescues the factor; global image normalization cannot remove material-dependent differences. The valid scalar-illumination cancellation and known-intensity reconstruction algebra survive.



### Finding and scope

The physical-approximation justification needs quantitative calibration assumptions. This does not refute useful empirical PAN guidance or the known-intensity reconstruction method.



### Proposed correction

The supplied bound is valid if \(\|q-k_0\|_\infty\leq\delta\) for known \(k_0>0\): \(|I_{\rm PAN}-k_0I|\leq\delta I\), hence relative calibrated error at most \(\delta/k_0\). A small actual ratio must be measured, not inferred from smoothness.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Problem 2: Dense top-k masking retains quadratic channel cost

Assessment: supported; impact: minor



Source: Latest arXiv v2, Section 2.3 and Eq.(23); current author architecture/CIDNet.py, TopkOperation and Topk_WindowSpectralAttn



### Source claim (paraphrase)

The spectral-attention discussion attributes a reduction from \(O(C^2)\) to \(O(KC)\) to top-k masking, with fixed retained channel fractions.



### Analysis

The actual source first forms all \(d^2\) scores, then creates dense masks, dense softmax outputs and a dense value product for each of four fractions. With \(P\) window positions, this retains \(\Theta(Pd^2)\) work. Even ideal sparse aggregation with \(K=\lfloor\rho d\rfloor\), fixed \(\rho>0\), is \(\Theta(Pd^2)\). A valid \(O(KC)\) upper expression therefore does not establish a smaller asymptotic order here.



### Finding and scope

The mechanism sparsifies support; the inspected implementation does not establish the claimed resource reduction. No hardware timing or reconstruction score is contradicted by these analytic counts alone.



### Proposed correction

Retain dense quadratic cost for this implementation and distinguish it from any measured constant-factor benefit. No new sparse kernel is proposed.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Problem 3: Test reconstruction error controls checkpoint saving

Assessment: supported; impact: minor



Source: Latest arXiv v2 experimental protocol; current author train.py, test-data loading and epoch loop, lines 132–143



### Source claim (paraphrase)

The training driver evaluates the named test scenes each epoch, updates the maximum test PSNR, and saves improving checkpoints above its threshold.



### Analysis

The selected epoch depends on \(\arg\max_e\operatorname{PSNR}_{\rm test}(\theta_e)\). Thus test targets affect model selection even without entering gradient updates. This is separate from the explicitly declared intensity input. A score on the same selected test set is consequently not a wholly untouched holdout estimate under this driver.

The current release matches the implicated supplemental routine. The source alone does not establish which saved checkpoint generated each historical table, whether another final holdout existed, or the size of selection optimism.



### Finding and scope

The current selection protocol uses test error; empirical correction requires the actual checkpoint and evaluation history.



### Proposed correction

Retain the supplied protocol correction: choose epochs using independent validation or a prespecified schedule, then evaluate on an untouched final test. No post hoc PSNR adjustment is justified.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- Exact calculations and static-source findings do not remeasure published experiments or establish the historical experiment-generating revision.
