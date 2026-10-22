# Prompt Tuning Decision Transformers with Structured and Scalable Bandits



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The conditional regret decomposition remains valid. Its application to fixed exploration needs additional assumptions, while the released interaction diagnostic and auxiliary UCB reset/anchor operations have concrete local mismatches.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Fixed exploration need not satisfy the conditional slot-regret premise

Assessment: not_issue; impact: minor



Source: Theorem 4.1 and Corollary 4.2, PDF p.6; Table 4, PDF p.15



### Source claim (paraphrase)

The theorem assumes slot regret and proves \(R(K)\le J^{-1}\sum_jR_j(K)+2K\varepsilon\); its sublinear corollary requires a further sublinear slot bound.



### Analysis

The decomposition follows directly by subtracting the additive rewards and bounding the two interaction terms by \(2\varepsilon\). With one slot, rewards \(1,0\), exact reward estimates and uniform exploration probability \(0.1\), even an oracle selector chooses the bad arm with probability \(0.05\), giving expected regret \(0.05K\). Thus that implementation need not satisfy the added sublinear premise. Positive fixed interaction bound also permits a linear term.



### Finding and scope

The conditional theorem is valid; practical application requires a separate feedback/exploration analysis. This is a scope clarification rather than a refutation.



## Problem 2: Observed noisy MAE is not a uniform interaction bound

Assessment: supported; impact: minor



Source: Section 5.3, PDF pp.9–10; regret_experiment.py, synthetic_reward and compute_interaction_term



### Source claim (paraphrase)

Figure 4’s interaction diagnostic is used to support \(\sup_\rho|h(\rho)|\le\varepsilon\).



### Analysis

The source computes mean absolute error of final slot models on observed noisy rewards. With two binary slots, target \((1,1)\), additive mean rewards \((1,1/2,1/2,0)\) and zero models, a record containing only \((2,2)\) has residual \(0\) while the maximum over all four actions is \(1\). A near-zero Gaussian noise observation gives an approximate version with positive probability. Conversely perfect additive models with \(h=0\) still have expected absolute residual \(0.05\sqrt{2/\pi}\approx0.0398942\).



### Finding and scope

The statistic mixes model error, noise and visited actions; it does not estimate the stated uniform structural quantity.



### Proposed correction

Describe it as observed mean absolute prediction residual. Keep noiseless additivity, noise and held-out/uniform residual checks distinct.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: Aliased reset snapshots and a differentiable anchor defeat their intended operations

Assessment: supported; impact: minor



Source: bandits.py, snapshot creation/reset and UCB initial-anchor construction, especially lines 292–304,404,416–418



### Source claim (paraphrase)

Reset dictionaries are saved without cloning, and the purported fixed initialization anchor retains an autograd path to the same parameter leaves.



### Analysis

A state dictionary’s tensors share parameter storage, so changing a parameter by \(0.25\) also changes its saved reset tensor; reloading that alias cannot restore initialization. Separately, let \(c(\theta)\) concatenate parameters and store its initial numerical vector without detaching. For \(\lambda\|c(\theta)-c(\theta_{\rm initial})\|^2\), backward differentiates both paths to the same leaves, yielding factor \(I-I=0\), even when its numerical value is positive. These are storage and chain-rule consequences; no model execution is required here.



### Finding and scope

The inspected auxiliary classes do not implement their stated reset/constant-anchor semantics. The effect on published rankings and other environment implementations remains unmeasured.



### Proposed correction

Deep-copy the reset state and detach/clone the anchor; define optimizer-state reset separately. These restore the local operations, not a complete UCB theorem.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
