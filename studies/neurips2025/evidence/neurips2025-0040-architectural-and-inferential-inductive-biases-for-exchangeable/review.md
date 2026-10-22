# Architectural and Inferential Inductive Biases for Exchangeable Sequence Modeling



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Two Gaussian information-loss formulas are mathematically incorrect: one omits observation noise, and one mixes KL directions. These substantial derivation errors determine Major while the central conditional-information identity remains valid. The released acquisition/rollout discrepancies are Minor and do not identify the historical figure-producing implementation.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Bayesian linear-regression information loss omits observation noise

Assessment: supported; impact: major



Source: Appendix D.6, Example 4, p.28; common proof p.29.



### Source claim (paraphrase)

Example \(4\) substitutes X Sigma X-transpose into a future-observation Gaussian determinant ratio.



### Analysis

Use prior variance \(2\), observation-noise variance \(2\), and repeated scalar input \(1\). After one observation, latent posterior variance is \(1\). Two future latent values therefore have singular covariance \(\begin{pmatrix}1&1\\1&1\end{pmatrix}\), so the printed noise-free determinant ratio diverges. Future observations instead have covariance \(K=\begin{pmatrix}3&1\\1&3\end{pmatrix}\), giving finite divergence \(\frac12\log(9/8)\simeq0.0588915178\). The covariance does not depend on the observed response.



### Finding and scope

Example4 omits observation-noise covariance and can return a divergent expression for a finite Gaussian information loss.



### Proposed correction

Use future-observation covariance \(K=X\Sigma X^\top+\tau^2I\) and the Gaussian ratio \(\det(\operatorname{diag}K)/\det K\), with the stated input/context expectations.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: The GP formula mixes KL directions

Assessment: supported; impact: major



Source: Example 5, p.28; Appendix D.6.1, p.29.



### Source claim (paraphrase)

Example \(5\) names forward \(\operatorname{KL}(P\|Q)\), but uses the precision of \(P\) in trace and mean terms.



### Analysis

For equal means, \(K_P=\begin{pmatrix}2&1\\1&2\end{pmatrix}\) and \(\Sigma_Q=2I\), the printed mixed expression gives \(0.4771743696\). Forward KL is \(\frac12\log(4/3)\simeq0.1438410362\), while reverse KL is \(0.1894922971\). Thus swapping the labels does not fix the formula. Positive observation noise makes both Gaussian laws nonsingular.



### Finding and scope

Example5 mixes forward and reverse Gaussian-KL terms; neither direction agrees with the printed expression.



### Proposed correction

For forward \(\operatorname{KL}(P\|Q)\), retain the corresponding determinant ratio and use \(\Sigma_Q^{-1}\) in trace and mean-quadratic terms. The conditional-information chain identities are not refuted.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: The public acquisition order is fixed rather than sequential

Assessment: supported; impact: minor



Source: Algorithm 3, p.25; run_al.py:242–280,317–330.



### Source claim (paraphrase)

Algorithm 3 recomputes uncertainty after each queried label.



### Analysis

The script scores every candidate once before the budget loop, then repeatedly takes the first \(k\) entries of that fixed ordering. Consider two duplicate GP candidates of prior variance \(1\) and an independent candidate of variance \(0.6\), with noise \(0.01\). Querying one duplicate reduces the other's variance to \(0.01/1.01\simeq0.00990099\); sequential uncertainty selection then chooses the independent point, whereas fixed ranking need not.



### Finding and scope

The released active-learning path uses a fixed initial uncertainty ranking rather than the sequential rule in Algorithm3.



### Proposed correction

Move score computation, one query and context update into one loop, or label the existing method as fixed-ranking batch acquisition. Historical figure attribution remains unknown.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: The rollout statistic is a final predictive mean

Assessment: supported; impact: minor



Source: Algorithm 3, p.25; compute_rollout_uncertainty, lines 119–121.



### Source claim (paraphrase)

Algorithm 3 averages all J generated samples within each path before comparing paths.



### Analysis

The release records the final predictive mean, rather than averaging all \(J\) generated samples along the path. For latent variance \(v\) and noise variance \(\tau^2\), the path-mean variance is \(v+\tau^2/J\), while the final-predictive-mean variance is \(v-v\tau^2/[\tau^2+(J-1)v]\). At \(v=\tau^2=1,J=1\), they are \(2\) and zero; at \(J=20\), they are \(1.05\) and \(0.95\). Both approach \(v\), so the alternative statistic is not automatically useless.



### Finding and scope

The release uses a final predictive mean instead of the declared within-path sample mean. Its asymptotic agreement does not make the finite statistics equal.



### Proposed correction

Compute the stated path-sample mean or explicitly define and analyze the alternate finite-path estimator. Corrected learning curves are not asserted.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- No new author-code execution, model spending, training, author contact or complete benchmark replication.

- Historical numerical results are retained evidence rather than current reruns.

- Local counterexamples do not invalidate every empirical result; missing historical run attribution remains unresolved.
