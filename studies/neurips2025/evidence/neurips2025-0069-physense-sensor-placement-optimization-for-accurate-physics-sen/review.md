# PhySense: Sensor Placement Optimization for Accurate Physics Sensing



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The A-optimality comparison omits covariance rank, directly invalidating its claimed dimension-independent guarantee. Determinant and released sampling/gradient/projection issues have narrower scopes.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: The A-optimality lower bound needs covariance rank

Assessment: supported; impact: major



Source: Current arXiv v5 Theorem 3.5, PDF p.5, Eqs.(3)–(4); Appendix A.2, PDF pp.16–17



### Source claim (paraphrase)

Theorem 3.5 gives \(L_F=(\pi/2)\sum_i\sqrt{\lambda_i}\) and claims \(2L_F^2/\pi^2\leq L_A=\sum_i\lambda_i\).



### Analysis

With covariance \(\operatorname{diag}(0,1,1,1)\), the zero component is exactly observed and the residual rank is \(3\). The trace is \(3\), while the asserted lower bound is \(9/2\). The proof uses \((\sum_i\sqrt{\lambda_i})^2\leq2\sum_i\lambda_i\), which requires a rank restriction not supplied.



### Finding and scope

The dimension-independent near-A-optimality comparison is false. The uniform-time Gaussian flow identity itself survives.



### Proposed correction

For rank \(r>0\), Cauchy–Schwarz gives \(4L_F^2/(r\pi^2)\leq L_A\leq4L_F^2/\pi^2\). Handle rank zero separately; the factor now depends on residual rank.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Trace does not give a positive determinant lower bound

Assessment: supported; impact: minor



Source: Current arXiv v5 Remark A.1, PDF p.17



### Source claim (paraphrase)

Remark A.1 extends trace comparisons to a two-sided determinant guarantee without a uniform spectral assumption.



### Analysis

At trace \(1\), \(\operatorname{diag}(1-\epsilon,\epsilon)\) has determinant \(\epsilon(1-\epsilon)\to0\). Removing observed zero-variance directions does not remove this positive-eigenvalue example. A log determinant similarly tends to negative infinity.



### Finding and scope

The determinant extension needs additional spectral conditions. Rank-dependent maximum-eigenvalue comparisons remain available.



### Proposed correction

Retain the AM–GM upper bound and state any uniform eigenvalue lower bounds needed for a two-sided relation.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: Logit-normal time changes the objective proved in the paper

Assessment: supported; impact: minor



Source: Current arXiv v5 Eq.(1), PDF p.4; Appendix A.2, PDF pp.16–17; Sea-Temperature/runners/exp_senseiver_rect_flow_sea_walk.py, time sampler



### Source claim (paraphrase)

The Gaussian identity integrates uniformly over \(t\in[0,1]\). Released placement runners instead use \(t=\operatorname{sigmoid}(U)\), \(U\sim\mathcal N(0,1)\), without inverse-density weights.



### Analysis

For scalar residual variance \(1\), the ideal residual integral changes from \(\pi/2\approx1.5708\) to approximately \(1.74126\). As variance grows, this logit-normal objective is bounded by \(1+2e^{1/2}+e^2\), while the trace diverges. Thus the surviving uniform-time comparison does not automatically apply to that release objective.



### Finding and scope

The public sampler targets a different functional. Historical experimental effects are unknown.



### Proposed correction

Use uniform time, or a justified importance weight \(1/q(t)\) for sampling density \(q\). Such weights may have poor variance; retaining logit-normal time instead requires an explicitly different objective and analysis.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 4: Sea interpolation severs coordinate gradients

Assessment: supported; impact: minor



Source: Section 3.2, PDF pp.4–5, Eq.(2); sea-temperature runner position interpolation



### Source claim (paraphrase)

The sea-temperature runner optimizes sensor coordinates through `bilinear_interp_with_mask`.



### Analysis

The helper constructs torch.tensor([wa,wb,wc,wd]) from coordinate-dependent tensor values, creating a detached tensor. Integer cell lookup supplies no replacement derivative. Sea-Temperature/models/physense_for_sea_crossattn_walk.py, forward, accepts row_indices and col_indices but does not read them; it uses the already sampled values and positional features. For the smooth interior field \(u(x,y)=x+2y\), the correct coordinate derivatives are \((1,2)\), which this detached route cannot supply.



### Finding and scope

The intended local coordinate gradient is absent in this public path. Mask and geometric feasibility remain separate.



### Proposed correction

Use a graph-preserving stack for the weights. Away from cell changes and with a nonzero retained-mask weight sum, this restores the ordinary bilinear derivative without establishing a complete ocean-feasible placement algorithm.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 5: The revised car projection is approximate

Assessment: supported; impact: minor



Source: Section 3.2, PDF p.5, Eq.(2); Appendix C.3, PDF p.26; repository issue #2 and later projection revision



### Source claim (paraphrase)

Repository issue #2 documented the historical missing projection call; the later release applies a local tangent-plane blend. The README identifies it as approximate.



### Analysis

Even with an exact plane projection, default blend \(\beta=1/2\) moves proposal \((0,0,1)\) toward \((0,0,0)\) only to \((0,0,1/2)\), which remains off the plane. Estimating the tangent plane adds another approximation.



### Finding and scope

The current update is not exact feasibility projection. This preserves both the acknowledged historical omission and its later replacement; it does not allege that no correction call exists.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
