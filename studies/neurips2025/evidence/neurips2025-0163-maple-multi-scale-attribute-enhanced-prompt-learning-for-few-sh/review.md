# MAPLE: Multi-scale Attribute-enhanced Prompt Learning for Few-shot Whole Slide Image Classification



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The release pairs entity-major prompts with a class-major reshape and implements training/graph choices that differ from the displayed method. Exact feature witnesses establish those local differences; reported classification performance and patient splits are not invalidated.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Entity-major prompts are consumed as class-major prompts

Assessment: supported; impact: minor



Source: Eq.(7), PDF p.6; model.py, lines 58–78,479–490



### Source claim (paraphrase)

Prompt construction uses flattened index \(eC+c\), while the reshape/permutation reads \(cE+e\) for entity \(e\), class \(c\).



### Analysis

For \(E=8,C=2\), only the first and final semantic slots retain their indices, leaving \(14\) of \(16\) mismatched; \(C=3\) gives \(22\) of \(24\). With unit zero-mean vector \(u\in\mathbb R^{512}\), visual features all \(u\), class prompts \(-u,u\), and unit logit scale, proper pairing gives mean logits \((-1,1)\), probabilities approximately \((0.119203,0.880797)\). The release groups alternating prompt rows into both class columns, whose means are \((0,0)\), probabilities \((0.5,0.5)\).



### Finding and scope

The feature-space computation loses semantic pairing and can change predictions. Actual-slide embedding realizability, adaptation to old wiring and benchmark effect remain separate.



### Proposed correction

Reshape the entity-major array directly to entity, class, embedding dimensions, without the class-major reshape/permutation. This restores the index identity under the stated construction.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: Stop-gradient and zero-fusion loss change the stated objective

Assessment: supported; impact: minor



Source: Eqs.(15)–(16), PDF p.7; model.py, lines 487–488,559–568



### Source claim (paraphrase)

The paper applies cross entropy to fused entity/slide logits; the release detaches visual entity features for positive fusion weight and changes the loss at zero weight.



### Analysis

After holding semantic indexing equal, take entity logits \((-\sin\theta,\sin\theta)\), constant zero slide logits, target class \(1\), and \(\lambda=0.3\). The displayed loss derivative at \(\theta=0\) is \(-(1-\lambda)=-0.7\), while the detached path gives \(0\). Attributes and the separate slide branch can still learn. At \(\lambda=0\), half the entities with logits \((1,-1)\), half with \((-1,1)\), give fused CE \(\log2\approx0.693147\), but average individual CE \(\log(2\cosh1)\approx1.126928\). The latter may be a deliberate stronger supervision choice, but is a different objective.



### Finding and scope

The release does not differentiate the literal stated loss in those branches. Neither choice is proved inferior or a cause of the reported scores.



### Proposed correction

Either document the stop operator and separate endpoint loss, or follow ordinary fused-logit cross entropy throughout. No accuracy recovery is claimed.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: The released graph is text-fixed rather than slide-dependent

Assessment: supported; impact: minor



Source: Eq.(8), PDF p.6; Figure 2, PDF p.4; model.py, lines 102–128,495–523,572



### Source claim (paraphrase)

The equation builds neighbors from slide visual entity features, while the release saves generic-text adjacency once.



### Analysis

Take \(16\) nodes, first eight generic-text vectors \(u\), remaining eight orthogonal vector \(v\), with seven nonself neighbors plus a self-loop. Both text groups have an unambiguous similarity boundary. A slide initially matching text has the same adjacency. Swapping visual vectors of nodes \(0\) and \(8\) makes the visual-neighbor set for node \(0\) equal to \(\{0,9,\ldots,15\}\), but the release still uses \(\{0,\ldots,7\}\). Its current visual inputs set node features, not edges. Figure 2 partly supports a text-graph interpretation, so author intent is ambiguous.



### Finding and scope

The graph specification and release differ; fixed text relations may still be useful, and graph attention is present.



### Proposed correction

Specify a fixed semantic-text graph with explicit conventions, or rebuild the declared visual graph per slide. The evidence does not select the better empirical variant.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
