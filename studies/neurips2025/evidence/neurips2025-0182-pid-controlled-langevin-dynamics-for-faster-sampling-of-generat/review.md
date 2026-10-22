# PID-controlled Langevin Dynamics for Faster Sampling of Generative Models



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



A legal strongly convex quadratic disproves the stated stability and stationary-law guarantee. Integral-gain decay alone also leaves derivative Langevin dynamics rather than ordinary Langevin dynamics. The toy release has separate recurrence differences.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Lower curvature does not control explicit-step stability

Assessment: supported; impact: major



Source: Proposition 1, Eqs.(3)â€“(4), PDF pp.6â€“7; Appendix B, p.22



### Source claim (paraphrase)

The proposition assumes \(-U\) is \(m\)-strongly convex and claims stability when \(\epsilon<[(1+2k_d)m]^{-1}\), then a unique stationary law with Gaussian noise.



### Analysis

On \(\mathbb R^2\), take \(-U=(x_1^2+10x_2^2)/2,m=1,k_d=1,\epsilon=1/10<1/3\). The second coordinate obeys \(z_{t+1}=-z_t+z_{t-1}\), with root \((-1-\sqrt5)/2\) of magnitude greater than one. Initial values \(z_{-1}=z_0=1\) yield \(1,1,0,1,-1,2,-3,\ldots\), and arbitrarily small scaled initial values still diverge. Gaussian forcing projects nontrivially onto the unstable mode. Any invariant characteristic function would satisfy \[|\phi(u)|\le\exp[-qu^2\sum_{j=0}^{n-1}r^{2j}/2]\to0\] for \(u\ne0\), contradicting continuity at zero.



### Finding and scope

The printed stability restriction and consequent invariant-law assertion are false even for a smooth globally strongly convex quadratic. No empirical benchmark failure follows.



### Proposed correction

For quadratic Hessian \(H\succ0\), mode-wise Jury conditions give exactly \(0<\epsilon<2/[(1+2k_d)\lambda_{\max}(H)]\). This yields a unique invariant Gaussian for the stable linear augmented chain. Local nonlinear linearization does not itself prove global stochastic recurrence.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: Integral decay does not remove derivative feedback

Assessment: supported; impact: major



Source: Section 3.2, PDF p.6; Algorithm 1, PDF p.7



### Source claim (paraphrase)

The text infers reduction to standard Langevin dynamics as \(k_i\to0\), although \(k_d\) remains positive.



### Analysis

For \(U=-x^2/2,k_i=0,k_d=1,\epsilon=0.1\), the limiting update is \(x_{t+1}=0.8x_t+0.1x_{t-1}+\sqrt{0.2}\xi_t\). Solving \(C=0.8V+0.1C\) and \(V=(0.8^2+0.1^2)V+0.16C+0.2\) gives \(V=180/187\), versus ordinary ULA variance \(20/19\). In stationarity \(\mathbb E[(x_t-x_{t-1})^2]>0\); stochastic derivative feedback does not vanish. The propositionâ€™s unnamed stationary law is not incorrectly attributed as the exact target.



### Finding and scope

The asserted transition reduction and its convergence inference are unsupported. Both fixed-step schemes can have discretization bias; this example does not show worse PID sample quality.



### Proposed correction

State that vanishing integral control leaves proportional-derivative dynamics, whose stability and invariant law need separate analysis. Coefficient limits alone do not certify a time-varying sampler.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: The toy sampler uses a different integral and gain schedule

Assessment: supported; impact: minor



Source: Algorithm 1 and Section 3.3, PDF p.7; toy/Langevin.py, PID_ALD



### Source claim (paraphrase)

The paper uses a global running mean, carried annealing history and per-step integral decay; the toy source divides a finite window by its configured length, resets history each level and decays once per level.



### Analysis

With window length \(2\), the first integral is \(s/2\), versus the published \(s\). At step \(0.04\), gain \(0.2\), and maximum initial score magnitude \(2\), this alone changes the first state by \(0.008\), independently of coupled noise. For two steps per level, starting gain \(0.2\) and decay \(0.9\), the code uses \(0.2,0.2,0.18,0.18\), versus per-step \(0.2,0.18,0.162,0.1458\). The toy README documents a moving-window option; the image sampler has different history handling.



### Finding and scope

A local specification/release variant is established, without authenticating historical figure-generation settings or extending the discrepancy to every sampler.



### Proposed correction

Either align the toy recurrence with Algorithm 1 or explicitly document the variant and exact experiment configurations. No restored empirical curve is claimed.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
