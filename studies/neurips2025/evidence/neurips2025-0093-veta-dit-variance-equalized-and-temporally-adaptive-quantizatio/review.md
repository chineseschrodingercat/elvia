# VETA-DiT: Variance-Equalized and Temporally Adaptive Quantization for Efficient 4-bit Diffusion Transformers



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The temporal-average and temporal-mixture definitions differ. Public scoring also uses signed rather than absolute maxima, and GPTQ calibration can smooth twice while inference smooths once.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Averaging tensors is not sampling a temporal mixture

Assessment: supported; impact: minor



Source: Section 3.2, PDF p.6, Eqs.(13)–(16); Appendix B, Algorithm 1, PDF p.21



### Source claim (paraphrase)

Equation (16) uses \(\tilde X=\sum_t\alpha_tX^{(t)}\), whereas Algorithm 1 samples/concatenates activation rows before covariance estimation.



### Analysis

Let \(X^{(1)}=((1,1),(-1,-1))\) and \(X^{(2)}=-X^{(1)}\). Equal scores give weights \(1/2\). The elementwise average is zero, with zero covariance; the row mixture has covariance \(\begin{pmatrix}1&1\\1&1\end{pmatrix}\). Reversing one timestep’s row order changes the average but leaves the mixture unchanged. KLT–Hadamard equalization of a specified covariance remains valid.



### Finding and scope

The two calibration objects are not equivalent without extra assumptions. Either can be an intentional heuristic if its interpretation is stated.



### Proposed correction

For a mixture, use mean \(\mu=\sum_t\alpha_t\mu_t\) and covariance \(\sum_t\alpha_t[C_t+(\mu_t-\mu)(\mu_t-\mu)^\top]\). Otherwise align the pseudocode and claims with the synthetic tensor average.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Signed maxima change the score and unshifted exponentials can overflow

Assessment: supported; impact: minor



Source: Eq.(13), PDF p.6; current dit/ptq_inference.py, get_incoherence_norm; analogous author PixArt/Open-Sora routines



### Source claim (paraphrase)

Equation (13) uses the largest absolute entry. Released `get_incoherence_norm` instead uses the signed maximum and directly exponentiates scores.



### Analysis

Rows \((-10,1)\) and \((10,-1)\) have equal required scores and weights \((1/2,1/2)\). Signed maxima give approximately \((0.14072,1.40720)\) and weights \((0.21986,0.78014)\). A finite \(505521\)-element tensor with one unit entry has score \(711\), whose direct exponential exceeds finite double range even though a single-timestep normalized weight is exactly \(1\).



### Finding and scope

The release differs from the stated sign-invariant score and has a defined-input numerical boundary. Real activation incidence is unknown.



### Proposed correction

Use maximum absolute entry, require nonzero finite norm, and subtract the maximum finite logit before exponentiation or use a stable softmax.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: GPTQ calibration uses a different basis from inference

Assessment: supported; impact: minor



Source: Appendix A, PDF p.21; current dit/ptq_inference.py and quant_utils/veta/veta_quant_layer.py, get_rotation_matrix and update_quantized_weight_rotated



### Source claim (paraphrase)

The caller stores smoothed data \(XS\) in `get_rotation_matrix`; the GPTQ update multiplies it by \(S\) again. Inference uses one smoothing transform.



### Analysis

Thus calibration receives \(XS^2T\) instead of \(XST\). For signed coordinate rows, \(S=\operatorname{diag}(2,1)\) and \(T=2^{-1/2}\begin{pmatrix}1&-1\\1&1\end{pmatrix}\), the intended accumulated Hessian is \(\begin{pmatrix}10&-6\\-6&10\end{pmatrix}\), whereas double smoothing gives \(\begin{pmatrix}34&-30\\-30&34\end{pmatrix}\). This is nonuniform curvature distortion; \(S=I\) is a passing case. Separate configuration naming issues can block a complete launch and are not treated as a successful run.



### Finding and scope

The intended public smoothing/GPTQ interface is inconsistent. No quantized-generation benchmark is recalculated.



### Proposed correction

Store either unsmoothed data and apply the scale once, or store the caller’s smoothed data and remove the extra multiplication. Use one explicit contract throughout calibration and forward inference.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
