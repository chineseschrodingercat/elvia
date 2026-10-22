# Implicit Reward as the Bridge: A Unified View of SFT and DPO Connections



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



A full-support one-step example separates TV-plus-KL distribution matching from ordinary SFT once the TV conjugate domain is retained. The raw-logit/Q theorem omits the reference-policy action term, and several alternative-loss rows fail direct substitution into the stated dual. These are core theoretical defects; the observed learning-rate and training comparisons are not independently remeasured.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Dropping the TV conjugate domain changes the SFT equivalence

Assessment: supported; impact: major



Source: Section 3.1–3.2, Eqs.(1)–(5), PDF pp.4–5; Appendix A.1–A.2, Eqs.(12)–(27), pp.15–16



### Source claim (paraphrase)

The paper claims TV distribution matching plus KL regularization becomes ordinary SFT because the TV conjugate is the identity, and the KL contribution disappears from the final optimization.



### Analysis

For \(f(u)=|u-1|/2\) on \(u\ge0\), the conjugate is \[f^*(t)=\begin{cases}-1/2&t<-1/2,\\t&-1/2\le t\le1/2,\\+\infty&t>1/2.\end{cases}\] Extending the absolute-value generator to all real inputs gives identity only on the bounded interval and infinity outside. Either interpretation requires a restriction that Appendix A.1 initially recognizes but A.2 drops. A valid TV dual uses a bounded critic: \[\max_{\|r\|_\infty\le1/2}\{q^\top r-\beta\log\sum_i\rho_i e^{r_i/\beta}\}.\]

Use a one-step terminal model, full-support expert \(q=(0.9,0.1)\), reference \(\rho=(0.5,0.5)\) and \(\beta=1\). For policy \((p,1-p)\), Eq.(1) is \[J(p)=|p-0.9|+p\log(2p)+(1-p)\log(2(1-p)).\] Its minimizer is \(p=e/(1+e)\approx0.731059\), with \(J\approx0.279886\); ordinary SFT selects \(p=0.9\), with \(J\approx0.368064\). Differentiating on either side of \(0.9\) and checking the boundary establishes the global minimum. The bounded critic \((1/2,-1/2)\) gives the matching dual optimum.

An SFT-optimal policy here would require implicit reward span \(\log9>1\); no common reward shift makes that span fit the bounded TV critic. For sufficiently small regularization, specifically \(\beta\le1/\log9\) in this example, the two optimizers can agree. That restricted countercontrol does not imply unrestricted equivalence.



### Finding and scope

The disappearance of the optimization constraint changes the problem. The general policy/implicit-reward representation can remain useful, but it does not establish the claimed exact equivalence to ordinary SFT or elimination of KL’s influence.



### Proposed correction

Retain the TV conjugate’s domain and the corresponding bounded reward or reward-span restrictions. The resulting constrained objective is not ordinary unconstrained SFT; a full sequential occupancy-measure formulation needs its own conditions.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: The Q/logit identification omits a reference-policy action term

Assessment: supported; impact: major



Source: Section 3.3, Theorem 2, Eq.(6), PDF p.6; Appendix A.3, Eqs.(28)–(34), p.16; Assumption 2 and Section 4.4



### Source claim (paraphrase)

The theorem identifies raw logits with the Q-function of the implicit reward up to a state-only offset, but its proof uses a reference-free maximum-entropy fixed point for a KL-relative objective.



### Analysis

For KL regularization relative to \(\rho(a\mid s)\), the relevant optimality relation is \[\pi(a\mid s)=\rho(a\mid s)\exp((Q_r(s,a)-V_r(s))/\beta).\] If policy logits \(\ell\) use temperature \(\tau\), then \[Q_r(s,a)=\frac{\beta}{\tau}\ell_a-\beta\log\rho(a\mid s)+V_r(s)-\beta\log\sum_b e^{\ell_b/\tau}.\] The reference term depends on the action and cannot generally be absorbed in a state-only offset.

For a one-step model with \(\pi=\rho=(0.8,0.2)\), zero reward, and \(\beta=\tau=1\), relative-KL optimization is maximized at \(\pi=\rho\) with \(V=0\). The implicit reward from Eq.(4) is zero and \(Q=(0,0)\). Valid logits are \((\log0.8,\log0.2)\), whose difference is \(\log4\). They cannot equal that Q-vector plus one common constant. A uniform reference removes this specific obstruction; an augmented Q that includes the log reference is a different quantity.

