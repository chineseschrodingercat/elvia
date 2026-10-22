# BioCLIP 2: Emergent Properties from Scaling Hierarchical Contrastive Learning



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The AwA2 metric uses binary values as attribute indices and averages only two of \(85\) columns. Classifier dropout remains active, and the approximate theoretical proxy needs additional confidence/error control.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The AwA2 metric selects two attribute columns instead of averaging all \(85\)

Assessment: supported; impact: minor



Source: Table 2, PDF p. 6; Appendix H, PDF p. 29.



### Source claim (paraphrase)

Appendix H, PDF p. 29, defines mean F1 across \(85\) binary AwA2 attributes; Table 2, PDF p. 6, reports the corresponding evaluation. The current author repository (commit 49e1cf50e0341ed41d13353d23cbf963bdb1293a), as well as v1.0.0, src/evaluation/awa2.py, lines 85–87, instead supplies column indices \([0,1]\) to the multilabel metric.



### Analysis

For an \(N\times85\) binary indicator target, the labels option \([0,1]\) selects attribute columns zero and one, rather than the two allowable values in every column. Let those two columns be predicted perfectly and invert the remaining \(83\), with both outcomes present in every column. The released mean is \(1\), while the intended macro-F1 is \(2/85\approx0.0235294\). This proves the metric discrepancy without identifying the historical predictions used in Table 2.



### Finding and scope

The released evaluator averages two attribute columns rather than the stated full set. No corrected paper score or reversal of the scaling result is established.



### Proposed correction

Evaluate all attribute columns, for example by using the metric's full multilabel default rather than selecting only two indices. Historical predictions and the exact table-producing evaluator are needed for a corrected reported score.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 2: AwA2 and FishNet evaluate the classifier with training-mode dropout active

Assessment: supported; impact: minor



Source: Section 5.1, PDF p. 6; Appendix H, PDF pp. 28–29; released AwA2/FishNet classifiers.



### Source claim (paraphrase)

Section 5.1, PDF p. 6, and Appendix H, pp. 28–29, evaluate frozen visual features with task classifiers. The AwA2 and FishNet scripts construct a head with a hidden width of \(512\), a dropout probability of \(0.5\), and an output layer for the task labels.

The v1.0.0 classifier construction is at lines 51–57 of each script, and evaluate() is at lines 60 onward. The current head 49e1cf50e0341ed41d13353d23cbf963bdb1293a retains this design and the same active evaluate call path. Inside evaluate(), the forward call is wrapped in torch.no_grad(), but the fitted classifier is never switched to evaluation mode anywhere in the corresponding script.



### Analysis

A newly created classifier stays in training mode until eval() is called; no_grad disables gradient recording but does not stop dropout. Putting the separate vision backbone into eval mode does not change the head. A single stochastic prediction is therefore evaluated without the declared Monte Carlo averaging protocol.



### Finding and scope

This is a supported local finding within the stated source/formulation scope. Its effect on the paper's aggregate experimental results remains unmeasured.



## Problem 3: The theoretical quadratic proxy needs an additional confidence assumption and a controlled approximation

Assessment: supported; impact: minor



Source: Theorem 5.1, PDF p. 8; Appendix C, PDF pp. 22–23.



### Source claim (paraphrase)

Theorem 5.1, PDF p. 8, assumes nearly orthogonal species prototypes and presents a quadratic expression governing the residual \(\delta=z-\mu_s\). Appendix C, pp. 22–23, expands (R2), then additionally supposes that the true-species softmax weight is close to one, replaces the weighted prototype mean by \(\mu_s\), and discards the linear term.

The manuscript explicitly describes this latter step as an approximation. The issue is therefore not that an approximate expression was asserted to be an exact equality. The concerns are the mismatch between the main theorem’s hypotheses and the extra confidence assumption, and the lack of an error regime supporting the approximation.



### Analysis

Let \(m=\sum_k w_k\mu_k\) be the softmax-weighted prototype mean at the expansion point. The Taylor linear term is \((m-\mu_s)^\top\delta/\tau\), and the quadratic covariance is \(\sum_k w_k\mu_k\mu_k^\top-mm^\top\). Nearly orthogonal prototypes alone do not make the true-species weight close to one. Replacing \(mm^\top\) by \(\mu_s\mu_s^\top\) can lose positive semidefiniteness. Since the appendix explicitly calls this an approximation, the finding is missing confidence/error control, not an assertion that the authors claimed an exact identity.



### Finding and scope

This is a supported local finding within the stated source/formulation scope. Its effect on the paper's aggregate experimental results remains unmeasured.



### Proposed correction

Retain the complete Taylor terms or state an explicit high-confidence approximation regime and its error bound. This does not revalidate full-model performance.

A local correction or qualification is proposed where specified; author adoption is not established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
