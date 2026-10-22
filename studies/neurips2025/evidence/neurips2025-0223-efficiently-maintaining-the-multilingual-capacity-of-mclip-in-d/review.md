# Efficiently Maintaining the Multilingual Capacity of MCLIP in Downstream Cross-Modal Retrieval Tasks



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Current public losses have different multiplicative scales, so their raw levels cannot establish relative convergence speed. Default batch/sampler settings also encode different fixed budgets rather than a shared convergence criterion. Retrieval-table outcomes remain unrefuted.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: Different objective scales confound raw convergence curves

Assessment: supported; impact: minor



Source: Section 5.2, p.9, Figure 4; pcl/continual_clip/loss.py, lines 32–43; models_TaPCL.py, lines 109–121; models_CiPCL.py, lines 109–120



### Source claim (paraphrase)

The current weighted TaPCL loss has an overall factor \(0.8\); CiPCL has factor \(0.5\) after its symmetric contrastive average. Lower raw objectives need not mean better or faster-learned retrieval representations.



### Analysis

Give source, target and prompted inputs identical similarity matrix \(S=\left(\begin{smallmatrix}1&0\\0&1\end{smallmatrix}\right)\). Its common symmetric cross-entropy is \(a=\log(1+e^{-1})\approx0.3132616875\). The release returns \(0.8a\approx0.2506093500\) versus \(0.5a\approx0.1566308438\), ratio \(5/8\), despite identical retrieval scores/orderings. Positive scaling is a valid optimization choice, but also scales plotted levels and slopes. Different sampling and negative sets add further comparison limits. Historical Figure 4 plot-code lineage is not established, so its actual gap is not identified with this synthetic ratio.



### Finding and scope

The release supplies a concrete loss-scale confound for cross-method convergence inference. Recall metrics may still support effective retrieval at smaller budgets.



### Proposed correction

Report each objective under its own weights. Compare checkpoints using the same held-out retrieval measure or a fixed unscaled validation objective, and record time/examples needed to reach a shared quality threshold.

A proposed correction is described; author adoption is not established.



## Problem 2: Batch units and imposed budgets do not identify convergence

Assessment: supported; impact: minor



Source: Section 5.1, p.8; MSCOCO36_TaPCL.yaml and MSCOCO36_CiPCL.yaml; Sampler.py; both training loops



### Source claim (paraphrase)

The paper states batch size \(128\) and compares required iterations. Public defaults use TaPCL loader batch \(64\) with two separate forwards, CiPCL batch \(128\) with one; their samplers retain fractions \(0.7\) and \(1\), and loops run fixed epoch-derived lengths.



### Analysis

For \(900\) records across nine equal nonempty classes, the sampler allocations are \(630\) and \(900\) per epoch. Ten epochs with final partial batches yield \(10\lceil630/64\rceil=100\) versus \(10\lceil900/128\rceil=80\) optimizer steps. These are imposed budgets, not measured stopping times. Two forwards of \(64\) can approximately match encoder invocation count of one \(128\) forward, a valid favorable interpretation; they still use separate contrastive matrices with \(63\) rather than \(127\) off-diagonal negatives per row. Fixed budgets can reach a plateau, so absent early stopping does not prove nonconvergence.



### Finding and scope

The current defaults need explicit batch/compute accounting and a common convergence criterion before iteration counts can measure required optimization work. No corrected speedup is inferred.



### Proposed correction

Declare loader size, forwards, matrix dimensions, sampled/unique records, epochs and steps separately. For convergence speed, use a common validation threshold with sustained attainment and report wall time and examples; the proposed comparison has not been run.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.
