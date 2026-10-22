# Speculative Jacobi-Denoising Decoding for Accelerating Autoregressive Text-to-image Generation



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The preliminary finite Jacobi iteration bound requires a fixed update map or position-specific coupled randomness, which the sampling notation does not specify. No failure of the separate speculative acceptance mechanism or actual implementation is established.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: The Jacobi bound needs fixed position-specific randomness

Assessment: supported; impact: minor



Source: Section 3, PDF p.4; cited Song et al. Proposition 1



### Source claim (paraphrase)

The paragraph writes sampled parallel updates and an at-most-\(N\) iteration bound without specifying coupling between iterations.



### Analysis

At \(N=1\), a uniform binary token with fresh independent draws has path \(0\to1\to0\) with probability \(1/4\), changing beyond one update. Path \(0\to0\to1\) also has probability \(1/4\), so a coincidental equality is not an absorbing fixed point. In contrast, draw one \(U_1\) once and use the same inverse-CDF map each time: the first update settles the token. In general, fixed \(U_i\) and causal maps \(G_i(x_{<i},U_i)\) settle the first \(j\) positions after \(j\) updates by induction; after \(N\) updates the vector equals the sequential ancestral sample and remains fixed.



### Finding and scope

The unconditional fresh-sampling interpretation is false, but the notation does not establish that the authors implement it. The separate speculative acceptance/progress rule and model quality are not refuted.



### Proposed correction

Specify reuse of the same random variate for each global token position, or a deterministic map/tie rule. An initially fixed seed that advances on every update is insufficient; an additional equality-check evaluation may be needed unless the known iteration bound is used directly.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
