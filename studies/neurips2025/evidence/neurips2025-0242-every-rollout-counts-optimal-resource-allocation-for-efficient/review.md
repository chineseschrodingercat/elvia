# Every Rollout Counts: Optimal Resource Allocation for Efficient Test-Time Scaling



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Exact Beta and embedding examples defeat the theoretical bridge to optimal success allocation and the claimed exact direction recovery. Independent rounding and released pre-pruning add finite-budget discrepancies; empirical search results are not remeasured.



## Scope

Rapid claim-focused reading of current author-paper passages and relevant released source. Direct mathematical or static-source reasoning is stated below. No author program, inherited verifier, model inference or benchmark was executed.



## Problem 1: A log-utility calculation does not prove the advertised success optimum

Assessment: supported; impact: major



Source: Proceedings Eq.(7), PDF p.4; Proposition 2, p.6; Theorem 1, p.7; Appendix B.2, p.17



### Source claim (paraphrase)

The paper’s independent Beta model minimizes failure \(F(B)=\prod_i\prod_{r=0}^{B_i-1}[\kappa(1-w_i)+r]/(\kappa+r)\), but its proportional-allocation justification switches to weighted logarithmic utility.



### Analysis

For \(k=2,N=3,\kappa=10,w=(2/3,1/3)\), proportional allocation \((2,1)\) has success \(271/297\), while \((3,0)\) has \(839/891\), an improvement of \(26/891\). This disproves unrestricted finite-concentration optimality, separately from the stated low-confidence regime.

In that regime, take \(k=N=2,w=(9/10,1/10),\kappa=1/100\). Nearest-rounded proportional counts \((2,0)\) give success \(9099/10100\); coverage \((1,1)\) gives \(91/100\), greater by \(92/10100\). As \(\kappa\downarrow0\), these tend to \(0.90\) and \(0.91\). Proper Beta laws and allowed quality scores realize both examples.

The limit rewards covering distinct candidates; if \(N\geq k\), any integer allocation covering all candidates can be optimal. By contrast, \(\sum_jQ_j\log B_j\) genuinely has proportional optimizer, and its KL gap is correct for that utility. No identity turns that gap into a success-probability comparison.



### Finding and scope

The central Bayesian-optimality bridge and success interpretation are unsupported; the log-utility result and empirical DORA comparisons remain distinct.



### Proposed correction

The existing exact integer optimizer repeatedly chooses a coordinate maximizing \(w_i/(\kappa+B_i)\). Each next rollout reduces log failure by \(-\log[1-\kappa w_i/(\kappa+B_i)]\); these marginal gains decrease along each coordinate, so greedy selection of the largest remaining prefix gain is optimal. This is a result for the independent Beta model, not evidence that actual LLM rollouts obey it.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Problem 2: Finite-temperature affinity does not exactly cancel direction multiplicity

Assessment: supported; impact: major



Source: Proceedings Theorem 1, PDF p.7; Eqs.(10)–(12), pp.6–7; Appendix B.3, pp.17–18



### Source claim (paraphrase)

Theorem 1 claims exact recovery of direction-level allocation from the affinity diagonal when scores are equal within each direction, without a separation assumption.



### Analysis

Use unit embeddings \(e_1=e_2=(1,0)\), \(e_3=(0.99,\sqrt{1-0.99^2})\), zero quality scores and \(T_s=0.01\). Write \(a=e\). Row-softmax diagonals are \(a/(2a+1),a/(2a+1),a/(a+2)\). The normalized total masses are \[W_A=\frac{2(a+2)}{4a+5},\qquad W_B=\frac{2a+1}{4a+5}.\] Equal direction scores require \((1/2,1/2)\), but \(W_A-1/2=3/[2(4a+5)]>0\). The contradiction occurs before rounding.

Actual inverse cluster sizes arise only under extra conditions, such as identical within-cluster embeddings and a zero-temperature limit with strict cross-cluster separation. Finite positive cross-affinities prevent exact inverse-size cancellation in general.



### Finding and scope

The exact recovery theorem fails under its written assumptions; the heuristic may still improve real search.



### Proposed correction

The supplied restricted result assumes uniqueness weights \(\gamma_i=c/k_j\) within direction \(j\), with a common \(c>0\). Summing quality–uniqueness products then cancels \(k_j\) exactly. A soft approximation requires a quantitative separation/error bound.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Problem 3: Independent rounding and quality pre-pruning change the finite allocation

Assessment: supported; impact: minor



Source: Proceedings Eq.(13), PDF p.7; current author scripts/sal/search/dora.py, allocation lines 290–310 and next-iteration beam construction



### Source claim (paraphrase)

The fixed rollout constraint is \(\sum_iB_i=N\), but the displayed rule rounds each normalized allocation independently. The release also removes zero quality-rounded candidates before diversity weighting.



### Analysis

Weights \((0.4,0.4,0.2)\) and \(N=4\) give rounded counts \((2,2,1)\), totaling \(5\). They are realized by orthogonal embeddings and quality scores \((\log2,\log2,0)\). Later truncating a repeated beam list restores its length but makes the allocation depend on order.

With three identical direction-A embeddings and one orthogonal direction-B embedding, quality weights \((0.3,0.3,0.3,0.1)\) round at budget \(4\) to \((1,1,1,0)\), discarding B before uniqueness. Applying quality and inverse-size diversity together instead yields roughly equal final weights and \((1,1,1,1)\). The current source has the quality-only pruning stage; no full author search was run.



### Finding and scope

The displayed/released finite allocation differs from the constrained rule; effects on published model-search accuracy are unmeasured.



### Proposed correction

For a proportional heuristic, compute all intended weights first and use floor counts plus largest fractional remainders under a declared tie rule to preserve the budget. That restores feasibility, not optimal success; the Beta optimizer is a separate correction.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- Exact calculations and static-source findings do not remeasure published experiments or establish the historical experiment-generating revision.
