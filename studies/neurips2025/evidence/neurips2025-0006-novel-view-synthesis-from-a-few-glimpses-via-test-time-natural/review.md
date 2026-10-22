# Novel View Synthesis from A Few Glimpses via Test-Time Natural Video Completion



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The supported corrections concern backward-coordinate pseudocode, schedule/weight notation, scene-specific optimization wording and scale-dependent heuristics. They do not demonstrate failure of the central rendering results. The author implementation already handles the weight reversal; the quadratic minimizer and tabulated PSNR advantages remain valid. Baseline attribution, calibrated depth confidence and end-to-end uncertainty/cost remain unresolved.



## Scope

Claim-focused reading of the identified paper and author-released materials. The arguments below distinguish mathematical contradictions, version-specific implementation defects and unresolved empirical consequences. No author code was executed in this revision.



## Problem 1: Released uncertainty and fusion differ from the published algorithm

Assessment: needs_evidence; impact: needs_evidence



Source: main pp. 5-6, Eqs. (2), (4), (5); main p. 8 hyperparameters; supplement pp. 3, 5-6



### Source claim (paraphrase)

Main Eqs. (\(2\)), (\(4\)) and (\(5\)), with the supplement's stated schedule, specify squared consistency kernels and continuously weighted clean-latent fusion.



### Analysis

The printed uncertainty uses squared geometric and photometric errors, whereas the active author-released source uses a cubic photometric kernel and dataset-specific fusion/schedules. A scalar error therefore receives a different confidence even with identical inputs. This supports a specification/release discrepancy, not attribution of the published scores to that exact source revision.



### Finding and scope

The available material identifies a scope or evidence gap; it does not prove that the reported empirical effect is false.



### Proposed correction

Specify the actual confidence kernels, fusion and dataset schedules; published-score attribution remains unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: Frame-dependent backward weights must be reversed with their frames

Assessment: supported; impact: minor



Source: supplement p. 3, Algorithm 1



### Source claim (paraphrase)

Supplement Algorithm 1 reverses the latent and guidance sequence but reuses the same frame-dependent weights without an explicit backward-coordinate redefinition.



### Analysis

Supplement Algorithm 1 reverses the latent and guidance sequences before the backward pass, but retains the same frame-indexed \(\gamma_t\). The weights must follow their frames: \(\widetilde x'_0=(\widehat x'_0+R(\gamma_t)\odot R(g))/(1+R(\gamma_t))\), with elementwise division.

For \(\gamma=[9,0,0]\), \(g=[10,20,30]\) and zero denoised predictions, forward fusion gives \([9,0,0]\). The printed backward rule, realigned to forward order, gives \([0,0,27]\); the reversed-weight rule gives \([9,0,0]\). Blending with \(\beta=[1,0.5,0]\) therefore introduces a spurious final-frame value \(27\) under the literal pseudocode. Zero weights are permitted by Eq. (\(5\)).

The author release already reverses the weights: SVD_2pass_prob_uncertain.py, lines 681-687, flips guidance, masks, latent order and lambda_ts; its Post variant does likewise at lines 693-698. This is a printed-algorithm discrepancy, not evidence that the released generator uses misaligned weights.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Reverse frame-dependent weights together with frames, or explicitly redefine them in backward coordinates; the examined implementation already handles the reversal.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: Baseline provenance is insufficient to isolate the reported gain

Assessment: needs_evidence; impact: needs_evidence



Source: main Tables 1 and 3, pp. 8-10; supplement §§B.5 and C.4; repository README



### Source claim (paraphrase)

Tables 1 and \(3\) report different DL3DV baseline scores while the full-model score is the same. Their causal comparison requires consistent initialization, losses and budgets.



### Analysis

Table 1's DL3DV nine-view baseline PSNR is \(12.99\), whereas Table 3's baseline is \(16.59\), both against full-model \(19.19\). The implied gains are \(6.20\) and \(2.60\) dB. This is not automatically a contradiction: the latter baseline includes depth regularization, and the supplement describes stereo initialization. Different losses, initialization, subsets or budgets need a row-level mapping. The paper already specifies every-eighth-image holdout for LLFF/DL3DV and DTU views \(25,22,28\) across \(15\) scenes. Shared SfM camera poses do not by themselves prove held-out appearance leakage.



### Finding and scope

The available material identifies a scope or evidence gap; it does not prove that the reported empirical effect is false.



### Proposed correction

Release matched baseline initialization, losses and budgets for the compared tables.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: The no-training statement applies only to the video backbone

Assessment: supported; impact: minor



Source: abstract p. 1; method heading p. 4; optimization description pp. 7-8; supplement p. 5



### Source claim (paraphrase)

The abstract describes no scene-specific training or fine-tuning, while the method performs iterative Gaussian scene optimization.



### Analysis

The abstract's no-scene-training wording is broader than the pipeline: each scene undergoes Gaussian optimization for \(10000\) iterations per cycle over three cycles, plus alignment/depth optimization. The valid narrower claim is that the pretrained video backbone requires no scene-specific finetuning. This preserves its reuse benefit while distinguishing preparation cost from feed-forward rendering.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Limit the no-finetuning statement to the video backbone and disclose per-scene Gaussian optimization.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 5: Zero consistency error does not identify true scene depth

Assessment: needs_evidence; impact: needs_evidence



Source: main Eq. (4), Fig. 3, and reconstruction claims in Figs. 5-7



### Source claim (paraphrase)

Equation (\(4\)) uses geometric and photometric consistency to select guidance, and the surrounding discussion associates it with reliable geometry.



### Analysis

