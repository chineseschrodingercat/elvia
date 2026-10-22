# Role Bias in Diffusion Models: Diagnosing and Mitigating through Intermediate Decomposition



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Single-component flags in the later SDXL release mask logs but retain both optimized losses. Its role-difference score supports relative preference rather than absolute alignment, and a finite intermediate limit causes inconsistent dictionary access. Original ablation correspondence remains unresolved.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: Single-component flags do not mask the optimized supervised loss

Assessment: supported; impact: minor



Source: Section 3.3, Eq.(3), PDF p.5; Table 3, p.9; rebind/scripts/sdxl/rebind_lora_sdxl.py, lines 1489–1507



### Source claim (paraphrase)

In the ordinary no-SNR branch, active/passive selection flags zero the corresponding logging variables but do not affect the weighted loss returned for optimization.



### Analysis

Use one active and one passive residual \(r_A=1\), \(r_P=3\), with weights \(5\) and \(1\). The returned mean is \((5+9)/2=7\) under active-only, passive-only and combined flags. The derivative with respect to the allegedly disabled passive residual is \(r_P=3\), whereas a genuine active-only loss has derivative zero. Both source groups are loaded; the combined method itself legitimately uses both.



### Finding and scope

The advertised public flag cannot by itself reproduce a single-component ablation. The code revision or external data selection used for Table 3 is not established.



### Proposed correction

Apply component masks to the optimized loss itself, for example \(A\lambda n_A^{-1}\sum r_{A,i}^2+P n_P^{-1}\sum r_{P,i}^2\), omitting disabled terms and their loader requirements. Log the same included terms.

A proposed correction is described; author adoption is not established.



## Problem 2: Relative role preference is not an absolute alignment threshold

Assessment: supported; impact: minor



Source: Section 4, Bias paragraph, PDF p.6; Table 3 and interpretation, p.9; load_triplet_data, lines 859–928



### Source claim (paraphrase)

The paper defines \(\beta=U-M\) and interprets \(\beta\le0\) as an unbiased, well-aligned image. The public pruning path tests relative ordering and does not use its absolute-threshold argument.



### Analysis

The criterion is exactly \(M\ge U\), satisfied by \((M,U)=(0.01,0)\) or \((0,0)\); it gives no positive lower bound on matching score. At combined weight \(1\), Table 3 gives matching/reversed scores \(63.4,75.5\); at weight \(5\), they are \(57.9,65.8\). The reported direction score improves by \(4.1\) percentage points while matching score falls by \(5.5\). Thus reduced reverse preference is supported, but the stated absolute-matching interpretation does not follow from that statistic. The public filter retains zero and low-score ties because only the sign of \(M-U\) is tested.



### Finding and scope

The relative statistic remains useful within its definition. No real image is assigned the synthetic scores, and human or fine-grained evaluation evidence is not rejected.



### Proposed correction

Describe \(\beta\le0\) as intended-over-reversed score ordering and report both scores. If absolute quality is intended, separately calibrate an explicit condition such as \(M\ge\tau\) together with \(M-U\ge\delta\); no numerical threshold is validated here.

A proposed correction is described; author adoption is not established.



## Problem 3: A finite intermediate limit is applied inconsistently across two passes

Assessment: supported; impact: minor



Source: create_intermediate_dpo_dataset, rebind/scripts/sdxl/rebind_lora_sdxl.py, lines 1017–1027 and 1083–1094



### Source claim (paraphrase)

The first pass slices each relation-type list to the requested finite limit, but the construction pass iterates through the unsliced list and indexes the partially populated dictionary.



### Analysis

With active relations \((a_1,a_2)\), passive relations \((p_1,p_2)\) and limit \(1\), loading creates only the first relation of each type and its reverse. Construction nevertheless reaches \(a_2\) and accesses its absent dictionary entry. The full-selection default loads all those keys and is a passing control; an image-count ablation is a different parameter.



### Finding and scope

The nondefault finite-relation configuration has a direct missing-key path. This does not show that a default experiment crashed or that Table 10’s image-count experiment is invalid.



### Proposed correction

Compute the selected relation lists once and reuse them during loading and construction. This prevents requests for unselected relation keys, without guaranteeing that all unrelated dataset errors are resolved.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.

- The February 2026 public SDXL snapshot postdates the conference; correspondence to original generating runs is unestablished.
