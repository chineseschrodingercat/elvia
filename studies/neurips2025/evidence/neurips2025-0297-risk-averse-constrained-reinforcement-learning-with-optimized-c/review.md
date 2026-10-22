# Risk-Averse Constrained Reinforcement Learning with Optimized Certainty Equivalents



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current release centers away the outer surrogate gradient at correct unit ratios and pairs noisy actions with different-action likelihoods. A separate polynomial OCE example refutes one claimed smooth-max sufficient condition, while the explicitly conditional convergence theorem survives.



## Scope

Rapid, claim-focused reading of the latest applicable author-paper and resource passages. Direct mathematical or static-source reasoning is stated below. No author program, retained verifier, model inference or benchmark was executed.



## Problem 1: Full-batch centering removes the prescribed outer gradient at unit likelihood ratios

Assessment: supported; impact: minor



Source: Proceedings Algorithm 1, PDF p.7, steps 5–6; current author wrapper/RA_C_RL.py, opt_var_update, lines 49–117; utils/storage.py, full_batch_generator, lines 148–170



### Source claim (paraphrase)

Algorithm 1 updates risk variables by sample-Lagrangian derivatives. The release instead differentiates a full-batch normalized PPO surrogate with respect to those reward parameters.



### Analysis

Let the unnormalized advantages be \(A_j(\lambda,t)\) and \(\widehat A_j=(A_j-\overline A)/(s(A)+10^{-5})\). Their sum is identically zero. The full-batch generator shuffles without splitting. With the unchanged policy and matching stored actions/log probabilities, all likelihood ratios are \(1\), and clipping leaves them unchanged. Thus \[\mathcal L_{\rm action}=-N^{-1}\sum_j\widehat A_j\equiv0,\qquad\nabla_{\lambda,t}\mathcal L_{\rm action}=0.\] Returns and value predictions are detached before the value loss, so it cannot restore the outer derivative.

The source stage reward is \(\widetilde r=r+\lambda[c+t-\beta^{-1}(t+v)_+]\). Take rewards \((1,2,3,4)\), velocities \((2,3,4,5)\), \(\gamma=0.9,\beta=0.5,c=1,(\lambda,t)=(0.4,-1)\). Every hinge is strictly active. The fixed-data discounted Lagrangian has derivatives \(\partial_\lambda\widehat L=-16.292\) and \(\partial_t\widehat L=-1.3756\), in contrast to the surrogate’s exact zero. Any positive sum/mean rescaling retains the discrepancy.

The collector permits zero additional action noise, making the unit-ratio case admissible. The paper’s noisy default also has the separate bookkeeping defect below; therefore this argument does not claim that every published noisy run freezes its outer parameters. Nonunit ratios can produce a derivative, but do not derive the prescribed sample-Lagrangian gradient.



### Finding and scope

The inspected current implementation fails to implement the outer update in this valid setting. No published learning curve is declared numerically false from that source discrepancy alone.



### Proposed correction

The existing prescription differentiates the fixed-policy sampled Lagrangian directly, then applies \(\lambda^+=\Pi_\Lambda(\lambda-\eta_\lambda\partial_\lambda\widehat L)\) and \(t^+=\Pi_{\mathcal T}(t+\eta_t\partial_t\widehat L)\). Its local derivatives and signs agree with the exact example; full training integration is not established.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Problem 2: Execution noise changes the action but not its stored old likelihood

Assessment: supported; impact: minor



Source: Proceedings Section 4.1, PDF p.8; current author wrapper/RA_C_RL.py, collect_data, lines 25–39; wrapper/PPO.py analogous collector



### Source claim (paraphrase)

The paper adds Gaussian execution noise of standard deviation \(0.05\). The source samples an action and its log probability, adds noise to that action in place, executes it, and stores the changed action with the earlier log probability.



### Analysis

With \(a\sim\pi_{\rm old}\) and execution noise \(\epsilon\), reevaluation constructs \(\rho=\pi_{\rm new}(a+\epsilon\mid s)/\pi_{\rm old}(a\mid s)\). The likelihood terms refer to different random variables. Even for an unchanged standard-normal policy, \[\rho=\exp\{-[(a+\epsilon)^2-a^2]/2\},\] which is generally not \(1\). For example, \(a=1,\epsilon=0.05\) yields \(e^{-0.05125}\ne1\).



### Finding and scope

The action-likelihood pairing is inconsistent in the inspected noisy collection paths. This does not measure its effect on returns, costs or published curves.



### Proposed correction

Keep the latent sampled action with its original policy likelihood, and send a separate noise-perturbed action to the environment. The independent noise then belongs to the transition kernel. Alternatively, both densities must describe the actual convolved executed-action law. Recomputing only one unconvolved Gaussian density is insufficient.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Problem 3: Unique inner optimizers do not imply a Lipschitz gradient

Assessment: supported; impact: minor



Source: Proceedings Appendix A.7, scenario 1, PDF p.19; Assumption 3.8, p.7; Theorem 3.12, p.8; current arXiv v 2 corresponding Appendix A.7



### Source claim (paraphrase)

Scenario1 asserts that a smooth base Lagrangian and unique inner maximizers give twice continuous differentiability and hence Lipschitz smoothness of the maximized value.



### Analysis

An OCE instance realizes \(F(\theta,t,\lambda)=2+(\lambda-1)\theta-\theta^4/4\). Use one recurrent state, actions and policy parameter in \([-1,1]\), \(\gamma=1/2\), linear utility \(g(u)=u\), rewards \(r_0=(1-\gamma)(2-a-a^4/4)\) and \(r_1=(1-\gamma)a\), threshold \(0\), \(\mathcal T=[0,2]\times[-1,1]\), and \(\Lambda=[7/8,9/8]\). Rewards are bounded; the action \(1/2\) is strictly feasible.

The smooth polynomial objective has a unique interior maximizer \(\theta^*=\sqrt[3]{\lambda-1}\). Direct substitution gives \[V(t,\lambda)=2+\tfrac34|\lambda-1|^{4/3},\qquad\partial_\lambda V=\operatorname{sgn}(\lambda-1)|\lambda-1|^{1/3}.\] The derivative quotient at \(\lambda=1\) is \(|h|^{-2/3}\to\infty\). Thus compactness, uniqueness and an infinitely differentiable base objective do not imply the stated smoothness. The inner family contains the exact maximizer; this does not test a separate universal-policy-parametrization premise.

Theorem 3.12 explicitly assumes smoothness, which this example violates. It remains a conditional theorem. The stronger second-order scenarios and the distinct smoothing alternative are not refuted by this example.



### Finding and scope

Restrict the claimed sufficient-condition route; the example refutes that implication rather than the conditional convergence theorem.



### Proposed correction

The supplied sufficient replacement uses uniform strong concavity \(\mu>0\), a cross-gradient Lipschitz bound \(B\), and joint outer-gradient bounds \(L_{zz},L_{z\theta}\). Variational inequalities give \(\operatorname{Lip}(\theta^*)\leq B/\mu\), then the envelope formula gives \(\operatorname{Lip}(\nabla V)\leq L_{zz}+L_{z\theta}B/\mu\). These stronger conditions are not asserted for arbitrary neural RL objectives.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- Mathematical counterexamples and source discrepancies do not remeasure published experiments; historical execution results were not rerun.
