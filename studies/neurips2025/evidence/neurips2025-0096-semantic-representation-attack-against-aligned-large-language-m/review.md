# Semantic Representation Attack against Aligned Large Language Models



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The reciprocal probability theorem can demand a probability greater than one. Representative/class optimization, infinite-class floors and nucleus sampling need narrower conclusions, while the original fixed-floor perplexity sufficient condition survives.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: The reciprocal lower bound can exceed one

Assessment: supported; impact: major



Source: Theorem 3.1, Eq.(5), PDF pp.4–5; Appendix A.1, PDF pp.24–25, Eqs.(19)–(31)



### Source claim (paraphrase)

Theorem 3.1 claims \(P(\hat y_2\mid c)>\delta/(D_{\rm seq}+\epsilon)\) under its coherence and semantic-class assumptions.



### Analysis

Let one-token context \(c\) have probability \(1\), followed by completed responses \(a,b,r\) with probabilities \((0.4,0.4,0.2)\), then certain termination. Put \(a,b\) in the same semantic class, \(\tau=2\), \(\epsilon=0.01\). Coherence is \(\sqrt{2.5}<2\); the appendix gives \(\delta=1/4\), while \(D_{\rm seq}=\log(0.4/0.4)=0\). The theorem demands \(0.4>25\), despite meeting its small-argument condition. Linearizing an exponential and then dropping the added constant does not preserve a numerical lower bound.



### Finding and scope

The central reciprocal theorem is false under its own assumptions. No model or operational attack is needed.



### Proposed correction

Retain the exact log-ratio identity \(P(\hat y_2\mid c)=P(\hat y_1\mid c)e^{-D_{\rm seq}}\), which gives lower bound \(\delta e^{-D_{\rm seq}}\). It does not prove semantic convergence by itself.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: An improved representative can reduce semantic-class mass

Assessment: supported; impact: minor



Source: Theorem 3.2, Eq.(6), PDF p.6; Appendix A.2, PDF pp.26–27



### Source claim (paraphrase)

Theorem 3.2’s argument treats maximizing one representative as maximizing the class mass, without a stated approximation factor or fixed within-class proportions.



### Analysis

Two feasible contexts give class probabilities \((0.400,0.380)\) and \((0.395,0.395)\) for responses \(a,b\). Maximizing \(a\) selects the first, but class masses are \(0.780<0.790\). Embed the contexts with probabilities \(0.005\) each, certain response termination, \(\tau=100\) and \(\epsilon=0.01\); then \(\delta=0.0002\), all class probabilities are coherent and all ordered-pair small-ratio conditions hold. The monotonic implication fails independently of the first theorem.



### Finding and scope

Optimizer equivalence and the proof’s monotonicity are unsupported. An unspecified empirical approximation tolerance is not quantitatively refuted.



### Proposed correction

Fixed positive proportions \(P(y_i\mid c)=w_iP(Y_\Phi\mid c)\), with \(w_i\) independent of context, are a sufficient condition for exact equivalence. They are not established properties of the models.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: An infinite completed-response class cannot share a positive floor

Assessment: supported; impact: minor



Source: Definition 3.1, Eq.(2), PDF p.3; sequence domain in Section 3.1



### Source claim (paraphrase)

Definition 3.1 requires \(P(y_i\mid c)>\delta>0\) for every member of a potentially infinite semantic class.



### Analysis

Distinct completed responses are disjoint events. For any \(N\) members, normalization gives \(1\geq\sum_iP(y_i\mid c)>N\delta\), impossible once \(N>1/\delta\). A finite class requires \(N\delta<1\). Overlapping prefixes cannot instead be summed as completed-response mass.



### Finding and scope

The formulation needs a finite feasible domain or a different coverage objective. The implemented finite search is not shown empty.



### Proposed correction

Specify a finite candidate class with compatible thresholds, or use a class-mass constraint. These are different objectives and do not automatically preserve Theorem 3.2.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 4: Nucleus mass does not enforce a fixed token-probability floor

Assessment: supported; impact: minor



Source: Theorem 3.3 and Algorithm 1; Appendix B.2, PDF pp.28–29; baselines/sra/utils.py, GenerationWorker selector



### Source claim (paraphrase)

Theorem 3.3 uses per-token probability above \(1/\tau\), while the released selector uses cumulative top-p mass and top-k truncation.



### Analysis

Probabilities \((0.90,0.04,0.03,0.03)\) at top-p level \(0.95\) select the first three tokens. At \(\tau=20\), two are below \(0.05\). A one-token context of perplexity \(19.9\) followed by the \(0.03\) token has perplexity \(\sqrt{19.9/0.03}>20\). The selector contains no fixed-floor check.



### Finding and scope

Nucleus selection alone does not preserve the same fixed-threshold guarantee. The original sufficient theorem remains valid.



### Proposed correction

Enforce the fixed floor or check cumulative perplexity directly. An adaptive threshold needs an explicit update and final validation before claiming its changed guarantee.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
