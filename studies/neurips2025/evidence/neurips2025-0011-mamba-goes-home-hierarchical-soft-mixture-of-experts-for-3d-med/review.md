# Mamba Goes HoME: Hierarchical Soft Mixture-of-Experts for 3D Medical Image Segmentation



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The released global dynamic-slot layer creates a quadratic routing tensor, contradicting the central linear-scaling explanation. This determines Major. Reported macro-averages, repeated table values and local specification/resource issues require reconciliation, but their effects on central empirical superiority have not been demonstrated.



## Scope

Full original concern list, current arXiv revision including methods and implicated appendices/tables, and current pinned author routing/model source inspected read-only. Shape counts and explicit table arithmetic are direct checks; no author program or model was executed.



## Problem 1: Global dynamic slots require quadratic routing

Assessment: supported; impact: major



Source: Current paper, Section 2.4, p. 6; author release src/models/soft_moe/soft_moe_with_dynamic_slots.py, lines 99–129 and 235–244.



### Source claim (paraphrase)

The dynamic hierarchy has linear routing complexity.



### Analysis

Let \(N\) be the input length, \(K\) the fixed group size, and \(E_1,S,E_2\) fixed expert/slot counts. The author implementation concatenates first-level slots into length \(L=\lceil N/K\rceil E_1S\). The next dynamic-slot layer pads to \(L'=E_2\lceil L/E_2\rceil\) and explicitly creates logits of shape \(B\times L'\times E_2\times(L'/E_2)\).

That tensor has \(B(L')^2\) entries, and its dot products cost \(\Theta(B(L')^2d)\). Thus global routing is quadratic in \(N\) at fixed grouping/width constants, despite constant-factor compression. For the stated first-stage settings, doubling \(N\) from \(110592\) to \(221184\) doubles global length from \(864\) to \(1728\), and multiplies logits entries from \(746496\) to \(2985984\). These are shape counts, not total GPU-memory measurements.



### Finding and scope

The strict linear-scaling explanation does not describe the author-released global routing. Small-input speed or memory benefits can still be real.



### Proposed correction

Report the full grouped/global complexity. Fixed global slot count \(Q\) would give \(O(BLQd)\) routing, but that changes the architecture and would need new training.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: The two-stage algorithm differs from the execution graph

Assessment: supported; impact: minor



Source: Paper pp. 4–5, 3



### Source claim (paraphrase)

The published two-stage equations describe the released execution graph.



### Analysis

The current paper uses learned slot embeddings and a group softmax router, whereas HierarchicalDynamicSlotsSoftMoE.forward generates embeddings from group means, uses learned scalar expert gates and a sigmoid group gate, and applies DynamicSlotsSoftMoE to all concatenated group slots. Under a pointwise interpretation of the printed FFNs, reshape followed by channel FFNs cannot create cross-group dependence: \(\partial y_g/\partial x_h=0\) for distinct groups. A matrix-valued FFN could instead mix tokens, so this is a conditional illustration of incomplete specification, not proof that every interpretation is local. The actual source performs global dispatch and has the quadratic routing counted above; the Mamba branch also supplies long-range dependence.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: Padding and mask boundary cases are incomplete

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 4



### Source claim (paraphrase)

The padding and attention-mask definitions cover valid boundary inputs.



### Analysis

An all-negative-infinity softmax row has no defined probability. The retained mask branch also admits padding contamination and an edge case in marking padded dynamic slots. Whether benchmark batches triggered these cases is unknown.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: Slot ablation does not keep parameters and memory fixed

Assessment: supported; impact: minor



Source: Paper pp. 9, 24



### Source claim (paraphrase)

Changing slot count holds parameters and memory fixed.



### Analysis

The current slot projection is a bias-free linear map from \(d\) to \(dE_1S\), containing \(d^2E_1S\) weights. With the four stated stage widths and expert counts and two repetitions per stage, these projections alone contain \(5769216S\) weights. Changing \(S=4\) to \(S=8\) therefore adds \(23076864\) parameters. The global routing length is also proportional to \(S\), so its array scales quadratically with \(S\). This contradicts the current p. 9 statement that the slot variations keep parameters and GPU memory constant; it does not replace a measured peak-memory comparison.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 5: Macro-average summaries conflict with their definition

Assessment: supported; impact: minor



Source: Paper pp. 19, 6, 30–31



### Source claim (paraphrase)

mDSC and mHD95 use the stated macro-average formulas.



### Analysis

Equation (19) explicitly gives equal weight to classes. In current Table 12, Hermes lists \[79.3,74.2,90.7,87.6,87.1,88.8,84.7\]; their mean is \(84.6286\%\), while the displayed mDSC is \(86.5\%\). Entry rounding cannot explain the \(1.8714\)-point difference. In Table 22, the seven foreground means for \(S=4\) and \(S=8\) are \(85.7714\%\) and \(85.9429\%\), while their displayed aggregates \(87.5\%\) and \(87.4\%\) reverse this order. An unreported background class could explain some FeTA values, but is not established. Different case/class aggregation or empty-mask handling requires a stated alternative definition; unrounded case outputs are needed to select final numbers.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 6: Main and appendix results conflict

Assessment: supported; impact: minor



Source: Paper pp. 7, 8–9, 21, 31



### Source claim (paraphrase)

Identically named experiments agree across main text and appendix, and the method is universally best.



### Analysis

Current Table 3 gives SegMamba FeTA mDSC/mHD95 as \(85.9/3.5\), whereas Table 12 gives \(86.5/5.8\). For CT-to-MRI transfer, Table 2 gives SegMamba mDSC \(84.4\), while Table 25 gives \(79.0\). They are not identified as different runs. The universal DSC-and-HD95 superiority statement on p. 9 also has a counterexample: AMOS-CT Hermes HD95 is \(11.3\) mm, below pre-trained Mamba-HoME at \(12.2\) mm. These internal comparisons preserve its other wins and do not determine which conflicting result is correct.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 7: Dataset accounting lacks a reconciled manifest

Assessment: supported; impact: minor



Source: Paper pp. 16, 17–18



### Source claim (paraphrase)

The described inclusion and deduplication rules determine the reported dataset counts.



### Analysis

Current Appendix A.1 subtracts \(194+43+200\) scans from \(9262\), giving \(8825\); Table 9 reports \(8788\), consistent instead with the footnote using \(80\) NIH scans. PANORAMA totals imply \(2238-1964=274\) earlier scans, whereas Table 9 lists \(334\) test scans and separately lists another \(60\) in-house cases. MVSeg is listed as \(110\) training scans in Table 9 but as \(105/30/40\) train/validation/test scans in Appendix B.2. These are accounting/version discrepancies, not demonstrated patient leakage.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 8: The parameter formula counts nonzero entries

Assessment: supported; impact: minor



Source: Paper pp. 20



### Source claim (paraphrase)

Eq.26 defines trainable parameter count.



### Analysis

An \(\ell_0\) expression counts nonzero values. A trainable scalar remains a parameter when its current value is zero, so Eq. (\(26\)) is not a general parameter-count definition.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 9: Patient-level statistics lack operational detail

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 8, 19–20, 35



### Source claim (paraphrase)

The stated tests establish patient-level significance and detection performance.



### Analysis

Wilcoxon claims and patient-detection formulas lack case values, pairing units, thresholds and full outcomes. Significance and patient-level generalization cannot be reconstructed from these aggregates.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 10: Decoder and resource descriptions leave limited reproducibility gaps

Assessment: needs_evidence; impact: needs_evidence



Source: Current paper, Eq. (17) and final prediction description, p. 6; DyT Table 8, p. 9; timing definition, Eq. (27), p. 20; author release src/models/MambaHoME.py.



### Source claim (paraphrase)

The decoder restores full resolution and the resource summaries describe the implemented measurements.



### Analysis

The printed \(I-1\) decoder stages start from a downsampled stem; the final prediction description leaves the final restoration operation implicit. The author model includes additional decoding, so no wrong output size is established. Table 8 gives default DyT FeTA mDSC \(87.4\), versus \(87.5\) in other default tables; different runs or rounding may account for this small difference. Hardware and timing definitions are supplied, but complete run-specific volumes, synchronization and memory-reset details are not linked to every result. The coarse displayed speed ratios alone do not refute the approximate prose percentage.



### Finding and scope

These are unresolved specification/run-provenance limits. The current code includes final decoding; no decoder-size failure or false measured speedup is established.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- No new author-code execution, training, empirical replication or contact.

- Historical verification outputs were inspected but not rerun.

- Missing run provenance and unresolved empirical interpretations remain explicit.
