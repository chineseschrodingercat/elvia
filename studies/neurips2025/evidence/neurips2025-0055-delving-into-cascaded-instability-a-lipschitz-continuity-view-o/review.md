# Delving into Cascaded Instability: A Lipschitz Continuity View on Image Restoration and Object Detection Synergy



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The stability discussion confuses maximum directional gain with necessary amplification, and Remark 3 uses a training-point condition to control a global Jacobian maximum. Released training recipes also differ from the displayed objective.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Operator norms do not lower-bound every directional gain

Assessment: supported; impact: minor



Source: Section 3.1, PDF p.4, paragraph before Remark 1



### Source claim (paraphrase)

Section 3.1 uses a restoration Jacobian norm above one to infer amplification of slight input changes, then invokes a larger detector norm.



### Analysis

Take \(A=\operatorname{diag}(2,1/10)\) and \(M=\operatorname{diag}(20,1/10)\). Their operator norms are \(2\) and \(20\), but the cascade maps \(\epsilon e_2\) to \((\epsilon/100)e_2\). These smooth linear maps therefore contract that finite perturbation despite large maximum gains.



### Finding and scope

Necessary amplification in every direction does not follow. Existence of amplified directions and the empirical observations remain possible.



### Proposed correction

The valid upper bound is \(\operatorname{Lip}(D\circ R)\leq\operatorname{Lip}(D)\operatorname{Lip}(R)\). A particular first-order gain is \(\|J_DJ_Rv\|/\|v\|\); a universal local lower bound requires a minimum-singular-value condition.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Training-point alignment does not control the global envelope

Assessment: supported; impact: minor



Source: Section 4.1, Remark 3, PDF p.6; Appendix A, PDF p.13



### Source claim (paraphrase)

Remark 3 assumes restoration-gradient alignment at a training point \(x^\star\), then bounds the derivative of the global Jacobian maximum \(C(\theta)\).



### Analysis

For \(B_\theta(x)=x+\theta(x^2-x)\) on \([0,1]\), \(0<\theta<1/2\), use losses \(L_r=2-\theta\), \(L_d=3-2\theta\), and weight \(1\). Then \(g_r=-1\), \(g_d=-2\), and at training point \(x^\star=0\) the required alignment is \(1\). Nevertheless \(C(\theta)=1+\theta\), attained at \(x=1\). Gradient flow has \(\dot\theta=3\), so \(\dot C=3\), while the printed bound is \(1\). Correcting only the detection-term sign does not repair the missing maximizer condition.



### Finding and scope

The stated sufficient condition does not establish this ancillary stability bound. It does not refute improved performance of the joint model.



### Proposed correction

Under the usual compactness and differentiable-envelope conditions, require alignment at every active maximizer. Use the signed detection contribution \[\max_{x\in\arg\max\phi}[-\langle\nabla_\theta\phi,g_d\rangle]\]. Strict decrease needs this term to be smaller than the restoration contribution.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: Public losses differ from the displayed parameter-Jacobian objective

Assessment: supported; impact: minor



Source: Section 4.2, Remark 4 and full objective, PDF p.7; Table 4, PDF p.9; released loss path



### Source claim (paraphrase)

Section 4.2 uses \(L_d+\lambda L_r+\lambda_p\|\nabla_\theta f_\theta(x)\|\), with a Charbonnier restoration loss and stated weights \(\lambda=10\), \(\lambda_p=0.01\).



### Analysis

The public recipes assemble weighted absolute-error/perceptual reconstruction terms and clipping or loss-gradient penalties. A loss-gradient norm is not generally the model-output parameter-Jacobian norm in the equation; clipping is an optimizer operation rather than that objective. No configuration-to-table mapping establishes which historical experiment used these recipes.



### Finding and scope

The inspected recipe is insufficient to reproduce the exact displayed objective. No published table entry is numerically contradicted.



### Proposed correction

Provide the exact loss, norm, reduction and experiment configuration. An operator norm must not silently become a Frobenius estimator; implementing another regularizer requires its own interpretation and evaluation.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
