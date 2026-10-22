# Exploring the limits of strong membership inference attacks on large language models



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Supplementary count/share summaries are incompatible with necessary identities. Threshold and score-resolution arguments also need corrections, while retraining instability must be distinguished from evidential strength; the main attack curves were not reproduced.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Count and share summaries violate necessary covariance identities

Assessment: supported; impact: minor



Source: Authors’ arXiv v3, Appendix E.2.6, Tables 5–6, pp. 53–54



### Source claim (paraphrase)

Per-seed counts satisfy \(A_r=T_rS_r\), with reported means and standard deviations of counts and shares.



### Analysis

Cauchy–Schwarz requires \(|\bar A/\bar T-\bar S|\le\sigma_T\sigma_S/\bar T\). Table 5 at FPR \(10^{-3}\) gives \(\bar T=15826,\sigma_T=1239,\bar A=3048,\bar S=0.133,\sigma_S=0.004\). The left side is \(0.05959446\), versus allowed \(0.00031317\); conservative rounding leaves \(0.05905679>0.00035245\). The bound \(T_r\ge\bar T-\sqrt{125}\sigma_T>0\) excludes zero-denominator suppression as an explanation. Table 6 also violates disjoint-bin mean additivity: \(10295+5883=16178\), while the stated union is \(16231\), beyond rounding.



### Finding and scope

Some reported summaries, bin identities or aggregation provenance are incompatible with the definitions. The raw ROC curves and overall AUC are not thereby proved wrong, and the affected entries cannot be identified uniquely.



### Proposed correction

Regenerate all counts, shares, unions and standard deviations from the same per-seed records with an explicit zero-denominator policy. Do not replace mean shares by ratios of means.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: An infimum plus inclusive threshold is not the conservative rank rule

Assessment: supported; impact: minor



Source: Authors’ arXiv v3, Appendix A, p. 17; Appendix E.2.8, p. 57



### Source claim (paraphrase)

The paper defines \(\tau=\inf\{t:\widehat F(t^-)\ge1-\eta\}\), uses \(s\ge\tau\), and claims equivalence to a next-distinct order statistic with empirical FPR at most \(\eta\).



### Analysis

For OUT scores \((1,2,3,4)\) and \(\eta=1/4\), the qualifying set is \((3,\infty)\), whose infimum is \(3\). Inclusive thresholding accepts two scores, giving FPR \(1/2\). The separately supplied next-distinct rule selects \(4\), giving \(1/4\). An infimum need not itself satisfy the left-limit CDF condition. The correct rank instruction is important counterevidence against assuming the experiments used a broken implementation.



### Finding and scope

The formal threshold and claimed equivalence fail, while the intended rank algorithm can preserve empirical calibration. Population FPR is not guaranteed by either finite-set count alone.



### Proposed correction

Take a minimum over observed scores plus \(+\infty\), or use the empirical quantile with a strict comparison. State the endpoint convention and distinguish new-score decisions between observed levels.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: Score spacing does not imply inverse-FPR comparison-population size

Assessment: supported; impact: minor



Source: Authors’ arXiv v3, Appendix A, Eq. (5), p. 17; Appendix B.2, pp. 19–20



### Source claim (paraphrase)

RMIA score spacing \(1/|Z|\) is used to infer a necessary comparison size of inverse minimum FPR.



### Analysis

Let \(|Z|=2\), both reference ratios be \(1\), comparison constant \(\gamma=1.1\). Of \(1000\) OUT records, give \(999\) ratio \(1\) and one ratio \(2\); give every IN record ratio \(2\). RMIA scores are \(0\) and \(1\). Threshold \(1\) yields FPR \(0.001\), TPR \(1\), despite \(|Z|=2\). An OUT law with masses \(0.999,0.001\) makes both reference draws equal to \(1\) with probability \(0.998001\). Score values and probability mass at those values are different quantities.



### Finding and scope

No distribution-free inverse-FPR requirement follows from quantization alone. Larger comparison sets can still improve the actual measured operating points.



### Proposed correction

Describe ties and distribution-dependent tail masses; empirical deterministic FPR resolution depends on the OUT calibration sample size and ties.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 4: Retraining flip rate alone does not determine positive evidence

Assessment: supported; impact: minor



Source: Authors’ arXiv v3, Section 5; Appendix E.2.7, pp. 55–56



### Source claim (paraphrase)

The paper distinguishes retraining instability but additionally interprets unstable positive calls as approximately coin-toss evidence.



### Analysis

Take \(s\mid\mathrm{IN}\sim N(0,1)\), \(s\mid\mathrm{OUT}\sim N(\delta,1)\), \(\delta=\Phi^{-1}(0.99)\), and a likelihood-ratio threshold equivalent to \(s\le0\). Positive probabilities are \(1/2\) under IN and \(0.01\) under OUT. IN retrainings have maximal flip rate \(2(1/2)(1/2)=1/2\), yet a positive event has Bayes factor \(50\). Under prior \(1/2\), posterior membership is \(0.5/(0.5+0.01)=0.980392\). It is unstable repeatability but strong IN-versus-OUT evidence. The paper’s binomial non-rejection label does not itself assert the null is proved.



### Finding and scope

Flip rate measures repeatability, not evidential strength without the competing OUT law and prior. No measured histogram or particular real-record posterior is changed by this countermodel.



### Proposed correction

Report instability alongside conditional error probabilities or likelihood ratios, and define any stronger reliability claim explicitly.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
