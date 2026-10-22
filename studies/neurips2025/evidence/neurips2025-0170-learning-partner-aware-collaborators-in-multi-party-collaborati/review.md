# Learning “Partner-Aware” Collaborators in Multi-Party Collaboration



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The token-to-response argument changes the discount objective and can reverse the preferred response. The invariance-to-performance proof lacks a linking premise, while released alignment and reward paths have bounded mismatches; solution diversity is not agreement.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Self-counterfactual invariance does not control policy optimality

Assessment: supported; impact: major



Source: Theorem B.4, Eqs.(27)–(32), arXiv v2 PDF p.31



### Source claim (paraphrase)

The proof turns a performance-difference identity into a bound involving direct task error and the difference of two policies’ own factual/counterfactual KL values.



### Analysis

In a one-state self-loop MDP, actions A,B have rewards \(1,0\), discount \(0.9\), and an irrelevant cue changed by the counterfactual prompt. A policy choosing A with probability \(0.1\), and the optimal policy always choosing A, both ignore the cue and have self-counterfactual KL \(0\). Their returns are \(1\) and \(10\). Thus equality of those statistics does not control their return gap. The undefined task-error residual is not silently set to zero: it could absorb the gap, but no calibrated relation establishing that is given. An optimum with divergence merely at most \(\delta\) also leaves residual \(C\delta\) in the limiting argument.



### Finding and scope

The claimed performance step needs an additional operational link to advantage or inter-policy distance. This is an established proof gap, not a numerical refutation made by assigning an undefined residual.



### Proposed correction

For a fixed intervener and bounded rewards, the ordinary performance-difference identity yields \[J(\pi^*)-J(\pi)\le2R_{\max}E_{d^{\pi^*}}\operatorname{TV}(\pi^*,\pi)/(1-\gamma)^2\]. This compares two policies, not each policy with its own counterfactual, and does not establish that the proposed regularizer controls it.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: Strict suboptimality needs a positive expected-advantage condition

Assessment: needs_evidence; impact: minor



Source: Theorem 3.2, PDF p.4; Theorem B.3, PDF pp.29–31



### Source claim (paraphrase)

The strict-loss statement exempts trivial or reward-captured intervention influence but does not define those exceptions or establish a positive total expected advantage.



### Analysis

A generic one-step action-flip kernel with probability \(p=0.1\), reward A=\(1\), B=\(0\), maps intended A probability \(q\) to return \(0.1+0.8q\). It is nonidentity but retains the same optimum \(q=1\), so strict loss is not implied by nonidentity alone. This illustration has an unobserved flip and is not established to match every detail of the paper’s intervention-observed dialogue protocol. A positive term at one state also does not prove a positive occupancy-weighted expectation if negative contributions remain.



### Finding and scope

The quantifiers/exceptions and strict-advantage premise need specification. A full-assumption dialogue counterexample is not established.



### Proposed correction

The weaker statement that an underlying-MDP optimum can become suboptimal is supported. A strict theorem needs an explicit positive discounted expected-advantage condition.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: Token aggregation changes the discounted objective

Assessment: supported; impact: major



Source: Lemma B.2, Eqs.(13)–(16), arXiv v2 PDF pp.28–29



### Source claim (paraphrase)

Both token and macro MDPs are defined using discount \(\gamma\), but the aggregated response reward uses \(\gamma^{(j-1)/L}\).



### Analysis

Use two two-token responses with forced suffix and termination. Set \(\gamma=1/4\), temperature \(\beta=0.1\); A rewards are \((0,1)\), B rewards \((0.3,0)\). The true token values are \(0.25,0.3\), so the soft policy gives A probability \(0.377541\). The printed fractional-power reward instead gives \(0.5,0.3\), giving A probability \(0.880797\). A tabular function class is Bellman complete and all suffix actions are forced, so representability or suffix entropy cannot explain this reversal.



### Finding and scope

The stated token/macro objectives are inequivalent. This does not show that experimental training used the printed fractional exponent.



### Proposed correction

With token discount \(\gamma_t\), aggregate reward is \(\sum_{j=1}^L\gamma_t^{j-1}r_j\) and continuation discount is \(\gamma_t^L\). For fixed lengths one may define \(\gamma_i=\gamma_t^L\); variable lengths require duration-aware continuation and consistent entropy/reference terms.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 4: Padded-row tails are not response-token positions

