# ROSE: Remove Objects with Side Effects in Videos



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The documented difference-mask grid permutes actual video coordinates despite matching token counts. The current evaluator also infers image units from brightness. Both are local supervision/reproducibility defects with unestablished effects on published video results.



## Scope

Rapid claim-focused reading of current author-paper passages and relevant released source. Direct mathematical or static-source reasoning is stated below. No author program, inherited verifier, model inference or benchmark was executed.



## Problem 1: Equal token counts do not preserve video coordinates

Assessment: supported; impact: minor



Source: Proceedings Appendix B, PDF p.19; current author rose/models/diff_mask_predictor.py; VAE and transformer patch-grid definitions



### Source claim (paraphrase)

The predictor reshapes \(28350\) patch scalars to \((10,15,189)\) before trilinear interpolation to \((81,480,720)\). It describes this as spatiotemporal patch supervision.



### Analysis

The stated causal VAE compression gives latent shape \((21,60,90)\), and the checkpoint/backbone stride \((1,2,2)\) yields actual patch grid \((21,30,45)\). Both products equal \(28350\), so the source’s token-count assertion passes despite different coordinates. Actual row-major index \(j=(30t+h)45+w\) maps \((1,0,0)\) to \(1350\); the documented reshape places it at \((0,7,27)\).

A bounded token field \(z_{t,h,w}=t/20\) is spatially constant on each correct time plane. The documented first plane mixes values \(0,0.05,0.10\) from three actual time planes, creating spatial variation. Trilinear interpolation cannot generally undo this coordinate permutation. The released default matches the displayed reshape; an unpublished training override or compensating learned features could change practical effects.



### Finding and scope

The documented/default supervision grid does not invert the backbone’s flattening. This does not establish failed inference, because the predictor is discarded there, or quantify the trained generator’s quality.



### Proposed correction

Carry the actual per-sample patch grid and flattening order into the predictor; here reshape to \((21,30,45)\). Use valid unpadded token lengths before interpolation. This restores the coordinate inverse without guaranteeing that changing a trained head preserves performance.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Problem 2: Brightness heuristics do not define image units

Assessment: supported; impact: minor



Source: Proceedings Section 5.1, PDF pp.8–9; current author utils/evaluate_video.py, preprocessing lines 20–38 and LPIPS lines 76–104



### Source claim (paraphrase)

The evaluator divides by the byte scale only if observed brightness exceeds the unit interval. Its LPIPS branch uses the first frame’s maximum to decide conversion for both frames.



### Analysis

For byte-valued constant RGB frames \(0\) and \(1\), correct unit-range MSE is \(1/255^2\), giving PSNR \(20\log_{10}255\approx48.1308\) dB. Both maxima are at most \(1\), so the source leaves them unchanged and computes unit-range PSNR \(0\) dB. Encoding the identical images as floating \(0,1/255\) changes this behavior.

For LPIPS, equivalent byte values \((64,192)\) are mapped to approximately \((-0.4980392,0.5058824)\), but unit-range floating equivalents remain \((0.2509804,0.7529412)\). The latter omits the required symmetric-range conversion. A byte black/white pair also changes conventions when reversed because only the first frame’s maximum controls both. These are input-contract differences, without loading or evaluating a perceptual network.



### Finding and scope

The current metric utility is representation dependent on valid inputs. The exact data format and evaluator used for historical tables are not established, so corrected table values or rankings are not inferred.



### Proposed correction

Declare input range and RGB layout explicitly: map byte images to \(U=x/255\), accept declared unit-range floats unchanged, then use \(U\) for PSNR/SSIM and \(2U-1\) for LPIPS. Reject unsupported units rather than inferring them from brightness.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- Exact calculations and static-source findings do not remeasure published experiments or establish the historical experiment-generating revision.
