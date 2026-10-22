# World Models as Reference Trajectories for Rapid Motor Adaptation



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Admissible scalar systems violate the control-error floor and the value guarantee. Small one-step prediction discrepancies do not bound accumulated trajectory deviation, and action-policy optimality does not remove the value function’s state-gradient term.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: The control-error floor fails even in a scalar linear plant

Assessment: supported; impact: major



Source: Assumption 4.1 and Theorem 4.2, p.5; Appendix F, Theorem F.1 and Eqs.(9)–(16), p.16



### Source claim (paraphrase)

The static feedback \(a_t^c=-\eta J_t^{\top}e_t\) is claimed to give floor \(\sqrt{\epsilon^2+P^2/\alpha^2}\), in addition to a decaying initial term.



### Analysis

Use identity encoding, \(F(z,a)=f(z,a)=2a\), nominal action zero, \(z_0=e_0=0\), additive disturbance \(P=1/10\), \(L=\alpha=2\), \(\epsilon=0\), and \(\eta=1/10<1/4\). All declared Jacobian, mismatch and authority conditions hold. With observed-minus-nominal discrepancy indexed at the next step, \(a_t^c=-e_t/5\) and \(e_{t+1}=-2e_t/5+1/10\). Therefore \(e_1=1/10\) and \(e_t=[1-(-2/5)^t]/14\), whose limit is \(1/14\). Both exceed the claimed floor \(1/20\), while the initial term is zero. Simultaneous steady-state feedback gives the same \(1/14\); changing the printed contraction factor cannot resolve the floor contradiction.



### Finding and scope

The bound is false under the additive perturbation channel used in the appendix. The recurrence is stable, so this is not a claim of universal controller instability or a simulation failure.



### Proposed correction

For the explicitly defined delayed static recurrence, action-Lipschitz continuity and \(\kappa=\eta L^2<1\) imply \(\|e_{t+1}\|\le\kappa\|e_t\|+\epsilon+P\), hence \[\|e_t\|\le\kappa^t\|e_0\|+(\epsilon+P)\frac{1-\kappa^t}{1-\kappa}.\] This restricted bound does not certify Algorithm 1’s learned-controller updates.

A proposed correction is described; author adoption is not established.



## Problem 2: One-step error does not imply the stated value guarantee

Assessment: supported; impact: major



Source: Theorem 4.3, p.5; Appendix F, Theorem F.2 and Eqs.(17)–(19), p.16



### Source claim (paraphrase)

The value loss is bounded by \(H_M(\epsilon^2+P^2/\alpha^2)/2\), using a pure quadratic Taylor expansion and identifying trajectory deviation with one-step prediction discrepancy.



### Analysis

Let states be real, actions in \([-1,1]\), discount \(1/2\), nominal dynamics \(F(z,a)=z+a\), and \(V(z)=-z^2\). Define reward \(R(z,a)=V(z)-V(z+a)/2-a^2\). Telescoping the discounted return gives \(V(z_0)-\sum_{t\ge0}2^{-t}a_t^2\), since bounded actions imply \(2^{-T}z_T^2\to0\). Thus nominal policy zero is optimal everywhere and \(V\) is its exact optimal value, with Hessian \(-2\).

Perturb to \(f(z,a)=z+a+\delta\), with arbitrarily small \(\delta>0\), \(P=0,\epsilon=\delta,L=\alpha=1,\eta=1/2\), and zero initialization. Then \(e_{t+1}=\delta-e_t/2\), \(z_{t+1}=z_t+e_{t+1}\); controls remain feasible and \(|e_t|\le\delta\). At time \(2\), \(z_2=3\delta/2\), so the value gap from the nominal trajectory is \(9\delta^2/4>\delta^2\). For a one-step reference \(z^*=\delta\), the gap is still \(5\delta^2/4>\delta^2\), because \(V^{\prime}(\delta)=-2\delta\ne0\). The quadratic expansion is exact, so no higher-order remainder explains either violation.



### Finding and scope

The claimed implication fails even when the one-step error bound is independently true and the optimal value is globally quadratic. Neither a stable reference trajectory nor a stationary state-value reference follows from action-Jacobian bounds or policy optimality.



### Proposed correction

With an independently \(\rho\)-contractive nominal state map, tracking obeys \(d_t\le\rho^td_0+b(1-\rho^t)/(1-\rho)\). A Hessian bound on the connecting segment gives \(|V(z)-V(z^*)|\le\|\nabla V(z^*)\|d+Hd^2/2\). Removing the linear term requires an additional stationary-reference assumption; neither condition is implied by the original theorem.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.
