# VividFace: A Robost and High-Fidelity Video Face Swapping Framework



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The hybrid training loop exhausts persistent iterators. Mask-fill intent and retrieval trial units remain unresolved, while the shorter sample demo is a reproduction scope limitation.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Persistent finite iterators exhaust during hybrid multi-epoch training

Assessment: supported; impact: minor



Source: Section 3.2/3.4; train.py, lines 435–443; train.sh



### Source claim (paraphrase)

The release constructs both finite loader iterators once before a requested multi-epoch alternating loop.



### Analysis

For two four-batch loaders, epoch zero consumes two batches from each and epoch one consumes the remaining two. Epoch two’s first video request raises StopIteration; only \(8\) updates occur despite the \(1000\)-epoch request. In general completion needs \(E\lceil L/2\rceil\le L_v\) and \(E\lfloor L/2\rfloor\le L_i\). Re-entering the outer loop does not renew exhausted iterator objects. This reasoning depends only on ordinary finite iterator semantics, not model or accelerator execution.



### Finding and scope

The released loop cannot generally perform its requested training schedule. Historical private training and published scores are not thereby proved wrong.



### Proposed correction

Renew iterators at each epoch for the equal-length schedule; explicitly choose stopping/cycling/resampling for unequal lengths and define whether an epoch is a full pass through either dataset.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Mask filling changes when unrelated frames are duplicated

Assessment: needs_evidence; impact: needs_evidence



Source: Section 3.3; train.py, lines 504–507; infer.py, line 408



### Source claim (paraphrase)

The conditioning expression uses per-frame/channel spatial numerators divided by total mask area across every flattened frame.



### Analysis

For \(N\) identical constant frames of value \(c\) with common nonempty mask area \(a\), each numerator is \(ca\) and the denominator is \(Na\); masked fill becomes \(c/N\). With \(c=1\), duplication changes fill from \(1\) to \(1/2\), even though the original pixels and mask are unchanged. Unmasked pixels are preserved. The paper does not require a per-frame-mean filling rule, so unintended semantics cannot be concluded from this dependency alone.



### Finding and scope

Cross-frame and frame-count dependence is exact, but whether it violates intended conditioning remains unresolved. No poorer temporal or identity score is inferred.



## Problem 3: Video-level retrieval percentages require a denominator clarification

Assessment: needs_evidence; impact: needs_evidence



Source: Section 5.1 and Tables 1/3



### Source claim (paraphrase)

The protocol states \(200\) generated videos and temporal average cosine comparisons, while reporting Top-1 \(78.3\%\) and Top-5 \(90.2\%\).



### Analysis

If each video produces one binary ranked result, accuracy lies on multiples of \(100/200=0.5\) percentage points; neither printed value is attainable, including one-decimal rounding. But framewise ranking over \(200\times128=25600\) frames has spacing \(0.00390625\) points, and \(20045\) successes gives \(78.30078125\%\). Repeats, exclusions or different pairing counts could likewise explain finer increments.



### Finding and scope

The direct one-rank-per-video reading is incompatible with the table, but the actual hidden metric convention is unresolved. No replacement accuracy is justified.



## Problem 4: The sample demo is not the full benchmark protocol

Assessment: not_issue; impact: minor



Source: Appendix A; infer.py, lines 666–667 and 760



### Source claim (paraphrase)

The paper evaluates \(128\)-frame videos with \(32\) DDIM steps; the README sample demo caps frame length at \(80\) and requests \(40\) steps.



### Analysis

A \(128\)-frame input remains divisible by \(8\), then the source cap yields \(80\) frames. The pipeline explicitly receives \(40\) inference steps. The README calls this a sample test, so a separate benchmark implementation could use the published settings.



### Finding and scope

This limits reproduction through the demo rather than disproving a paper result. A matching evaluator needs explicit frame cap, steps, checkpoint and metric configuration.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
