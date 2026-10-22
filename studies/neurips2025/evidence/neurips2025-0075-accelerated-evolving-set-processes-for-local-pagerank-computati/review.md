# Accelerated Evolving Set Processes for Local PageRank Computation



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The public local-PageRank routines have queue/reactivation defects, and their saved error metric and timing boundaries differ from the named comparisons. The abstract accelerated framework is not refuted.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: The inner queue can stop before processing active vertices

Assessment: supported; impact: minor



Source: Theorem A.3, PDF pp.18–20; Algorithm 4, PDF p.28; ppr_solver.py, _locAPPR, lines 253–333



### Source claim (paraphrase)

`ppr_solver.py`, `_locAPPR`, allocates a circular queue of one size but advances indices with a different modulus.



### Analysis

The queue capacity is \(n+1\), but increments use modulo \(n\) and sentinel detection uses an ordinary index difference. On a two-vertex single-edge graph, take \(\alpha=1/4\), \(\eta=1/2\), unit seed \(e_1\), center/start \(y=z_0=(2,2)^\top\), and tolerance \(0.01\). The inner quadratic has \(H=\begin{pmatrix}9/8&-3/8\\-3/8&9/8\end{pmatrix}\), \(b_{\rm eff}=(5/4,1)^\top\), and gradient \((1/4,1/2)^\top\). Both vertices are active. Queue writes place vertex zero in slot one, vertex one in slot zero, then overwrite slot one with the sentinel; the routine returns without updates. Exact minimizer is \(z^*=(19/12,17/12)^\top\), so \(h(z_0)-h(z^*)=\tfrac12(z_0-z^*)^\top H(z_0-z^*)=19/96>0.01\). This center satisfies the inner contract but is not asserted reachable in the default outer run.



### Finding and scope

The routine violates its inner accuracy contract on valid inputs. A default end-to-end convergence failure is not established.



### Proposed correction

Use the allocated capacity for every circular increment and circular distance test, or an explicit deque/sentinel design with consistent emptiness semantics.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: The lazy baseline drops a still-active processed coordinate

Assessment: supported; impact: minor



Source: Section 4 baseline; Lemma 2.1, PDF p.3; ppr_solver.py, appr, lines 26–99



### Source claim (paraphrase)

The baseline `appr` routine checks neighbors for activation after a push but can leave its own retained residual unqueued.



### Analysis

On a four-vertex star with a leaf source, \(\alpha=1/4\) and \(\epsilon=1/5\), the processed source retains residual \(3/8\). Its neighbor threshold prevents reactivation through the center. Returned estimate \((0,1/4,0,0)\) differs from exact PageRank \((3/8,19/40,3/40,3/40)\), with normalized error \(9/40>1/5\).



### Finding and scope

This baseline path fails its requested normalized tolerance. Other PageRank routines are not covered.



### Proposed correction

Requeue the processed coordinate whenever its retained residual remains active, preserving the same activation invariant as neighbors.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: The saved error is not the figure’s degree-normalized error

Assessment: supported; impact: minor



Source: Figures 2 and 4 and convergence figures; ppr_solver.py, norm_inf and saved errs calls



### Source claim (paraphrase)

The evaluation labels a density-normalized infinity error, but its saved `norm_inf` path does not divide the recovered PageRank error by degree.



### Analysis

For a center-seeded four-star and zero estimate, the saved error is \(5/8\), while the named degree-normalized error is \(5/24\). Nonconstant degrees make these different metrics rather than a universal common rescaling.



### Finding and scope

The public metric label and computation differ. A specific published ranking reversal is not established.



### Proposed correction

Use the declared degree normalization, or relabel and interpret the actual metric consistently.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 4: Reported timers cover unequal portions of the methods

Assessment: supported; impact: minor



Source: Section 4, timing figures and Table 4; ppr_solver.py, _locAPPR, _locGD and outer timer accumulation



### Source claim (paraphrase)

The accelerated path sums inner timers that start after initialization and scans, omitting outer residual/momentum work; the baseline timer begins before its initialization.



### Analysis

Those boundaries omit different necessary work, so the returned times cannot directly support an end-to-end speed ratio. This is a source-level accounting observation rather than a new latency measurement.



### Finding and scope

The public timing outputs need a common scope. No corrected large-graph speedup is estimated.



### Proposed correction

Time the same complete-call boundary for both methods, state warmup/synchronization rules and preserve component timings separately.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
