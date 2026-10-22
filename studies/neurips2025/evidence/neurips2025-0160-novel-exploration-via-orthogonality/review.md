# Novel Exploration via Orthogonality



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Strict eigenvector-magnitude ascent can terminate on an exact plateau before reaching the required novelty threshold. The undirected random-walk geometry also requires degree weighting, while a separate selector branch differs from the documented exploration protocol.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Strict magnitude ascent can stop at a plateau

Assessment: supported; impact: major



Source: Theorem 3.3 and proof, PDF p.4; option.take_option_action



### Source claim (paraphrase)

For \(L=I+\operatorname{diag}(N)-P\), starting at \(N_i>\operatorname{Re}\lambda\), the theorem promises a strictly increasing magnitude path ending below that threshold.



### Analysis

Use the directed cycle \(0\to1\to2\to0\), \(N=(1/4,1/8,11/28)\), \(f=(1,1,7/8)\), and \(\lambda=1/4\). Direct substitution gives \(Lf=\lambda f\), and the positive eigenvector is the principal mode after a nonnegative irreducible shift. Starting at \(2\), magnitude rises to \(1\) at node \(0\), but \(N_0=\lambda\). The only next step reaches node \(1\) at equal magnitude, violating strict ascent; only that plateau traversal reaches \(N_1<\lambda\). A connected undirected tree with edges \(01,12,23,14,45\), \(N=(1/2,1/2,0,0,0,0)\), \[f=(0,0,1/\sqrt2,1,-1/\sqrt2,-1)\], and \(\lambda=1-1/\sqrt2\) gives a second exact eigenpair: node \(0\) has only the zero-magnitude successor \(1\), so no first strict step exists.



### Finding and scope

Both positive plateaus and zero plateaus defeat the universal strict claim and the corresponding stop-on-ties interpretation. The more restricted source-maximum theorem and reported reward curves are not refuted.



### Proposed correction

With nonzero starting entry, strict ascent guarantees only an endpoint \(N\le\operatorname{Re}\lambda\). Allowing nondecreasing steps can restore the strict novelty threshold under strong connectivity, but requires plateau traversal with a visited set and changes the existing termination policy.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: An undirected random walk is not Euclidean Hermitian

Assessment: supported; impact: major



Source: Section 3, PDF pp.3–4; Appendix D, PDF p.22



### Source claim (paraphrase)

The operator \(I+\Gamma-D^{-1}A\) is called Hermitian on undirected graphs and assigned an unweighted Euclidean edge-energy formula.



### Analysis

For the three-vertex undirected path, degrees are \((1,2,1)\), so \(P_{01}=1\ne P_{10}=1/2\). With zero potential and \(x=(0,1,0)\), \(x^\top(I-P)x=1\), but the printed edge sum \(\tfrac12\sum_{ij}P_{ij}(x_i-x_j)^2=3/2\). Right eigenvectors \((1,1,1)\) and \((1,-1,1)\) have distinct eigenvalues \(0,2\) yet Euclidean inner product \(1\).



### Finding and scope

Euclidean symmetry and orthogonality fail on irregular graphs. Real eigenvalues survive by similarity to a symmetric matrix; regular graphs remain a valid special case.



### Proposed correction

Use the degree-weighted inner product and quotient \[\frac{\tfrac12\sum_{ij}A_{ij}(x_i-x_j)^2+\sum_i d_iN_ix_i^2}{\sum_i d_ix_i^2},\] or the symmetric operator \(D^{1/2}LD^{-1/2}\). This does not itself prove orthogonality of nonlinear magnitude-based policies.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: Random-option selection occurs outside the epsilon event

Assessment: supported; impact: minor



Source: Section 5, PDF p.7; all_functions.py, AgentQ2.option_action, lines 487–514



### Source claim (paraphrase)

The paper chooses a random option with probability initP conditional on an epsilon exploration step. The release makes a new option draw after the epsilon-greedy action.



### Analysis

With one eligible option, no active option, a greedy primitive action and independent draws \(u,v\), let \(\epsilon=\mathrm{initP}=0.1\). At \(u=0.5,v=0.05\), the release overrides a greedy action with an option; the described conditional procedure does not. The eligible-decision branch probability is \(0.1\), versus \(0.1\cdot0.1=0.01\). These are branch probabilities, not fractions of all environment transitions. An outer false exploration flag suppresses this direct branch, but recursive termination calls need not preserve that flag.



### Finding and scope

The released selector and described protocol differ. Published-run correspondence and reward-curve effects remain unestablished.



### Proposed correction

Either condition option sampling on the single epsilon event or document the independent override, according to the actual run protocol. No fully integrated selector repair is claimed.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
