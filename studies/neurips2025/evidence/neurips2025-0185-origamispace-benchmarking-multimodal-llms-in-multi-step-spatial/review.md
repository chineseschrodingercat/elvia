# ORIGAMISPACE: Benchmarking Multimodal LLMs in Multi-Step Spatial Reasoning with Mathematical Constraints



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Published rates and accuracy means do not follow their ordinary stated common-population/full-set interpretations. The openly documented evaluator fallback also cannot measure physical folded-state properties. Exact denominators and the actual experiment backend remain unresolved.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: The joint pass rate violates the marginal event bound

Assessment: supported; impact: minor



Source: Table 2, Gemini2.5-pro/environmental learning, PDF p.8; caption and Sections 3.2,4.4



### Source claim (paraphrase)

Four no-error marginals are \[100\%,90.74\%,92.57\%,84.27\%\], but compilation pass rate is \(65.89\%\).



### Analysis

If these exhaust failure on one population with common weights, the union bound gives \(\Pr(\cap_i E_i)\ge\sum_i\Pr(E_i)-3=67.58\%\), at most the smallest marginal \(84.27\%\). The displayed joint rate is below the lower bound by \(1.69\) percentage points. Even allowing the first entry to mean \(99.5\%\) and generous remaining rounding gives lower bound \(67.065\%\), above \(65.895\%\). Common-weight averaging preserves the inequality; no independence is needed.



### Finding and scope

The entries cannot all have the ordinary stated event meaning. Conditional stages, unequal denominators, extra failure types, different intermediate/final populations or a transcription error remain possible and require explicit protocol clarification; no raw outputs are declared impossible.



### Proposed correction

Publish output-level flags, denominators, unavailable-test handling and final success. State conditional metrics or additional failure categories explicitly. The consistency interval is not a corrected measurement.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: Three full-run accuracies lie on an integer grid

Assessment: supported; impact: minor



Source: Table 1, PDF p.7; Section 5.3, p.8; question counts, Sections 4.1â€“4.3



### Source claim (paraphrase)

With \(N\) binary-scored questions and three complete runs, mean percentage is \(100S/(3N)\) for integer total successes \(S\).



### Analysis

MiniCPM-o pattern prediction reports \(26.99\%\) for \(N=350\). Two-decimal rounding would require \(283.3425\le S\le283.4475\), containing no integer; adjacent means round to \(26.95\%\) and \(27.05\%\). The complete author table has \(60\) of \(65\) model means incompatible with final-only rounding under the stated counts; allowing each run to be rounded first can move a mean by at most \(0.010\) percentage points, and still leaves \(54\) outside that necessary allowance. Compatible entries are retained as controls, and human rows are excluded.



### Finding and scope

The table and ordinary full-set three-run interpretation are inconsistent. Unequal subsets, partial credit or other weighting could change the grid but are not established; this does not prove fabrication or a ranking change.



### Proposed correction

Supply per-run evaluated IDs, integer numerators/denominators and the exact aggregation. Recompute from raw predictions if ordinary accuracy was intended; do not replace entries with nearest grid points.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: The documented fallback does not evaluate physical folded-state properties

Assessment: supported; impact: minor



Source: Section 4.4, PDF p.6; Appendix D.7â€“D.16, PDF pp.24â€“27; appendix/3_eval_2.tex



### Source claim (paraphrase)

The appendix openly allows planar input vertices, random angles, empty constraint lists, always-true theorem mocks and a constant layer score when backends are absent.



### Analysis

In the declared branch with both constraint lists empty, similarities are \(1\); both theorem mocks are true, hence \(\mathrm{CS}=0.3+0.3+0.2+0.2=1\) independently of geometry. Separate compiler failures or exception branches can prevent reaching this score and are not ignored. With layer score \(0.5\), \(\mathrm{FFS}=0.7e^{-5d_H}+0.15\le0.85\), including identical point sets. Normalized planar vertices cannot distinguish different folds or layer orders sharing the same crease vertices.



### Finding and scope

These documented fallbacks have limited capability. Actual experiment-time backend/configuration is unavailable, so constant CS or placeholder-based published rewards are not asserted. The warnings are disclosed rather than concealed.



### Proposed correction

Require real capability for physical metrics or mark them unavailable. Give geometry-only development scores distinct names and publish the actual backend/configuration; no restored experimental validity is claimed.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 4: The dataset step summary and appendix list use different counts

Assessment: supported; impact: minor



Source: Section 3.3, PDF p.4; Appendix A, PDF pp.12â€“14



### Source claim (paraphrase)

The main text states mean \(8.2\), range \(3\)â€“\(25\), while the appendix lists \(350\) entries in groups of \(112,146,92\).



### Analysis

Even the group-minimum bound is \((112\cdot3+146\cdot10+92\cdot20)/350=10.38857>8.2\). Aggregating listed counts gives \(5059\) total, mean \(14.4542857143\), maximum \(30\), with \(52\) entries above \(25\). A different step definition or dataset revision could explain the discrepancy.



### Finding and scope

A scoped dataset/provenance clarification is retained; no authoritative replacement definition or actual model result is inferred.



### Proposed correction

Identify the instance/step definition and dataset revision used for each summary.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 5: Euler checking requires an explicit face convention

Assessment: not_issue; impact: minor



Source: Figure 2, PDF p.5; Appendix D.1, p.23; Appendix C.2.2, p.21



### Source claim (paraphrase)

The square with one diagonal has \(4\) vertices, \(5\) edges and \(2\) bounded faces, while the appendix mentions Euler value \(2\).



### Analysis

Counting only paper faces gives \(4-5+2=1\); adding the unbounded exterior gives \(2\). Both are standard conventions. Without the actual validator it is unknown which it counts. Appendix C supplies the proper alternating-angle Kawasaki condition, so an abbreviated main-text statement is not separately inflated.



### Finding and scope

Convention clarification only, not an established rejected-input failure.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
