# Sample-Efficient Tabular Self-Play for Offline Robust Reinforcement Learning



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



A fully covered two-stage game makes the paper’s gap zero while a player has a profitable unilateral deviation. Separate defects affect the printed supremum TV dual, an unrestricted adaptive concentration lemma and the lower-bound recursion. The current implementation uses a correct supremum structure but its nominal joint-value metric does not measure robust equilibrium regret.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Zero printed gap can conceal a profitable unilateral deviation

Assessment: supported; impact: major



Source: Section 2, Eqs.(6),(8)–(9), PDF pp.4–5; Algorithm 2, p.8; Theorem 4.2, pp.8–9



### Source claim (paraphrase)

Let \(L(\mu,\nu)=\inf_P V^{\mu,\nu,P}\) and \(U(\mu,\nu)=\sup_P V^{\mu,\nu,P}\), using the two players’ prescribed uncertainty sets. Their utilities are \((L,-U)\). Equation (9) substitutes reference equilibrium values for current joint-policy values, and Algorithm 2 combines the maximizing strategy of one zero-sum game with the minimizing strategy of another.



### Analysis

True unilateral regret is \[\max\{\max_{\mu'}L(\mu',\nu)-L(\mu,\nu),\ U(\mu,\nu)-\min_{\nu'}U(\mu,\nu')\}.\] Separate robust envelopes need not form a common zero-sum payoff, even with equal radii.

Take horizon \(2\), states \(s_0,s_1\), two actions per player, and both radii \(1/4\). At time \(1\), at either state set \[R=\begin{pmatrix}3/20&7/20\\1/2&7/10\end{pmatrix},\qquad P(s_1)=\begin{pmatrix}1/2&1/2\\0&0\end{pmatrix}.\] At time \(2\), reward is \(0\) at \(s_0\) and \(1\) at \(s_1\), independent of actions. Direct binary TV optimization gives \[L=\begin{pmatrix}2/5&3/5\\1/2&7/10\end{pmatrix},\qquad U=\begin{pmatrix}9/10&11/10\\3/4&19/20\end{pmatrix}.\] Row \(2\) strictly dominates for \(L\); column \(1\) strictly dominates for minimizing \(U\). The actual equilibrium is \((2,1)\), with reference values \(L^*=1/2,U^*=3/4\).

The separate zero-sum saddles are \((2,1)\) for \(L\) and \((1,1)\) for \(U\). The crossed output is \((1,1)\). Its maximizing-player regret is \(1/2-2/5=1/10\), while minimizing-player regret is zero. Yet the paper’s gap is \(\max\{1/2-1/2,\ 3/4-9/10\}=0\). Interpreting \(U^*\) instead as the separate minimax value \(9/10\) also gives zero.

Uniform initial states and uniform behavior policies give time-one joint occupancies \(1/8\), and time-two joint occupancies \(3/16\) and \(1/16\). Thus \(d_m^n=1/16>0\); the clipped numerator is at most \(1/8\), yielding \(C_r^*\le2\). Sample thresholds can be met by increasing the number of trajectories. The calculation grants correct zero terminal values, exact transitions and vanishing bonuses; strict best-response inequalities persist under sufficiently small estimation errors.



### Finding and scope

The printed certificate does not characterize absence of profitable unilateral deviations, and the exact-model crossed strategy output need not be a robust Nash equilibrium. This rejects the usual equilibrium interpretation of the rate, rather than a numerical bound on the paper’s weaker printed gap. Uncertainty-free common-payoff games remain a valid special case.



### Proposed correction

Use actual robust current-policy values in both unilateral regrets. A known-model backward construction can solve the corresponding bimatrix game with utilities given by each player’s own robust continuation payoff. Its offline statistical rate and computation require a new analysis; replacing a solver does not preserve the stated theorem automatically.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: The printed supremum TV dual clips in the wrong direction

Assessment: supported; impact: major



Source: Appendix B.1, Lemma B.1, Eq.(27b), PDF p.23; Eq.(17), p.7



### Source claim (paraphrase)

