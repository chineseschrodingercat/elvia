# EPA: Boosting Event-based Video Frame Interpolation with Perceptually Aligned Learning



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The supported issues concern a scale-dependent robustness diagnostic, local differences between loss equations and released code, state/metric interfaces, and reporting. Their consequences for the paper's central interpolation results have not been established, so the strict assessment is Minor. Appropriate DISTS input handling, disclosed stochastic variation and the absence of demonstrated target-to-prediction leakage remain counterevidence.



## Scope

Claim-focused reading of the identified paper and author-released materials. The arguments below distinguish mathematical contradictions, version-specific implementation defects and unresolved empirical consequences. No author code was executed in this revision.



## Problem 1: Cross-space raw distances do not demonstrate robustness

Assessment: supported; impact: minor



Source: Main PDF p.9, Fig 8 and discussion



### Source claim (paraphrase)

Figure 8 interprets smaller raw distances in different feature spaces as greater robustness.



### Analysis

The image-space distance \(47.70\) and feature-space distances \(27.01,12.16,7.71\) have different dimensions and scales. Multiplying any representation by \(0.001\) reduces its raw perturbation distance by a factor of \(1000\), without improving relative error or semantic discrimination. Therefore these raw cross-space distances alone cannot establish robustness.



### Finding and scope

This limits the robustness diagnostic; it does not refute the usefulness of the learned features or the measured interpolation results.



### Proposed correction

Define perturbations and compare dimensionless sensitivity with semantic discrimination/downstream reconstruction on matched examples.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: Signal-to-noise ratio is interpreted in the wrong direction

Assessment: supported; impact: minor



Source: Supplement PDF p.4, Table 4 and discussion



### Source claim (paraphrase)

The supplement treats its lower SNR values as evidence of greater robustness.



### Analysis

Supplement treats lower SNR as greater robustness but provides no formula or units. Standard \(\mathrm{SNR}=10\log_{10}(P_{\rm signal}/P_{\rm noise})\): noise amplitude \(0.1\) gives \(20\) dB; amplitude \(0.5\) gives \(6.0206\) dB; higher is cleaner.



### Finding and scope

Unknown definition prevents determining which repair matches original calculations; do not speculatively invert table values.



### Proposed correction

Publish exact statistic; rename noise-to-signal/error quantities or correct standard-SNR direction and use comparable representations.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: The implemented loss differs from Eq. 3

Assessment: supported; impact: minor



Source: Main PDF p.5, Eq 3 code/model/ourModel.py:116-118



### Source claim (paraphrase)

The released second-stage training objective should match the coefficients in Eq. (3).



### Analysis

Paper stage-two weights: Laplacian weight \(0.2\) and branch weights \(0.1\). Release uses \(1.0,0.5,0.1\) respectively. Feature alignment uses MSE; generic manuscript \(L^2\) wording does not specify reduction across scales.



### Finding and scope

Historical table-generating objective unknown. Repair requires retraining to assess empirical consequences.



### Proposed correction

Use \(L_{\rm LPIPS}+0.2L_{\rm Lap}+\sum_s(L_{{\rm MSE},s}^{\rm main}+0.1L_{{\rm MSE},s}^{(0)}+0.1L_{{\rm MSE},s}^{(1)})\), or amend paper/configs to actual asymmetric objective.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: Frozen parameters still allow the pretrained state to change

Assessment: supported; impact: minor



Source: code/model/ourNet.py:11-14 code/model/ourModel.py:53-54,109 code/util/utils_func.py:346-369



### Source claim (paraphrase)

The pretrained feature extractor is intended to remain fixed during subsequent training.



### Analysis

Freezing parameters and initial eval do not survive recursive parent.train() for BatchNorm buffers. Actual ResNet feature wrapper with frozen parameters changes running mean by \(0.0679887\) after synthetic forward.



### Finding and scope

No pretrained weights used for this test; no measured effect on published output or accuracy.



### Proposed correction

Restore fixed generator/backbone eval after parent.train(), or override train. Preserve gradients through decoder inputs rather than applying blanket no_grad.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 5: Evaluation has incompatible return values and signatures

Assessment: supported; impact: minor



Source: code/predict/pred_utils.py:110-124,164 code/predict/vimeo90k.py:67 code/predict/hsergb.py:88 code/predict/gopro.py:52,73-74



### Source claim (paraphrase)

Dataset evaluation callers and prediction helpers must agree on returned values and metric arguments.



### Analysis

Helper returns one tensor of shape \((1,24,4,5)\), while callers unpack two outputs; actual unpack raises ValueError. GOPRO metric-logger call omits required dists argument, raising TypeError.



### Finding and scope

Fixes proven runtime failures, not model accuracy or historical experiment provenance.



### Proposed correction

Use consistent named event outputs and complete metric dictionaries; smoke-test each dataset adapter.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 6: LPIPS inputs violate the metric contract

Assessment: supported; impact: minor



Source: code/predict/pred_utils.py:46-47 LPIPS calls in code/predict/ code/predict/bsergb.py:31,87 code/model/ourModel.py:116



### Source claim (paraphrase)

LPIPS evaluation should follow the metric's input, normalization and device conventions.



### Analysis

Several adapters pass uint8 NumPy HWC arrays directly to LPIPS; BS-ERGB/train tensor paths omit \([0,1]\) normalization. CPU LPIPS/CUDA tensor path also conflicts. SSIM uses each image observed range rather than fixed nominal 255.



### Finding and scope

No pretrained LPIPS metric reproduction or re-estimated scores. Rank-change direction unknown; SSIM example effect tiny. Examined DISTS tensor convention is appropriate.



### Proposed correction

