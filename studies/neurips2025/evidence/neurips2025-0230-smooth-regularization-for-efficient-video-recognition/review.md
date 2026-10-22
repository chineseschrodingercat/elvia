# Smooth Regularization for Efficient Video Recognition



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The documented Kinetics test subset differs from the cited MoViNet validation protocol, so unmatched score differences do not isolate model gains. An anchored relative scale theorem also does not imply unit-sphere embeddings. The loss and original appendix theorem survive the scoped checks.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: Cross-model gains require a common population

Assessment: supported; impact: minor



Source: Kinetics-600 Tables 1–2; author README, lines 146–156; official pre-paper MoViNet evaluation configuration



### Source claim (paraphrase)

Author documentation explicitly identifies still-accessible labeled test videos, while the cited baseline configuration uses validation data. Baseline values match the official model table.



### Analysis

For author set \(S_G\), baseline set \(S_B\), the reported difference decomposes as \[A_G(S_G)-A_B(S_B)=[A_G(S_G)-A_B(S_G)]+[A_B(S_G)-A_B(S_B)].\] The second term is unmeasured. A baseline scoring \(72/100\) on one set and \(78/100\) on another can appear \(6\) points behind an identical-prediction modified model tested only on the latter. This establishes non-identification, not actual video-set difficulty. An unseen matched rerun could resolve it.



### Finding and scope

Matched manifests/predictions are required. The internal attention-only versus GRW ablation may remain informative if its protocol is shared; the strongest split evidence concerns MoViNet, not automatically every row or Kinetics-400.



### Proposed correction

Evaluate all checkpoints on one frozen labeled manifest, with clip/crop and compute conventions explicit. The existing author subset clarification is credited but does not supply matched baseline results.

The authors already published the test-subset clarification. A matched baseline evaluation resolving this comparison is not established.



## Problem 2: A relative span theorem does not imply unit norm

Assessment: supported; impact: minor



Source: Affine-normalization discussion; Appendix A, anchored scalar theorem and Propositions 1–2



### Source claim (paraphrase)

The main text attributes near-unit-sphere embeddings to affine-map/GRW optimization; the appendix proves a relative anchored bound.



### Analysis

Translation by \(c\) leaves all velocities, accelerations and permuted energies unchanged, so \(L_\alpha(Z+c)=L_\alpha(Z)\). Changing affine bias realizes arbitrarily large norms with identical regularizer. This does not refute the theorem’s anchor \(z_1=0\), or analyze classifier/weight-decay interactions. The anchored scalar span proof remains valid.



### Finding and scope

Relative scale does not establish unit radius or shell concentration; empirical norm claims need their own distribution and normalization convention.



### Proposed correction

For any loss sublevel \(L_\alpha(Z)\le\log((T-1)!)\), nonnegative ordering loss and Cauchy–Schwarz give \[\|z_j-z_1\|\le\sqrt{2(T-1)\log((T-1)!)/\alpha}\]. This is relative and conditional, not a unit-sphere theorem.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.
