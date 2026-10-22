# Transformers Learn Faster with Semantic Focus



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Explicit softmax/support-change and geometric-series counterexamples undermine several stated bounds. The released evaluation and landscape scripts also diverge from their declared contracts; full experimental effects remain unknown.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The stated softmax \(\ell_1\)-Lipschitz constant misses an essential contribution

Assessment: supported; impact: major



Source: Lemma 2, Eq. (12), PDF p. 8; Lemma 4, Eqs. (109)–(110), PDF p. 45.



### Source claim (paraphrase)

Paraphrase: Lemma 2, PDF p. 8, Eq. (12), and its expanded Lemma 4, PDF p. 45, Eqs. (109)–(110), state that whenever both vectors have spread at most \(\delta>0\),

\[ \|s(z)\|_\infty\le e^\delta/L, \qquad \|s(z)-s(\bar z)\|_1\le(e^\delta/L)\|z-\bar z\|_1. \]



### Analysis

Take \(z=(0,0,0)\), \(\bar z=(0.01,0,0)\), and \(\delta=0.01\). Both spreads satisfy the hypothesis. The exact change is \(\|s(z)-s(\bar z)\|_1=4(e^{0.01}-1)/(3(e^{0.01}+2))\approx0.004451827\), but the claimed bound is \((e^{0.01}/3)0.01\approx0.003366834\). The first probability bound remains valid; the Lipschitz inequality does not.

The Jacobian is \(\operatorname{diag}(p)-pp^\top\): column \(j\) contributes \(p_j(1-p_j)\) on the diagonal and the same total off diagonal, so its induced \(\ell_1\) norm is \(\max_j2p_j(1-p_j)\). At uniform probabilities this exceeds \(1/L\) whenever \(L>2\). The earlier cited softmax result contains an analogous problematic constant; no priority claim is made.



### Finding and scope

The stated softmax Lipschitz constant is false, so later stability bounds cannot use that constant without a new derivation. No experimental performance reversal follows from this calculation.



### Proposed correction

Use the exact induced Jacobian norm \(\max_j2p_j(1-p_j)\). On a fixed support of size \(n\), \(\min\{1/2,2e^\delta/n\}\) is a safe bound; keep probability and derivative constants distinct and rederive downstream estimates.

The stated local proposal is retained; the current paper or author source still has the identified behavior. No author adoption is established.



## Problem 2: The heavy-hitter support-change proof drops common-support normalization terms

Assessment: supported; impact: major



Source: Lemma 6, PDF pp. 54–56, especially Eqs. (229)–(230), PDF p. 55.



### Source claim (paraphrase)

Lemma 6, PDF pp. 54–56, seeks a Lipschitz comparison of \(s_b(z)\) and \(s_{\bar b}(\bar z)\), with \(b=m(z)\), \(\bar b=m(\bar z)\), \(k\) selected logits, selected spread at most \(\delta\), and gap at least \(\Delta>0\). In Eq. (229), it applies a fixed-mask bound at an intermediate vector. In Eq. (230), PDF p. 55, it bounds the full distance between two differently masked softmaxes by contributions on indices where the masks differ. Both steps need conditions or terms that are absent.



### Analysis

The endpoint pair \(z=(1,2,0)\) and \(\bar z=(1,0,2)\) has the respective top-two masks in the claim, selected spread \(\delta=1\) and positive gap \(\Delta=1\), so it meets the stated endpoint conditions without a tie.

At \(\bar z=(1,0,2)\), compare masks \((1,1,0)\) and \((1,0,1)\). Their common first coordinate changes because the two normalizers differ. The full \(\ell_1\) distance is \(2e/(e+1)\approx1.462117\), whereas summing only the two changed-support coordinates gives \(1\). Thus Eq. (230) drops a positive contribution even without a support-boundary tie; the separate fixed-mask intermediate step also needs its own domain conditions.

The intermediate fixed-mask step is also unjustified: \(z=(0,0,-10)\) and \(\bar z=(0,-10,0)\) each have own-support spread \(0\) and gap \(10\), but applying the old mask to \(\bar z\) selects logits of spread \(10\). The endpoint assumption \(\delta=0.01\) therefore does not hold at that intermediate vector.



### Finding and scope

The displayed support-change estimate is not a valid proof of the claimed bound. A corrected argument must retain common-support normalization changes.



### Proposed correction

On the stated positive-gap domain, the weaker valid constant is \(\max\{C_{k,\delta},1/\Delta\}\), where \(C_{k,\delta}\) is a valid fixed-support constant. Different supports require an input change of at least \(2\Delta\), while probability-vector distance is at most \(2\). This avoids the invalid intermediate steps but does not restore the claimed favorable dependence on \(k\).

The stated local proposal is retained; the current paper or author source still has the identified behavior. No author adoption is established.



## Problem 3: The multilayer loss bound can be negative because the geometric-series formula lacks its domain condition

Assessment: supported; impact: major



Source: Theorem 2, Eq. (11), PDF p. 8; Corollary 1, Appendix F.3, Eq. (79), PDF p. 42.



### Source claim (paraphrase)

Theorem 2, PDF p. 8, Eq. (11), and Corollary 1 in Appendix F.3, PDF p. 42, Eq. (79), give

\[ \lambda_{\mathcal L}=\alpha\left[\Xi+q^\tau\left(1+ \frac{\lambda_\theta}{L(q-1)}\right)\right], \quad q=\lambda_{\mathcal X}. \]



### Analysis

