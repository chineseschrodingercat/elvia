# Token Bottleneck: One Token to Remember Dynamics



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current paper specifies cosine reconstruction while the active release uses squared error. A positive-rescaling witness proves non-equivalence; checkpoint provenance and benchmark consequences remain unresolved.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: The described cosine objective differs from released squared reconstruction loss

Assessment: supported; impact: minor



Source: Section 3.3, Eq. (1); Appendix C.1; models_tobo.py, forward_loss and decoder projection; engine_tobo.py training loss



### Source claim (paraphrase)

The method describes cosine distance between predicted and target patches, while forward_loss computes coordinate-mean squared error after optional target-only normalization.



### Analysis

Let a nonzero target after optional normalization be \(u\), with predictions \(z=u\) and \(z=2u\). Both have cosine distance \(0\); their squared losses are \(0\) and \(\|u\|^2/d>0\). More generally the cosine radial derivative is \(0\), whereas the squared-loss derivative at scale \(\alpha\) is \(2(\alpha-1)\|u\|^2/d\). LayerNorm precedes the unconstrained final affine projection, so it does not impose unit norm on predicted pixels. The documented training path gives the ToBo branch nonzero weight. Appendix C.1 explicitly discloses the auxiliary Siamese loss, so that branch is not an additional undisclosed change.



### Finding and scope

The current author paper and release optimize different reconstruction objectives. Which objective generated each published checkpoint remains unresolved; downstream performance and the token-bottleneck mechanism are not refuted.



### Proposed correction

If released squared loss generated the experiments, describe the masked coordinate-mean squared error and target normalization; otherwise identify the cosine-training source and checkpoint configurations. This is a provenance-dependent proposal, not a validated retraining result.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
