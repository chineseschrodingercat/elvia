# DCA: Graph-Guided Deep Embedding Clustering for Brain Atlases



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The released DCA release omits centroids from optimization and changes graph/evaluation definitions. Its orthogonality expression can be nonreal or cancel, and zero-shift inversion can fail on a valid Laplacian.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The released training optimizer never updates the declared learnable centroids

Assessment: supported; impact: minor



Source: Section 3.2, Eq. (5), PDF pp. 4–5; separate supplement Section 6.1, p. 12.



### Source claim (paraphrase)

Section 3.2, Eq. (5), PDF pp. 4–5, and separate supplement Section 6.1 describe gradient updates of both centroids and the final encoder projection. Released DCA/model.py registers self.D as a trainable root parameter. DCA/main.py, train_DCA, constructs its Adam optimizer solely from model.swinunetr.named_parameters(), which excludes that root parameter.



### Analysis

The centroid parameter \(D\) is a root parameter outside model.swinunetr.named_parameters(), the sole input to the released optimizer. Backpropagation can set \(D\)'s gradient, but optimizer.step cannot update an absent parameter. Thus that released path does not implement the claimed trainable-centroid update. This source-level conclusion does not identify the historical table-producing program.



### Finding and scope

The current optimizer cannot update its declared learnable centroid parameter; the program used for each published table remains unidentified.



### Proposed correction

Include the centroid parameter together with the intentionally unfrozen encoder parameters, using explicit parameter groups or all parameters with requires_grad enabled; clear gradients for the same complete set.

The existing local proposal remains applicable to the current author source/formal text; author adoption is not established.



## Problem 2: Graph weighting subtracts the wrong mean and can reverse an edge’s sign

Assessment: supported; impact: minor



Source: Section 3.2, Eq. (2), PDF p. 5.



### Source claim (paraphrase)

Paraphrase: Section 3.2, page 5, Eq. (2), defines the weight of an edge by cosine similarity between the two individually demeaned embeddings:

\[a_{ij}=\cos(z_i-\bar z_i\mathbf1,z_j-\bar z_j\mathbf1), \qquad \bar z_i=\frac1d\sum_{r=1}^d z_{ir}. \]



### Analysis

For embeddings \((0,1)\) and \((10,11)\), subtracting each row's own mean gives identical centered vectors and cosine \(1\). Subtracting the common scalar mean \(5.5\) instead gives cosine \(-99/101\). The released common-mean operation can therefore reverse an edge sign rather than merely rescale its weight.



### Finding and scope

A valid adjacent pair changes weight from positive one to a negative value under global centering; downstream atlas changes have not been measured.



### Proposed correction

Subtract each embedding’s mean along its feature dimension before cosine similarity; specify a separate policy for constant embeddings. This corrects centering but does not ensure nonnegative graph weights.

The existing local proposal remains applicable to the current author source/formal text; author adoption is not established.



## Problem 3: The public homogeneity evaluator removes zero and negative correlations

Assessment: supported; impact: minor



Source: Section 3.3, Eq. (6), PDF p. 6.



### Source claim (paraphrase)

Paraphrase: Section 3.3, page 6, Eq. (6), defines parcel homogeneity using all ordered distinct voxel pairs:

\[H_k=\frac{1}{m_k(m_k-1)}\sum_{i,j\in P_k,\ i\ne j}R(v_i,v_j). \]



### Analysis

Take three nonconstant voxel time series \(x,x,-x\), with \(x=(1,-1,0)\). Their strict lower-triangle correlations are \((1,-1,-1)\), so the paper’s all-pair mean is \(-1/3\); the current AtlaScore function retains only the positive entry and returns \(1\). The separate current training utility averages all three values and matches the paper, so the finding cannot be assigned to every published homogeneity result.



### Finding and scope

The public evaluator changes the statistic, but another active author utility implements the correct all-pair mean; table-to-evaluator lineage is unresolved.



### Proposed correction

Average all finite distinct-pair correlations as specified, without discarding nonpositive values; define missing/constant-series handling explicitly before any cohort reanalysis.

The existing local proposal remains applicable to the current author source/formal text; author adoption is not established.



## Problem 4: Including self-distance inflates the silhouette relative to Eq. (7)

Assessment: supported; impact: minor



Source: Section 3.3, Eq. (7), PDF p. 6.



### Source claim (paraphrase)

Paraphrase: Section 3.3, page 6, Eq. (7), first computes a voxel’s mean dissimilarity to the other voxels of its own parcel,

