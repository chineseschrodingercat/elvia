# From Linear to Nonlinear: Provable Weak-to-Strong Generalization through Feature Learning



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



A missing strong-sample dimension factor invalidates a central proof control. Four additional local proof/quantifier defects have bounded corrections or unresolved dynamical scope.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Dimension assumption does not imply the strong-noise bound

Assessment: supported; impact: major



Source: Condition 3.1(C1), PDF p.5; Appendix A.2.3, Eq.(6), p.23; Theorem 3.4 proof



### Source claim (paraphrase)

The dimension condition has terms \(n_{\rm wk}^2\log(Cn_{\rm wk}^2/\delta)\) and \(n_{\rm st}\log(Cn_{\rm st}/\delta)\), multiplied by \(C(\log T^*)^2\). The proof defines \[\beta_{\rm st}=4C_{\rm st}n_{\rm st}\sqrt{d^{-1}\log(C_{\rm st}n_{\rm st}/\delta)}\] and asserts \(\beta_{\rm st}\log T^*\leq1/100\).



### Analysis

Fix sufficiently large constants \(C\geq4,C_{\rm st}>0\), and take \(\delta=1/4,\sigma_p=1,p_e=1/2,p_h=1/(4C),p_b=1/2-1/(4C)\). Let orthogonal signal norms satisfy \(\|\mu\|^2=d^{1/3},\|\nu\|^2=d^{1/4}\), and let \(n_{\rm wk}=\lfloor d^{2/5}\rfloor,n_{\rm st}=\lfloor d^{3/5}\rfloor,m=\lceil C(\log d)^2\rceil,\sigma_0=d^{-10},\eta=d^{-2},\varepsilon=d^{-1}\). A fixed-degree polynomial horizon has \(\log T^*=\Theta(\log d)\). C1 requires only \(O(d^{4/5}(\log d)^3)+O(d^{3/5}(\log d)^3)=o(d)\); C2 holds by diverging samples and width. C3 permits initialization of order \(d^{-13/20}/\sqrt{\log d}\), above the chosen value; C4 holds because \(d^{-2}=o(d^{-3/2})\). For C5 the signal ratio grows as \(d^{1/12}\), and both samples exceed the \(d^{1/3}\) lower scale. In C6, \(Cp_h=1/4<p_b\) and the other required term is \(O(d^{-1/12}\sqrt{\log d})\). Condition 3.2 permits samples of order \(d^{2/3}/\log d\), above both selected sample sizes. Yet the asserted small quantity is \(\Theta(d^{1/10}(\log d)^{3/2})\), which diverges.



### Finding and scope

The deterministic implication used repeatedly in the strong-model proofs is false under the stated assumptions, including the data-scarce regime. This invalidates the current proof route; it is not a constructed training trajectory refuting the final test-error conclusions.



### Proposed correction

Add explicitly the sufficient condition \[d\geq160000C_{\rm st}^2n_{\rm st}^2\log(C_{\rm st}n_{\rm st}/\delta)(\log T^*)^2.\] This restores exactly the small-noise step while shrinking the theorem domain; other proof obligations remain.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Logistic-ratio inequality is reversed

Assessment: supported; impact: minor



Source: Lemma B.1, property W3, PDF p.28



### Source claim (paraphrase)

For \(a>b\), the proof upper-bounds \((1+e^b)/(1+e^a)\) by \(e^{b-a}\).



### Analysis

The exact difference is \((1-e^{b-a})/(1+e^a)>0\). For \(a=\log(17/8),b=\log2\), the margin gap \(\log(17/16)\) lies between \(1/32\) and \(1/4\), but the ratio is \(24/25>16/17\). This refutes the scalar inequality, without claiming reachability of that pair by gradient descent.



### Finding and scope

The printed inequality is false. Its intended nonexpansion can nevertheless be recovered under the existing weak-regime margin lower bound, so this local defect does not independently refute the weak-training result.



### Proposed correction

