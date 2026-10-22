# Bootstrap Off-policy with World Model



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The conditional-policy KL premise does not imply the stated return bound, and the Gaussian concentration radius is dimensionally invalid. A separate mixture inference fails, while public objective/helper discrepancies remain release-level concerns.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Per-state policy KL does not uniformly control discounted occupancy

Assessment: supported; impact: major



Source: Theorem 1, Eq.(6), PDF p.6; Appendix A.2, PDF pp.15–16



### Source claim (paraphrase)

Theorem 1 assumes \(D_{\mathrm{KL}}(\beta(\cdot\mid s)\Vert\pi(\cdot\mid s))\leq\varepsilon\) at every state and asserts \(J(\beta)-J(\pi)\leq R_{\max}\sqrt{2\varepsilon}/(1-\gamma)\).



### Analysis

Use states \(u,b\), start at \(u\), and let \(b\) be absorbing. At \(u\), positive actions enter \(b\), nonpositive actions stay; rewards are \(r(u,a)=0\), \(r(b,a)=-1\). Behavior is uniform on \([-1,0]\); the learned policy places mass \(0.99\) there and \(0.01\) uniformly on \((0,1]\). At \(b\) the policies agree. Every conditional KL is at most \(\varepsilon=-\log0.99\). With \(\gamma=0.99\), the behavior return is zero and the learned return is \(-[1/(1-\gamma)-1/(1-0.99\gamma)]\approx-49.74874\). The asserted bound is only \(\sqrt{-2\log0.99}/0.01\approx14.17768\). Conditional action closeness does not supply uniform future occupancy closeness.



### Finding and scope

Theorem 1 is false under its stated conditional-policy premise. The counterexample uses the same start law, kernel and bounded rewards. No Gaussian-policy restriction is stated in this theorem.



### Proposed correction

The original return bound follows if every joint state-action marginal instead has KL at most \(\varepsilon\). Under only the original per-state premise, the trajectory chain rule gives prefix KL at most \((t+1)\varepsilon\), leading to the weaker sum \(R_{\max}\sum_{t\geq0}\gamma^t\sqrt{2(t+1)\varepsilon}\).

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: The Gaussian radius omits necessary dimension dependence

Assessment: supported; impact: major



Source: Lemma 4, Appendix A.1, PDF pp.14–15; Theorem 2 proof, PDF pp.16–17



### Source claim (paraphrase)

Lemma 4 asserts \(\Pr(\|a-\mu\|_2\leq\sqrt{2\Lambda\log(1/\delta)})\geq1-\delta\) for \(a\sim\mathcal N(\mu,\Sigma)\), where \(\Lambda=\lambda_{\max}(\Sigma)\).



### Analysis

Take \(a\sim\mathcal N(0,I_4)\) and \(\delta=1/20\). The squared radius is \(2\log20\). Exact \(\chi^2_4\) coverage is \(1-(1+\log20)/20\approx0.800213\), below the promised \(0.95\). The missing trace and dimension terms cannot be discarded from a norm concentration inequality.



### Finding and scope

The lemma and uses of this radius in Theorem 2’s proof are invalid as stated. This does not measure any empirical policy error.



### Proposed correction

A valid Gaussian bound uses squared radius \(\operatorname{tr}\Sigma+2\sqrt{\operatorname{tr}(\Sigma^2)x}+2\Lambda x\), with \(x=\log(1/\delta)\). It follows from the centered Gaussian quadratic-form moment bound and Chernoff’s inequality.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: Mixture KL cannot be assigned to each component without an information term

Assessment: supported; impact: minor



Source: Appendix A.3, PDF p.17, step (2); Eq.(8), PDF p.6



### Source claim (paraphrase)

Appendix A.3 uses \(D_{\mathrm{KL}}(\beta\Vert\pi)\leq\varepsilon\), with \(\beta=\sum_iw_iP_i\), to infer \(\|\mu_i-\mu_\pi\|\leq\sqrt{2\varepsilon\Lambda(\Sigma_\pi)/w_i}\) for every Gaussian component.



### Analysis

Let \(\beta=\tfrac12\mathcal N(-1/2,1)+\tfrac12\mathcal N(1/2,1)\) and \(\pi=\mathcal N(0,1)\). Its KL is at most \(\log\cosh(1/4)\leq1/32\), yet either mean shift \(1/2\) exceeds the inferred \(\sqrt{1/8}\). For component label \(Z\), the exact identity is \(\sum_iw_iD_{\mathrm{KL}}(P_i\Vert\pi)=D_{\mathrm{KL}}(\beta\Vert\pi)+I(Z;A)\). The omitted mutual information is nonnegative.



### Finding and scope

The component-mean inference fails. This example alone does not refute every separately capped final radius.



### Proposed correction

Using \(I(Z;A)\leq H(w)\) gives component KL at most \((\varepsilon+H(w))/w_i\) for \(w_i>0\); replace the numerator in the mean bound accordingly. Remove zero-weight components before dividing.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 4: The released actor path differs from forward-KL replay alignment

Assessment: supported; impact: minor



Source: Section 3.2, PDF pp.4–5, Eqs.(2)–(5); Algorithm 1, PDF p.6; released policy loss



### Source claim (paraphrase)

Section 3.2 derives a replay-action expectation of \(-\log\pi_\theta(a_\beta\mid s)\). The applicable author paths are `boom/boom_alg.py`, `update_pi`, lines 235–284, and `boom/common/math.py`, `gaussian_logprob`, lines 26–31.



### Analysis

`update_pi` ignores the replay action, samples current-policy actions and substitutes the current-policy standard deviation, so it does not evaluate the derived replay-action cross-entropy. This concern was previously raised in repository issue #2; closure alone establishes neither correction nor author acceptance. Separately, the density helper multiplies an already summed residual by the dimension. For \(d=2\), standardized residual \((1,1)\) and log standard deviation \(0\), it gives approximately \(-3.837877\) rather than the correct \(-2.837877\).



### Finding and scope

These are public implementation discrepancies. Their effect on the original experiments is unknown.



### Proposed correction

For diagonal Gaussian density, sum coordinate residuals once and subtract \(d\log(2\pi)/2\) once. To implement the stated forward-KL target, evaluate policy density and intended weights on the same replay actions; specify any stopped-gradient weights and transformed-policy Jacobian.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
