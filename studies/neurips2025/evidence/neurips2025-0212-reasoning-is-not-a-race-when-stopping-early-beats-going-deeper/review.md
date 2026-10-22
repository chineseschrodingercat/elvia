# Reasoning Is Not a Race: When Stopping Early Beats Going Deeper



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The finite-step equality in Theorem 3.6 omits higher-order terms; admissible beam-search examples can reverse its predicted curvature sign. The surrounding dominance claim and early-stopping method are explicitly qualified as conjectural and heuristic.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: The printed second difference drops a sign-relevant remainder

Assessment: supported; impact: minor



Source: Theorem 3.6, Claim 3.7 and Proposition 3.8, p.6; Appendix A.3, p.14



### Source claim (paraphrase)

Theorem 3.6 prints \(\Delta^2E_t=p_t[\Delta V_{t+1}-\Delta V_t+V_t(\epsilon_t-\epsilon_{t+1})]\). Its proof discards products of small terms without retaining a remainder or a quantitative condition controlling their effect on curvature.



### Analysis

Use an absorbing incorrect state, horizon \(3\), correct-proposal error \(q=0.01\), beam width \(1\) and two independent expansions. Correct proposals score \(0.5\); an incorrect proposal scores \(1\) with probability \(a_t\), otherwise \(0\). Then \(\epsilon_t=q^2+2q(1-q)a_t\), \(V_t=(1-q)^{3-t}\), \(p_{t+1}=p_t(1-\epsilon_t)\), and \(E_t=p_tV_t\). For \(\epsilon=(0.002,0.00208,0.00216)\), all ranking error rates are below random-selection error \(q\) and increase over time. Yet \[E=(0.970299,0.9781398,0.9859649184)\] has \(\Delta^2E_0=-0.0000156816\), whereas the printed right side is \(+0.00002137608\). The omitted remainder \(-0.00003705768\) reverses the sign.

Increasing errors \((0.002,0.00201,0.00202)\) instead give positive actual curvature \(0.0000534798\); increasing ranking error alone does not imply concavity. The paper’s additional dominance expectation is qualitative, so this does not refute a separately imposed numerical dominance inequality. Claim 3.7 says “we expect,” Proposition 3.8 says “typically,” the footnote calls the shapes conjectural, and Section 4 calls the stopping rule heuristic.



### Finding and scope

The finite equality is false and cannot alone certify curvature. The affine z-score observation and elementary concave-sequence lemma are unaffected; no new beam-search benchmark result is asserted.



### Proposed correction

In this absorbing submodel the exact identity is \[\Delta^2E_t=p_t[(1-\epsilon_t)(1-\epsilon_{t+1})V_{t+2}-2(1-\epsilon_t)V_{t+1}+V_t].\] Retain the omitted remainder and require the negative leading contribution to exceed its magnitude before concluding strict concavity. A model with recovery from incorrect states needs additional terms; the absorbing formula is not a universal replacement.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.
