# Policy Compatible Skill Incremental Learning via Lazy Learning Interface



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The latest paper’s unconditional fallback union can select an already rejected skill despite an available goal-valid skill. The official supplement and current author implementation already use a conditional candidate branch that avoids this counterexample.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: An unconditional fallback can defeat goal validation

Assessment: supported; impact: minor



Source: Section 4.3, Eq.(8), p.5; Appendix A.2, Algorithm 2; Appendix A.3, Figure 8; lazySI.py, forward, lines 1111–1154



### Source claim (paraphrase)

When the proposed skill fails goal validation, the printed rule ranks state proximity over \(A(g)\cup\{z_h\}\), where \(A(g)\) contains goal-valid skills. The following prose says the rejected proposal \(z_h\) is only a fallback when no valid candidate exists.



### Analysis

Take two skills, proposal \(z_h=1\), state \(s=0\), and goal \(g=10\). Give the state prototypes means \(0,1\), the goal prototypes means \(0,10\), and every Gaussian variance \(1\). With threshold \(\sqrt{\chi^2_{1,0.99}}\approx2.575829\), skill \(1\) fails goal validation and skill \(2\) passes. The unconditional union nevertheless ranks skill \(1\) first because its state distance is \(0\), versus \(1\). Four duplicate prototypes satisfy the stated prototype count; small perturbations preserve the strict inequalities. The same construction embeds in \(60\) dimensions with identity covariance, whose threshold is approximately \(9.401<10\). In contrast, the author implementation collects valid candidates and introduces its nearest-goal fallback only when that collection is empty, so it avoids this example.



### Finding and scope

The current printed candidate formula does not enforce its own stated fallback semantics. This is a paper/implementation specification inconsistency, with no demonstrated current-code failure or reward reduction.



### Proposed correction

Make the rule conditional: retain \(z_h\) if it is valid; otherwise rank over \(A(g)\) when nonempty; use an explicitly chosen fallback only when \(A(g)=\varnothing\). Align the empty-set fallback with the implementation, which uses nearest goal proximity rather than necessarily returning \(z_h\).

The official supplemental implementation and current public implementation already avoid the demonstrated failure. The latest paper formula still contains the unconditional union.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.
