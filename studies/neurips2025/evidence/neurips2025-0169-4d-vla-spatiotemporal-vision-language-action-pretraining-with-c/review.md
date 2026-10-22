# 4D-VLA:  Spatiotemporal Vision-Language-Action Pretraining with Cross-Scene Calibration



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The active release performs bilinear center-stencil depth resizing instead of complete-patch averaging and missingness testing. Exact sparse/depth examples reverse inclusion in both directions, without establishing a robot-performance effect.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Bilinear stencil sampling does not implement the patch-wide rule

Assessment: supported; impact: minor



Source: Section 4.2, PDF p.6; unproject.py, interpolate_depth, lines 54–67



### Source claim (paraphrase)

The paper computes patch-mean depth and skips the \(3\)-D feature when over \(90\%\) of the patch is masked; the release downsamples depth and mask bilinearly.



### Analysis

At a \(14\)-to-\(1\) reduction with align_corners false, a patch output samples only its four central pixels, each weight \(1/4\). One valid central depth \(2\) among \(196\) pixels gives interpolated mask \(1/4>0.1\), so the release retains it despite \(195/196>0.9\) missingness. If only the four central pixels are invalid and the other \(192\) have depth \(2\), it rejects a mostly valid patch. With every pixel valid, central depth \(2\) and other depths \(4\), the patch mean is \(776/196\approx3.959184\), but the release gives \(2\). Both mask examples avoid ambiguity over averaging zero placeholders; the full-valid example avoids missing data entirely.



### Finding and scope

The stated complete-patch mean/missingness operation and active release differ. Constant/full-invalid controls agree, and no action failure or dataset prevalence is inferred.



### Proposed correction

For aligned patches compute \(n_P=\sum M_p\) and \(u_P=\sum M_pD_p\). Retain when \(n_P>0\) and \(10n_P\ge A\), and use \(u_P/n_P\). This restores the declared local rule for the stated partition; changed checkpoints/performance require separate evaluation.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
