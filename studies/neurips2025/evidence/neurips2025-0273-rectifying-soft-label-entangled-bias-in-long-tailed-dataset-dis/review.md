# Rectifying Soft-Label Entangled Bias in Long-Tailed Dataset Distillation



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Positive finite distributions refute the transfer coefficient and the training/test discrepancy equivalence in the central theorem. Uniform class counts also do not establish conditional feature matching; a weaker consistent population bound survives.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: The bounded-loss transfer coefficient is too small

Assessment: supported; impact: major



Source: Section 3.1, Eq. (3); Appendix A.2, Eq. (17)



### Source claim (paraphrase)

For \(0\le f\le C\), the paper bounds transferred loss by distilled loss plus \(C\sqrt{\mathrm{KL}(P\|Q)}/(2\sqrt2)\).



### Analysis

Let the input be a singleton, \(Q(Y)=P_{\rm tr}(Y)=(4/5,1/5)\), balanced \(P_{\rm te}(Y)=(1/2,1/2)\), and classifier \(\widehat p=(4/5,1/5)\). Label shift holds and \(C=\log5\). Direct evaluation gives \(\ell_Q=0.50040242\), \(\ell_{\rm te}=0.91629073\) and \(\mathrm{KL}(P_{\rm te}\|Q)=\log(5/4)\). The printed right side is \(0.76919756\), strictly below the actual loss. The general bounded-loss argument is \(E_Pf-E_Qf\le C\operatorname{TV}(P,Q)\le C\sqrt{\mathrm{KL}(P\|Q)/2}\); its coefficient is twice the printed one.



### Finding and scope

The displayed transfer guarantee is false on a strictly positive admissible two-class model. The corrected coefficient retains a population transfer bound but does not reproduce the ADSA accuracy gains.



### Proposed correction

Replace the coefficient by \(C/\sqrt2\) and use the bounded-loss/total-variation argument. This corrects the numerical guarantee without proving the calibration algorithm optimal.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Training and test joint KL are identified despite label shift

Assessment: supported; impact: major



Source: Theorem 3.1, Eqs. (4)–(6); Appendix A.2



### Source claim (paraphrase)

The discrepancy defined from the training law is called equivalent to decompositions based on the balanced test law.



### Analysis

On the singleton-input example \(P_{\rm tr}=Q=(4/5,1/5)\) and \(P_{\rm te}=(1/2,1/2)\), the original joint KL is \(0\), while the proposed prior-plus-conditional decomposition is \(\log(5/4)>0\). With \(Q=(1/2,1/2)\), the original KL becomes \(0.19274476\) and the test-law KL becomes \(0\). The difference changes with \(Q\), so a constant independent of the distilled law cannot repair equality.



### Finding and scope

The theorem changes which distributional discrepancy is being optimized. Both ordinary KL chain rules remain valid when consistently applied to the test joint.



### Proposed correction

Define \(R_{\rm te}=\mathrm{KL}(P_{\rm te}(X,Y)\|Q(X,Y))\) explicitly; its feature/posterior and prior/conditional chain-rule decompositions are exact. Use this new quantity in the corrected population bound.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: A balanced prior does not imply matched conditional features

Assessment: supported; impact: minor



Source: Appendix A.2, Eqs. (38)–(40)



### Source claim (paraphrase)

The appendix infers zero conditional and feature-marginal KL from a uniform test class prior.



### Analysis

Use \(P_{\rm tr}(Y)=(4/5,1/5)\), \(P_{\rm te}(Y)=Q(Y)=(1/2,1/2)\), and for both classes \(P_{\rm tr}(X\mid y)=P_{\rm te}(X\mid y)=(4/5,1/5)\), \(Q(X\mid y)=(1/5,4/5)\). All masses are positive and label shift holds. Each conditional KL and the feature-marginal KL equal \((3/5)\log4>0\), while the class-prior KL is \(0\).



### Finding and scope

The zero-discrepancy simplification requires successful conditional distribution matching in addition to equal class counts. The example does not show equal IPC or calibration is practically ineffective.



### Proposed correction

State equality of every class-conditional distribution as an additional premise. Positive uniform prior weights then make the conditional KL sum zero exactly when each conditional matches.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
