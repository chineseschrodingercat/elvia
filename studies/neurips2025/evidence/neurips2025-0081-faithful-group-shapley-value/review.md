# Faithful Group Shapley Value



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The second-order stability rate omits a divergent harmonic factor, while a public benchmark estimator omits normalization constants. Conditional FGSV faithfulness and the definition itself are not refuted.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: The strict stability rate omits a logarithmic factor

Assessment: supported; impact: minor



Source: Proceedings Proposition 2, p. 7; separate supplement §A.6, p. 21.



### Source claim (paraphrase)

Proposition 2 gives a constant-factor second-order SGD rate under the stated polynomial step, batch and horizon scalings.



### Analysis

Let the common background records have feature zero, and choose four distinct added records with features \((1,1,0,0)\). The four size-\(N\) datasets contain respectively \(k=2,1,1,0\) unit-feature records. Use scalar loss \(\ell(w;z)=-a(z)w\), start \(w_0=0\), step \(N^{-1/4}/t\), batch size \(N\) and horizon \(N\). A bounded smooth utility can equal \(w^2\) on \([-2,2]\), extend as \(8-(4-|w|)^2\) for \(2<|w|<4\), and equal \(8\) outside; it has bounded derivative and Lipschitz derivative. Every reached iterate is below \(2\). Without replacement, \(w_T(k)=kN^{-5/4}H_N\), where \(H_N=\sum_{t\leq N}1/t\). Thus the four-utility difference is \(2N^{-5/2}H_N^2\). Independent with-replacement batches give \(2N^{-5/2}(H_N^2-H_N^{(2)}/N)\), with \(H_N^{(2)}=\sum_{t\leq N}t^{-2}\). Scaling by \(N^{5/2}\) diverges, contradicting the strict power-only bound under the stated regularity. This does not establish an optimal alternative rate.



### Finding and scope

The exponent-only bound needs qualification. This does not refute conditional faithfulness or prove an optimal alternative rate.



### Proposed correction

Retain the supplement’s capped exponent \(\nu_{\rm eff}=\min\{2\tau_1+\tau_2-1/2,1/2\}\) and its two-term bound, or explicitly account for the logarithmic factors under the example’s scaling.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: The benchmark estimator omits normalization factors

Assessment: supported; impact: minor



Source: Lemma 1/Eq. (8), p. 4; Theorem 2/Eq. (9), pp. 4–5; exp1_benchmark/estimators.py lines 343–405.



### Source claim (paraphrase)

The benchmark path estimates the defined FGSV by combining small- and large-cardinality branches.



### Analysis

For eight players and additive utility \(U(S)=|S\cap S_0|/8\), \(|S_0|=4\), exact group value is \(1/2\). The benchmark path omits the small-branch factor \(n/[s(n-s)]\) and large-branch factor \(n/(n-1)\), giving limiting value \(127/224\approx0.566964\). Additivity removes approximation remainder and within-stratum variation, so increasing samples does not remove that normalization bias. Other release paths partly include the factors.



### Finding and scope

The named estimator does not converge to the defined value on this additive control. Published benchmark exposure is unresolved.



### Proposed correction

Insert the missing cardinality factors while preserving the existing central-difference division by two. This restores this estimator’s algebraic correspondence, not a new benchmark result.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
