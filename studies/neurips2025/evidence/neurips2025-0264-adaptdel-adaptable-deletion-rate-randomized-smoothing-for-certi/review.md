# AdaptDel: Adaptable Deletion Rate Randomized Smoothing for Certified Robustness



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Released upper-bound and edit-search routines admit false certificates. A separate normalization proof gap can be repaired while preserving the final printed bounds.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Released upper bound can certify a genuine one-edit flip

Assessment: supported; impact: major



Source: Lemma 6, Appendix A, PDF p.17; var_del_certs.py and var_del_len_certs.py, compute_upperbound



### Source claim (paraphrase)

The printed upper relaxation rounds its partial partition upward and includes target outside-event mass. The current repository rounds downward and omits that mass; the conference supplement also rounds downward and uses the wrong residual rate.

The current author release and conference supplement route the supplied edit/lecuyer certification configuration through these bound comparisons; the guarantee is preservation of the smoothed class throughout the returned edit ball.



### Analysis

For the official supplement, let \(x=\texttt{cdefghija}\), neighbor \(\bar x=\texttt{cdefghijb}\), and deletion rate \(p=q=0.9\). Define class A if a occurs, or the output is one of \(\emptyset,\texttt{c},\texttt{d},\texttt{cd},\texttt{ce},\texttt{cf},\texttt{cg}\). Conditional common-token mass is \(s_0=0.9^8+2(0.1)0.9^7+4(0.1)^2 0.9^6=0.54738423\). Thus A probability changes from \(0.592645807\) to \(0.492645807\), flipping the majority after one substitution. Valid conservative inputs \((0.59,0.41)\) nevertheless give released bounds \(L=0.47829690>U=0.47821403\), falsely passing. The error persists at equal rates, independently of the supplement’s additional wrong-rate term. For identical input ab at rate \(0.8\), event “output a” has probability \(0.16\), while the current upper routine returns approximately \(0.04\).



### Finding and scope

The released certifier is not generally sound, including a conference-supplement path. This does not refute the printed final bounds or establish which original benchmark certificates change; those require their original counts and run provenance.



### Proposed correction

Use an upper ceiling and the target residual mass \(1-q^{n-N}\), or the normalized fractional common-subsequence envelope. Re-certify affected outputs after integration.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Edit search excludes pure-deletion boundaries

Assessment: supported; impact: major



Source: Section 3.4, PDF p.6; var_del_certs.py, search_worst_case_bound, lines 211–218



### Source claim (paraphrase)

The implementation enumerates substitutions and insertions, computes deletions as the remaining radius, and skips deletion count at least the radius.



### Analysis

Pure deletion \((n_{\rm sub},n_{\rm ins},n_{\rm del})=(0,0,r)\) is always skipped. For deletion-only attacks it is the only candidate, leaving the initialized margin at infinity. Take input ab, deletion rate \(0.1\), and class A iff b occurs. Its smoothed A probability is \(0.9\), but deleting b gives nonempty neighbor a with A probability zero. Conservative inputs \((0.89,0.11)\) are valid; the search can return radius \(2\) without evaluating the one-deletion flip.



### Finding and scope

The release enumeration does not cover its claimed threat set. This establishes a general interface failure, without measuring the frequency of inflated full-edit radii in the published data.



### Proposed correction

Admit the pure-deletion endpoint, enforce feasible operation counts, distinguish an empty search from a verified margin, and explicitly handle radius zero.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: Common-subsequence normalization is lost in the proof

Assessment: supported; impact: minor



Source: Appendix A, Eqs.(9) and (15), PDF pp.15 and 17; Theorem 4 proof p.19



### Source claim (paraphrase)

The proof treats normalized common-subsequence mass as though it were unconditional full-input probability, omitting the outside-deletion factor.



### Analysis

Write \(a=p^{m-N},b=q^{n-N}\). Actual class masses satisfy \(\mu=aT_p+r_x\), with \(0\leq r_x\leq1-a\), and target mass \(bT_q+r_{\bar x}\). Thus normalized common mass lies between \(\ell=\max(0,(\mu-1+a)/a)\) and \(u=\min(1,\mu/a)\). For input ab, neighbor ac and rate \(0.8\), event “no b” has source probability \(0.8\) but normalized common mass \(1\), refuting the printed superset claim. Nevertheless, fractional likelihood-ratio envelopes give valid bounds \(bG_-(\ell)\) and \(1-b+bG_+(u)\). Convexity of \(G_-\), concavity of \(G_+\), and the paper’s extra floor/ceiling slack show that its final printed bounds are conservative relative to these valid bounds.



### Finding and scope

The intermediate derivation needs repair, but this does not establish false final Lemmas 3 or 6. The general normalized probability argument preserves their final bounds on nondegenerate rates.



### Proposed correction

Keep the outside-event factors, optimize normalized common masks with fractional final groups, and finish certification by comparing target-class lower and competitor upper bounds at the target input.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
