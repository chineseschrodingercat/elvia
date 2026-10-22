# LLM-DAMVC: A Large Language Model Assisted Dynamic Agent for Multi-View Clustering



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Reported clustering accuracy/purity pairs violate their common-prediction ordering, including two proposed-method rows and numerous baselines. The printed rejection softmax retains rejected agents, and the official core detaches both contrastive encoder paths. Correct table values and full training effects remain unresolved.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: Common-prediction accuracy cannot exceed purity

Assessment: supported; impact: major



Source: Tables 1–2; released ClusteringMetrics.calculate_acc and calculate_purity



### Source claim (paraphrase)

The proposed method reports ACC/PUR \((99.67,99.64)\) on BDGP and \((98.66,98.43)\) on Handwritten; numerous baseline pairs also have ACC above purity.



### Analysis

For contingency counts \(C_{kj}\ge0\), each matching term \(C_{k,\pi(k)}\le\max_jC_{kj}\). Summing and maximizing proves \(\mathrm{ACC}\le\mathrm{PUR}\), including unequal class/cluster counts via zero padding. The inequality survives matched nonnegative-weight averaging and separate maxima over the same run collection. Ordinary common rounding preserves it; even independent \(0.005\)-percentage-point errors cannot explain gaps \(0.03\) and \(0.23\). The current metric functions implement these definitions. Different sample/run collections or nonstandard aggregation could explain coexistence only with an explicit different protocol; transcription remains possible.



### Finding and scope

The table cannot currently be read as mutually consistent metrics from common predictions under its stated definitions. The wrong cell or underlying cause is not identified, and no fabrication or corrected true accuracy is inferred.



### Proposed correction

Recover sample IDs, true/predicted labels, run IDs and aggregation weights; compute both metrics on each common prediction vector and regenerate affected tables. The ordering is necessary, not sufficient, for experimental validity.

A proposed correction is described; author adoption is not established.



## Problem 2: Zeroing rejected scores does not exclude their agents

Assessment: supported; impact: minor



Source: Section 3.5, Eqs.(15)–(17); EnhancedAggregator.aggregate, lines 446–489



### Source claim (paraphrase)

A failed confidence threshold sets an agent’s raw score to zero before softmax. Its resulting numerator is \(e^0=1\), so it remains in the mixture.



### Analysis

With \(2\) views, \(2\) samples, \(2\) clusters and threshold \(0.7\), let the only accepted agent predict rows \((0.71,0.29),(0.29,0.71)\); each of three rejected agents predicts \((0.31,0.69),(0.69,0.31)\). Feature norms \(0.01\) give raw scores \((0.0071,0,0,0)\). Softmax assigns total rejected mass approximately \(0.7486663884\); the first fused row is approximately \[(0.4105334446,0.5894665554)\], reversing the accepted decision, with the second reversed symmetrically. All rows are valid positive probabilities. This refutes strict exclusion, while a deliberate softer downweighting interpretation remains legitimate.



### Finding and scope

The printed rule does not implement strict rejection and can let rejected agents determine the result. This is a formula-level witness conditional on a valid routing threshold, without any LLM call or benchmark claim.



### Proposed correction

For nonempty accepted set \(A\), normalize \(w_a=\mathbf1_{a\in A}e^{r_a-r_*}/\sum_{b\in A}e^{r_b-r_*}\). This gives zero rejected weight and unit mass. If all agents fail, explicitly abstain or declare a relaxed-threshold fallback.

A proposed correction is described; author adoption is not established.



## Problem 3: The core detaches both contrastive encoder losses

Assessment: supported; impact: minor



Source: LLM_damvc_core.py, get_features, lines 185–190; compute_loss, lines 813–866



### Source claim (paraphrase)

The trainer obtains all view features through an accessor using no-gradient recording, then constructs feature and frequency contrastive terms exclusively from those returned features.



### Analysis

No recorded derivative connects these features back to encoder parameters. The frequency module’s FFT/amplitude/distance operations have no trainable parameter that recreates that missing edge, so adding either loss to another differentiable term cannot supply its intended encoder derivative. Other direct encoder calls remain differentiable, so this does not disable all training. The historical CPU witness reports finite contrastive losses and restored nonzero gradients under a connected-accessor control; those author-method executions were not rerun in this pass.



### Finding and scope

The archived official core cannot realize the stated encoder optimization from these two terms along the inspected path. Full experiment implementation identity and benchmark effects remain unknown.



### Proposed correction

Use a training accessor with gradient recording enabled for these losses, keeping inference-only suppression separate. Verify optimizer membership and the connected derivative; no full retrained replacement is certified.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.
