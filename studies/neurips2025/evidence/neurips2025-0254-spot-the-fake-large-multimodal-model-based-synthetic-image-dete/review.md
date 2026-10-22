# Spot the Fake: Large Multimodal Model-Based Synthetic Image Detection with Artifact Explanation



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Two table comparisons are incompatible with standard shared-prediction/shared-pool interpretations, and a released parser has a bounded substring failure. Aggregation and experimental impact remain unresolved.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Accuracy and F1 pairs exceed a necessary feasibility bound

Assessment: supported; impact: minor



Source: Table 2 and Section 5.2, PDF p.7



### Source claim (paraphrase)

The AIDE rows report accuracy/F1 percentages \((85.9,94.5)\) on FakeClue and \((65.6,80.2)\) on LOKI.



### Analysis

For one binary confusion matrix, accuracy \(a=(\mathrm{TP}+\mathrm{TN})/N\) and positive-class F1 satisfy \[f=\frac{2\mathrm{TP}}{2\mathrm{TP}+\mathrm{FP}+\mathrm{FN}}\leq\frac{2a}{1+a}.\] The largest F1 values at the reported accuracies are \(92.4153\%\) and \(79.2271\%\), below the reported values. Allowing every displayed number a rounding error of \(0.05\) percentage points still gives maximum compatible F1 values \(92.4443\%\) and \(79.2636\%\), below \(94.45\%\) and \(80.15\%\). The same bound holds for macro/support-weighted F1 and identical-weight run averages by concavity.



### Finding and scope

The two baseline pairs cannot describe standard accuracy and F1 from the same predictions. Different thresholds, subsets or aggregation rules remain possible omitted distinctions; no specific replacement number is determined.



### Proposed correction

Provide confusion counts, thresholds, sample identities and averaging rules, then regenerate the two metrics consistently.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Class and overall accuracies imply incompatible prevalences

Assessment: supported; impact: minor



Source: Table 3, PDF p.8



### Source claim (paraphrase)

Real, fake and overall accuracies are compared across methods on DMimage.



### Analysis

On a common pooled test set, \(O=qR+(1-q)F\), with the same real-image prevalence \(q\) for all methods. CNNSpot implies \(q=(40.6-28.4)/(87.8-28.4)\approx0.205387\); Gram-Net implies \(q=(67.4-78.8)/(62.8-78.8)=0.7125\). Independent rounding intervals of \(0.05\) percentage points give disjoint prevalence ranges \([0.203704,0.207071]\) and \([0.70625,0.71875]\). Each row can be feasible individually, but both cannot use the same pooled set and interpretation.



### Finding and scope

The common-set pooled comparison needs denominator or aggregation clarification. Different subsets, coverage, weighting or inherited baseline protocols could explain it; the source alone does not identify which.



### Proposed correction

Declare the sample denominator and aggregation unit for each method; use a common manifest and recompute the overall rate when a pooled comparison is intended.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: Substring parsing can reverse an explicit synthetic-image label

Assessment: supported; impact: minor



Source: scripts/eval.py, lines 152–167; scripts/eval_vllm.py, lines 153–168; Appendix H, PDF pp.27–34



### Source claim (paraphrase)

The release searches the first sentence for real before fake and randomly labels unrecognized responses. Prompts request a canonical label sentence.



### Analysis

The string “This is a fake image with unrealistic shadows.” contains real inside unrealistic, so the first branch predicts real despite the explicit fake label. Canonical “This is a fake image. The shadows are unrealistic.” avoids the collision because the first sentence lacks real. An unrecognized answer takes random.choice rather than an abstention path.



### Finding and scope

The parser failure is concrete for noncanonical responses with explicit labels. Its frequency in the reported outputs is unknown; perfectly canonical outputs avoid this witness. Repository issue 5 previously discussed format dependence, so novelty is not asserted.



### Proposed correction

Parse an explicit anchored label field or declared grammar, and retain unrecognized answers as abstentions with a stated denominator policy.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 4: AUC averaging and experiment identity remain ambiguous

Assessment: needs_evidence; impact: minor



Source: Tables 5–6, PDF p.9; Table 2, p.7



### Source claim (paraphrase)

Table 5 labels an AUC column Average; Tables 2 and 6 share some FakeVLM LOKI values but differ in others.



### Analysis

The FWA, Face X-ray and SRM arithmetic means of displayed subtype AUCs are \(87.925,97.050,96.175\), versus reported \(87.7,95.9,95.8\). However, pooled AUC need not equal an arithmetic mean. Likewise matching accuracy and CSS across two tables do not prove identical checkpoints, runs or protocols.



### Finding and scope

Neither an unconditional AUC arithmetic error nor a duplicated-run inconsistency is established without the aggregation definition and experiment identities.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