Use \(\log[g(a)/g(b)]=-\int_b^a e^u/(1+e^u)\,du\). For \(b\geq-1\), this gives \(g(a)/g(b)\leq e^{-(a-b)/(1+e)}\). The induction bounds give \(b\geq-8(1+2/C)/C^2-\kappa_{\rm wk}/64>-1\); with the stated noise-norm ratio the resulting exponent remains negative.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: Pseudo-opposite response uses true-opposite coefficients

Assessment: supported; impact: minor



Source: Lemma C.2, PDF p.34; signal decomposition in Appendix A.2



### Source claim (paraphrase)

The lemma bounds \(F_{-\hat y_i}\) using underlined coefficients associated with the class opposite the true signal.



### Analysis

If a hard example has true label \(+1\) but pseudo-label \(-1\), then \(-\hat y_i=+1\). Its response to \(\nu_+\) contains the own-class coefficient \(\overline N_{+,r}\), whereas the displayed bound controls \(\underline N_{+,r}\). Bounds on the latter do not algebraically bound the former. Taking the underlined coefficients zero and the overlined response arbitrarily large demonstrates the missing premise, but is not a reachable-iterate counterexample.



### Finding and scope

The cited proof step needs additional time-indexed own-class signal controls. Surrounding simultaneous-induction properties may provide them; a full dynamical counterexample has not been established.



### Proposed correction

Include the stated signal signs and own-class averages bounded by \(Q=\kappa_{\rm st}/64\). Under \(\alpha_{\rm st}\leq0.01\) and \(\beta_{\rm st}\log T^*\leq0.01\), the resulting response bound is \(0.69123<\kappa_{\rm st}/16\approx1.24245\). Each use must establish those premises at the required induction time.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 4: Averaging a maximum is bounded in the wrong direction

Assessment: supported; impact: minor



Source: Lemma D.3 proof, PDF p.55



### Source claim (paraphrase)

The proof replaces the average of filterwise maxima by the maximum of filter averages as an upper bound.



### Analysis

For the two nonnegative arrays \((1,0)\) and \((0,1)\), the average of pointwise maxima is \(1\), while the maximum average is \(1/2\). The valid general inequality points in the opposite direction. This is an algebraic counterexample rather than a claimed training iterate.



### Finding and scope

The manipulation is invalid, but a fixed signal patch has one type across all filters; the desired local conclusion can be proved without the maximum interchange.



### Proposed correction

Split by the fixed signal type and whether the pseudo-label agrees with the true label. Apply the relevant signed mean coefficient bound directly; the stated smallness and horizon conditions then recover a signal response at most \(\alpha_{\rm st}+1/2\).

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 5: Universal strict-error formula omits zero margins

Assessment: supported; impact: minor



Source: Proposition 2.1, PDF p.3



### Source claim (paraphrase)

For every weak-model parameter \(w\), the paper asserts strict hard-example error probability \(\Pr(yf_{\rm wk}<0\mid\mathcal S_h)=1/2\).



### Analysis

In \(d=6\), use orthogonal signals \(\mu_+=2e_1,\mu_-=2e_2,\nu_+=e_3,\nu_-=e_4\), noise covariance \(\operatorname{diag}(0,0,0,0,1,1)\), positive mixture probabilities and \(w=2e_1-2e_2\). Every hard signal and every noise realization is orthogonal to \(w\), so the hard margin is identically zero and the strict-error probability is \(0\). Easy and both-signal margins are respectively \(8\) and \(4\); this is not the zero classifier.



### Finding and scope

The universal quantifier fails because of ties. Sign symmetry instead gives \(\Pr(M<0)=[1-\Pr(M=0)]/2\). Positive finite trained weak-model iterates can have nondegenerate noise projections, preserving the intended random-guess conclusion in that narrower setting.



### Proposed correction

State the identity including zero-margin mass, use randomized tie error, or add the nondegeneracy premise \(\sigma_p\|\Lambda w\|>0\).

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
