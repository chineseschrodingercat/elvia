# Diffusion on Demand: Selective Caching and Modulation for Efficient Generation



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The gate penalty can shrink along an exact function-preserving rescaling direction, so it does not alone measure modulation strength or justify hard thresholding.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Gate-only regularization does not identify modulation strength

Assessment: supported; impact: minor



Source: Section 3.3, Eq.(5), PDF p.5; Section 3.4, Eq.(7), and threshold setting, p.6



### Source claim (paraphrase)

The written relaxed objective jointly learns sigmoid gate \(\beta\in(0,1)\) and unrestricted affine parameters, using \(L(h)=h+\beta[(\alpha-1)h+\gamma]\) and a penalty \(\lambda\sum\beta\), then thresholds the gates.



### Analysis

For any \(0<t<1\), replace \(\beta\) by \(t\beta\), \(\alpha\) by \(1+(\alpha-1)/t\), and \(\gamma\) by \(\gamma/t\). Every block output is unchanged for every input, while a positive gate penalty strictly decreases. For cached scalar \(h=1\) and target \(2\), choose \(\beta_k=1/k,\alpha_k=1+k,\gamma=0\); the fit is exact and objective \(\lambda/k\to0\), but no finite admissible parameters attain zero. Thresholding at any fixed positive \(c\) eventually drops every such gate and returns output \(1\), not \(2\).



### Finding and scope

The written objective has a nonidentifiable rescaling direction and admits a nonattainment example. The paper states no universal optimizer-attainment theorem; AdamW dynamics or unreported parameter constraints could alter finite runs. No measured speedup or generation-quality claim is refuted.



### Proposed correction

Explicit bounded affine parameters on a closed gate domain make a continuous finite-sample objective attain a minimum. For retained gates, fold soft coefficients exactly using \(\alpha_{\rm deploy}=1+\beta(\alpha-1),\gamma_{\rm deploy}=\beta\gamma\); dropping gates still needs effect-based validation.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
