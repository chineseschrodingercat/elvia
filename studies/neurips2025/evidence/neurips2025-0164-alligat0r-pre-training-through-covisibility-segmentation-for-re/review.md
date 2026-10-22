# Alligat0R: Pre-Training through Covisibility Segmentation for Relative Camera Pose Regression



Preliminary assessment: No Issue Found

Independent scientific review: pending. Author adoption: not requested.



No substantive scientific error was established in the inspected covisibility objective, pose losses, metric interpretation or reported split descriptions. A released host timer remains a limited reproducibility caveat without a replacement runtime measurement.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: The pose-loss normalization admits an equivalent parameterization

Assessment: not_issue; impact: minor



Source: Pose loss, arXiv v2 Eq.(8), PDF p.5



### Source claim (paraphrase)

The manuscript uses squared residual norm with uncertainty, whereas code can use component-mean MSE.



### Analysis

The code form \(e^{-s}\|r\|^2/d+s/2\) equals \(\|r\|^2/(2\sigma^2)+\log\sigma+\tfrac12\log(2/d)\) under \(s=\log(2\sigma^2/d)\). The added constant does not alter optimization. A sign-folded angular diagnostic also does not replace metric translation error: \((1,0,0)\) versus \((-1,0,0)\) has distance \(2\).



### Finding and scope

These are compatible parameterization/metric distinctions, without a demonstrated scientific contradiction.



## Problem 2: Unsynchronized host timing is only a limited caveat

Assessment: not_issue; impact: minor



Source: Released eval.py, get_pose_estimation, lines 59–62; runtime comparison



### Source claim (paraphrase)

The release measures host elapsed time around a potentially asynchronous CUDA forward call.



### Analysis

The timer stops before outputs are copied to CPU, so it need not include all completed GPU work. However historical timing provenance, device execution and the complete measurement path are unestablished. No numerical runtime was remeasured.



### Finding and scope

A synchronized/event-based rerun would be needed to assess the published runtime; the current observation alone does not refute it.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.

- Scene memberships, raw annotations, trained-model accuracy and GPU runtime were not independently reproduced.
