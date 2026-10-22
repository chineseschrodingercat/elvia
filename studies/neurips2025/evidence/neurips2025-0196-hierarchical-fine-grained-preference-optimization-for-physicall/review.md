# Hierarchical Fine-grained Preference Optimization for Physically Plausible Video Generation



Preliminary assessment: No Issue Found

Independent scientific review: pending. Author adoption: not requested.



The diversity sentence has an inherited distance/similarity naming ambiguity. The cited DEITA source uses similarity and correctly excludes duplicates under that interpretation. No substantive PhysHPO selection failure is established.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Distance/similarity terminology does not establish a selection failure

Assessment: not_issue; impact: minor



Source: Section 4.3, PDF p.5; cited DEITA compute_distance/filter



### Source claim (paraphrase)

The sentence calls \(d\) nearest-neighbor cosine distance and accepts \(d<0.9\).



### Analysis

Literal standard distance \(1-\cos\) accepts a duplicate of \(e_1\) with distance \(0\), rejecting \(e_2\) and \(-e_1\) at distances \(1,2\). However, the cited DEITA implementation names a normalized dot product “distance” and rejects similarity above its threshold. It therefore excludes the duplicate and supplies a plausible inherited convention. Similarity \(c<0.9\) is equivalent to nearest distance \(d_{\min}>0.1\), not \(d_{\min}>0.9\); DEITA’s equality-retaining convention instead uses \(c\le0.9\).



### Finding and scope

Scope/terminology clarification only. The unavailable PhysHPO selector is not shown to use the literal reversed interpretation; no actual dataset or benchmark failure follows.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
