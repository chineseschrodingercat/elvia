# Bigger, Regularized, Categorical: High-Capacity Value Functions are Efficient Multi-Task Learners



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Reward scaling does not generally supply the claimed bound on true soft returns; an explicit Bellman fixed point exceeds the categorical support. The categorical network's own outputs remain bounded. Evaluation quotas, normalizer implementation and historically reported loader defects are local issues with unknown table impact.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Reward scaling alone does not bound the true soft Q

Assessment: supported; impact: major



Source: Appendix B, p.25; Appendix C.2, pp.26–27, Eqs.2–3.



### Source claim (paraphrase)

Appendix C.2 motivates reward normalization as keeping modeled returns within fixed categorical support.



### Analysis

Consider a self-transition model with continuous state, uniform actions on \([-1,1]\), reward \(1\), \(\gamma=0.99\), \(V_{\max}=10\) and \(\alpha=1/(10\log2)\). Then \(\alpha H=0.1\), the ordinary discounted reward-return bound is \(100\), and the entropy return is \(10\). The printed scale is \(c=1/11\). The soft Bellman equations give \(V=210/11\) and \(Q=2089/110\simeq18.9909>10\). A categorical output remains inside its atoms by construction; the true soft fixed point does not.



### Finding and scope

The stated reward-only normalization does not generally keep the true entropy-regularized Bellman fixed point inside the chosen support. Categorical network outputs remain bounded by their atoms.



### Proposed correction

Bound the complete scaled reward-plus-entropy return under explicit global reward, entropy and temperature conditions. A sampled historical maximum alone is not such a bound.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: Release bootstrap and entropy correction differ

Assessment: supported; impact: minor



Source: jaxrl/normalizer.py:16–30,63–68; brc_learner.py:147; Appendix C.2.



### Source claim (paraphrase)

The paper describes critic bootstrap and empirical task-policy entropy in its normalizer.



### Analysis

The author normalizer bootstraps using mean reward divided by \(1-\gamma\), without a terminal critic input. Its correction is \[-\alpha\,\mathrm{target\_entropy}/[2(1-\gamma)]\], where target_entropy is minus half the action dimension. This is a dimension-derived heuristic, rather than the stated empirical task-policy entropy and terminal-critic recipe.



### Finding and scope

The current release uses a dimension-based heuristic and reward bootstrap, differing from the stated empirical-entropy and critic-bootstrap recipe.



### Proposed correction

Use the specified terminal critic and measured entropy, or document the actual alternate recipe and its run mapping.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: Parallel success counts can exceed task quotas

Assessment: supported; impact: minor



Source: Author envs.py: parallel evaluation episode-completion and success accumulation loop.



### Source claim (paraphrase)

The evaluator reports per-task success rates over requested episode counts.



### Analysis

While awaiting slower parallel environments, the evaluator continues adding successes for a task whose episode quota is already complete. It can therefore produce reported rates \([2,1]\). A success probability cannot exceed one: numerator and denominator are drawn from different episode sets. The frequency and paper-table impact require original episode-duration logs.



### Finding and scope

The current evaluator can count successes outside the episode set in its denominator. The frequency and published-score impact remain unknown.



### Proposed correction

Stop accumulating every metric for a task after its evaluation quota, or divide by the exact number accumulated.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: Checkpoint restoration uses the actor loader for other objects

Assessment: supported; impact: minor



Source: Author jaxrl/agent/brc_learner.py, lines 239-243; jaxrl/utils.py, lines 84-90; repository issue 2, Error in brc_learner.load.



### Source claim (paraphrase)

The release is expected to restore actor, critic, target critic and temperature states by role.



### Analysis

All four restore assignments invoke self.actor.load, whose serialization template and retained identity are those of the actor. Changing only filenames does not make actor, critic and temperature model structures interchangeable. The concern was already reported in repository issue \(2\), Error in brc_learner.load, on 2025-10-10; this is historical reproduction, not a new priority claim.



### Finding and scope

Current restore calls use the actor template for other model roles, retaining the known public restoration defect.



### Proposed correction

Call each role object’s own loader. Current issue/commit records do not establish author adoption of this correction.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- No new author-code execution, model spending, training, author contact or complete benchmark replication.

- Historical numerical results are retained evidence rather than current reruns.

- Local counterexamples do not invalidate every empirical result; missing historical run attribution remains unresolved.
