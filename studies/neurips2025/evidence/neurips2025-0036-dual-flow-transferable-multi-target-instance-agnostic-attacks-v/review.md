# Dual-Flow: Transferable Multi-Target, Instance-Agnostic Attacks via In-the-wild Cascading Flow Optimization



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Small ODE time steps do not control a fixed parameter step; an explicit smooth counterexample refutes Theorem 2's descent implication. The Morse cutoff proof has a separate local strict-growth gap. The ideal-flow statements and empirical attack results remain distinct.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Small time steps do not guarantee loss descent

Assessment: supported; impact: major



Source: Theorem 2, p.4; Algorithm 1, p.5; Proposition 4/Appendix A.2, pp.24–25.



### Source claim (paraphrase)

Theorem 2 claims an update improves next-time extrapolated loss when the time decrement is sufficiently small and functions are smooth.



### Analysis

Choose constant velocity parameters \(\theta=\phi=0.02\), time \(t=0.5\), input \(0.49\), binary logits \((-10000(u-0.5)^2,0)\), and parameter step \(0.001\). The gradient is \(73.105857863\), so \(\theta^+=-0.053105857863\). Old next-time extrapolation remains \(0.49\); the updated extrapolation is \(0.5265529289315-0.073105857863\delta\). For every \(0<\delta\le0.1\), this moves farther from \(0.5\), increasing cross-entropy with clipping inactive. At \(\delta=0.05\), losses are \(1.3132616875\) and \(5.2482877367\). Arbitrarily small time decrements cannot repair an uncontrolled finite parameter step.



### Finding and scope

Theorem2 lacks a parameter-step condition needed for its claimed next-time descent; arbitrarily small time decrements do not repair this smooth finite-step counterexample.



### Proposed correction

Control the parameter learning rate and gradient alignment through a descent argument, as well as the ODE time discretization.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: The cutoff construction does not give almost-everywhere strict growth

Assessment: supported; impact: minor



Source: Proposition 1, p.4; Appendix A.1, pp.23–24.



### Source claim (paraphrase)

Proposition 1 requires a nondecreasing Morse-energy flow with strict growth almost everywhere.



### Analysis

The proof sets an extra cutoff to zero throughout neighborhoods of critical points, not only at the points. Every noncritical initial point in such an open frozen region has constant energy, contradicting almost-everywhere strictness. Nondecrease and existence of some suitable flow are not refuted.



### Finding and scope

The displayed cutoff construction does not establish almost-everywhere strict energy growth. Nondecrease and existence of a different suitable flow are not refuted.



### Proposed correction

An existing narrower construction uses \(X=\mu^2\nabla j\), with an interior-positive boundary-defining \(\mu\), avoiding the extra frozen critical neighborhoods. Its scope is a smooth bounded domain with finite-time boundary noncontact, not arbitrary hard-clipped image domains.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- No new author-code execution, model spending, training, author contact or complete benchmark replication.

- Historical numerical results are retained evidence rather than current reruns.

- Local counterexamples do not invalidate every empirical result; missing historical run attribution remains unresolved.
