# Towards Generalizable Retina Vessel Segmentation with Deformable Graph Priors



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The current paper and author release retain three Major mathematical defects in the variational model: an unnormalizable bounded-energy prior on the stated unbounded domain, reversed energy signs in the approximate landmark update, and a Beta-KL normalization sign that changes training gradients. Entropy/reconstruction scaling and returned SoftDice semantics remain two separate Minor issues. No segmentation table was independently recomputed.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Bounded cosine energy does not define the stated prior on an unbounded space

Assessment: supported; impact: major



Source: Section 3.2, Eqs. (1)–(4), PDF p. 5; Section 3.3, PDF p. 6; Appendix A.2.4, PDF p. 17 (Gaussian variational family).



### Source claim (paraphrase)

The bounded cosine energy kernel \(e^{-H}\) is treated as a normalized prior on an unbounded space and used with an untruncated Gaussian variational law.



### Analysis

For a finite graph, \(z_i\in[0,1]\), finite \(d_i>0\) and cosine similarities \(|c_{ij}|\le1\), the written energy satisfies \[0\le H(S;u)\le\sum_{i\in I_G}z_i|N(i)|e^{d_i}+|I_G|\sum_{i=1}^n(1-z_i)e^{d_i}=:M(u)<\infty.\] This bound is independent of the amplitude of \(S\). Consequently \[\int_{\mathbb R^n}e^{-H(S;u)}\,dS\ge e^{-M(u)}\int_{\mathbb R^n}1\,dS=\infty.\] Excluding zero-window null sets or stabilizing the cosine denominator does not supply confinement. The paper’s untruncated Gaussian variational family has unbounded support; restricting only the prior to a bounded pixel box would instead make the variational KL infinite.



### Finding and scope

This is a general normalization obstruction for the written prior. A bounded-support prior would also require matching the Gaussian variational support; treating the kernel as a regularizer is a different interpretation.



### Proposed correction

Use a proper confining/base measure or consistently bounded support, or treat the energy solely as a regularizer. None of these alternatives alone constitutes a repaired full ELBO.

The freshly retrieved official paper retains the cited formula or definition. The current author repository head retains the implicated implementation where available. Existing local algebraic corrections do not establish a complete repaired model, retraining result or author adoption.



## Problem 2: The d-update reverses energy signs and is only approximate Gamma conjugacy

Assessment: supported; impact: major



Source: Eq. (14), PDF p. 6; Appendix A.2.3, Eqs. (35)–(43), PDF pp. 16–17; author get_gamma_d.



### Source claim (paraphrase)

The update combines log p(d) with log p(S|..), but subsequent equations add the energy terms with the opposite sign.



### Analysis

The negative energy expands as \(-Ae^{-cd}-Be^{cd}=-A-B+(A-B)cd+O(d^2)\), opposite to the displayed linear sign. With prior shape \(2\), rate \(10^{-4}\), mean latent \(1/2\) and cosine \(1/2\), the off-graph example gives printed rate \(10^{-4}\), versus sign-correct first-order rate \(0.2501\). The original exponential dependence on \(d\) is not Gamma-conjugate. Taylor approximation, MGF clipping and the partition-function problem remain separate limitations.



### Finding and scope

The local sign/approximation issue is supported. Neither the first-order fix nor a one-variable integral is asserted to be the correct full posterior, particularly given the prior-normalization problem.



### Proposed correction

Preserve the negative-energy sign and label the Taylor-Gamma update as approximate; the full consistent prior/posterior still requires analysis.

The freshly retrieved official paper retains the cited formula or definition. The current author repository head retains the implicated implementation where available. Existing local algebraic corrections do not establish a complete repaired model, retraining result or author adoption.



## Problem 3: The Beta-KL log-Beta sign changes training gradients

Assessment: supported; impact: major



Source: Appendix A.2.4, Eqs. (54)–(57), PDF p. 17; author losses.py, lines 42–49, and graphseg.py, line 599.



### Source claim (paraphrase)

