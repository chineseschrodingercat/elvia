# Private Evolution Converges



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The dimension-one convergence rate conflicts with final independent sampling, and other probability/packing claims have explicit domain counterexamples. A CIFAR selector mismatch is confined to the supplied implementation.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Final sampling prevents the claimed dimension-one rate

Assessment: supported; impact: major



Source: Theorem 4.1, PDF p.6; Algorithm 2, PDF p.5, line 9



### Source claim (paraphrase)

Theorem 4.1 covers \(d=1\) and claims \(\widetilde O(dD\sigma^{1/d})\) error. Algorithm 2 ends by drawing \(m\) independent samples, with \(m\) of order \(\sigma^{-1}\) up to logarithmic factors.



### Analysis

Use target \(\mu=(\delta_0+\delta_1)/2\). For any candidate distribution on \([0,1]\), its independent empirical CDF at an interior threshold is \(K/m\), with \(K\sim\operatorname{Binomial}(m,p)\). For even \(m\), the symmetric convex expected deviation from \(1/2\) is minimized at \(p=1/2\) and equals \(\tfrac12\binom{m}{m/2}2^{-m}\asymp m^{-1/2}\). Integrating the CDF deviations over \((0,1)\) gives the same lower bound for \(\mathbb E W_1\), uniformly over the preceding candidate law and therefore also over its randomness. The prescribed sample count is of order \(\sigma^{-1}\) up to logarithms, giving a \(\sigma^{1/2}\) obstruction incompatible with the asserted dimension-one \(\sigma\) rate.



### Finding and scope

The theorem’s stated dimension-one conclusion fails for its own final sampling step. Dimensions at least two and other output algorithms are not refuted.



### Proposed correction

The established balancing recurrence supports the exponent \(1/\max\{d,2\}\), yielding \(\widetilde O(dD\sigma^{1/\max\{d,2\}})\). Use integer sample counts and an iteration horizon controlling the residual term.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: A fixed-dataset accuracy premise cannot imply the packing bound

Assessment: supported; impact: major



Source: Lemma 3.1, PDF p.5; Definition D.1, PDF p.17; proof, PDF p.28



### Source claim (paraphrase)

Lemma 3.1 states accuracy at a fixed dataset \(S\) and concludes \(\varepsilon\geq\log M(\Omega,\rho;2\eta)\). Its packing convention permits distances equal to \(2\eta\).



### Analysis

A mechanism that always returns that fixed \(S\) is perfectly private and perfectly accurate there, regardless of the larger domain’s packing number. Even uniform closed-ball accuracy permits the constant midpoint on \([0,1]\) when \(\eta=1/2\), since the endpoint accuracy balls touch. Uniform input accuracy and strict separation are therefore necessary for the proposed disjoint-event proof. Diameter and ambient dimension alone also do not lower-bound packing growth.



### Finding and scope

The lemma as quantified admits trivial counterexamples. A dimension-dependent interpretation additionally requires domain geometry.



### Proposed correction

Require accuracy at every input and centers separated by more than \(2\eta\). The neighboring-dataset disjoint-event argument then gives \(\varepsilon\geq\log((M-1)(1-\tau-\delta)/\tau)\) under the stated error ranges.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: The histogram proposition can return a nonprobability measure

Assessment: supported; impact: minor



Source: Section 4.2, Proposition 4.1, PDF pp.7–8; Appendix H, PDF pp.26–28



### Source claim (paraphrase)

Proposition 4.1 normalizes retained noisy mass when positive and otherwise returns the zero histogram, then states an ordinary probability-measure \(W_1\) bound.



### Analysis

For one positive bin with \(n=1\), \(\varepsilon=1/2\), and \(\delta=0.1\), all mass is discarded with probability \(0.95\). The returned zero measure has total mass zero, so the asserted ordinary \(W_1\) quantity is undefined. The proof also omits absolute values on negative discarded noise. The simulation caller’s fallback and Algorithm 2’s simplex projection avoid this particular output defect and must remain distinct.



### Finding and scope

The proposition is not well-defined on its stated output branch. This does not show that Algorithm 2 returns a zero measure.



### Proposed correction

On empty retained mass, return a probability distribution fixed on the public candidate support, then analyze the fallback probability and discarded absolute mass. This is probability-valued post-processing, with privacy conditional on the support’s provenance.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 4: The class-name selector uses position rather than dataset class identity

Assessment: supported; impact: minor



Source: Section 6, PDF p.9; Figures 3–4, PDF p.10; PE_cifar10_code.ipynb, cell 8



### Source claim (paraphrase)

The CIFAR notebook’s `Cifar10` selector iterates the length of the requested class-name list instead of resolving those names against the dataset class map.



### Analysis

A one-name dog request therefore selects class index \(0\), which is airplane, rather than dog index \(5\), while retaining dog metadata. The mismatch follows directly from the selector.



### Finding and scope

The release can mislabel the selected subset. Which historical code produced the published dog figures is unverified.



### Proposed correction

Resolve requested names through the dataset’s actual class map and keep a separate local subset label.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
