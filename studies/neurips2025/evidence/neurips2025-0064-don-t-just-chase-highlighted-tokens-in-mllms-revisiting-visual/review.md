# Don’t Just Chase “Highlighted Tokens” in MLLMs: Revisiting Visual Holistic Context Retention



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The proportional allocator does not inherit a greedy approximation guarantee. Additional semantic-pruning proof and public selection/quota paths need correction, without a demonstrated failure of the reported visual-language results.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Proportional allocation is not the guaranteed greedy algorithm

Assessment: supported; impact: minor



Source: Section 4.1, PDF p.6, Eq.(4); Appendix C, Corollary 1, PDF p.31; proof C.3, PDF p.32



### Source claim (paraphrase)

Appendix C attaches a \(1-1/e\) guarantee to the allocation discussion, whereas Eq.(4) uses proportional crop scores.



### Analysis

For two crops with \(100\) constant-score tokens each, scores \(1\) and \(1/99\) yield quotas \((99,1)\) and log utility \(0\). Feasible quotas \((50,50)\) give \(\log(2500/99)>0\). Thus the claimed positive multiplicative guarantee cannot be attached to that proportional allocation. A separately specified marginal-gain greedy procedure is not refuted.



### Finding and scope

The supporting algorithm-to-guarantee attribution is invalid; empirical usefulness of proportional quotas remains open.



### Proposed correction

For positive sorted scores, initialize one token per crop and allocate remaining feasible tokens by maximal log-prefix marginal gain. Its diminishing marginal sequences justify the appropriate separable allocation argument.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Token coverage does not by itself control pruning normalization

Assessment: supported; impact: minor



Source: Appendix C, PDF p.31, Assumption 1, Lemma C.1, Theorem C.1 and proof C.2



### Source claim (paraphrase)

Appendix C passes from token similarity/coverage assumptions to a transformer-output preservation bound.



### Analysis

With zero queries, attention on \([e_1,e_1,e_2]\) gives \((2/3,1/3)\), while pruning one duplicate gives \((1/2,1/2)\). Perfect coverage of the removed duplicate does not preserve multiplicity or normalization. A fixed-shape Lipschitz argument needs a common lifted representation and a separate deletion bound. The unspecified remainder may absorb this example.



### Finding and scope

A proof bridge is missing; the full numerical theorem is not refuted by this control.



## Problem 3: Selection uses raw attention instead of the computed holistic score

Assessment: supported; impact: minor



Source: Section 4.1, PDF p.6, Eqs.(3)–(5); llava/model/utils.py, lines 22–164



### Source claim (paraphrase)

Equation (5) selects holistic scores; `llava/model/utils.py`, `HoloV`, computes those scores but takes top entries from `patch_attn`. The mean-normalized crop term also largely cancels.



### Analysis

For duplicated \(e_1\) and one \(e_2\), attentions \((0.333,0.333,0.334)\) can rank the \(e_2\) token highest by attention while holistic scores favor \(e_1\). Away from degeneracy, crop normalization makes the diversity contribution nearly a common factor, with rounding boundaries still relevant. Repository issues #13 and #15 already discuss parameter insensitivity.



### Finding and scope

The released path differs from the score definition; historical parameter effects are not newly quantified.



### Proposed correction

Use the intended holistic score for selection and an explicitly defined crop aggregation that does not unintentionally normalize away the desired variation. No recovered benchmark result is established.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 4: Overflow quotas produce padding instead of feasible real tokens

Assessment: supported; impact: minor



Source: Section 4.1, PDF p.6, quota redistribution; llava/model/utils.py, lines 100–157



### Source claim (paraphrase)

Section 4.1 specifies capacity caps and redistribution; the released function floors quotas and later pads short outputs without redistributing overflow.



### Analysis

Two crops of capacity \(2\), weights \((0.98,0.02)\) and budget \(3\) produce nominal quotas \((3,0)\). The path selects only two real tokens and pads a zero, although \((2,1)\) is feasible.



### Finding and scope

The overflow branch violates the stated quota rule. Nonoverflow behavior is unaffected.



### Proposed correction

Cap initial quotas by capacity, then repeatedly allocate remaining tokens to an eligible crop under a declared priority rule until the feasible budget is met.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
