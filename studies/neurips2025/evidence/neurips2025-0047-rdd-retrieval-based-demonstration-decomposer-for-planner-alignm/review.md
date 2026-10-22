# RDD: Retrieval-Based Demonstration Decomposer for Planner Alignment in Long-Horizon Tasks



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The current paper and author release still omit the shortest feasible dynamic-programming prefix, contradicting the stated complete-partition optimum guarantee on a legal four-frame example. A separate Minor concern distinguishes linear scoring calls from the implementation’s quadratic length checks and path copies. Robot success rates are not independently refuted.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: The first feasible prefix is skipped

Assessment: supported; impact: major



Source: Corollary 3.1.1, PDF p. 4; Algorithm 1 and Appendix A.2, pp. 22–23; current rdd/algorithms.py, max_sum_partition and rdd_score



### Source claim (paraphrase)

Under additive interval scores and allowed lengths, Algorithm 1 is said to find an optimal full partition.



### Analysis

Take \(N=4\), minimum length \(2\) and maximum length \(4\). All frame features can equal \((1,0)\); a single two-frame prior interval has duration \(1\), so its endpoint feature matches every candidate. With the author scorer’s default mode, \(\alpha=1\) and \(\beta=0\), angular distance is zero and its score is the negative frame count times \(|1-(e-s)|\). Two-frame segments score \(0\), while the four-frame segment scores \(-8\). The loop begins at \(3\), leaving \(D_2=-\infty\), and hence returns \(-8\) rather than the feasible two-segment optimum \(0\). Interpreting the paper’s outside duration as \(e-s\) instead gives the full segment \(-6\), with the same strict contradiction. If the maximum length is \(3\), the valid two-segment solution is still missed. Invalid-edge scores of \(-\infty\) do not restore the omitted feasible state.



### Finding and scope

The listed algorithm and matching author release fail the stated universal optimum guarantee. Standard additive dynamic programming remains valid; no robot success-rate effect is inferred.



### Proposed correction

Start at the shortest feasible prefix, preserve genuinely infeasible states and backtrack a full partition. The corrected standard recurrence is distinct from a new robot experiment.

The latest target arXiv version and freshly retrieved proceedings Algorithm 1 retain the omitted prefix; the current author repository retains the same loop lower bound. The existing standard-recurrence correction is analytic, with no new robot execution or author adoption established.



## Problem 2: Linear scorer calls do not bound total implementation cost

Assessment: supported; impact: minor



Source: Corollary 3.1.1, PDF p. 4; speed discussion, PDF pp. 8–9; Appendix A.2, PDF p. 23.



### Source claim (paraphrase)

With bounded segment length, the paper counts linear scoring calls and later describes linear algorithm runtime.



### Analysis

With allowed lengths \(2\) through \(4\), the release checks all previous breakpoints before discarding illegal lengths. It makes \(N(N+1)/2+N-5=\Theta(N^2)\) length checks but only \(3N-7\) scorer calls. Full-prefix partition copies add further work. The finite Table 14 budget \(44549/386\simeq115.41\,\mathrm s\) is a valid call-count calculation, not a total asymptotic-runtime proof.



### Finding and scope

The call-count result is preserved; an asymptotic linear total-runtime claim needs restricted candidate loops and path storage assumptions. Finite empirical timings are not refuted.



### Proposed correction

Restrict candidate breakpoints to the valid length band and store predecessor links. With declared interval-access and scoring cost \(C_J\), that gives \(O(NW(1+C_J))\) time for width \(W\).

The current author function still scans every previous breakpoint before checking lengths and copies full partition prefixes. The bounded scoring-call statement remains valid; no new end-to-end timing was measured.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- Local contradictions and specification differences do not establish the magnitude or direction of changes to the published benchmark scores.

- No author contact or adoption; novelty and complete historical-run provenance are unestablished.
