# KVCOMM: Online Cross-context KV-cache Communication for Efficient LLM-based Multi-agent Systems



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The release uses L1 placeholder distances where the method describes L2, and quality-preservation wording exceeds the reported point estimates. Entropy/top-p scope is qualified; the authors’ previously corrected first-token accounting is retained as cleared current evidence.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: The interpolation metric is L1 rather than the described L2

Assessment: supported; impact: minor



Source: Eqs.(6)–(7), PDF p.8; approximation Appendix/Table A.4; _compute_anchor_weight_entry



### Source claim (paraphrase)

Placeholder distances use mean absolute tensor differences, while the method and norm ablation identify Euclidean weighting.



### Analysis

Use two identical layers, one token, query \((0,0)\), anchors A=\((0,20)\), B=\((11,11)\), temperature \(1\). Full Euclidean distances are \(\sqrt{800}\approx28.2843\) and \(22\), giving weights approximately \((0.001862,0.998138)\), entropy \(0.01957\) bits below the default \(0.3\) threshold. Reuse is admitted. Placeholder mean absolute distances are instead \(10,11\), giving \((0.731059,0.268941)\) and reversing anchor preference. For offset values \(0,10\), the interpolated coordinate changes from about \(9.98138\) to \(2.68941\). Positive-temperature rescaling cannot repair a reversed ordering.



### Finding and scope

The accepted-input release is a hybrid metric, not the stated L2 interpolation. Actual cache prevalence, performance and table-producing commit are unresolved.



### Proposed correction

Either use an explicitly defined Euclidean reduction or describe the hybrid admission/prefix/placeholder metrics and match the ablation configuration.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: Activation cutoff differs from conventional top-p selection

Assessment: needs_evidence; impact: minor



Source: Section 3.3 and cache-maintenance Algorithm 1; predict_as_anchor, lines 1041–1055



### Source claim (paraphrase)

The source uses the last cumulative sum below \(p\), and selects all anchors when no cumulative sum is below \(p\).



### Analysis

At \(p=0.9\), weights \((0.95,0.05)\) select both anchors, while \((0.60,0.35,0.05)\) select only the first with mass \(0.60\). Conventional nucleus selection would select one and two respectively. The first case can pass the entropy admission gate. These counts affect future eviction, not current interpolation weights. The paper does not define activation as conventional nucleus selection.



### Finding and scope

The threshold discontinuity is established, but classification as an unintended defect requires the missing activation contract.



### Proposed correction

If standard nucleus selection is intended, retain the smallest prefix reaching mass \(p\), including its crossing element. This conditional correction is not an accuracy guarantee.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: Low relative entropy does not bound absolute distance

Assessment: not_issue; impact: minor



Source: Section 3.3, entropy admission Eq.(5); conditional Lipschitz propositions



### Source claim (paraphrase)

Low entropy is used as a reuse-confidence heuristic; its mathematical information is relative anchor preference.



### Analysis

For anchors \(0,10\) and every scalar query \(q>10\), distances are \((q,q-10)\). Their softmax weights and entropy remain fixed, with entropy about \(0.00072045\) bits, while nearest distance grows without bound. For the \(1\)-Lipschitz offset \(F(q)=q\), interpolation remains near \(9.999546\); queries \(20,100,1000\) have errors about \[10.000454,90.000454,990.000454\]. This is a function-class witness, not an asserted unbounded ray in an actual finite-vocabulary model.



### Finding and scope

The heuristic does not supply an absolute-radius guarantee. The paper’s conditional distance bounds are not contradicted.



## Problem 4: First-token latency is already included in the current table

Assessment: not_issue; impact: minor



Source: Section 4.3 correction footnote and Table 2, PDF p.9



### Source claim (paraphrase)

The authors disclose an earlier omission and report updated latency components.



### Analysis

Agent \(5\) has \(17.5+21.1+16.2=54.8\) ms, and \(428.6/54.8\approx7.82117\), matching \(7.82\). The five rounded speedups agree with component sums. These are TTFT/prefill results; ordinary decoding is not accelerated and full-response speedup is not inferred.



### Finding and scope

No current-table arithmetic error is established; the earlier omission was already corrected by the authors.



## Problem 5: Universal quality preservation exceeds the reported results

Assessment: supported; impact: minor



Source: Abstract and Section 3.1; Table 1, PDF p.8; Table A.2 and AIME discussion



### Source claim (paraphrase)

The paper describes operation without quality degradation across its workload results.



### Analysis

HumanEval with two Qwen-Coder agents changes \(86.3\%\to81.4\%\), a decrease of \(4.9\) percentage points. Other reported configurations decline, including AIME by \(9.2\) points, while some improve or tie. The appendix acknowledges a resource/decoding-length explanation for AIME; it does not erase the observed loss. Rounded point estimates alone do not establish statistical significance or isolate the cache approximation’s causal effect.



### Finding and scope

The supported evidence is heterogeneous performance, not universal preservation. No benchmark result is remeasured or declared fabricated.



### Proposed correction

Qualify preservation by configuration and acknowledge reported accuracy/resource tradeoffs. Matched output-budget evidence is needed for a causal explanation.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
