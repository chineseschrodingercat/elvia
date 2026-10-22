# Equi-mRNA: Protein Translation Equivariant Encoding for mRNA Language Models



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The asserted convex-angle product-group homomorphism fails on a two-element subgroup. A separate ambient-rotation assertion omits its complement, although the correct lift appears earlier. Regression-table compatibility is unresolved without common prediction and aggregation records.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: Convex angle averaging does not preserve the product-group law

Assessment: supported; impact: major



Source: Appendix A.5.1, PDF pp.17–18; Proposition A.4 and proof, PDF pp.20–21



### Source claim (paraphrase)

The proposed map sends component rotations to \(\phi(R(\theta_1),\ldots,R(\theta_n))=R(\sum_iw_i\theta_i\bmod2\pi)\) and is asserted to be a homomorphism for fixed or learned convex weights.



### Analysis

Take \(G_1=G_2=\{I,-I\}\), weights \(w_1=w_2=1/2\), and \(g=h=(-I,I)\), using angles \(0,\pi\). Then \(gh=(I,I)\), so \(\phi(gh)=I\); but \(\phi(g)=\phi(h)=R(\pi/2)\), giving \(\phi(g)\phi(h)=-I\). A coordinatewise angular carry of \(2\pi\) becomes only \(\pi\) after half weighting. Without a fixed branch, even the representatives \(0\) and \(2\pi\) for the identity give different outputs. A branch makes a function but does not fix the exhibited group-law failure.



### Finding and scope

The claimed product-group homomorphism is false. This does not refute circular-mean equivariance under one common rotation or the empirical prediction results.



### Proposed correction

Integer angle coefficients give well-defined torus homomorphisms. Alternatively, the paper’s circular mean \(s/|s|\), \(s=\sum_iw_iz_i\), is equivariant under a common rotation when weights are invariant and \(s\ne0\); it has a different guarantee. Keeping the unnormalized sum handles zero resultants globally.

A proposed correction is described; author adoption is not established.



## Problem 2: The projected Stiefel operator is not an ambient rotation

Assessment: supported; impact: minor



Source: Section 2.3, PDF p.4; Section 2.5, PDF pp.5–6; Proposition A.3 and proof, PDF pp.19–20



### Source claim (paraphrase)

Proposition A.3 asserts \(VRV^\top\in SO(d)\) and identity action on the orthogonal complement when \(V^\top V=I_2\).



### Analysis

For \(d=3\), \(V=(e_1,e_2)\) and \(R=R(\pi/2)\), the operator sends \(e_3\) to zero and has determinant zero. Generally \((VRV^\top)^\top(VRV^\top)=VV^\top\), a rank-two projector rather than the ambient identity. However, Sections 2.3 and 2.5 already give the correct full lift, and an aligned base vector in the plane makes the embedding values coincide. The projected-circle conclusion survives.



### Finding and scope

The appendix’s ambient operator assertion is false, while its restricted-plane interpretation and earlier corrected construction survive. An implementation failure is not established.



### Proposed correction

Use the existing full lift \(Q=I-VV^\top+VRV^\top\). Orthogonal plane/complement blocks give \(Q^\top Q=I\) and determinant \(1\). If projection is intended, restrict the rotation assertion to the plane.

The correct complement-preserving formula already appears in Sections 2.3 and 2.5; reconciliation of the appendix is not established.



## Problem 3: The reported regression pairs need a matched-evaluation definition

Assessment: needs_evidence; impact: needs_evidence



Source: Tables 15–16, PDF pp.31–32; Appendix A.9.2 and A.10, PDF pp.25–26



### Source claim (paraphrase)

The mRFP columns pair Pearson correlation and coefficient of determination for the same named variants. If they use one common nonconstant target/prediction vector and standard definitions, they must satisfy \(R^2\le r^2\).



### Analysis

Writing \(t=\sqrt{S_{pp}/S_{yy}}\) and \(d^2=N(\bar p-\bar y)^2/S_{yy}\), residual expansion gives \(R^2=r^2-(t-r)^2-d^2\le r^2\). The vanilla row has \(r=0.6875\) and \(R^2=0.8028\), while \(r^2=0.47265625\). The same conditional comparison fails in all thirteen printed mRFP rows, with the smallest gap over \(0.223\), beyond four-decimal rounding. However, separate checkpoints, subsets, target scales or fold/run aggregation can invalidate a direct shared-vector comparison; averaged correlations need not obey the squared-mean bound.



### Finding and scope

The table values are incompatible under a common-vector standard-metric interpretation. The paper does not supply enough evaluation records to establish that interpretation or identify a wrong column.



### Proposed correction

Identify sample IDs, prediction vectors, target scale, checkpoint, metric implementation and aggregation for both columns. Recompute matched metrics if that was intended; no replacement score is determined by correlation alone.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.

- Actual embedding/pooling implementation and matched prediction-level metric records were not identified in the acquired materials.