Equation (27b) minimizes \(p^\top[V]_\alpha-\sigma(\alpha-\max_s[V]_\alpha(s))\), with upper clipping \([V]_\alpha=\min(V,\alpha)\) and \(\alpha\in[\min V,\max V]\).



### Analysis

The maximum clipped entry equals \(\alpha\), so the penalty vanishes; minimizing gives \(\min V\), regardless of \(p,\sigma\). For \(p=(1/2,1/2),V=(0,1),\sigma=1/4\), the printed result is \(0\). Feasible distributions are \(q=(1-t,t)\), with \(t\in[1/4,3/4]\), so the actual supremum is \(3/4\).



### Finding and scope

The general displayed dual is false. The current author source provides important counterevidence: alpha_min_backup uses lower clipping, and the policy routines obtain a supremum by negating an infimum of the negative value vector. Those structural implementations are consistent with the correct operation and were not executed here.



### Proposed correction

The correct full-simplex dual, with \(m=\min V,M=\max V\), is \[\sup_{\operatorname{TV}(q,p)\le\sigma}q^\top V=\min_{\alpha\in[m,M]}\{p^\top\max(V,\alpha)+\sigma(M-\alpha)\}.\] It follows by applying the valid infimum formula to \(M\mathbf1-V\) and substituting \(\alpha=M-t\). On the binary example its minimum is \(3/4\).

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: Nominal joint value does not measure unilateral robust regret

Assessment: supported; impact: minor



Source: Section 5, PDF p.10; main.py, generate_VI, figure_wrt_samples and evaluate_policies



### Source claim (paraphrase)

The experiments support equilibrium learning, but the available script compares nominal joint-policy values to a nominal baseline, without computing robust current values or unilateral best responses.



### Analysis

For the one-step game \(A=\begin{pmatrix}1&0\\0&1\end{pmatrix}\), let \(\mu=(1,0)\), \(\nu=(1/2,1/2)\). The joint value and equilibrium value are both \(1/2\), so the released absolute-value score is zero. The minimizing player can switch to column \(2\), reducing its cost to \(0\); regret is \(1/2\). Positive uncertainty radii do not affect a one-step payoff. Statically, generate_VI never uses its sigma argument; evaluate_policies performs expected nominal backups; figure_wrt_samples compares those joint values. The snapshot also differs from the paper in action count, seed count and numerical framework.



### Finding and scope

The available metric cannot certify robust Nash regret. It can legitimately describe joint-value error. The exact producing code and run histories for the published curves are not established by this snapshot, so the paper’s numerical curves are not declared fabricated or reproduced.



### Proposed correction

Evaluate each player’s robust current value and its robust best response to the fixed opponent, then report both regrets. Existing joint-value error can remain a separate descriptive metric.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 4: The concentration rate cannot cover every bounded adaptive vector

Assessment: supported; impact: major



Source: Lemma D.1, Eq.(46), PDF p.27; dependence discussion, p.28; Appendix G.1, p.51



### Source claim (paraphrase)

The lemma permits any \(V\) with \(\|V\|_\infty\le H\), explicitly without independence from the empirical transition row, but gives an empirical-Bernstein rate without a state-dimension term.



### Analysis

For uniform \(p_i=1/S\), take empirical frequencies \(\hat p\) from \(N\) independent categorical draws and choose \(I=\{i:\hat p_i>1/S\}\), \(V_i=H\mathbf1_{\{i\in I\}}\), \(\sigma=1/(2S)\). If \(\hat p\ne p\), both masses of the nonempty excess set exceed \(\sigma\). Binary TV minimization gives \[\inf_{q\in U_\sigma(\hat p)}q^\top V-\inf_{q\in U_\sigma(p)}q^\top V=H\operatorname{TV}(\hat p,p),\] while \(\operatorname{Var}_{\hat p}V\le H^2/4\).

