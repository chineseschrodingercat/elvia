# MODEM: A Morton-Order Degradation Estimation Mechanism for Adverse Weather Image Recovery



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The scan backend uses a first-order input coefficient instead of the displayed exact zero-order hold. Morton locality is a scope qualification; reported restoration scores remain untested.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Released scan uses an approximate input coefficient

Assessment: supported; impact: minor



Source: Section 4.2, Eqs.(9)–(10), PDF p.7; modem_arch.py, selective scan call; Mamba v2.0.4, selective_scan_ref



### Source claim (paraphrase)

The paper specifies exact zero-order hold \(\bar A=e^{\Delta A}\), \(\bar B=(e^{\Delta A}-I)A^{-1}B\). The current author release calls its pinned Mamba selective scan, whose input coefficient is \(\Delta B\).



### Analysis

For one state and step, take \(A=-1,B=C=1,\Delta=x_1=1,h_0=D=0\). The negative state parameter and positive step are allowed. The exact continuous equation \(\dot h=-h+1\) gives \(h(1)=1-e^{-1}\approx0.632121\), whereas the backend recurrence gives \(h_1=1\). Its transition coefficient is exponential, but its input increment uses no exponential correction.



### Finding and scope

The formula and linked primitive differ for the same generated coefficients. Both define legitimate discrete models; this does not refute restoration accuracy or imply that the exact-ZOH model would perform better.



### Proposed correction

Document the implemented first-order coefficient \(\Delta B\), or use the exact diagonal coefficient \(\operatorname{expm1}(\Delta a)b/a\), with limit \(\Delta b\) at zero. Changing a trained model’s recurrence requires new empirical validation.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Morton ordering has block locality rather than a uniform neighbor guarantee

Assessment: not_issue; impact: minor



Source: Appendix A.6, PDF p.19



### Source claim (paraphrase)

The locality motivation says nearby image pixels remain nearby in the scan.



### Analysis

Adjacent pixels \((2^m-1,0)\) and \((2^m,0)\) have interleaved indices \((4^m-1)/3\) and \(4^m\), so their scan gap is \((2\cdot4^m+1)/3\) despite unit spatial distance. Conversely an aligned dyadic square fixes the high interleaved bits and occupies a contiguous interval.



### Finding and scope

The motivation is valid as hierarchical block locality and does not require a universal adjacent-pixel bound. No permutation or inverse-scan defect is established; the empirical scan comparison is not refuted.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
