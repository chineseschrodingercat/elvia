# Lie Detector: Unified Backdoor Detection via Cross-Examination Framework



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The classical CCA invariance derivation and scaling comparison are false. Separate endpoint metrics have absent-class denominators, and stated access/reference requirements need reconciliation with the actual algorithm. Detector performance under its required access is not refuted.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Classical CCA is invariant to invertible feature transformations

Assessment: supported; impact: major



Source: Appendix G.1â€“G.2, PDF pp.28â€“30; comparison Table Appendix 8



### Source claim (paraphrase)

The argument claims CCA correlations change under anisotropic diagonal scaling and uses that to justify a scaling advantage of CKA.



### Analysis

For invertible feature maps \(T,U\), every original projection pair \(Xa,Yb\) is retained by choosing \(a^\prime=T^{-1}a\), \(b^\prime=U^{-1}b\), since \((XT)a^\prime=Xa\), \((YU)b^\prime=Yb\). The inverse mapping preserves the full feasible correlation sets, including subsequent decorrelation constraints. Thus every defined classical canonical correlation is unchanged. Conversely, take centered rows \[A=((1,0),(-1,0),(0,1),(0,-1))^\top\] and \(B=A\operatorname{diag}(2,1)\). CCA is perfect on their shared full-rank column space, but linear CKA equals \(5/\sqrt{34}\approx0.857493\), versus \(1\) for A with itself.



### Finding and scope

The comparative proof is mathematically wrong. CKA retains orthogonal/isotropic invariance and may remain empirically suitable; stronger CCA invariance is not automatically desirable.



### Proposed correction

State classical CCAâ€™s invertible-feature invariance. SVCCA can lose general anisotropic invariance when truncation changes its retained subspace, rather than because CCA lacks scale invariance. Linear CKA equal to one requires proportional nonzero centered Gram matrices, not identical activations.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: All-clean/all-backdoored endpoints lack the stated metric denominators

Assessment: supported; impact: minor



Source: Appendix B.2, PDF p.24; Table Appendix 5 and client composition, PDF p.27



### Source claim (paraphrase)

DSR is backdoor sensitivity and FPR is clean-model false-positive rate, but the all-clean endpoint reports DSR \(100\%\) and all-backdoored endpoints report positive FPR.



### Analysis

Under those definitions, \(\mathrm{DSR}=\mathrm{TP}/(\mathrm{TP}+\mathrm{FN})\) has denominator zero when all four clients are clean; FPR has denominator zero when all four are backdoored. Twelve ordered pairings and repeated trials cannot create an absent class. Overall accuracy/specificity could equal \(100\%\) in an all-clean group, but are different quantities. Half-step sensitivity percentages among twenty models could arise from pair/run averaging, so that separate aggregation ambiguity is not declared fabrication.



### Finding and scope

The endpoint populations and stated denominators are inconsistent. An unstated external clean set or alternate prediction unit could explain values, but requires its protocol; corrected numerical entries cannot be recovered here.



### Proposed correction

Declare prediction units, repeated-context weighting and confusion counts; mark an absent-class rate unavailable, or identify the additional population that defines it.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: Restricted-access claims do not describe the specified procedure

Assessment: supported; impact: minor



Source: Main Algorithm 1 and Eqs.(5)â€“(10), PDF pp.5â€“7; Appendix F, PDF p.28; clean-reference statements



### Source claim (paraphrase)

The appendix says internals and label supervision are unnecessary, while the algorithm uses internal activation kernels, gradients/fine-tuning and supervised cross entropy.



### Analysis

The specified supervised loss needs \(y_i\), and the centered kernel \(H A_lA_l^\top H\) needs intermediate activations that arbitrary output predictions do not determine. Adam trigger optimization and subsequent fine-tuning require the corresponding differentiable/trainable access. Lack of access to the providerâ€™s original training process is compatible with those requirements; it is not output-only black-box access. The algorithm can omit a trusted clean reference while a particular experiment uses one, but the textâ€™s different assumptions need separate result scopes.



### Finding and scope

The broad access statements require qualification. No hidden label leakage, unfair pairing or detector failure under the actual required access is established.



### Proposed correction

Describe inspectable/differentiable suspect models, the supervised label requirement and any fine-tuning access. Separate reference-assisted experiments from experiments with only suspect models.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
