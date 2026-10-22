# A Differential and Pointwise Control Approach to Reinforcement Learning



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The latest paper retains unsupported derivative-learning and staged-propagation guarantees and assigns post-fit accuracy to earlier collection episodes in its regret proof. Separate current-release findings concern label alignment, baseline objectives, simulated significance tests and transformed uncertainty bands. No benchmark ranking is recomputed.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: Stationary canonical paths need the missing optimal-control conditions

Assessment: supported; impact: minor



Source: Section 2.1, Eqs.(4)–(9), PDF p.3; Section 2.3, pp.4–5; Appendix D.1, pp.24–25; current arXiv:2404.15617v4



### Source claim (paraphrase)

Action stationarity and canonical dynamics alone do not select the optimal initial costate or impose terminal transversality. The reward described as penalizing control effort also has a positive quadratic action term under maximization.



### Analysis

Use \(\dot s=a\), \(s(0)=1\), horizon \(1\), free terminal state and reward \(-\tfrac12\int_0^1(s^2+a^2)dt\). The paper-sign Hamiltonian is \(pa+(s^2+a^2)/2\); stationarity gives \(a=-p\). Initial costate zero yields \(s=\cosh t\), \(p=-\sinh t\), satisfying the displayed equations but giving reward \(-\sinh2/4\approx-0.906715\), below the admissible zero-action reward \(-1/2\). Correct transversality instead gives \(p(1)=0\) and initial costate \(\tanh1\). Separately, maximizing \(a^2/2-1\) prefers \(a=2\) over zero, so that term alone is not an effort penalty.



### Finding and scope

The stationary-to-optimal bridge needs conditions. Appendix D’s value-gradient discussion and an abstract assumption of the optimal operator are valid restricted alternatives; neither is contradicted by the example.



### Proposed correction

State the canonical equations as necessary conditions along an appropriately selected optimal trajectory. Specify terminal conditions and the initial costate/value gradient, or explicitly assume the optimal operator; reconcile reward maximization and effort cost consistently.

A proposed correction is described; author adoption is not established.



## Problem 2: The finite derivative-learning rate needs capacity, local mass and anchor control

Assessment: supported; impact: major



Source: Definition 3.1, PDF p.5; Lemma B.3, pp.17–18; Definition B.5 and Lemma B.7, pp.18–20; current arXiv:2404.15617v4



### Source claim (paraphrase)

The stated smooth bounded-parameter conditions alone imply a finite derivative-learning sample count \(O(\epsilon^{-(2d+4)})\); the restricted proof further drops an anchor residual using its linearly bounded condition.



### Analysis

Take \(d=1\), uniform input on \([0,1]\), target \(g(x)=x\), and the permitted bounded smooth class \(\mathcal H=\{0\}\). Every derivative residual is \(1\), so for \(\epsilon=1/2\) no finite sample count succeeds. A conditional optimization statement when the target belongs to the class does not supply the absent realizability premise.

The cone step also needs sampling geometry: at \(Y=1-\epsilon_1/4\), an outward annular interval \((Y+\epsilon_1/2,Y+\epsilon_1)\) lies outside \([0,1]\) and has zero probability, contradicting a uniform positive local-mass assertion. Finally, linear boundedness controls a difference, not an anchored value: \(h_1(x)=1+x\), \(Y=1/2\), \(X=51/100\) satisfies the difference condition with constant \(1\), yet \(|h_1(X)|=1.51>0.01\). The missing term is \(|h_1(Y)|\).



### Finding and scope

The literal capacity claim is false and the proposed sample-rate proofs lack independent geometric/residual conditions. This does not refute every strengthened realizable learning theorem.



### Proposed correction

Require quantified approximation capacity, optimization tolerance and suitable local sampling mass. Retain \(|h_1(X)|\le|h_1(Y)|+C\|\nabla h_1(Y)\|\|X-Y\|\), or impose the exact interpolation needed to remove its anchor. No repaired original exponent is established.

A proposed correction is described; author adoption is not established.



## Problem 3: The staged proof changes probability and rollout-distribution guarantees

Assessment: supported; impact: major



Source: Definition 3.1 and Theorem 3.2, PDF pp.5–6; Appendix B, Eqs.(31)–(37), pp.15–16; Corollary 3.5; current arXiv:2404.15617v4



### Source claim (paraphrase)

