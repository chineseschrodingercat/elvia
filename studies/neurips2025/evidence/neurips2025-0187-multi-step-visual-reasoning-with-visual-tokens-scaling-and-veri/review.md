# Multi-step Visual Reasoning with Visual Tokens Scaling and Verification



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current stopping heuristic differs from the defined signed trajectory reward, and BLINK failure handling excludes unsuccessful executions. MathVista ablation records remain a separate unresolved configuration/results discrepancy.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: The stopping heuristic is not a signed trajectory increment

Assessment: supported; impact: minor



Source: Section 3.3–3.4, PDF p.5; verifier.py, lines 69–97; inference.py, lines 962–1005



### Source claim (paraphrase)

The paper sums observed planning/action log-probability ratios and stops when their signed increment is below a positive threshold; source uses a change norm of next-token vocabulary log-ratio vectors.



### Analysis

At observed token \(0\), scale \(1\), threshold \(0.5\), distributions \((0.2,0.8)\) versus \((0.8,0.2)\) give signed increment \(-\log4<0.5\), but vector change from zero has norm \(\sqrt2\log4>0.5\). Conversely, repeating ratio vector \((\log4,-\log4)\) across states gives norm \(0\) but a positive new token increment \(\log4>0.5\). Source slices only the final input-logit row, which predicts a future token, instead of gathering preceding rows for observed events. For three observed ratios \(9\) and an equal final distribution, the required sum is \(3\log9\), but the retained vector is zero.



### Finding and scope

Both event choice and aggregation differ. The threshold requests TerminateAction; actual loop exit depends on the returned action, and a separate ten-iteration cap remains. These examples do not satisfy every theorem premise and do not refute its abstract stopping theorem.



### Proposed correction

Teacher-force and causally align actual newly scored planning/action tokens, gather their log probabilities and sum signed ratios with an explicit mask. Exclude prompt/tool/padding/previously counted content; complete multimodal integration and threshold calibration remain unverified. Alternatively define and analyze the distinct heuristic.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: BLINK accuracy silently conditions on successful execution

Assessment: supported; impact: minor



Source: Table 1, PDF p.8; eval/BLINK/main.py, lines 95–135



### Source claim (paraphrase)

Exception cases are logged without an answer record, while accuracy divides by stored answers and labels that count dataset length.



### Analysis

For two valid planned examples, one correct response and one inference exception produce \(1/1=100\%\) from the source flow. Planned-set accuracy with failure unsuccessful is \(1/2=50\%\), and coverage is \(50\%\). The exception may concern a valid image/question; malformed labels are unnecessary. When every inference succeeds the two denominators agree.



### Finding and scope

The release reports success-conditional accuracy for failed runs. No historical failure count or corrected benchmark value is established.



### Proposed correction

Retain an explicit status for every planned ID and report coverage/failures with the predefined scoring/retry policy. Do not silently remove failed predictions from a full-benchmark denominator.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: The MathVista ablation configurations need reconciliation

Assessment: needs_evidence; impact: needs_evidence



Source: Main Table 2, PDF p.9; Appendix L/Table 10, PDF p.38



### Source claim (paraphrase)

Apparently corresponding Qwen2.5VL rows report MathVista \(52.60,66.50\) versus \(7.80,23.52\); Qwen2VL rows report \(37.50,60.30\) versus \(20.24,23.80\).



### Analysis

The V*Bench/MMStar columns match for the four rows, supporting a configuration comparison, but not proving MathVista protocols coincide. Main full-minus-counterpart gains are \(13.90,22.80\), versus appendix \(15.72,3.56\). Different splits, checkpoints, answer extraction or denominators could explain the values; neither table is automatically the correction. The BLINK accounting defect does not establish a MathVista cause.



### Finding and scope

Unresolved candidate result/protocol inconsistency; raw experiment identity is needed before a numerical error is adjudicated.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
