# A Minimalist Example of Edge-of-Stability and Progressive Sharpening



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



This analysis gives an admissible counterexample to Lemma 4.5's lower constant and identifies distinct reduction/Hessian/monotonicity gaps. These affect the stated mathematical justification without proving every qualitative edge-of-stability claim false.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The \(0.75\) lower constant in Lemma 4.5 fails inside the stated initialization set

Assessment: supported; impact: major



Source: Lemma 4.5, PDF p. 7; proof in Appendix E.4, PDF p. 25.



### Source claim (paraphrase)

Lemma 4.5, PDF p. 7 and Appendix E.4, PDF p. 25, claims \(0.75L_2\le\widehat L\le3.3L_2\) for every stated initialization before \(T_4=\min\{t\ge0:b_2(t)\ge0.5\sqrt{\lambda_1\eta/2}\}\). Here \(L_2=(\lambda_2/2)(1-ab_2)^2\). To exclude a transcription-scale explanation, use the favorable intended surrogate \(\widehat L_c=(\lambda_2/2)(1-Ab_2)^2\), with \(A=\sqrt{2/(\lambda_1\eta)}\). The lower comparison still fails.



### Analysis

Set \(\lambda_1=100\), \(\lambda_2=1/100\), \(\eta=1/10\), and \((a,b_1,b_2)=(1/3,3/2000,11/10)\). These values satisfy the stated initialization and pre-stopping conditions. Even using the favorable intended normalization of the surrogate, direct substitution at \(t=0\) gives losses \(0.00129065045\) and \(0.00200555556\), whose ratio is \(0.64353762<0.75\). The lemma's lower bound therefore fails without relying on the omitted scale factor.



### Finding and scope

Lemma 4.5's stated universal lower comparison is false on its claimed domain. This invalidates that quantitative component of the analysis; it does not demonstrate failure of the observed training phenomenon.



### Proposed correction

For \(r=Ab_2\le1/2\) and \(u=a/A\in[\sqrt{0.55},\sqrt{2.1}]\), the ratio \(((1-r)/(1-ur))^2\) lies between \(0.631504254974859\) and \(3.295443406779994\). Thus replace the lower constant on this pre-threshold domain; the stronger upper bound \(1\) survives when \(a\le A\). The first discrete crossing may overshoot and needs separate treatment.

The specified local mathematical proposal is retained; no current author correction or adoption is established.



## Problem 2: The symmetric three-feature restriction is not the claimed Euclidean gradient-descent reduction

Assessment: supported; impact: minor



Source: Appendix C, PDF pp. 14–15 (symmetric reduction).



### Source claim (paraphrase)

Paraphrase: Appendix C, PDF pp. 14–15, adds an independent relevant feature \(x_3\) having the same variance as \(x_2\), sets the target to \(x_2+x_3\), and considers symmetric initialization \(b_2=b_3\). After substituting this equality, it identifies the resulting loss with the original model after replacing \(\lambda_2\) by \(2\lambda_2\), and asserts equivalent gradient-descent dynamics.

The equality of restricted loss values is correct. The equivalence of Euclidean gradient updates in the chosen common coordinate is not.



### Analysis

