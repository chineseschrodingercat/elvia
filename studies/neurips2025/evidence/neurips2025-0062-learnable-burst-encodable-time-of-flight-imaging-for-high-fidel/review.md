# Learnable Burst-Encodable Time-of-Flight Imaging for High-Fidelity Long-Distance Depth Sensing



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The public forward model assumes the same ambient exposure for independently learned codes, and its implemented information expression differs from the Gaussian Fisher formula. No historical depth result is remeasured.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Ambient light is not integrated through each learned code

Assessment: supported; impact: minor



Source: Section 3.1, PDF p.4, Eqs.(5)–(6); network.py, lines 131–178



### Source claim (paraphrase)

Equations (5)–(6) require ambient contribution proportional to \(I_{\rm amb}\int D_i(t)\,dt\). `network.py` instead adds a shared factor based on \(500\) to every \(1000\)-sample channel.



### Analysis

Independent normalization does not force equal code sums. For valid code sums \((250,750,500,200)\) and ambient scale \(0.6\), the coded contributions are \((150,450,300,120)\); the shared implementation gives \((300,300,300,300)\). Half-duty channels are a passing special case.



### Finding and scope

The public forward model imposes an unenforced equal-duty assumption. Its historical measurement effect is unknown.



### Proposed correction

Use the actual per-channel code sum, including sample spacing and accumulation factors, in both expected intensities and information-loss curves. Derive noise variance from those same corrected means.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: The information expression is not the stated Fisher information

Assessment: supported; impact: minor



Source: Section 3.3, PDF p.6, Eq.(9); loss_function.py, lines 6–23; train.py, line 186



### Source claim (paraphrase)

For Gaussian measurements with mean \(\mu(d)\) and variance \(V(d)=\mu(d)+\nu\), Eq.(9) requires \(J=\mu^{\prime2}/V+V^{\prime2}/(2V^2)\). `loss_function.py` introduces a second-derivative term and different coefficients.



### Analysis

Taking the expectation of the squared Gaussian score yields the displayed nonnegative Fisher expression. A second derivative of the mean does not appear in that identity. A finite positive-variance quadratic mean can make the implemented sum negative while Eq.(9)’s finite-difference sum is positive, so the discrepancy is not a common normalization. Such a quadratic is a diagnostic mean, not an asserted learned code curve.



### Finding and scope

The routine does not compute Eq.(9). This does not prove an observed optimization failure in the paper.



### Proposed correction

Use \([1/V+1/(2V^2)](g\mu)^2\) under the same mean-dependent variance model. State finite-difference boundaries, the depth/phase Jacobian and the design distribution used for accumulation.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
