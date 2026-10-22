# Dynamic Masking and Auxiliary Hash Learning for Enhanced Cross-Modal Retrieval



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The chosen cosine margin makes the negative-pair hinge identically zero. A separate ambiguity about the downstream training graph remains unresolved because the actual implementation was unavailable.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: The selected margin disables the negative-pair term

Assessment: supported; impact: minor



Source: Section 2.5, PDF pp.6–7, Eqs.(24)–(28); Section 3.1 parameter setting



### Source claim (paraphrase)

Section 2.5 defines cosine similarities \(S_{ij}\) of normalized nonzero embeddings and negative loss proportional to \(\max(0,S_{ij}-\xi)\). Sections 3.1 and 3.5 select \(\xi=1\).



### Analysis

Cauchy–Schwarz gives \(S_{ij}\leq1\), so every negative hinge is zero whenever \(\xi\geq1\). Collapsed same-direction embeddings and an orthogonal two-class construction can both attain zero for this pairwise subobjective. Thus the selected setting cannot supply the stated negative-pair repulsion.



### Finding and scope

The negative component is inactive as written. This does not establish collapse of an unknown complete training objective or refute the retrieval measurements.



### Proposed correction

A margin \(m<1\) restores a nonempty active region \(S_{ij}>m\). At \(m=0\), two collapsed negative pairs contribute \(2\), while orthogonal negatives contribute \(0\). This only repairs the hinge’s active region.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: The loss-to-hash-parameter connection is underspecified

Assessment: needs_evidence; impact: needs_evidence



Source: Section 2.4, PDF pp.5–6, Eqs.(13)–(23); Section 2.5 loss inputs



### Source claim (paraphrase)

Equations (13)–(23) introduce auxiliary channel weights and hash-probability parameters, whereas Section 2.5 names the earlier mapped features as the loss inputs.



### Analysis

Under the literal upstream-feature reading, the loss does not depend on the separate downstream parameters, and their partial derivatives are zero. If the feature notation instead denotes downstream outputs, or another loss is used, that conclusion need not hold. The implementation needed to choose between these readings is unavailable.



### Finding and scope

Whether the actual auxiliary and hash parameters receive training gradients requires additional evidence.



### Proposed correction

Specify the actual loss inputs, trainable parameter groups and computational graph. No replacement objective or claim that the authors left parameters untrained is established.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