\[w_i=\frac1{m_k-1}\sum_{j\in P_k,\ j\ne i}[1-R(v_i,v_j)],\]



### Analysis

For two-voxel parcels with all distinct-pair correlations zero, within- and adjacent-parcel dissimilarities are both \(1\), giving silhouette \(0\). Including each self-distance of zero makes the within-parcel mean \(1/2\), producing silhouette \(1/2\). This uses the paper's adjacent-parcel rule and isolates the self-distance denominator error.



### Finding and scope

Self-distance reduces the within-parcel mean by a size-dependent factor and inflates the stated silhouette; the cohort-level magnitude and comparisons are unmeasured.



### Proposed correction

Exclude the diagonal before computing within-parcel mean dissimilarity; state singleton and missing-correlation conventions separately.

The existing local proposal remains applicable to the current author source/formal text; author adoption is not established.



## Problem 5: The orthogonality penalty is not a well-defined measure of orthogonality

Assessment: supported; impact: minor



Source: Appendix A.9.1, PDF p. 33; separate supplement Section 6.2, p. 13.



### Source claim (paraphrase)

Paraphrase: final Appendix A.9.1, page 33, and separate supplement Section 6.2, page 13, define a centroid matrix \(D\in\mathbb R^{K\times d}\) with unit-norm rows, its Gram matrix \(G=DD^\top\), and \(G_{\rm off}=G-I_K\). The displayed penalty is

\[R_\perp(D)=\sqrt{\frac1{K(K-1)}\sum_{i\ne j}(G_{\rm off})_{ij}}. \]



### Analysis

Unit centroid rows \((1,0)\) and \((-1,0)\) give ordered off-diagonal Gram sum \(-2\), so the displayed square root is nonreal. Conversely, rows \[(1,0,0),(1,0,0),(-1/2,\sqrt3/2,0)\] give sum zero although the first two rows coincide. A signed sum under a square root cannot be a real, nonnegative orthogonality measure on the stated domain.

Exact orthogonal unit rows additionally require \(K\le d\), since \(\operatorname{rank}(DD^\top)\le d\). At dimension \(256\), resolutions above \(256\) cannot satisfy \(DD^\top=I_K\). A soft decorrelation objective remains meaningful. The current default total_loss comments out this regularizer, so no NaN failure of default training or error in its ablation table is inferred.



### Finding and scope

The displayed penalty needs a nonnegative, noncancelling definition. The calculation does not establish that the historical implementation optimized this literal expression or that the clustering benchmark conclusions fail.



### Proposed correction

Use an explicitly nonnegative absolute or squared off-diagonal Gram penalty, with its domain specified. This is a local objective change whose empirical effect has not been measured.

A local correction or qualification is proposed where specified; author adoption is not established.

The existing local proposal remains applicable to the current author source/formal text; author adoption is not established.



## Problem 6: Zero-shift spectral inversion can fail on a valid spatial graph

Assessment: supported; impact: minor



Source: Section 3.2, PDF p. 5; released sparse_spectral_clustering zero-shift eigsh call.



### Source claim (paraphrase)

Section 3.2, PDF p. 5, forms the graph Laplacian \(L=D_{\rm degree}-W\) and requests its smallest eigenvectors. The released sparse_spectral_clustering path calls eigsh in shift-invert mode at \(\sigma=0\), which requires solving with \(L-\sigma I=L\).



### Analysis

Every exactly formed unnormalized graph Laplacian satisfies \(L\mathbf1=0\), so \(L\) is singular even for a connected graph. A zero-shift inverse solve can therefore fail on an otherwise valid spatial graph. Floating-point perturbations can allow some factorizations to proceed; this is not evidence that every complete run crashes.

A connected three-voxel path with unit edge weights gives \[L=\begin{pmatrix}1&-1&0\\-1&2&-1\\0&-1&1\end{pmatrix},\] whose eigenvalues are \(0,1,3\). The desired smallest two exist, but the current \(\sigma=0\) shift requests inversion of singular \(L\). This is independent of the negative-edge centering concern.



### Finding and scope

An admissible connected graph makes the released inverse-shift solve singular; this input-dependent solver defect does not establish failure of every complete DCA run.



### Proposed correction

Request smallest algebraic eigenpairs without a zero inverse shift, or use a separately validated nonzero-shift/preconditioned solver with residual checks. Nearest-to-zero and smallest algebraic eigenvalues differ for signed graphs.

The existing local proposal remains applicable to the current author source/formal text; author adoption is not established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
