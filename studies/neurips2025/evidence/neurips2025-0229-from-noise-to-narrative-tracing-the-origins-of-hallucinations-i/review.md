# From Noise to Narrative: Tracing the Origins of Hallucinations in Transformers



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Current Figure 5b contains 126 pairs despite its stated 252-pair quartile, matching a second median filter. Released analysis also differs in length-scaled maxima, repeated-score aggregation, semantic purity and activation frequency.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: The plotted intervention population is smaller than stated

Assessment: supported; impact: minor



Source: Figure 5b/caption, current PDF p.8; Language/analysis/suppress_hall_scores.py, lines 84 and 183–210



### Source claim (paraphrase)

The caption assigns mean reduction \(0.19\) to a \(252\)-example top quartile of \(1006\) cases; final plotting applies another within-quartile median filter.



### Analysis

The first rule selects raw faithfulness below its full-data lower quartile; the second keeps its lower half. Distinct scores yield \(252\), then \(126\). Independently, current-PDF count-axis/vector geometry gives before counts \((11,36,79)\), after \[(11,4,2,8,5,7,5,11,16,57)\], each totaling \(126\). The code uses ordinary unweighted histograms. The mean lines therefore concern the narrower displayed subset rather than a verified full-quartile effect.



### Finding and scope

The plotted population disagrees with its caption. The excluded half’s effect is unknown; its inclusion could coincidentally preserve the rounded mean, but that is not verified.



### Proposed correction

Recompute the full initial cohort or explicitly describe the second selection and smaller population. No corrected full-cohort mean is available.

A proposed correction is described; author adoption is not established.



## Problem 2: The maximum-activation statistic is length-scaled

Assessment: supported; impact: minor



Source: Section 5; Language/train/hall_score_pls.py, line 41



### Source claim (paraphrase)

The paper defines \(\max_ta_{itj}\), but code uses \(\max_ta_{itj}/n_i\).



### Analysis

Non-BOS rows \((1,2),(3,4)\) have maxima \((3,4)\), versus released \((1.5,2)\). Repeating the rows preserves maxima but changes release output to \((0.75,1)\). A sample-dependent divisor cannot generally be removed by column scaling. This operator example does not assume actual repeated words preserve transformer activations.



### Finding and scope

PLS/VIP preprocessing differs and can encode length. Original activations/logs are needed for changed predictive results.



### Proposed correction

Remove the divisor to implement the written maximum, or declare the length-scaled statistic and compare maxima/length-only controls on common splits.

A proposed correction is described; author adoption is not established.



## Problem 3: The first cross-validation repeat is duplicated

Assessment: supported; impact: minor



Source: Language/train/hall_score_pls.py, repeat initialization/append and final plot aggregation



### Source claim (paraphrase)

Ten pooled out-of-fold repeat scores are stored as \((r_0,r_0,r_1,\ldots,r_9)\); the point is the first score and the error bar its duplicated-list population deviation.



### Analysis

For control scores \(r_s=s/10\), deviation becomes approximately \(0.30287875\), versus \(0.28722813\) with each once; first point \(0\) differs from repeat mean \(0.45\). These illustrate aggregation only. PLS fits training folds, so no fitting leakage is alleged. Repeat-level pooled variability is legitimate if identified.



### Finding and scope

Duplicate storage is a release error; point/error-bar conventions require clarification, with no corrected original uncertainty available.



### Proposed correction

Store each repeat once, declare the point and deviation convention, preserve negative coefficients in records and label the repetition unit.

A proposed correction is described; author adoption is not established.



## Problem 4: Categorical purity is not semantic cosine coherence

Assessment: supported; impact: minor



Source: Semantic interpretability definition; Vision/analysis/vit-noise-sae-interpretability.py, stats and PURITY_THRESH



### Source claim (paraphrase)

The paper describes top-\(16\) label cosine coherence with threshold \(0.75\). Active code uses maximum label fraction with threshold \(0.30\), leaving its cosine helper unused.



### Analysis

Eight labels each of orthogonal types give majority \(1/2\), passing code, but distinct-pair cosine \(7/15<0.75\). Conversely, \(16\) distinct labels with unit vectors \(e_r=\sqrt{0.9}u_0+\sqrt{0.1}u_r\) have pairwise cosine \(0.9\), passing semantic coherence, but majority \(1/16<0.30\). Including self-pairs preserves both decisions. These are metric-domain witnesses, not claimed pretrained embeddings.



### Finding and scope

The active metric is a different function; original labels/embeddings are required to reconcile interpretability percentages. Qualitative examples remain possible.



### Proposed correction

Define normalized label embeddings and pair averaging, then apply the stated cosine criterion; alternatively identify the actual categorical statistic under its own definition.

A proposed correction is described; author adoption is not established.



## Problem 5: Activation frequency divides batch means twice

Assessment: supported; impact: minor



Source: Vision/analysis/vit-noise-sae-interpretability.py and companion maximally-activating-image routine



### Source claim (paraphrase)

The code sums batch activation means and divides again by total token count.



### Analysis

One feature active on all \(4\) tokens yields \(1/4\) in one batch or \(1/2\) in two equal batches, while true frequency is \(1\). For equal batch size \(m\), released frequency is true frequency divided by \(m\); unequal sizes also misweight batches. At \(32\) images times \(49\) patches, the illustrative log shift is \(-\log_{10}1568\approx-3.19535\), potentially moving frequency bins.



### Finding and scope

The quantity depends on irrelevant partitioning and is not empirical activation probability. Actual selected features and percentages remain unrecomputed.



### Proposed correction

Sum integer active counts and token totals, then divide once. Linearity proves partition invariance; regenerate actual bins to assess effects.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.
