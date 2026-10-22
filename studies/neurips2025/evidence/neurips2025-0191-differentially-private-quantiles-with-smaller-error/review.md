# Differentially Private Quantiles with Smaller Error



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Current integer counting noise fails the suffix-shift contract used to connect the implementation to the privacy proof. Historical indexing bugs are already fixed. Shared counting randomness and substitute-delta conversion are separate release/protocol issues; no final-output privacy violation is established.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Signed integer tree noise has a forbidden suffix-shift parity

Assessment: supported; impact: minor



Source: Lemma 3.1 Eq.(2), latest PDF p.5; current k_ary_tree_noise.py, prefix_noise_terms



### Source claim (paraphrase)

The proof interface requires positive output probability to survive every unit suffix shift; the experimental implementation combines integer geometric-difference noise with signs.



### Analysis

At supported \(m=k=2\), height \(1\), independent integer nodes \(Z_0,Z_1,Z_2\) give \(N_1=Z_0+Z_1-Z_2\), \(N_2=Z_0+Z_1+Z_2\). Thus \(N_2-N_1=2Z_2\) is even. At ranks \((10000,20000)\), output equal to the ranks has positive probability because all nodes can be zero, while shifting the second output by \(1\) has zero probability. No finite exponential ratio can bound positive by zero. The same adjacent-difference parity appears in the height-one \(m=10\) experimental choice. Increased variance or widely separated ranks cannot repair support.



### Finding and scope

The current discrete module does not instantiate the required counting law. The continuous construction and existence lemma are not disproved; later randomized slice/quantile release may lose the internal parity information, so final-output nonprivacy is not established.



### Proposed correction

An ordinary dyadic-prefix mechanism with independently noised interval counts can satisfy the contract: a unit suffix shift changes one stream increment and at most \(T=\lceil\log_2m\rceil+1\) interval queries. Node mass proportional to \(e^{-\epsilon|z|/T}\) bounds the joint likelihood ratio by \(e^\epsilon\). This conservative alternative changes noise constants and needs full-pipeline integration/review.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: The historical node-alias/prefix defect is already fixed

Assessment: not_issue; impact: minor



Source: Conference supplement k_ary_tree_noise.py; author commits of 10 September 2026; current prefix_noise_terms



### Source claim (paraphrase)

The conference source reused sibling-index cache keys across parents and stopped at the first rather than last leaf boundary.



### Analysis

At \(m=8,k=2\), its coefficients force \(-N_1+2N_3-2N_4-N_5+2N_6=0\), whereas suffix shift \((0,1,1,1,1,1,1,1)\) changes that expression by \(1\). Current code uses parent-dependent absolute node keys and stops at rem equal to block size minus one, removing this rational support identity. These local fixes do not remove the separate integer parity above.



### Finding and scope

Known historical defect, cleared in the current source. Neither a historical benchmark change nor complete current privacy is inferred.



## Problem 3: Nominal repetitions condition on one counting-noise draw

Assessment: supported; impact: minor



Source: Section 6/Figure 1, latest PDF pp.9–10; current real_data_eps1.ipynb, cell 19; persistent tree cache



### Source claim (paraphrase)

One SliceQuantile object is constructed outside the \(200\)-repetition loop and its tree is not reset between queries.



### Analysis

Let \(Z\) be shared counting noise, \(Q_i\) random queries and \(E_i\) fresh single-quantile noise. Even if draws are conditionally independent, for loss \(Y_i=f(Q_i,Z,E_i)\), variance of the mean is \(\mathbb E[\operatorname{Var}(Y_i\mid Z)]/R+\operatorname{Var}(\mathbb E[Y_i\mid Z])\). Bootstrapping observations from one fixed \(Z\) cannot estimate the between-counting-noise term. New outer seeds do not clear an existing cache. Final exponential-mechanism outputs can still differ, so this is not a cached-final-answer claim.



### Finding and scope

The replication scheme supports conditional rather than fully randomized uncertainty unless the between-noise term vanishes. Numeric undercoverage or a ranking reversal is not established.



### Proposed correction

For independent complete-mechanism repetitions, create/reset the tree with a continuing nonreplayed RNG stream, while optionally pairing query seeds separately. State which sources of randomness the uncertainty covers.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 4: Substitute delta is loosened instead of tightened

Assessment: supported; impact: minor



Source: Theorem 4.2, latest PDF p.7; current slice_quantile.py, is_delta_approximate_DP



### Source claim (paraphrase)

The theorem gives final failure bound \(F\delta_{\rm int}\), \(F=1+e^{\epsilon_{\rm CC}+2\epsilon_{\rm EM}}\); source multiplies the requested delta by \(F\) before the internal bound.



### Analysis

At total epsilon \(1\), split \(0.5\), substitute adjacency, the correctly calibrated epsilon components are \(1/4,1/6\). Thus \(F=1+e^{7/12}=2.7920018257\). Requested \(10^{-16}\) needs internal \(10^{-16}/F=3.5816595491\times10^{-17}\), but source forwards \(F10^{-16}\), yielding only the conditional theorem bound \(F^2\,10^{-16}=7.7952741945\times10^{-16}\). No outer division in the inspected path cancels it.



### Finding and scope

The certification argument does not establish the requested substitute parameter. This is not a lower bound on actual final-output privacy loss, and the separate counting-contract issue remains.



### Proposed correction

Divide the requested final delta by the theorem’s factor once, keeping internal and target names distinct. This fixes accounting direction without proving privacy of the complete implementation.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
