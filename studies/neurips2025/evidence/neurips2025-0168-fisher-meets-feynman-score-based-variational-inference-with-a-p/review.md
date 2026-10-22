# Fisher meets Feynman: score-based variational inference with a product of experts



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The conditional convergence theorem requires a fixed almost-sure curvature floor that finite unbounded-support samples do not generally satisfy. Its conditional proof and the main Feynman construction remain intact. Singular-expert integrability is a limitation the authors explicitly acknowledge and check.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Finite tail batches preclude the claimed uniform curvature premise

Assessment: supported; impact: minor



Source: Theorem 3.1, Eq.(32), PDF p.8; Appendix E, PDF pp.19–22



### Source claim (paraphrase)

The convergence theorem assumes some deterministic \(\lambda>0\) lower-bounds every empirical Hessian almost surely.



### Analysis

Take one expert \(q_a(z)\propto(1+z^2)^{-a}\), initial \(a=1\), target \(q_2\), and batch size \(1\). The initial proposal is Cauchy, the unique Fisher-divergence minimizer is \(a=2\), and the score residual there is identically zero. Expert score \(Q=-2z/(1+z^2)\) gives actual Hessian \(8z^2/(1+z^2)^2\). For every \(\lambda>0\), choosing \(R>\max(1,\sqrt{8/\lambda})\) makes the Hessian below \(\lambda\) on \(|Z|>R\), which has positive probability \(2\arctan(1/R)/\pi\). Any finite independent batch can fall entirely in that tail. Larger batches reduce that probability, not to zero. Separately rank is at most \(BD\), so \(K>BD\) forces singularity.



### Finding and scope

The theorem remains conditional, but its stated sampling procedure does not generally meet the fixed almost-sure floor. Finite observed positive eigenvalues cannot establish that deterministic assumption; convergence failure is not proved.



### Proposed correction

A conditional mean-contraction premise \(E[(1+\eta m_t)^{-1}\mid\mathcal F_t]\le\rho<1\), with \(m_t=\lambda_{\min}(M_t)\), yields \(E\|e_t\|\le\rho^t\|e_0\|+\eta\delta(1-\rho^t)/(1-\rho)\) from the quadratic variational inequality. This is a different assumption; its multivariate applicability is unestablished.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: Singular experts need the separately acknowledged integrability check

Assessment: not_issue; impact: minor



Source: Section 2.1, PDF p.3; Eq.(30), PDF p.7; Appendix F.4, PDF p.26



### Source claim (paraphrase)

Total expert weight above \(D/2\) alone is not sufficient when singular precisions are allowed; the paper explicitly notes and checks this limitation.



### Analysis

In dimension \(2\), use precisions \(\operatorname{diag}(1,0)\), \(\operatorname{diag}(0,1)\), \(I\), initial weights \((1,1,6/5)\), target \(N(0,\operatorname{diag}(10,1/2))\), sample \((1,1)\), and proximal coefficient \(1/10\). The unique constrained quadratic minimizer is \((0,319/193,408/965)\), certified by residual \((79/965,0,0)\) and inactive sum constraint. Its total weight exceeds \(1\), but on \(|y|\le1\) the density lower-bounds a positive multiple of \((x^2+2)^{-408/965}\), whose \(x\)-integral diverges because \(816/965<1\). Strict margins persist near that sample. The authors’ full-rank-weight condition or a valid separate certificate excludes this update.



### Finding and scope

This explains the necessity of the extra verification the authors already report. It does not establish any improper plotted model or omitted author check.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