For completeness set \(Z=\operatorname{TV}(\hat p,p)\) and let \(Y=X-N/S\), \(X\sim\operatorname{Bin}(N,1/S)\), with variance \(v=N(S-1)/S^2\ge1\). The fourth moment is at most \(4v^2\); Hölder gives \(\mathbb E|Y|\ge\sqrt v/2\). Hence \(\mathbb EZ\ge\frac14\sqrt{(S-1)/N}\). Changing one observation changes \(Z\) by at most \(1/N\); Efron–Stein gives variance at most \(1/(2N)\). Chebyshev therefore gives \[\Pr\{Z\ge\tfrac18\sqrt{(S-1)/N}\}\ge1-\frac{32}{S-1}.\]

For polynomially large \(N,K\) satisfying burn-in conditions, the proposed right side is at most \[C_4H\sqrt{\log(KH/\delta)/(4N)}+C_4H\log(KH/\delta)/N\]. Any universal \(C_4\) is eventually defeated by the state-dimension factor above. The row example embeds in a full-coverage model with uniform states and transition rows; conditioning on its row count preserves uniform independent next states. It is not asserted that Algorithm 2 produces this particular adaptive vector. Appendix G.1 instead begins with a fixed independent vector and does not supply the claimed independence-removal step.



### Finding and scope

The unrestricted adaptive-vector lemma is false at the stated rate. An algorithm-specific leave-one-out or stability proof could still establish a suitably restricted rate, but is not supplied by the displayed fixed-vector argument.



### Proposed correction

Restrict the lemma to an independent vector and separately establish the independence or dependence control needed for the actual algorithmic iterates. No replacement algorithm-specific rate is claimed here.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 5: The hard-family recursion overlooks other zero-valued absorbing states

Assessment: supported; impact: major



Source: Appendix E.1, Eqs.(86)–(100), PDF pp.37–38; Lemma E.2, Eq.(94); Appendix H.1, pp.59–60



### Source claim (paraphrase)

Equation (86) makes every \(m_j\), \(j\ne f\), an absorbing zero-reward state. The full-simplex TV set in Eq.(89) can move mass to those states, while Eq.(94b) assumes its adverse mass moves to \(m_f\).



### Analysis

Take states \((m_f,n_f,m_j,n_j)\), horizon \(H=16\), two actions, \(c_0=1/4,c_1=1/8,c_2=1/4,\sigma=1/2\), \[p=129/256,\quad \Delta=1/1024,\quad q=515/1024.\] These satisfy \(p>q\ge1/2\), \(H>16\log2\), \(\sigma\le1-c_0\), \(\sigma>c_2/(2H)\), \(\Delta\le c_1\sigma/H\) and \(p+\Delta\le1\). Choose any admissible packing vector and its good action at \(m_f\).

At time \(H\), values are \((0,1,0,1)\). At time \(H-1\), robust values are \((1/256,3/2,0,3/2)\). At \(H-2\), nature can shift mass \(1/2\) from the absorbing \(n_f\) to \(m_j\), at TV distance exactly \(1/2\). Since \(m_j\) has value zero, this is optimal and gives \(V_{H-2}(n_f)=7/4\). Equation (94b) instead adds \(\sigma V_{H-1}(m_f)=1/512\), yielding \(897/512\). The same omitted destination affects Eq.(94a).



### Finding and scope

The literal hard-family recursion and its claimed minimum-state ordering are false. Equation (98) describes a different nonabsorbing background family and is relevant evidence of possible intended wording; adopting it would require coordinated reconstruction of the construction and proof. This finding does not rule out a similar lower-bound rate from another family.



### Proposed correction

For the displayed family and \(q\ge\sigma\), write \(u_h=p\mu_h(\phi_h\mid m_f)+q\mu_h(1-\phi_h\mid m_f)\). The corrected recursions are \[V_h(m_j)=0,\quad V_h(n_i)=1+(1-\sigma)V_{h+1}(n_i),\] \[V_h(m_f)=(u_h-\sigma)V_{h+1}(n_f)+(1-u_h)V_{h+1}(m_f).\] Induction keeps the \(n_i\) tied and highest-valued, while \(m_j\) remains a minimum; moving adverse mass there verifies the formulas. The information-theoretic separation, coverage and rate must then be reanalyzed.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.

- The multiplayer extension was not independently refuted; fixed-policy robust Bellman evaluation and common-payoff special cases remain outside the adverse findings.
