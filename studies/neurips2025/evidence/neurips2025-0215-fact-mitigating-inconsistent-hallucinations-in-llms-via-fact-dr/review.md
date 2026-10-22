# FACT: Mitigating Inconsistent Hallucinations in LLMs via Fact-Driven Alternating Code-Text Training



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Under the described supervised pseudo-label interpretation, inverse-quality weighting reinforces low-quality code rather than penalizing its probability. The filter audit reports predictive values as sensitivity/specificity; a separate table inconsistency still needs original evaluation evidence.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: Inverse-quality weighting can reinforce a bad pseudo-label

Assessment: supported; impact: minor



Source: Sections 3.3–3.4, pp.5–6, Eqs.(4)–(8); Appendix B.1



### Source claim (paraphrase)

The paper calls both directions supervised fine-tuning and uses model-generated code as the text-to-code supervision target. Equation (8) weights its loss by \(1-S_i\), assigning non-executable code score \(S_i=0.1\). Under ordinary detached-target negative log-likelihood, this fits a low-quality target more strongly.



### Analysis

Let the two outputs be faithful code and code using an undefined year variable, with scores \(1\) and \(0.1\). Let faithful-code probability be \(q=\sigma(a)\). A bad target contributes \(-0.9\log(1-q)\), whose derivative is \(0.9q\). At \(a=0\), a unit descent step sends \(a\) to \(-0.45\) and \(q\) to approximately \(0.3893607661\); a good target has zero weight and produces no update. Sampling once from the initial model gives expected post-step faithful probability approximately \(0.444680383<0.5\).

For finite outputs with fixed quality scores and targets sampled from the same current policy, the expected detached-target gradient obeys \[\mathbb E[(1-S)\nabla(-\log p_\theta)]=\nabla\sum_c p_\theta(c)S(c).\] Gradient descent therefore moves against the local expected-quality gradient. This establishes the conditional mechanism, not an observed full-training result. Equation (8) does not expand the underlying loss; an unreported target repair, separate frozen sampling policy or rejection stage could change this interpretation, and the alternating reconstruction update can offset it.



### Finding and scope

The written inverse-quality rationale is not justified by ordinary supervised pseudo-label likelihood. Actual checkpoint behavior requires the precise target/loss pipeline; no end-to-end degradation is claimed.



### Proposed correction

For the same restricted setup, confidence weighting \(S[-\log p_\theta]\) reverses the expected gradient sign and improves expected proxy quality to first order. Rejecting or repairing non-executable targets is another proposed condition; neither is established as a validated replacement for the complete method.

A proposed correction is described; author adoption is not established.



## Problem 2: The stratified filter audit estimates predictive values

Assessment: supported; impact: minor



Source: Section 4.3, p.9, Fact Filtering analysis; Section 4.1, retained/non-factual/invalid fractions



### Source claim (paraphrase)

The audit samples \(100\) texts from each predicted factual/non-factual group, yet labels agreement rates \(93\%\) and \(92\%\) as true-positive and true-negative rates.



### Analysis

Conditioning on predicted group estimates positive and negative predictive values, rather than conditioning on true class. In the displayed balanced sample the counts are \(TP=93,FP=7,FN=8,TN=92\): sample sensitivity is \(93/101\), specificity \(92/99\), while predictive values are \(0.93\) and \(0.92\). If the sampled strata are representative and invalid cases are excluded, weighting by population predicted fractions \(a=0.5374,b=0.2785\) yields sensitivity \(a(0.93)/(a(0.93)+b(0.08))\approx0.957323\) and specificity \(b(0.92)/(b(0.92)+a(0.07))\approx0.871977\). These are conditional plug-in estimates, not validated population performance; the invalid fraction \(0.1841\) needs its own handling.



### Finding and scope

The stated sampling scheme does not directly estimate the named sensitivity/specificity. Individual annotations and uncertainty intervals are unavailable, so no exact population error rate is asserted.



### Proposed correction

Rename the observed stratum agreements as predictive values. To estimate sensitivity and specificity, specify reference labels, sampling weights, uncertainty and the treatment of invalid/abstained cases.

A proposed correction is described; author adoption is not established.



## Problem 3: One SQuAD metric pair needs evaluation provenance

Assessment: needs_evidence; impact: needs_evidence



Source: Table 2, p.9, LLaMA/SymbCoT row



### Source claim (paraphrase)

The row reports SQuAD F1 \(82.14\) and exact match \(86.20\).



### Analysis

For the standard same-example, same-prediction SQuAD metrics, exact match implies token F1 \(1\), and other F1 values are nonnegative. Hence aggregate F1 cannot be below exact match when aggregation weights and examples agree. The printed ordering violates that condition. A transposed cell, transcription error or different evaluation protocol is not distinguishable from the table alone.



### Finding and scope

The pair needs original predictions and metric definitions. This unresolved reporting observation is not counted as a demonstrated model-performance error.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.

- The related MIH-TCCT preprint has a different title/method and is not substituted for the current FACT publisher article. The precise unreleased text-to-code loss and checkpoint lineage remain unavailable.
