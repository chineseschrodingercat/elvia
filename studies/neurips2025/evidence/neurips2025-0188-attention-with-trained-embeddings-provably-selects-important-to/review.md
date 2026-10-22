# Attention with Trained Embeddings Provably Selects Important Tokens



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The implicit-bias proof does not justify preservation of tied argmax sets, and the multiclass extension omits classifier Gram interactions. The older all-constraints-tight formula has already been removed from the current main paper and does not count as a current scientific error.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Directional convergence does not preserve tied argmax sets

Assessment: supported; impact: major



Source: Lemma C.6, PDF pp.31–34, especially p.32; Lemma C.5, p.29; Eqs.(10)–(12)



### Source claim (paraphrase)

The proof infers finite-time selection equivalence to the limiting direction and applies fixed-gap derivative bounds.



### Analysis

With embeddings \(e_1,e_2,e_3\), let \(p_R=(R+\sqrt R,R,0)\). Its normalized direction tends to \((1,1,0)/\sqrt2\), but every finite argmax is \(\{1\}\), while the limiting argmax is \(\{1,2\}\). The normalized first/second gap is \[\sqrt R/\sqrt{(R+\sqrt R)^2+R^2}\to0\], so no fixed positive gap follows. Separation between distinct limiting groups does not separate members tied within one group. Relevant-token membership or distinct finite-time scores likewise does not exclude limiting ties.



### Finding and scope

The tied-limit proof step for the central max-margin characterization is unsupported. This algebraic curve is not an actual gradient-flow trajectory or a counterexample satisfying the theorem’s random event; the theorem itself remains unrefuted.



### Proposed correction

Unique limiting maximizers with gap \(m>0\) and embedding-difference bound \(D\) preserve selection whenever \(\|u_t-u\|<m/(2D)\). That adds a hypothesis; the full flow needs a proof of strictness or an argument handling tied faces and shrinking gaps.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: Multiclass overlaps depend on the classifier Gram matrix

Assessment: supported; impact: major



Source: Section 4.3, Eq.(14), PDF p.7; Appendix E, p.39



### Source claim (paraphrase)

The printed leading overlap retains only class coefficient \(c_{sk}\), without a stated orthogonality condition on output classifiers.



### Analysis

At uniform initial probabilities, \(E_s^1=E_s^0+\eta_0\sum_\ell c_{s\ell}v_\ell\), so \((E_s^1)^\top v_k=(E_s^0)^\top v_k+\eta_0\sum_\ell c_{s\ell}v_\ell^\top v_k\). Take two one-token examples \(a,b\) with labels \(1,2\), and equal unit classifiers \(v_1=v_2=e_3\). Both logits always agree, the loss is identically \(\log2\), and every embedding gradient is zero. The printed class-one term for token \(a\) is instead \(\eta_0/4>0\). Gaussian initial overlap vanishes with dimension, while this omitted leading discrepancy does not.



### Finding and scope

The general multiclass extension lacks a necessary Gram condition. This does not refute the separately formulated binary theorem or empirical correlations for the actual learned classifiers.



### Proposed correction

Retain the full Gram expression. If \(G=I+\Delta\), the omitted contribution is bounded by \(\eta_0\|c_s\|_1\max_\ell|\Delta_{\ell k}|\); an explicit asymptotic Gram control and initial-remainder analysis can justify the simpler leading formula.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: The all-constraints-tight formula is already superseded

Assessment: not_issue; impact: minor



Source: Current Lemma 4.2 and Appendix C.2, PDF pp.5,26; historical arXiv v1 and separate older supplement



### Source claim (paraphrase)

The old version gave \(\widehat p=M^\dagger\mathbf1\), assuming every margin inequality is tight. The current main paper asserts uniqueness only.



### Analysis

For differences \(e_1-e_2,e_2-e_3,e_1-e_3\), the third row is the sum of the first two. Requiring all three margins \(1\) is impossible, while \(p=(1,0,-1)\) is optimal with margins \((1,1,2)\) and KKT multipliers \((1,1,0)\). The old pseudoinverse gives \((2/3,0,-2/3)\), violating the first two inequalities. Current proceedings and later arXiv revisions remove the pseudoinverse assertion. A separately distributed older supplement still contains it, so its derivation must be read as superseded.



### Finding and scope

Known historical correction, not a current-main-paper error; only the material-version discrepancy remains.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
