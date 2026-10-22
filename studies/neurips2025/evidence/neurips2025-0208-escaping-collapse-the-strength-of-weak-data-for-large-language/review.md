# Escaping Collapse: The Strength of Weak Data for Large Language Model Training



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The literal response-level filter and ordinary-set convention contradict the prompt-level partition and probability estimate used by the main convergence proof. A separate first-success boundary is missing from the induction. An explicitly specified trial-level repair recovers the intended rate without contradicting the LLM experiments.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: The response-level rejection rule does not give the required prompt partition

Assessment: supported; impact: major



Source: Definition 2 and Definition 4; Algorithm 2; Appendix A.1 and Lemma 10; current arXiv:2502.08924v2, PDF pp.5–7 and 19–20



### Source claim (paraphrase)

Definition 2 rejects a prompt when an individual response fails, while Lemma 10 assumes rejection only after all \(k\) independent trials fail. Appendix A.1 also uses ordinary sets of response pairs.



### Analysis

Use four prompts \((a,b,c,d)\), binary correctness, \(\alpha=1\), \(\beta=1/2\), a perfect filter and an initially wrong model. On every nonempty prompt subset, let the weak labeler correctly label the first \(\lceil|U|/2\rceil\) prompts. The first weak round correctly labels \(a,b\); the next labels \(c\) correctly with weight \(1/2\), after its earlier wrong weight \(1/4\), giving \(Q_2(c)=2/3\). At the third round, mixed correct/incorrect responses occur with probability \(1-(2/3)^k-(1/3)^k>0\). The written filter then places \(c\) in both accepted and rejected prompt sets.

For an exact Lemma 10 probability violation, use two prompts and \(\beta=\gamma=1/2\), \(T=3\), \(k=12\). The required lower bound on \(k\) is about \(11.5615\). After the first weak round, one prompt is always correct. Ordinary-set deduplication leaves one pair, accepted with probability \(1/2\), so the lemma’s event fails with probability at least \(1/2>1/T\). Keeping occurrences but retaining the any-failure rule instead gives rejection probability \(1-2^{-12}\), also inconsistent with an all-failure estimate.



### Finding and scope

The partition and probability proof do not follow from the literal specification. This is not a direct counterexample to every parameter condition of the final quality theorem; its intended all-trials-fail interpretation is coherent.



### Proposed correction

Keep independent trial identities until filtering, reject a prompt only when no trial is accepted, and retain exactly one accepted response per prompt per round. Then conditional rejection probability is at most \((1-\beta\gamma)^k\), and a union bound gives \(nT e^{-\beta\gamma k}\).

A proposed correction is described; author adoption is not established.



## Problem 2: The induction needs the first correct weak-label round

Assessment: supported; impact: minor



Source: Lemma 11(d) and induction for part (a); current arXiv:2502.08924v2, PDF pp.20–23



### Source claim (paraphrase)

The proof invokes a positive-quality lower bound stated for \(r<t\) when a prompt can first receive its correct weak label at \(r=t\).



### Analysis

Under the explicitly repaired trial-level routing, a newly correct prompt has \(Q_t(x)=\lambda_t/\sum_{s\le t}\lambda_s\). Prior shrinkage gives \(\lambda_s\le(1-\beta)^{t-s}\lambda_t\), so \[Q_t(x)\ge\frac{1}{\sum_{j=0}^{t-1}(1-\beta)^j}=\frac{\beta}{1-(1-\beta)^t}\ge\beta.\] This supplies the omitted first-success case without applying the earlier premise beyond its domain. Previously correct prompts only receive correct accepted responses, so their quality cannot decrease.



### Finding and scope

The written induction omits a necessary boundary invariant. Its repair, together with the explicit filtering repair, supports the intended convergence rate; empirical training is not reproduced.



### Proposed correction

Track the first correct weak-label round, retain the displayed boundary bound, and then propagate monotone correctness. With \(R=\lceil\log(2/\epsilon)/\beta\rceil\), enough later accepted rounds leave at most \(\epsilon/2\) residual error on the already corrected prompts and at most \(\epsilon/2\) uncorrected mass.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.