The hypotheses do not require \(q>1\). On the intended bounded domain, choose dimension and sequence length \(d=L=2\), depth \(\tau=1\), bounds \(B=\Xi=1\), and LayerNorm scale \((0.6,0.6)\), shift zero, and \(\epsilon=1\). Valid conservative attention constants \((\lambda_X,\lambda_W,\lambda_V)=(0.01,0.02,2)\) give the paper's block constants \(q=0.7272\) and \(\lambda_\theta=3.8544\). With \(\alpha=1\), its loss constant is \(1+0.7272[1+3.8544/(2(0.7272-1))]\approx-3.410116\).

For an actual positive difference, take zero attention/feed-forward weights and input tokens \((0.5,-0.5)\). Two LayerNorm applications give \[(0.1554963166,-0.1554963166)\]. Comparing readouts \((1,0)\) and \((0,0)\) with sample loss \(|f|\) yields loss difference \(0.1554963166>0\), despite the negative claimed upper bound. All outputs and readout norms stay within the stated unit bounds.



### Finding and scope

The unrestricted geometric-series simplification is false on an admissible bounded domain. It is undefined at q equal to one and can be negative below one; this does not imply the experiments used that regime.



### Proposed correction

Retain the nonnegative finite sum \(\alpha[\Xi+q^\tau+(\lambda_\theta/L)\sum_{j=0}^{\tau-1}q^j]\). The sum is \((q^\tau-1)/(q-1)\) for \(q\ne1\) and \(\tau\) at \(q=1\). Alternatively impose \(q>1\) for the looser printed bound. This repairs only the composition step; its attention constants still require justification.

A local correction or qualification is proposed where specified; author adoption is not established.

The stated local proposal is retained; the current paper or author source still has the identified behavior. No author adoption is established.



## Problem 4: Released attention applies dropout during evaluation

Assessment: supported; impact: minor



Source: Appendix D, PDF p. 29; released multihead_attention.py, scaled_dot_prod.



### Source claim (paraphrase)

Appendix D, PDF p. 29, specifies dropout probability \(0.01\). In released multihead_attention.py, scaled_dot_prod calls functional dropout with the supplied dropout_p and the default active training mode. MultiHeadAttention.forward supplies the same positive probability in evaluation mode.



### Analysis

A functional dropout call using its default training flag continues to mask activations after the enclosing module enters eval mode unless the module's training flag is passed. This is a contract mismatch for the released attention path; published-run provenance and numerical effects are not inferred.



### Finding and scope

Current attention remains stochastic in evaluation mode; no remeasurement establishes the size of its effect on model rankings or loss surfaces.



### Proposed correction

Pass the enclosing module’s training state to functional dropout, or supply zero dropout probability during evaluation.

The stated local proposal is retained; the current paper or author source still has the identified behavior. No author adoption is established.



## Problem 5: ListOps skips one example and divides evaluation totals by the full dataset size

Assessment: supported; impact: minor



Source: Appendix D (ListOps implementation); released ListOps training and evaluation denominator calculations.



### Source claim (paraphrase)

In the released listops.py, batch_yielder and evaluate stop at the dataset size minus one, omit the final item, and divide evaluation totals by the full dataset size.



### Analysis

With \(N=5\) uniformly correct examples, the loop counts only \(4\) but divides by \(5\), reporting \(80\%\) instead of \(100\%\). The loss denominator has the same mismatch. The relative effect on a full benchmark depends on its size; no substantial benchmark impact is established.



### Finding and scope

The released evaluator omits one example; at the stated holdout size \(N=2000\), this isolated accounting error is at most \(0.05\) percentage points and does not explain the reported convergence gains.



### Proposed correction

Use the full dataset size as the exclusive loop and slice boundary, then divide the totals by the number of examples actually processed.

The stated local proposal is retained; the current paper or author source still has the identified behavior. No author adoption is established.



## Problem 6: The loss-landscape code does not compute the direction-normalized estimator in Eq. (306)

Assessment: supported; impact: minor



Source: Figure 5, PDF p. 10; Appendix G.5, PDF pp. 62–65, especially Eq. (306), PDF p. 63.



### Source claim (paraphrase)

Figure 5, PDF p. 10, Appendix G.5, PDF pp. 62–65, and Eq. (306), PDF p. 63, interpret neighboring loss-grid differences as directional estimates of the loss Lipschitz constant. The displayed estimator divides by both the coordinate step \(\epsilon\) and the norm of the perturbation direction:

\[ \frac{|\mathcal L(\Theta+x\vartheta_1+y\vartheta_2) -\mathcal L(\Theta+(x+\epsilon)\vartheta_1+y\vartheta_2)|} {\epsilon\|\vartheta_1\|}, \]



### Analysis

Let \(\theta=2\), \(L(\theta)=\theta\), direction \(v=2\), and step \(\epsilon=0.005\). The loss change is \(0.01\). Dividing only by \(\epsilon\) gives \(2\), whereas the direction-normalized quotient in Eq. (306) is \(1\). The released quotient changes under direction rescaling, so it is a different estimator.



### Finding and scope

Omitting direction norms changes the measured landscape statistic; the required norms are unavailable for reconstructing corrected published curves, and no performance reversal follows.



### Proposed correction

For horizontal edges, divide each difference by \(h_x\|\vartheta_1\|\); for vertical edges, divide by \(h_y\|\vartheta_2\|\). Normalize these two sets before pooling their quantiles, because the direction norms can differ. The norms must use the same parameter metric as the theorem being evaluated; with the paper’s tuple norm, this is the maximum spectral norm across matrix parameter blocks, with an explicit convention for vectors and auxiliary learned parameters. Alternatively normalize both complete directions to unit norm in that metric before producing the grid.

A local correction or qualification is proposed where specified; author adoption is not established.

The stated local proposal is retained; the current paper or author source still has the identified behavior. No author adoption is established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
