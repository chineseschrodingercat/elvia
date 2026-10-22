# PDPO: Parametric Density Path Optimization



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The two-dimensional congestion kernel is singular while code uses a different bounded kernel. Absolute continuity does not guarantee a diffeomorphic transport class; Appendix A has repairable variational errors with fixed-endpoint equivalence retained.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The reported finite two-dimensional congestion problem is regularized in code but singular in the mathematical definition

Assessment: supported; impact: minor



Source: Latest arXiv v3, Appendix F.4, PDF p. 23; current author parametric_pushforward/obstacles.py, congestion_cost.



### Source claim (paraphrase)

Appendix F.4, PDF p. 30, defines

\[\mathcal C(\rho)= \int_{\mathbb R^d\times\mathbb R^d} \frac{2}{|x-y|^2}\rho(x)\rho(y)\,dx\,dy. \]



### Analysis

In two dimensions, a smooth density positive near a point makes the near-diagonal contribution of \(|x-y|^{-2}\) proportional to \(\int_0^\epsilon r^{-1}\,dr=+\infty\). Removing exact empirical self-pairs does not remove this population singularity. The implementation uses denominator \(|x-y|^2+1\), a bounded regularized functional, so its finite numerics do not evaluate the literal displayed objective.



### Finding and scope

This is a supported local finding within the stated source/formulation scope. Its effect on the paper's aggregate experimental results remains unmeasured.



## Problem 2: Absolute continuity alone does not justify the diffeomorphic static formulation

Assessment: supported; impact: major



Source: Section 2.1, PDF p. 3; Section 3.1 and Theorem 1, PDF p. 5 (diffeomorphic endpoint maps).



### Source claim (paraphrase)

Section 2.1, PDF p. 3, restricts the distributions to Lebesgue-dominated densities. The introduction, p. 1, describes a continuous velocity field. Section 3.1, p. 5, defines the static endpoint maps to be orientation-preserving diffeomorphisms and infers that this set is nonempty from the existence of endpoint densities. Theorem 1 then equates the dynamic problem (6) with the diffeomorphic static problem (11).

Appendix B, latest arXiv v3 PDF pp. 14–15, starts the forward direction by treating a dynamic local minimizer as a \(C^1\) diffeomorphic flow. Absolute continuity of the endpoint measures and continuity of the velocity do not establish this flow regularity.



### Analysis

Starting from uniform density on \([-1,1]\), continuous velocity \(v(x)=2\operatorname{sign}(x)\sqrt{|x|}\) sends nonzero particles to \(\operatorname{sign}(x)(\sqrt{|x|}+t)^2\). At positive time the endpoint density has two separated support components and finite action. A global diffeomorphism maps the initial connected support to a connected set, so no such diffeomorphism matches that endpoint. The example belongs to the broad weak continuity-equation class, while stronger continuously differentiable flow assumptions exclude it.



### Finding and scope

Endpoint absolute continuity and continuous velocity do not establish the claimed unrestricted diffeomorphic admissibility/equivalence. Matching stronger flow regularity changes the problem scope and must be explicit.



## Problem 3: Appendix A’s optimality equations need correction, while fixed-endpoint minimizer equivalence can be retained

Assessment: supported; impact: minor



Source: Latest arXiv v3, Section 2.2, PDF p. 4; Appendix A, optimization problems (17)–(18) and displayed KKT equations, PDF p. 14.



### Source claim (paraphrase)

Section 2.2, PDF p. 4, and Appendix A, Eqs. (17)–(18), latest arXiv v3 PDF p. 14, relate a deterministic continuity-equation action with Fisher information to stochastic control with diffusion coefficient \(\sigma^2/2\), using \(\Phi=S+(\sigma^2/2)\log\rho\).



### Analysis

With \(v=\nabla S\) and positive potential action, the variational Hamilton–Jacobi equation has the opposite displayed signs for the potential/Fisher terms; the stochastic multiplier equation also requires its diffusion Laplacian. However, setting \(a=\sigma^2/2\) and \(u=v+a\nabla\log\rho\) changes the integrated action only by a fixed endpoint-entropy term under the stated regularity and boundary conditions. Thus the appendix equations need correction while the fixed-endpoint minimizer correspondence can survive.



### Finding and scope

The local optimality-equation derivation needs correction. The entropy-boundary argument preserves fixed-endpoint minimizers under its regularity and boundary restrictions.



### Proposed correction

Use corrected variational equations and prove the action identity including its endpoint-entropy term, with the density regularity and boundary conditions stated explicitly.

A local correction or qualification is proposed where specified; author adoption is not established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
