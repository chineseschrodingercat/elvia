# Test-Time Adaptation by Causal Trimming



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The local trimming proposition does not automatically cover history-averaged prototypes, and nullspace removal can erase an arbitrary direction. The stated local correction result remains intact.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Averaged prototypes require a separate history condition

Assessment: not_issue; impact: no_issue_found



Source: Sections 4.3–5, pp. 4–6, Eqs. (2)–(5); Appendix A.1/A.3.



### Source claim (paraphrase)

The local trimming proposition reasons about the current boundary \(q\); deployment can instead use an averaged boundary \(\bar q\).



### Analysis

With \(q=(1,10,1)\), prior removed direction \((0,1,1)/\sqrt2\), current removed direction \(e_2\), and current feature \((1,-1,1)\), the local corrected margin is \(2\). The history-averaged boundary \((1,2.25,-1.75)\) instead gives margin \(-0.75\). The local conditions hold, but averaging adds an uncontrolled term.

For the deployed history rule, the signed margin is \(m_{\rm local}+y\hat z^\top(\bar q-q)\). The additional condition \(|\hat z^\top(\bar q-q)|<m_{\rm local}\) suffices for a positive margin. This explains the local theorem’s coverage; it does not amend a disproved theorem.



### Finding and scope

The local proposition survives; it does not alone guarantee the deployed history rule.



## Problem 2: Removing beyond positive rank can erase an arbitrary null direction

Assessment: supported; impact: minor



Source: Sections 4.1–4.2, p. 4, Eq. (1); Section 6, p. 7; methods/tact_utils.py lines 214–217.



### Source claim (paraphrase)

The method removes the leading \(m\) covariance eigenvectors as augmentation-varying directions.



### Analysis

For covariance \(\operatorname{diag}(0,2,0)\), only \(e_2\) varies. Removing two directions permits ordered bases \((e_2,e_1,e_3)\) or \((e_2,e_3,e_1)\), which respectively erase or preserve causal feature \(e_1\). Nullspace choices do not encode observed augmentation variation.



### Finding and scope

The removal count needs a rank convention. This does not prove that published selected settings encounter the ambiguity or that all positive-variance directions are noncausal.



### Proposed correction

Cap removal by a declared numerical positive-rank threshold. If a positive-eigenvalue tie is split, specify a subspace-level or invariant tie convention.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
