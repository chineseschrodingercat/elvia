# Fairshare Data Pricing via Data Valuation for Large Language Models



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The flat-price formula misses replacement expenditure and complementary bundles. The dynamic fair-price guarantee uses insufficient unconditional control, its uniform finite crossover has false quantifiers, and royalty endpoint candidates omit internal bundle switches.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: The flat-price threshold excludes valid purchases

Assessment: supported; impact: major



Source: Eq.(9), Lemma 2, repeated Eq.(36); Algorithm 1



### Source claim (paraphrase)

The formula uses budget remaining after the old optimum and excludes old negative-surplus bundles, although replacement frees spending and complementarity can rescue such bundles.



### Analysis

With budget \(1\), old price \(p_A=1\) and utilities \((0,2,3,3)\) for \((\varnothing,A,B,AB)\), old optimum \(A\) exhausts budget, giving printed new threshold zero. Yet at \(p_B=1\), \(B\) uniquely wins with surplus \(2\). Separately, budget \(4\), \(p_A=2\), utilities \((0,1,1/2,5)\) exclude old \(A\), giving threshold \(1/2\), while \(AB\) uniquely wins at \(p_B=2\). A second buyer with budget \(2\), utilities \((0,3,0,3)\), makes old price \(2\) revenue-optimal. Creation costs \(1/4\) allow positive profits, so nonoptimal old sellers do not explain the examples.



### Finding and scope

The closed-form demand threshold and price-candidate set fail in the permitted nonadditive model; empirical prices are not recomputed.



### Proposed correction

For all affordable old bundles \(\mathcal A\), let \(G_0=\max_{S\in\mathcal A}[u(S)-c(S)]\) and \[\tau=\max\{0,\max_{S\in\mathcal A}\min[b-c(S),u(S\cup\{j\})-c(S)-G_0]\}.\] A positive price qualifies exactly up to this threshold when a new-containing maximizing bundle is accepted at ties. Seller endpoint attainment needs explicit tie handling.

A proposed correction is described; author adoption is not established.



## Problem 2: Unconditional surplus does not bound conditional continuation

Assessment: supported; impact: major



Source: Assumption 2, Eq.(7); Bellman Eq.(8); argument around Eq.(29)



### Source claim (paraphrase)

A state-conditional continuation value is bounded using an unconditional surplus mean without temporal independence or uniform conditional assumptions.



### Analysis

Draw persistent observed states \(H,L\) equally. Set budget/fair price \(1\), utilities \(2,11/10\), participation \(\pi(p,1)=p\), sensitivity \(1\) and discount \(3/4\). Unconditional fair surplus \(11/20\) gives required discount \(20/31\), satisfied strictly. In low state fair value is \(2/5\), while half-price value is \((3/5)/(1-3/8)=24/25\). The contingent policy improves ex-ante value from \(11/5\) to \(62/25\). All offered prices exceed creation cost \(1/4\).



### Finding and scope

Fair payment need not be optimal under the displayed stochastic assumptions. Independence or uniform conditional continuation control would be substantive additions.



### Proposed correction

Require every reachable fair continuation value to be at least \(m/(1-\delta)\), with payment-independent exogenous transitions. Then \(\delta Lm/(1-\delta)\ge1\) makes fair payment a Bellman maximizer. The low state requires \(\delta\ge10/11\), excluding this example.

A proposed correction is described; author adoption is not established.



## Problem 3: A uniform finite crossover does not follow

Assessment: supported; impact: major



Source: Lemmas 3–4 and strict eventual-inferiority/uniform-threshold proof



### Source claim (paraphrase)

The weak discount condition is used to infer strict eventual loss for underpayment and one finite horizon covering every underpaying schedule.



### Analysis

With utility \(2\), fair price/budget \(1\), \(\pi(p,1)=p\) and permitted discount \(1/2\), every constant \(p\in[0,1]\) has infinite value \(2\). At finite \(T\), underpayment value \(2[1-(p/2)^{T+1}]\) exceeds fair value \(2[1-2^{-(T+1)}]\). Weak optimality survives; strict inevitable inferiority does not.

Even at \(\delta=3/4\), fix any horizon \(T\), set \(\varepsilon=\delta^T/[8(T+1)^2]\), pay \(1-\varepsilon\) before \(T\) and \(1/2\) thereafter. Bernoulli’s inequality gives fair-minus-underpayment cumulative value at most \(2\varepsilon(T+1)^2-\delta^T/2=-\delta^T/4<0\). Choosing a schedule for each horizon is allowed by the claimed supremum over schedules; it does not produce one policy that wins forever under a strict margin.



### Finding and scope

Discount equality permits ties at infinity, and the unrestricted schedule family has no uniform finite crossover. Fixed simulated policies may still cross over.



### Proposed correction

Separate non-strict optimality, policy-specific crossover and uniform bounds. Fix the policy before the horizon limit; a uniform bound needs restrictions on the policy family. No original-generality replacement is established.

A proposed correction is described; author adoption is not established.



## Problem 4: Royalty endpoints miss an internal bundle switch

Assessment: supported; impact: major



Source: Royalty Eqs.(15),(19),(21),(44), Lemma 6



### Source claim (paraphrase)

Monotone revenue within one chosen bundle does not prevent a downward revenue jump when the buyer switches between two bundles containing the new dataset.



### Analysis

Use utilities \((0,1,10,12)\), rate budget \(1/2\), old rate \(\alpha_A=1/2\), shares \(f_A=\mathbf1_{A\in S}\min(\alpha_A/5,1/10)\) and \(f_B=\mathbf1_{B\in S}\alpha_B(1+\mathbf1_{A\in S})/10\). They are nonnegative, coordinatewise monotone and total below \(3/10\). Buyer values for \(B,AB\) are \(10-\alpha\), \(54/5-12\alpha/5\), crossing at \(4/7\), always above outside value \(9/10\). A tie choosing \(AB\) gives seller revenue \(12\alpha/5\) through \(4/7\), then \(\alpha\): unique maximum \(48/35\) at \(4/7\). Both proposed suprema are \(1\), missing it; substituting total share in the printed conditions does not remove the switch. The old share is already revenue-maximized and creation costs \(1/20,1/4\) permit profits.



### Finding and scope

The attained feasible interior optimum defeats the general endpoint characterization, beyond any open-endpoint technicality.



### Proposed correction

For finite piecewise-affine shares, partition at every buyer-utility tie, budget boundary and coefficient breakpoint; inspect endpoints/one-sided limits with explicit tie/attainment rules. This is a restricted replacement, not a theorem for arbitrary monotone functions.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.
