# Feature Distillation is the Better Choice for Model-Heterogeneous Federated Learning



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Rectangular orthonormal projection preserves only retained-subspace geometry, and separate projection orthogonality does not prevent conflicting updates to shared features. The square exponential identity, dimensional alignment and empirical regularization benefits remain compatible with these limits.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: Dimension reduction cannot preserve all source geometry

Assessment: supported; impact: minor



Source: Section 3.3, Eqs.(6)–(8), pp.6–7



### Source claim (paraphrase)

The text invokes rotational invariance after truncating a square orthogonal matrix to align a lower-dimensional teacher, attributing feature-shape preservation to that map.



### Analysis

In a favorable orientation let \(A=Q_d^{\top}\), \(AA^{\top}=I_d\), \(P=A^{\top}A\). Then \(\|Av\|^2=\|v\|^2-\|(I-P)v\|^2\). With \(D=4,d=2,Q=\exp(0)=I_4\), the projection retains only the first two coordinates: \(e_3,e_4\) collapse to zero despite distance \(\sqrt2\). The data matrix containing the standard basis has full row rank, so a full-rank assumption does not rescue preservation. Multiplication by any fixed projection remains linear regardless of sample count/rank.



### Finding and scope

Norms/distances survive exactly on retained directions, not all source features. Tensor-dimension alignment and possible task-relevant approximate preservation remain intact.



### Proposed correction

State contraction and retained-subspace isometry. If discarded pairwise components are at most \(\varepsilon\) times original distance, retained distance lies between \(\sqrt{1-\varepsilon^2}\) and one times original distance; that data-dependent condition is not established here.

A proposed correction is described; author adoption is not established.



## Problem 2: Separate orthogonality does not eliminate shared-gradient conflicts

Assessment: supported; impact: minor



Source: Section 3.3, conflict-prevention explanation and Eq.(9)



### Source claim (paraphrase)

Per-map identities \(A_iA_i^{\top}=I\) do not control cross-map inner products \(g_i^{\top}g_j=r_i^{\top}A_iA_j^{\top}r_j\).



### Analysis

Use coordinate projections from \(\mathbb R^4\) retaining first \(2\) and first \(3\) coordinates, both permitted truncations of \(I_4\). At \(z=(1,1,1,0)\), apply softmax to projected features and use teachers \((0.9,0.1)\), \((0.1,0.8,0.1)\). For teacher-to-student KL, shared gradients are \((-2/5,2/5,0,0)\) and \((7/30,-7/15,7/30,0)\), inner product \(-7/25<0\). For the printed reversed KL direction it is \(-\log9\log8/12<0\). Thus improving one term can worsen the other to first order under either convention. Softmax is an explicit favorable domain assumption, not recovered unavailable code.



### Finding and scope

Individual projection orthogonality permits this operational conflict. Conditioning improvements, learned conflict reduction and empirical benefit remain possible; no universal parameter-gradient result follows.



### Proposed correction

Describe a per-projection constraint and empirical regularizer; measure defined gradient conflicts. Cross-map orthogonality would suffice at the shared-feature level but is not imposed and may be infeasible; it is not offered as a validated replacement.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.
