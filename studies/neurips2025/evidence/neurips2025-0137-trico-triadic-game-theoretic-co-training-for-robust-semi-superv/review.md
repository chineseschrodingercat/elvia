# TRiCo: Triadic Game-Theoretic Co-Training for Robust Semi-Supervised Learning



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The generic equilibrium proof is insufficient although the full zero-weight game has a degenerate equilibrium. Released teacher, pseudo-label and MI-gradient paths differ from the objectives, and a launcher uses official test labels for updates.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: Compactness and continuity do not prove the stated pure-strategy equilibrium

Assessment: supported; impact: minor



Source: Section 2.5, Assumptions 1–2 and Theorem 1, Eq. (8), PDF p. 5; Appendix A, PDF pp. 13–14.



### Source claim (paraphrase)

Paraphrase: Assumption \(1\) and Assumption \(2\) in Section 2.5, p. 5, require a compact finite-dimensional joint strategy space and continuity in each player’s own strategy. Theorem 1, Eq. (8), concludes that a deterministic strategy tuple exists satisfying all unilateral best-response inequalities. Appendix A, pp. 13–14, strengthens the discussion to joint continuity and invokes Glicksberg as if compactness plus continuity guaranteed a pure-strategy Nash equilibrium. The same appendix then presents zero-gradient conditions for teacher and students in Eqs. (27), (\(28\)), and (\(32\)), pp. 14–15.

The student minimizes \(R_S=\lambda_u L_{\rm unsup}+\lambda_{\rm adv}L_{\rm adv}\); the generator maximizes expected entropy; the teacher’s simultaneous-game payoff is validation accuracy of the fixed students. Appendix A uses teacher constraints \(0\leq\tau,\lambda_u,\lambda_{\rm adv}\leq1\), \(\lambda_u+\lambda_{\rm adv}\leq1\), a bounded student parameter ball, and an \(\ell_\infty\) perturbation ball.



### Analysis

Compactness and continuity alone do not imply a pure-strategy equilibrium. For example, on \(x,y\in[-1,1]\), let player one maximize \((x-y)^2\) and player two minimize it. The second player's best response is \(y=x\), where the first can always improve by changing \(x\); no pure equilibrium exists. This disproves the generic inference, not the paper's full game. Its allowed zero loss weights yield a separate degenerate equilibrium with uniform students, so asserting nonexistence for that complete domain would be wrong.



### Finding and scope

The general compact-continuous-game proof is insufficient, but the paper's full zero-weight domain permits a degenerate equilibrium. This does not establish a false existence conclusion for that full game, so Minor is appropriate.



### Proposed correction

Use a mixed-strategy statement for the generic compact continuous game, or supply a proof using the actual payoff structure. Preserve the direct zero-weight equilibrium as bare existence; replace boundary zero-gradient assertions with constrained optimality conditions and treat convergence separately.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 2: The public teacher update scales a training gradient instead of differentiating validation performance

Assessment: supported; impact: minor



Source: Section 2.3, Eqs. (5)–(7), PDF p. 4; Algorithm 1, line 16, PDF p. 5; Appendix B, PDF pp. 15–16.



### Source claim (paraphrase)

Paraphrase: Section 2.3, p. 4, Eqs. (5)–(7), and Algorithm 1, p. 5, line 16, update teacher parameters according to the validation effect of the student update. Appendix B, pp. 15–16, describes a one-step unroll and validation differentiation through the inner gradient, while also using a first-order/Reptile description. Section 3, p. 6, says the initial threshold and weights are \((0.05,0.5,0.5)\) and are adaptively learned.



### Analysis

Let the inner loss be \(\lambda(w-1)^2/2\), \(\lambda=\operatorname{sigmoid}(\phi)\), start \(w=0\), and use step \(\eta=0.1\). The one-step student is \(w'=0.1\lambda\). For validation loss \((w'-1)^2/2\), differentiation at \(\phi=0\) gives \(-0.02375\). Scaling a direct training derivative does not compute that mixed derivative, and a Boolean threshold supplies no ordinary gradient. This distinguishes the released heuristic from the stated unrolled validation objective.

The current helper multiplies the direct training derivative \(0.125\) by detached validation loss \(0.45125\), giving \(0.05640625>0\), opposite to the one-step validation derivative \(-0.02375\). The threshold enters only a Boolean comparison and receives no ordinary derivative.



### Finding and scope

The current scalar-rescaled training gradient can oppose the specified validation meta-gradient and cannot adapt the hard threshold by ordinary differentiation; benchmark exposure is unresolved.



### Proposed correction

Use an explicitly differentiable inner update when computing the outer validation derivative, or describe and evaluate the implemented heuristic as a different update. No restored benchmark performance is claimed.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 3: The public cross-view targets differ from the stated ensemble pseudo-labels

