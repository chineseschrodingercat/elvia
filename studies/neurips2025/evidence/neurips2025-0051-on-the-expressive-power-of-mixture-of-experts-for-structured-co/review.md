# On the Expressive Power of Mixture-of-Experts for Structured Complex Tasks



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The triangular router has an endpoint tie defect in its pointwise construction. This leaves the essential-supremum and existential alternatives open; finite-width training plateaus do not establish an asymptotic expressivity obstruction.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Integer interfaces do not identify a valid local expert

Assessment: supported; impact: minor



Source: Appendix B.2, PDF pp.26–28, Eqs.(13)–(14)



### Source claim (paraphrase)

Appendix B.2 infers a valid interval from the maximum of the triangular scores \(\tau_i(t)=(t-i+1)_++(t-i)_+-2(t-i+1/2)_+\). It then invokes the selected expert’s local approximation guarantee for arbitrary inputs.



### Analysis

At every integer interface all scores are zero. Take three exact affine experts \(g_1(t)=t\), \(g_2(t)=2t-1\), \(g_3(t)=3t-3\), each used on its corresponding unit interval. Their joined target is continuous. At \(t=2\), a lowest-index tie selects \(g_1(2)=2\), although both valid adjacent pieces give \(f(2)=3\). Local errors are zero but the constructed pointwise error is \(1\). A fixed score-only tie cannot select appropriate intervals at every endpoint.



### Finding and scope

The displayed pointwise assignment fails at interfaces. This null-set failure does not refute an essential-supremum bound or the existence of another valid router.



### Proposed correction

Use affine nearest-center scores \(a_i(t)=2c_it-c_i^2\), where \(c_i=i-1/2\). They order the centers by distance; adjacent endpoint ties involve only intervals containing that endpoint. A constant feature implements the intercept in a linear gate.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Finite training plateaus do not establish an approximation floor

Assessment: not_issue; impact: no_issue_found



Source: Section 6, PDF p.10, finite-width MoE experiment



### Source claim (paraphrase)

Section 6 interprets the plateau of a six-expert model over the tested widths as limited expressive power.



### Analysis

Set every expert equal to the same dense ReLU network \(g\). The top-one output is then \(g\) for every router decision, so this class contains the corresponding dense class. A finite optimization plateau cannot establish a positive asymptotic approximation-error floor for that containing class.



### Finding and scope

The observed table is not contradicted. A fixed-resource depth advantage remains compatible with this containment argument.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
