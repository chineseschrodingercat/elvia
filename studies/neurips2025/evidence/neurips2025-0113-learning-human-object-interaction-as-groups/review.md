# Learning Human-Object Interaction as Groups



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The released HOI grouping release has no gradient route to its learnable proximity scorer and uses enclosing-box overlap and Euclidean neighborhoods where the paper specifies IoU and cosine similarity.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The learnable geometric proximity scorer has no differentiable route to the task loss

Assessment: supported; impact: minor



Source: Section 3.3, PDF pp. 4–5; Appendix Algorithm 1, PDF p. 23.



### Source claim (paraphrase)

Section 3.3, PDF pp. 4–5, and Algorithm 1, PDF p. 23, describe a learnable proximity score followed by selecting the \(K^g\) smallest-score entities and aggregating their features. Released models/geo_group.py, TransformerBlock.forward, uses the box_pos linear scorer only to produce top-k indices for gathering those entities.



### Analysis

The scorer values affect the task loss only through discrete neighbor indices and are then discarded. That index-selection operation provides no differentiable path to the scorer. Including the scorer in an optimizer cannot create a missing gradient route; learning it requires an additional continuous dependence or separate objective.



### Finding and scope

The declared proximity scorer cannot learn through discarded integer top-k indices; other group-context and detector parameters can still learn.



### Proposed correction

Either describe the scorer as fixed, or add a differentiable score-value route or separate learning objective. One existing proposal subtracts \(s_{ij}/\tau\) from selected-neighbor attention logits; a shared scorer bias cancels in that softmax, so use an identifiable parameterization. This changes the architecture and does not differentiate membership changes or establish restored mAP.

The existing local or architectural proposal remains applicable to the unchanged current-head source; no author adoption or corrected model performance is established.



## Problem 2: The geometric overlap feature uses enclosing-box area rather than union area

Assessment: supported; impact: minor



Source: Section 3.3, PDF p. 5 (overlap feature).



### Source claim (paraphrase)

Paraphrase: Section 3.3, page 5, defines the overlap feature as

\[\operatorname{IoU}(B_i,B_j)=\frac{|B_i\cap B_j|}{|B_i\cup B_j|}. \]



### Analysis

Two squares of side \(1/2\), offset by \((1/4,1/4)\), have intersection area \(1/16\) and union area \(7/16\), so their IoU is \(1/7\). Their enclosing rectangle has area \(9/16\), giving the released ratio approximately \(1/9\). The enclosing-box denominator differs from the union before any small stabilizing constant is considered.



### Finding and scope

The overlap feature is not IoU on valid boxes, while a separate correct author IoU utility limits the defect to this local feature.



### Proposed correction

Use set union \(|B_i|+|B_j|-|B_i\cap B_j|\), or reuse the correct author IoU utility; define degenerate-box handling separately.

The existing local or architectural proposal remains applicable to the unchanged current-head source; no author adoption or corrected model performance is established.



## Problem 3: Semantic neighbor selection computes Euclidean rather than cosine neighborhoods

Assessment: supported; impact: minor



Source: Section 3.4, PDF p. 5; Appendix Algorithm 2, also labeled Algorithm S2 in the separate supplement.



### Source claim (paraphrase)

Section 3.4, PDF p. 5, and Appendix Algorithm 2 define semantic neighbors by cosine similarity. Released models/sem_group.py, knn, instead ranks Euclidean distances without the unit-norm restriction that would make these rankings equivalent.



### Analysis

From query \((1,0)\), candidate \((10,0.1)\) has cosine approximately \(0.99995\) but squared distance \(81.01\). Candidate \((1,1)\) has cosine approximately \(0.7071\) and squared distance \(1\). The neighbor order reverses even when self-neighbors are handled consistently.



### Finding and scope

Unnormalized Euclidean KNN can select different context from cosine similarity; no measured downstream detection effect is established.



### Proposed correction

Compute cosine scores directly, or L2-normalize nonzero query features before the Euclidean KNN call; define the zero-vector and positional-feature conventions explicitly.

The existing local or architectural proposal remains applicable to the unchanged current-head source; no author adoption or corrected model performance is established.



## Problem 4: Released neighborhood settings disagree with the paper, and a constructor argument is ignored

Assessment: supported; impact: minor



Source: Section 3.5, PDF p. 6; Table 4(b,c), PDF p. 8.



### Source claim (paraphrase)

Section 3.5, PDF p. 6, and Table 4(b,c), PDF p. 8, specify geometric and semantic group sizes \(4\) and \(2\). The released GEN construction instead calls default Geometric_Group instances whose internal TransformerBlock uses \(2\), and a default Semantic_Group using \(4\). The inspected construction path supplies no override linking those settings to the paper's chosen pair.



### Analysis

The current GEN constructs default Geometric_Group objects whose internal block is hardcoded to \(k=2\); its semantic groups default to \(k=4\). The paper’s selected counts are \(K^g=4\), \(K^s=2\). Even passing geometric \(k=4\) does not reach the internal block. The constructor likewise stores num_layers without constructing that many internal blocks; this is distinct from GEN’s external stage loop and does not establish how the paper’s depth ablation was run.



### Finding and scope

The default neighbor counts and ignored constructor arguments impair reconstruction of the stated settings; publication checkpoint configuration is not established.



### Proposed correction

Pass the requested neighbor count to the operational block and explicitly set the intended geometric/semantic counts at construction. Clarify whether depth means internal repeated blocks or external GEN stages, without inventing a new unvalidated composition.

The existing local or architectural proposal remains applicable to the unchanged current-head source; no author adoption or corrected model performance is established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