In addition, shifting all logits at a state by arbitrary \(c(s)\) leaves its policy unchanged but shifts its log-sum-exp by \(c(s)\). Therefore policy identities do not establish cross-state value rankings. Assumption 2 is an extra gauge-sensitive empirical assumption. Reported rank correlations for a fixed implementation need not be false, but cannot remove this freedom or prove the theorem.



### Finding and scope

The raw-logit theorem fails for an allowed nonuniform reference even before addressing gauge-sensitive state comparisons. The current theorem does not follow from the valid implicit-reward ratio identity.



### Proposed correction

Include the action-dependent \(-\beta\log\rho(a\mid s)\) term, the \(\beta/\tau\) scale and a declared state gauge. Distinguish the original reward’s Q-function from any reference-augmented quantity. Cross-state value estimation requires additional gauge control.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: The alternative losses do not consistently instantiate the stated dual

Assessment: supported; impact: major



Source: Table 3, PDF p.8; Appendix B, Table 5, p.17; Appendix A.1, Eqs.(18)–(22), pp.15–16



### Source claim (paraphrase)

Several rows pair incompatible divergence generators, conjugates or training targets, and drop a value term or conjugate domain required by the dual.



### Analysis

Use a one-step model with \(\beta=1\), expert \(q\), reference \(\rho\), policy \(\pi\), and \(c=V(s_0)\). Implicit reward is \(r_i=\log(\pi_i/\rho_i)+c\). The complete reward objective is \[F=-\sum_i q_i f^*(-\log(\pi_i/\rho_i)-c)-c.\] For KL, \(f^*(t)=e^{t-1}\), so \[F=-e^{-c-1}\sum_i q_i\rho_i/\pi_i-c.\] It is not a probability difference times an exponential.

For \(q=(0.9,0.1)\), \(\rho=(0.5,0.5)\), \(c=0\), and \(\pi=(p,1-p)\), the correct KL target maximizes \(-e^{-1}(0.45/p+0.05/(1-p))\) at \(p=0.75\). The printed row instead gives \(e^{-1}(0.8p-0.4)\), increasing toward \(p=1\). Moving \(p\) from \(0.75\) to \(0.99\) decreases the correct objective from approximately \(-0.294304\) to \(-2.006615\), while increasing the printed one from \(0.073576\) to \(0.144209\).

The displayed Pearson divergence has denominator \(p\): \(\sum_i(q_i-p_i)^2/p_i\). Its generator is \((u-1)^2/u\), with conjugate \(2-2\sqrt{1-t}\) for \(t\le1\), infinite otherwise. The listed quadratic conjugate \(t+t^2/4\) instead belongs to generator \((u-1)^2\), whose divergence has denominator \(q\); on \(u\ge0\) it also has a constant branch \(-1\) for \(t<-2\). For \(P=(3/4,1/4)\), \(Q=(1/2,1/2)\), the two divergences are \(1/3\) and \(1/4\), respectively.

The missing \(-c\) term is not generally constant under the stated reward optimization. Take \(\pi=q=\rho=(1/2,1/2)\), constant reward \(2\) and hence \(c=2\). For the quadratic generator, the full dual gives \(-f^*(-2)-2=-1\); the printed Pearson target gives \(2-2^2/4=1\), exceeding primal minimum \(0\). Fixing \(c=0\) removes this witness but is an additional gauge restriction.

The squared-Hellinger conjugate is \(t/(1-t)\) only for \(t<1\), and infinite otherwise. Choose \(\pi_1=0.1,\rho_1=0.5,c=0\). Then \(r_1=\log0.2<-1\), so the proper dual is infeasible, while its printed rational expression is finite, approximately \(2.640856\). The half-weighted Jensen–Shannon definition also requires \(-\frac12\log(2-e^{2t})\), with \(t<\frac12\log2\), rather than the listed unhalved conjugate. This scaling changes the objective at fixed regularization strength. The Pearson, Hellinger, JS and GAN targets must all retain the full value term and applicable domains.



### Finding and scope

These are substantive derivation mismatches in the stated alternatives, including optimizer reversal and a weak-duality violation. They do not independently determine which expression an unavailable training implementation actually optimized, or whether the reported empirical improvements persist.



### Proposed correction

Derive each row from a consistently oriented generator, its full piecewise conjugate and domain, and the complete objective including the initial value term. Keep reference-policy and gauge conventions consistent across all rows; empirical consequences require the actual producing implementation.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.

- No author-released training implementation was available for static comparison; none of the empirical training results is declared reproduced or invalidated by these objective-level examples.
