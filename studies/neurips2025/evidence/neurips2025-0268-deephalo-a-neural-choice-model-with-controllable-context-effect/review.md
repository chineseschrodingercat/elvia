# DeepHalo: A Neural Choice Model with Controllable Context Effects



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



A one-layer model has a nonzero observable second-order effect, refuting depth-based order control under variable menu normalization. Padding and baseline correspondence are separate narrower concerns.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Actual-menu normalization creates higher-order effects in one layer

Assessment: supported; impact: major



Source: Sections 2.2 and 3.2, current arXiv v1 PDF pp.3 and 5–6, Eqs.(4)–(5)



### Source claim (paraphrase)

The feature-based architecture averages over actual menu size and asserts that layer l has interaction effects only through order l under its subset decomposition.



### Analysis

Use scalar features \(x=(1,2,3,4)\), one layer/head, unit weights, and ReLU encoders/modulators acting identically on these positive features. The specified utility is \(u_j(S)=x_j[1+\sum_{k\in S}x_k/|S|]\). For the always-present pair \(1,2\), log odds on menus \(12,123,124,1234\) are \(-5/2,-3,-10/3,-7/2\). The mixed difference for optional items 3 and 4 equals \(-7/2+3+10/3-5/2=1/3\). First-order relative utilities must have zero such difference. The observable odds eliminate any common utility-shift ambiguity.



### Finding and scope

The one-layer interaction-order upper bound is false over the stated variable-menu domain. Permutation equivariance survives; a fixed-cardinality empirical slice does not establish the required subset identities.



### Proposed correction

Replace actual-size normalization by a fixed positive constant and mask all invalid contributions. With base-only modulators and linear aggregation/readout, Boolean menu-membership degree increases by at most one per layer, proving the repaired order upper bound.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Padded alternatives enter the context summary

Assessment: supported; impact: minor



Source: Appendix B.2, current arXiv v1 PDF p.18; Model/FeatureBased.py, DeepHalo.forward, lines 63–76



### Source claim (paraphrase)

The appendix says dummy states are reset to zero after residual layers and do not affect aggregation. The release sums all affine projected states before applying a valid-item mask only to the modulator.



### Analysis

A zero raw feature need not have zero embedding after biased layers and normalization. Even if its state were zero, an affine aggregate projection contributes its bias. With projection weight zero and bias one, five slots containing two real items produce unmasked summary \(5/2\), versus the correct masked summary \(1\). Item-specific modulators can turn that difference into unequal valid-logit changes; final dummy softmax masking cannot remove prior context contamination.



### Finding and scope

The released class violates the specified dummy noninterference. Actual real-data training paths/checkpoints are not available to quantify the published effect.



### Proposed correction

Mask embeddings and residual states, and mask after each affine aggregate projection before summing. This gives padding invariance by induction for deterministic evaluation.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: Named baseline descriptions differ from the cited models

Assessment: supported; impact: minor



Source: Appendix C.2.2, current arXiv v1 PDF p.20; RUMnet Section 2.3; TasteNet-MNL Section 3.1



### Source claim (paraphrase)

The appendix describes RUMnet as an alternative-order GRU and TasteNet as deriving user representations from mean offered-item features, while interpreting the comparison as involving context-independent approaches.



### Analysis

The cited RUMnet uses shared feed-forward component utilities, per-component softmax and probability averaging, not an item-order GRU. A scalar GRU recurrence \(h_t=h_{t-1}/2+\tanh(x_t)/2\) can change matched item utility differences when order reverses. Original TasteNet maps fixed consumer characteristics to taste coefficients; replacing those with menu mean changes the object. For the described scalar dot product \(u_j=x_j\bar x_S\), log odds of features 1 and 2 change from \(-3/2\) to \(-2\) when feature 3 is added.



### Finding and scope

The published baseline specifications are different from the cited architectures. Missing baseline training implementations leave open whether the code or the descriptions need correction; no table ranking is recalculated.



### Proposed correction

Identify and release the actual baseline architectures/inputs and distinguish adapted models from the named originals; rerun faithful versions if the intended comparison is to those originals.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
