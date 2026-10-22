# Personalized Subgraph Federated Learning with Differentiable Auxiliary Projections



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Counterexamples affect the three principal mathematical guarantees. APV sign and kernel-normalization mismatches and narrower table-level claims are separate issues; reported accuracies were not reproduced.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The small-bandwidth gradient does not imply principal-component learning

Assessment: supported; impact: major



Source: Theorem 3.1, Eqs. (9)–(10), PDF p. 6.



### Source claim (paraphrase)

Paraphrase of Theorem 3.1, p. 6, Eqs. (9)–(10): for the covariance \(C=N^{-1}\sum_i h_i h_i^\top\), the APV gradient has the expansion

\[ \nabla_a\mathcal L=-\frac{2}{\sigma^2}Ca+R(\sigma), \qquad \|R(\sigma)\|=O(1),\quad \sigma\to0^+. \]



### Analysis

Use centered embeddings \(\pm e_1\) and projection \(a=(1,1)/\sqrt2\). The Gaussian cross-weight is \(q=\exp(-4a_1^2/\sigma^2)\). As \(\sigma\to0^+\), smoothing approaches the identity and the projection derivative decays exponentially. In contrast, the asserted term \(-2Ca/\sigma^2\) is nonzero and diverges for this covariance. Even choosing the linear-loss gradient as the identity cannot reconcile those limits.

With loss \(\mathcal L=(\|z_1\|^2+\|z_2\|^2)/2\), the proof’s linear-gradient assumption holds with \(W=I\). Writing \(t=\tanh(2a_1^2/\sigma^2)\), the exact derivative is \[\nabla_a\mathcal L=\left(\frac{8a_1}{\sigma^2}\tanh\frac{2a_1^2}{\sigma^2}\operatorname{sech}^2\frac{2a_1^2}{\sigma^2},0\right)^\top\to0.\] Separately, for covariance \(\operatorname{diag}(1/4,1/2)\) and step \(0.4\), the written normalized iteration multiplies coordinates by \((0.9,0.8)\), so it selects the smaller-eigenvalue direction, rather than the principal one.



### Finding and scope

The claimed leading PCA-gradient expansion is false on the stated finite-embedding domain. This invalidates that theoretical explanation, not the reported classification measurements.



### Proposed correction

Retain exact quotient-rule differentiation. For fixed finite embeddings with positive projected separation \(\delta\) and bounded loss gradients, the derivative is \(O(\sigma^{-2}e^{-\delta^2/\sigma^2})\to0\). This valid restricted statement does not repair the original PCA-identification claim.

The existing restricted mathematical or implementation proposal is retained; the current paper/source still has the cited statement. No author adoption is established.



## Problem 2: The sorting limit needs a tie condition, and its convolution bound is incorrect

Assessment: supported; impact: major



Source: Theorem 3.2, Eq. (11), PDF p. 6.



### Source claim (paraphrase)

Paraphrase of Theorem 3.2, p. 6, Eq. (11): for kernel-smoothed embeddings sorted by their scalar scores, and any fixed zero-padded convolution \(\operatorname{Conv}_W\),

\[ \|\operatorname{Conv}_W(\widetilde Z)-\operatorname{Conv}_W(\widetilde H)\|_F\to0 \quad(\sigma\to0^+). \]



### Analysis

Take embeddings \((0,1)\) and \((0,-1)\) and projection \(a=e_1\). Their projected scores tie, so kernel smoothing averages both to zero for every bandwidth. A one-tap identity convolution of the original embeddings retains them, giving Frobenius difference \(\sqrt2\) rather than a limit of zero. A tie restriction and a valid convolution estimate are needed.

The convolution proof also underestimates overlapping contributions: scalar taps \((1,1,1)\) acting on \((1,1,1)\) with zero padding produce \((2,3,2)\), of norm \(\sqrt{17}>3\), exceeding the claimed product \(\sqrt3\sqrt3\). This is independent of the tie witness.



### Finding and scope

The stated universal limit is false without additional score-separation conditions. Its failure concerns the formal guarantee; the actual frequency of score ties is not measured.



### Proposed correction

The correct fixed-input limit averages embeddings within each equal-score class. Distinct scores, or identical embeddings within each tie class, recover \(Z\to H\). The convolution constant \(\sum_\tau\|W_\tau\|_{\rm op}\) is valid by the triangle inequality for zero-padded shifts; neither correction proves equivalence to an implemented architecture without that convolution.

The existing restricted mathematical or implementation proposal is retained; the current paper/source still has the cited statement. No author adoption is established.



## Problem 3: The global convergence bound omits the cost of mixing heterogeneous objectives

Assessment: supported; impact: major



Source: Theorem 3.3, Eq. (12), PDF p. 7.



### Source claim (paraphrase)

Theorem 3.3, p. 7, Eq. (12), assumes: every local loss is \(L\)-smooth; stochastic gradients are unbiased with variance at most \(\zeta^2\); every loss satisfies a \(\mu\)-Polyak–Łojasiewicz inequality; and

\[ \rho=\sup_t\|\Omega^{(t)}-\mathbf1\mathbf1^\top/K\|_2<1. \]



### Analysis

Let the two client objectives be \(f_1(\theta,a)=\tfrac12(\theta-1)^2+\tfrac12(a-1)^2\) and \(f_2(\theta,a)=\tfrac12(\theta+1)^2+\tfrac12(a-1)^2\). They are smooth and PL, with exact gradients. From common state \((0,1)\), a local step moves \(\theta\) oppositely; perfect averaging returns both clients to \((0,1)\). Their average local-optimum gap remains \(1/2\), even with zero gradient noise and perfect mixing. A bound forcing that gap to zero omits the cost of heterogeneous optima.

