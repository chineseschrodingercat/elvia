# Exploring Neural Granger Causality with xLSTMs: Unveiling Temporal Dependencies in Complex Data



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The public weighted shrinkage is not its intended proximal map; cross-station normalization changes the graph’s interpretation. Released Lorenz sampling/noise and training settings also differ from the methods description. Historical benchmark effects remain unresolved.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: The released weighted shrinkage is not the proximal map

Assessment: supported; impact: minor



Source: Section 3.2, Eq.(4), PDF p.5; Algorithm 1, line 16, PDF p.21; models/clstm.py, lines 342–360



### Source claim (paraphrase)

For fixed positive normalized weights, the compression step should minimize \(J(U)=\tfrac12\|U-W\|_F^2+\sum_jt_j\|U_j\|_2\). The release instead divides a column by \(\max(\|W_j\|_2,\lambda\eta)\), even when its weighted threshold is smaller.



### Analysis

Take two columns \(W=(1/2,2)\), \(\lambda\eta=1\), and \(\alpha=(1/10,9/10)\), embedded in the allowed hidden dimension by zero padding. Grant the release’s threshold convention \(t=2\alpha=(1/5,9/5)\). It returns \((0.15,0.20)\), whereas columnwise soft thresholding gives \((0.30,0.20)\). The objective values are respectively \(2.07125\) and \(2.06\); the first-coordinate derivative at the release output is \(0.15-0.5+0.2=-0.15\), so the return is not the unique minimizer. Uniform weights are a passing special case.



### Finding and scope

The public nonuniform-weight operator differs from the correct printed formula. Its later optimization and benchmark effects are unmeasured.



### Proposed correction

Use \((1-t/r)_+w\) for \(r=\|w\|_2>0\), with zero output for a zero column. Cauchy–Schwarz reduces the objective to \(\tfrac12(s-r)^2+ts\), uniquely minimized by \(s=(r-t)_+\). Match the threshold scaling to the stated objective.

A proposed correction is described; author adoption is not established.



## Problem 2: Cross-station normalization changes the channel histories

Assessment: supported; impact: minor



Source: Appendix C, Moléne description, PDF p.22; prepare_data.py, lines 66–84



### Source claim (paraphrase)

The released Moléne loader normalizes across stations at each time: \(Y_{j,t}=(X_{j,t}-\min_\ell X_{\ell,t})/(\max_\ell X_{\ell,t}-\min_\ell X_{\ell,t})\). A graph of these channels need not describe raw-station history relations.



### Analysis

Use independent stationary channels \(X_t=(0,U_t,1,M_t)\), with \(U_t\) iid uniform on \([1,2]\) and \(M_t=3+M_{t-1}/2+\eta_t\), where \(\eta_t\) is iid uniform on \([-1,1]\). Its stationary solution lies in \([4,8]\). No raw channel causes another. Normalization gives \(Y_t=(0,B_t,C_t,1)\), with \(B_t=U_t/M_t\) and \(C_t=1/M_t\). The marker history reveals the previous autoregressive state, and the conditional prediction is \[\mathbb E[B_t\mid M_{t-1}=m]=\frac34\log\frac{4+m/2}{2+m/2}.\] It is strictly decreasing, taking approximately \(0.275794\) at \(m=5\) and \(0.232616\) at \(m=7\).

Even given \(M_{t-2}=m_0\) and the complete earlier target history, observing \(B_{t-1}=b\) leaves the fresh state on the nontrivial interval \((a-1,a+1)\cap(1/b,2/b)\), where \(a=3+m_0/2\). Its conditional density is proportional to \(m\). Thus the strictly varying conditional prediction is not recoverable from the target’s entire history, while the marker reveals it. This establishes a newly created predictive relation, not merely one-step correlation.



### Finding and scope

The normalization is legitimate for a graph of relative temperatures. Inferring raw physical station relations requires a separate justification; no actual weather edge is disproved here.



### Proposed correction

For raw-channel history preservation, fixed invertible channelwise affine transforms \(Y_{j,t}=a_jX_{j,t}+b_j\), \(a_j\ne0\), preserve each history sigma-field. Otherwise identify the target as the transformed-variable graph.

A proposed correction is described; author adoption is not established.



## Problem 3: The public Lorenz generator uses a different observation protocol

Assessment: supported; impact: minor



Source: Appendix C, Lorenz-96, PDF p.22; synthetic.py, lines 60–79; prepare_data.py, lines 93–97



### Source claim (paraphrase)

The paper specifies output spacing \(0.05\) and noise added at each simulation step. The loader retains the generator’s default \(\delta=0.1\), and the source adds noise after deterministic integration.



### Analysis

With \(N=T+B\) inclusive grid points from zero to \(N\delta\), actual output spacing is \(N\delta/(N-1)\). At \(T=500\) and \(B=1000\), this is \(150/1499\approx0.100067\). The separate post-integration addition makes observational noise: unlike \(z_{k+1}=az_k+\epsilon_k\), an earlier observation perturbation cannot propagate into a later deterministic state. If “each step” meant observational noise, that portion is descriptive ambiguity rather than a stochastic-model error.



### Finding and scope

The inspected generator does not match the reported spacing; noise placement is explicit in the source. Which version generated the published scores remains unresolved.



### Proposed correction

Pin the historical generator and choose output times \(t_k=k\Delta\) for the intended spacing. Specify observational versus process noise before any experiment revision; an arbitrary stochastic-solver substitution is not justified.

A proposed correction is described; author adoption is not established.



## Problem 4: The release does not honor the described batch and optimizer settings

Assessment: supported; impact: minor



Source: Section 4, Training and Evaluation Details, PDF p.7; models/clstm.py, lines 497–568; F40T500.yaml



### Source claim (paraphrase)

The paper describes full-batch Adam, weight decay \(0.1\), learning-rate warmup \(2000\) and coefficient warmup \(1500\). The public path uses replacement minibatches and constructs AdamW without forwarding the declared decay.



### Analysis

The sampler requests \(256\,\mathrm{max\_iter}\) replacement draws and the loader hardcodes batch size \(256\), regardless of the exposed argument. With \(T=500\), context \(10\) and stride \(1\), there are \(490\) windows, so such an update is not full batch. The optimizer call forwards only learning rate; logging a decay value in extra keyword arguments does not apply it. The released configuration uses warmup \(2200\) and coefficient start \(2000\). Generic minibatch pseudocode does not resolve the explicit full-batch experimental description.



### Finding and scope

These are distinct reproducibility settings. Neither stochastic optimization nor AdamW is intrinsically invalid, and published-result correspondence is not established.



### Proposed correction

Expose and forward the selected optimizer parameters, honor an explicit full-batch or minibatch mode, and retain the resolved experiment configuration. No replacement training run is validated.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.

- The pinned public release is not established as the program that generated every original checkpoint or benchmark score.
