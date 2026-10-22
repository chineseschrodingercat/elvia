# Act Only When It Pays: Efficient Reinforcement Learning for LLM Reasoning via Selective Rollouts



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The release can finish adaptive sampling below its effective-batch target and uses mean-threshold histories rather than the written zero-variance streak. Both findings are bounded implementation discrepancies; historical training and efficiency effects are unresolved.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Adaptive refill can exit with too few effective prompts

Assessment: supported; impact: minor



Source: Algorithm 1 and Appendix F; verl/trainer/ppo/ray_trainer.py, lines 1141–1182



### Source claim (paraphrase)

The algorithm promises a full effective batch, but last_sampling bypasses the actual accumulated-count condition after a predicted final refill.



### Analysis

Use the documented \(256\)-prompt target, raw cap \(384\), and \(8\) responses per prompt. A first raw batch yields \(192\) effective groups; the estimated refill is \(1.25(256-192)/(1/2)=160\), setting last_sampling. If that refill yields \(48\), the source exits with \(240<256\) groups. Mixed \(0.1/1\) rewards and constant \(0.1\) rewards realize the effective/ineffective groups. No premise forces identical realized yields across batches. With no effective groups, the code first divides by \(1-\alpha=0\), before its cap can apply.



### Finding and scope

The active release can violate the effective-batch invariant or fail on an admissible zero-yield batch. Historical occurrence and resulting speed/accuracy changes remain unknown.



### Proposed correction

Permit successful exit only when the accumulated count meets the target; explicitly branch on zero yield and use a retry/abort policy. This proves successful-exit correctness, not termination when effective prompts never occur.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Mean-threshold runs differ from zero-variance streaks

Assessment: supported; impact: minor



Source: Equations (3)–(5); presampling_selector.py, easy_probabilistic_skip and hard_probabilistic_skip; ray_trainer.py, lines 1121–1132



### Source claim (paraphrase)

The written retention rule uses the most recent consecutive zero-variance groups. The release stores means, counts separate easy/hard threshold runs and applies a retention floor.



### Analysis

An all-\(1\) group followed by an all-\(0.1\) group has equality streak \(z=2\), hence retention \(0.5^2=0.25\); the hard mean-threshold run counts only the latest group and retains with \(0.5\). A group with four \(0\) and four \(0.1\) rewards has mean \(0.05\), variance \(0.0025>0\), so the written rule retains with \(1\), but the hard branch can retain with only \(0.5\). The rewards are allowed by the released formatting/correctness scheme. Constant same-type streaks agree, and a strictly binary reward domain would avoid the second example; the actual multivalued domain does not.



### Finding and scope

The released pre-filter is a different history statistic, not an implementation of the equality indicator. No claim is made that every skipped prompt would improve future training.



### Proposed correction

Record the equality indicator before reducing groups to means and update the trailing streak by increment/reset; alternatively describe the released threshold runs. Disclose the \(0.01\) retention floor separately from the minimum exploration base.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
