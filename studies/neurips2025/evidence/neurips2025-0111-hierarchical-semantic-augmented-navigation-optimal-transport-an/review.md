# Hierarchical Semantic-Augmented Navigation: Optimal Transport and Graph-Driven Reasoning for Vision-Language Navigation



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The written diagonal-only OT planner cannot transport between unequal marginals; under equal uniform marginals its plan is cost-independent. The claimed minimum-cost goal guarantee therefore does not follow.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: Infinite off-diagonal transport cost conflicts with the intended unequal marginals

Assessment: supported; impact: major



Source: Section 3.3, Eqs. (2)–(3) and Theorem 3.1, PDF p. 6.



### Source claim (paraphrase)

Paraphrase: Section 3.3, page 6, Eqs. (2)-(3), proposes transporting a uniform distribution over candidate nodes to a semantically biased target using a cost that is finite only on matching node indices. Theorem 3.1 and the following proof claim a unique optimal plan, convergence of Sinkhorn, and an optimal goal choice. The proof states lower semicontinuity of the cost and absolute continuity of both distributions with respect to Lebesgue measure as its hypotheses. The inspected rendered source is page 6.



### Analysis

Finite cost forces \(T_{ij}=0\) whenever \(i\ne j\). The row and column constraints then require both \(T_{ii}=\mu_i\) and \(T_{ii}=\nu_i\), hence \(\mu=\nu\). For \(\mu=(1/2,1/2)\) and \(\nu=(3/4,1/4)\), every coupling must move at least \(1/4\) off diagonal, giving infinite cost. Atomic node distributions also do not meet the cited Lebesgue-absolute-continuity hypothesis.



### Finding and scope

The theorem does not establish a finite unique transport plan or Sinkhorn convergence for its intended unequal node marginals. This is a mathematical failure of the written planner, separate from the unmeasured experimental implementation.



### Proposed correction

Equalizing the marginals restores diagonal feasibility but removes semantic redistribution. A different transport or direct goal-choice formulation would require an explicit changed objective; it is not a validated replacement for the complete navigation system.

A local correction or qualification is proposed where specified; author adoption is not established.

The stated reformulations are local proposals; the June 2026 author revision retains the diagonal-cost formulation and proof. No author correction or adoption is established.



## Problem 2: With equal uniform marginals, the plan cannot identify the minimum-cost goal

Assessment: supported; impact: major



Source: Text after Eq. (3), goal argmax, and Theorem 3.1 proof, PDF p. 6.



### Source claim (paraphrase)

Paraphrase: page 6 immediately after Eq. (3), the paper selects a goal by maximizing \(T_{ii}\). The proof of Theorem 3.1 then infers that this goal minimizes \(C_{ii}\) under the semantic constraint. This is the specific implication checked here.



### Analysis

With both marginals uniform on two nodes, the sole finite-cost coupling is \(T=I/2\), regardless of the diagonal costs. For diagonal costs \((2,1/2)\), both nodes maximize \(T_{ii}\), including the more expensive one. In general the plan is \(I/m\), so maximizing its diagonal cannot imply minimum-cost goal selection.



### Finding and scope

The minimum-cost goal implication is false even when finite feasibility is restored by equal uniform marginals. Merely equalizing the marginals does not repair goal selection.



### Proposed correction

For direct semantic-adjusted goal cost, minimizing \(\sum_i c_ix_i\) over the simplex selects minimum-cost candidates. A distinct KL-regularized formulation with positive semantic prior \(q\) and \(\varepsilon>0\) yields \(x_i\propto q_i e^{-c_i/\varepsilon}\). These are explicit changed decision objectives with elementary optimality proofs, not empirically validated replacements for HSAN.

The stated reformulations are local proposals; the June 2026 author revision retains the diagonal-cost formulation and proof. No author correction or adoption is established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
