# Overcoming Sparsity Artifacts in Crosscoders to Interpret Chat-Tuning



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current manuscriptâ€™s KL direction differs from the released evaluation, and the running variance pools incompatible sample/population denominators. Exact positive-probability and four-observation examples establish local discrepancies, without proving a reversal of any published latent ranking.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: The two KL directions can reverse the approximation ranking

Assessment: supported; impact: minor



Source: arXiv v4 Section 3.2, PDF p.7; compute_kl and intervention-evaluation call



### Source claim (paraphrase)

The paper defines \(D_{\rm KL}(Q_S\Vert P)\), where \(P\) is original chat and \(Q_S\) is modified output. The codeâ€™s log-target operation computes \(D_{\rm KL}(P\Vert Q_S)\).



### Analysis

Let \(P=(0.8,0.2)\), \(Q_A=(0.5,0.5)\), \(Q_B=(0.99,0.01)\). The specified divergences are about \(0.2231435513\) and \(0.1810049606\), preferring B; the released direction gives \(0.1927447570\) and \(0.4286718823\), preferring A. Every entry is positive and finite logits realize them. Adding identical positive tail mass to a larger vocabulary scales all divergences by the same positive factor and retains the reversal.



### Finding and scope

The metric correspondence is wrong in general. Both directions are legitimate choices; the example does not identify an actual Figure 4 reversal or show that codeâ€™s intended metric was intrinsically inappropriate.



### Proposed correction

Either swap the evaluation arguments to follow the manuscript or revise the manuscriptâ€™s direction and associated interpretation to follow the code. Scalar averages cannot recover the opposite KL without underlying distributions.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: Variance depends on how the same observations are batched

Assessment: supported; impact: minor



Source: RunningMeanStd.update/update_from_moments, lines 347â€“439; Figure 4 uncertainty pipeline



### Source claim (paraphrase)

Batch variance uses default sample denominator \(n_b-1\), then merge code multiplies it by \(n_b\) as if it were population variance.



### Analysis

For observations \((0,2,4,6)\), the mean is \(3\), centered sum of squares \(20\), population variance \(5\), sample variance \(20/3\). One batch stores \(20/3\). Splitting into \((0,2)\), \((4,6)\) gives batch means \(1,5\), sample variances \(2,2\); the source merge returns \((2\cdot2+2\cdot2+16)/4=6\), neither correct convention. Singleton calls also create undefined batch sample variance although the pooled sample becomes defined.



### Finding and scope

The variance arithmetic is not partition-invariant and can change plotted uncertainty. Token dependence and interval coverage remain separate statistical questions.



### Proposed correction

Store centered sum of squares \(M_2\). Merge using \(M_{2,A}+M_{2,B}+(\mu_B-\mu_A)^2n_An_B/(n_A+n_B)\), and divide only at readout by the chosen total denominator.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
