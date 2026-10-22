# Nonlinearly Preconditioned Gradient Methods: Momentum and Stochastic Analysis



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Two local release defects concern a half-scaled real phase gradient and a zero-gradient singularity. No convergence-theorem counterexample is established.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Real phase-retrieval derivative is missing a factor of two

Assessment: supported; impact: minor



Source: Appendix F.2.1, Eq.(42), PDF p.32; phase_retrieval/phase_ret.py, Problem.df; phase_retrieval/algorithms.py



### Source claim (paraphrase)

The real objective is \(f(x)=(2m)^{-1}\sum_i((a_i^\top x)^2-y_i)^2\), while the release returns \(m^{-1}A^\top[(Ax)\odot((Ax)^2-y)]\).



### Analysis

The real chain rule gives twice that returned vector. With \(A=(1,0),m=1,y=0,x=(2,0)^\top\), the objective is \(8\), true gradient \((16,0)^\top\), and released expression \((8,0)^\top\). The minibatch formulas share the missing factor. This is not reconciled by a complex-derivative convention because the stated domain and driver arrays are real.



### Finding and scope

The objective/oracle normalization is inconsistent. Logged gradient norms would be half the true values at the same iterates; all compared phase-retrieval methods share this convention, and no ordering reversal or convergence-theorem counterexample follows.



### Proposed correction

Multiply full and batch derivatives by two, or explicitly redefine the optimized objective and internal scales consistently. A nonlinear preconditioner generally prevents absorbing the difference solely into the outer learning rate.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Isotropic wrapper is undefined at zero gradients

Assessment: supported; impact: minor



Source: Algorithm 1, PDF p.5; Eq.(14), p.7; matrix_factorization/preconditioners.py, lines 18–20; algorithms.py, line 18



### Source claim (paraphrase)

The numerical radial wrapper evaluates the scalar preconditioner times \(g/\|g\|\), without a zero branch.



### Analysis

The cosh-dual radial map is \(\operatorname{arsinh}(\|g\|)g/\|g\|\) away from zero and extends continuously as zero because \(\operatorname{arsinh}(r)/r\to1\). The released quotient divides by zero at \(g=0\). This input occurs for matrix factorization \(f(U,V)=\|UV^\top-A\|_F^2/2\) at \(U=V=0,A=I_2\), where both gradients vanish even though the objective is positive. The update calls the wrapper before any zero-gradient termination.



### Finding and scope

The release has a removable-singularity failure on a valid stationary input. It does not establish NaNs in the published random-initialization runs; the mathematical map and convergence proofs already have the correct zero value.



### Proposed correction

Return a zero preconditioned-gradient term at zero norm and leave the momentum recurrence intact; nonzero previous momentum should still decay normally.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
