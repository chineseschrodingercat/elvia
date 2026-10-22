# MultiNet: Adaptive Multi-Viewed Subgraph Convolutional Networks for Graph Classification



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The stationary-limit formula and spectral-radius argument do not establish MultiNet's central anti-collapse explanation. Explicit linear counterexamples show the failures. Other implementation, cross-validation and reporting discrepancies remain local findings; they do not establish which private runs produced the reported classifier scores.



## Scope

Claim-focused reading of the identified paper and author-released materials. The arguments below distinguish mathematical contradictions, version-specific implementation defects and unresolved empirical consequences. No author code was executed in this revision.



## Problem 1: Correct stationary limit and a graph-level counterexample

Assessment: supported; impact: major



Source: Main PDF p.4, Section 2.2, Theorem 1, Eqs 1-2 Main PDF p.5, Section 3.2



### Source claim (paraphrase)

Theorem 1 identifies the deep symmetric-normalized propagation limit with an arithmetic-mean projector and uses it to infer graph-level collapse.



### Analysis

For a connected aperiodic graph with augmented degrees \(\widetilde d_i\), the normalized adjacency power converges to \(uu^\top\), where \(u_i=\sqrt{\widetilde d_i}/\sqrt{\sum_j\widetilde d_j}\). For the self-looped three-node path, \(u=(\sqrt2,\sqrt3,\sqrt2)/\sqrt7\), which is not the uniform vector. Thus \(uu^\top\ne\mathbf1\mathbf1^\top/3\). In the paper's linear identity-weight setting, equal initial features on this path and a regular triangle need not have equal limiting mean readouts: degree factors remain. The arithmetic-mean limit and the resulting universal graph-level conclusion therefore fail.

With constant scalar initial node feature \(1\), the self-looped path has limiting mean readout \((11+4\sqrt6)/21\), while the self-looped regular triangle has limiting mean \(1\). Their equal initial feature means therefore do not imply equal limiting graph readouts under the theorem’s own linear identity-weight simplification.



### Finding and scope

The counterexample refutes the stated stationary identity and graph-level implication. It does not deny empirical oversmoothing in graph networks.



### Proposed correction

Use the degree-dependent projector and specify conditions on limiting graph readouts. Distinguish mean/sum pooling, regular/disconnected graphs, weights and nonlinearities.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: Smaller spectral radius does not establish anti-collapse

Assessment: supported; impact: major



Source: Main PDF p.7, Section 4, Eqs 11-12 and following paragraph



### Source claim (paraphrase)

Section 4 treats a reduced spectral radius as sufficient evidence against collapse.



### Analysis

Admissible equal two-view gates produce \(M=S/2\), with spectral radius \(1/2\). If \(S^L\to uu^\top\), then \(M^L=2^{-L}S^L\to0\): features collapse to zero. Relative eigenvalue ratios are unchanged by this scalar rescaling, so normalized oversmoothing is not removed either.



### Finding and scope

Reducing the absolute spectral radius does not establish the claimed anti-collapse property. Learned gates and nonlinearities need their own analysis; classifier accuracy is not determined by this linear example.



### Proposed correction

Analyze relative spectral decay under the actual recurrence. A qualified linear remedy is persistent initial-feature injection with convergent resolvent; its assumptions and effect on accuracy would still require verification.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: Evaluation-time BatchNorm and node-order dependence

Assessment: supported; impact: minor



Source: code/model.py:118-120,125,134



### Source claim (paraphrase)

The graph classifier's evaluation should respect node relabeling and its stated normalization convention.



### Analysis

Fresh BatchNorm1d uses node index as channel and remains training-mode even after parent.eval(); it is unregistered and called unconditionally once. Helper batch-change error \(2.15487\); five full-model seeds produce relabeling differences \(0.000326\)–\(0.007388\).



### Finding and scope

Symmetric full-model input yielded only \(1.19\times10^{-7}\) relabeling difference; that negative result is retained. Synthetic differences are not benchmark accuracy changes.



### Proposed correction

Use registered, appropriately masked feature normalization or per-node LayerNorm; preserve evaluation mode and node equivariance.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: Parameter registration can be lost on device transfer

Assessment: supported; impact: minor



Source: code/model.py:20-22,71-73



### Source claim (paraphrase)

The learned convolution parameters must remain registered after device placement.



### Analysis

nn.Parameter(cpu_tensor).to(device) returns an ordinary non-leaf Tensor when a device copy occurs, losing module parameter registration. Actual GraphConv has weight/bias on CPU but no named parameters on meta device.



### Finding and scope

CUDA execution was not performed. A no-op CPU conversion can conceal the issue; no inference about undisclosed historical training is made.



### Proposed correction

Create tensors on the target device before wrapping, or move the completed module. Check named_parameters, state_dict and optimizer membership; retrain after repair.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 5: Padding is treated as graph content

Assessment: supported; impact: minor



Source: code/main.py:104-126 code/model.py:134-135,173-177



### Source claim (paraphrase)

Zero padding should not become extra graph content in normalization or readout.



### Analysis

Real-node counts are not used as a mask; affine/normalization/readout operations include padded positions. Adding two zero-padded nodes to an unchanged graph changes full-model logits by 0.137769.



### Finding and scope

Synthetic counterexample establishes release sensitivity, not its effect under the authors fixed dataset padding. Corrected model accuracy is untested.



### Proposed correction

