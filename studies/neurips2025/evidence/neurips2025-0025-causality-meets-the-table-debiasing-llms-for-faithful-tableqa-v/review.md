# Causality Meets the Table: Debiasing LLMs for Faithful TableQA via Front-Door Intervention



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The current paper still replaces the observational question marginal by equally weighted generated variants and replaces an evidence expectation by a union of evidence. Finite front-door models show these substitutions change the identified causal probability. This is Major damage to the claimed causal-adjustment interpretation, without establishing that the reported TableQA accuracy gains are false. Full mediation remains an explicitly unresolved modeling condition.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Generated paraphrases do not identify the observational marginal

Assessment: supported; impact: major



Source: Section 4.1, p.4, Eq.4; Appendix C, p.24, Figure 7.



### Source claim (paraphrase)

Section 4.1 substitutes equal weights on jointly generated question variants for the observational marginal \(P(Q)\) in the front-door formula.



### Analysis

Generated variants follow a proposal \(g(q^{\prime}\mid q,T)\), which need not be the observational marginal \(P(Q)\). Consider independent-noise binary structural equations: \(C\sim\operatorname{Bernoulli}(4/5)\); \(Q=C\) with probability \(9/10\); \(E=Q\) with probability \(4/5\); and \(A=E\mathbin{\mathrm{XOR}}C\). This has exactly the front-door paths \(C\to Q,C\to A,Q\to E\to A\), and all conditioning cells are positive. The marginal of \(Q\) is \((13/50,37/50)\). For \(E=0\), the conditional answer probabilities across the two question values are \((4/13,36/37)\); for \(E=1\), they are \((9/13,1/37)\). Direct intervention at \(Q=1\), and the correctly weighted front-door formula, both give \(8/25=0.32\). Replacing only the question weights by \((1/2,1/2)\) gives \[\frac15\frac12\left(\frac4{13}+\frac{36}{37}\right)+\frac45\frac12\left(\frac9{13}+\frac1{37}\right)=\frac{200}{481}\approx0.4158004158.\] Equal-probability generation, even if exact, does not identify the different observational law.



### Finding and scope

The current Section 4.1 substitution is not generally an estimator of the stated front-door marginal. The classical front-door formula remains valid in this same counterexample. Multiple paraphrases may still improve empirical answers, but that observation does not establish causal identification.



### Proposed correction

Use an identified observational marginal or justified importance weights \(P(Q)/g\) on common support. This does not identify the unknown proposal of an actual LLM.

The current proceedings Section 4.1 retains the simultaneous-generation uniformity justification; the current author repository is empty. The conditional importance-weighting identity remains an applicable analytic correction, not evidence of an adopted implementation.



## Problem 2: Evidence union changes the expectation target

Assessment: supported; impact: major



Source: Section 4.2 and front-door Eq.3; evidence aggregation and voting steps.



### Source claim (paraphrase)

Section 4.2 substitutes a union of retrieved evidence for the outer front-door evidence average.



### Analysis

Let the evidence values be \(E_0=\{r_0\}\), \(E_1=\{r_1\}\), and \(E_2=\{r_0,r_1\}\), with probabilities \((9/20,9/20,1/10)\) conditional on the fixed question. Let the answer mechanism return the cardinality of its evidence, independently of the question wording. The original outer mixture therefore gives answer \(2\) with probability \(1/10\). Even granting two independent samples from exactly the correct evidence law, their union has cardinality \(2\) with probability \[1-2(9/20)^2=119/200=0.595.\] With \(n\) samples that probability is \(1-2(9/20)^n\to1\), while the target remains \(0.1\). The union remains within the original evidence support, so the discrepancy does not rely on evaluating an undefined evidence state. The inner question average is immaterial here, isolating the outer-operator substitution.



### Finding and scope

The current union step changes the evidence random variable and can reverse the modal answer. It does not generally implement the original front-door expectation, even with correct sampling and increasing sample size. This does not quantify any actual TableQA benchmark effect.



### Proposed correction

Average conditional answer probabilities over the intended evidence mixture and its weights, rather than treating evidence union as that expectation.

The current proceedings Section 4.2 and its evidence-aggregation prompt retain the union operation. Preserving a probability mixture is an analytic alternative; redefining the union as a new mediator would require its own identification assumptions.



## Problem 3: The operational model does not establish full mediation

Assessment: needs_evidence; impact: needs_evidence



Source: Eq.1, Section 3.2 and the front-door graph.



### Source claim (paraphrase)

The depicted front-door graph has no direct Q-to-A path.



### Analysis

The answer prompt receives both \(Q\) and \(E\). This signature does not prove a direct causal effect, but it does not establish the full-mediation assumption \(Q\to E\to A\) either. That assumption needs a causal model or suitable evidence; the classical identification formula is conditional on it.



### Finding and scope

Full mediation is an additional unverified causal assumption for this operational prompt interface. The presence of both inputs alone proves neither a direct effect nor its absence; this concern is not a counterexample to the classical front-door theorem.



### Proposed correction

State and justify mediation/support assumptions explicitly; the classical identification formula remains conditional on them.

The current Eq. (1) still supplies both question and evidence to the answer prompt. No additional causal-model verification was available from the empty author repository.



## Limits

- The current author repository is empty, so no implementation or historical prediction files could be inspected. No model, author program or old verifier was executed. The counterexamples concern causal identification, not the magnitude of benchmark effects. Figure/table population correspondence and training-data contamination remain unresolved without sample identities and run records.
