# Mint: A Simple Test-Time Adaptation of Vision-Language Models against Common Corruptions



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The class-gradient formula omits the severity-squared factor from the normalization denominator. An exact finite-support population satisfies both printed covariance conditions but reverses the promised derivative sign; the automatically differentiated implementation and reported accuracy are not thereby refuted.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: The printed covariance conditions permit a negative class gradient

Assessment: supported; impact: major



Source: Theorem 3.2, Eqs.(3)–(5), PDF p.5; Appendix B.4, PDF pp.26–27



### Source claim (paraphrase)

The theorem gives nonnegative class-weight gradient when \(\sigma^2\ge\|b\|^2/(4d_{\rm irr})\) and \(\sigma^2\ge\|c\|^2/(4d_{\rm noise})\), where \(c=\operatorname{Cov}(v^{\rm noise},\hat y)\) already includes noise severity.



### Analysis

Let \(Y,R_0,R_1,R_2,R_3\) be independent uniform signs, \(y=(Y+1)/2\), \[v=(Y,R_0,0,R_1/2,R_2/2,R_3/2)\], \(\mu=1\), \(s=1/2\), and all weights \(1\). Use opposite unit text embeddings in direction \((11/10,0,0,8,4,2)\). Then \(\hat y=\mathbf1\{(11/10)Y+4R_1+2R_2+R_3>0\}\), with strict margin \(0.1\). All \(32\) atoms have norm squared \(11/4\). Their exact moments are \(p=1/2\), \(C=8\), \(\sigma=1/16\), \(b=0\), and \(c=(3/16,1/16,1/16)\). Both printed conditions hold because \(1/256\ge11/3072\). Varying only the class weight \(x\), the retained variance identity gives \[V(x)=\frac{4x^2+11}{64x^2+112},\qquad V^{\prime}(1)=-\frac2{121}.\] The printed derivative instead gives \(5/242>0\).



### Finding and scope

The sign conclusion fails under the stated model. At \(s=1\) the missing factor disappears, and for \(s\ge1\) the printed condition can still suffice. The paper does not impose that restriction on its latent severity. A full update’s accuracy and the autodifferentiated release objective are separate questions.



### Proposed correction

The noise bracket must be \(4\sigma^2s^2d_{\rm noise}-\|c\|^2\), giving sufficient condition \(\sigma^2\ge\|c\|^2/(4s^2d_{\rm noise})\) for positive severity/dimension. Quotient differentiation also gives shift derivative \(-2V(\mathbf1)s^2\delta^2/D_0\); its nonpositive sign survives the coefficient correction. Zero severity or absent components need separate omission rather than division by zero.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