Pass real-node masks; zero padded features after transformations and exclude padding from assignments, pooling and normalization.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 6: The implemented recurrence differs from the analyzed recurrence

Assessment: supported; impact: minor



Source: Main PDF pp.5-6, Eqs 4-7 code/model.py:122-136,166-172



### Source claim (paraphrase)

The released recurrence is intended to implement the multiview propagation analyzed in the manuscript.



### Analysis

Paper specifies fixed initial assignments and separate view states propagated before final fusion. Release recomputes assignments and fuses every layer. Literal Eqs \(5\)-\(6\) also gate the first state twice, while release gates once; release adds normalization operations.



### Finding and scope

Alternative implemented architecture can be legitimate; discrepancy does not identify which private code generated tables.



### Proposed correction

Choose a canonical recurrence: preserve view states/fixed assignments as written, or revise equations and analyze layer-indexed assignments/fusion. Publish actual run configuration.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 7: Cross-validation and coverage are not reproduced by the entrypoint

Assessment: supported; impact: minor



Source: Main PDF p.8, Section 5.1 code/main.py:146-166,223-240



### Source claim (paraphrase)

The manuscript describes repeated ten-fold cross-validation for its graph-classification results.



### Analysis

Entrypoint uses fold \(0\) once rather than looping over ten repetitions of ten-fold CV. With \(188\) graphs, floor-width folds test only \(180\) indices; \(180\)-\(187\) are never tested and excluded from final-fold training.



### Finding and scope

Public reproduction path is incomplete; this does not prove the authors omitted their stated protocol in private scripts.



### Proposed correction

Use stratified complete outer folds and inner selection; preserve splits/seeds and publish \(100\) outer-fold scores plus repetition summaries.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 8: Additional concrete reproduction faults

Assessment: supported; impact: minor



Source: code/main.py:76,108-109,114-115,195-200,235-238 CLI and evaluation paths in code/main.py



### Source claim (paraphrase)

The released command-line and evaluation interfaces are intended to support the listed dataset settings.



### Analysis

Two-class head cannot accept six-class targets; two dimension arguments become strings when explicitly supplied. Final returned model is epoch \(99\) but accuracy is epoch \(90\); graph truncation uses first node indices and squeeze can scalarize singleton batches.



### Finding and scope

No benchmark rerun or corrected accuracy. Truncation is a defined release behavior requiring an explicit dataset protocol.



### Proposed correction

Derive class count, type integer arguments, return matching checkpoint/score, support dataset capacity or sparse batching, and use reshape(\(-1\)) for labels.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 9: Error bars have incompatible definitions

Assessment: supported; impact: minor



Source: Main PDF p.8, Section 5.1 and Table 1 Main PDF p.10, Table 3 Main PDF p.16, checklist item 7



### Source claim (paraphrase)

The uncertainty annotations describe the same statistic and independent evaluation unit.



### Analysis

Text describes standard deviation while captions/comparison/checklist describe standard error. Imported baseline rows may use incompatible uncertainty conventions; fold scores are not independent repetition-level measurements.



### Finding and scope

No independent significance claim is verified; the actual historical uncertainty calculation is unknown.



### Proposed correction

Publish fold/repetition scores, identify independent unit and each plus/minus quantity, and recompute consistent paired summaries.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 10: Average-rank audit

Assessment: supported; impact: minor



Source: Main PDF p.8, Table 1



### Source claim (paraphrase)

Table 1's average ranks summarize the stated within-dataset ranking convention.



### Analysis

Standard descending within-dataset ranks with average ties give DGK \(12.5714\) vs \(10.57\), RWGK \(14\) vs \(13.14\), WLSK \(8.1429\) vs 7.14. MultiNet mean rank \(16/7\simeq2.285714\) is reproduced and remains strongest under this convention.



### Finding and scope

An unstated alternative ranking convention could explain differences; classified unresolved rather than a proved historical calculation error.



### Proposed correction

Publish ranking universe, code and handling of missing entries; avoid mixing imported ranks from different tables.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 11: The directional-diversity proxy is explicitly distinguished from the formal definition

Assessment: not_issue; impact: no_issue_found



Source: Main PDF pp.3-4, Definition 1 Main PDF p.9, Eq 13 and Section 5.3



### Source claim (paraphrase)

Directional diversity is compared with the formal diversity definition.



### Analysis

Authors acknowledge cosine-distance measure does not satisfy Definition 1. Vectors \((1,0)\) and \((2,0)\) have zero cosine distance but unequal magnitude; zero vectors need a convention.



### Finding and scope

The authors acknowledge this proxy limitation. It is a scoped clarification, not a current author error or a newly established anti-collapse guarantee.



## Problem 12: Claim calibration and checklist consistency

Assessment: supported; impact: minor



Source: Main conclusion Main PDF p.8, Table 1 Limitations and existing-assets checklist items Section 5.4



### Source claim (paraphrase)

The conclusion and checklist should reflect the displayed dataset wins, assumptions and assets.



### Analysis

Table 1 has MultiNet losses on ENZYMES and DD, so universal superiority exceeds five wins out of seven. Checklist NA answers conflict with disclosed assumptions/space limitations and use of public datasets; three variants are said but four listed.



### Finding and scope

Reporting corrections do not allege license violations or independently invalidate experiments.



### Proposed correction

State five dataset wins and strong average rank; disclose limitations/assets and correct variant count.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.