Take \(Q=1\), \(\eta=1/4\), \(L=\mu=1\), and equal client weights. Their nonzero APVs stay at \(1\), giving exactly the prescribed uniform mixing and \(\rho=0\); exact gradients give \(\zeta=0\). After the first local step the two task parameters are \(1/4\) and \(-1/4\), so mixing resets both to zero. The actual average gap is \(1/2\), whereas Eq. (12) bounds it by \((1/2)(3/4)=3/8\). Thus every stated assumption is met and the theorem fails already at one round.



### Finding and scope

The stated convergence guarantee cannot hold for every permitted heterogeneous-client problem. The example does not show that the method fails for all datasets or that a global-objective guarantee with a different target is impossible.



### Proposed correction

A common convex objective with doubly stochastic mixing permits a narrower local-descent argument. The heterogeneous personalized setting instead needs explicit control of losses at other clients’ parameters; no corrected theorem with the original assumptions is established.

The existing restricted mathematical or implementation proposal is retained; the current paper/source still has the cited statement. No author adoption is established.



## Problem 4: Sign-equivalent local representations receive opposite server similarities

Assessment: supported; impact: minor



Source: Section 3.2, PDF p. 5; Appendix C.1.1, PDF p. 24.



### Source claim (paraphrase)

Section 3.2, p. 5, interprets APV cosine similarity as similarity of the local subgraphs. Appendix C.1.1, p. 24, explicitly recognizes that the local kernel and classifier are unchanged when \(a\) is replaced by \(-a\). These two facts are incompatible without an orientation convention.



### Analysis

Replacing \(a\) by \(-a\) leaves every squared projected difference, kernel weight and local prediction unchanged, but changes cosine similarity with \(a\) from \(1\) to \(-1\). At similarity temperature \(10\), a sign-equivalent partner can receive relative weight \(1/(e^{20}+1)\). This is descriptor non-identifiability; shared initialization may nevertheless maintain orientation in practice.



### Finding and scope

Sign reversal preserves the complete local function but changes server similarity; common initialization may preserve orientation, and no incidence of harmful sign flips is measured.



### Proposed correction

A sign-invariant comparison such as \(\cos^2(a,b)\) or projector \(aa^\top/\|a\|^2\) removes this exact descriptor ambiguity. Averaging the vectors also requires a sign-alignment/tie policy to avoid cancellation. These are unvalidated design proposals, not recovered benchmark performance.

The existing restricted mathematical or implementation proposal is retained; the current paper/source still has the cited statement. No author adoption is established.



## Problem 5: The released kernel uses per-node cosine normalization instead of the paper’s common normalization

Assessment: supported; impact: minor



Source: Section 3.1, PDF p. 3; released models/fedpub_aux/nets.py, MaskedGCN._kernel_aggregate, line 59.



### Source claim (paraphrase)

Section 3.1, p. 3, defines \(s_i=\langle h_i/\max_j\|h_j\|,a\rangle\). In the README-selected source, models/fedpub_aux/nets.py, MaskedGCN._kernel_aggregate, line 59, instead evaluates F.cosine_similarity(h, self.aux.unsqueeze(\(0\)), dim=\(-1\)). Thus every node is separately divided by its own norm and the APV norm. Both then use the same Gaussian weighting pattern.



### Analysis

For \(h_1=(1,0)\), \(h_2=(2,0)\), \(a=(1,0)\), and \(\sigma=1\), common normalization gives scores \((0.5,1)\) and aggregates approximately \((1.4378234991,0)\) and \((1.5621765009,0)\). The current cosine code makes both scores \(1\), returning \((1.5,0)\) for each. A global bandwidth adjustment cannot turn distinct projected scores into a tie. The active current source therefore computes a different allowed-input function.



### Finding and scope

The released default kernel differs from the stated projection map; publication-run identity and performance sensitivity are not established.



### Proposed correction

Use the paper’s common-node-norm score with explicit zero/normalization conventions, or label the cosine implementation as a different method and rework dependent analysis.

The existing restricted mathematical or implementation proposal is retained; the current paper/source still has the cited statement. No author adoption is established.



## Problem 6: The claim of winning every setting is contradicted by Table 1

Assessment: supported; impact: minor



Source: Table 1, PDF p. 7; Section 4.2, PDF p. 8.



### Source claim (paraphrase)

Section 4.2, PDF p. 8, claims leadership in every dataset/client-count combination. Table 1, PDF p. 7, gives the corresponding means and standard deviations.



### Analysis

On Amazon-Computer with \(10\) clients, FedAux reports \(89.92\) versus GCFL \(90.03\); with \(20\) clients it reports \(88.35\) versus Local \(89.52\) (and GCFL \(89.08\)). On Amazon-Photo with \(10\) clients it reports \(92.30\) versus FED-PUB \(92.46\). Thus the highest printed mean occurs in \(15\) of \(18\) settings. The unweighted mean FedAux–FedAvg difference is \(127.56/18\approx7.0866667\) percentage points, so the separate \(4.5\%\) gain needs an explicit averaging convention. No significance conclusion follows from these displayed means.



### Finding and scope

The universal wording must be narrowed to the actual table comparisons. A mean difference does not establish statistical significance or overall method inferiority.



### Proposed correction

The directly supportable statement is that FedAux obtains the highest reported mean in \(15\) of the \(18\) settings in Table 1. This statement is verified by a complete column comparison. It is not a statistical-significance result: the table gives three-run means and standard deviations, and the raw paired runs were not reanalyzed. This analysis does not infer that every positive difference is significant or that the three negative differences show an overall inferior method.

A local correction or qualification is proposed where specified; author adoption is not established.

The existing restricted mathematical or implementation proposal is retained; the current paper/source still has the cited statement. No author adoption is established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
