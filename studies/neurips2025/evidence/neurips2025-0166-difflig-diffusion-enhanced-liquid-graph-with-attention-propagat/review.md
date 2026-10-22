# DiffLiG: Diffusion-enhanced Liquid Graph with Attention Propagation for Grid-to-Station Precipitation Correction



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The official implementation uses incompatible geographic coordinates, retains closed edges after softmax, has a constant consensus score, discards grid history and exceeds the reported parameter count in one submodule alone. Published forecast effects remain unmeasured.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Geographic degrees and normalized coordinates are conflated

Assessment: supported; impact: minor



Source: Section 3.4 and Algorithm 1, PDF pp.5–6; Appendix J, PDF pp.33–34; MixData.py and Haversine layer methods



### Source claim (paraphrase)

The paper defines physical Haversine distances and geographic nearest neighbors; the release feeds min–max-normalized coordinates into a degree-based Haversine formula.



### Analysis

Points \((100^\circ,30^\circ)\) and \((100.125^\circ,30^\circ)\) are about \(12.0372\) km apart with Earth radius \(6371\) km. After longitude bounds \(70\)–\(140\) and latitude bounds \(15\)–\(55\), the same formula on normalized values gives about \(0.198558\) km, reversing the predicate at threshold \(0.5\). Coordinate-Euclidean ranking also differs: from \((100^\circ,50^\circ)\), candidates \((101.4^\circ,50^\circ)\) and \((100^\circ,51^\circ)\) have coordinate distances \(1.4,1\), but Haversine distances approximately \(100.063,111.195\) km, reversing the nearest neighbor.



### Finding and scope

The physical graph operations differ from the description. Coordinate normalization for learned embeddings remains legitimate; benchmark consequences are unresolved.



### Proposed correction

Keep raw coordinates for physical distances and normalized coordinates for embeddings; rank the intended neighbors using the declared physical metric.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: Multiplying a logit by zero does not remove its edge

Assessment: supported; impact: minor



Source: Section 3.4, PDF p.5; GNN_Layer_External.message, lines 87–99; internal counterpart



### Source claim (paraphrase)

The paper multiplies normalized attention by gate and decay; the release applies softmax after multiplying the raw logits.



### Analysis

For logits \((-1,8)\), decays \((0.5,0.2)\), gates \((1,0)\), the source normalizes logits \((-0.5,0)\), yielding weights approximately \((0.377541,0.622459)\). The closed edge receives positive, larger mass, while the paper’s factorized expression has second coefficient exactly \(0\). All-closed groups become uniform. A hard threshold comparison converted to floating point also supplies no ordinary gradient to the threshold, despite its parameter declaration.



### Finding and scope

Closed edges survive aggregation and the hard threshold does not implement the described learned gate path.



### Proposed correction

Apply the declared gate/decay after normalized attention with explicit neighborhood and empty-group conventions. A masked-softmax alternative requires its own specified normalization and gate-gradient rule.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: The consensus score is constant and aggregation crosses examples

Assessment: supported; impact: minor



Source: Section 3.6, PDF pp.6–7; selector.py, forward and score reductions



### Source claim (paraphrase)

The selector is described as attention across candidates, assigning a candidate-specific consensus score.



### Analysis

Its input \((N,M,d)\) is permuted to \((M,N,d)\) for default sequence-first attention, so stations are the sequence and candidates are batches. Averaging both station dimensions of a row-stochastic attention matrix gives \(M^{-2}\sum_{u,v}A_{nuv}=1/M\) for every candidate in evaluation mode. Thus candidates \((0,1,3)\) and \((4,2,1)\) both score \(1/3\). Other selector branches remain active. Their unsegmented averaging can also make one example depend on batch mates: candidate scores \((0,2)\) give softmax \((0.119203,0.880797)\), but adding another example with \((10,-10)\) makes the pooled logits \((5,-4)\), reversing the first example’s mixture.



### Finding and scope

The claimed consensus branch cannot distinguish candidates at evaluation, and global pooling can couple separate forecast examples.



### Proposed correction

Use the intended candidate/station attention layout and a nonconstant, explicitly defined consensus reduction; segment independent example-level score aggregation.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 4: The grid branch discards every earlier timestep

Assessment: supported; impact: minor



Source: Figure 2, PDF p.4; GNN_Layer_External.forward, line 66



### Source claim (paraphrase)

The described grid encoder attends over temporal input, while its active forward path selects only the final column.



### Analysis

Two grid nodes with histories \((1,2,3,4)\), \((5,6,7,8)\) and alternatives \((1001,1002,1003,4)\), \((1005,1006,1007,8)\) both map to \((4,8)\). Holding other inputs and randomness fixed, all downstream values in this branch agree; derivatives with respect to discarded times are zero. A temporal-attention module is constructed but unused in the active path. The separate station-history encoder remains active.



### Finding and scope

The release cannot use the claimed grid temporal history. This does not mean the entire model has no temporal information.



### Proposed correction

Either implement/document the intended temporal encoder or state that only the final gridded field is used. No replacement architecture is established as restoring results.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 5: One configured submodule exceeds the reported full-model count

Assessment: supported; impact: minor



Source: Table 2, PDF p.7; DiffLiG_Launcher.py, line 31; SimpleGraphDiffusion constructor



### Source claim (paraphrase)

Table 2 reports \(49{,}361\) full-model parameters, while the launcher uses hidden width \(h=128\).



### Analysis

The active diffusion constructor contains three \(h\to h\) graph convolutions, two \(2h\to h\) convolutions, a \(2\to h\) position projection, an \(h\to h\) output projection and an \(h\to1\) auxiliary head. Their standard total is \(8h^2+10h+1=132{,}353\). Even the five graph-convolution matrix weights alone contain \(7h^2=114{,}688\), independent of bias or auxiliary-head conventions. Ensemble reuse does not multiply this count.



### Finding and scope

The released configuration cannot be the reported parameter-count configuration. The exact table-producing configuration is unknown.



### Proposed correction

Identify the actual experiment configuration/checkpoint and count its instantiated parameters; no guessed replacement full-model count is supplied.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
