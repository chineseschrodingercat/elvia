# A Reinforcement Learning-based Bidding Strategy for Data Consumers in Auction-based Federated Learning



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The written online moments do not preserve the single-component fixed point. The common-scale bidding and unimodality arguments require restrictions absent from the finite partially observed auction setting.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: The online moment update does not preserve a constant observation

Assessment: supported; impact: minor



Source: Section 4.2, PDF p.6, Eqs.(10)–(13); experimental step size, PDF p.8



### Source claim (paraphrase)

Equation (13) writes \(\mu_k^+=\mu_k+\kappa w_ks\) and an unforgotten covariance increment, rather than normalized sufficient-statistic updates.



### Analysis

For one component, responsibility \(1\), \(\kappa=1/2\), and incoming state equal to current mean \(s=(4,1,0.6)\), the formula returns \(3s/2\) instead of \(s\). The utility coordinate is admissible under the stated reputation counts. A constant observation should not move its equal component mean away.



### Finding and scope

The displayed recursion is not the stated normalized online moment operation. The historical implementation is unknown.



### Proposed correction

Maintain mass \(N\), first moment \(M\) and raw second moment \(R\), each updated by the same forgetting factor and responsibility. Recover \(\mu=M/N\) and \(\Sigma=R/N-\mu\mu^\top\).

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: One common bid scale does not solve every finite hard-budget problem

Assessment: supported; impact: minor



Source: Section 3, PDF p.3, Eqs.(1)–(2); Section 4.3, PDF p.6



### Source claim (paraphrase)

Section 3 motivates bids \(b_i=v_i/\omega\) from a finite binary budget problem and discusses a common optimal scale.



### Analysis

With budget \(8\) and utility/price pairs \((0.6,4)\), \((0.9,7)\), the optimum skips the first and wins the second. Winning the second with one scale needs \(\omega<9/70\), which also wins the first and leaves insufficient budget. Skipping the first requires \(\omega\geq3/20\). The strict gap precludes the desired common-scale decision.



### Finding and scope

Exact finite optimality does not follow. Adaptive per-auction scales and relaxed pacing remain valid possibilities.



### Proposed correction

Interpret a common shadow price as a Lagrangian or fractional/expected-budget rule, with explicit assumptions. Do not equate that relaxation with every sequential binary optimum.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: Nonunimodal action values need not indicate estimation error

Assessment: supported; impact: minor



Source: Section 4.3, PDF p.6, action-value unimodality paragraph before Algorithm 1



### Source claim (paraphrase)

Section 4.3 treats action-value nonunimodality as abnormal estimation in a partially observed market.



### Analysis

Use two auctions, budget \(4\), discount \(1\), utilities \((3/5,9/10)\), and three equally likely hidden regimes with price pairs \((1,5),(2,3),(3,5)\). All initial observations agree. At first bids \((1/2,3/2,5/2,7/2)\), the exact optimal expected utilities are \((0.3,0.5,0.4,0.6)\). The first bid loses all regimes, leaving only the second regime’s affordable future reward \(0.9/3=0.3\). The second bid earns \(0.6\) in regime one and can still earn \(0.9\) in regime two, totaling \(0.5\). The third bid wins the first two regimes but leaves insufficient budget for their later prices, totaling \(0.4\). The fourth wins all first auctions and no later one, giving \(0.6\). These bids and needed continuations are available under initial scale \(1\), rule \(b=v/\omega\), and finite multiplicative rates \[\{-29/35,-13/16,-19/25,-3/5,-7/16,1/5,5\}\], all greater than \(-1\). Competitor prices can exceed the target budget. Current win/loss information and budget affect continuation value, so nonunimodality occurs without value-estimation error.



### Finding and scope

A unimodality check is a heuristic diagnostic under the stated general market, not a universal test of value accuracy.



### Proposed correction

State extra market/continuation restrictions before asserting a shape theorem. Preserve the nonunimodal control when using the heuristic.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