Assessment: supported; impact: minor



Source: Eqs. (1)–(2), PDF p. 3; Algorithm 1, lines 6–8, PDF p. 5.



### Source claim (paraphrase)

Paraphrase: Eq. (1), p. 3, defines MI from the ensemble predictive mean. The text accepts samples when \(I>\tau\), and the definition following Eq. (2) uses \(\hat y^{(i)}=\arg\max_y\bar p^{(i)}(y)\). Each student’s accepted pseudo-label is sent to the other student. Algorithm 1, p. 5, lines 6–8 repeats MI selection and cross-view supervision.



### Analysis

Dropout predictions \[(0.9,0.1),(0.1,0.9),(0.1,0.9)\] have ensemble argmax class \(1\), while the first draw selects class \(0\). A first-draw target is therefore not the stated ensemble target. Sender-based acceptance and an intersection of both students' acceptance masks are also distinct policies; the source must identify which it implements.



### Finding and scope

Current first-draw targets disagree with the explicitly defined ensemble, and acceptance-mask provenance is a separate policy choice; actual benchmark target errors are not measured.



### Proposed correction

Compute the mean predictive probability vector before selecting its label, and specify whether acceptance uses the sending student or both students. Reversing an uncertainty inequality alone is not established as an accuracy repair.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 4: Detaching MI removes its entire contribution to the generator gradient

Assessment: supported; impact: minor



Source: Section 2.2, Eq. (3), PDF p. 4; Algorithm 1, line 9, PDF p. 5.



### Source claim (paraphrase)

Section 2.2, Eq. (3), PDF p. 4, and the generator docstring use entropy plus a weighted mutual-information term. Algorithm 1, line 9, instead shows entropy alone, which is retained as counterevidence. Released methods/trico/generator.py, lines 11–17, differentiates its perturbed input, but utils.py, line 15, detaches the MI value, so that path has \(\nabla_x I=0\).



### Analysis

Detaching the computed mutual information makes its gradient with respect to generator parameters zero. It may remain a reported scalar or selection statistic, but cannot contribute the claimed differentiable MI pressure to that generator objective through the detached path.

With binary dropout logits \((x,0)\) and \((-x,0)\), let \(h(x)\) be their single-draw entropy. Their mean is uniform and \(I=\log2-h\). At \(x=1\), the intended \(h+2I\) derivative is \(+0.1966119332\), but detaching \(I\) leaves derivative \(-0.1966119332\). Sign perturbations of size \(0.1\) therefore go to \(1.1\) and \(0.9\), respectively.



### Finding and scope

The current detach removes the entire MI gradient and can reverse the stated joint-objective perturbation, while preserving the entropy-only variant and perturbation bound.



### Proposed correction

Provide differentiable MI for the generator while detaching a separate selection statistic, or explicitly adopt and evaluate the entropy-only algorithmic variant.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 5: The public launcher feeds the official test split into teacher updates

Assessment: supported; impact: minor



Source: Section 3, PDF p. 6 (validation/testing protocol); released launcher.



### Source claim (paraphrase)

Paraphrase: Section 3, p. 6, describes a fixed validation subset consisting of \(10\%\) of labeled training data for teacher feedback, with the official test set used for testing. This separation matters even if the teacher update is the heuristic identified in Problem 2, because the feedback still changes parameters used in later student learning.



### Analysis

Passing the official test split as validation data into the teacher's update objective uses held-out labels for training. In this launcher path the resulting score is not independent final testing. It does not establish that every historical paper run used the public launcher unchanged.



### Finding and scope

The actual launcher routes official test labels into adaptive teacher feedback; unchanged private experiment provenance and numerical score effects remain unknown.



### Proposed correction

Construct an explicit stratified validation subset from the available labeled training examples before building the loaders. Keep its labels out of inner supervised training, preserve the declared label budget, and pass only this validation loader to teacher updates. Keep the official test loader solely in evaluation. Save split indices and seeds so disjointness and label counts can be checked independently. Runs produced by the defective path need retraining and fresh evaluation; reports from an independently correct private path would instead require provenance showing that separation. No numerical adjustment to existing accuracies can repair an adaptive test-label dependency.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 6: The MI inequality needs a reliability-versus-uncertainty interpretation

Assessment: not_issue; impact: no_issue_found



Source: Eq. (1) and pseudo-acceptance discussion, PDF p. 3.



### Source claim (paraphrase)

The source uses a dropout mutual-information threshold in selecting pseudo-labels.



### Analysis

High epistemic disagreement does not itself guarantee a reliable label. It can be an intentional uncertainty curriculum, but that is a different rationale from confidence filtering; reversing the inequality alone has not been validated as an accuracy repair.



### Finding and scope

Scope clarification preserving uncertainty-based selection as a possible intentional policy.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
