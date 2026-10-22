# Spectral Analysis of Diffusion Models with Application to Schedule Design



Preliminary assessment: No Issue Found

Independent scientific review: pending. Author adoption: not requested.



No substantive error was established in the core shared-basis diffusion derivation. Finite KL optimization needs a nonsingularity/common-support qualification, and the eigenvalue-only Wasserstein expression needs the shared eigenbasis already present in that derivation; empirical recurrence/FID results were not refuted.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The finite KL schedule objective needs a nonsingularity or common-support condition

Assessment: not_issue; impact: no_issue_found



Source: Section 3.3 (positive-semidefinite target covariance); Theorem 4.2, Eq. (16), PDF p. 6; Eq. (14) endpoint constraints.



### Source claim (paraphrase)

Theorem 4.2, Eq. (16), PDF p. 6, gives a Gaussian KL schedule objective, while Section 3.3 permits positive-semidefinite target covariances. Appendix D.2, Eq. (38), PDF pp. 17–18, gives the usual determinant/inverse expression; the issue concerns its finite-domain qualification, not a main-text transcription sign.



### Analysis

A singular target Gaussian is supported on a proper affine subspace. If the generated Gaussian retains positive variance in a target-null direction because the final noise floor is nonzero, the measures do not have the required absolute continuity and KL is infinite. A pseudodeterminant alone cannot turn incompatible supports into a finite objective.

For \(\Lambda_0=\operatorname{diag}(0,1)\), mean \((1,0)\), and endpoints \(\bar\alpha_0=0.9999\), \(\bar\alpha_S=0.00004\), the null-direction DDIM variance telescopes to \((1-\bar\alpha_0)/(1-\bar\alpha_S)=5/49998>0\). The target assigns mass one to \(v_1=1\), while the generated Gaussian assigns zero there, so KL is \(+\infty\). This extended-real result does not contradict the recurrence; finite optimization needs positive-definite covariances or equal affine supports. The exact covariance and regularization used in the synthetic KL plot are unavailable, so a numerical error in that plot is not established.



### Finding and scope

Domain qualification for a finite optimization objective; no incorrect reported numerical covariance construction or core spectral recurrence was established.



## Problem 2: The eigenvalue-only Wasserstein formula requires a shared eigenbasis

Assessment: not_issue; impact: no_issue_found



Source: Appendix D.1, Eq. (36); common-basis Lemma 3.3.



### Source claim (paraphrase)

Paraphrase: Appendix D.1 introduces the Wasserstein-\(2\) distance between two Gaussian distributions with means \(\mu_1,\mu_2\), covariances \(\Sigma_1,\Sigma_2\), and corresponding covariance eigenvalues using

\[W_2^2=\|\mu_1-\mu_2\|^2+ \sum_i\left(\sqrt{\lambda_i^{(1)}}-\sqrt{\lambda_i^{(2)}}\right)^2. \]



### Analysis

Covariances \(\operatorname{diag}(1,4)\) and \(\begin{pmatrix}2.5&-1.5\\-1.5&2.5\end{pmatrix}\) share eigenvalues but different orientations. Pairing only their sorted spectra would give zero, although their Gaussian Wasserstein distance is positive. The formula is valid under a shared eigenbasis, which the paper's central Gaussian derivation already supplies.

The unrestricted covariance calculation gives \(W_2^2=10-\sqrt{82}>0\), whereas sorted equal spectra give zero. In the paper’s own common eigenbasis, the Gaussian matrix-square-root formula reduces exactly to the displayed eigenvalue expression. The rotated example lies outside that already supplied common-basis condition.



### Finding and scope

Formula-scope qualification; the source core derivation already supplies its required common eigenbasis.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
