# AlphaBeta is not as good as you think: a simple class of synthetic games for a better analysis of deterministic game-solving algorithms



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current SCOUT pseudocode inspects a leaf before its empty-window guard, while the finite-cost proof assigns zero cost to that state. An exact legal tree violates the finite prefactor-one inequality; a factor-two comparison preserves the main asymptotic upper bound.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Leaf-first SCOUT incurs a cost excluded by its finite bound

Assessment: supported; impact: minor



Source: Algorithm 4 and Theorem 5.2, arXiv v3 PDF p.7; Appendix A.3



### Source claim (paraphrase)

The theorem bounds full-window SCOUT leaf inspections by \(\sum_{s=-n+1}^n I_{\rm test}^{x,s}(h)\), but the proof assumes empty windows cost zero even at a leaf.



### Analysis

Take \(n=1,b=2,h=2\), root value \(0\), ordinary-child distribution concentrated at \(0\); the entire legal negamax tree is zero. TEST at thresholds \(0,1\) costs \(2,2\), total \(4\). Printed SCOUT first pays two reads testing the first child, then one read in its improving re-search, then rereads that leaf at window \([0,0]\), and finally tests the other root child once: total \(5>4\). Every game value returned is correct. A full-support uniform distribution on \(\{-1,0,1\}\), conditional root \(0\), likewise gives expected SCOUT \(11/2\) versus summed TEST \(115/24\); the point-mass case is not essential.



### Finding and scope

The exact finite-cost bound does not describe the printed guard order. This does not establish wrong game values or falsify the asymptotic comparison.



### Proposed correction

Check the empty window before reading a leaf to match the proof. Alternatively, for nonempty full windows \(n\ge1\), every extra read can be charged to a preceding TEST read, giving printed cost at most twice corrected cost. That fixed factor preserves the asymptotic upper growth bound when limits exist; it does not restore the finite prefactor one.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
