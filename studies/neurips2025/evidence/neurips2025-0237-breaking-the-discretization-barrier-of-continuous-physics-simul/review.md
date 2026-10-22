# Breaking the Discretization Barrier of Continuous Physics Simulation Learning



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The post-correction error bound is valid under its stated recurrence, but it does not give the same bound between corrections or force actual error to converge. Additive resets and cell-dependent graph neighborhoods also do not automatically preserve temporal or spatial continuity.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: The geometric error bound needs a post-correction domain

Assessment: supported; impact: minor



Source: Theorem 3.1, Eqs.(15)–(16), PDF p.6; Appendix F, Eqs.(24)–(27), p.24



### Source claim (paraphrase)

The main display uses \(K=\lfloor(t-t_0)/\Delta\rfloor\) for time \(t\), while the proof establishes a bound on error just after correction \(K\).



### Analysis

Write \(e_k^+\) for corrected error. The assumptions imply \[e_{k+1}^+\le\alpha e_k^++B,\quad \alpha=\kappa e^{L_F\Delta}<1,\quad B=\kappa E_{\rm ODE}+\delta_C.\] Hence \(e_K^+\le\alpha^K e_0^++B(1-\alpha^K)/(1-\alpha)\). This is the valid recurrence proved in Appendix F.

An arbitrary-time extension needs an unfinished-flow factor. For ideal trajectory \(0\), exact learned ODE \(\dot y=y\), \(\Delta=1\), initial corrected value \(1\) and correction \(y^+=e^{-2}y^-\), the assumptions hold with \(L_F=1,\kappa=e^{-2},E_{\rm ODE}=\delta_C=0\). Post-correction errors are \(e^{-k}\), but at \(t=1/2\) the error is \(e^{1/2}>1\), exceeding Eq.(16) read literally with \(K=0\).



### Finding and scope

The proof’s explicit post-correction interpretation resolves the principal domain issue. The same floor-indexed bound cannot be used unchanged at arbitrary times between corrections.



### Proposed correction

Label the bound as applying to \(e_K^+\). If a partial-interval residual \(E_{\rm ODE}(\tau)\) is established, use \(e(t_K+\tau)\le e^{L_F\tau}e_K^++E_{\rm ODE}(\tau)\).

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: A convergent upper envelope does not force error convergence

Assessment: supported; impact: minor



Source: Theorem 3.1 after Eq.(16), PDF p.6; final paragraph of Appendix F, p.24



### Source claim (paraphrase)

The paper concludes that actual corrected error converges to the nonzero floor \(C_2=B/(1-\alpha)\).



### Analysis

The inequality establishes only \(\limsup_K e_K^+\le C_2\). For a smooth scalar counterexample take ideal state \(0\), zero learned ODE, \(\Delta=1\), initial state \(0\), and corrected-state map \(G(y)=\cos^2(\pi y/2)\). Its additive corrector is \(G(y)-y\). Since \(|G(y)|\le1\le |y|/2+1\), assumption (b) holds with \(\kappa=1/2,\delta_C=1\); take \(E_{\rm ODE}=0\), so \(\alpha=1/2,C_2=2\). The trajectory alternates \(0,1,0,1,\ldots\), never converging, while satisfying every displayed upper bound. The assumption controls error relative to the ideal state; it does not require pairwise contraction of \(G\).



### Finding and scope

Bounded long-horizon error follows conditionally, but existence of an error limit or equality to the envelope floor does not.



### Proposed correction

Replace the limit claim by \(\limsup_K e_K^+\le C_2\). If \(B=0\), the existing inequality does imply convergence to zero; otherwise extra dynamical assumptions are needed.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: Nonzero additive correction creates a temporal jump

Assessment: supported; impact: minor



Source: Section 3.2, Eqs.(11)–(12) and final inference paragraph, PDF p.5



### Source claim (paraphrase)

The hybrid inference strategy is said to maintain continuity and smoothness although it adds a discrete correction after each ODE interval.



### Analysis

Equation (12) uses the previous corrected state in a lagged residual. Let the ODE be zero and initial state \(1\); choose \(\lambda=1/2\) and an admissible constant residual \(r_\psi(1)=-1/2\). The state immediately before reset is \(1\), while immediately after it is \(3/4\). The jump is \(-1/4\). In general continuity requires the added residual to vanish at the reset. The theorem explicitly permits pre/post states, so this finding does not contradict its hybrid formulation.



### Finding and scope

Arbitrary-time queries and piecewise smooth ODE segments remain possible; globally continuous trajectories are not guaranteed by the printed reset construction.



### Proposed correction

Describe a piecewise smooth hybrid trajectory and state which side of a reset defines a query. A continuously forced replacement would be a different method requiring its own analysis.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 4: A changing four-vertex neighborhood can break spatial continuity

Assessment: supported; impact: minor



Source: Section 3.1, Eq.(4), PDF p.4; Section 3.3, pp.5–6; Algorithm 1, p.22; Appendix C.1, p.23



### Source claim (paraphrase)

Relative-position message passing over the four vertices of the query’s cell is used to support spatial continuity.



### Analysis

Consider adjacent cells \([0,1]\times[0,1]\) and \([1,2]\times[0,1]\). Set all vertex features at \(x=0,1\) to zero and both at \(x=2\) to one; these values can sample the smooth field \(x(x-1)/2\). Choose zero query Gabor initialization, zero positional term and bias, and first message weight \(1\). As a query crosses \(x=1\), Eq.(4) sums features of four vertices: its one-sided outputs are \(0\) and \(2\). A second residual layer with zero weight/bias is the identity, and a continuous ReLU readout preserves this nonnegative jump. Within each fixed cell the map can be continuous; neighbor-set switching is the obstruction.



### Finding and scope

The printed decoder does not guarantee continuity across cell boundaries. Extra interpolation in an unavailable implementation could change this conclusion, and no trained spatial discontinuity is asserted.



### Proposed correction

A shared-vertex bilinear interpolation construction would enforce continuity across cell boundaries, but not necessarily differentiability. This proposed decoder change has not been validated as preserving trained performance.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.

- The published author repository could not be resolved in the current metadata check; conclusions about architecture are bounded to the paper’s printed specification.
