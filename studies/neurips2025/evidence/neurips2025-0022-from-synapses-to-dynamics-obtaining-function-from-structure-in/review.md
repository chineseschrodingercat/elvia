# From Synapses to Dynamics: Obtaining Function from Structure in a Connectome Constrained Model of the Head Direction Circuit



Preliminary assessment: Needs Evidence

Independent scientific review: pending. Author adoption: not requested.



The current final paper retains two ambiguous definitions concerning mirror symmetrization and signed velocity. Their literal forms admit counterexamples, but the implementation convention is unavailable and bidirectional trajectories provide counterevidence to an experimental failure. Needs Evidence remains appropriate.



## Scope

Latest-source comparison of the final proceedings paper, its official supplemental PDF and the current bioRxiv version history, concentrating on the two unresolved definitions. No author implementation or network simulation was executed.



## Problem 1: Mirror-symmetrization notation needs implementation evidence

Assessment: needs_evidence; impact: needs_evidence



Source: Final proceedings, Appendix A.1, p. 21, connection-group definition and both weight-symmetrization equations; Figure A1.



### Source claim (paraphrase)

Appendix A.1 divides each connection group by \(2n_{st}\), while the group key retains both source and target lateralizations. It says the resulting matrix gives identical weights to mirror-related connections while preserving overall strength.



### Analysis

Take four neurons \(a_L,a_R,b_L,b_R\), with lateralization-free labels \(a,a,b,b\), and only the two mirror-related directed connections \(a_L\to b_L\) and \(a_R\to b_R\), of weights \(2\) and \(6\). They belong to different displayed keys, \((a,b,L,L)\) and \((a,b,R,R)\), each with \(n_{ab}=1\). The printed rule therefore returns weights \(1\) and \(3\): they remain unequal and their total changes from \(8\) to \(4\). Removing only the factor \(2\) would still leave the groups separate.

This demonstrates that the literal grouping does not establish the stated invariants. It does not determine the actual preprocessing: the implementation could additionally merge mirror groups or count their multiplicities differently. The current official supplement repeats the same equations; the final paper also supplies Figure A2, a control without symmetrization using separately tuned left and right populations.



### Finding and scope

The displayed definition requires clarification. Without the actual grouping function and matrices, this remains an unresolved implementation-versus-notation concern rather than a finding that the published dynamics fail.



### Proposed correction

Clarify the actual pairing and group-count convention and provide the preprocessed matrix. No experiment-restoring correction is established.

No correction of the printed definition was found in the current final paper or official supplement; the intended implementation convention remains unresolved.



## Problem 2: The signed-speed loss may omit a direction convention

Assessment: needs_evidence; impact: needs_evidence



Source: Final proceedings, Section 4.2, pp. 5–6, signed velocity inputs and linear-consistency loss; Figure 2 and Appendix A.7, Figures A9–A10, pp. 26–27.



### Source claim (paraphrase)

The paper trains an integrator with inputs \(u\in[-U,U]\) and signed decoded angular velocity \(v=\delta\theta(t)\). Its linear-consistency loss takes the variance of \(v/|u|\) around a common mean across nonzero inputs.



### Analysis

For equally weighted nonzero inputs \(u=1,-1\), let the correct bidirectional response be \(v=u\). The two ratios \(v/|u|\) are \(1,-1\), their mean is \(0\), and the displayed mean squared deviation is \(1\). The direction-insensitive response \(v=|u|\) gives ratios \(1,1\) and loss \(0\). This is a contradiction between the literal signed-ratio definition and the stated linear-response objective.

The current paper nevertheless shows bidirectional integration and reversal of heading motion in Figure 2 and Figures A9–A10. Section 4.2 and Appendix A.7 explicitly inject velocity through opposite GLNO populations. Those observations make an omitted magnitude or direction-group convention plausible; they do not supply the actual decoder, unwrapping and loss computation.



### Finding and scope

The notation does not settle whether the implemented loss is incorrect. Bidirectional trajectories and possible separate directional averaging are retained as counterevidence; no failed experiment or invalid dynamical result is established.



### Proposed correction

Specify whether the ratio uses signed velocity, speed magnitude or separate directional groups. No new network repair or rerun is asserted.

The current final paper retains the absolute-input denominator; its implemented directional convention remains undocumented in the inspected materials.



## Limits

- Independent scientific adjudication remains pending.

- The official supplemental archive contains a PDF, without the actual symmetrization, decoding or loss implementation. Original matrices and trajectories were not available for this check.

- The examples check the printed definitions; they do not establish which convention generated the experimental figures.

- No author code, network optimization or empirical replication was executed.
