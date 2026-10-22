# No-Regret Online Autobidding Algorithms in First-price Auctions



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



A one-atom auction refutes the all-strategy auxiliary-CDF theorem, while an ordered value sequence refutes the appendix’s pathwise regret claim. A separate false dual inequality admits a local repair.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: One auxiliary CDF cannot represent every randomized tradeoff

Assessment: supported; impact: major



Source: Theorem 3.1, proceedings PDF p.6; Lemma A.3, full arXiv PDF pp.16–18



### Source claim (paraphrase)

The theorem asserts a single CDF \(F_{\rm conv}\) that gives two-way reward/payment dominance between every randomized original strategy and a deterministic auxiliary strategy, for any competing-bid distribution.



### Analysis

Take one round, value \(1\), and competing bid exactly \(a=1/2\), with ties won. Randomizing between bids \(a\) and zero with probability \(q\) yields reward/payment \((q,aq)\), and every original strategy obeys \(P\geq aR\). Reverse dominance implies any auxiliary bid with positive allocation \(s\) must have \(b\geq a\). Forward dominance of the mixture requires \(s\geq q\) and \(bs\leq aq\). Thus \(aq\geq bs\geq as\geq aq\), forcing \(b=a,s=q\). The same CDF would need \(F_{\rm conv}(a)=1/4\) and \(F_{\rm conv}(a)=1/2\), impossible. Atomic distributions and favorable tie-breaking are explicitly admitted.



### Finding and scope

The all-strategy equivalence theorem fails on its stated domain. This undermines the stated deterministic-reduction justification, while leaving open weaker optimization-specific alternatives.



### Proposed correction

Keep the convex set of payment/allocation pairs. On a finite bid menu, randomized bids give exactly its convex hull and each upper boundary edge can be implemented by mixing its two endpoints. A per-round Lagrangian can instead optimize directly under the original CDF.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Fixed-sequence regret and stage comparator claims fail

Assessment: supported; impact: major



Source: Lemma B.2, full arXiv PDF pp.23–24; Lemma B.5, p.27; Proposition 3.2, proceedings p.7



### Source claim (paraphrase)

The appendix upgrades an i.i.d. expected-regret bound to every fixed value sequence, and substitutes a global offline comparator for separately ROI-feasible stage optima.



### Analysis

Let even \(T\), \(F^\dagger=F=\delta_{1/2}\), and \(\varepsilon=0\). Values are \(6/25\) for the first half and \(19/25\) for the second. Starting at \(\lambda=1\), winning a low round has Lagrangian value \(-1/50\), so the algorithm loses with zero update. Every high round has positive value \(19/25+13\lambda/50\), so all are won. Algorithm reward is \(19T/50\); the globally ROI-feasible all-win policy has reward/payment \(T/2\), giving regret \(3T/25\). Stage-feasible low-round reward is zero, so summing stage optima gives only \(19T/50\), below the global optimum. This is the reverse of the needed comparator replacement.



### Finding and scope

The fixed-sequence lemma is false and the stage pooling argument does not prove the global benchmark. This ordered event can be rare under i.i.d. values and therefore does not by itself refute the main expected-regret result.



### Proposed correction

Preserve expectation over i.i.d. values and compare all stages to one common stationary dual benchmark. The proposed direct-CDF argument recovers expected orders under its stated feedback assumptions, rather than a pathwise claim.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: One-step dual inequality fails for an admissible auction

Assessment: supported; impact: minor



Source: Appendix A.2, full arXiv PDF p.22, after Eq.(11)



### Source claim (paraphrase)

The proof asserts \(\alpha\lambda_tg_t\leq2(\lambda_t-\lambda_{t+1})+2\alpha^2\), with \(\lambda_{t+1}=\lambda_te^{-\alpha g_t}\).



### Analysis

Use \(T=100,\alpha=1/10,\lambda_1=1,F=\delta_1,v_1=51/100\). Bidding \(1\) is the strict best response since its Lagrangian value is \(1/50>0\); thus \(g_1=-49/100\) and \(\lambda_2=e^{49/1000}\). The left side is \(-0.049\), but the right side is at most \(-0.078\) by \(e^x\geq1+x\). Multiplying a negative difference by \(2\) cannot supply the claimed larger upper bound.



### Finding and scope

The printed intermediate inequality is false. Its intended dual-sum order has a local replacement, so this defect alone does not refute the final expected-regret rate.



### Proposed correction

Under \(0<\alpha\leq1,|g|\leq1,\lambda g\geq-1\), use \(\alpha\lambda g\leq(1+\alpha)(\lambda-\lambda e^{-\alpha g})+3\alpha^2\). Splitting by the sign of \(g\) proves the bound; telescoping gives \(\sum_t\lambda_tg_t\leq5\sqrt T\).

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
