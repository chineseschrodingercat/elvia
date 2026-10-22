# Longer Context, Deeper Thinking: Uncovering the Role of Long-Context Ability in Reasoning



Preliminary assessment: Needs Evidence

Independent scientific review: pending. Author adoption: not requested.



The claimed primary explanation of shorter outputs depends on an unspecified aggregation convention. Pooled arithmetic conflicts with that explanation, but macro-averaging remains a viable alternative; the empirical table is not adjudicated.



## Scope

Rapid, claim-focused reading of the latest applicable author-paper and resource passages. Direct mathematical or static-source reasoning is stated below. No author program, retained verifier, model inference or benchmark was executed.



## Problem 1: The output-length explanation needs a common aggregation convention

Assessment: needs_evidence; impact: needs_evidence



Source: Latest arXiv v 2, Appendix C, Table 11 and following paragraph, PDF p.24



### Source claim (paraphrase)

The paragraph attributes shorter generations primarily to a larger proportion of correct responses, which tend to be shorter.



### Analysis

Under response-level pooling, let \(p\) be the correct fraction and \(c,w\) the conditional mean lengths. Then \(m=pc+(1-p)w\). The exact symmetric composition contribution between settings is \[C=\tfrac12(p_1-p_0)[(c_0-w_0)+(c_1-w_1)].\] For short supervision, the table gives \(p_0=1267/2500\), \(p_1=1360/2500\), \((c_0,w_0)=(3189,23145)\) and \((c_1,w_1)=(3906,14921)\). The reconstructed change is \(-4102.4592\) tokens, of which composition contributes \(-576.0606\), about \(14.04\%\). For long supervision the corresponding amounts are \(-2059.2932\) and \(-709.3710\), about \(34.45\%\). Changes within outcome groups account for more under this convention.

The reconstructed row means are \[13031.2992,8928.84,12119.1668,10059.8736\], while the printed overall means are \(12991,8782,11187,9335\). Ordinary rounding cannot explain these differences. However, conditional means averaged equally over questions need not have the same weights as pooled correct/incorrect counts. That alternative can break the displayed pooling identity without making the measurements erroneous. The aggregate table does not identify the convention or the causal mechanism.



### Finding and scope

The principal-composition explanation is unsupported by the pooled interpretation, but the actual weighting/cohort remains unresolved. Response-level records or an explicit aggregation definition are needed before declaring an erroneous empirical table. The reported reasoning accuracies are not refuted.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- Mathematical counterexamples and source discrepancies do not remeasure published experiments; historical execution results were not rerun.
