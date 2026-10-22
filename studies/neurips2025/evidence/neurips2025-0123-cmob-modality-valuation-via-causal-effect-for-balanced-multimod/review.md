# CMoB: Modality Valuation via Causal Effect for Balanced Multimodal Learning



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Pointwise confidence monotonicity is false even for calibrated Bayes prediction. Released scoring changes the declared gate/scale and its checkpoint loop selects on test accuracy.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: Adding a predictive modality need not increase confidence for each sample

Assessment: supported; impact: major



Source: Section 3.2, Proposition 1 and Eq. (1), PDF p. 5.



### Source claim (paraphrase)

Paraphrase of Proposition 1: For a sample with modality set \(M\), any nested subsets \(B\subseteq C\subseteq M\), and any multimodal classifier, the confidence on \(x_B\) is strictly less than the confidence on \(x_C\), which is no greater than the confidence on \(x_M\) (Section 3.2, PDF page 5). The surrounding discussion assumes that all modalities are predictive and motivates a positive relationship between confidence and additional modalities for a reliable classifier. Equation (1)’s benefit uses a related confidence comparison.

The problem is the pointwise guarantee. Conditional entropy is an expectation over observations, and its monotonicity does not imply monotonic confidence on every observed sample. The counterexample uses a proper inclusion \(B\subset C=M\), so it does not depend on the strict inequality’s trivial failure when two subsets are equal.



### Analysis

Take a balanced binary label and two conditionally independent predictive signals with accuracies \(0.9\) and \(0.8\). Observing a positive first signal gives posterior \(0.9\) and odds \(9\). On the positive-probability event that the second signal is negative, its likelihood ratio is \(1/4\), so the posterior becomes \(9/(9+4)=9/13<0.9\). This is the exact calibrated Bayes classifier. Expected conditional entropy can improve while confidence decreases on an individual observation.



### Finding and scope

The stated universal pointwise confidence monotonicity is false even for informative modalities and calibrated prediction. This undermines that theoretical justification; it does not by itself measure the training strategy's utility.



### Proposed correction

Replace the pointwise proposition by the average information inequality \(H(Y\mid X_C)\le H(Y\mid X_B)\), or weak average Bayes-accuracy monotonicity under its posterior assumptions. Neither result implies a per-sample confidence gate.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 2: Released benefit scoring omits the confidence gate and changes the operational contribution scale

Assessment: supported; impact: minor



Source: Section 3.2, Eq. (1), PDF p. 5; Section 3.3, Eq. (4), PDF p. 6; Eq. (5), PDF p. 7.



### Source claim (paraphrase)

Eq. (1), Section 3.2, PDF p. 5, gates benefit on both correct prediction and the specified confidence comparison. Eq. (4), Section 3.3, PDF p. 6, defines contribution \(\Phi_m\), while Eq. (5), PDF p. 7, applies the weak-modality threshold \(\Phi_m\le1\). The released scoring omits that confidence gate and uses a rescaled contribution.



### Analysis

Omitting the confidence comparison changes eligibility for the benefit. Independently, a contribution rescaling \(c_m=\Phi_m/2\) requires changing the weak-modality threshold \(\Phi_m\le1\) to \(c_m\le1/2\). Retaining threshold one after rescaling changes decisions for \(1<\Phi_m\le2\). Neither operation is an equivalent rewriting of the stated gate and contribution units.

A shared linear-fusion realization has correct-class probabilities \(0.9\) for audio alone, \(0.8\) for visual alone and \(0.7\) for both. With log-odds \(L_A,L_V,L_F\), choose shared bias \(b=L_A+L_V-L_F\) and contributions \(L_A-b,L_V-b\). Both proper confidence comparisons fail, yet the current correctness-only scorer gives full benefit \(2\). When full confidence instead equals \(0.95\), the gate passes and paper contributions are \(2\), versus code scores \(1\); the loader adds a weak-modality copy at \(1\) but none at \(2\).



### Finding and scope

An architecture-realizable probability fixture changes the gate and augmentation branch; the historical table-producing implementation remains unidentified.



### Proposed correction

A manuscript-faithful implementation needs an explicit policy for the comparison subset in Eq. (1), must compute the stated confidence gate, and must use the Eq. (4) contribution in units consistent with all subsequent transformations and thresholds. A normalized contribution \(c_m=\Phi_m/2\) can also be used, but the paper’s weak threshold \(\Phi_m\le1\) then becomes \(c_m\le1/2\). Every dependent branch, masking rule, and transformation must be expressed in the same units; changing a single displayed constant does not prove the whole strategy coherent.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 3: The released loop selects saved checkpoints using test-set accuracy

Assessment: supported; impact: minor



Source: Released CMoB.py, dataset construction at lines 273–291 and checkpoint selection at lines 356–387.



### Source claim (paraphrase)

This finding concerns the released procedure and its ability to supply an independent final evaluation. CMoB.py, lines 273–275, creates a training dataset, a second dataset named train_val_dataset using training mode, and a dataset using test mode. Lines 291 onward wrap the latter in test_dataloader. At line 356, each epoch calls the evaluation function with that test loader. Lines 358–359 compare the returned accuracy with best_acc; lines 361–387 construct and save a checkpoint when it improves.

The data route is not inferred from variable names alone. datasets/dataloader.py, lines 29–40, maps training mode to train.csv, validation mode to val.csv, and the remaining test route to test.csv. A separate validation branch exists. The function name valid does not change the fact that the actual argument is test_dataloader.



### Analysis

Using test-loader accuracy to decide when to save a checkpoint makes that set part of model selection. The selected score is consequently not an independent final-test assessment for this loop. The public snapshot does not prove that the paper's historical tables used exactly this selection path.

For two independent fixed models with population accuracy \(1/2\), selecting the larger correctness bit on one test example reports expected accuracy \(3/4\). Selection on independent validation instead leaves expected test accuracy \(1/2\). This establishes the mechanism, not its magnitude in CMoB.



### Finding and scope

Current source routes test.csv into checkpoint selection; the amount of selection optimism and historical table provenance are unknown.



### Proposed correction

Select checkpoints using an independent validation set, then evaluate the selected model once on an untouched test set. No new training or corrected test accuracy is supplied.

A local correction or qualification is proposed where specified; author adoption is not established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
