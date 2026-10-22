# Continual Model Merging without Data: Dual Projections for Balancing Stability and Plasticity



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The public solver has rank-index and gradient-scaling mismatches. The task-space rationale additionally needs optimizer and coverage restrictions. No universal preservation or final Pareto outcome follows from the tested proxies.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: The threshold-crossing index is not the component count

Assessment: supported; impact: minor



Source: Section 4.2, PDF p.6; current FusionBench fusion_bench/method/dop/dop.py, SVD searchsorted and subspace slices



### Source claim (paraphrase)

`dop.py` uses the zero-based crossing index as the rank in a slice.



### Analysis

For singular values \((3,1)\), a \(0.9\) cumulative threshold crosses at index \(1\), but keeping one component captures only \(0.75\) of the mass. For \((1,0)\), crossing index zero yields an empty subspace, zero proxy and potentially undefined zero-loss normalization.



### Finding and scope

The public rank selection omits the crossing component.



### Proposed correction

Convert index to count by adding one, with separate rules for zero total mass and zero normalization losses.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Normalized-gradient coefficients do not give raw-gradient common descent

Assessment: supported; impact: minor



Source: Eq.(3), PDF pp.6–7; current FusionBench fusion_bench/method/dop/dop.py, gradient_normalizers, MinNormSolver and scaled backward



### Source claim (paraphrase)

Equation (3) chooses coefficients for a minimum-norm combination, but the release solves using loss-normalized gradients and applies the coefficients to raw gradients.



### Analysis

At \(w=1\), losses \(8w^2\) and \(32(w-2)^2\) have raw gradients \(16,-64\), normalized gradients \(2,-2\), and normalized coefficient \(1/2\). Applying that coefficient to raw gradients gives \(-24\), so subtracting the direction increases the first loss. The default smoothed coefficients approximately \((0.7997,0.2003)\) still give \(-0.024\), whereas raw minimum-norm coefficients \((0.8,0.2)\) give zero.



### Finding and scope

This release step lacks the stated per-step common-descent property. It does not determine every final Pareto status.



### Proposed correction

Use the same gradients for coefficient selection and application. Treat coefficient smoothing as a changed algorithm unless a separate descent check preserves the required inequalities.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: The raw-gradient span argument does not automatically extend to Adam

Assessment: supported; impact: minor



Source: Properties 4.1–4.2, pp. 5–6; Adam fine-tuning in Appendix C, p. 25.



### Source claim (paraphrase)

Properties 4.1–4.2 derive a task-vector span relation by scalar-step gradient-descent telescoping, while expert training includes Adam.



### Analysis

For input \(x=(1,2)\), zero initial weight and an appropriate squared loss, the raw gradient is \((-1,-2)\). Adam’s first normalized update is approximately \((0.1,0.1)\), outside the one-dimensional span of \(x\). Coordinatewise preconditioning need not preserve a raw-gradient span.



### Finding and scope

The scalar-gradient-descent proposition survives with its optimizer restriction. Its extension to all Adam-trained experts is not justified.



### Proposed correction

Restrict updates to scalar linear combinations of historical raw gradients, or analyze the actual preconditioned update spaces.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 4: A task-vector proxy need not cover the full old input subspace

Assessment: supported; impact: minor



Source: Section 3.2.2, p. 5; Section 4.2 proxy-retention interpretation, p. 6.



### Source claim (paraphrase)

The retention interpretation treats zero projection loss in retained task-vector directions as protecting all old inputs.



### Analysis

Let \(W_0=\operatorname{diag}(0,1)\), \(W_o=I\), and \(W_n=W^*=\operatorname{diag}(1,3)\). The old task vector is \(\operatorname{diag}(1,0)\); both stated task proxies vanish, yet old input \(e_2\) changes output from \(e_2\) to \(3e_2\). Directions unchanged by old fine-tuning can still matter to old prediction.



### Finding and scope

Zero proxy is not a universal old-task preservation theorem. The paper’s approximation language remains material.



### Proposed correction

Full preservation follows if the retained task subspace covers the old input subspace and the corresponding projection loss is zero. Mere containment in the opposite direction is insufficient.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
