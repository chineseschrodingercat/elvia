# ZPressor: Bottleneck-Aware Compression for Scalable Feed-Forward 3DGS



Preliminary assessment: No Issue Found

Independent scientific review: pending. Author adoption: not requested.



The spatial moment penalty does not provide an information bound for the full feature tensor. The paper explicitly permits an IB-inspired heuristic interpretation, which is consistent with this limitation. No error in the structural compression or rendering result is established.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Spatial moment matching is not a full-feature information bound

Assessment: not_issue; impact: no_issue_found



Source: Section 3.3, Eq. (8), PDF p. 6; Appendix A.4, PDF p. 16; author LossIB.forward, lines 36–49.



### Source claim (paraphrase)

Equation (8) writes a conditional KL for the representation; Appendix A.4 uses the weaker description IB-inspired regularization.



### Analysis

The author's LossIB.forward computes \(R=(2BN\ln2)^{-1}\sum(\mu^2+s^2-1-\ln s^2)\) from spatial moments of a feature map, with \(s^2\) including the implementation's variance stabilizer \(\epsilon\). It does not integrate the conditional law of the whole tensor.

Let \(a=(1,1,-1,-1)\), \(b=(1,-1,1,-1)\), and \(z_k=\sqrt{1-\epsilon}[\cos(2\pi k/M)a+\sin(2\pi k/M)b]\). These maps have zero spatial mean and variance \(1-\epsilon\), so the stabilized moment penalty is zero. An injective finite deterministic code of this form has \(I(X;Z)=\log_2M\) for uniform labels, whereas a constant code has the same penalty and zero information.



### Finding and scope

The moment regularizer does not bound full-tensor information without extra assumptions. The paper already permits a heuristic IB-inspired reading, which is not contradicted; no trained feature reachability or rendering failure is established.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- Local contradictions and specification differences do not establish the magnitude or direction of changes to the published benchmark scores.

- No author contact or adoption; novelty and complete historical-run provenance are unestablished.
