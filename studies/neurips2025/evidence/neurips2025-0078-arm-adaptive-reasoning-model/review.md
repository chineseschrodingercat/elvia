# ARM: Adaptive Reasoning Model



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The public actor’s reduction depends on microbatch partition and differs from the per-question loss. The efficiency table compares requested budgets with unequal achieved token use.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Microbatch averaging differs from equal-question weighting

Assessment: supported; impact: minor



Source: Eq. (6), p. 5; Appendix A.1/Eq. (7), p. 14; core_algos.py lines 302–333 and dp_actor.py line 272.



### Source claim (paraphrase)

Equations (6)–(7) define \(L=Q^{-1}\sum_qN_q^{-1}\sum_{i,k}\ell_{qik}\), where \(N_q\) is the total response-token count for question \(q\).



### Analysis

The actor instead uses \[\sum_b(m_b/m)\,N_b^{-1}\sum_{(q,i,k)\in b}\ell_{qik}\], where \(m_b\) is the number of response sequences in microbatch \(b\), \(m\) the total response count, and \(N_b\) its valid response-token count. Unequal question lengths make these coefficients depend on partition. Two questions, each with eight responses of lengths \(32\) and \(288\), give loss \(-0.1707128\) in one microbatch versus \(-0.1260209\) in two question microbatches, with identical valid autoregressive observations. This differs from the written equal-question loss \(Q^{-1}\sum_qN_q^{-1}\sum_{i,k}\ell_{qik}\), where \(N_q\) is fixed across the complete response group.



### Finding and scope

The reduction is not the written equal-question objective. No resulting benchmark delta is measured.



### Proposed correction

Compute each full-question denominator before splitting, retain question identity, and weight each valid token by \(1/(QN_q)\). Summing those weighted losses is partition invariant.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Requested budgets do not establish matched achieved computation

Assessment: supported; impact: minor



Source: Appendix K.3, pp. 23–24, Table 12 and interpretation.



### Source claim (paraphrase)

Appendix K.3 interprets Table 12 as a comparison at similar token usage after matching requested L1 budgets to ARM averages.



### Analysis

The table’s achieved token totals are \(8090\) versus \(6597\) for pass-at-one and \(8518\) versus \(6618\) for majority-at-eight. Under equal-dataset averaging, ARM uses \(22.63\%\) and \(28.71\%\) more tokens. Its mean accuracy is higher, but some tasks regress; the table does not identify the accuracy ordering at truly matched achieved tokens.



### Finding and scope

The efficiency interpretation must distinguish target budget from actual work. No counterfactual matched-token ranking is inferred.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
