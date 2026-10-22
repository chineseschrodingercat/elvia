# AutoData: A Multi-Agent System for Open Web Data Collection



Preliminary assessment: Needs Evidence

Independent scientific review: pending. Author adoption: not requested.



Selected F1/precision/recall triples violate a rounding-safe bound for common-weight aggregation. The paper does not exclude different populations or weights, so the empirical judgment remains unresolved.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Reported metric triples need their aggregation reconciled

Assessment: needs_evidence; impact: needs_evidence



Source: Tables 1, 5 and 6; Appendix D.2 and D.7



### Source claim (paraphrase)

The paper describes ordinary information-extraction F1, precision and recall, but does not fully specify column populations, weights or undefined-case treatment.



### Analysis

For ordinary per-unit F1 \(h(p,r)=2pr/(p+r)\), the Hessian quadratic form is \(-4(ra-pb)^2/(p+r)^3\le0\). Thus common nonnegative weights imply \(\bar F\le h(\bar P,\bar R)\), including hierarchical common-weight macro averages. Table 1 reports AutoAgent–Stock \((F,P,R)=(73.54,94.37,52.71)\) percent. Even two-decimal rounding requires \(73.535\le h(94.375,52.715)=67.64536\), impossible. However different column weights or populations can violate that necessary bound without an arithmetic error. Mere inequality between macro F1 and the harmonic mean is not itself a defect.



### Finding and scope

The row is inconsistent under a common-weight interpretation, but the actual aggregation remains unresolved. No replacement F1 or changed method ranking follows without scoring code and per-unit data.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
