# Reinforcing Spatial Reasoning in Vision-Language Models with Interwoven Thinking and Visual Drawing



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The public reflection proxy loses step and line-operation information, and invalid view-change answers can receive credit through default zeros. The decoding-cost table omits generated-prefix interactions.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: The reflection proxy does not retain cross-step operation identity

Assessment: supported; impact: minor



Source: Sections 3.1–3.2, PDF pp.4–6, Eq.(5); Section 4.3, PDF p.9; verl/utils/reward_score/gcot.py, format_reward, lines 64–133



### Source claim (paraphrase)

The prose defines reflection across reasoning steps and includes box and line operations. `format_reward` concatenates turns and compares only same-label box coordinates.



### Analysis

Two changed same-label boxes in one turn can therefore give a positive proxy without any second drawing step. Changed same-label lines across two turns are ignored. The printed formula itself omits an explicit distinct-step condition, so the first mismatch concerns its adjacent prose. Reflection is returned separately rather than simply added as RL reward. Author issue #6 explains latest-same-label drawing merge as intentional behavior.



### Finding and scope

The public proxy does not reliably implement the cross-step all-operation description. Exact historical figure processing is unresolved.



### Proposed correction

Retain step, operation type, image identity, coordinates and label; require distinct steps and changed operation signatures for the stated syntactic proxy. This still does not prove semantic self-correction.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Unknown motion fields silently become a valid zero vector

Assessment: supported; impact: minor



Source: Appendix C.2, PDF p.26; released eval/evaluate.py, lines 24–73; SPAR annotation question 2863



### Source claim (paraphrase)

The view-change parser accepts arbitrary keys; recognized directional lookups default to zero before scoring.



### Analysis

Invalid text `bad:123` becomes the zero motion vector. Actual question \(2863\) has target \((1.6,0,0,-75,15)\), so two zero axes score perfectly and mean credit is \(0.4\). Across the \(400\) public view-change targets, zero-vector scores occur with counts \((129,117,91,50,13)\) at scores \((0,0.2,0.4,0.6,0.8)\), mean \(0.2505\). This is an artificial invalid-answer baseline, not any model’s observed prediction distribution. Explicit valid zero-motion answers may properly receive partial credit.



### Finding and scope

The evaluator needs an explicit invalid-answer policy. Published scores cannot be corrected without their raw predictions.



### Proposed correction

Validate recognized axes, duplicate/opposing keys and finite values before vector conversion, then apply the same valid-vector metric. Document any intentionally permissive omission convention.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: The decoding table omits within-response attention

Assessment: supported; impact: minor



Source: Appendix E.1, PDF pp.30–31, Eqs.(9)–(10), Table 6; measured Table 7, PDF p.33



### Source claim (paraphrase)

Table 6 gives prompt-only \(O(MN)\) work for a dense cached decoder with input length \(M\) and output length \(N\).



### Analysis

Generated query \(j\) attends to \(M+j\) previous keys. Summing gives \(MN+N(N-1)/2\). At \(M=1,N=128\), the count is \(8256\), not \(128\); their ratio grows with output length. KV caching avoids recomputing old keys but not attention to them.



### Finding and scope

The unrestricted two-variable expression omits a term under standard dense attention. The measured runtime table and other sparse/recurrent mechanisms are not refuted.



### Proposed correction

For each generated block, include \(P_kB_k+B_k(B_k-1)/2\), where \(P_k\) is existing context and \(B_k\) the new block length. State a prompt-dominated approximation if that restricted regime is intended.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
