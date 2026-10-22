# Unifying Reconstruction and Density Estimation via Invertible Contraction Mapping in One-Class Classification



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The reflected-resolvent construction need not contract under its stated assumptions, scalar LipSwish is noninjective, and the depth comparison confuses fixed-network bounds with cross-depth guarantees. The active tabular density path separately loses state/accumulator chains and uses the wrong determinant sign.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: The stated reflected-resolvent block can expand

Assessment: supported; impact: major



Source: Section 3.1.2, Eq.(2), p.6; Appendix B, p.22



### Source claim (paraphrase)

The paper calls \(f=((I+G)/2)^{-1}-I\) a contraction whenever \(G\) is invertible with \(\operatorname{Lip}(G)<1\).



### Analysis

On \(\mathbb R\), choose \(G(u)=-u/2\), an invertible map with Lipschitz constant \(1/2\). Then \((I+G)/2=u/4\), so \(f(x)=3x\) and \(f^{\circ k}(1)=3^k\). More generally, writing \(d=u-v,e=G(u)-G(v)\) gives \(\|f(x)-f(y)\|^2-\|x-y\|^2=-\langle d,e\rangle\); a norm bound does not impose its required sign. Invertibility and monotonicity remain compatible with this expansion.



### Finding and scope

The architecture’s stated hypothesis does not supply the contraction assumed in its reconstruction theory. This does not imply every learned instance expands or that every benchmark fails.



### Proposed correction

A new strong-monotonicity hypothesis \(\langle d,e\rangle\ge m\|d\|^2\), \(m>0\), gives squared contraction factor at most \(1-4m/(1+\eta)^2\). Alternatively scale the block by \(0<c<(1-\eta)/(1+\eta)\), using \(\operatorname{Lip}(f)\le(1+\eta)/(1-\eta)\). These are new assumptions/architecture changes, not properties established for current trained models.

A proposed correction is described; author adoption is not established.



## Problem 2: Scalar LipSwish does not preserve global invertibility

Assessment: supported; impact: minor



Source: Appendix B, p.22; Appendix F.2, p.25



### Source claim (paraphrase)

The described post-block activation \(s_\beta(x)=x/[1.1(1+e^{-\beta x})]\) is said to be invertible.



### Analysis

For \(\beta=1\), put \(r=1+\sqrt2\), \(x_1=-\log r\), \(x_2=-2\log r\). Since \(1+r^2=2(1+r)\), both distinct inputs have output \(-\log r/[1.1(1+r)]\). Thus the scalar activation is noninjective; composing it after a bijection preserves the collision. The active tabular code instead puts LeakyLSwish inside \(G\), which need not itself be injective for \(I\pm G\) to be invertible. That code placement is counterevidence against alleging this exact collision in the released complete flow.



### Finding and scope

The paper’s scalar-invertibility justification and described post-block architecture are false. The witness alone does not prove that the differently structured current full implementation is noninvertible.



### Proposed correction

Align the description with internal Lipschitz activations and justify the block inverse through the bijectivity of the identity-plus/minus contraction. A true post-block activation would require a separate proof of bijectivity.

A proposed correction is described; author adoption is not established.



## Problem 3: Cross-depth convergence does not follow from a product bound

Assessment: supported; impact: major



Source: Proposition 2 and its proof, p.5



### Source claim (paraphrase)

The proposition allows independently parameterized contraction layers yet infers that increasing depth moves abnormal outputs closer to a fixed point and a normal target.



### Analysis

For a fixed composition, \(\|\varphi_K(t)-x_K^*\|\le(\prod_j\eta_j)\|t-x_K^*\|\) is valid, but the fixed point varies with \(K\). Let \(e>0\), \(f_1(t)=t/2+e\), \(f_2(t)=t/2+e/2\). Their nested compositions are \(\varphi_1=t/2+e\), \(\varphi_2=t/4+e\); both reconstruct normal point \(0\) with error \(e\). At \(t=2e\), distance to the respective fixed point increases from \(0\) to \(e/6\), despite a smaller Lipschitz constant.

Global optimization of the stated unsquared loss also does not repair the quantifier. On normal points \(\{-e,e\}\), mean reconstruction loss for any \(L\)-Lipschitz map is at least \((1-L)e\), by the triangle inequality between the two endpoints. Nested maps \(\psi_1=t/2+e/2\), \(\psi_2=t/4-3e/4\) attain that bound for caps \(1/2,1/4\), with fixed points \(e,-e\). At abnormal input \(11e/10\), distances to those fixed points, and to the normal set, increase from \(e/20\) to \(21e/40\). These are global optima for the declared loss classes, not for the released joint MSE/density objective.



### Finding and scope

The per-network bound survives, but neither small training loss nor the product Lipschitz constant establishes monotone actual proximity across independently parameterized depths.



### Proposed correction

Retain the fixed-composition bound. A common fixed point \(x^*\) for every layer supplies \(\|\varphi_{K+1}(t)-x^*\|\le\eta_{K+1}\|\varphi_K(t)-x^*\|\); normal-set membership still needs its own condition.

A proposed correction is described; author adoption is not established.



## Problem 4: The active inverse-density chain drops states and reverses its sign

Assessment: supported; impact: minor



Source: Section 3.2, Eqs.(4),(6), pp.6–7; flow_net/denet.py, prob_predictor, lines 106–109; flow_net/layers/iMonotoneBlock.py, inverse, lines 67–80 and power-series coefficients around line 141



### Source claim (paraphrase)

The inverse-density loop passes the same final latent and original prior to every module, discards inverse states and overwrites density. The component inverse also subtracts a determinant series representing the forward block.



### Analysis

Even granting correct module inverses, take \(F_0(x)=x/2,F_1(x)=x/4,F_2(x)=x/5\). At \(x=1,z=1/40\), correct inversion visits \(1/40,1/8,1/2,1\) and adds \(\log(1/40)\) to the latent log density. The outer loop instead returns only module zero’s \(\log(1/2)\) correction at the unchanged latent, an error \(\log20\).

The odd-power coefficients \(-2/k\) yield \(\log\det(I-A)-\log\det(I+A)\), the forward determinant. For \(G(w)=w/3\), the block is \(f(x)=x/2\). Subtracting that forward determinant gives \(2\pi(x/2)\), whose integral is \(4\), whereas input density is \(\pi(x/2)/2\), with mass \(1\). The active prior returns an ordinary log density, so a negative-log convention does not explain the sign.



### Finding and scope

The released active tabular path is not the stated change-of-variables density evaluator. A constant affine offset can preserve rankings, and historical checkpoint/benchmark correspondence is unresolved.



### Proposed correction

Carry inverse state and density through every reversed module and add each forward log determinant, or subtract an explicitly inverse determinant. The chain rule proves the sum; both outer propagation and component sign must agree. Native solvers, gradients and benchmark reruns remain unverified.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.