The staged argument requires a confidence statement about mean error, retained fit after a new hypothesis is trained, and guarantees on adaptive rollout distributions; its definition and sample budgets do not supply all three.



### Analysis

A pointwise tail event does not yield the same mean threshold. For uniform \(X\in[0,1]\), set \(w=1/40\) and \(e(x)=(1-((x-1/2)/w)^2)^3\) inside the width-\(2w\) interval and zero outside. Then \(\Pr(e>0.01)<0.1\), but \(\mathbb E e=4/175>0.01\). Taking \(h(x)=\int_0^x e(u)du\) realizes a smooth derivative residual.

The base sample count uses failure probability \(\delta\), but the strengthened induction starts at \(\delta/3^{H-1}\). Reusing samples does not itself retain a population error guarantee for a newly fitted hypothesis. Nor does a continuous initial density imply the same property after rollout: locally, the allowed Euler–Hamiltonian form with \(g(s,p)=-sp/\Delta_t\) maps \((s,p)\) to \((0,2p)\), collapsing a smooth density to a line. A smooth cutoff makes the construction bounded on a compact domain. The small-step limit also requires uniform derivative and confidence/sample-budget control as \(H\) grows.



### Finding and scope

These are substantive unmet proof obligations; the supplied examples isolate invalid transitions rather than claiming to satisfy every hypothesis of a single full staged counterexample.



### Proposed correction

A sufficient operator statement explicitly assumes simultaneous bounds \(\mathbb E\|F(G^{(i)}X)-G(G^{(i)}X)\|\le\epsilon_{\rm op}\) on every relevant rollout law, with \(F\) Lipschitz. Then \(e_j\le L e_{j-1}+\epsilon_{\rm op}\) gives \(e_j\le\epsilon_{\rm op}\sum_{i=0}^{j-1}L^i\). This does not prove that the proposed sample budgets achieve those stronger assumptions.

A proposed correction is described; author adoption is not established.



## Problem 4: Post-fit accuracy cannot bound earlier collection regret

Assessment: supported; impact: major



Source: Algorithm 1, lines 2,4,6–7, PDF p.5; Eq.(20), Corollary 3.6 and Eq.(21), p.7; current arXiv:2404.15617v4



### Source claim (paraphrase)

The online training-regret proof assigns the fitted stage-\(k\) error to episodes actually collected using the previous policy, yielding the advertised \(O(K^{5/6})\) special case.



### Analysis

At permitted fixed horizon \(H=2\), there is one training stage. If the random initial policy has allowed expected episode gap \(c>0\), all \(K=N_1\) collection episodes use it, so expected collection regret is \(cK\), even if learning becomes exact immediately afterward. For \(c=1/4\), its ratio to \(K^{5/6}\) is \(K^{1/6}/4\), unbounded. This is a schedule-level conditional obstruction for any admitted nonzero initialization gap, not a newly simulated Hamiltonian benchmark.



### Finding and scope

The stated post-training accuracy does not establish the claimed online training regret. The loss incurred before fitting cannot be reduced retroactively.



### Proposed correction

Use a separate deployment statement or prove accuracy for the policies actually collecting each batch. Under extra exploration and deployment assumptions, an explore-then-deploy comparison has \(C_1\epsilon^{-\mu}+C_2K\epsilon\), giving order \(K^{\mu/(\mu+1)}\); this comparison is not a repaired dfPO theorem.

A proposed correction is described; author adoption is not established.



## Problem 5: The replay path pairs a successor score with its predecessor state

Assessment: supported; impact: minor



Source: Definition 2.1 and Eq.(12), PDF p.4; query_system.py, get_zero_order_info; memory.py, ReplayMemory._query_samples



### Source claim (paraphrase)

The oracle is defined to return a state and its own score; the public query appends a successor and its post-step value, while replay pairs values with the state list excluding its last entry.



### Analysis

For \(s_{t+1}=s_t+a_t\), \(\mathcal F(s)=s^2\), \(s_0=1\) and \(a_0=1\), the successor is \(2\) with value \(4\). Pairing that value with states[:-1] gives \((1,4)\), although \(\mathcal F(1)=1\). Correct successor pairing is \((2,4)\). Zero action is a passing special case. A next-state value target could be defined, but it is policy-dependent and differs from the paper’s same-state score.



### Finding and scope