Use consistent RGB floating-point NCHW tensors in \([0,1]\), enable the metric's intended normalization and align devices. Reevaluate existing predictions under one declared metric convention.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 7: The published entrypoints need substantial reconstruction

Assessment: supported; impact: minor



Source: code/interpolation.py code/main.py code/train.py README and checkpoint loading



### Source claim (paraphrase)

The published training/inference entry points are intended to support the documented reconstruction workflow.



### Analysis

The inference parser omits resume fields consumed by model setup. Training uses an unset dataset and a placeholder first-stage checkpoint, with hardcoded path/device assumptions. The first-stage/filtering/split recipe is incomplete. The author release does expose a bsergb.pth asset, so lack of a runnable entry point must not be described as absence of any checkpoint.



### Finding and scope

Available checkpoint was not downloaded/executed. Incomplete public entrypoints do not establish absence of private scripts.



### Proposed correction

Separate training/inference configs; publish working adapters, paths, first-stage recipe, filtered sample IDs, configs and checkpoint formats/checksums.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 8: Sampling heat is ignored, while stochastic behavior is acknowledged

Assessment: supported; impact: minor



Source: code/model/ourModel.py:95-99 code/model/ourNet.py:19 Flow latent sampling



### Source claim (paraphrase)

The inference heat argument is intended to control the latent sampling scale.



### Analysis

inference(heat=...) calls child without heat; requested \(0\) reaches child as default \(0.3\). GT feature branch is computed but static dataflow shows it is returned as supervision, not fed to predicted branches.



### Finding and scope

Stochastic color variation is acknowledged, not itself an error. With fixed evaluation normalization, no test-target prediction leakage is demonstrated.



### Proposed correction

Forward heat and declare seeded/deterministic sampling; remove unused target-feature computation from inference.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 9: Training settings do not agree across sources

Assessment: supported; impact: minor



Source: Main PDF p.6 Supplement PDF p.2 code/train.py:15-21,32,51



### Source claim (paraphrase)

The main text, supplement and training source should identify the actual batch and learning-rate settings.



### Analysis

Main paper batch \(40\); supplement stages \(28/32\); release 32. Effective code learning-rate endpoints \(3.75\times10^{-5}\) and \(3.75\times10^{-7}\) differ from stated \(10^{-4}\) and \(10^{-6}\); per-table training/fine-tuning/filtering manifests incomplete.



### Finding and scope

Cannot select historical truth among conflicting sources. TLXNet training-scope exception is disclosed.



### Proposed correction

Publish exact per-result run datasets, sample IDs, stage checkpoints, batches, steps, LR formula, seeds and disclosed baseline exceptions.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 10: Significance and human preference exceed the evidence shown

Assessment: supported; impact: minor



Source: Main/supplement quantitative tables Main PDF p.15, checklist item 7 Main PDF p.18, human-subject item



### Source claim (paraphrase)

The paper's significance and visual-preference statements require evidence for the statistic being claimed.



### Analysis

Tables show point estimates without intervals, seed variation or paired sequence results, while significance checklist is affirmative. No human-preference study; qualitative/proxy metrics cannot establish measured participant preference.



### Finding and scope

Gains may be useful. No universal requirement that every interpolation study include human participants; no reported score is replaced.



### Proposed correction

Release sequence-level scores and paired uncertainty; distinguish seed reliability and describe visual quality as proxy/qualitative unless measured in a study.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 11: Narrow the strongest claims to match the disclosed method and tables

Assessment: supported; impact: minor



Source: Abstract/introduction and main PDF p.5, Eqs 2-3 Supplement EventAid/degradation/efficiency tables code/predict/bsergb.py



### Source claim (paraphrase)

The strongest decoupling, robustness, metric and efficiency descriptions should match the disclosed formulation and tables.



### Analysis

Image LPIPS/Laplacian supervision remains in both-stage formulation; strongest decoupling wording needs qualification. EPA loses EventAid DISTS at \(7/15\) skips to TLXNet, although LPIPS/FloLPIPS favorable; pen_03 and runtime/trainable-parameter scope are limited.



### Finding and scope

Disclosed scene example is not evidence of deliberate cherry-picking. Hardware/training-time information is provided; no new efficiency measurement.



### Proposed correction

Describe hybrid supervision and metric-specific wins; scope scene robustness and distinguish trainable, total deployment parameters and end-to-end runtime.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 12: Repair the architecture formula rather than infer a broken implementation

Assessment: supported; impact: minor



Source: Main PDF p.5, Eq 1 code/model/blocks.py, deformable alignment/fusion



### Source claim (paraphrase)

Eq. (1) should define the feature input, deformable operation and channel fusion.



### Analysis

Displayed deformable-convolution formula omits sampled feature argument and channel projection after concatenation. Source supplies original features, offsets/mask, and projection; operation is not proven broken.



### Finding and scope

Manuscript omission, not evidence that implementation lacks its actual feature input.



### Proposed correction

Show offset/mask estimation, DeformConv(feature; offset, mask), \(2C\)-to-\(C\) fusion projection and residual SE operation with dimensions.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 13: LPIPS is cited to the wrong entry and two related-work references do not concern VFI.

Assessment: supported; impact: minor



Source: Main PDF p.5, LPIPS citation Main PDF p.3, related work References 21-22,49-50



### Source claim (paraphrase)

The LPIPS and related-work citations should identify the corresponding methods.



### Analysis

LPIPS cites \(49\) instead of relevant \(50\); listed VFI references \(13\) and \(43\) concern other tasks; \(21\)/\(22\) duplicate CBMNet. Normalized flow wording should be normalizing flow.



### Finding and scope

Editorial issues do not independently invalidate experiments; not every external bibliographic field was audited.



### Proposed correction

Repair indices, remove duplicate and correct terminology.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.
