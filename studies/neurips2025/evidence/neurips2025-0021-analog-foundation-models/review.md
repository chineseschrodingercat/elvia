# Analog Foundation Models



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The author-released PCM evaluator and training-conversion path differ from the manuscript specification. These are local release/provenance issues without demonstrated damage to the central reported hardware results. The strict label is Minor; clipping attribution and historical table configuration remain unresolved.



## Scope

Full original three-concern report and fresh proceedings E.1/Table13/clipping discussion checked; six current pinned author files read and compared. Historical probes were not rerun; direct distribution/dataflow and missing-control arguments suffice for the bounded findings.



## Problem 1: PCM evaluation uses a different stochastic law

Assessment: supported; impact: minor



Source: Appendix E.1, p.26; apply_noise_model.py: add_PCM_noise.



### Source claim (paraphrase)

Appendix E.1 describes zero-mean Gaussian error with one cubic standard-deviation polynomial.



### Analysis

Current Appendix E.1 specifies \(\widehat W=W+\eta\), with zero-mean Gaussian \(\eta\) and one cubic standard-deviation rule. The current add_PCM_noise rescales conductance, forces output zero when \(|g|<0.6\), uses one polynomial up to \(52.5\), and another above it. A legal row with maximum absolute weight \(1\) and a nonzero entry \(0.3/180\) has normalized conductance just below \(0.3\), so that entry is deterministically set to zero: its error has nonzero mean and zero variance. Unit conversion and coefficient rounding cannot make this a zero-mean Gaussian. The high-conductance branch does approximately match the printed polynomial; the discrepancy is localized, and no historical benchmark effect is measured.



### Finding and scope

The stated local claim or source contract fails as described. Its effect on historical experiment scores is unmeasured.



### Proposed correction

Specify the piecewise evaluation law, normalization and threshold, and bind the reported hardware results to the exact author version used.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: The clipping contribution is confounded

Assessment: needs_evidence; impact: needs_evidence



Source: Current paper, Appendix C.3 and Table 13, p. 24; clipping interpretation, p. 6 and Appendix D.1, p. 25.



### Source claim (paraphrase)

The comparison interprets Table 13 as clipping contributing more than training noise.



### Analysis

Table 13 gives printed noisy-evaluation averages \(62.92\), \(65.44\) and \(65.96\). The first change adds a complete adaptation/training and quantization pipeline including clipping; the second adds training noise within that already adapted pipeline. If \(A(B,C,N)\) denotes the score with non-clipping adaptation \(B\), clipping \(C\), and noise \(N\), the table supplies \(A(0,0,0)\), \(A(1,1,0)\) and \(A(1,1,1)\), but omits \(A(1,0,0)\). Consequently the isolated clipping effect \(A(1,1,0)-A(1,0,0)\) may be larger, smaller or negative while retaining all three observations. The \(2.52\)-point composite gain and \(0.52\)-point conditional-noise gain do not identify that comparison. The SNR/quantization mechanisms remain compatible with clipping helping in practice.



### Finding and scope

This remains a bounded scope or unresolved-source concern; broader experimental invalidity is not established.



### Proposed correction

Narrow attribution to the compared composite settings or provide matched component ablations.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: The displayed training entry does not convert analog layers

Assessment: supported; impact: minor



Source: Current author src/analog_foundation_models/train.py, model construction and Trainer call; utils/train_utils.py, clipping hook; utils/aihwkit_utils.py; example.py inference conversion.



### Source claim (paraphrase)

The public training pipeline is intended to implement hardware-aware analog training.



### Analysis

The current training entry loads an ordinary AutoModelForCausalLM from the standard base model and passes it to CustomTrainer without analog-layer conversion or use of create_rpu_config. The Trainer clips only if the model exposes analog_layers; its shown path does not create those layers. The inference example separately performs conversion, which does not retroactively change the training path. This establishes a public-entry gap rather than proving the final paper’s internal training used no analog operators; the pinned public head predates the final manuscript.



### Finding and scope

The stated local claim or source contract fails as described. Its effect on historical experiment scores is unmeasured.



### Proposed correction

Provide the intended analog-layer conversion and run configuration in the training entry; no restored full-model training result is asserted.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- No new author-code execution, model spending, training, author contact or complete benchmark replication.

- Historical numerical results are retained evidence rather than current reruns.

- Local counterexamples do not invalidate every empirical result; missing historical run attribution remains unresolved.
