# Probing Neural Combinatorial Optimization Models



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Closed-tour rotation can create an impossible positive next-node label, and row-level splits can place paired representations of one routing instance in both train and test. Adjusted-significance provenance remains incomplete.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: Rotating a closed tour creates an impossible positive label

Assessment: supported; impact: minor



Source: Task 2, arXiv v1 PDF p. 4; Appendix B.1.2, pp. 15–16; data_gen.py compare_routes, lines 185–218.



### Source claim (paraphrase)

Task \(2\), PDF p. 4 and Appendix B.1.2, PDF pp. 15–16, defines a positive candidate as an optimal next-node connection. Released sample_codes/1_data_gen/data_gen.py, compare_routes, rotates closed tours to align them while retaining their repeated terminal vertex.



### Analysis

Take the simple closed tour lists \(O=(0,6,1,2,3,4,5,0)\) and \(G=(0,6,3,1,2,4,5,0)\), aligned from vertex \(4\). The source forward rotation makes \(O\) into \((4,5,0,0,6,1,2,3)\), while the greedy sequence begins \((4,5,0,6,\ldots)\). Their first reported divergence is therefore \[(\mathrm{current},\mathrm{negative},\mathrm{positive})=(0,6,0)\]. A self-edge cannot be a next unvisited choice in any Hamiltonian cycle; moreover \(\{0,6\}\) is an edge of the supplied optimal tour.

Rotating only the distinct cycle vertices instead yields the first divergence \((6,3,1)\). The defect is preservation of cycle representation, before any probe fit. The paper describes an additional constrained-optimality filter that is absent from this sample path and could protect a different historical pipeline.



### Finding and scope

The current sample generator can create an impossible supervised target, but its exposure in the original filtered probing datasets is unresolved.



### Proposed correction

Remove the repeated closure endpoint before modular rotation or reversal; validate distinct candidates and source-tour adjacency, then perform the stated forced-negative and forbidden-positive optimization checks.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 2: Held-out rows are not held-out routing instances

Assessment: supported; impact: minor



Source: Appendix B.2.1, arXiv v1 PDF p. 17; example_probing_exp.ipynb cells 7 and 15.



### Source claim (paraphrase)

Appendix B.2.1, PDF p. 17, describes training/test splits but does not require grouping by routing instance. The released probing notebook creates a positive and a negative Task \(2\) row for each instance, then splits rows rather than instance identifiers.



### Analysis

Positive and negative probe rows share one underlying routing instance and embeddings. Splitting rows independently can put one member into training and the paired member into testing. The resulting score measures held-out rows, not generalization to independent routing instances; grouping by instance is required for that interpretation.



### Finding and scope

The released split supports generalization to held-out rows, not necessarily new routing instances. The paper does not explicitly state the stronger grouping rule, and the historical score inflation is not quantified.



### Proposed correction

If the intended claim concerns unseen routing instances, assign and retain an instance_id before creating rows. Split those IDs, or use GroupShuffleSplit, and place every row and every repeated extraction from an instance in the same partition. For model comparisons, preserve the same grouped split across models and layers. Any hyperparameter selection or feature selection must remain within training groups.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 3: The released plotting cell does not identify the stated adjusted-significance analysis

Assessment: needs_evidence; impact: needs_evidence



Source: Adjusted-significance statement, PDF p. 8; released sample notebook, cell 19.



### Source claim (paraphrase)

The paper's PDF p. 8 states Benjamini–Hochberg FDR control over \(256\) dimensions; the released sample notebook's cell 19 marks raw p-values.



### Analysis

Raw thresholds do not implement BH adjustment. However, an unadjusted example cell does not prove the correction was never run elsewhere. The complete p-value family, correction operation and adjusted output are needed to verify the reported adjusted decisions.



### Finding and scope

Evidence gap concerning historical adjusted-significance provenance; no substitute significance verdict is supplied.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
