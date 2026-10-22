# scSplit: Bringing Severity Cognizance to Image Decomposition in Fluorescence Microscopy



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The expected patch-variance derivation omits patch-mean covariance, and mean-standard-deviation normalization does not guarantee unit expected variance. These are bounded moment/specification corrections; the valid weaker normalization and microscopy results are not refuted. The stricter assessment is Minor.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Expected patch variance drops a mean-covariance term

Assessment: supported; impact: minor



Source: Section 3.2, Eq. (2), PDF p. 4; supplement A, Eqs. (2) and (5)–(10), PDF pp. 21–22.



### Source claim (paraphrase)

The paper uses population-pixel covariance in the expected within-patch variance formula and substitutes the square of the expected patch mean for its expected square.



### Analysis

Take paired patches \(c_0=(B+S_0,B-S_0)\), \(c_1=(B+S_1,B-S_1)\), with equiprobable \(B\in\{2,4\}\) and independent signs. Pixel marginals are stationary and nonnegative, endpoint spatial variances are one, and population pixel covariance is one. At \(t=1/4\), the printed equation gives one, but directly centered variance is \((3/4)^2+(1/4)^2=5/8\). The missing cross contribution is \(2t(1-t)[\operatorname{Cov}(p_0,p_1)-\operatorname{Cov}(\mu_0,\mu_1)]\); subtracting \((\mathbb E\mu_t)^2\) instead of \(\mathbb E\mu_t^2\) loses patch-mean variation.



### Finding and scope

The stated stationarity conditions do not remove patch-mean variation. The missing term is a genuine local formula error; the code directly estimates sample statistics, so no dataset-level performance change follows from this witness.



### Proposed correction

Use expected within-patch covariance or explicitly change the target to pooled pixel variance. The algebra alone does not repair an experiment.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: Mean-standard-deviation scaling does not give unit expected variance

Assessment: supported; impact: minor



Source: Section 3.2, PDF p. 4; supplements A–B, PDF pp. 22–23; author model/normalizer.py, lines 35–48.



### Source claim (paraphrase)

SCIN is said to ensure zero expected mean and unit expected variance, while the documented procedure and code average per-patch standard deviations.



### Analysis

With exact scale \(s=\mathbb E\sigma>0\), expected normalized within-patch variance is \(\mathbb E\sigma^2/(\mathbb E\sigma)^2=1+\operatorname{Var}(\sigma)/(\mathbb E\sigma)^2\). For equiprobable contrasts \(1,3\), the mean scale is \(2\), and expected variance is \((1/4+9/4)/2=5/4\), rather than one. The nonnegative patches \(4+AS(1,-1,-1,1)\), with \(A\in\{1,3\}\) and independent sign \(S\), realize this witness. Under the release's sample-standard-deviation convention, average sample variance is \(1.25\) and population variance \(0.9375\); conventions must not be mixed.



### Finding and scope

Unit expected variance is not guaranteed, while the weaker unit mean standard deviation in the supplement is valid. No segmentation or unmixing score change is established.



### Proposed correction

Retain the algorithm and state unit mean standard deviation, or use \(\sqrt{\mathbb E\,v}\) if expected within-patch variance is the intended normalization. Changed scaling requires empirical evaluation.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- Local contradictions and specification differences do not establish the magnitude or direction of changes to the published benchmark scores.

- No author contact or adoption; novelty and complete historical-run provenance are unestablished.
