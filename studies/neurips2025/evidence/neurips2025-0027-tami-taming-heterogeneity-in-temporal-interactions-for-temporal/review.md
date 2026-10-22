# TAMI: Taming Heterogeneity in Temporal Interactions for Temporal Graph Link Prediction



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current paper retains an incorrect exact-skewness claim under the standard Type-I Pareto interpretation, and the current author memory path can use equal-time events across batch boundaries despite the strict-past task definition. Both are Minor within the available evidence: a distribution convention can repair the first, while the second has no quantified current benchmark effect.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: The transformed Pareto variable need not have skewness two

Assessment: supported; impact: minor



Source: Proposition 1, p.4; Appendix A, p.21, Eq.7 and densities.



### Source claim (paraphrase)

Proposition 1 assigns skewness \(2\) to \(\log(1+T)\) for a standard Pareto time difference.



### Analysis

For standard Type-I Pareto \(T\) with shape \(\alpha\) and minimum \(c>0\), the density of \(Y=\log(1+T)\) is \[f_Y(y)=\frac{\alpha c^\alpha e^y}{(e^y-1)^{\alpha+1}},\qquad y\ge\log(1+c),\] rather than a shifted exponential density. With \(\alpha=4,c=1\), its first three moments are approximately \[(0.833333333333,0.718517562805,0.648490931824)\], giving skewness \(2.571420899\), rather than \(2\). More generally, write \(T=cV\) for \(V\sim\operatorname{Pareto}(1,\alpha)\), \(\alpha>3\). As \(c\downarrow0\), \(\log(1+cV)/c\to V\) and is bounded by \(V\). Dominated convergence of the first three moments implies its skewness approaches that of \(V\), which exceeds \(2\); it therefore cannot equal \(2\) for every scale. If the intended assumption is instead that \(1+T\) is Type-I Pareto, the shifted-exponential conclusion does hold.



### Finding and scope

The exact constant in current Proposition 1 is not valid for an arbitrary standard Type-I Pareto time difference. This is a distribution/shift condition issue; it does not refute empirical benefits of logarithmic compression or the paper’s acknowledged non-Pareto data behavior.



### Proposed correction

State the appropriate shifted-Pareto/Lomax model or use the log-ratio transform.

Current Proposition 1, Appendix A and latest arXiv v1 retain the same shift and density. Specifying a Pareto law for the shifted variable is the existing conditional correction; the author’s intended convention remains unconfirmed.



## Problem 2: Equal-time memory can include non-past events

Assessment: supported; impact: minor



Source: Sections 3.1/3.3, PDF pp. 3–6; current models/modules.py, decoder forward/TRCMemory; evaluate_models_utils.py, positive-batch update



### Source claim (paraphrase)

The task definition predicts at \(\tau\) from the graph strictly before \(\tau\).



### Analysis

The current decoder retrieves memory by node pair without a query-time filter; positive-batch prediction then updates that memory. Consider two events for pair \((1,2)\), both at timestamp \(1\), in successive batches with initially empty memory. Set the current one-dimensional edge embedding to \(1\), the historical aggregation weight to \(1/2\), and the final logit to the stored historical coordinate. The first prediction has logit \(0\), then stores \(1/2\); the next same-time prediction reads logit \(1/2\), yielding probability \(\sigma(1/2)\approx0.6224593312\) rather than \(0.5\). Under the paper’s strict \(G_{<1}\) semantics, neither event is available to the other, so both should read empty historical memory. A strictly later query may legitimately read the first event, and events kept in one batch read the same pre-batch state. These controls isolate the equal-time batch boundary.



### Finding and scope

The current author release still permits this strict-time information mismatch. No current AP change, prediction change count or historical experiment contamination rate was measured. A protocol ordered by timestamp and event index could permit such reads, but would require a different declared information clock.



### Proposed correction

Score an entire timestamp group before insertion, or filter stored events strictly before each query time.

The latest author decoder removed an unused timestamp argument but still has no timestamped memory lookup. Current evaluation updates positive memories after each batch. The existing strict-time-group alternative remains an analytic proposal, not an adopted or benchmark-verified correction.



## Limits

- No author program, data scanner or old verifier was executed in this pass. The memory counterexample is derived directly from the current functions; previously reported dataset trigger counts were not freshly replayed and are not used as current performance evidence. The Pareto conclusion is explicitly conditional on the distribution convention.
