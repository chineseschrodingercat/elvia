# Scaling Unlocks Broader Generation and Deeper Functional Understanding of Proteins



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The released all-experts eager MoE branch has a tensor-rank and routing-order defect. The protein-stability and cluster-coverage arguments require narrower interpretation; standard top-two model results were not invalidated.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: Soluble-expression measurements do not uniquely identify improved thermodynamic stability

Assessment: supported; impact: minor



Source: Section 4.2, PDF p. 9 (training stability); Section 3.1, PDF p. 6 (assay scope).



### Source claim (paraphrase)

Paraphrase: Section 4.2, p. 9, first uses ESMFold/PyRosetta analyses to evaluate predicted stability. It then measures the two lowest-perplexity generations from pretrained and stability-aligned ProGen3-46B for each of \(32\) prompts with split-GFP. The paper reports higher expression for \(8\) prompts, lower expression for \(3\), and no significant difference for \(21\), and concludes that alignment’s improvement in the stability of generated sequences is verified computationally and experimentally.

Section 3.1, p. 6, gives the necessary qualification: this assay measures soluble protein abundance and can depend on mRNA abundance/stability, translation, folding equilibrium, kinetic stability, degradation, aggregation, and toxicity. Appendix D, pp. 24–30, describes the expression assay and SDS-PAGE checks.



### Analysis

An expression readout can increase with translation or total abundance while folding free energy stays fixed. The source itself lists these confounders. Thus the final experimental stability inference is not identified by split-GFP alone; measured expression changes remain interpretable.



### Finding and scope

Supported inference-scope qualification, not a demonstrated error in the fluorescence data.



### Proposed correction

The proposed clarification recommends describing improved soluble expression and requiring direct thermodynamic measurements for a stronger stability conclusion.

A local correction or qualification is proposed where specified; author adoption is not established.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 2: The released all-experts MoE branch has both a rank mismatch and an expert-order mismatch

Assessment: supported; impact: minor



Source: Appendix B.1, Eq. (2), PDF p. 20; released moe.py eager-routing implementation.



### Source claim (paraphrase)

Appendix B.1, Eq. (2), p. 20, defines a routed weighted sum of expert outputs. The paper normally activates two of eight experts and uses Megablocks for training.

The released implementation additionally defines an eager SparseMoeBlock in src/progen3/model/moe.py. Its forward method accepts hidden states of shape \((B,S,D)\). Lines 99–105 implement the branch where the number of experts equals the number selected per token. ProGen3Config explicitly allows this configuration: it clamps the selected count to the expert count and only requires both to be positive. The problematic source occurs identically in the official conference supplement and the pinned public repository.



### Analysis

For hidden states of shape \((B,S,D)\), stacking \(E\) expert outputs yields shape \((B,S,D,E)\), but the released einsum declares only three axes for that operand. A second independent mismatch remains after flattening: top-k probabilities are in score order, whereas expert outputs are stacked in expert-index order. Those weights cannot be paired by position without restoring the index correspondence.



### Finding and scope

The explicit all-experts eager branch violates its tensor/routing contract; the paper’s standard top-two Megablocks configuration does not enter that branch.



### Proposed correction

Flatten token dimensions consistently and restore expert-index correspondence before the weighted sum. This proposal concerns the all-experts eager branch; it does not test the paper's usual top-two Megablocks configuration.

A local correction or qualification is proposed where specified; author adoption is not established.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 3: Reference-sequence perplexity does not determine total cluster generation mass

Assessment: supported; impact: minor



Source: Section 3.1, PDF p. 6 (cluster natural perplexity).



### Source claim (paraphrase)

Paraphrase: Section 3.1, p. 6, uses the average perplexity of natural proteins in clusters to assess whether additional sampling from a smaller model could recover clusters generated by a larger model. High perplexity of the reference naturals is interpreted as low probability of generating a member of that cluster, motivating an out-of-distribution interpretation.

The directly observed finite-sample cluster coverage is distinct from this inference about possible additional sampling.



### Analysis

Consider one natural reference in a cluster and one additional cluster member, with all sequences equally long. Model \(A\) assigns probabilities \((0.01,0.40)\), model \(B\) assigns \((0.02,0)\), and each assigns its remaining probability outside the cluster. The reference has lower perplexity under \(B\), but total cluster mass is \(0.02\) under \(B\) versus \(0.41\) under \(A\). Reference likelihood therefore cannot determine cluster sampling mass.



### Finding and scope

Supported qualification of the likelihood-to-coverage implication; observed generated-cluster coverage is not refuted.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