Assessment: supported; impact: minor



Source: Eq.(4) and response comparison, PDF pp.6–7; ICR_trainer.py, lines 726–787



### Source claim (paraphrase)

The release counts response tokens and takes that many values from the end of right-padded factual/counterfactual rows.



### Analysis

For a short example in a two-row batch, use factual mask \((0,1,1,0,0,0)\) and counterfactual mask \((0,0,0,1,1,0,0,0)\). The same two response tokens have log probabilities \((-0.1,-0.2)\) and \((-1.1,-1.2)\), so their sampled log ratios are \(1,1\), summing to \(2\). Equal final padding values \((-0.4,-0.5)\) make tail subtraction zero instead, with reward scattered to padding positions. An unpadded longer row can agree. Negative sampled log ratios are not themselves an error; their expectation, rather than every sample, is a KL.



### Finding and scope

The supplied path can omit or misplace the intended signal on variable-length right-padded batches. Published-run dependency/import correspondence remains unresolved.



### Proposed correction

Gather values using both valid response masks, verify identical ordered token IDs, compute paired differences and scatter them to factual response positions. Do not truncate unmatched responses.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 5: The supplied task proxy directly rewards participant agreement

Assessment: supported; impact: minor



Source: Appendix D.2, PDF pp.42–43; reward_functions.py, calculate_ppo_deli_proxy_reward



### Source claim (paraphrase)

The text withholds agreement/common-ground reward during training, but the proxy combines \(0.7\) correctness, \(0.2\) agreement and \(0.1\) format.



### Analysis

For cards A,7,B,6, let both participants support A and 7. In the aligned output, both oppose B and are unsure about 6. In the mixed output, participant two swaps its oppose/unsure choices on B and 6. Each retains identical task utility, supplied correctness \(0.416667\), and format \(1\); agreement changes \(1\to0.75\). The source’s scaling then changes reward \(0.83125\to0.68875\), difference \(2.85\cdot0.2\cdot0.25=0.1425\). A single-participant path may make this component inactive, and an imported module is absent from the release.



### Finding and scope

The supplied multi-participant proxy contradicts the stated exclusion. Actual agreement leakage into the published training run is not established.



### Proposed correction

Either remove agreement from the declared task-only reward and evaluate it separately, or disclose explicit agreement training with a matched ablation. No guessed reward rescaling recovers the tables.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 6: Hard-coded A/7 scoring penalizes the paper’s U/9 answer

Assessment: supported; impact: minor



Source: Main Example 1, PDF p.4; Appendix D.2, PDF p.43; calculate_deli_correctness, lines 791–879



### Source claim (paraphrase)

The rule requires inspecting a vowel and an odd-number card, while the valid-JSON scorer uses the literal key set A,7.



### Analysis

For the paper’s U,S,8,9 example, correct stances support U and 9, oppose S and 8. The source treats U/9 as non-key and scores correctness \(-1\), proxy \(-2.332\) with full agreement/format. The wrong all-oppose response gets correctness about \(-0.166667\), proxy \(-0.3895\), hence higher reward. Equivalent correct cards A,K,2,7 get a different positive score. The malformed-JSON category fallback does not repair this valid-JSON path.



### Finding and scope

The supplied helper violates logical-category invariance on an in-paper instance. Canonicalized experimental inputs could avoid it, but no trace establishes that preprocessing; final evaluation’s separate category mapping is not accused of the same bug.



### Proposed correction

Condition on the actual card set/rule and classify vowels or odd numbers as necessary checks. The proposed category-based control restores logical equivalence without establishing a new training reward scale.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 7: Solution-diversity gain does not establish agreement

Assessment: not_issue; impact: minor



Source: Section 6, PDF p.8; Table 1, PDF p.9; evaluator solution-set collection



### Source claim (paraphrase)

DeliData common-ground gain is defined through the number of explored solution types relative to initial types.



### Analysis

If three participants initially all propose V and later propose O,E,C respectively, explored diversity rises from \(1\) to \(4\), giving gain \(3\), while final participants disagree and none selects the correct OV solution. The operational metric remains meaningful for exploration. If the discussion set excludes initial proposals, \(|U|-|I|=|U\setminus I|-|I\setminus U|\) can be negative; it is not the number of newly explored types.



### Finding and scope

This is a metric-scope clarification, not a contradiction in the reported diversity score or an independent measurement of consensus.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
