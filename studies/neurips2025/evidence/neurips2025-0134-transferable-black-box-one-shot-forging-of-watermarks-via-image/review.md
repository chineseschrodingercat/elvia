# Transferable Black-Box One-Shot Forging of Watermarks via Image Preference Models



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The released original-resolution extraction adds a resize residual absent from the paper's perturbation formula. It can attribute ordinary lost image detail to a watermark even without an optimization update.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: Original-resolution subtraction adds a resizing residual absent from Equation (4)

Assessment: supported; impact: minor



Source: Section 3.2, Eq. (4), PDF p. 6; released optimize_image.py extraction, lines 50–55.



### Source claim (paraphrase)

Section 3.2, Eq. (4), PDF p. 6, forms a perturbation at the resized resolution and then upsamples that perturbation for transfer. Released optimize_image.py, lines 50–55, instead subtracts an upsampled optimized image from the original-resolution reference.



### Analysis

Let \(D\) downsample, \(U\) upsample, \(x\) be the original image and \(z\) the optimized low-resolution image. The specified perturbation is \(U(Dx-z)\), while the helper uses \(x-Uz\); their difference is \(x-UDx\). Setting \(z=Dx\) eliminates optimization changes, but the helper still assigns ordinary lost resize detail as a nonzero perturbation. Quantization is not needed for this discrepancy.



### Finding and scope

The exact operator difference contaminates extracted residuals at changed resolutions; same-resolution controls and unknown experimental image sizes prevent a benchmark-level conclusion.



### Proposed correction

The proposed correction resizes the working-resolution perturbation and preserves the original subtraction operands; no decoder or attack-success rerun is claimed.

A local correction or qualification is proposed where specified; author adoption is not established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.

- The existing author clarification restricts preference-score comparison to watermark variants of the same image; no newly discovered absolute-score calibration error is asserted.
