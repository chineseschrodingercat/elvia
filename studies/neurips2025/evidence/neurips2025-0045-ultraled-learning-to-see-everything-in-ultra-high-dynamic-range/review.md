# UltraLED: Learning to See Everything in Ultra-High Dynamic Range Scenes



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The author release has a restricted-resolution control branch, a mismatch with zero-residual initialization, and a nondefault 16-bit export defect. These are local faults. The default paper camera geometry and central historical image results are not refuted, so the strict label is Minor.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Control feature sizes match only a restricted resolution class

Assessment: supported; impact: minor



Source: Eqs. (5)–(6), PDF pp. 5–6; author cunet_arch.py, lines 96–165; inference entry, line 123.



### Source claim (paraphrase)

The inference tool accepts RAW images and relies on model padding/cropping, but its control branch adds a fixed two rows before alignment.



### Analysis

The backbone addition uses size \((4\lceil H/16\rceil,4\lceil W/16\rceil)\), while the control branch uses \((\lfloor H/4\rfloor+2,\lfloor W/4\rfloor)\). At \(H=W=32\), these are \(8\times8\) and \(10\times8\). Compatibility requires \(H\bmod16\in\{8,9,10,11\}\) and \(W\bmod16=0\). The paper's packed camera shape \(2344\times3520\) satisfies the condition, so the witness does not refute that default geometry.



### Finding and scope

The code arithmetic proves an input-domain defect without running a model. It does not show failure at the original camera geometry.



### Proposed correction

Align control size to the padded backbone feature shape, or state the restricted input domain. No end-to-end corrected model result is asserted.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: The released training path omits zero residual initialization

Assessment: supported; impact: minor



Source: Text following Eq. (6), PDF p. 6; author cunet_arch.py, lines 8–11 and 28–40; stage-two training configuration.



### Source claim (paraphrase)

The method describes zero-initialized convolutional residual blocks.



### Analysis

The zero_module helper is defined but the four ResidualBlock instances construct default Conv2d layers without invoking it. A fresh stage-two network has no pretrained network_g in the traced configuration, so loading the ratio estimator cannot initialize these residual branches to zero.



### Finding and scope

A specific release/training-recipe discrepancy is supported. Nonzero trained weights alone would not be evidence, and the original historical training version remains unknown.



### Proposed correction

Initialize the residual branch as specified, or identify the historical initialization actually used. Zeroing its final convolution gives zero initial residual algebraically.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: Requested \(16\)-bit pixel values wrap during final \(8\)-bit export

Assessment: supported; impact: minor



Source: Author UltraLED inference documentation; image_process_ultraled.py, lines 87–88 and 126–131.



### Source claim (paraphrase)

The script exposes output bit depth but always casts the returned array to uint8 before saving.



### Analysis

On the requested 16-bit path, valid values \[[0,255,256,32768,65535]\] cast to uint8 become \([0,255,0,0,255]\). This is modular truncation, not monotonic 16-to-8-bit rescaling. The cast occurs after selected-bit-depth postprocessing and before imwrite.



### Finding and scope

The nondefault 16-bit export path has a concrete encoding defect. Default 8-bit behavior and original evaluation scores are outside this counterexample.



### Proposed correction

Preserve uint16 for the 16-bit output path; explicitly rescale and label an 8-bit preview if desired.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- Local contradictions and specification differences do not establish the magnitude or direction of changes to the published benchmark scores.

- No author contact or adoption; novelty and complete historical-run provenance are unestablished.
