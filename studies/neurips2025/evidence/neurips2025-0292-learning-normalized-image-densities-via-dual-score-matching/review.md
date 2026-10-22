# Learning normalized image densities via dual score matching



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The forward Brownian estimator identity needs a Laplacian/convention correction, and Bayes optimality does not yield a fixed-image dimensionality upper bound. These are local interpretation/derivation defects; the central dual-score training identities survive.



## Scope

Rapid, claim-focused reading of the latest applicable author-paper and resource passages. Direct mathematical or static-source reasoning is stated below. No author program, retained verifier, model inference or benchmark was executed.



## Problem 1: The forward Brownian identity omits a Laplacian drift

Assessment: supported; impact: minor



Source: Latest arXiv v 3, Appendix A.2, Eq.(17), PDF p.17; Appendix B, Eq.(35), p.20



### Source claim (paraphrase)

For forward Brownian motion \(dX_t=dW_t\), Eq.(17) writes \[U(X_0,0)=U(X_T,T)-\int_0^T\nabla U\cdot dW_t+\tfrac12\int_0^T\|\nabla U\|^2dt.\]



### Analysis

For the true heat-flow energy \(U=-\log p_t\), \(\partial_tU=\tfrac12\Delta U-\tfrac12\|\nabla U\|^2\). Forward Itô calculus therefore gives \[dU=\nabla U\cdot dW_t+(\Delta U-\tfrac12\|\nabla U\|^2)dt.\] Take the normalized heat flow \(p_t=\mathcal N(0,1+t)\). Then \(U(y,t)=\tfrac12\log[2\pi(1+t)]+y^2/[2(1+t)]\) and \(\Delta U=1/(1+t)\). The printed right-hand side exceeds the true initial energy by \(\log(1+T)\) on every Brownian path, almost surely. At \(T=1\), the gap is \(\log2>0\).

A right-endpoint stochastic integral adds the quadratic-covariation term \(\int\Delta U\,dt\), so that convention can rescue the displayed formula. It is not the ordinary forward Itô reading of the stated forward SDE. This is a background estimator identity; the spatial/time-score training objectives do not use this formula.



### Finding and scope

The stated forward interpretation needs a drift correction or an explicit backward-integral convention. This does not establish an error in the reported learned-energy likelihood measurements.



### Proposed correction

For a smooth true heat-flow energy, subtract \(\int_0^T\Delta U(X_t,t)dt\) from the printed right-hand side. Alternatively, explicitly define and consistently discretize a right-endpoint integral.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Problem 2: Bayes optimality does not give a pointwise dimensionality upper bound

Assessment: supported; impact: minor



Source: Latest arXiv v 3, Eq.(11), PDF p.9; Appendix C.3, p.22



### Source claim (paraphrase)

Appendix C.3 claims the denoiser-MSE dimensionality estimate upper-bounds the true dimensionality. Equation (11) conditions on an individual clean image \(X=x\).



### Analysis

Let the true clean law be \(P=\mathcal N(0,1)\), noise variance \(t=1\), and model law \(Q=\mathcal N(0,1/3)\). Both give smooth, normalized heat flows. The true denoiser is \(m(y)=y/2\), while the model-energy denoiser is \(g(y)=y/4\). With \(Y=x+Z\) and \(Z\sim\mathcal N(0,1)\), \[D(x,1)=(x^2+1)/4,\qquad D_g(x,1)=(9x^2+1)/16.\] Thus \(D_g-D=(5x^2-3)/16<0\) throughout \(|x|<\sqrt{3/5}\), a set of positive probability. At \(x=0\), the estimate is \(1/16\) versus the true \(1/4\).

Bayes orthogonality instead gives the population identity \[\mathbb E\|X-g(Y)\|^2=\mathbb E\|X-m(Y)\|^2+\mathbb E\|m(Y)-g(Y)\|^2.\] Its cross term vanishes after conditioning on \(Y\), not after fixing \(X=x\). In this same example, population dimensionalities are \(1/2\) and \(5/8\), so population Bayes optimality survives.



### Finding and scope

The one-sided interpretation of individual-image dimensionalities is invalid. Their actual observed curves, nonnegativity and the population MSE bound are not disproved.



### Proposed correction

State the upper bound only after averaging over the true clean-data law: \(\mathbb E_XD_g=\mathbb E_XD+t^{-1}\mathbb E\|m_t(Y)-g_t(Y)\|^2\). Individual-image estimates remain nonnegative but have no general one-sided error guarantee.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Problem 3: The homogeneity discussion depends on regularity at the origin

Assessment: not_issue; impact: no_issue_found



Source: Latest arXiv v 3, Appendix B.2, PDF p.19



### Source claim (paraphrase)

The discussion relates a conservative degree-one homogeneous score to Gaussian conditionals along affine lines.



### Analysis

Degree-one homogeneity with differentiability at the origin implies \(s(y)=Ds(0)y\), by evaluating \([s(hy)-s(0)]/h\) as \(h\downarrow0\). Conservativity then gives a symmetric quadratic potential; normalizability requires a positive-definite precision. Gaussian conditionals follow. A counterexample based on \(V(a,b)=\tfrac12\sqrt{a^4+b^4}\) lacks score differentiability at the origin and therefore does not refute this globally differentiable reading.



### Finding and scope

Retain this as a regularity clarification. No separate error is established under the stronger smoothness interpretation, and no exact Gaussian claim is inferred for the approximately homogeneous trained architecture.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- Mathematical counterexamples and source discrepancies do not remeasure published experiments; historical execution results were not rerun.
