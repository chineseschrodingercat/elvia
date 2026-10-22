# Mozart: Modularized and Efficient MoE Training on 3.5D Wafer-Scale Chiplet Architectures



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The later arXiv version still lists insufficient capacity for one fully resident FP16 copy of the stated largest model under its six-stack configuration. This is a Minor documentation/modeling inconsistency unless another storage or offload mechanism is supplied. The separate token-copy upper bound remains valid with its original layout quantifier.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: The documented six-stack resident-weight configuration lacks capacity

Assessment: supported; impact: minor



Source: Latest arXiv v1, Sections 4.1/5.1/5.2 and Tables 1–2, PDF pp. 6–8



### Source claim (paraphrase)

The setup lists \(30.5\) billion parameters, FP16 weights and six HBM2 stacks of \(8192\) MB, with distributed resident weight storage.



### Analysis

One FP16 copy needs \(30.5\times10^9\cdot2=61\times10^9\) bytes. Even treating each listed stack as \(8192\) MiB gives only \(48\) GiB \(=51539607552\) bytes, a shortfall of \(9460392448\) bytes. Assigning all \(17\cdot100\) tiles' \(2.265\) MiB SRAM to weights still gives only about \(55.577\) GB. A smaller per-token active parameter count does not store the remaining experts; another memory/offload/compression layer could, but must be identified.



### Finding and scope

The documented resident-weight interpretation is inconsistent by capacity arithmetic. Host/offload/extra-stack traces could resolve it; the source does not establish that no such unreported mechanism exists. Simulator throughput and energy values were not independently recomputed.



### Proposed correction

Provide the actual memory hierarchy and trace. Added storage, offload or compression changes the capacity/performance model and requires explicit evaluation.

The later arXiv version, posted in March 2026, retains the six-stack FP16 configuration and the listed capacities. The current author repository README provides no additional memory hierarchy or simulator trace resolving this arithmetic.



## Problem 2: Tightness of a general upper bound depends on the layout quantifier

Assessment: not_issue; impact: no_issue_found



Source: Latest arXiv v1, token-copy upper bound and expert/attention layout in Section 4



### Source claim (paraphrase)

The token-copy quantity bounds remote all-to-all traffic, with equality requiring zero local copies.



### Analysis

With two devices, one expert each and top-\(k\) routing with \(k=2\), each token makes one local and one remote copy. The universal bound \(2\) is valid; the tight remote count for that fixed layout is \(1\). Under unrestricted per-token expert routing, the fixed-layout maximum is \(\sum_i n_i\min(k,N_e-m_i)/\sum_i n_i\). A source device holding no experts can attain the general bound.



### Finding and scope

This is a quantifier clarification, not a counterexample to the original inequality or the concrete Mozart attention-source layout. It must not be counted as a second disproved theorem.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- Local contradictions and specification differences do not establish the magnitude or direction of changes to the published benchmark scores.

- No author contact or adoption; novelty and complete historical-run provenance are unestablished.