Appendix A.2.4, Eq. (56), PDF p. 17, prints a positive \(\log[\Gamma(\alpha)\Gamma(\beta)/\Gamma(\alpha+\beta)]=\log B(\alpha,\beta)\) term for the variational Beta distribution in the KL defined by Eqs. (54)–(55). The correct variable normalization term has the opposite sign. The active author losses.py function, lines 42–49, called by graphseg.py at line 599, repeats the printed sign.



### Analysis

Exact Beta KL includes \(\log B(\alpha_0,\beta_0)-\log B(\alpha,\beta)\). The active expression uses a positive sign on the latter term. At \(q=p=\operatorname{Beta}(2,2)\), both parameter gradients are \(-5/3\), whereas a correct KL is minimized there with zero gradient. No additive constant changes this. For \(\operatorname{Beta}(3,3)\) versus \(\operatorname{Beta}(2,2)\), the true KL is \(0.0427712457674\), while the centered source expression is \(-3.17610457910\).



### Finding and scope

The wrong log-Beta sign is present in the paper itself, Eq. (56), and in the called loss function. It changes the core variational objective and its gradients; an unused alternate source function has the correct structure. No performance effect or corrected segmentation score is established.



### Proposed correction

Restore the full Beta-KL sign structure while preserving numerical dtype. This algebraic correction does not establish a repaired model experiment.

The freshly retrieved official paper retains the cited formula or definition. The current author repository head retains the implicated implementation where available. Existing local algebraic corrections do not establish a complete repaired model, retraining result or author adoption.



## Problem 4: Entropy and reconstruction normalization alter relative loss weights

Assessment: supported; impact: minor



Source: Appendix A.2.4, Eqs. (47) and (51)–(53), PDF p. 17; author losses.py, lines 5–10, and graphseg.py, lines 589 and 603–605.



### Source claim (paraphrase)

The objective is presented as a variational decomposition with per-element normalization.



### Analysis

Gaussian negative entropy has variable term \(-\frac12\sum\log\sigma^2\); the paper uses coefficient \(-1\) and the active code \(-2\), while the other terms retain their own weights. Reconstruction is averaged and then divided again by element count \(N\). For unit residuals and \(N=4,8,16\), this yields \(0.25,0.125,0.0625\), whereas the stated half-per-element quadratic is \(0.5\). These are parameter-dependent relative-weight and size effects, not one additive constant.



### Finding and scope

The source objective has parameter-dependent relative-weight and batch-size differences. These cannot all be absorbed into an additive constant or common scalar.



### Proposed correction

Use the intended one-half entropy coefficient and one declared reconstruction normalization; full probabilistic consistency and retraining outcomes remain open.

The freshly retrieved official paper retains the cited formula or definition. The current author repository head retains the implicated implementation where available. Existing local algebraic corrections do not establish a complete repaired model, retraining result or author adoption.



## Problem 5: Returned SoftDice is replaced by label-optimized hard Dice

Assessment: supported; impact: minor



Source: Appendix B.1, PDF p. 19; author metrics.py, lines 143–205, and find_best_dice_threshold, lines 5–38.



### Source claim (paraphrase)

The paper defines SoftDice using continuous probabilities and a squared denominator; the release overwrites its soft_dice variable with the best hard-threshold score on the supplied labels.



### Analysis

For probabilities \((0.49,0.48)\), labels \((1,0)\), and stabilizer \(10^{-6}\), the paper's squared-denominator SoftDice is \(0.6664402132\). Hard F1 at threshold \(0.5\) is zero; searching thresholds \(0,0.01,\ldots,1\) selects \(0.49\) and returns hard Dice \(1\). The source overwrites its soft_dice variable with that label-optimized hard score; its earlier soft value also has a different linear denominator.



### Finding and scope

This confirms an evaluation-function semantics error. It does not establish that the published tables used this code or prove test-set leakage; historical predictions/calls are unavailable.



### Proposed correction

Compute the stated continuous SoftDice separately from hard-threshold metrics. If a threshold is selected, do so under a separately defined validation protocol.

The freshly retrieved official paper retains the cited formula or definition. The current author repository head retains the implicated implementation where available. Existing local algebraic corrections do not establish a complete repaired model, retraining result or author adoption.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- Local contradictions and specification differences do not establish the magnitude or direction of changes to the published benchmark scores.

- No author contact or adoption; novelty and complete historical-run provenance are unestablished.
