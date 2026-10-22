# Semantic and Visual Crop-Guided Diffusion Models for Heterogeneous Tissue Synthesis in Histopathology



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The reported TCGA comparison supports mixed, modest FD changes and a recall tradeoff rather than a two-to-threefold gain. The absolute FLD threshold also does not establish patient privacy; no actual privacy leak is demonstrated.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: TCGA tables do not support the headline magnitude or uniform improvement

Assessment: supported; impact: minor



Source: Abstract, PDF p.1; Table 1, PDF p.8; supplementary Section 2.3 and Table S2, PDF pp.23–24



### Source claim (paraphrase)

The text describes a two-to-threefold FD improvement including TCGA and broadly superior quality under crop conditioning.



### Analysis

For the eight shared TCGA encoders, only five FD values decrease and the baseline/new ratios lie between \(0.8268824771\) and \(1.1109190807\). PathDino changes \(4306.7\to3876.7\), a factor \(1.110919\); DINOv2 changes \(117.5\to142.1\), a \(20.94\%\) increase. Any nonnegative consistently weighted ratio of sums is a convex combination of those ratios and cannot reach \(2\). All eleven supplementary recalls and F1 scores decline; for example Lunit recall changes \(0.017\to0.010\), RN50-BT \(0.212\to0.149\), and UNI \(0.016\to0.014\). PANDA improves across the main encoders, and rounding-compatible F1 values are not arithmetic errors.



### Finding and scope

TCGA supports a metric tradeoff and encoder-dependent changes. The displayed measurements, positive PANDA evidence and downstream segmentation results are not refuted.



### Proposed correction

Qualify the headline by dataset: TCGA’s displayed FD improvement factor is at most \(1.111\), with lower recall/F1 across all eleven encoders.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: Absolute FLD does not calibrate patient-identification risk

Assessment: supported; impact: minor



Source: Supplementary Section 2.1 and Table S1, PDF pp.22–23; cited FLD paper, Eqs.(3),(5)



### Source claim (paraphrase)

Values below \(10\) are interpreted as effective protection against patient reconstruction or identification.



### Analysis

FLD is an adjusted feature-space negative log-likelihood, not an identification probability. Let records be \((z,s)\), with confidential identifier \(s\), and evaluated feature map \(\phi(z,s)=z\). Two generators can return the same four feature vectors \((0,0),(1,0),(0,1),(1,1)\), while one repeats confidential identifiers and the other supplies unrelated identifiers. All fitted feature-metric inputs and FLD values are equal, yet direct identifier matching succeeds on \(4/4\) versus \(0/4\). This is a mathematical information-loss witness, not an asserted pathology-encoder collision.



### Finding and scope

An absolute feature score alone cannot supply the claimed general privacy conclusion. The model’s actual leakage risk was not measured.



### Proposed correction

Relabel FLD as a sample-quality/generalization diagnostic and remove the universal privacy-threshold interpretation; no numerical privacy bound is established.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
