# CLAWS:Creativity detection for LLM-generated solutions using Attention Window of Sections



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



A historical supplemental label-overwrite defect is already repaired in a later repository. Released AP conventions and prototype confidence handling differ, and input/request artifacts do not identify the final filtered benchmark.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The current correctness guard preserves hallucinated labels

Assessment: not_issue; impact: no_issue_found



Source: Section 2.2.2, PDF p. 4; Appendix B.1, PDF p. 21; separate supplement PDF p. 8, printed p. 24.



### Source claim (paraphrase)

Section 2.2.2 and Appendix B.1 classify a response as typical or creative only after the correctness gate. The original supplementary evaluator overwrote hallucinated labels in its final novelty loop; the current author repository instead guards that loop.



### Analysis

In current src/labeling.py, any evaluator rejection assigns Hallucinated_Solution. Lines 131–138 run novelty assignment only when that label is absent. A response rejected by both judges therefore retains its hallucinated label. This directly removes the historical overwrite counterexample.



### Finding and scope

The historical supplementary defect is fixed in the current source. Which version produced the published measurements is not established, and no current labeling defect is asserted from this witness.



## Problem 2: The binary APm column is not the same metric across the released evaluation strategies

Assessment: supported; impact: minor



Source: Section 4.3, PDF p. 7; Table 3, PDF p. 9; Appendix Tables 11–15, PDF pp. 28–30.



### Source claim (paraphrase)

Section 4.3, PDF p. 7, defines APm as macro Average Precision with equal class weights; Table 3 and Appendix Tables 11–15 use that heading for binary hallucination detection. The released evaluation strategies under src/evaluation_strategy use positive-class-only AP in some paths and the mean of classwise AP values in others.



### Analysis

For labels \((0,0,0,1)\) with tied class scores \((0.5,0.5)\), positive-class AP is \(0.25\), negative-class AP is \(0.75\), and macro AP is \(0.5\). These distinct quantities cannot share a macro-AP label without qualification. Perfect predictions give one under both conventions, so agreement on that control does not establish equivalence.



### Finding and scope

The current binary evaluation paths compute different AP quantities under a common macro-AP heading. Published table values have not been recomputed.



### Proposed correction

Average the independently computed classwise AP values in every strategy, or explicitly label positive-class AP separately.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 3: Prototype AUROC and AP discard the continuous distance ordering

Assessment: supported; impact: minor



Source: Sections 4.2–4.3, PDF p. 7; released prototype.py, lines 324–361.



### Source claim (paraphrase)

Section 4.2, p. 7, defines the prototype classifier using Euclidean distance to class center embeddings and the nearest class. Section 4.3 then reports AUROC and AP alongside F1. The later implementation’s prototype.py, lines 324-349 for multiclass and \(351\)-\(361\) for binary classification, passes one-hot predicted class labels to the ranking metrics. The MLP, XGBoost, and TabM strategies pass class probability scores.



### Analysis

One-hot class predictions discard the continuous prototype-distance ordering. Under standard tie credit their binary AUROC is \((\mathrm{TPR}+\mathrm{TNR})/2\). Two examples assigned the same class can still have different distances, so this evaluates a coarser score than the probability-ranking metrics used by other strategies. Hard-label AUROC itself remains defined.

For one-dimensional prototypes at \(0\) and \(1\), queries \(0.1,0.2,0.3,0.4\) with labels \(0,0,1,1\) all receive hard label \(0\). Hard-label AUROC and positive-class AP are both \(0.5\), whereas the score \(-|z-1|\) ranks both positives above both negatives and gives both values \(1\).



### Finding and scope

Supported metric-comparability clarification, not an assertion that hard-label ROC is undefined.



### Proposed correction

Keep nearest-prototype labels for F1 and accuracy. To assess distance ranking, retain a class score such as \(s_c(z)=-\|z-\mu_c\|_2\) and use those scores for the classwise ROC/AP calculations, with the explicit averaging rule from Problem 2. ROC/AP depend on score order, so negative values themselves cause no problem. If normalized scores such as a distance softmax are chosen instead, specify that choice and any temperature fixed using reference/validation data. In multiclass settings, softmax normalization can alter a class’s one-versus-rest ranking; no equivalence between these different score constructions is asserted here.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 4: Released input datasets and generation requests do not identify the described final filtered experiment

Assessment: supported; impact: minor



Source: Sections 2.3–2.3.1, PDF p. 4; released final-input filtering and reference-cap path.



### Source claim (paraphrase)

Sections 2.3–2.3.1 describe a final extended set of \(4545\) problems, a disjoint \(29\)-problem REF and \(371\)-problem TEST split, and at most two supplied reference solutions for non-REF prompts. The current data files and generation loop are the corresponding author-released inputs.



### Analysis

The current AMC, AIME and AHSME JSON lists contain \(2228,935,1732\) records, totaling \(4895\), which is \(350\) above the stated final count. Equality of full problem text after whitespace normalization gives \(16\) AMC–TEST matching pairs and zero REF–TEST pairs. This checks released inputs, not an unavailable final experiment manifest.

Current generation_and_feature_extraction.py loops through every supplied reference count. A non-REF record with three solutions therefore permits \(k=3\); with three generations per reference count it requests \(9\) responses, including a third-reference prompt. The stated cap is not enforced in this loop.



### Finding and scope

The release does not identify the described final filtered corpus, and its default generation path permits more than two non-REF references. These findings do not prove overlap or excess references in the actual table-producing runs.



### Proposed correction

Release the final filtered split manifest and apply the stated two-reference cap to non-REF requests. Preserve REF exceptions explicitly rather than deleting records solely to force a target count.

A local correction or qualification is proposed where specified; author adoption is not established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
