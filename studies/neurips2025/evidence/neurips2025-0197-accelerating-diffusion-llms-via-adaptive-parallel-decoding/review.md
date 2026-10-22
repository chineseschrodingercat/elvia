# Accelerating Diffusion LLMs via Adaptive Parallel Decoding



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The sequence-level product-of-experts target differs from token-normalized mixing. The released sampler also applies positive temperature twice and discards shared target randomness through a default-greedy call. These findings do not establish a loss of the method’s empirical speed–quality benefit.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Token normalization does not sample the general sequence-level target

Assessment: supported; impact: minor



Source: Eq.(8), PDF p.5; Algorithm 1 lines 9–11 and target interpretation, p.6



### Source claim (paraphrase)

The paper defines \(p_T(x)\propto p_D(x)^R q(x)^{1-R}\), but normalizes mixed logits separately at each token.



### Analysis

Take two binary positions, uniform factorized \(p_D=1/4\), \(R=1/2\), and verifier joint \(q=(0.49,0.01,0.25,0.25)\) over \(00,01,10,11\). Global normalization gives \(p_T=(7/18,1/18,5/18,5/18)\), first-token probability \(4/9\). Local normalization keeps first token uniform and yields joint \((7/16,1/16,1/4,1/4)\), with total variation \(1/18\). All probabilities are positive. Here identical first-token shared-randomness draws make the draft and sampled target prefix agree, avoiding a separate draft-prefix approximation. In general local denominators depend on the path; one global partition function cannot replace their product.



### Finding and scope

The general target-draw identification is false. Endpoint \(R=0,1\), history-independent conditionals or constant normalizer products are special controls. Eq.(8) is a valid distribution definition, and the final adaptive output was not established to be promised equal to it.



### Proposed correction

Explicitly define the local verifier distributions and scope the acceptance rule accordingly. Exact global-target conditionals would require suffix partition sums, for which no efficient implementation is established.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: The positive-temperature helper effectively squares temperature

Assessment: supported; impact: minor



Source: Appendix C, PDF p.14; generation_utils.py, lines 97–123



### Source claim (paraphrase)

The sampler divides logits by \(T\), then divides exponentiated scores by \(E^T\), with \(E=-\log U\).



### Analysis

The maximizing score is equivalent to \(\ell/T^2-\log E\), hence its retained-support law is softmax at \(T^2\). Filtering first uses \(T\), so with active cutoffs the whole sampler is not simply a conventional \(T^2\) sampler. For logits \((0,0.2)\), \(T=0.2\), top-p \(0.95\), both tokens survive filtering. Nominal second-token probability is \(e/(1+e)=0.7310585786\), versus implemented \(e^5/(1+e^5)=0.9933071491\). At \(T=1\) the discrepancy disappears; the zero-temperature greedy branch is separate.



### Finding and scope

The supported positive-temperature path uses a different law from its nominal setting and the repository’s ordinary categorical baseline. Benchmark direction/magnitude and historical use remain unestablished.



### Proposed correction

Apply temperature once, filter the intended logits, then add standard Gumbel noise: \(X=\arg\max[\operatorname{filter}(\ell/T)+G]\). Preserve a common explicit filtering/sampling convention when comparing methods.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: The target call ignores the supplied shared randomness

Assessment: supported; impact: minor



Source: Algorithm 1 and one-shot endpoint, PDF p.6; generation_utils.py, apd_accept_criterion lines 126–138



### Source claim (paraphrase)

The target sampler call passes noise but omits temperature; its zero default returns raw logits and ignores noise.



### Analysis

Use two positions with logits \((0,0.2)\), \(T=0.2,R=1\), top-p \(0.95\), positive noise factors \((0.3,0.9)\). Proposal scores are \(1/0.3=3.3333\) and \(e/0.9=3.0203\), choosing token \(0\) at both positions. These factors have an open admissible neighborhood under the source noise transform. The target default chooses greedy token \(1\), and forced first acceptance yields mask \((1,0)\). Identical distributions evaluated with the same sampling map/noise must instead produce \((1,1)\).



### Finding and scope

The helper fails the stated shared-noise endpoint for supported stochastic proposals. Coincidental greedy agreement and zero-temperature proposals are countercontrols; no natural-prompt failure frequency is established.



### Proposed correction

Use one canonical noise tensor and identical explicit temperature/filtering/tie conventions for both sampling paths. At the identical-distribution endpoint, equality then follows directly. This does not repair the separate global-target interpretation.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
