# OpenHype: Hyperbolic Embeddings for Hierarchical Open-Vocabulary Radiance Fields



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Operation-dependent precision promotion can erase an order-one Lorentz distance between valid points. A separate CPU gradient failure does not generalize to the successful CUDA controls.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Promoting the output does not recover rounded Lorentz intermediates

Assessment: supported; impact: minor



Source: Appendix A, PDF p.21; Appendix D.2, PDF p.23; openhype/utils/lorentz.py, get_time_comp and pairwise_dist; openhype/openhype_ae/hyperbolic_ae.py, distance call



### Source claim (paraphrase)

Appendices A and D.2 use Lorentz maps and distances, with a radial cap for stability. The release promotes only part of the distance calculation.



### Analysis

Let \(R=2^{14}\), \(x=(\sqrt{R^2+1},R,0)\), and \(y=(\sqrt{R^2+2},R,1)\), with curvature parameter \(1\). Rationalization gives \[-\langle x,y\rangle_L=(3R^2+2)/(\sqrt{(R^2+1)(R^2+2)}+R^2)\], hence distance approximately \(0.962424\). Single-precision squared norms lose the unit increments before the Lorentz subtraction, so a later double-precision output cannot restore them. The points satisfy the configured cap. A distinct finite-loss CPU case had invalid gradients, whereas the corresponding CUDA controls had finite gradients. The CPU/CUDA outcomes are historical measurements from the stated source snapshot, not new runtime executions in this pass; the original recommended dependency environment remains untested.



### Finding and scope

The distance path is precision-sensitive. Neither universal gradient failure nor invalidity of the published CUDA training is established.



### Proposed correction

Promote operands before the squared norms, reconstructed time coordinates and Lorentz product. Keep the backend-specific passing controls; changing only the final dtype does not address prior cancellation.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.

- The historical numerical controls use a different runtime from the recommended original environment; cross-version behavior was not newly tested.