For a symmetric loss \(F(b_2,b_3)\), the tied loss \(g(b)=F(b,b)\) has derivative \(g'(b)=\partial_2F+\partial_3F=2\partial_2F\). The original symmetric Euclidean update uses \(b^+=b-\eta\partial_2F\), whereas unadjusted gradient descent on \(g\) uses twice that change. Equal restricted loss values therefore do not imply the claimed equal-learning-rate dynamics.



### Finding and scope

The asserted Euclidean-GD equivalence for the higher-dimensional extension fails; equality of restricted loss values and preservation of symmetry remain valid.



### Proposed correction

The tied-coordinate embedding induces metric \(\operatorname{diag}(1,1,2)\). Use the reduced update \(\theta^+=\theta-\eta\operatorname{diag}(1,1,1/2)\nabla F\), or an orthonormal sum coordinate with target amplitude \(\sqrt2\), before transferring the theorem.

The specified local mathematical proposal is retained; no current author correction or adoption is established.



## Problem 3: The sharpness proof substitutes a Gauss–Newton quadratic form for the full Hessian

Assessment: supported; impact: major



Source: Theorem 4.1; proof in Appendix E.2, PDF p. 22.



### Source claim (paraphrase)

Appendix E.2, PDF p. 22, in the proof of Theorem 4.1, identifies sharpness with the maximum over \(t_1^2+t_2^2+t_3^2\le1\) of

\[ \lambda_1(t_2a+t_1b_1)^2+ \lambda_2(t_3a+t_1b_2)^2. \]



### Analysis

Write the squared-residual model as \(L=\frac12\sum_i\lambda_i r_i^2\). Then \(\nabla^2L=\sum_i\lambda_i(\nabla r_i\nabla r_i^\top+r_i\nabla^2r_i)\). The displayed quadratic form keeps only the first term. For bilinear residuals, \(\nabla^2r_i\ne0\), so the omitted residual term generally persists away from zero loss. A Gauss–Newton form cannot establish the asserted full-Hessian sharpness bounds without controlling this term.

For the stated loss, the missing matrix has off-diagonal entries \(R_{12}=\lambda_1ab_1\) and \(R_{13}=\lambda_2(ab_2-1)\), with symmetric counterparts. At \[(\lambda_1,\lambda_2,a,b_1,b_2)=(100,0.01,0.5,0.005,0.6)\], the full-Hessian largest eigenvalue is approximately \(25.00999844\), whereas the printed Gauss–Newton form gives \(25.00250036\). The analytic residual difference already disproves the identity.



### Finding and scope

The cited proof does not establish its full-Hessian sharpness claim. This is a substantial gap in the central derivation; the statement is not upgraded to a counterexample to every possible corrected bound.



### Proposed correction

Retain the residual matrix and use \(\lambda_{\max}(H)\le\lambda_{\max}(G)+\rho\), where \[\rho=\sqrt{(\lambda_1ab_1)^2+[\lambda_2(ab_2-1)]^2}\]. Conditional on the preceding boundedness and zero-residual convergence results, \(\rho\to0\), restoring the final limiting-sharpness inference without asserting the incorrect identity along the trajectory.

The specified local mathematical proposal is retained; no current author correction or adoption is established.



## Problem 4: Decreasing bounds on gradient-flow-solution sharpness do not imply stepwise monotonicity

Assessment: supported; impact: minor



Source: Introduction, PDF p. 2; Section 5.1 and Theorem 5.2, PDF pp. 8–9.



### Source claim (paraphrase)

The discussion on PDF p. 2 and Section 5.1, PDF pp. 8–9, presents the result as a decrease of gradient-flow-solution (GFS) sharpness along gradient descent. The precise Theorem 5.2 encloses this sharpness between functions that decrease as \(b_2\) increases. The text also uses a near-monotonic description. This analysis does not assert that Theorem 5.2’s displayed enclosing bounds are false. It checks whether the stronger interpretation, monotonicity of the exact GFS sharpness at every GD step, follows. It does not.



### Analysis

The gradient-flow invariant is \(\gamma=a^2-b_1^2-b_2^2\). With the model's unit target normalization, zero loss has \(b_1=0\) and \(ab_2=1\), so \(q=a_\infty^2=(\gamma+\sqrt{\gamma^2+4})/2\) determines the limiting state used for GFS sharpness. Decreasing upper and lower envelopes do not imply a decrease of the exact quantity at every discrete gradient-descent step. The near-monotone description and displayed envelopes can remain valid despite a small local increase.

For \(\lambda_1=100\), \(\lambda_2=0.01\), \(\eta=0.1\), and admissible \(\theta_0=(1/3,1/1500,1)\), two projected-GD updates leave projection inactive. The exact invariant difference is \[\gamma_2-\gamma_1=\frac{4884795542280911349753184700897}{12611344042968750000000000000000000000}>0.\] Since \(q\) increases with \(\gamma\) and the \(\lambda_1q\) branch dominates, exact GFS sharpness increases from approximately \(64.98729109\) to \(64.98730259\). This is compatible with decreasing envelopes and near-monotone wording.



### Finding and scope

The stronger stepwise-monotonic interpretation is not implied by the theorem. Its displayed decreasing envelopes and the paper's near-monotone qualification are not refuted.



### Proposed correction

Describe decreasing envelopes or a near-monotone trend rather than strict all-step monotonicity of exact GFS sharpness.

The specified local mathematical proposal is retained; no current author correction or adoption is established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
