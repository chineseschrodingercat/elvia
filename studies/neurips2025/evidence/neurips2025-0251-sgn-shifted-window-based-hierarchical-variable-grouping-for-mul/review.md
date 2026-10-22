# SGN: Shifted Window-Based Hierarchical Variable Grouping for Multivariate Time Series Classification



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Five bounded release/specification discrepancies concern odd-period shifts, dataset initialization, two similarity objectives and FLAAP subject splitting. The reported benchmark gains are not remeasured.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Odd-period shifts fail to invert

Assessment: supported; impact: minor



Source: Section 3.3, Eq.(7), PDF p.6; Table 7, p.28; SGN.py, TemporalSwinTransformerBlock.forward, lines 164–191



### Source claim (paraphrase)

The right cyclic shift is said to restore the original coordinates after shifting by \(P/2\). The release uses floor-divided shifts \((-P)//2\) and \(P//2\); the PTB-XL configuration has \(P=25\).



### Analysis

For \(P=2k+1\), the shifts sum to \(-(k+1)+k=-1\), rather than zero. With an identity feature map, \(P=3\) and input \((0,1,2,3,4,5)\), the two rolls give \((1,2,3,4,5,0)\); the prefix overwrite yields \((0,2,3,4,5,0)\). Even periods give cancelling shifts.



### Finding and scope

The released odd-period coordinate mapping does not implement the stated restoration. This does not establish any change in benchmark accuracy.



### Proposed correction

Compute \(h=\lfloor P/2\rfloor\) once and use shifts \(-h,+h\); their cyclic maps are inverse for every integer period.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Initialization always loads TDBRAIN assignments

Assessment: supported; impact: minor



Source: Section 3.1, PDF p.4; Appendix A, p.24; SGN.py, GumbelGroupEmbedding.__init__, line 237; exp_classification.py, _build_model, lines 44–67



### Source claim (paraphrase)

The model initializes grouping from the selected dataset, but the embedding always reads groups_matrix_T.npy.



### Analysis

The builder writes distinct files for TDBRAIN, PTB-XL, FLAAP and UCI-HAR, with shapes \[(33,4),(12,4),(6,5),(9,6)\]. A clean PTB-XL build writes only its own file, so the fixed TDBRAIN filename is absent. If the TDBRAIN file exists instead, its \(33\) channel rows cannot contract with the \(12\) PTB-XL input channels.



### Finding and scope

The published construction path has a concrete filename/shape mismatch. An unpublished renaming workflow and the experimental snapshot remain unknown.



### Proposed correction

Pass the selected assignment matrix directly to the embedding and require its shape to equal \((C,G)\).

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: Cosine regularization changes assignment preferences

Assessment: supported; impact: minor



Source: Section 3.1, Eq.(3), PDF p.5; SGN.py, similarity_regularization, lines 276–280



### Source claim (paraphrase)

The paper uses \(L=\sum_{ij}S_{ij}\|M_i-M_j\|^2\), with signed cosine similarities. The release uses weights \((1+S_{ij})/2\) and divides by \(C^2\).



### Analysis

For \(C=G=2\), assignment rows \((1,0),(0,1)\), and off-diagonal cosine \(s\), the paper gives \(4s\) while the release gives \((1+s)/2\). At \(s=-1\), these are \(-4\) and \(0\); at \(s=0\), they are \(0\) and \(1/2\). The difference includes an unweighted pair-distance penalty and cannot be absorbed into a positive loss rescaling.



### Finding and scope

The documented and released objectives are inequivalent, including interior soft assignments by continuity. Which objective generated the tables is not established.



### Proposed correction

Specify whether signed cosine weights or shifted nonnegative weights are intended, and align the displayed objective and implementation.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 4: Initializer computes squared distance correlation

Assessment: supported; impact: minor



Source: Appendix A, Eqs.(9)–(12), PDF p.24; exp_classification.py, distance covariance and similarity functions



### Source claim (paraphrase)

The paper clusters rows of distance correlation \(R_n\); the routine returns squared distance covariance and therefore normalizes to \(R_n^2\).



### Analysis

For \(X=(0,1,2,3)^\top\) and \(Y=(0,1,0,1)^\top\), double-centering gives cross-value \(1/8\) and self-values \(13/16,1/4\). Thus the routine returns \(R_n^2=1/\sqrt{13}\), whereas Eq.(9) gives \(R_n=13^{-1/4}\). Entrywise squaring is nonlinear, so it need not preserve Euclidean row distances used by K-means.



### Finding and scope

The formula/routine discrepancy is established for nonconstant samples. The builder loads precomputed matrices, so this does not determine their provenance or show that the benchmark groupings change.



### Proposed correction

Take the nonnegative square root of the normalized squared quantity to match Eq.(9), with an explicit zero-variance convention; alternatively document the squared initializer.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 5: FLAAP loader does not enforce subject separation

Assessment: supported; impact: minor



Source: Section 4.1, PDF pp.7–8; Appendix B.3, p.25; data_loader.py, FLAAPLoader.load_flaap_dependent, lines 622–648



### Source claim (paraphrase)

The experiment description restricts each subject to one data subset. The released FLAAP loader splits sample arrays twice without receiving subject identifiers.



### Analysis

The function calls sample-level train_test_split with test fractions \(0.2\) and \(0.25\), producing \(60/20/20\) sample proportions. Subject labels do not enter either call. Therefore windows from the same subject are eligible for different subsets; sample partitioning alone cannot establish the stated subject-disjoint guarantee. TDBRAIN instead uses explicit identifier lists.



### Finding and scope

The release lacks the claimed safeguard. Actual FLAAP subject overlap and score inflation require the unavailable benchmark split manifest; neither is established by this source check.



### Proposed correction

Partition by subject identifiers and publish the disjoint subject lists, allowing approximate sample proportions when subject sizes differ.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
