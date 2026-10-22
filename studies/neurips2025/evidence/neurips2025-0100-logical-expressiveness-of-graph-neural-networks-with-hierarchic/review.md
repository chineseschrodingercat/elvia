# Logical Expressiveness of Graph Neural Networks with Hierarchical Node Individualization



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The individual-graph WL cutoff is too short for pointed-node equivalence, with a known late-refinement construction. Two proof constructions also omit neighbor exclusions and decomposition links; the hierarchy conclusions are not refuted.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Pointed-node WL can separate after the individual-size cutoff

Assessment: supported; impact: minor



Source: Current arXiv v2 Section 2, PDF p.3, WL cutoff and following all-depth classifier implication; Krebs and Verbitsky, universal-cover lower-bound family



### Source claim (paraphrase)

Section 2 defines indistinguishability after \(\max(|G|,|H|)\) rounds and then asserts indistinguishability by every permitted depth classifier.



### Analysis

Krebs and Verbitsky’s known family with parameters \(s=7,t=3\) gives two connected simple graphs, each with \((t+1)(s+10)-5=63\) vertices, maximum degree three and degree-one roots. Their rooted views agree through depth \(2[t(s+5)-1]=70\) and separate at \(71\). Joint exact color refinement has the same equality/separation. Thus the printed cutoff \(63\) passes a pair that an allowed depth-\(71\) classifier separates. This is a pointed-node result, not a claim about equal whole-graph color histograms.



### Finding and scope

The short cutoff is inconsistent with the following all-depth implication. The relation defined by the entire classifier family and the main hierarchy are not refuted.



### Proposed correction

Define equality at every depth, or refine the disjoint union to partition stability. A safe fixed cutoff is \(|G|+|H|-1\), since a partition can strictly split at most that many times.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: The multiset formula does not exclude absent neighbor types

Assessment: supported; impact: minor



Source: Current arXiv v2 Proposition 2.4, PDF p.4; Appendix A, PDF p.16, induction formula for a target neighbor multiset



### Source claim (paraphrase)

Appendix A fixes multiplicities only for types appearing in a target multiset \(Z\). For empty \(Z\), its count conjunction is empty.



### Analysis

Take a single edge with both vertices labeled \(p\), initial scalar embeddings \(1\), degree bound \(1\), and one-layer sum aggregation with combination equal to the aggregate. Output zero is attainable at an isolated \(p\) vertex. The printed zero-output disjunct for \(Z=\varnothing\) reduces to \(p\), so it incorrectly accepts the edge endpoint, whose actual output is \(1\).



### Finding and scope

The translation formula is incomplete. Proposition 2.4’s existence statement is not disproved.



### Proposed correction

Add total degree at most \(|Z|\), or include zero counts for all other finite previous-layer types. Positive count classes already exhaust \(|Z|\) neighbors, so the added condition excludes every extra type.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: The proposed decomposition misses inter-fibre connections

Assessment: supported; impact: minor



Source: Current arXiv v2 Proposition 5.7(1), PDF p.8; proof, PDF pp.25–26



### Source claim (paraphrase)

Proposition 5.7’s proof joins each equal-parent edge bag only to its endpoint vertex bags and calls the resulting structure a tree decomposition.



### Analysis

For triangle \(a,b,c\), let \(\operatorname{dep}(a)=\bot\), \(\operatorname{dep}(b)=\operatorname{dep}(c)=a\). The admissible rank-one map gives bags \[\{a\},\{a,b\},\{a,c\},\{a,b,c\}\]. The listed edges connect the latter three in a path but isolate \(\{a\}\); bags containing \(a\) are disconnected. The triangle still has treewidth \(2\), satisfying the stated inequality.



### Finding and scope

The construction is not a tree decomposition as written. The inequality and hierarchy are not contradicted.



### Proposed correction

Connect a representative bag from each nonroot parent-fibre component to its parent bag; connect root components in a tree. Well-founded parent levels prevent cycles and no bag enlarges. In the triangle, one link to the isolated parent bag suffices.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
