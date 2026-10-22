# Equilibrium Policy Generalization: A Reinforcement Learning Framework for Cross-Graph Zero-Shot Generalization in Pursuit-Evasion Games



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The public dynamic program’s cost depends on predecessor degrees; equilibrium alone does not ensure finite capture. Evaluation-distribution and sampled-minimum differences need separate interpretation.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Queue uniqueness does not bound predecessor-query work

Assessment: supported; impact: minor



Source: Section 3.2.1, p. 6; Algorithm 1, p. 5; official DP_implementation (2 pursuers).cpp.



### Source claim (paraphrase)

The implementation’s runtime argument counts each state being enqueued once but does not retain its predecessor-neighborhood costs.



### Analysis

On a complete graph with two pursuers and stay actions, all \(n^3\) states are terminal at initialization. Each popped state still inspects \(n\) evader and \(n^2\) pursuer predecessors, yielding order \(n^6\) candidate checks. Unsuccessful scans cost work even when they add no queue entry.



### Finding and scope

The released degree-independent near-linear cost is not established. Bounded-degree behavior or an improved indexed algorithm is not excluded.



### Proposed correction

State dependence on agent count and maximum degree, or supply and analyze the promised implicit neighborhood structure including unsuccessful queries.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Equilibrium existence does not imply finite capture everywhere

Assessment: supported; impact: minor



Source: Section 3.2.1, p. 6, sentence following complexity paragraph.



### Source claim (paraphrase)

The theoretical discussion infers guaranteed finite capture from pure-strategy equilibrium without restricting to a capture-winning region.



### Analysis

Use three isolated vertices with stay actions, distinct starts for two pursuers and one evader. There is only one possible policy pair, hence a pure equilibrium, but capture never occurs. The model does not impose connectedness or a universally winning region.



### Finding and scope

The finite-capture implication is too broad. A value identity with \(\gamma^{\infty}=0\) can remain valid.



### Proposed correction

Restrict finite-capture claims to the finite capture-winning region and state the infinite-rank convention separately.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: Imported and new curves use different test distributions

Assessment: supported; impact: minor



Source: Current arXiv v2 Section 4.3, PDF p.10, Figure 4; Appendix D.2, differing baseline initial-game filters



### Source claim (paraphrase)

Appendix D.2 discloses that the original baseline filtering could not be reproduced and substitutes distance-filtered games for the new evaluation.



### Analysis

The imported and new Figure 4 curves therefore average different initial-game distributions. Differences in average difficulty can affect scores even without a policy change. The disclosed choice is not hidden leakage, and no ranking reversal is established.



### Finding and scope

The figure juxtaposes protocols; it does not isolate a controlled policy effect.



### Proposed correction

Evaluate both methods on shared graph edges, starts, exits, horizon and reward/discount conventions, or state the different-protocol scope explicitly.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 4: A minimum of sampled returns is not a minimum of expected returns

Assessment: supported; impact: minor



Source: Official supplement multi-exit/5vs1-pursuer/test_worker.py run_episode_shortest and stochastic driver.



### Source claim (paraphrase)

The stochastic worker minimizes one realized return per exit, whereas worst-case expected utility is \(\min_e\mathbb E[R_e]\).



### Analysis

In the stated connected five-pursuer, eight-exit example, each exit is captured with probability \(1/8\). Return \(+1\) for capture and \(-1\) otherwise gives worst expected utility \(-3/4\). Independent single draws followed by a minimum instead have expectation \(2(1/8)^8-1\approx-0.99999988\). In general \(\mathbb E[\min_eR_e]\leq\min_e\mathbb E[R_e]\). Deterministic-return evaluation is unaffected.



### Finding and scope

The stochastic release statistic targets a different quantity. No actual published model score is recalculated.



### Proposed correction

Estimate the conditional mean for each exit using repeated returns, then minimize those estimates and quantify finite-sample selection uncertainty.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
