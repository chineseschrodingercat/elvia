# A Compressive-Expressive Communication Framework for Compositional Representations



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The arbitrary-encoder complexity claim and contrastive upper bound have direct counting/algebra counterexamples. Coverage, prefix inclusion, released PDM weighting and uniqueness statements require narrower conditions.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Coverage needs growth of every relevant fibre

Assessment: supported; impact: minor



Source: Appendix D, Theorem D.3, p. 28; Remark D.4, pp. 28–29.



### Source claim (paraphrase)

Appendix D extends coverage to arbitrary coordinate subsets and factor domains, beyond its finite union bound.



### Analysis

Full-tuple coverage fails for a proper training subset when \(k=n\). Even with \(k<n\), domains \([N]\times[2]\), sample fraction \(1/2\) and \(k=1\) have probability \(2^N/\binom{2N}{N}\to0\) of seeing every first-coordinate value. There are only two completions per such value, so overall dataset growth does not make its fibre large.



### Finding and scope

The finite avoidance/union bound survives; the general asymptotic coverage implication needs fibre assumptions.



### Proposed correction

For a coordinate set \(A\), use fibre size \(M/N_A\) and exact avoidance probability \(\binom{M-M/N_A}{m}/\binom{M}{m}\). Require the resulting union bound to vanish rather than only total domain size to grow.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: A final constraint can exclude a prefix allowed by the average constraint

Assessment: supported; impact: minor



Source: Appendix E, pp. 29–30, Proposition E.1(1).



### Source claim (paraphrase)

Proposition E.1 claims prefix-set inclusion for arbitrary positive average and final reconstruction thresholds.



### Analysis

Use one input, teacher message \(00\), and two-bit alternatives. Both one-bit receiver outputs are \(0\); complete messages \(00,01\) reconstruct \(0\), while \(10,11\) reconstruct \(0.15\). Sender \(10\) has average discrepancy \(0.075<0.1\), yet its prefix \(1\) has no completion below final threshold \(0.1\).



### Finding and scope

Arbitrary-threshold prefix inclusion is false. Nonnegative loss still bounds final discrepancy by the number of positions times the average.



### Proposed correction

Use the valid relation that average threshold \(M\) implies final threshold \(CM\) for message length \(C\), or impose additional receiver/threshold structure before asserting stronger inclusion.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: Codeword length is not the description of an arbitrary encoder

Assessment: supported; impact: major



Source: Definition F.2 and Eqs. (10)–(12), p. 31; Proposition F.3.



### Source claim (paraphrase)

Equation (11) assigns encoding complexity approximately \(\sum_i\log_2N_i\), while Definition F.2 permits arbitrary injective factor encoders of minimal codeword length.



### Analysis

For two factors of size \(N=2^m\), a minimal-length injective encoder is a permutation of \(N\) codewords. There are \((N!)^2\) compositional maps. Counting descriptions forces typical map complexity of order \(N\log N\), not the \(2\log_2N\) bits in one encoded factor pair. A half-domain containing each factor value can still distinguish the maps. A fixed simple rule-based encoder is an important restricted alternative, but its simplicity is not implied by injectivity.



### Finding and scope

The universal encoder-description comparison omits the allowed function class and conditioning context.



### Proposed correction

Distinguish message length, encoder description and conditional description given a fixed encoder. Restrict to a specified simple encoder family before using a logarithmic map-complexity denominator.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 4: The contrastive upper bound fails in the exact one-hot regime

Assessment: supported; impact: major



Source: Appendix F.4, p. 35, Eqs. (31)–(32).



### Source claim (paraphrase)

Equation (32) bounds the nonnegative self-positive contrastive loss by \(-1+N-\log N-\bar d\).



### Analysis

For \(N=2\) identical exact-one-hot messages, true loss is \(\log2\approx0.69315\), while the claimed upper bound is \(1-\log2\approx0.30685\). Distinct binary messages give true loss \(\log(1+e^{-1})\approx0.31326\), but claimed bound approximately \(-0.19315\). Both satisfy the exact message regime, so a negative bound cannot upper-bound this positive loss.



### Finding and scope

The algebraic bound cited to support the PDM connection is false. This does not assert that the reported large-batch experiment used this small batch.



### Proposed correction

Retain the exact log-sum-exp expression or supply a valid inequality with its normalization and diagonal terms. No replacement empirical objective is validated.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 5: The soft PDM implementation uses norm-weighted averaging

Assessment: supported; impact: minor



Source: Eq.(3), PDF p.6; author release losses.py, pdm, lines 42–56



### Source claim (paraphrase)

Equation (3) averages positionwise cosines; `losses.py`, `pdm`, instead divides a sum of dot products by a sum of norm products.



### Analysis

For positive two-symbol rows \((0.9,0.1),(0.5,0.5)\) against \((0.9,0.1),(0.9,0.1)\), the release yields approximately \(0.903916\), while the mean cosine is \(0.890434\). Equal-norm and one-hot messages are passing cases. The hard branch additionally uses a count rather than a fraction at fixed length.



### Finding and scope

The soft release objective differs from the defined mean. Historical experiment code is unresolved.



### Proposed correction

Normalize each position’s dot product before averaging. State any deliberate hard-branch length scaling and corresponding objective coefficient.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 6: Convex loss need not give a unique reconstruction

Assessment: supported; impact: minor



Source: Appendix G.3, p. 36, Eqs. (35)–(37).



### Source claim (paraphrase)

Appendix G.3 infers uniqueness of the optimal deterministic reconstruction from convexity.



### Analysis

For conditional \(X=\pm1\) with equal probabilities and absolute reconstruction loss, every \(y\in[-1,1]\) has risk \(1\). Convexity gives no uniqueness. Squared Euclidean loss instead has the unique conditional mean under a finite second moment.



### Finding and scope

The universal uniqueness inference fails; the squared-error experiments are unaffected by this example.



### Proposed correction

Require an appropriate strict-convexity condition, or state existence/optimality without uniqueness.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
