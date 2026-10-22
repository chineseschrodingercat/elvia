# Decomposing Interventional Causality into Synergistic, Redundant, and Unique Components



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



A fully supported binary causal model makes MACE decrease when interventions enlarge, refuting unrestricted monotonicity/nonnegativity claims. Plotting can then omit or clip signed contributions.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: Enlarging the intervention set can reduce MACE, invalidating the unrestricted nonnegativity theorem

Assessment: supported; impact: major



Source: Section 3.2, Lemma 1 and Theorem 2, PDF p. 5; proof, PDF p. 6; Appendix A.1, Lemma 2, PDF p. 13.



### Source claim (paraphrase)

Paraphrase of the complete relevant claims: Appendix A.1, Lemma 2 (p. 13), asserts that \(A\subseteq B\) implies \(m(A)\leq m(B)\). Section 3.2, Lemma 1 (p. 5), asserts monotonicity of \(r\) on the redundancy order. Theorem 2 (p. 5; proof on p. 6) then asserts \(C(\alpha;Y)\geq0\) for all antichains. No assumption of independent source variables or monotonicity of the actual interventional response ranges is attached to these claims. The paper explicitly discusses correlated dynamical contexts in Section 4.2.



### Analysis

Let \(A,H\) be independent fair bits, \(E\sim\operatorname{Bernoulli}(1/4)\) independent, \(B=H\oplus E\), \(C=H\), and \(Y=A\oplus B\oplus C\). All observable source assignments have positive probability and no source causes another. Under \(\operatorname{do}(A)\), \(Y=A\oplus E\), giving \(\operatorname{MACE}(A)=1/2\). Under \(\operatorname{do}(A,B)\), \(C\) remains fair and \(Y\) is fair for every imposed assignment, giving \(\operatorname{MACE}(AB)=0\).

Adding interventions replaces mechanisms; the resulting response distributions need not contain those of the smaller intervention family. The decrease contradicts unrestricted intervention monotonicity, and the stated inversion produces a negative partial contribution \(-1/2\). Correlated contexts are permitted by the source, so independence cannot be silently added to remove the example.

For an explicit two-source decomposition, choose analyzed sources \(\{A,B\}\) while \(C\) remains background. Then \(m(A)=1/2\), \(m(B)=0\), \(m(AB)=0\) and the minimum redundancy is \(0\). Möbius reconstruction gives the joint-only atom \(m(AB)-\max\{m(A),m(B)\}=-1/2\). Every source assignment is supported, so this does not rely on unspecified off-support responses.



### Finding and scope

The unrestricted monotonicity and universal nonnegativity claims are false. The decomposition can still be studied with an explicit monotonicity assumption or a separately defined envelope; those changes alter its scope or meaning.



### Proposed correction

State and justify a monotonicity assumption for the intervention-effect set function, or define a monotone-envelope variant and disclose its changed scientific meaning. Neither is a replacement proof of the unrestricted original claim.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 2: The cellular-automaton plot omits signed contributions produced by the decomposition

Assessment: supported; impact: minor



Source: Section 4.2, PDF p. 7; Figure 3, PDF p. 8; released notebook cells 5–6.



### Source claim (paraphrase)

Section 4.2, PDF p. 7, and Figure 3, PDF p. 8, compare cellular-automaton contexts. The authors' notebook, zero-based cells \(5\)–\(6\), implements simulation and plotting with a positive-only atom-selection threshold and nonnegative display limits.



### Analysis

Atoms never exceeding \(0.01\) are omitted by the positive-only mask, while display limits \([0,1.1]\) clip negative contributions of retained atoms. Once signed contributions are possible, those operations can hide them. The released settings of \(1000\) steps with \(0.05\) burn-in also differ from the stated \(10000\) steps with the first \(500\) removed. No new cellular-automaton simulation or negative-context frequency is claimed.



### Finding and scope

This is a supported local finding within the stated source/formulation scope. Its effect on the paper's aggregate experimental results remains unmeasured.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
