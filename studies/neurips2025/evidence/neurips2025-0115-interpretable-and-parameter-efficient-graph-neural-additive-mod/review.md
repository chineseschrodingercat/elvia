# Interpretable and Parameter Efficient Graph Neural Additive Models with Random Fourier Features



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The stated pair-dependent Gaussian need not be positive semidefinite, and the imported robustness bound has incompatible domain/order conditions. Hop interpretation and released experiment protocols require separate corrections.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The pair-dependent Gaussian expression is not a valid covariance for every permitted graph

Assessment: supported; impact: major



Source: Section 3.1, Eq. (4), PDF p. 4.



### Source claim (paraphrase)

Paraphrase: Section 3.1, Equation (4), PDF p. 4 uses

\[K_{ij}=\exp\!\left[-\frac{a_{ij}(x_{i,k}-x_{j,k})^2}{2\Theta^2}\right]\]



### Analysis

A positive-semidefinite matrix with unit diagonal and \(K_{12}=1\) must satisfy \(K_{13}=K_{23}\): the first two unit feature vectors have inner product one and must coincide. The allowed choice \(x_1=x_2\), with different positive pair weights to a third node having \(x_3\ne x_1\), gives \(K_{12}=1\) but \(K_{13}\ne K_{23}\). The displayed pair-dependent Gaussian therefore fails to be a covariance on its stated graph domain.

Take \(x=(0,0,1)\), \(\Theta=1\), and positive pair weights \(a_{12}=1\), \(a_{13}=2\log2\), \(a_{23}=2\log4\). Then \[K=\begin{pmatrix}1&1&1/2\\1&1&1/4\\1/2&1/4&1\end{pmatrix}.\] For \(v=(1,-1,-1/4)^\top\), \(v^\top Kv=-1/16\), an impossible covariance quadratic form. This complete connected weighted graph satisfies the written domain; a single global weight is a valid RBF control.



### Finding and scope

The formula does not define a positive-semidefinite covariance for every permitted graph. This contradicts the central covariance justification; no new prediction-error or benchmark estimate follows.



### Proposed correction

Define one global filtered feature \(Z=H(L)X\) and apply the RBF kernel to \(Z_{ik}-Z_{jk}\), as in the later architecture. Its Fourier representation gives a nonnegative expected squared modulus, proving PSD. This is a changed covariance construction, not an algebraic identity with pair-dependent rescaling.

The existing local mathematical or protocol proposal is retained; the current author source/formal paper still has the identified behavior. No author adoption is established.



## Problem 2: The robustness theorem imports a bound with the wrong matrix domain and order conditions

Assessment: supported; impact: major



Source: Theorem 4.2, PDF p. 6; Appendix A, PDF p. 21; Lemma A.1, Eq. (11), PDF p. 22.



### Source claim (paraphrase)

Paraphrase: Theorem 4.2, PDF p. 6, repeated in Appendix A on p. 21, bounds every node’s prediction change by \(CK\epsilon D\|X\|_2\). Lemma A.1, Equation (11), p. 22, applies the corresponding filter bound to \(H(L)=\sum_{h=0}^{R}\alpha_hL^h\), explicitly taking \(L\) to be the normalized Laplacian. Its constant is

\[K_{\rm printed}=\frac14\|\alpha\|_1(R^2-1) \left(\frac{R-1}{R+1}\right)^R.\]



### Analysis

The imported higher-order result controls powers of \(L-I\), whose spectrum lies in \([-1,1]\), and treats first order separately. The paper instead uses powers of an unshifted normalized Laplacian. At \(R=1\), the printed factor \(R^2-1\) makes \(K=0\), although choosing the nonconstant filter \(H(L)=L\) allows a nonzero response to graph perturbation. Thus neither the matrix-domain substitution nor the missing order restriction is justified by that imported bound.

For the normalized Laplacians of the three-node path and triangle, choose \(X=e_2\), \(H(L)=L\), and scalar readout \(g(z)=\sqrt2\cos z\). The first-node outputs differ by approximately \(0.1659409412\), while the printed order-one constant is zero. Even repairing the reciprocal ratio leaves a matrix-domain failure: for \(H(L)=L^6\), the filter difference norm is approximately \(53.00267785\), exceeding the source-style bound \(41.84124064\); the shifted \(L-I\) control satisfies that bound.



### Finding and scope

The stated robustness theorem is not established by the cited argument, and its unrestricted first-order specialization cannot hold as written. Reversing a transcription ratio does not resolve these substantive conditions.



### Proposed correction

For unshifted normalized Laplacians of nonnegatively weighted undirected graphs, use \(K=\sum_{h=1}^R h2^{h-1}|\alpha_h|\). The noncommutative telescoping identity for \(\widehat L^h-L^h\) and \(\|L\|,\|\widehat L\|\le2\) prove it. Multiply by the stated RFF/readout constants for output stability; this restores a qualitative finite-degree bound with a different constant.

The existing local mathematical or protocol proposal is retained; the current author source/formal paper still has the identified behavior. No author adoption is established.



