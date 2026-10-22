# Implicit-ARAP: Efficient Handle-Guided Neural Field Deformation via Local Patch Meshing



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The author release has local cotangent assembly, shared-edge, pole-alignment and coordinate-grid defects, alongside equation/configuration discrepancies. Their effects on the paper's central deformation results are not established, so the strict label is Minor. Projection guarantees, matched handle accuracy and sampling/termination scope remain unresolved.



## Scope

All fifteen original concerns, current final paper passages, freshly retrieved official supplemental source and the author-linked current public repository compared read-only. Direct geometry/dataflow checks only; no author, PyTorch, mesh or old verifier program executed.



## Problem 1: Cotangents are paired with the wrong edges

Assessment: supported; impact: minor



Source: Paper pp. 5; iarap/model/nn/loss.py



### Source claim (paraphrase)

The retained ARAP assembly assigns each cotangent to its opposite edge.



### Analysis

The current official supplemental PatchARAPLoss lists edges \((0,1),(1,2),(0,2)\), but assigns cotangents of angles at vertices \(0,1,2\) in that order rather than to opposite edges. For vertices \((0,0,0),(2,0,0),(0,1,0)\), the angle cotangents are \(0,2,1/2\). Correct edge weights are \(w_{01}=1/2,w_{12}=0,w_{02}=2\); the source gives \(0,2,1/2\). With identity rotations and displacement \((0,0.2,0)\) only at the third vertex, the implemented energy is \(0.10\), becoming \(0.02\) after reversing vertex order without changing geometry. Correct assembly gives \(0.08\) in both orders. No global coefficient removes this ordering dependence; its benchmark effect remains unknown.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: Shared edges are overwritten and counted twice

Assessment: supported; impact: minor



Source: loss.py



### Source claim (paraphrase)

Shared-edge weights are accumulated and used with the intended multiplicity.



### Analysis

The current supplemental source assigns all per-face cotangents into a dense matrix using repeated indices, then adds its transpose; it does not scatter-add same-direction contributions. Even after repairing the preceding angle pairing, vertices \[(0,0),(2,0),(0.4,1),(2,2)\] and faces \((0,1,2),(1,3,2)\) give opposite-angle contributions \(0.4\) and \(0.625\) on shared edge \(\{1,2\}\). Their sum must be \(1.025\), while a last-write interpretation gives \(0.625\); cyclically rewriting the second face as \((3,2,1)\) changes the stored result without changing its geometry. GPU repeated-index assignment order was not measured. The later per-face edge list also repeats interior edges, changing their relative contribution after weights have already been assembled. Neither a global sum/mean convention nor a global loss coefficient repairs these relative differences.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: Tangent alignment is singular at the poles

Assessment: supported; impact: minor



Source: Paper pp. 4; iarap/model/base_sdf.py; deform_trainer.py



### Source claim (paraphrase)

Tangent alignment handles valid normals at the coordinate poles.



### Analysis

Division by squared norm of \(n\times e_z\) fails for exact SDFs \(f(x,y,z)=z\) and \(f(x,y,z)=-z\). Generic-direction checks pass, so this is a pole singularity rather than a universally reversed rotation.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: Approximate-SDF projection need not converge

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 4, 23; base_sdf.py



### Source claim (paraphrase)

Repeated normalized-gradient projection converges for the stated approximate fields.



### Analysis

For \(f(x,y,z)=az\), normalized-gradient iteration gives \(z_{\rm next}=(1-a)z\), converging only for \(0<a<2\). At \(a=2\) it cycles; \(a=3\) diverges. The local exact-SDF interpretation is not refuted.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 5: Marching-Cubes coordinates use the wrong denominator

Assessment: supported; impact: minor



Source: iarap/train/deform_trainer.py



### Source claim (paraphrase)

Marching-Cubes indices map to the endpoint-inclusive sampling coordinates.



### Analysis

Endpoint-inclusive sampling on \([-1,1]\) needs \(-1+2i/(R-1)\), whereas source uses \(-1+2i/R\). An origin plane shifts to \(-1/R\) and the upper endpoint to \(1-2/R\). Baseline geometry is biased; ranking after repair is unknown.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 6: Eikonal loss uses absolute instead of squared error

Assessment: supported; impact: minor



Source: Paper pp. 23; loss.py



### Source claim (paraphrase)

The source Eikonal objective equals the printed squared penalty.



### Analysis

The paper squares gradient-norm error while the source takes its absolute value. At errors \(0.1\) and \(1\), ratios are \(10\) and \(1\), so no constant coefficient reconciles them.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 7: Handle groups receive different weights

Assessment: supported; impact: minor



Source: Paper pp. 4, 25; loss.py; config/defaults.py



