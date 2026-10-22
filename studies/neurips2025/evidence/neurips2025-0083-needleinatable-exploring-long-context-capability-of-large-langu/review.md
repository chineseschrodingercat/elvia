# NeedleInATable: Exploring Long-Context Capability of Large Language Models towards Long-Structured Tables



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The release has an all-occurrences coordinate bug and a ragged-table serializer boundary. Several fixed-size assets also disagree with their stored or serialized dimensions. Full experiment linkage remains unresolved.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: The location formatter repeats the row as the column

Assessment: supported; impact: minor



Source: Section 4.1, p. 8; Appendix C.4, p. 25; certain_key_all_location lines 200–221.



### Source claim (paraphrase)

The all-occurrences generator stores row/column pairs correctly but formats both output coordinates using the row component.



### Analysis

In a two-by-three table with target cells \((1,2)\) and \((2,3)\), the stored pairs are correct but the output is \((1,1),(2,2)\). Neither formatted cell need contain the target.



### Finding and scope

This generator can produce wrong answer coordinates. Its final training-data linkage is not established.



### Proposed correction

Format row from the first stored component and column from the second, preserving the structured pair until serialization.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Ragged rows can silently lose columns

Assessment: supported; impact: minor



Source: build_cell-lookup.py list_to_markdown_table, lines 310–334.



### Source claim (paraphrase)

The Markdown serializer derives column widths from a transpose before making every row equally long.



### Analysis

For rows \([H_1,H_2]\) and \([r_1,r_2,\mathrm{LOST}]\), `zip(*rows)` exposes only two columns. The resulting format has no third placeholder, so the extra cell disappears. Pre-padding and some repeated-call paths avoid this boundary.



### Finding and scope

The serializer does not preserve every cell of arbitrary ragged input. A blanket claim about all generated prompts is not warranted.



### Proposed correction

Copy and pad every row to the maximum width before deriving widths and placeholders, then serialize all columns without mutating the original table.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: Some fixed-size assets have inconsistent actual widths

Assessment: supported; impact: minor



Source: Section 3.3/Figure 4, pp. 6–7; Tables 7–8, pp. 26–27; NIAT_cropped_tables.json records 0,12,29,37.



### Source claim (paraphrase)

The public fixed-size JSON and corresponding prompts are presented as equal-dimension long-table inputs.



### Analysis

Among fifty inspected records, advertised \(28\)-by-\(28\) cases at indices \(0,12,37\) store \(28\)-by-\(32\) arrays and expose those extra columns in their prompts. Record \(29\) instead stores width \(29\) but serializes width \(28\); it is not another extra-column prompt.



### Finding and scope

The assets need a shape/provenance correction before a fixed-size analysis. The entire Figure 4 result is not numerically refuted.



### Proposed correction

Align dimension metadata, stored arrays and the actual serialized prompt for each affected asset. Use original predictions and experiment mapping before revising any aggregate metric.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