The current public replay path has a direct label-alignment discrepancy. No effect on original trained policies is quantified.



### Proposed correction

Pair post-step values with states[1:], or query the intended current-state score before advancing. Reconcile the full stage/oracle semantics before treating a local slice change as a complete repair.

A proposed correction is described; author adoption is not established.



## Problem 6: Reward decay and baseline constructor settings differ from the description

Assessment: supported; impact: minor



Source: Section 4.2 and Appendix C.1/Table 3, PDF pp.8 and 21; envs/bbo.py; benchmarks/sb3_utils.py



### Source claim (paraphrase)

The written reward multiplier at step \(m\) is \(\gamma^{-m}\); the release divides by a squared accumulated discount, giving \(\gamma^{-2m}\). DDPG and TQC also omit supplied learning-rate and return-discount constructor arguments.



### Analysis

At \(\gamma=0.81\), first step, zero action and functional cost \(1\), the written reward is \(-1/0.81\), but the release gives \(-1/0.81^2\). For molecular \(\gamma=0.0067\), the first-step magnitude ratio is about \(149.254\). The inverse get_val uses the same squared convention and remains internally consistent, so terminal reported functional values are not thereby shown wrong. Direct constructor inspection shows four other baseline branches forward the supplied scalars, while DDPG/TQC do not.



### Finding and scope

The public baseline objective/configuration differs from the declared setup. Historical checkpoints and package versions are needed to establish original settings and ranking effects.



### Proposed correction

Reconcile the intended reward exponent and inverse conversion, pass each intended constructor setting explicitly, and retain the instantiated configuration before any benchmark reanalysis.

A proposed correction is described; author adoption is not established.



## Problem 7: The significance notebook tests simulated observations

Assessment: supported; impact: minor



Source: Appendix C.2 and Table 4, PDF p.21; analysis.ipynb, cell 4; prior public AuditOwl entry 1867



### Source claim (paraphrase)

The paper describes tests on seed-level observations, but the released notebook draws new Gaussian samples from table summaries and tests those simulated samples.



### Analysis

The cell sets sample size \(10\), calls np.random.normal separately for each method and then Welch’s ttest_ind, without reading observed seed means. For the surface comparison, its input summaries are \(6.296\pm0.048\) and \(6.365\pm0.030\). If these were independent sample means/standard deviations of size \(10\), their direct summary-statistic t value would be approximately \(-3.854809\), whereas the recorded simulated-data t value is approximately \(-1.8138\). A paired analysis would additionally require actual covariance; neither value is certified as the correct paper reanalysis here.



### Finding and scope

That cell cannot establish the stated observed-data significance test. The issue was already publicly reported; the notebook alone does not establish exclusive historical use or invented benchmark means.



### Proposed correction

Recover actual seed-level observations and apply the design-appropriate prespecified test, effect-size and uncertainty calculation. Do not replace observations by new random draws.

Previously reported in public AuditOwl entry 1867; author adoption or a corrected observed-data analysis is not established.



## Problem 8: The molecular bands are enlarged and capped display intervals

Assessment: supported; impact: minor



Source: Figure 1(c), PDF p.8; benchmarks_run.py, molecular std_scale; utils.py, _bootstrap and _tsplot



### Source claim (paraphrase)

The current molecular plotting branch uses scale \(3000\); the helper multiplies bootstrap percentile half-widths and caps each at one fifth of the median magnitude.



### Analysis

If raw percentile deviations from median \(m\) are \(d_-,d_+\), the returned endpoints are \(m-\min(3000d_-,|m|/5)\) and \(m+\min(3000d_+,|m|/5)\). Small uncapped intervals are thus widened by \(3000\); once capped around median \(100\), the interval can be \([80,120]\). Means are not changed. These bands cannot be interpreted as unscaled bootstrap intervals, although intentional visual enlargement is legitimate when labeled.



### Finding and scope

The released plotting transform requires disclosure for inferential interpretation. The exact published-figure generating revision is unresolved, and table standard deviations are not shown to use this transform.



### Proposed correction

For inferential uncertainty use the untransformed interval and state its unit/level; label any enlarged visualization with its exact factor and cap. Recover original trajectory/plotting provenance before revising published figures.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.

- The unchanged current public source is not established as the exact generator of every historical checkpoint, statistical claim or plotted figure.
