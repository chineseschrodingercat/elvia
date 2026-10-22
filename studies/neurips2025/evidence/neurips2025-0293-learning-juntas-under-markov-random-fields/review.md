# Learning Juntas under Markov Random Fields



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The unknown-graph preprocessing remark drops a necessary interaction-strength dependence. A two-variable smoothed MRF family proves the exact-recovery obstruction; the main supplied-graph junta theorem remains outside that counterexample.



## Scope

Rapid, claim-focused reading of the latest applicable author-paper and resource passages. Direct mathematical or static-source reasoning is stated below. No author program, retained verifier, model inference or benchmark was executed.



## Problem 1: The unknown-graph preprocessing claim omits interaction strength

Assessment: supported; impact: minor



Source: Proceedings Remark 1.4 and Theorem 1.3, PDF p.3; Definition 1.2, p.2; current arXiv v 1 corresponding passages



### Source claim (paraphrase)

Remark 1.4 proposes exact recovery of an unknown MRF dependency graph with complexity \(\operatorname{poly}(n^t,2^\lambda)\), then applies the known-graph junta algorithm. No lower bound on nonzero interactions is included.



### Analysis

Let \(n=2,\lambda=1,\sigma=1/4\), draw \(\alpha_i\) independently uniformly on \([-1/4,1/4]\), and set \[P_{\eta,\alpha}(x)\propto e^{\eta x_1x_2}(1+\alpha_1)^{x_1}(1+\alpha_2)^{x_2},\qquad0\leq\eta\leq1.\] This is positive, order at most two, degree at most one, and has unperturbed derivative coefficient norms at most \(1\). Its minimal graph is empty at \(\eta=0\), but has an edge for every \(\eta>0\), since its odds ratio is \(e^\eta\). The prescribed external-field smoothing does not change that ratio.

Writing \(F(\eta)=\log Z_\alpha(\eta)\), the sufficient statistic \(x_1x_2\) is binary, so \(F^{\prime\prime}\leq1/4\) and \(D_{\rm KL}(P_{0,\alpha}\Vert P_{\eta,\alpha})\leq\eta^2/8\). For any sample budget \(N\geq1\), choose \(\eta=N^{-1/2}\). Product-law Pinsker gives total variation at most \(1/4\), even if the smoothing coordinates are revealed. Any exact-graph test then has equal-prior average error at least \(3/8\), preventing success \(2/3\) on both alternatives with a budget independent of interaction strength.

This concerns exact minimal-graph recovery. A valid supergraph is a different target; the complete graph is always valid but can destroy the degree-dependent runtime. The formal junta theorem explicitly receives a graph, and the calculation does not refute that known-graph guarantee or rule out a different robust preprocessing method.



### Finding and scope

The stated strength-independent exact-recovery preprocessing is unsupported. Keep the supplied-graph theorem separate from this extension.



### Proposed correction

Retain the known-graph theorem, and restrict the cited exact-structure-learning pipeline to the identifiability/nondegeneracy assumptions of the chosen structure learner, including its interaction-strength-dependent sample cost.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- Mathematical counterexamples and source discrepancies do not remeasure published experiments; historical execution results were not rerun.
