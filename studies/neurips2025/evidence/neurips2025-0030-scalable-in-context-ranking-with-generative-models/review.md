# Scalable In-context Ranking with Generative Models



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current later PyTorch release retains untruncated MRR under cutoff-specific names, an empty-prediction correctness fallback, and unscaled ranking logits in its SDPA path. It also retains a documented later normalization change that can reverse cross-head document rankings. These Minor release/replication concerns do not establish errors in the original JAX/TPU results.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: MRR lacks the requested cutoff and empty predictions count as correct

Assessment: supported; impact: minor



Source: Section 5.1, PDF p. 8; current src/blockrank/utils.py, evaluation metrics lines 352–358 and 412–443; scripts/eval_attn.py, incremental evaluator



### Source claim (paraphrase)

The paper reports MRR@\(10\) and P@1.



### Analysis

The current evaluation requests untruncated recip_rank and copies that one result into every reported MRR cutoff. For one query with \(11\) candidates, only the last relevant, predicting only the first \(10\) causes unpredicted candidates to be filled with zero scores. The relevant item then contributes \(1/11\) to the release’s MRR@\(10\), although no relevant item was returned within the cutoff and the correct truncated value is zero. Separately, an empty prediction becomes an empty top-one set; the code’s subset test accepts it against any ground-truth set. Precision@\(1\) requires an actual relevant first item, so this empty-output success is false. These are current source behaviors, not reconstructed historical table measurements.



### Finding and scope

The current released metric helpers still violate their cutoff and empty-output contracts. Correcting affected scores requires predictions and relevance labels; no numerical change to the paper’s original tables has been established.



### Proposed correction

Apply the rank cutoff before reciprocal-rank scoring; return zero for empty predictions; preserve IDs/scores explicitly.

The latest author default head retains both the copied untruncated reciprocal-rank result and empty-set subset check. The original paper explicitly used JAX/TPU, so the later PyTorch evaluator is not assumed to be its historical evaluator.



## Problem 2: The later scoring denominator changes document rankings

Assessment: supported; impact: minor



Source: Sections 4.2/4.3, PDF pp. 7–8; current src/blockrank/losses.py, document score normalization lines 65–80; December 2025 normalization change



### Source claim (paraphrase)

The paper normalizes query-to-document attention over document tokens.



### Analysis

The paper normalizes each head over document tokens. The current release instead includes instruction/query token mass in each denominator, reweighting heads before aggregation. For two one-token documents and two heads, let document exponential masses be \((0.9,0.1)\) and \((0.2,0.8)\), with other-token masses \(9\) and \(1/9\), respectively. All values are positive and hence realizable by finite logits. Document-only means are \((0.55,0.45)\), ranking A first; the current all-token means are \((0.135,0.365)\), ranking B first. A single head or equal document-mass fractions across heads preserves ranking, which bounds the counterexample. The change is attributed to the author’s later public normalization commit and may be intentional; it is not established to be an accidental defect.



### Finding and scope

The current release is a mathematically distinct scoring variant and cannot be assumed equivalent to the written document-only normalization. The finding is a Minor version/replication mismatch, not proof of an invalid original ranking method or worse performance of the variant.



### Proposed correction

Use the documented document-token denominator or explicitly describe the alternate scoring variant. Historical table attribution remains unresolved.

The current default head retains the later all-token denominator. The change is historically attributed to the December 2025 author commit. Restoring document-only normalization is conditional on seeking the paper’s scoring definition; no claim of author intent or adoption is made.



## Problem 3: SDPA ranking logits omit attention scaling

Assessment: supported; impact: minor



Source: Section 4.2, PDF p. 7; current blockrank_std_attention.py, SDPA return-score construction lines 640–645



### Source claim (paraphrase)

The SDPA and eager attention backends should return equivalent ranking logits for the same query/key tensors.



### Analysis

The hidden-output SDPA call receives the correct scaling, but its separately returned ranking logits are \(QK^\top\) plus mask, omitting \(1/\sqrt{d_k}\). Set \(d_k=4\), query \(q=(1,0,0,0)\), and key first coordinates \[(-20,-20,4,-4,3,3,-20,-20),\] with other coordinates zero; the middle two pairs are documents A and B. Correct scaled document exponential sums satisfy \(e^2+e^{-2}<2e^{1.5}\), ranking B first. Unscaled returned sums satisfy \(e^4+e^{-4}>2e^3\), ranking A first. A common positive scaling of individual logits does not preserve a ranking obtained after exponentiation and token aggregation. The hidden-output operation remains correctly scaled; the discrepancy is specifically in the returned score path.



### Finding and scope

The current SDPA ranking-score path still differs from the specified scaled attention and can reverse document rankings. This particular omission does not apply to the separately scaled eager path; no original JAX benchmark effect is established.



### Proposed correction

Apply \(1/\sqrt{d_k}\) to returned logits under the same convention, then check backend parity.

Current SDPA code retains the missing scale in the independent returned-logit construction. The existing local correction scales that product before adding its mask; it changes no already-correct hidden-output computation and has no demonstrated benchmark result.



## Limits

- No author program, attention kernel, model or old verifier was executed. The public PyTorch release is later than the original JAX/TPU experiments. Missing historical predictions prevent estimating metric or ranking effects on the paper’s tables. Normalization is a documented version difference whose intent and empirical merits remain unestablished.
