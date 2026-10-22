# PINN Balls: Scaling Second-Order Methods for PINNs with Domain Decomposition and Adaptive Sampling



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The entropy optimizer formula is correct, but its proof’s full-support justification is incomplete. The boundary penalty also depends on the ball geometry, so fixed boundary coordinates do not justify dropping its geometry derivative unless the ansatz is explicitly frozen.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: Finite entropy does not establish strict positivity

Assessment: supported; impact: minor



Source: Appendix A, Lemma A.4, proof of the Gibbs optimizer; Theorem A.5



### Source claim (paraphrase)

The proof states that an optimizer must have positive density because otherwise its entropy objective is infinite, then uses multiplicative variations to derive an Euler equation over the domain.



### Analysis

On \([0,1]\), density \(p=2\) on the first half and zero elsewhere has finite entropy \(\int p\log p=\log2\), using \(0\log0=0\). It is not the optimizer; it disproves the finiteness rationale rather than the optimizer formula. Multiplicative variations preserve its zero set, so a separate full-support argument is needed. If “positive density” means only absolute continuity, the existence-of-density statement is reasonable but still does not justify strict positivity in the later variation step.



### Finding and scope

The lemma’s conclusion remains valid under its stated bounded-continuous residual and positive-temperature assumptions; the proof needs completion, not a reversed theorem verdict.



### Proposed correction

For bounded continuous \(f_0\), let \(Z=\int e^{f_0/\beta}\), \(q=e^{f_0/\beta}/Z\). Then \(E(p)=\beta D_{\mathrm{KL}}(p\|q)-\beta\log Z\), proving the unique optimizer \(q\), including full support. At unit domain volume and residual sup norm \(a_n\to0\), \(0\le\beta\log Z_n\le a_n\) and \(p_n\to1\) uniformly.

A proposed correction is described; author adoption is not established.



## Problem 2: The boundary penalty changes with shared ball geometry

Assessment: supported; impact: minor



Source: Eqs.(8)–(10),(13), main algorithm; boundary-term independence statement near the geometry update



### Source claim (paraphrase)

The same centers/radii parameterize normalized expert gates and the adaptive density. Fixed boundary coordinates do not make predictions at those coordinates independent of geometry.



### Analysis

On \([0,1]\), use constant experts \(U_1=0,U_2=1\), centers \(0,1\), radii \(2,2\), endpoint boundary targets zero and the printed quartic gates. Every endpoint lies strictly inside both balls. Predictions are \(u(0)=9/25,u(1)=16/25\), hence mean boundary loss \(B=0.2696\). Differentiating only the second radius gives \(\partial_{s_2}u(0)=96/625\), \(\partial_{s_2}u(1)=0\), and \(\partial_{s_2}B=864/15625=0.055296\ne0\). Thus dropping the term is not the full tied-geometry gradient. Freezing the ansatz during a density-only surrogate update, exact boundary enforcement or zero residual can legitimately remove it, but fixed sample coordinates alone cannot.



### Finding and scope

The written omission needs a declared detachment/surrogate policy or the missing derivative. Without author implementation, historical computational-graph behavior and numerical impact remain unknown.



### Proposed correction

For the full tied geometry, include \(\nabla_\varphi B\) and both the direct residual derivative and density derivative in the interior term. A frozen-proposal importance estimator must hold its samples/denominator fixed while differentiating the numerator. Alternatively explicitly define a density-only frozen-ansatz surrogate and analyze that method separately.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.
