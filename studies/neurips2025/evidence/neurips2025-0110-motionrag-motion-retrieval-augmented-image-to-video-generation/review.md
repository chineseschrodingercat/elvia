# MotionRAG: Motion Retrieval-Augmented Image-to-Video Generation



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The released CAMA inference branch changes the target-image range relative to training/reference frames. Its learnable initial token is also absent from the stage-\(2\) optimizer and incremental checkpoint.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: CogVideoX inference changes the target image’s pixel range before CAMA

Assessment: supported; impact: minor



Source: Section 3.3 and Figure 3, PDF p. 5; Section 3.5, PDF p. 6; released CogVideoX CAMA input path.



### Source claim (paraphrase)

Paraphrase: Section 3.3, page 5, describes the target image and the first frame of each reference video as inputs to the same DINO appearance encoder and resampler. Figure 3 depicts that common image-encoding path. Section 3.5, page 6, uses the trained CAMA component during inference. No separate target-only brightness transform is specified.

The current src/data/dataset.py, lines 88–96, scales physical pixels to \([0,1]\) and then normalizes with mean and standard deviation \(0.5\), producing \([-1,1]\). Training target frames and reference first frames follow that convention. The shared inherited DINO preprocessing maps \(x\) to \((x+1)/2\) before channel standardization.



### Analysis

Let a dataset pixel be \(x=2u-1\), where \(u\in[0,1]\). The common DINO preprocessing restores it by \(P(x)=(x+1)/2=u\). The inference wrapper first restores \(u\), then applies the same preprocessing again, yielding \(P(u)=(u+1)/2\). Thus black becomes \(0.5\) in the target branch but stays \(0\) in training/reference branches. A constant image makes this comparison independent of resizing.



### Finding and scope

A black inference target reaches the shared encoder as gray while training/reference black remains black; generated-video effects and use of that release path in published runs remain unmeasured.



### Proposed correction

Make the helper’s input range explicit. For the inference caller, convert \([0,1]\) back to \([-1,1]\) only before CAMA; preserve the base generator’s \([0,1]\) image. The direct training helper already receives \([-1,1]\), so an unconditional conversion in the shared helper is an invalid general patch.

The two-part local proposal remains applicable to the current release; no author adoption is established. The separate author clarification about prior short-video base adaptation is not a correction of these findings.



## Problem 2: The initial context token is neither optimized nor retained by the released stage-\(2\) recipe

Assessment: supported; impact: minor



Source: Figure 3, PDF p. 5; Section 3.5, PDF p. 6; Appendix A, PDF p. 21.



### Source claim (paraphrase)

Figure 3, PDF p. 5, calls the initial context a learnable token. Current ActionTransformer.__init__, lines 256–262, creates root parameter sos_token with shape \((1,q,d)\), where \(q=25\), \(d=1024\), and forward line 298 uses it. The released stage-two recipe selects trainable child modules transformer and condition_proj; the root parameter belongs to neither.



### Analysis

The root parameter sos_token belongs to neither configured trainable child module transformer nor condition_proj. Selecting only those modules omits the token from optimizer groups, and filtering checkpoint keys by the same prefixes omits it from saved state. A requires_grad flag cannot compensate for exclusion from the optimizer and checkpoint.



### Finding and scope

The initial token is used but cannot be updated or reproduced from the filtered checkpoint under the current recipe; the effect of learning it on the central method is not measured.

A distributed checkpoint could contain additional state; none was downloaded. Adding a future save rule cannot reconstruct a missing historical token value.



### Proposed correction

The proposed correction adds the actual root parameter to optimization and serialization. A missing historical token cannot be recovered merely by changing the save filter.

A local correction or qualification is proposed where specified; author adoption is not established.

The two-part local proposal remains applicable to the current release; no author adoption is established. The separate author clarification about prior short-video base adaptation is not a correction of these findings.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.

- An existing author clarification credits prior short-video adaptation of the frozen CogVideoX base; no unequal-baseline error is inferred from the release configuration alone. Nonuniform FVD changes and the empirical-oracle interpretation remain bounded scope notes rather than newly measured errata.
