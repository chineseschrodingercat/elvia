# From Replication to Redesign: Exploring Pairwise Comparisons for LLM-Based Peer Review



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The unregularized Bradley–Terry likelihood need not identify cross-component ranks or attain a finite maximum. These limitations are especially relevant to sparse-comparison interpretation, without showing wrong reported rankings.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Disconnected components do not identify a global ranking

Assessment: supported; impact: minor



Source: Sections 3.1–3.2, p. 4, Eq. (2); Section 4.2, p. 6.



### Source claim (paraphrase)

The stated pairwise likelihood estimates a global paper ranking without an explicit connected-component completion rule.



### Analysis

Two balanced-win components \(\{1,2\}\), \(\{3,4\}\) have centered equally maximizing scores \((c,c,-c,-c)\) for every \(c\). Component offsets, and hence cross-component order, are unidentified. With \(7158\) papers and \(1000\) pairwise comparisons, at most \(2000\) papers appear, leaving at least \(5158\) untouched.



### Finding and scope

The likelihood alone does not uniquely determine all global ranks in the allowed sparse regime. A regularizer or completion rule adds information.



### Proposed correction

State graph connectivity, completion/tie rules and any prior or penalty. Restrict unregularized interpretation to identifiable score differences.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Connected comparisons need not have a finite maximum

Assessment: supported; impact: minor



Source: Section 3.2, p. 4, Eq. (2) over real-valued coefficients.



### Source claim (paraphrase)

Connectivity alone is sometimes read as sufficient for finite unregularized score estimation.



### Analysis

For two papers with one observed win, the comparison graph is connected and centered log likelihood is \(\log\sigma(t)\), where \(t\) is their score difference. It increases toward zero as \(t\to\infty\), so no finite maximum is attained. The pairwise ordering itself is still supported.



### Finding and scope

A finite estimate requires stronger conditions or a different explicit estimator.



### Proposed correction

A declared positive ridge penalty makes the logistic objective coercive and strictly convex, supplying a unique finite penalized estimate. This is distinct from the unregularized likelihood.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
