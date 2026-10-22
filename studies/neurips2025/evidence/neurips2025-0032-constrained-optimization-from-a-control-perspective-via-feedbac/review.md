# Constrained Optimization From a Control Perspective via Feedback Linearization



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Exact admissible flows violate the infeasible-initialization rate, terminal-residual conclusion and specified momentum-merit descent. These central mathematical failures determine Major. They do not establish divergence of all feedback flows; the separate OPF metric mismatch is a local issue.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: The strong-convexity bound omits infeasible initial error

Assessment: supported; impact: major



Source: Theorem 6, Appendix C.1, p.22.



### Source claim (paraphrase)

Theorem 6 gives objective-gap decay proportional to \(e^{-2\mu t}\) without requiring feasible initialization.



### Analysis

Let \(f(s,r)=((s-1)^2+r^2)/2\), \(h(s,r)=s\), \(T=I,K=1,\mu=1\), with initial point \((-1,0)\). The constraints have full row rank and the Hessian is \(I\). The exact flow is \(s=-e^{-t},r=0\). Its constrained-optimum objective gap is \(e^{-t}+e^{-2t}/2\), whereas the claimed envelope is \(3e^{-2t}/2\). At \(t=\log2\), these are \(5/8\) and \(3/8\). Convergence still occurs; the claimed envelope does not.



### Finding and scope

The quantitative strong-convexity envelope fails at an allowed infeasible initialization; convergence itself survives this example.



### Proposed correction

Require feasible initialization for the projected-gradient proof, or add an explicit normal-infeasibility term.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: Finite squared-residual integral does not imply terminal convergence

Assessment: supported; impact: major



Source: Theorems 1,4, pp.4–7; terminal-limit proofs, p.21 and Appendix E, p.25.



### Source claim (paraphrase)

Theorems \(1\) and \(4\) conclude that last-time KKT gaps vanish from a finite integral bound.



### Analysis

Let \(\phi\) be a smooth compactly supported unit-height bump and \(g(s)=1/(1+s^2)+\frac12\sum_{k\ge1}\phi((s+k)/2^{-k-3})\). Define \(F(s)=\int_{-\infty}^s g(u)\,du\), \(f(s,r)=F(s)\), \(h=r\), \(T=I,K=1\). The sum is locally finite; \(f\) is smooth, lower bounded and has bounded gradient.

The exact flow is \(\dot s=-g(s),\dot r=-r\). It crosses every \(s=-k\) at times tending to infinity, where the KKT residual is at least \(1/2\). Nonetheless \(\int g(s(t))^2dt=\int g(s)\,ds\) along the descending trajectory is finite. Narrowing peaks preserve finite integral without a vanishing terminal residual. The source's Jacobian/multiplier assumptions do not supply the missing uniform continuity.



### Finding and scope

A finite residual integral does not ensure the claimed last-time KKT convergence without an additional regularity condition.



### Proposed correction

Add and verify a condition implying uniform continuity of the residual, then use an appropriate integral-to-limit theorem. The integral and best-iterate guarantees are not refuted.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: The specified momentum merit can initially increase

Assessment: supported; impact: major



Source: Theorem 5, p.9; Appendix F, pp.26–28.



### Source claim (paraphrase)

Theorem 5 gives numerical thresholds intended to make its particular merit function nonincreasing.



### Analysis

Use \(f(x)=0.01\log\cosh x\), \(h(x)=10^{-4}x\), \(T=K=1\), \(a_1=1,a_2=100000,\alpha=200000\), \(x_0=0.1,z_0=0\). Bounds \(M=1,D=20000,L_f=0.01,L_1=100,L_2=1.04\) satisfy the printed thresholds \(a_2\ge93200\) and \(\alpha\ge108003.05\). Direct differentiation of the full stated merit gives \(0.01[0.01\operatorname{sech}^2(0.1)-0.001]\simeq8.9006629\times10^{-5}>0\). This refutes its nonincrease claim, not stability under every alternative energy.



### Finding and scope

The theorem’s own sufficient constants permit a positive derivative of its stated merit function, disproving its nonincrease claim.



### Proposed correction

Rework the specific merit/threshold proof; no complete general replacement theorem is asserted.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: The OPF code omits the complementarity absolute value

Assessment: supported; impact: minor



Source: Paper KKT-gap definition, p.6; two OPF MATLAB metric paths.



### Source claim (paraphrase)

The paper defines KKT gap using the absolute value of lambda-transpose h.



### Analysis

The paper's gap uses \(|\lambda^\top h|\), while both author MATLAB metric paths insert the signed \(\lambda^\top h\) into a maximum with nonnegative residuals. A large negative value is then hidden. This is a local metric-definition mismatch; corrected OPF curves require the original per-step values.



### Finding and scope

The public OPF metric omits the absolute value in the declared complementarity term. Historical curves cannot be corrected without their per-step values.



### Proposed correction

Use \(|\lambda^\top h|\) consistently in that metric.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- No new author-code execution, model spending, training, author contact or complete benchmark replication.

- Historical numerical results are retained evidence rather than current reruns.

- Local counterexamples do not invalidate every empirical result; missing historical run attribution remains unresolved.
