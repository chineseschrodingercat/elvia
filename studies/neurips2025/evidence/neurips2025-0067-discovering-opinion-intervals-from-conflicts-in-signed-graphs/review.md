# Discovering Opinion Intervals from Conflicts in Signed Graphs



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The public affinity cache can return a nonmaximal label, and the linear-time pseudocode omits exact whole-graph candidate scoring. The original conjecture was explicitly conjectural and has known author follow-up refutation.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: A stale runner-up can produce a nonmaximal assignment

Assessment: supported; impact: minor



Source: Algorithm 1, PDF p.7, line 7; pinned heuristics/src/gaic.rs, affinity/favorite updates



### Source claim (paraphrase)

Algorithm 1 requires a maximum-agreement label. In `heuristics/src/gaic.rs`, the runner-up state is updated only when the favorite changes.



### Analysis

After affinities become \((1,5,4)\), the cached runner-up can remain label zero. Removing two neighbors of the favorite gives \((1,3,4)\), without triggering the required rescan. Zero-temperature selection can therefore return agreement \(3\) despite an available value \(4\). This is a state-invariant failure, not a statement about every clustering run.



### Finding and scope

The released update can violate the maximizing assignment rule. Its frequency and benchmark impact are unknown.



### Proposed correction

Rescan favorites after decreases, using the existing complete affinity scan and its declared tie convention. A more selective cache update needs an equivalent maintained invariant.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Exact candidate scoring has an omitted quadratic cost

Assessment: supported; impact: minor



Source: Theorem 2.3, PDF p.6; Proposition B.1, PDF p.21; Algorithm 2, PDF p.22, line 11



### Source claim (paraphrase)

Theorem 2.3 states linear dependence on graph order for fixed approximation parameters; Algorithm 2 compares exact full-graph candidate agreement scores.



### Analysis

Two candidates such as balanced two-part and all-one assignments can differ on \(\Theta(n^2)\) edge signs. Exact comparison over arbitrary signed input requires accounting for those cross edges. Counting only sampled assignment work omits the pseudocode’s full scoring step. Approximate sampled ranking can support a separately specified randomized procedure.



### Finding and scope

The stated exact-scoring pseudocode is not justified by the linear runtime accounting. This does not prove that no linear-time PTAS exists.



### Proposed correction

Include the exact scoring cost, or explicitly sample candidate scores with an error budget compatible with the approximation proof and declared random-access input model.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: The conjecture has known subsequent author refutation

Assessment: not_issue; impact: no_issue_found



Source: The original three-quarter conjecture; authors’ MLG 2026 follow-up, Theorem 3



### Source claim (paraphrase)

The original \(3/4\) guarantee is labeled a conjecture; the authors’ MLG 2026 follow-up Theorem 3 refutes it.



### Analysis

For \(n=256\), random independent edge signs give a finite existence argument: there are at most \((2n)^{2n}\) interval-overlap patterns, while each fixed pattern’s chance of agreement above the target is bounded by \(\exp(-\binom n2/8)\). Their product is below one. This is a probabilistic existence argument, not an enumerated optimum or new discovery.

The elementary universal guarantee is \(|E|/2\): the better of all-overlapping and pairwise-disjoint interval assignments satisfies at least half the signed edges. The author follow-up limits a larger uniform constant in its stated asymptotic setting. This contextualizes known subsequent progress; it is not a repair of a falsely proved theorem.



### Finding and scope

A conjecture can be disproved by later work without constituting a false proof in the original paper. Historical attribution remains with the authors.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