## Problem 3: A Laplacian coefficient does not directly measure one hop’s contribution

Assessment: supported; impact: minor



Source: Section 3.2, PDF p. 6; Section 6.1, PDF p. 8; Section 6.3, Figure 4(c), PDF p. 9; Appendix C.3, PDF p. 26.



### Source claim (paraphrase)

Paraphrase: The interpretation around Figure 4(c), Section 6.3, PDF p. 9, identifies each \(\alpha_h\) with information from the \(h\)-hop neighborhood. Related language occurs in Section 3.2/p. 6 and Appendix C.3/p. 26. Section 6.1/p. 8 describes explanatory curves against raw input feature values.



### Analysis

Let \(S=I-L\) and \(\alpha=(1,-2,1)\). Then \(H(L)=I-2L+L^2=S^2\). On a three-node path, an endpoint has no immediate-neighbor contribution in \(S^2\), although \(|\alpha_1|=2\) is largest. Laplacian-basis coefficients mix walk lengths and do not directly measure a single hop's contribution.

The same path/filter also defeats an unconditional raw-feature curve: changing \(X=(0,0,0)^\top\) to \((0,0,1)^\top\) leaves the first node’s raw value zero but changes its filtered value from \(0\) to \(1/2\). Its nonlinear contribution therefore depends on neighbor context. Feature-channel additivity and the radius bound remain valid.



### Finding and scope

Laplacian coefficients and filtered-channel outputs do not uniquely identify exact-hop or unconditional raw-feature effects; the architecture remains additive and finite-range.



### Proposed correction

Describe the parameters as coefficients in the Laplacian polynomial basis. Any exact-distance interpretation must first combine the relevant polynomial terms for the specified graph and input.

A local correction or qualification is proposed where specified; author adoption is not established.

The existing local mathematical or protocol proposal is retained; the current author source/formal paper still has the identified behavior. No author adoption is established.



## Problem 4: The public implementation’s R=\(1\) ablation uses no graph edges

Assessment: supported; impact: minor



Source: Eq. (6) and Algorithm 1, PDF pp. 5–6; Section 6.2, PDF p. 8; released models/gnamrff model implementations.



### Source claim (paraphrase)

Paraphrase: Equation (6), Algorithm 1 (pp. 5-6), and the one-hop interpretation of the \(R=1\) row in Section 6.2/p. 8 use degree \(R\), with powers zero through \(R\). The audited public implementation instead allocates torch.randn(R) and loops over range(\(1\), R) in models/gnamrff.py lines 18-31 and models/gnamrff_graph.py lines 23-35.



### Analysis

The released loop treats \(R\) as the number of coefficients. For \(R=1\), only the identity term survives and no edge information is propagated. That graph-free setting differs from the paper's degree-one convention, which includes both \(I\) and \(L\).



### Finding and scope

The current order convention removes all edge dependence at its first setting; exact historical ablation configuration and resulting accuracy changes remain unknown.



### Proposed correction

If \(R\) denotes degree, allocate \(R+1\) coefficients and include powers through \(L^R\); if it denotes coefficient count, relabel the degree as \(R-1\) and call its first setting graph-free. Historical run convention must be identified before relabeling or rerunning the ablation.

The existing local mathematical or protocol proposal is retained; the current author source/formal paper still has the identified behavior. No author adoption is established.



## Problem 5: The public graph experiment runner performs repeated holdouts rather than the specified \(10\)-fold protocol

Assessment: supported; impact: minor



Source: Section 6.4, PDF pp. 9–10; Appendix C.1, PDF p. 25; separate supplement p. 6.



### Source claim (paraphrase)

Paraphrase: Section 6.4 and Appendix C.1, pp. 9-10 and \(25\), specify \(10\)-fold graph cross-validation, with three random seeds per fold. The same protocol is stated on supplementary PDF p. 6.



### Analysis

Repeated random holdouts do not form a \(10\)-fold partition: test sets can overlap and examples need not be tested exactly once. Thus the public runner implements a different evaluation protocol; the source alone does not identify all historical table-producing runs.

The loader also resets the Torch seed to the fold after the caller sets a training seed, so the intended independent seed variation is not realized through that ordering. Within each call the train, validation and test slices are disjoint; this is a protocol mismatch, not demonstrated within-run test leakage.



### Finding and scope

The public reproduction path implements repeated holdouts and resets the training seed, rather than the stated fold/seed hierarchy; no inflation of historical means is established.



### Proposed correction

Generate one immutable partition of graph IDs into ten test folds. For each outer fold, reserve its test IDs and choose validation IDs only from the remaining training pool. Save all IDs. Train three independently seeded models per fold, using a separate split generator and setting the training seed after split selection. Average according to the declared hierarchy and state whether the reported uncertainty is across folds, seeds, or both.

A local correction or qualification is proposed where specified; author adoption is not established.

The existing local mathematical or protocol proposal is retained; the current author source/formal paper still has the identified behavior. No author adoption is established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
