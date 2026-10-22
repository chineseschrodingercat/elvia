# Optimizing Retrieval for RAG via Reinforcement Learning



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The online positive/negative threshold conditions overlap without an explicit resolution rule. The re-indexing comparison also changes retriever representation, so it cannot isolate indexing strategy alone.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The stated online positive and negative conditions have overlapping domains

Assessment: supported; impact: minor



Source: Section 3.3, PDF p. 6 (threshold definitions).



### Source claim (paraphrase)

Mathematical transcription, with the surrounding procedure paraphrased: Section 3.3, PDF p. 6, defines the thresholds

\[T_q^+=\max_{d\in D_q^-}p(d),\qquad T_q^-=\min_{d\in D_q^+}p(d),\]

The following rule labels a document positive when \(p(d)>T_q^+\), negative when \(p(d)<T_q^-\), and otherwise discards it, without an explicit conflict rule.



### Analysis

When calibration negatives all lie below positives, \(T^+=\max p_{\rm neg}<T^-=\min p_{\rm pos}\). Any new score \(p\in(T^+,T^-)\) satisfies both \(p>T^+\) and \(p<T^-\), hence both printed label conditions. An explicit overlap rule or branch priority is needed; no observed double-label rate is inferred.

For a two-token gold answer \((a,b)\), let each required conditional probability be \(r\) versus alternative \(1-r\), followed by certain end-of-sequence. Fifty calibration documents with \(r=0.1\) fail greedy exact match and have gold probability \(0.01\); fifty with \(r=0.9\) succeed with probability \(0.81\). Both pools are nonempty. A later document with \(r=0.6\) has gold probability \(0.36\), strictly inside the overlap and satisfies both predicates.



### Finding and scope

A normalized autoregressive example proves ambiguous membership; unavailable training code leaves actual priority and double-insertion incidence unknown.



### Proposed correction

Explicitly state branch priority, or use the proposed conservative rule: positive above \(\max(T_q^+,T_q^-)\), negative below \(\min(T_q^+,T_q^-)\), and abstain otherwise. The latter is logically disjoint but has untested learning behavior.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 2: The re-indexing comparison changes both retrieval representation and indexing strategy

Assessment: supported; impact: minor



Source: Section 5.1, Figure 5, PDF p. 10; Appendix H, PDF pp. 22–23.



### Source claim (paraphrase)

Paraphrase: Section 5.1, PDF p. 10, interprets the comparison in Figure 5 as favoring late-parametric retrieval over periodic re-indexing. Appendix H, pp. 22–23, gives the detailed setup and attributes the weaker re-indexed configuration to index staleness.

The Appendix H baseline description uses SIDR for the late-parametric system and DPR for the periodic-re-indexing system. It states that the dimensionalities are \(30522\) and \(768\) respectively and explains the change by available GPU memory. The following training description nevertheless characterizes the models as differing only in their in-training retrieval strategies.



### Analysis

The observed comparison is \(Y(\mathrm{SIDR},\mathrm{late})-Y(\mathrm{DPR},\mathrm{periodic})\). Adding and subtracting \(Y(\mathrm{SIDR},\mathrm{periodic})\) separates a strategy effect from an unmeasured representation effect. The appendix discloses dimensions \(30522\) and \(768\), so this is documented confounding, not concealment. The two-system comparison cannot identify the sign or size of the strategy-only effect.



### Finding and scope

The disclosed backbone change leaves an unmeasured architecture component in the comparison; the complete-system advantage can remain valid.



### Proposed correction

Restrict the conclusion to the compared complete systems, or use a matched retriever/checkpoint and vary only the refresh policy to identify its effect.

A local correction or qualification is proposed where specified; author adoption is not established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
