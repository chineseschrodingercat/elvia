# Learning to Flow from Generative Pretext Tasks for Neural Architecture Encoding



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The public GatedGCN option bypasses the intended reverse-edge/configuration branch. The initialization tests also support non-detection, not identical underlying distributions.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: The supported encoder string bypasses GNN preprocessing

Assessment: supported; impact: minor



Source: Appendix A.1 and A.4, PDF pp.14–15; released main.py, lines 57, 91–139 and 149–164



### Source claim (paraphrase)

`main.py` accepts `gatedgcn` in construction and the README, but the reverse-edge/configuration predicate accepts only `gnn` or `gin`.



### Analysis

Therefore `gatedgcn` takes the alternative configuration before constructing GatedGCN. A directed three-node chain retains two edges rather than the required four after reverse augmentation. For NB-301, that branch uses two layers rather than the stated three. No preceding alias conversion repairs this path; GIN and FlowerFormer are consistent-route controls.



### Finding and scope

The documented release command differs from the appendix protocol. Which program produced each original score is unresolved.



### Proposed correction

Use `gatedgcn` consistently in preprocessing, default selection and construction, then specify the historical experiment configuration.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Non-rejection does not establish distributional equality

Assessment: supported; impact: minor



Source: Appendix B.9.1 and Figure 11, PDF p.20



### Source claim (paraphrase)

Appendix B.9.1 and Figure 11 infer the same performance distribution from non-rejecting paired signed-rank tests on nine trials per initialization.



### Analysis

Nine nonzero differences with absolute ranks one through nine and positive rank sum \(25\) give exact two-sided probability \(0.8203125\). That non-rejecting rank/sign pattern has positive probability under a continuous symmetric difference law centered at a nonzero shift. Thus non-rejection cannot establish equality, even under a valid test model. The raw trials and pairing are not reconstructed.



### Finding and scope

The tests did not detect differences in that sample. No actual difference between the paper’s initialization populations is asserted.



### Proposed correction

State non-detection at the nominal \(0.05\) level. A practical-equivalence claim requires a prespecified tolerance, effect estimates and an appropriate uncertainty analysis.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
