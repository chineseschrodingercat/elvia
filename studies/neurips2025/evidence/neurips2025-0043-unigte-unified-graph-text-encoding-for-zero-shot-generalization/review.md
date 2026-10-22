# UniGTE: Unified Graph–Text Encoding for Zero-Shot Generalization across Graph Tasks and Domains



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Choosing one tied shortest path by node-index order can make heterogeneous edge bias depend on node numbering. This invalidates an unconditional architectural permutation guarantee; it does not measure failures of the published checkpoint.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Index-dependent shortest-path ties break edge-bias equivariance

Assessment: supported; impact: major



Source: Section 2.2.2, Eq. (4) and complete-attention invariance statement, PDF pp. 4–5; author modeling/ft_datasets/algos.pyx, floyd_warshall, lines 9–55.



### Source claim (paraphrase)

The full graph attention is described as permutation invariant, with edge scores averaged over a selected shortest path.



### Analysis

Use a diamond graph with paths \(0\to1\to3\) and \(0\to2\to3\), both of length two. Give the first path edge bias zero and the second bias two. The author's Floyd-Warshall implementation updates only on strict distance improvements and processes intermediate indices in order, so it selects the first path. Swapping nodes \(1,2\) and all their attributes while fixing endpoints \(0,3\) switches the chosen bias: \(B_{03}=0\), \(B'_{03}=2\), although equivariance requires \(B'=PBP^\top\) and equality at those fixed endpoints. Distance bias itself remains equivariant; the selected heterogeneous edge bias does not.



### Finding and scope

The unconditional edge-bias equivariance guarantee needs a path-tie condition or invariant aggregation. Unique paths/equal path scores remain unaffected; no checkpoint-specific failure rate or reachability claim is established.



### Proposed correction

Aggregate shortest-path edge information equivariantly, or state the unique-path/equal-score restriction. This changes the definition and is not a verified trained-model repair.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- Local contradictions and specification differences do not establish the magnitude or direction of changes to the published benchmark scores.

- No author contact or adoption; novelty and complete historical-run provenance are unestablished.
