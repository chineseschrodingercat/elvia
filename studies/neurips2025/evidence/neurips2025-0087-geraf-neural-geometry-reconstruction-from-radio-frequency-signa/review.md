# GeRaF: Neural Geometry Reconstruction from Radio Frequency Signals



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The central additive lensless-transmittance derivation fails even on a valid monotone planar SDF. The printed matched-filter derivative also lacks a resultant factor, but the later release supplies a correct magnitude-chain path.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Additive calibration conflicts with the defining transmission integral

Assessment: supported; impact: major



Source: Current arXiv v2 Section 6, PDF p.7, Eq.(7); Appendix B.1–B.2, PDF pp.21–22



### Source claim (paraphrase)

Section 6, Eq.(7), uses \(T_r=T_p-C_p(0)+C_r(0)\) to calibrate reused-ray transmittance. Appendix B defines density from the clipped logarithmic derivative of the logistic CDF \(C\).



### Analysis

On a monotone entering ray the integral gives \(T(u)=C(u)/C(0)\). Use the true planar SDF \(f=(x+z)/\sqrt2\) and unit logistic scale. Origins \((0,0,\sqrt2\log3)\) and \((-\sqrt2\log2,0,\sqrt2\log3)\) lie in the same aperture plane and have CDFs \(3/4\), \(3/5\); choose their common endpoint at CDF \(1/2\). Then \(T_p=2/3\), but additive calibration gives \(31/60\), while the receiver ray requires \(5/6\). All values are finite and positive, and both straight rays are monotone for this planar SDF.



### Finding and scope

The central calibration formula is not derived from the stated density, even before nonmonotone path complications. No reconstruction benchmark is remeasured.



### Proposed correction

For monotone entering rays, the correct origin adjustment is \(T_r=T_pC_p(0)/C_r(0)\). General paths instead depend on accumulated downward variation of \(\log C\), so this endpoint ratio is not a universal ray-reuse repair.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: The printed magnitude derivative omits the complex resultant

Assessment: supported; impact: minor



Source: Current arXiv v2 Appendix A.5, PDF p.19, Eq.(13); Algorithm 1, PDF p.20



### Source claim (paraphrase)

Appendix A.4 differentiates \(P_j=|z_j|\) but omits the resultant needed in its magnitude derivative.



### Analysis

For one positive real input with coefficient \(1\) and signal \(2\), \(P=2\), true derivative is \(1\), while the printed rule gives \(1/P=1/2\). This real subcase avoids complex-gradient convention ambiguity. The later `rf_rendering.py` instead computes real/imaginary outputs followed by `torch.hypot`, which retains the needed chain rule.



### Finding and scope

The printed formula is wrong; a current released gradient defect and historical benchmark effect are not established.



### Proposed correction

For \(z\ne0\), use \(d|z|=\operatorname{Re}(\bar z\,dz)/|z|\), with a declared convention for the final real-loss complex gradient and the zero boundary.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.

- The later GeRaF-SENS code and later arXiv extension are distinct from the original proceedings implementation history.
