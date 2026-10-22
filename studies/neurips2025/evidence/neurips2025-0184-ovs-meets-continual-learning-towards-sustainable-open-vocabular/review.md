# OVS Meets Continual Learning: Towards Sustainable Open-Vocabulary Segmentation



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Three released/supplementary implementation discrepancies affect the EWC anchor and image/text interpolation state. Small valid inputs establish different regularization or decoder parameters, without establishing an effect on published benchmark rankings.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: The EWC reference precedes checkpoint loading

Assessment: supported; impact: minor



Source: Supplement B.3, supplement PDF p.2; fcclip/previous/ewc.py, lines 22,31â€“42; train_net.py, lines 459,474â€“476



### Source claim (paraphrase)

The constructor clones trainable parameters before the trainer loads previous-task weights. The ordinary reference dictionary is not restored by model state loading.



### Analysis

For constructor value \(0\), loaded previous value \(3\), precision \(F=2\) and coefficient \(1\), the code penalty at the loaded model is \(2(3-0)^2=18\), gradient \(12\). EWC centered at the previous model instead gives \(2(3-3)^2=0\), gradient \(0\). Setting precision later changes no reference clone. Unchanged parameters, zero precision and zero coefficient are valid exceptions. The disclosed use of new-task Fisher data is a separate adaptation, not an additional hidden bug.



### Finding and scope

The released EWC baseline can move away from the checkpoint it should preserve. A private historical fix or different run remains possible; no specific published score is attributed to this path.



### Proposed correction

Capture detached previous-task parameter clones after checkpoint restoration and before a new task. Mid-task resume must retain the original task-boundary anchor rather than recenter it. Persist anchor and precision explicitly.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: Changing datasets leaves the old text-domain gate cached

Assessment: supported; impact: minor



Source: Algorithm 1, main PDF p.5; fcclip_ensemble.py, set_metadata lines 80â€“87, calculate_text_distance lines 165â€“172; Trainer.test multi-dataset loop



### Source claim (paraphrase)

Metadata changes clear text features but leave text_prototype_distance, whose nonempty value suppresses recomputation.



### Analysis

Construct unit-vector training embeddings with domain-zero frequencies \(9e_1,1(-e_1),3e_2,3(-e_2)\), and domain one with coordinates swapped. Their Gaussian means are \((1/2,0),(0,1/2)\) and regularized covariances \(0.375001I\). Queries \(e_1,e_2\) therefore have opposite log-density gaps \(\pm1.3333297778\), giving gates \[(0.7913908857,0.2086091143)\] and its reversal. After the first metadata call, the second returns the cached first vector. With image gate \((0.5,0.5)\), a relevant incremental weight is \(0.5\) instead of \(0.7913908857\). Repeating each class vector over the declared templates preserves this valid normalized-feature construction.



### Finding and scope

The multi-dataset scripts expose a stale-state path. These synthetic embeddings prove possible parameter change, without claiming a real CLIP/class-name pair has these exact values or measuring benchmark impact.



### Proposed correction

Invalidate the text-domain distance whenever its metadata/features change, or key the cache by all relevant inputs.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: Text fusion is bypassed above three prototypes

Assessment: supported; impact: minor



Source: Algorithm 1, main PDF p.5; fcclip_ensemble.py, optimized_task_arithmetics lines 195â€“198



### Source claim (paraphrase)

The general estimator takes the elementwise image/text maximum, but the source does so only when the prototype count is at most \(3\).



### Analysis

With five prototypes, choose image probabilities \[(0.8,0.05,0.05,0.05,0.05)\] and text probabilities \[(0.05,0.8,0.05,0.05,0.05)\]. Both are positive normalized softmax outputs. The first incremental weight should be \(0.8\), but the branch uses \(0.05\). A scalar first task vector \(1\) and all other/base vectors zero give decoder coordinate \(0.05\) rather than \(0.8\). The post-maximum vector need not be normalized under the paperâ€™s own definition.



### Finding and scope

A general-input method/release discrepancy is established. Three-or-fewer prototypes or image-dominant components are countercontrols; historical scenario use and accuracy effects remain unknown.



### Proposed correction

Apply the declared fusion at every supported count or explicitly document the image-only switch and affected scenario settings. No improved segmentation result is claimed.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
