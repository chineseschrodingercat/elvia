# The Future Unmarked: Watermark Removal in AI-Generated Images via Next-Frame Prediction



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Independent horizontal and vertical searches need not maximize the combined latent-distance surrogate. A separate exact score example shows why a low detection rate at one operating point does not establish statistical indistinguishability. Neither finding remeasures the reported image attack.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Independent axis maxima can cancel in the combined warp

Assessment: supported; impact: minor



Source: Section 3.2, Eqs.(1)–(2), PDF p.5; utils.py, max_warp_latents



### Source claim (paraphrase)

The displayed target maximizes joint latent distance. The release maximizes \(L(d_x,0)\) and \(L(0,d_y)\) separately and combines their offsets.



### Analysis

For the accepted four-channel \(64\times64\) latent \(z_{c,i,j}=(-1)^{i+j}\), the released \(512\)-pixel flow grid induces latent source coordinate \(j+d_x/8-1/16\), with nearest-neighbor reflection. Offset \(-27\) flips parity at \(61\) of \(64\) positions per axis. Hence \(L(-27,0)=L(0,-27)=1.90625\), but the selected combination gives \[L(-27,-27)=4(61/64)(3/64)=0.1787109375.\] Offset \(20\) flips only \(2\) positions, so \[L(-27,20)=2\{(61\cdot62+3\cdot2)/4096\}=1.849609375.\] Both pairs lie within the source’s own candidate product and \([-40,40]^2\).



### Finding and scope

The accepted-input heuristic need not solve the joint surrogate objective. Reachability of this checkerboard by natural-image inversion, and any resulting attack-quality effect, remain unestablished.



### Proposed correction

Joint finite enumeration returns a maximizer over its declared candidate product. It does not solve unrestricted continuous flow optimization or prove better watermark removal.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: One low-FPR operating point does not imply indistinguishability

Assessment: supported; impact: minor



Source: Section 4.1, PDF p.7; Section 4.2 RQ1, Table 1 and Figure 3, PDF p.8



### Source claim (paraphrase)

The discussion infers indistinguishability from shifted detector distances and low \(\mathrm{TPR}\) at \(1\%\) false-positive rate.



### Analysis

Let lower distance indicate a watermark. Take negative scores \(0,1,\ldots,99\) and positive scores consisting of seven copies of \(-0.5\) and ninety-three copies of \(7.5\). Threshold \(0.5\) gives \(\mathrm{FPR}=0.01\) and \(\mathrm{TPR}=0.07\). Yet the pairwise AUC is \[(7\cdot100+93\cdot92)/10000=0.9256.\] These are explicitly constructed scores, not the paper’s unpublished image scores. Repository issue 2, opened by XiaoxiKong on 27 December 2025, independently raised the high-AUC concern; its empirical measurements were not reproduced here.



### Finding and scope

The operating-point result remains meaningful, but does not establish equality of score distributions or absence of all watermark information.



### Proposed correction

State that the evaluated detector’s sensitivity falls at the threshold calibrated to \(1\%\) false-positive rate; retain the distinction from distributional indistinguishability.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: Distributional image-quality scores do not certify each image

Assessment: not_issue; impact: minor



Source: Image-quality evaluation, PDF pp.8–9 and Appendix quality tables



### Source claim (paraphrase)

FID and aggregate CLIP scores assess distributional quality and prompt alignment.



### Analysis

Permuting generated images within a prompt-compatible collection preserves distributional FID and aggregate semantic scores while changing which source image receives which output. Thus those summaries alone cannot certify instance-wise preservation. The paper’s reported scores themselves are not contradicted.



### Finding and scope

This is a metric-scope clarification; no separate image-level defect is established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
