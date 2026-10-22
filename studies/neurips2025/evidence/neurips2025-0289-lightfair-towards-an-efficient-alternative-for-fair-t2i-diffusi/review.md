# LightFair: Towards an Efficient Alternative for Fair T2I Diffusion via Debiasing Pre-trained Text Encoders



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Generator-kernel calibration is an explicit applicability premise. Centroid normalization, foreground-image specification and universal spectral semantics need local corrections; the reported fairness outcomes were not reproduced.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: The odds theorem is conditional on generator-kernel calibration

Assessment: not_issue; impact: minor



Source: Theorem 4.1, Eq. (8); Appendix D.1–D.5



### Source claim (paraphrase)

Equal distances imply equal Gaussian neighbor probabilities; the proof identifies that kernel with actual diffusion attribute probabilities.



### Analysis

Take \(z_1=(1,0),z_2=(-1,0),u=(0,1),\rho=1\). Equal squared distances \(2\) give kernel probabilities \((1/2,1/2)\). A separate generator can obey every attribute-specific prompt perfectly but generate attributes \((.9,.1)\) from the neutral prompt. A constant concept gives attribute–concept independence. This does not contradict a theorem that explicitly assumes the actual generator is the calibrated Gaussian kernel; it shows that neighbor selection and prompt compliance do not derive that premise.



### Finding and scope

Under the intended calibrated idealization the exponential-distance algebra is valid. Its application to learned diffusion remains a modeling assumption requiring qualification.



## Problem 2: Normalized centroid cosine changes the intended mean score

Assessment: supported; impact: minor



Source: Section 4.2.1, Eqs. (9)–(10); Algorithm 1



### Source claim (paraphrase)

The losses replace mean image cosine scores by cosine to an average image embedding, dropping the centroid norm.



### Analysis

For unit text \(u=(1,0)\), let attribute embeddings be \((.8,\pm.6)\) and \((.2,\pm\sqrt{.96})\), each equiprobable. Centroids \((.8,0)\) and \((.2,0)\) both have cosine \(1\), but squared distances to \(u\) are \(.04\) and \(.64\), giving calibrated odds \((.5744425,.4255575)\) at unit bandwidth. Generally \(E\cos(t,X)=t^T\mu\), whereas \(\cos(t,\mu)=t^T\mu/\|\mu\|\). Attribute-specific rotations preserve the example and give mean-score spread \(.3\) while centroid-cosine spread is zero. Algorithm 1’s raw dot product is valid counterevidence: actual implementation convention is unavailable.



### Finding and scope

The displayed cosine loss differs from the intended mean-score/unnormalized-distance target. This does not show the unreleased experiments used the wrong convention.



### Proposed correction

Use raw centroid dot products for mean cosine. For distance-based odds, retain actual squared distances or explicitly redefine normalized representatives and calibrated model.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: The embedding attention formula does not specify a foreground image

Assessment: supported; impact: minor



Source: Section 4.2.2, Eq. (13); Algorithm 1



### Source claim (paraphrase)

Attention over image/text embeddings is described as a highlighted image fed back to the image encoder.



### Analysis

With one pooled image query and one pooled text key/value, the score has one entry, so softmax is \([1]\) and the output is the text value regardless of the image. Its shape is an embedding, not RGB pixels or a spatial mask. With token matrices, the output is a mixture of text values per image token; patch-grid selection, mask aggregation, normalization and upsampling are still needed. A hidden routine could supply them; visual examples do not uniquely define it.



### Finding and scope

The published operator is insufficient to reproduce the foreground module. Actual generated foreground images are not proved independent of input.



## Problem 4: Spectral ordering needs a decreasing-power premise

Assessment: supported; impact: minor



Source: Proposition 4.2; Appendix E



### Source claim (paraphrase)

The proposition states a universal low-frequency recovery advantage and assigns attributes to late high-frequency recovery.



### Analysis

The derived SNR increment is \(\Delta_i(f)=K_iS(f)\), with \(K_i>0\). It decreases in frequency only if signal power does. A positive \(16\)-pixel signal \(x_j=3+\cos(2\pi j/16)/2+2\cos(8\pi j/16)\) has unitary powers \(S(1)=1,S(4)=16\). With cumulative noise values \(.1,.4,.2\) and unit expected noise power, increments are \(1/24\) and \(2/3\), reversing the unrestricted ordering. Dividing pixels by \(6\) fits \([0,1]\) without changing the ratio. A decreasing power-law model gives the claimed conditional ordering, but neither SNR nor frequency alone identifies semantic attribute timing.



### Finding and scope

The universal spectral/semantic explanation fails; the measured two-stage sampler can still work in its tested prompts.



### Proposed correction

State the decreasing expected signal-power premise and restrict the result to the SNR surrogate; retain semantic timing as an empirical observation.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