Under pure camera rotation about one optical center, pixel correspondence is a depth-independent homography. In a constant-color region, arbitrary positive assigned depth can therefore yield zero geometric cycle error and zero photometric error, so Eq. (\(4\)) gives \(U=0\) despite wrong depth. This is a scoped observability counterexample, not a statement that the benchmark has only degenerate scenes. Reported image-quality improvements and existing geometric/photometric ablations remain evidence of rendering benefit, without proving metrically correct geometry.



### Finding and scope

The available material identifies a scope or evidence gap; it does not prove that the reported empirical effect is false.



### Proposed correction

Describe consistency as internal agreement rather than calibrated true-depth confidence.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 6: Reported gains and partial timing do not establish significance or total cost

Assessment: needs_evidence; impact: needs_evidence



Source: main pp. 8-9; checklist pp. 17-18; supplement §C.3, pp. 6-7



### Source claim (paraphrase)

The reported comparisons and supplement timing are used to discuss superiority and efficiency.



### Analysis

The checklist explicitly discloses absent significance reporting. The small \(0.17\) dB LLFF lead lacks a paired scene/run uncertainty analysis; larger observed differences do not remove that uncertainty. Compute information is provided: about \(30\) minutes of Gaussian optimization per cycle and \(20\) minutes for one \(25\)-frame clip on an NVIDIA A40. Three training cycles give roughly \(90\) minutes of that component. With \(p\) clips per generation round and \(k\) rounds, \(90+20pk\) minutes is only serial component arithmetic; it omits initialization, alignment, transfer and any reuse/parallelism.



### Finding and scope

The available material identifies a scope or evidence gap; it does not prove that the reported empirical effect is false.



### Proposed correction

Report paired scene uncertainty and end-to-end cost with component accounting.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 7: Diffusion time units and nonnegative spatial weights need a common definition

Assessment: supported; impact: minor



Source: Main PDF: diffusion notation, p. 4; Eqs. (2) and (5), pp. 5-6. Supplement: p. 2 and schedule/Algorithm 1, pp. 5-6.



### Source claim (paraphrase)

The main schedule is normalized to the unit interval, the supplement uses a reverse-step scale near \(100\), and a nominally positive scalar weight later becomes spatial and may be zero.



### Analysis

The main schedule uses a threshold on \([0,1]\), while the supplement uses \(\tau=70\overline U+30\) on a reverse-step scale near \(100\). At \(\overline U=0.5\), these conventions give \(0.65\) and \(65\). State whether the comparison is \(t/T\le0.7\overline U+0.3\) or \(t\le T(0.7\overline U+0.3)\), and distinguish reverse indices from scheduler noise timestamps.

The preliminaries write \(g^2(x)\) although the diffusion coefficient is \(g(t)\), and call \(\sigma_t\) a variance while using \(dx=(x-\widehat x_0)\,d\sigma/\sigma\). With variance \(v=\sigma^2\), the equivalent expression is \(dx=(x-\widehat x_0)\,dv/(2v)\).

Eq. (\(2\)) calls \(\gamma_{t,i}\) a positive scalar, but Eq. (\(5\)) allows zero and spatial variation. Nonnegative diagonal/broadcast weights resolve the type issue. The unweighted quadratic term keeps the Hessian positive definite, so Algorithm 1's elementwise minimizer is correct, including zero-weight entries.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Use one explicit diffusion-time convention and nonnegative broadcast weights; the weighted-quadratic minimizer remains valid.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 8: The pose-selection heuristic has a chosen translation scale

Assessment: not_issue; impact: no_issue_found



Source: supplement p. 4, Eq. (S-8)



### Source claim (paraphrase)

Supplement Eq. (S-8) combines translation distance and angular distance with coefficients set to one.



### Analysis

The pose score combines translation distance with angle using unit coefficients. Candidate \(A\) with distance \(0.1\), angle \(0.8\) radians scores about \(0.40657\); candidate \(B\) with distance \(0.5\), angle zero scores \(0.60653\). Multiplying translation coordinates by ten gives \(0.16530\) and \(0.00674\), reversing their ranking under a unit change. Normalize scene scale or specify reciprocal-unit coefficients. The author function correctly converts camera centers, so that separate error is not alleged. A pose heuristic need not measure actual occlusion/field-of-view overlap.

Equation (S-8) explicitly introduces two balancing parameters and fixes them for the reported implementation. Its dependence on translation units does not alone refute a stated scale-invariance theorem, because no such theorem is given. A reproducible implementation should keep the same scene scaling and parameter convention; changing units without transforming the coefficient changes the heuristic itself.



### Finding and scope

The constructed ranking reversal establishes unit sensitivity, not a current mathematical error in a fixed-scale pose-selection heuristic. Its correspondence to actual covisibility remains an empirical question.



## Problem 9: SDS improves some displayed metrics but worsens LPIPS

Assessment: supported; impact: minor



Source: Supplement: Table S-1 and discussion, p. 6; main PDF: Table 3.



### Source claim (paraphrase)

Supplement Table S-1 and the discussion describe baseline improvement from image inpainting.



### Analysis

Supplement Table S-1 reports SDS PSNR \(18.12\), SSIM \(0.551\), and LPIPS \(0.738\), compared with RePaint LPIPS \(0.403\) and the full model's 0.335. The \(0.738\) value is visible in the rendered PDF. If Table 3's baseline LPIPS \(0.405\) is the intended comparator, SDS worsens that metric despite improving PSNR and SSIM. The prose that image inpainting improves the baseline should state which metrics and baseline are meant. This does not justify guessing that \(0.738\) is a typo or replacing it with a more convenient number.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

State the metric-specific SDS pattern without guessing a replacement for the displayed LPIPS value.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.
