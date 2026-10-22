# ReplaceMe: Network Simplification via Depth Pruning and Transformer Block Linearization



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



A nondefault unmerged fusion path omits a residual transform. Padding and regularization paths also differ from the intended calibration objective; the default merged least-squares path is an explicit passing control.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Adjacent unmerged transforms omit the transformed residual

Assessment: supported; impact: minor



Source: Current arXiv v4 Section 2.2, PDF pp.3–4, Eq.(5); Appendix A.16, PDF pp.23–24; ReplaceMe/lstsq.py, lines 195–246



### Source claim (paraphrase)

The fitted full-state target is \((Y+MT_1)T_2\), but the unmerged fusion applies both transforms only to the MLP contribution.



### Analysis

The fused expression is \(Y+MT_1T_2\), missing \(Y(T_2-I)\). In the scalar three-block example with \(T_1=3\), \(T_2=2\), the result is \(7\) rather than \(8\). The default merged fit uses one residual transform \(7\) and returns \(8\), so this witness does not accuse that default route.



### Finding and scope

The nondefault adjacent-unmerged option is not algebraically equivalent to its fit.



### Proposed correction

Merge adjacent cuts before fitting, as the passing default does, or explicitly transform the residual contribution. No blanket removal of fusion is justified.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Padding rows change the least-squares calibration target

Assessment: supported; impact: minor



Source: Current author ReplaceMe/lstsq.py and ReplaceMe/cosine_dist.py, flattened calibration activation accumulation



### Source claim (paraphrase)

The tokenizer supplies an attention mask, but flattened calibration activations enter the fit without masking padded positions.



### Analysis

Valid scalar rows \((M,B)=(1,1),(2,2)\) fit \(T=1\). Adding a masked row \((1,10)\) changes the unweighted fit to \(T=2.5\), giving valid-row squared error \(11.25\). The model’s attention mask does not automatically exclude a saved padded activation from a later regression.



### Finding and scope

The fit can depend on padding and batching. A deliberate pad-inclusive objective would need to be declared; historical influence is unknown.



### Proposed correction

Apply the same valid-token mask to every aligned activation tensor, giving weighted regression \(\|W^{1/2}(MT-B)\|_F^2\) with zero weights on padding.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: The elasticnet branch penalizes activations rather than the matrix

Assessment: supported; impact: minor



Source: Section 2.3, p. 4, Eq. (9); Section 3.3.2/Table 5, p. 8; utils.py lines 254–260.



### Source claim (paraphrase)

Equation (9) regularizes the transform matrix \(T\). The released `utils.py`, `adam_method`, instead applies its elasticnet-like term to transformed activations.



### Analysis

With input and target row \((1,0)\), matrices \(\operatorname{diag}(1,1)\) and \(\operatorname{diag}(1,100)\) produce the same transformed row and released loss, approximately \(0.135\), but very different matrix norms. An activation penalty cannot generally implement the stated matrix penalty.



### Finding and scope

The public option does not reproduce that regularization definition. The private ablation implementation is not identified.



### Proposed correction

Define the matrix regularizer and reduction explicitly and apply it to the matrix. Keep ordinary unregularized cosine and least-squares ridge paths distinct.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 4: The inverse and sample count require rank and noise conditions

Assessment: not_issue; impact: no_issue_found



Source: Current arXiv v4 Eq.(6), PDF p.4; Appendix A.2, PDF p.15; Appendix A.12, PDF p.21



### Source claim (paraphrase)

The displayed solution uses \((M^\top M)^{-1}M^\top B\), and the token discussion links a square transform to a quadratic token requirement.



### Analysis

For \(M=((1,1),(2,2))\), the inverse is undefined although a pseudoinverse gives an exact fit. Conversely, noiseless \(M=I_d\) recovers an arbitrary \(d\)-by-\(d\) transform from \(d\) vector-valued rows, so \(d^2\) parameters do not imply \(d^2\) tokens. No historical singular calibration is established.

Rank-revealing least squares or an explicitly declared ridge estimator specifies behavior beyond the full-rank inverse formula. Algebraic identifiability and statistical accuracy require separate conditions; no historical singular fit is established.



### Finding and scope

Full-column rank, conditioning, noise and dependence assumptions are needed for those interpretations.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
