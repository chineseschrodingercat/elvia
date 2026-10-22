# Dendritic Resonate-and-Fire Neuron for Effective and Efficient Long Sequence Modeling



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Branch magnitudes do not give the exact real-soma response, and full adaptive-threshold differentiation includes history. The claim that fixed-width BPTT inherently has quadratic work is false; the public adaptive path is separately incomplete.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Branch responses must retain phase before aggregation

Assessment: supported; impact: minor



Source: Section 4.2, PDF p.5, Eqs.(7)–(10); Appendix A.3, PDF pp.22–23



### Source claim (paraphrase)

Equation (10) equates the soma response magnitude with a weighted sum of individual branch magnitudes.



### Analysis

Two stable poles \(\pm ie^{-1}\), unit gains and DC input give individual-magnitude sum \(2/\sqrt{1+e^{-2}}\approx1.87702\). The actual real-soma gain is \(2/(1+e^{-2})\approx1.76159\). Positive weights do not align complex phases. The chosen poles correspond to positive time constants and allowed discrete frequencies.



### Finding and scope

The exact response equality is wrong. Useful broader sensitivity or a declared heuristic coverage score remains possible.



### Proposed correction

Combine complex transfer functions first, with \(|\sum_iC_iH_i|\leq\sum_i|C_i||H_i|\). For a real soma/input, derive the real impulse response before taking its Fourier transform.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: The full surrogate gradient includes threshold history

Assessment: supported; impact: minor



Source: Section 4.3, PDF pp.5–7, Eqs.(11)–(16); Appendix B.1, PDF p.25



### Source claim (paraphrase)

The two-stage graph uses preliminary spikes \(b_t=\Theta(u_t-V_0)\), threshold \(v_t=V_0+\sum_k\alpha_kb_{t-k}\), and final spikes \(s_t=\Theta(u_t-v_t)\).



### Analysis

Under surrogate \(G\), earlier soma derivative is \(-G(u_t-v_t)\alpha_{t-r}G(u_r-V_0)\). A current-time-only formula omits this path. With \(u_1=w,u_2=0.9w,w=1.25,V_0=1,\alpha_1=0.5\), loss \(s_2\), and the actual supplemental triangular surrogate, the full derivative is \(0.625(0.9-0.5\cdot0.75)=0.328125\), versus detached/local \(0.5625\). The numeric control is not the paper’s stated double-Gaussian surrogate; the general missing-path identity applies when its factors are nonzero.



### Finding and scope

The displayed local expression is not the unrestricted surrogate chain rule. Explicitly detached-history training would be a legitimate different rule.



### Proposed correction

Include the history adjoint or name the stop-gradient rule and analyze it separately. The public main path disables adaptation, so this does not identify historical model gradients.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: Fixed-state BPTT has linear arithmetic work

Assessment: supported; impact: major



Source: End of Section 3.2 and Figure 1(c), PDF p.4; Appendix B.2, PDF p.25



### Source claim (paraphrase)

Sections 3.2–4.1 and Appendix B.2 attribute \(O(L^2)\) work to recursive BPTT dependencies and describe FFT training as an asymptotic reduction to \(O(L\log L)\).



### Analysis

For fixed-state recurrence \(u_t=au_{t-1}+wx_t\) and loss \(\mathcal L=\sum_tu_t^2/2\), compute each forward state once. Reverse adjoints satisfy \(\lambda_t=u_t+a\lambda_{t+1}\), and \(d\mathcal L/dw=\sum_t\lambda_tx_t\). Each of the \(L\) forward and reverse steps has constant work, proving \(\Theta(L)\) despite shared parameters and temporal dependence. Fixed-cost nonlinear reset/surrogate nodes do not introduce another factor of \(L\).



### Finding and scope

The paper’s general quadratic-BPTT premise and claimed work reduction are false. Linear temporal span and GPU utilization differ from arithmetic work; reported wall-clock speedups can still be true.



### Proposed correction

Compare linear-work recurrent differentiation, quadratic naive dense convolution and FFT convolution with explicit width, branch, memory and parallel-span assumptions.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 4: The principal public neuron path leaves adaptation commented out

Assessment: supported; impact: minor



Source: Section 4.3, PDF pp.5–7; Table 4, PDF p.9; supplemental models/layers.py, lines 100–131



### Source claim (paraphrase)

In supplemental `models/layers.py`, `BiRFModel` defines static-threshold spikes while adaptive construction and use remain comments.



### Analysis

Soma values \((1.25,1.25)\) give static output \((1,1)\). With baseline threshold \(1\) and prior-spike weight \(0.5\), the stated adaptive graph instead gives \((1,0)\). Adaptive utilities and post-hoc plotting code exist elsewhere, so the mechanism is not absent everywhere. Missing source/entry-point mapping and the surrogate difference prevent inferring the original private training path.



### Finding and scope

The principal public forward method is not a complete implementation of the adaptive variant.



### Proposed correction

Identify the actual adaptive training module and per-experiment configuration rather than treating post-hoc plots or commented code as activated training. No complete repaired experiment is supplied.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
