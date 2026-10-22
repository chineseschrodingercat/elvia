# Semi-off-Policy Reinforcement Learning for Vision-Language Slow-Thinking Reasoning



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Reward-support construction does not establish near-unit importance ratios, and the scalar comparison does not justify the ratio-free policy gradient. Checkpoint reuse of evaluation scores has a separate selection interpretation.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Reward support does not imply ratio closeness

Assessment: supported; impact: minor



Source: Current arXiv v2 Appendix A, PDF p.17, Lemma A.1 and Assumption A.2



### Source claim (paraphrase)

After Lemma A.1, the paper infers Assumption A.2, including \(|\pi_\theta(y)/\mu(y)-1|\leq\delta\), from its rewarded-support construction.



### Analysis

Behavior probabilities \((0.99,0.01)\) and target probabilities \((0.01,0.99)\) have identical positive support. Reward only the shorter correct first output. The rewarded ratio is \(1/99\), with deviation \(98/99\) from one, despite satisfying the support requirement. Caption success or positive support does not impose a numerical ratio bound.



### Finding and scope

The support-to-closeness implication fails. The scalar lemma remains valid if closeness is supplied separately.



### Proposed correction

Assume or assess ratio closeness independently. With \(|R|\leq1\), that premise gives \(|\mathbb E[(w-1)R]|\leq\delta\), but does not itself control policy-gradient error.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: The ratio-free update can oppose the true return gradient

Assessment: supported; impact: major



Source: Current arXiv v2 Section 4.3, PDF p.5, Eq.(7); Appendix A, PDF pp.17–18, Lemma A.3



### Source claim (paraphrase)

Equation (7) cites a scalar importance-sampling lemma when replacing the weighted policy-gradient expectation by an unweighted one.



### Analysis

Use two equally likely contexts with behavior reward probability \(1/2\). Target reward probabilities are \(p_A=0.505+2\theta\), \(p_B=0.495-1.98\theta\), for \(|\theta|\leq1/400\). All rewarded ratios are within \(0.02\) of one. At zero, the true expected-return derivative is \((2-1.98)/2=1/100\). The ratio-free score expectation is \([2/0.505-1.98/0.495]/4=-1/101\). Thus even the assumed small ratios permit an update opposite to return improvement; equality of scalar objectives at the point does not control their derivatives.



### Finding and scope

The derivation of the core ratio-free return gradient is invalid under the stated assumptions. Empirical usefulness of reward-weighted likelihood is a different claim.



### Proposed correction

Retain importance weights, or state a gradient-specific bound. If rewarded score norm is bounded by \(M\), error is at most \(\delta\mathbb E[|R|\|s\|]\leq\delta M\). Alternatively identify the update as the gradient of a fixed-data reward-weighted log-likelihood objective.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: Selected GRPO checkpoints reuse reported evaluation scores

Assessment: supported; impact: minor



Source: Current arXiv v2 Section 6.2, PDF p.7, checkpoint-selection paragraph; evaluation appendix



### Source claim (paraphrase)

Section 6.2 selects GRPO checkpoints by average MathVision/MMMU Pro performance and then reports those benchmarks; Appendix C identifies the evaluation splits.



### Analysis

Those outcomes are therefore model-selection data for the selected GRPO rows, rather than an untouched final test. The selection rule does not establish training-data overlap, a numerical optimism magnitude or a ranking reversal. SOPHIA-only rows outside that selection are not implicated.



### Finding and scope

The relevant benchmark rows need a selection-aware interpretation. Their reported values are not recalculated.



### Proposed correction

Use a disjoint validation set or a prespecified step, then assess the selected checkpoint on independent test data. Existing checkpoints may permit a new evaluation without retraining.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
