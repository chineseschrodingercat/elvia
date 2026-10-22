# Optimal Best Arm Identification under Differential Privacy



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



An actual-tail-product concentration lemma is false on one legal observation, and a time-uniform logarithmic envelope has the wrong stochastic scale. Direct Chernoff and square-root-scale alternatives preserve important downstream routes, but do not constitute a complete reproof. A zero-weight uniqueness claim is a separate boundary error.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: The actual-tail-product concentration upper bound fails

Assessment: supported; impact: major



Source: Lemma 12, PDF pp.41–42; Eq.(24)



### Source claim (paraphrase)

The lemma upper-bounds the tail by \(f(-\log M)\), where \(M\) is the supremum of products of actual upper tails and \(f(u)=(u+3-\log2)e^{-u}\).



### Analysis

Take one observation \(Z\sim\mathrm{Ber}(0.01)\), independent \(S\sim\mathrm{Lap}(1)\), \(x=0.01,\epsilon=1\). Over \(z\in(0.01,0.02)\), \(\Pr(Z\ge z)=0.01\), so \(M=0.005\). The proposed bound is \(0.005(3-\log2-\log0.005)=0.03802585093\). Direct conditioning gives \(\Pr(Z+S\ge0.02)=0.99e^{-0.02}/2+0.01(1-e^{-0.98}/2)=0.49332178779\). A large below-mean Bernoulli endpoint term is not dominated by the interior upper-tail product used in the proof.



### Finding and scope

The lemma is false under its own assumptions. This is not a counterexample to the different modified-divergence bound or the private mechanism.



### Proposed correction

Independence yields a direct Chernoff exponent \(I(\lambda)=\sup_{0<s<\epsilon}[s\lambda-\log(1-\mu+\mu e^s)+(n/t)\log(1-s^2/\epsilon^2)]\). Bernoulli/Laplace convex conjugacy identifies it with the stated modified divergence, giving the stronger bound \(e^{-tI(\lambda)}\). This restores the concentration statements and a stopping-rule proof input without relying on the false actual-tail lemma; it is not a full algorithm reproof.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: The claimed uniform envelope is smaller than Bernoulli fluctuations

Assessment: supported; impact: major



Source: Lemma 55 and proof, PDF pp.78–79; later expected-time arguments



### Source claim (paraphrase)

The lemma claims \(\widetilde N|\widetilde\mu-\mu|\le W_\mu\log(e+\widetilde N)\) with a finite sub-exponential random constant for all geometric releases.



### Analysis

For \(\mu=1/2,\epsilon=1,\eta=1\), let \(N_k=2^{k-1}\), \(C_k=Z_{N_k}-N_k/2+S_k\), with \(k\) independent Laplace noises. The claimed finite envelope forces \(C_k/\sqrt{N_k}\to0\) almost surely. Yet its characteristic function is \([\cos(t/(2\sqrt{N_k}))]^{N_k}(1+t^2/N_k)^{-k}\to e^{-t^2/8}\), a nondegenerate Gaussian limit. Bounded convergence under the claimed almost-sure limit would instead give \(1\). This rules out the proposed supremum, without any finite-simulation inference.



### Finding and scope

The logarithmic-over-sample rate used in the expected-time proof is invalid. A finite realized stopping horizon does not justify the claimed uniform bound over all potential arm releases; final expected-time conclusions remain unrefuted.



### Proposed correction

A valid weaker form is \(\sqrt{\widetilde N}|\widetilde\mu-\mu|\le W^\prime_\mu\log(e+\widetilde N)\). Normalized Bernoulli/Laplace sums have uniformly bounded local moment-generating functions on the geometric grid; a union bound over tails weighted by growing log counts gives a sub-exponential supremum. Polynomial sample thresholds, for example \((6W^\prime_\mu/r_0)^4\), still have finite moments. All downstream uses and leading constants must be updated consistently.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: A single positive weight need not give a unique global minimizer

Assessment: supported; impact: minor



Source: Lemma 35 third bullet, PDF p.59; Eq.(3)



### Source claim (paraphrase)

For nonnegative weights with positive maximum, the lemma claims the minimizer over \([0,1]\) is unique.



### Analysis

At \(\lambda=0.8,\mu=0.2,\epsilon=1,w=(1,0)\), the objective is \(d_\epsilon^-(0.8,u)\), equal to zero for every \(u\in[0.8,1]\). Thus \(0.8\) and \(0.9\) are distinct global minimizers. A tie-breaking convention can select one but cannot prove uniqueness.



### Finding and scope

The boundary-domain claim fails. The minimum value and interior optimal-allocation result are not refuted, because both weights are positive at the relevant interior optimum.



### Proposed correction

Require both weights positive for uniqueness on \([0,1]\), or define the canonical minimizer on \([\mu,\lambda]\). Strict convexity on that restricted interval and compactness yield uniqueness and continuity away from the zero-weight vector.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
