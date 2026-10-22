# PhySwin: An Efficient and Physically-Informed Foundation Model for Multispectral Earth Observation



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The spectral-objective, metric-identity and decoder descriptions need correction, and released masking/protocol details differ from the manuscript. These are local mathematical or release issues without demonstrated failure of the central foundation-model results. The strict label is Minor; stability, splits, finetuning scope and complete experiment reproduction remain unresolved.



## Scope

All seventeen original concerns, current proceedings methods/appendices and current author model/configuration/README files read. Checked the distinct spectral objectives, metric identity and reachable static branches; no training, GPU timing, author code or old verifier executed.



## Problem 1: Spectral objectives differ

Assessment: supported; impact: minor



Source: Paper pp. 4, 6; swinv2/modeling_swinv2.py; forward_loss



### Source claim (paraphrase)

The author-released implementation optimizes the printed spectral objective.



### Analysis

The current paper penalizes adjacent predicted-band differences \(\|D\widehat r\|^2\), whereas forward_loss penalizes \(\|D(\widehat r-r)\|^2\). For ten-band perfect reconstruction \(r=\widehat r=(0,1,1,\ldots,1)\), all values lie in the allowed range, yet the printed penalty is \(1\) and the released penalty is \(0\). Mean rather than sum reduction changes a positive factor, not this zero-set discrepancy. In a two-band analytic slice with squared reconstruction plus weight \(0.25\), the printed objective has optimum \((1/6,5/6)\), while the error-difference objective is zero at \((0,1)\). This slice demonstrates distinct objectives, not a full-network optimum. The current defaults also differ from the printed weights. Historical training effects remain unknown.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: Balanced macro-F1 need not equal accuracy

Assessment: supported; impact: minor



Source: Paper pp. 25



### Source claim (paraphrase)

Balanced single-label datasets have macro-F1 equal to accuracy.



### Analysis

The balanced confusion matrix \(\begin{pmatrix}100&0\\50&50\end{pmatrix}\) has accuracy \(0.75\) but macro-F1 \((0.8+2/3)/2\simeq0.733333\). Balanced classes therefore do not imply macro-F1 equals accuracy. Standard micro-F1 equals accuracy for single-label classification; the paper's EuroSAT entries need their actual aggregation specified.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: The forward path disables spectral masking

Assessment: supported; impact: minor



Source: Paper pp. 5–6



### Source claim (paraphrase)

The public forward path performs the stated spectral-group masking.



### Analysis

The helper defaults to disabled and returns original embeddings; the caller does not override it, while mask-token initialization is commented. This snapshot cannot implement the claimed active mask path; historical runs remain unknown.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: Decoder stride contradicts output dimensions

Assessment: supported; impact: minor



Source: Paper pp. 23; encoder_stride



### Source claim (paraphrase)

The appendix decoder stride reconstructs the input’s stated spatial/band dimensions.



### Analysis

Sixteen tokens, a stride-\(4\) decoder and ten bands produce \(16\cdot4^2\cdot10=2560\) values, whereas a \(128\times128\) ten-band output needs \(163840\). The author's stride-\(32\) implementation resolves this count. This is a printed architecture discrepancy, not a demonstrated source output-size failure.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 5: An unmasked shifted backbone can pass None to roll

Assessment: supported; impact: minor



Source: Swinv2Layer.forward; Swinv2Backbone.forward



### Source claim (paraphrase)

The unmasked shifted backbone accepts its optional-mask input.



### Analysis

The optional mask can be None, but inverse shifting checks only shift size before calling torch.roll on it. This is a reachable static interface issue; no full runtime was executed.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 6: Several rankings contradict the tables

Assessment: supported; impact: minor



Source: Paper pp. 8, 9–10, 24–25



### Source claim (paraphrase)

The stated rankings and equivalences match the reported tables.



### Analysis

Tiny BEN \(86.63\) is below SeCo \(87.81\) and CACo 87.00. Base MADOS \(63.06\) and PASTIS \(15.69\) rank third, not always top two. Other equivalence statements hide task-specific tradeoffs.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 7: The shown mixing study does not establish below-two-percent variation

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 9, 22



### Source claim (paraphrase)

The shown mixing ablations establish the unrestricted below-two-percent stability claim.



### Analysis

The \(50\)-to \(75\)-percent change gives SegMunich \(5.49\), OSCD \(3.37\) and EuroSAT \(2.09\) percentage-point differences. Appendix Tiny/single-dataset results and prose Base claims may be different experiments, so unshown Base stability remains unresolved.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 8: A directional cap is not energy conservation

Assessment: supported; impact: minor



Source: Paper pp. 4, 21



### Source claim (paraphrase)

