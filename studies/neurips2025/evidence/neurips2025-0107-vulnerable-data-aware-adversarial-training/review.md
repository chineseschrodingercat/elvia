# Vulnerable Data-Aware Adversarial Training



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Margin-change scores do not universally order adversarial vulnerability, and the printed sampling-probability rule lacks an equal-score case. The heuristic's reported empirical gains are not refuted.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: Margin change need not order distance to the boundary or susceptibility to the stated attack

Assessment: supported; impact: minor



Source: Section 4.1, Eqs. (2)–(5), PDF p. 4; Section 4.2, Eq. (6), PDF p. 5.



### Source claim (paraphrase)

Paraphrase: Section 4.1, p. 4, interprets a larger absolute change of margin between a natural input and its adversarial example as indicating that the natural input is harder to attack, hence less vulnerable. This motivates the negative sign in Eq. (2); Eqs. (3)–(5) replace the hard maximum by log-sum-exp. Section 4.2 then favors higher scores through Eq. (6), p. 5.

The paper does not state this interpretation as a theorem with extra restrictions on logit derivatives, local linearity, or identical sensitivity across examples. Its checklist also explicitly says that it does not contain theoretical results. The claim assessed here is therefore the general explanatory interpretation of the score, not a nonexistent formal theorem.



### Analysis

Use ten logits on \(x\in[0,1]\), with true-class logit \(g(x)=10(x-1/2)-9\operatorname{ReLU}(x-11/20)\) and nine competing logits zero. Both \(x_A=0.51\) and \(x_B=0.90\) are correctly classified. At temperature \(\tau=5\), the soft margin is \(g(x)-\log(9)/5\), so its change equals the change of \(g\). Cross-entropy FGSM with \(\epsilon=8/255\) moves each point left by that budget without clipping. It flips \(A\), whose boundary distance is \(0.01\), while \(B\), at distance \(0.4\), remains robust throughout the allowed interval.

The score gives \(V_A=-16/51\) and \(V_B=-8/255\), and the paper’s two-point sampling formula yields \(P_A=1/4\), \(P_B=3/4\). Thus the robust point is prioritized. This valid counterexample disproves the general explanatory identification; it neither measures its frequency in trained models nor refutes the heuristic’s empirical usefulness. The filtering-specific budget was not separately established, so the witness uses the stated FGSM probe and an explicit valid evaluation budget.



### Finding and scope

A valid FGSM example reverses the explanatory ranking, while the paper presents a heuristic and its measured accuracy gains remain unchallenged.



### Proposed correction

Describe negative margin change as an empirical heuristic that need not order true robustness; restrict performance claims to the evaluated settings. No validated efficient replacement algorithm is supplied.

The local qualification or neutral-tie proposal is retained. Current accessible paper text still has the cited rule; author implementation and adoption are unestablished.



## Problem 2: Equation (6) is undefined when the vulnerability scores are equal

Assessment: supported; impact: minor



Source: Section 4.2, Eq. (6), PDF p. 5.



### Source claim (paraphrase)

Paraphrase of Eq. (6), Section 4.2, p. 5: for each training example,

\[ P_i=\frac12\left(\frac{V_i-\bar V}{D_i}+1\right),\qquad \bar V=\frac1n\sum_{j=1}^nV_j,\qquad D_i=\max_{1\le j\le n}|V_i-V_j|. \]



### Analysis

With affine true-class logit \(x-1/2\) and zero competing logits, the correctly classified inputs \(0.51\) and \(0.90\) have equal margin-change score \(-8/255\). Their centered scores and dispersion denominator are both zero. Equation (6) therefore contains \(0/0\), although their boundary distances differ.



### Finding and scope

The written probability rule omits a valid tied-score case; unavailable author code may already guard it, and no occurrence in published runs is established.



### Proposed correction

The proposed clarification defines neutral equal-score probabilities and checks normalization; no released-code claim is made.

A local correction or qualification is proposed where specified; author adoption is not established.

The local qualification or neutral-tie proposal is retained. Current accessible paper text still has the cited rule; author implementation and adoption are unestablished.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
