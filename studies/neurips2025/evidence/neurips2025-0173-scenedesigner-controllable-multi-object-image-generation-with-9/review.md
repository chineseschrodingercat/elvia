# SceneDesigner: Controllable Multi-Object Image Generation with 9-DoF Pose Manipulation



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current public application implements global conditioning but omits the paperâ€™s object-specific latent proposals and ordered mask blending. This previously reported release limitation is established by argument flow; historical image-quality results are not refuted.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: The public entry point omits object-specific latent blending

Assessment: supported; impact: minor



Source: Algorithm 1, PDF p.7; app.py generate_image; pipeline_scenedesigner.py denoising loop



### Source claim (paraphrase)

The paper sets \(z_0=x_t+\Delta t\,v_g\), forms each \(u_i=x_t+\Delta t\,v_i\), and replaces masked regions by \(z_i=(1-M_i)\odot z_{i-1}+M_i\odot u_i\).



### Analysis

The application passes only global condition/prompt data and the denoising path advances a single global prediction; renderer-created individual object files are not consumed by that call. With a \(2\times2\) zero latent, \(\Delta t=1/2\), global velocity \(1\), object velocity \(2\), and a mask selecting one pixel, global-only output is \(0.5\) everywhere, while Algorithm 1 gives \(1\) at the selected pixel. Their difference is exactly \(M_1\Delta t(v_1-v_g)\); empty masks or equal velocities are agreement cases.



### Finding and scope

The released entry point does not reproduce DOS. This does not prove the historical experiments omitted it or that DOS cannot improve outputs.



### Proposed correction

The published ordered mask recurrence is the verified local update. An integrated implementation additionally needs object prompts, maps, latent masks and matching scheduler/overlap conventions; no complete pipeline repair is claimed.

The public report in repository issue 3, dated 28 February 2026, had already raised this release gap. No accepted integrated correction is established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
