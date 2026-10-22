# PARTONOMY: Large Multimodal Models with Part-Level Visual Understanding



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The pooled Gaussian objective and released tokenwise loss differ beyond scale. Rare-class and zero-shot interpretations need explicit limits, and several appendix comparisons overstate their tables.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The published pooled-span Gaussian KL penalty differs from the released tokenwise MSE objective

Assessment: supported; impact: minor



Source: Section 4, Query Projection with KL Constraint, PDF p. 7.



### Source claim (paraphrase)

Paraphrase: in Query Projection with KL Constraint, Section 4, p. 7, the last-layer representations are pooled over each contiguous B/I span and compared with the corresponding pooled frozen teacher representation through a Gaussian KL penalty. Footnote 3 identifies mean pooling. The displayed formula is unnumbered. With \(N_+\) spans and \(m_s\) tokens in span \(s\), it is

\[L_{\mathrm{paper}}=\frac1{N_+}\sum_{s=1}^{N_+} \frac{\|\bar h_s-\bar t_s\|_2^2}{2\sigma^2},\qquad \bar h_s=\frac1{m_s}\sum_{k\in s}h_k,\quad \bar t_s=\frac1{m_s}\sum_{k\in s}t_k.\]



### Analysis

For one two-token span, let student vectors be \((1,0),(-1,0)\) and teacher vectors both zero. The pooled means agree, so the paper's penalty is \(0\), while tokenwise MSE is positive. In general tokenwise MSE adds the within-span variance of the student–teacher deviations. Changing a scalar loss weight cannot remove that extra term.

For dimension \(d=2\) and \(\sigma=1\), the current elementwise-mean loss gives \(1/4\) for that span. Generally it equals the pooled penalty divided by \(d\), plus \((2\sigma^2md)^{-1}\sum_k\|\Delta_k-\bar\Delta\|^2\). This extra nonnegative within-span variance term is structural, while one-token and constant-displacement spans are matching controls up to dimensional scaling.



### Finding and scope

The current release penalizes token-level variation absent from the stated pooled objective; the actually trained objective and resulting benchmark effect remain untraced.



### Proposed correction

Either pool each student and teacher span first and sum squared coordinate differences as stated, or document the actual tokenwise feature-averaged loss and its extra variance term. Any change of loss scale needs separate empirical assessment.

The existing objective or interpretation proposal remains applicable to current v3/current-head source; no author adoption is established.



## Problem 2: Image-balanced macro-gIoU does not establish improved segmentation of rare part classes

Assessment: supported; impact: minor



Source: Section 3.3, Segmentation Evaluation, PDF p. 6; Appendix C.2–C.3, PDF p. 18.



### Source claim (paraphrase)

Paraphrase: Section 3.3, Segmentation Evaluation, p. 6, defines micro-gIoU by averaging all part-mask IoUs and macro-gIoU by first averaging within each image, then averaging the image means. The text interprets the latter as less affected by common parts. Appendix C.2-C.3, p. 18, attributes reported macro advantages to rare or uncommon part performance.

The released evaluator confirms the averaging unit: src/evaluation/evaluators/masks.py, lines 47-74, appends one mean per update in the macro branch and all paired mask IoUs in the micro branch. No part-class label is used for this reduction.



### Analysis

Averaging first by image equalizes image weights, not part-class frequencies. With one mask in each of ten images, nine common-class successes can dominate a complete rare-class failure in the tenth image. Therefore a higher image-macro gIoU need not imply better rare-class performance. The metric remains well defined and useful for image balancing.

An explicit ranking reversal uses nine common-class masks and one rare-class mask, one per image. Model A has IoUs \(1\) on common masks and \(0\) on the rare mask; model B has \(7/9\) and \(1\). Image-macro favors A, \(0.9>0.8\), while rare-class performance favors B, \(0<1\), and class-macro favors B, \(1/2<8/9\). Binary masks on a nine-pixel ground truth realize all values.



### Finding and scope

Metric-inference clarification; the metric itself is well defined.



### Proposed correction

Interpret the current metric as a mean of per-image mask IoUs. Tie stronger rare-part conclusions to explicitly defined class identities, frequencies and class-stratified results.

The existing objective or interpretation proposal remains applicable to current v3/current-head source; no author adoption is established.



## Problem 3: Several comparative conclusions in Appendix C do not follow from its own printed tables

Assessment: supported; impact: minor



Source: Appendix C.1–C.3, PDF p. 18; Tables 9–11, PDF pp. 18–19.



### Source claim (paraphrase)

Appendix C.1-C.3, p. 18, makes stronger statements than some entries in Tables 9-11, pp. 18-19, support. The relevant claims, paraphrased, concern uniform superiority over the zero-shot baselines, a maximum two-point micro-gIoU gap after finetuning, and a macro-gIoU advantage used to diagnose another model’s treatment of uncommon parts.

This analysis checks these as substantive claims about comparative performance. It does not count numerical formatting, spelling, or table-caption mistakes as errata. The mismatch matters because it can reverse which method is favored on a task.



### Analysis

The appendix's uniform-superiority wording has a PartImageNet Intersection-macro exception. Its claimed maximum micro-gIoU deficit of two points is also contradicted by the PACO comparison, whose gap is \(3.8\) points. The macro result alone cannot diagnose another model's rare-class behavior, for the image-versus-class averaging reason in the preceding problem. These are corrections to conclusions drawn from the printed tables, not new performance measurements.

Current Table 10 gives PLUM \(12.2\) versus PixelLM \(12.8\) for zero-shot PartImageNet Intersection macro, and finetuned Difference macro \(60.7\) versus GLaMM \(65.4\), reversing the asserted advantage. Current Table 9 gives finetuned PACO Difference micro \(32.2\) versus PixelLM \(36.0\), a gap of \(3.8\), exceeding the stated two-point limit. Favorable cells remain; no new IoUs or significance test were computed.



### Finding and scope

Narrow the appendix comparisons to their individual printed wins and losses. No new significance test or overall ranking is established.



### Proposed correction

A correction supported by the printed evidence is: PLUM leads most zero-shot segmentation comparisons in these tables, with a PartImageNet Intersection-macro exception; after finetuning it leads the six Identification/Intersection macro cells, while its micro-gIoU gap reaches \(3.8\) points on PACO. Difference-macro results depend on the dataset and comparator. They do not establish uniform dominance or a per-class diagnosis.

A local correction or qualification is proposed where specified; author adoption is not established.

The existing objective or interpretation proposal remains applicable to current v3/current-head source; no author adoption is established.



## Problem 4: Zero-shot requires the stated training-stage qualification; it does not mean absence of part-mask supervision

Assessment: not_issue; impact: no_issue_found



Source: Section 5, Implementation Details, PDF p. 7; Appendix A.1, PDF pp. 15–16; Appendix C.1, PDF p. 18.



### Source claim (paraphrase)

Section 5, Implementation Details, p. 7, explicitly defines the zero-shot baseline as the checkpoint after initial adaptation on a mixture that includes PACO-LVIS, Pascal Parts, and PartImageNet, before further PARTONOMY task finetuning. Appendix A.1, pp. 15-16, also describes this preliminary training stage. In contrast, Appendix C.1, p. 18, includes a statement that PLUM uses no part masks during pretraining.



### Analysis

The source qualifies zero-shot by training/evaluation stage. Prior part-mask supervision is compatible with that narrower usage; it is only incompatible with an unqualified claim of no part-mask training. Retaining the stated qualification resolves the apparent contradiction.



### Finding and scope

No additional error established beyond terminology scope.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
