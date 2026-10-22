# Asymptotic theory of SGD with a general learning-rate



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



An auxiliary moment inequality omits conditional centering, but its actual main-proof application satisfies the missing condition. A vanishing-step remark needs a nonsummability qualification. Released R plotting scripts also swap moments or average Euclidean error under an MSE label.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: The moment inequality needs a mixed-term condition

Assessment: supported; impact: minor



Source: Lemma B.1, PDF p.15; actual use in Lemma B.2, pp.15–16



### Source claim (paraphrase)

The statement claims \(\|X+Y\|_p^2\le\|X\|_p^2+(p-1)\|Y\|_p^2\) for arbitrary finite-moment random vectors.



### Analysis

At \(p=2\), deterministic \(X=Y=1\) requires \(4\le2\). Even centered equal Rademacher variables give the same failure. The mixed inner product need not vanish. A sufficient condition is \(\mathbb E[Y\mid\mathcal G]=0\) with \(X\) measurable to \(\mathcal G\); the usual martingale smoothness inequality then applies. In Lemma B.2, the past iterate/drift is measurable and iid unbiased gradient noise is conditionally centered, exactly as the proof states.



### Finding and scope

The auxiliary statement is false, but its repaired actual application preserves the one-step recursion and Theorem 2.1 under the paper’s original assumptions.



### Proposed correction

Add conditional centering to the lemma. For its SGD application, identify the past sigma-algebra explicitly; no change to the main recursion is required.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: Vanishing steps alone need not remove accumulated noise

Assessment: supported; impact: minor



Source: Remark 2.2, PDF p.5; Theorem 2.1, Eq.(2.2)



### Source claim (paraphrase)

The isolated remark says the exploration sum is \(o(1)\) when \(\eta_n\to0\).



### Analysis

For \(f(\theta,\xi)=(\theta-\xi)^2/2\), independent Rademacher \(\xi\), start at optimum \(0\), use \(p=2,\mu=L_2=M_2=1,c_0=1,\eta_t=0.1\,2^{-t}\). The theorem’s step restrictions hold, but the first summand alone gives \(S_n\ge0.0025e^{-0.05}>0\). Actual variance also obeys \(v_n\ge0.0025\prod_{k=2}^n(1-\eta_k)^2\ge0.00225625\). Thus initialization removal does not cure the isolated criterion. Remark 2.1 separately discusses divergent accumulated steps, which may be the intended joint premise.



### Finding and scope

The isolated sufficiency statement needs qualification; the finite bound and separately analyzed Linear-D2Z result are not refuted.



### Proposed correction

For a fixed infinite schedule, require both \(\eta_t\to0\) and \(\sum_t\eta_t=\infty\) with fixed \(c_0>0\). Splitting off finitely many early terms and bounding the tail by \( \delta e^{c_0M}/c_0\), \(M=\sup\eta_t\), proves convergence. Finite-horizon triangular arrays need their own uniform conditions.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: The plotting helpers exchange MSE and squared-error SD

Assessment: supported; impact: minor



Source: Functions.R, lines 69–109; empirical Figures 2–6



### Source claim (paraphrase)

The statistic function returns named list \((\mathrm{se.sd},\mathrm{mse})\), but positional helpers label the first MSE and second SD.



### Analysis

Three error vectors \((0,0),(3,4),(0,0)\) have squared errors \(0,25,0\), mean \(25/3\) and sample SD \(25/\sqrt3\). Returned list order therefore labels approximately \(14.4338\) as MSE and \(8.3333\) as SD; both center and ribbon are exchanged. Names do not reverse R insertion order.



### Finding and scope

The released plotting map is incorrect. The statistic producer itself is correct, and actual provenance of every published figure remains unestablished; no native R run occurred in this check.



### Proposed correction

Extract the mse and se.sd fields by name in both helpers, then regenerate affected figures from run-level errors or saved statistic objects.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 4: The Figure 1 script averages norms rather than squared norms

Assessment: supported; impact: minor



Source: Figure 1 and Section 3.2, PDF p.7; section_3_2_plot_1.R, mse.lr.linear.schedule



### Source claim (paraphrase)

The script returns \(\sqrt{\sum_j(\theta_j-\theta_j^\star)^2}\) before averaging, under an MSE label.



### Analysis

Errors \((0,0),(3,4)\) yield mean norm \(2.5\), MSE \(12.5\), and RMSE \(\sqrt{12.5}\), all distinct. Squaring the mean norm gives \(6.25\), which cannot recover MSE. An \(O(n^{-1/2})\) MSE bound only gives \(O(n^{-1/4})\) mean norm by Jensen, so the released statistic cannot directly validate the stated MSE rate.



### Finding and scope

The local metric is mislabeled or miscomputed. The theorem remains independent, and this script has not been authenticated as the exact source of the published figure.



### Proposed correction

Return squared norms for MSE, or relabel the statistic and revise its theoretical comparison. Recover run-level errors rather than squaring an aggregate mean.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
