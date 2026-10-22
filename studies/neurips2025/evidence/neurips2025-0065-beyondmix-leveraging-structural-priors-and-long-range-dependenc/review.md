# BeyondMix: Leveraging Structural Priors and Long-Range Dependencies for Domain-Invariant LiDAR Segmentation



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Cross-domain receptive fields are neither universally necessary nor, by the stated proof alone, sufficient for invariant useful features. These limitations concern the supporting distributional argument rather than the empirical segmentation method.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: A local feature can remain invariant and useful under both shifts

Assessment: supported; impact: minor



Source: Appendix A, PDF p.21, reverse proposition, Eqs.(18)–(20); Section 1, PDF p.3



### Source claim (paraphrase)

Appendix A’s reverse implication rules out effective invariant features without a receptive field spanning both domains.



### Analysis

Let \(X=(U,A)\), with balanced \(U\), nuisance probabilities \(P_s(A=1)=1/4\), \(P_t(A=1)=3/4\), and \(P_s(Y=U\mid A)=0.95-0.20A\), \(P_t(Y=U\mid A)=0.75+0.20A\). Both raw and conditional laws shift. Yet the local feature \(f(X)=U\) has identical balanced domain laws, zero domain information and zero population MMD; its Bayes classification accuracy is \(0.90\) in each domain.



### Finding and scope

The universal necessity implication fails. The usefulness of larger receptive fields on the evaluated data remains possible.



### Proposed correction

State a distribution-, hypothesis-class- and optimization-dependent claim rather than universal necessity. No change to the empirical method follows from this scope correction.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Mixed-input gradients do not follow from the displayed weighted objective

Assessment: supported; impact: minor



Source: Appendix A, PDF p.21, forward argument, Eqs.(15)–(17)



### Source claim (paraphrase)

Appendix A’s forward argument identifies a mixed-input gradient with a weighted source/alignment gradient and then asserts near-zero domain information.



### Analysis

For inputs \(x_s=1\), \(x_t=3\), mixture weight \(1/2\) and a logistic linear feature at parameter zero, the mixed supervised gradient is \(-1\), while the displayed weighted gradient is \(-1/4\). If Eq.(16) defines a weighted objective instead, the algebra is valid but concerns another object. Equation (17) additionally assumes the near-equality \(H(D\mid Z)\approx H(D)\) needed for invariance.



### Finding and scope

The written argument does not establish sufficiency for the actual learning process. It does not prove that a specific optimizer fails.



### Proposed correction

Specify the mixing, labels, feature class, loss and optimization conclusion. Under a characteristic kernel, zero population MMD implies equal feature laws, but receptive-field coverage alone does not establish that premise.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