The directional output cap enforces energy conservation in the claimed general sense.



### Analysis

A reciprocal BRDF equal to one inside a \(30^\circ\) polar cap and zero outside has hemispheric reflectance \(\pi/4<1\), but a directional reflectance factor \(\pi>1.2\). Thus an imposed directional cap can be a useful heuristic without being equivalent to energy conservation.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 9: Channel smoothing and wavelength-derivative energy are distinct scopes

Assessment: not_issue; impact: no_issue_found



Source: Paper pp. 4, 21



### Source claim (paraphrase)

The printed adjacent-band difference is a spectral smoothness regularizer.



### Analysis

For unequal center-wavelength gaps, a piecewise-linear approximation to integrated squared derivative is \[\int |r\prime(\lambda)|^2\,d\lambda\approx\sum_b\frac{(r_{b+1}-r_b)^2}{\lambda_{b+1}-\lambda_b}.\] The printed unweighted differences instead define a valid regularizer on channel adjacency. Section 3.1 motivates smoothness in wavelength but does not assert equality to this particular derivative integral. Band-response integration and real spectral edges further bound the physical interpretation. This distinguishes quantities without demonstrating that the chosen regularizer is invalid or empirically inferior.



### Finding and scope

The channel regularizer is mathematically legitimate. The observation limits a stronger continuous-wavelength interpretation and supplies no separate model-error finding.



## Problem 10: Epoch counts need a defined convention

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 21



### Source claim (paraphrase)

The sample, batch and update counts describe a consistent epoch convention.



### Analysis

At batch \(2048\), \(712874\) and \(549488\) samples require \(349\) and \(269\) updates per full pass, not \(695\) and 537. Mixing streams or repeated inputs could explain the factor; ordinary epoch accounting is not reconciled.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 11: Frozen-head and full finetuning scopes differ

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 6, 23



### Source claim (paraphrase)

The finetuning statements identify whether encoders or only heads are trained.



### Analysis

Main text says finetuning while Appendix Table 12 states frozen encoders. Different tables may use different protocols, requiring explicit mapping before causal comparison.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 12: Split identities are not auditable

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 6



### Source claim (paraphrase)

The description establishes appropriate pretraining/test and spatial separation.



### Analysis

Pretraining and classification share FMoW-S2/BEN sources but lack an identity intersection manifest. Overlapping SegMunich patches are safe if regions are split first; actual leakage is not established.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 13: Throughput is not universal end-to-end latency

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 9



### Source claim (paraphrase)

The throughput measurements establish the stated general latency advantage.



### Analysis

Batch-four feature-extraction ratios \(1102/76.4\simeq14.424\) and \(87.2/2=43.6\) are correct. They do not measure batch-one complete pipelines across all hardware; Tiny efficiency and Base accuracy are distinct configurations.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 14: Module gains are not monotone

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 7–9



### Source claim (paraphrase)

The full module combination maintains the component accuracy gains.



### Analysis

Three seeds are disclosed, but Full is below Physics-only on OSCD \(52.07\) versus \(52.23\), SegMunich \(43.29\) versus \(44.71\) and EuroSAT \(93.73\) versus 94.05. Paired seeds are needed to quantify significance; displayed means do not imply monotone gains.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 15: The complete experimental pipeline is unreleased

Assessment: needs_evidence; impact: needs_evidence



Source: Current author README, dataset/README.md and repository file scope; current paper Appendices A–F. The earlier six-page supplemental extract is not the current primary.



### Source claim (paraphrase)

The released materials reproduce the complete reported pipeline.



### Analysis

The author release lacks training/downstream entries, evaluation, weights and full split/PANGAEA configurations; README marks them pending. An accessible source link is not complete reproducibility.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 16: The range term is not everywhere differentiable

Assessment: supported; impact: minor



Source: Paper pp. 4



### Source claim (paraphrase)

The range penalty is everywhere differentiable.



### Analysis

The ReLU penalty has unequal one-sided derivatives at its bounds. It is piecewise differentiable and can still be optimized with subgradients.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 17: The F1 discrepancy depends on aggregation

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 8



### Source claim (paraphrase)

The displayed precision, recall and F \(1\) share one specified aggregation rule.



### Analysis

The displayed \(P=52.39\) and \(R=57.20\) give harmonic mean \(2PR/(P+R)\simeq54.69\), rather than \(54.29\). This is inconsistent if all three are from one confusion matrix, but averaging per-image/city quantities separately can explain it. No unconditional replacement value follows.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- No new author-code execution, training, empirical replication or contact.

- Historical verification outputs were inspected but not rerun.

- Missing run provenance and unresolved empirical interpretations remain explicit.
