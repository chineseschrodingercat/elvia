# RNNs perform task computations by dynamically warping neural representations



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The current arXiv v2 retains invalid nonorthogonal curvature and energy-as-length formulas. Two further local geometric arguments need corrected maps/rank conditions.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Curvature formula fails in nonorthogonal coordinates

Assessment: supported; impact: major



Source: Section S8.4, arXiv v2 PDF p.23; working-memory notebook wm.ipynb, cell 65



### Source claim (paraphrase)

The paper and supplied curvature routine compute Gaussian curvature from the metric entries \(E,F,G\), without requiring orthogonal coordinates.



### Analysis

Use the regular plane chart \(r(u,v)=(u,e^uv,0)\). Its metric is \(E=1+e^{2u}v^2,F=e^{2u}v,G=e^{2u}\), with positive determinant \(e^{2u}\). The printed expression yields \(K=-1/2\), while the release’s different placement of factors yields continuum value \(K=1\). The surface is exactly a plane, so its independent geometric curvature is \(0\): every normal second-derivative component vanishes. A denominator regularizer changes the wrong nonzero value slightly and cannot restore zero.



### Finding and scope

The curvature computation is invalid on an admissible regular chart, so curvature-based patch selection and interpretations require reanalysis. This does not show the actual trained surface is flat or invalidate independent first-derivative metric analyses.



### Proposed correction

For \(J=[r_u\ r_v]\), use \(g=J^\top J\), normal projection \(P_\perp=I-Jg^{-1}J^\top\), and \[K=\frac{\langle P_\perp r_{uu},P_\perp r_{vv}\rangle-\|P_\perp r_{uv}\|^2}{\det g}.\] This Gauss formula applies in arbitrary ambient dimension at rank-two points.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Energy is treated as geometric length

Assessment: supported; impact: major



Source: Definition S7.2, arXiv v2 PDF p.15; Sections S8.3–S8.4, pp.21–23; wm.ipynb, cell 62



### Source claim (paraphrase)

The paper defines curve length by \(\int g(\dot\gamma,\dot\gamma)dt\), and some plotting blocks integrate diagonal metric entries directly.



### Analysis

On the Euclidean line, \(\gamma_1(t)=t\) and \(\gamma_2(t)=(t+t^2)/2\), \(0\leq t\leq1\), trace the same segment with positive velocities. The printed functional gives \(1\) and \(13/12\), while both geometric lengths are \(1\). With variable duration, \(\gamma_T=t/T\) has energy \(1/T\), so the endpoint infimum degenerates to zero. Even normalized grid positions differ: for embedding \(r(\theta)=\theta+\theta^2\), the half-interval cumulative energy fraction is \(7/26\), versus arclength fraction \(3/8\).



### Finding and scope

The central distance definition and affected grid interpretations use parameter-dependent energy rather than invariant length. Some other source cells use square roots correctly; the finding does not apply to every figure.



### Proposed correction

Use \(\int\sqrt{g(\dot\gamma,\dot\gamma)}dt\) for length and distinguish fixed-curve arclength from a minimizing geodesic distance. Fixed-duration minimum energy gives squared distance divided by duration, under suitable geodesic existence.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: Orthogonal-vector subtraction has a different pullback

Assessment: supported; impact: minor



Source: Section S8.5, arXiv v2 PDF p.25



### Source claim (paraphrase)

The map \(\phi(u_1,u_2)=u_2v_2-u_1v_1\), with orthogonal input vectors, is assigned pullback \(\left[\begin{smallmatrix}1&-1\\-1&1\end{smallmatrix}\right]\).



### Analysis

For \(v_1=e_1,v_2=e_2\), the Jacobian is \(\operatorname{diag}(-1,1)\) and the actual pullback is \(I_2\), of rank \(2\), rather than the claimed rank-one matrix. Generally it is \(\operatorname{diag}(\|v_1\|^2,\|v_2\|^2)\). The asserted matrix instead corresponds to \((u_2-u_1)v\) along one unit output direction.



### Finding and scope

The explanatory map calculation is wrong. It does not disprove the measured network’s rank-one output geometry, which may implement the different scalar-projection map.



### Proposed correction

Define the intended operation explicitly as \((u_2-u_1)v\) if scalar subtraction along a common direction is intended.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 4: Ambient full rank does not ensure tangent immersion

Assessment: supported; impact: minor



Source: Proposition S7.2, arXiv v2 PDF p.14



### Source claim (paraphrase)

A full matrix-rank ambient Jacobian and an embedded input manifold are asserted to give an immersed manifold after composition.



### Analysis

Take \(\psi(t)=(0,t)\) and \(\phi(x_1,x_2)=x_1\). The input map is an embedding and the ambient Jacobian \([1\ 0]\) has maximal matrix rank, but \(\phi\circ\psi=0\), with zero tangent derivative. The tangent lies entirely in the ambient kernel.



### Finding and scope

The local proposition lacks a tangent-injectivity condition. A separate full tangent-span condition elsewhere in the paper has the appropriate role, and the counterexample is not a refutation of that statement.



### Proposed correction

Require \(\operatorname{rank}(J_\phi D\psi)=\dim M\), equivalently trivial intersection of the tangent image with the ambient kernel. Full ambient column rank is a sufficient stronger condition.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
