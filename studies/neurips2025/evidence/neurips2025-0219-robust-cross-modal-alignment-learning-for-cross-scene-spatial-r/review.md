# Robust Cross-modal Alignment Learning for Cross-Scene Spatial Reasoning and Grounding



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current released grounding path fails padding invariance, implements a different retention schedule from the paper, and omits an incomplete evaluation tail. Exact component/index examples establish these local defects; their effect on historical trained-checkpoint accuracy is unresolved.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: Validity masks do not protect the full grounding path

Assessment: supported; impact: minor



Source: model/vision/basic_modules.py, AP, lines 69–122; model/vision/transformers.py, encoder forward, lines 197–215; pipeline/pipeline_mixin_old.py, lines 563–569



### Source claim (paraphrase)

One aggregation branch normalizes over padding; the encoder adapter discards its supplied padding mask; evaluation bypasses the grounding head’s object mask.



### Analysis

For valid feature \(u=(1,0)\), let \(X_A=(u,u,0,0)\), \(X_B=(u,u,10u,10u)\), both with length \(2\). Admissible zero projection/balance parameters give a masked first branch \(u\), unmasked second branches \(u/2,11u/2\), and final outputs \(3u/4,13u/4\). Only padding values changed, so pooling is not padding-invariant.

The encoder receives a key-padding argument but calls self attention without it. With identity projections, four valid \(u=(1,0)\) and four invalid values changing from zero to \(v=(0,1)\), active attention returns \(cu\) versus \(cu+(1-c)v\), where \(c\approx0.9012299943\); valid-key masking returns \(u\) in both cases. Finally logits \((0.6,0.4,1.2,0.1)\) with validity \((1,1,0,0)\) select padded index \(2\) unmasked versus real index \(0\) masked. These are admissible component examples, not measured checkpoint outputs.



### Finding and scope

Padding can change valid features and permit prediction of no real object along the active release path. Its frequency and effect on published accuracy remain unmeasured.



### Proposed correction

For each nonempty valid set \(S\), normalize both pooling branches only over \(S\). Propagate and apply key-column validity before retention/softmax, and restrict final argmax to valid objects. Explicitly handle empty valid sets; a final mask alone does not undo earlier feature contamination.

A proposed correction is described; author adoption is not established.



## Problem 2: The active retention levels differ from equal quantiles

Assessment: supported; impact: minor



Source: Section 4.3, p.6, Eqs.(4)–(5); model/vision/transformers.py, Attention, lines 70–122



### Source claim (paraphrase)

The paper describes \(L=6\) equal quantile segments with progressive retention. The six active code branches mix half/full counts with fractions based on eighths.



### Analysis

At \(n=24\), the paper’s retained counts are \((4,8,12,16,20,24)\); current active counts are \((12,24,9,12,15,18)\). Divisibility removes rounding as an explanation. Branches one and four are equal under strict ranking, so their contribution is \((\mu_1+\mu_4)A_1V\), leaving only five distinct levels. Two additional computed branches do not enter the output and cannot restore the stated family.



### Finding and scope

The release is not an exact implementation of the equal-six-quantile construction. Which schedule generated historical results and which is intended require clarification.



### Proposed correction

Either document the actual fractions and duplicate level or implement the intended \(k_j=\lfloor jn/L\rfloor\), \(j=1,\ldots,L\), with positive-count and valid-key rules. Changing the schedule requires empirical re-evaluation.

A proposed correction is described; author adoption is not established.



## Problem 3: Grounding evaluation omits the last incomplete batch

Assessment: supported; impact: minor



Source: pipeline/pipeline_mixin_old.py, grounding evaluation, batch_size and num_batches around lines 518–536



### Source claim (paraphrase)

The grounding loop uses batch size \(3\) and floor division \(\lfloor N/3\rfloor\), although every query has already been encoded and no divisibility precondition is stated.



### Analysis

For \(N=5\), only indices \(0,1,2\) are processed. Outcomes \((1,1,1,0,0)\) give retained accuracy \(1\) versus complete accuracy \(3/5\); reversed outcomes give \(0\) versus \(2/5\). Thus the omitted tail can bias either way. For \(N<3\), no query is grounded and the later division has zero denominator. This is exact loop arithmetic, not a fresh neural evaluation.



### Finding and scope

The evaluator visits only \(N-(N\bmod3)\) queries. The actual omitted annotation list and its correctness require checkpoint-specific re-evaluation.



### Proposed correction

Iterate starting indices \(0,3,6,\ldots<N\) and clamp each end to \(N\). Those disjoint intervals cover every index exactly once. Guard empty sets and absent subgroups before division.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.