### Source claim (paraphrase)

The source averages handles using the paper’s all-handle rule.



### Analysis

Moving and static groups are averaged separately in source. One erroneous moving handle and nine exact static handles give \(1\)/\(3\) versus printed all-handle vector average 0.1. Group counts change relative weights.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 8: The angle formula lacks a common vertex

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 7



### Source claim (paraphrase)

The face-angle formula is invariant to rigid translation.



### Analysis

Directly applying a point map to two edge vectors makes the angle translation-dependent. Translating \((1,0),(0,1)\) by \((1,1)\) creates spurious \(53.13^\circ\) error under that literal rule. Actual evaluation behavior remains unresolved.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 9: Default settings do not identify the reported runs

Assessment: supported; impact: minor



Source: Paper pp. 24–26; config/defaults.py; model/nn/invertible.py



### Source claim (paraphrase)

Default release configuration identifies the stated experimental network and schedule.



### Analysis

The current final supplementary demo uses invertible width \(128\), versus the paper’s stated \(256\), ARAP weight \(10\) versus the implicit-field setting \(1000\), and an SDF learning-rate milestone override of \(10000\) versus the stated \(1000,2000,5000\). The final README explicitly permits CLI overrides, so these do not establish which settings produced the tables. The separate current public repository is an earlier July 2025 release: its SDF demo already uses ARAP weight \(1000\), although other defaults differ. Thus the weight discrepancy is specifically against the current final supplementary demo, not every author resource. The separate eight-layer, width-\(256\) SDF architecture matches and is not confused with invertible deformation width.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 10: Radius changes regularization strength

Assessment: supported; impact: minor



Source: Paper pp. 30–31; loss.py



### Source claim (paraphrase)

Patch-radius ablation isolates geometry while preserving relative regularization scale.



### Analysis

Patch scaling by \(\rho\) preserves cotangents but scales squared edge energy by \(\rho\) squared, confounding geometry and loss strength. An absolute Heron-area floor further breaks small-triangle scale invariance. Authors partly acknowledge weak small-patch regularization.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 11: Comparisons need matched handle accuracy

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 7–8, 28



### Source claim (paraphrase)

The main comparisons establish rigidity preservation at comparable constraint satisfaction.



### Analysis

An unchanged shape preserves rigidity while failing target handles. Main tables lack matched moving/static-handle tolerances and failure rates; authors acknowledge this tradeoff. An unfair comparison is not proven without paired constraint errors.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 12: Constant optimization cost is not constant total cost

Assessment: not_issue; impact: no_issue_found



Source: Paper pp. 26–27



### Source claim (paraphrase)

Given a fixed neural field and patch budget, the deformation optimization avoids direct dependence on input mesh vertex count.



### Analysis

The current high-resolution section explicitly discusses the deformation procedure separately from internal SDF fitting, and Table 4 includes the fitting contribution while Figure 18 excludes it. With a fixed field, patch count and optimization budget, that limited optimization-scaling claim can hold. Producing all \(N\) deformed vertices still costs at least \(\Omega(N)\) time/output space, and field preparation has its own accuracy-dependent cost. This bounds the scope of the claimed stage-level efficiency rather than refuting it as a total-pipeline theorem.



### Finding and scope

The output-size lower bound does not contradict the explicitly scoped optimization comparison; no separate current complexity error is established.



## Problem 13: Finite datasets do not remove uncertainty

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 17



### Source claim (paraphrase)

Finite dataset size removes the need to quantify optimization variability.



### Analysis

The checklist openly states no error bars. Initialization, sampling and triangulation remain variable; per-task failures and repeated runs are needed to assess stability.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 14: Projected sampling needs scope and termination bounds

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 23; base_sdf.py



### Source claim (paraphrase)

The projected sampler has the claimed uniformity and defined termination behavior.



### Analysis

Finite-band projection is not generally exactly area-uniform because curvature changes the volume element. A loop without total attempts can fail to terminate when near-zero points are unavailable. No benchmark hang is claimed.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 15: An auxiliary unchanged-vertex test reduces the wrong axis

Assessment: supported; impact: minor



Source: iarap/model/arap.py



### Source claim (paraphrase)

The auxiliary unchanged-vertex test requires all coordinates to remain fixed.



### Analysis

The ARAPMesh helper treats any coordinate fixed across neighbors as a wholly unchanged vertex. A planar \(90^\circ\) rotation preserves \(z\) but changes \(x,y\), so affected vertices can be incorrectly zeroed. Main-table impact is unknown.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- No new author-code execution, training, empirical replication or contact.

- Historical verification outputs were inspected but not rerun.

- Missing run provenance and unresolved empirical interpretations remain explicit.
