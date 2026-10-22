# COALA: Numerically Stable and Efficient Framework for Context-Aware Low-Rank Approximation



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The introduction’s universal uniqueness claim fails at singular-value ties, and one public incremental QR helper rejects valid short initial blocks. Gap-conditioned theory and the main QR construction survive.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Positive regularization does not remove rank-cutoff ties

Assessment: supported; impact: minor



Source: Introduction, PDF p.2, first contribution bullet; Proposition 1 and Theorem 1



### Source claim (paraphrase)

The introduction claims a unique regularized rank-constrained solution for every calibration matrix \(X\).



### Analysis

For \(W=X=I_2\), rank budget \(1\) and \(\mu=1/2\), the objective is \(3\|I_2-W^\prime\|_F^2/2\). Both \(\operatorname{diag}(1,0)\) and \(\operatorname{diag}(0,1)\), and every rank-one orthogonal projector, attain global minimum \(3/2\). The discarded singular-value bound proves optimality. Positive definite weighting does not make the rank-constrained feasible set convex.



### Finding and scope

The universal introductory statement is too strong. The gap-conditioned theorem and Proposition 1’s allowance of multiple solutions are explicit countercontrols.



### Proposed correction

After the invertible rank-preserving change \(Y=W^\prime(XX^\top+\mu I)^{1/2}\), apply ordinary truncated SVD. At a nontrivial cutoff, uniqueness requires a strict gap in the weighted matrix’s singular values.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: The QR helper compares feature count with the wrong factor dimension

Assessment: supported; impact: minor



Source: Algorithm 1, PDF p.4; released lib/TSQR.py, qr_one_device, lines 38–77



### Source claim (paraphrase)

`lib/TSQR.py`, `qr_one_device`, compares a new block’s feature-row count with the intermediate reduced QR factor’s row count.



### Analysis

A full-row-rank \(4\)-by-\(5\) matrix may be split into \(4\)-by-\(2\) and \(4\)-by-\(3\) blocks. Reduced QR of the first transpose gives \(R_0\) of size \(2\)-by-\(4\). Comparing the next feature count \(4\) with its row count \(2\) rejects valid common-feature blocks. Stacking \(R_0\) with the next transpose is dimensionally valid.



### Finding and scope

The public helper rejects a valid streamed partition. A square-first-block control and a separate concatenation path can avoid it.



### Proposed correction

Compare against the factor’s column count or the saved feature count. The update then preserves \(R^\top R=\sum_iX_iX_i^\top\), including short initial blocks.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
