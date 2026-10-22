# MDNS: Masked Diffusion Neural Sampler via Stochastic Optimal Control



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Exact counterexamples refute the stated KL accuracy threshold, a general SOC existence argument and the unrestricted UDNS extension. Potts and normalization discrepancies are separate release-level findings.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: The KL threshold does not imply single-draw accuracy

Assessment: supported; impact: major



Source: Proposition 2, PDF p.7; proof p.26; total-variation convention p.28



### Source claim (paraphrase)

The proposition asserts probability at least \(3/4\) of relative partition-estimator error at most \(\varepsilon\) when either path KL is at most \(\varepsilon^2/2\).



### Analysis

Use one masked coordinate with three clean states and common unmasking rate \(1/(1-t)\). Set proposal \(q=(1/4,1/4,1/2)\), target \(p=(2/5,1/10,1/2)\), and \(U_i=-\log p_i\), so \(Z=1\). The jump-time laws agree and path likelihood ratios are \(p_i/q_i=(8/5,2/5,1)\). For \(\varepsilon=1/2\), success occurs only in the third state, with probability \(1/2\). Yet \(D_{\rm KL}(p\Vert q)\approx0.0963724\) and \(D_{\rm KL}(q\Vert p)\approx0.111572\), both below \(1/8\). The full-support importance estimator is still unbiased.



### Finding and scope

The stated normalizer-accuracy guarantee is false in a valid masked process. Sampling quality and unbiasedness are separate claims and are not refuted by this witness.



### Proposed correction

Under target absolute continuity, Markov and Pinsker give failure probability at most \[\sqrt{2\min(D_{\rm KL}(P\Vert Q),D_{\rm KL}(Q\Vert P))}/\varepsilon\]. The sufficient threshold \(\varepsilon^2/32\) recovers success probability \(3/4\).

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Potts baseline collapses match counts into Boolean presence

Assessment: supported; impact: minor



Source: Eq.(18), PDF p.9; utils_potts.py, Metropolis energy calculation, lines 240–249, and Glauber update



### Source claim (paraphrase)

The Potts energy counts every matching neighboring spin. The release adds Boolean NumPy arrays without converting them to integer counts.



### Analysis

On a periodic \(3\times3\) lattice with three states, \(J=1,h=0,\beta=1.2\), change one spin in the all-zero configuration to state \(1\). Four matching edges disappear, so the correct Metropolis acceptance is \(e^{-4\beta J}\approx0.00822975\). Boolean addition retains one true entry instead of count four, giving \(e^{-\beta J}\approx0.301194\). All reverse one-site moves are accepted, so target-weighted incoming and outgoing fluxes at the all-zero state are respectively \(\pi(s_0)e^{-4\beta J}\) and \(\pi(s_0)e^{-\beta J}\); the target is not stationary for this kernel.



### Finding and scope

The released local sampler is wrong for the stated Potts target. Its exact contribution to published baseline tables requires code-to-run provenance; longer burn-in alone cannot fix the target mismatch.



### Proposed correction

Cast each comparison to integers before adding, or stack and sum with an integer reduction. Use the resulting integer neighbor count in the Metropolis difference and Glauber conditional.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: UDNS discretization and zero-time boundary lack valid domain conditions

Assessment: supported; impact: major



Source: Appendix F.1, PDF pp.38–40; Algorithm 4 and Appendix F.3, pp.41–42



### Source claim (paraphrase)

The UDNS Euler kernel uses nonnegative learned scores and an early start near zero with \(\gamma(t)=1/t\), without an exit-rate step bound.



### Analysis

For the stated \(D=16,N=2,K=50\), choose \(\epsilon=1/1000\) and the reference score identically one. The first step has \(\Delta t=999/50000\); each flip probability is \(9.99\), and the stay probability is \(1-16(9.99)=-158.84\). Even the reference kernel needs \(\epsilon\geq4/29\). Separately, integrating \(1/t\) from zero gives immediate endpoint independence: \(\Pr(X_t\ne X_0)=1-N^{-D}\) at every positive time, incompatible with right continuity at zero. At finite \(\epsilon\), exact independence is lost; for a two-state target \((3/4,1/4)\), the uniformly initialized exact transformed process instead ends with first-state probability \(3/4-3\epsilon^2/[4(4-\epsilon^2)]\).



### Finding and scope

The literal extension is not a stochastic Euler algorithm throughout its declared score/start domain, and its singular initial path law needs separate formulation. This does not invalidate the distinct one-jump masked process.



### Proposed correction

Enforce \(\Delta t\max_x[-Q_t(x,x)]\leq1\), with appropriate support restrictions for weights. Formulate the process from a positive initial time or an entrance law and rederive its boundary/weight statements; clipping probabilities alone does not restore them.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 4: A nonmemoryless reference can have a fixed-initial control optimum

Assessment: supported; impact: major



Source: Section 3.1, PDF p.4; Lemma 8 and Remark 1, p.24



### Source claim (paraphrase)

The paper infers nonexistence of an SOC solution when the globally tilted path law fails the prescribed initial boundary.



### Analysis

For bounded finite-state rates and finite reward, define \(h_t(x)=E_0[e^{r(X_T)}\mid X_t=x]\). The conditional tilt \(dP^\dagger/dP^0=e^{r(X_T)}/h_0(X_0)\) preserves the prescribed initial law \(\mu\). For every admissible \(P\) with that law, \[J(P)=D_{\rm KL}(P\Vert P^\dagger)-E_\mu\log h_0.\] Thus it is the unique minimizing path law, regardless of endpoint independence. For the two-state rate-one switching chain, \(\mu=(1/2,1/2),T=1,e^r=(1,2)\), endpoints remain dependent and \(h_0=((3-e^{-2})/2,(3+e^{-2})/2)\) is nonconstant, yet this admissible optimum exists.



### Finding and scope

Incompatibility of a global tilt does not imply nonexistence of the constrained optimum. The deterministic masked initial state makes global and conditional normalization agree there, preserving that special construction.



### Proposed correction

Use the conditional tilt and Doob rates \(Q^\dagger_t(x,y)=Q^0_t(x,y)h_t(y)/h_t(x)\), or explicitly assume \(h_0\) is constant on the initial support before using global-tilt marginals.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 5: Released loss and reward normalizations differ from the estimators

Assessment: supported; impact: minor



Source: Eq.(16), PDF p.7; utils_train.py, loss_wdce, lines 72–94; rnd reward accumulation



### Source claim (paraphrase)

The release repeats softmax-normalized importance weights and then averages over the full batch; reward callbacks omit the displayed \(D\log N\) offset.



### Analysis

With normalized weights \(\omega_i\) and \(R\) remasking replicates, the stated self-normalized loss is \(\sum_i\omega_i R^{-1}\sum_r\ell_{ir}\). A mean over \(BR\) weighted entries instead returns this divided by \(B\). For the reward, subtracting \(\log N\) at every unmasking step while supplying only \(-U\) gives \(W_{\rm code}=W_{\rm paper}-D\log N\), so the expectation estimates \(Z/N^D\). At \(D=4,N=2,U=0\) with a uniform model, it returns weight \(1\) although the physical partition sum is \(16\).



### Finding and scope

These are normalization discrepancies. A fixed positive loss scale preserves ideal minimizers, and a common log-weight offset preserves normalized weights and ESS; neither proves wrong normalized samples or a published ranking reversal.



### Proposed correction

Remove the extra batch averaging factor and state whether the estimated normalizer is a counting-measure partition sum or a uniform-reference expectation. Add \(D\log N\) when reporting physical \(\log Z\).

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
