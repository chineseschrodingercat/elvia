# Plug-and-play Feature Causality Decomposition for Multimodal Representation Learning



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Two substantial theoretical failures remain in the current final paper: deterministic conditional information is identically zero, and the permitted URD aggregation need not be a measure-preserving bijection. These invalidate the stated causal justification, without establishing that the reported prediction scores are incorrect.



## Scope

Fresh reading of the final proceedings theorem, its proof, the complete URD equations and the official supplemental appendix. The current publication channels and exact-title search were checked for a later target version; no author implementation was executed.



## Problem 1: Deterministic conditional mutual information is zero

Assessment: supported; impact: major



Source: Final proceedings, Theorem 4.1 and Eqs. (4)–(6), p. 5; Appendix A, Eqs. (28)–(29), pp. 21–22.



### Source claim (paraphrase)

Theorem 4.1 takes the deterministic representation \(U=F(H)\), assumes \(F\) is a measure-preserving bijection, and equates maximization of \(I(U;Y\mid H)\) with an interventional mutual-information objective. Eqs. (4)–(6) use that equivalence to justify the supervised InfoNCE term as backdoor adjustment and noise removal.



### Analysis

For every measurable deterministic \(F\), the conditional joint law given \(H=h\) is exactly the product of its conditional marginals: \[P_{U,Y\mid H=h}=\delta_{F(h)}\otimes P_{Y\mid H=h}=P_{U\mid H=h}\otimes P_{Y\mid H=h}.\] Therefore every conditional KL divergence is zero and \(I(F(H);Y\mid H)=0\). This proof applies to discrete and continuous representations without subtracting potentially infinite differential entropies. Bijectivity or volume preservation cannot restore a representation-selection signal.

Appendix A additionally treats a fixed label marginal as implying \(P(Y\mid H)=P(Y)\). That implication is false: fixed marginal prevalence is compatible with completely predictive features. An algebraic manipulation of the observational distribution also cannot define a changed interventional probability law without specifying the intervention distribution and its label marginal.

A complete witness to different maximizers can be given under the volume-preserving reading used by Appendix B. Let \(I_j=[j,j+1)\), for \(j=0,1,2\), and let \(H\) have densities \(1/2,1/4,1/4\) on those intervals. Let \(F_0\) be the identity and \(F_1\) swap \(I_0,I_1\) by translation while fixing the remainder of the real line. Both are Lebesgue-measure-preserving measurable bijections. Define \(U_j=F_j(H)\), \(R_j=H-F_j(H)\), and the same label mechanism \(Y=\mathbf1_{\{U_j+R_j\in I_1\}}\). Both schemes have the identical observational label \(Y=\mathbf1_{\{H\in I_1\}}\), and both conditional-information objectives are zero.

Define randomized intervention by sampling \(U_j\) from its own observational marginal independently of \(H\), retaining \(R_j(H)\) and the stated label mechanism. The input interval probabilities are \(q_0=(1/2,1/4,1/4)\) and \(q_1=(1/4,1/2,1/4)\). For \(F_0\), the three conditional label probabilities are \((0,1,0)\); for \(F_1\), they are \((1/4,1/4,1/2)\). With binary entropy \(H_b\) in bits, the corresponding mutual informations are \[I_{q_0}(U;Y)=H_b(1/4)=0.8112781245,\qquad I_{q_1}(U;Y)=H_b(5/16)-\tfrac34H_b(1/4)-\tfrac14=0.0375796392.\] Thus both maps maximize the constant CMI over this two-map family, whereas only \(F_0\) maximizes this defined interventional objective. If preservation instead means preservation of a specified nonuniform probability law, this particular interval swap need not qualify; the general CMI identity remains unchanged.



### Finding and scope

The current deterministic conditional-information objective is degenerate, and the published proof does not establish its replacement by the stated causal objective. The explicit randomized-intervention witness also separates maximizer sets under the declared volume-preserving interpretation. The supervised loss can remain a useful predictive regularizer; its empirical usefulness does not repair this causal derivation.



### Proposed correction

A valid replacement identity is \(I(F(H);Y\mid H)=0\). If \(F\) has a measurable inverse, data processing in both directions also gives \(I(F(H);Y)=I(H;Y)\). Treat InfoNCE as predictive supervision unless a nondegenerate, identifiable intervention model and its estimator are separately established. This does not restore the original causal theorem.

The current final paper and freshly obtained official appendix retain the implicated construction; no adopted correction is established.



## Problem 2: Layerwise constraints do not certify the aggregate map

Assessment: supported; impact: major



Source: Final proceedings, Eqs. (7)–(8), pp. 5–6; Appendix B, Algorithms 1–3, p. 23.



### Source claim (paraphrase)

The paper asserts that its URD construction is a measure-preserving bijection. It constrains linear-layer singular values and constructs orthogonal affine layers, while the complete map aggregates three weighted residual decompositions with real-valued, linearly projected gates \(w_k\in\mathbb R\).



### Analysis

The actual aggregate is \[U=F_f\!\left(\sum_{k=1}^{3}w_kU_k\right),\quad U_k=F_d(H_k),\quad H_1=H,\quad H_k=H-\sum_{i<k}w_iU_i.\] Choose one-dimensional identity component maps, zero biases and zero coefficients in each gate projection, so \(w_1=w_2=w_3=0\). Identity component matrices have singular value \(1\), satisfy the \(10^{-5}\) lower bound, and can be obtained from Algorithm 3 by \(W=[1]\), since \(\exp(W-W^\top)=1\).

Every residual input then equals \(H\), but the weighted sum and output are identically zero. In particular, inputs \(H=0\) and \(H=1\) both map to \(U=0\). The full map is not injective and sends an interval of length \(1\) to a point. More generally, any deterministic outer component would return the constant \(F_f(0)\), regardless of unspecified activation details. The printed real linear gates do not exclude this allowed zero choice.

The positive control is important: Algorithm 3 itself is correct for a square affine layer. For \(A=W-W^\top\), \(Q=e^A\) satisfies \(Q^\top Q=I\) and \(\det Q=e^{\operatorname{tr}A}=1\); translation does not change volume. Pure compositions preserve this property. Weighted sums and residual feedback are not pure composition. Even an additional hypothetical equal softmax gate would yield \(U=[1-(1-1/3)^3]H=(19/27)H\) with identity components, which is invertible but not volume preserving. That control is not a claim that the paper uses softmax.



### Finding and scope

The constraints do not guarantee the complete URD map is a measure-preserving bijection, although the isolated affine-layer construction is valid. The counterexample refutes a universal architectural guarantee; it does not show that the trained representation actually collapsed.



### Proposed correction

Retain the valid affine-layer statement and remove the unsupported whole-map guarantee unless a full-network invertibility and Jacobian argument is supplied. No architecture-preserving causal repair is established.

The current final paper and freshly obtained official appendix retain the implicated construction; no adopted correction is established.



## Limits

- Independent scientific adjudication remains pending.

- No author implementation, training logs or sample-level predictions were available for this check, and no author code was executed.

- The interventional witness below explicitly adopts Lebesgue-volume preservation and a randomized do-operation. A different specified reference measure or intervention requires its own analysis; the conditional-information zero identity does not depend on those choices.

- The theoretical counterexamples do not determine the empirical contribution of supervised contrastive learning, alignment or additional model capacity.

- Direct current OpenReview note/PDF requests returned HTTP 403; the current final proceedings and its official supplement were accessible and inspected.
