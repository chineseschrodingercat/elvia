# Attention (as Discrete-Time Markov) Chains



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Identity addition need not slow mixing, and eigenvalue modulus alone does not certify metastability. A nonuniform personalization helper is nonstochastic; the central stationary-chain construction and empirical results remain separate.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Adding identity transitions can accelerate mixing

Assessment: supported; impact: minor



Source: Section 4.1, identity-addition interpretation



### Source claim (paraphrase)

The paper states that \((I+A)/2\) preserves stationary state and slows convergence because of increased self-transition.



### Analysis

Take positive stochastic attention \(A=\left(\begin{smallmatrix}.1&.9\\.9&.1\end{smallmatrix}\right)\), realizable by finite logits \(Q=I,K=\sqrt2(\log A)^T\). Its nontrivial eigenvalue is \(-.8\); the lazy chain has \(.1\). From a single-state start, total variation to \((1/2,1/2)\) is \((.8)^k/2\) versus \((.1)^k/2\). Thus identity addition accelerates this already aperiodic chain. Stationary-distribution preservation remains valid.



### Finding and scope

The unrestricted mixing-direction explanation is false. TokenRank and reported empirical improvements are not thereby refuted.



### Proposed correction

State the eigenvalue map \(\lambda\mapsto(1+\lambda)/2\); mixing direction depends on the spectrum. A reversible nonnegative-spectrum restriction supports the narrower spectral-slowdown statement.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Eigenvalue modulus does not certify metastable regions

Assessment: supported; impact: minor



Source: Sections 3.1/4.4; Supplement E.1; dino.py eigenvalue weighting



### Source claim (paraphrase)

The magnitude of the second eigenvalue is associated with stable metastable regions and used for head weighting.



### Analysis

Positive stochastic matrices with diagonal entries \(.99\) or \(.01\), respectively, have nontrivial eigenvalues \(.98\) and \(-.98\), hence identical modulus. In a two-state chain, expected singleton residence time is \(1/(1-A_{ii})\): \(100\) for the first, only \(1/.99\) for the second. Large negative modulus describes persistent alternation rather than prolonged residence; the scalar also loses multiplicity information.



### Finding and scope

Modulus alone neither certifies nor counts metastable regions. The measured weighting correlation can still hold for observed attention heads; their negative-mode frequency is unmeasured.



### Proposed correction

Present modulus as an empirical spectral feature; stronger semantic-metastability claims require structural assumptions and retention/exit measurements.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: Nonuniform personalization breaks row stochasticity

Assessment: supported; impact: minor



Source: helpers.py, prep_for_power_method, lines 63–83



### Source claim (paraphrase)

The helper promises a stochastic personalized transition but uses \(E=ee^T/n\).



### Analysis

For \(A=\left(\begin{smallmatrix}.8&.2\\.3&.7\end{smallmatrix}\right)\), \(\alpha=.8\) and probability vector \(e=(.75,.25)^T\), the returned row sums are \(.875\) and \(.825\). Generally they equal \(\alpha+(1-\alpha)e_i\sum_je_j/n\), not one. Normalizing later power iterates produces a different Perron iteration, not a stochastic matrix. The default all-ones branch is valid.



### Finding and scope

The optional personalized release branch violates its contract. No evidence shows published demos used that branch.



### Proposed correction

For normalized positive \(p\), use \(T=\alpha A+(1-\alpha)\mathbf1p^T\). Rows sum to one; positivity gives ergodicity. Zero entries in \(p\) need additional assumptions for that stronger guarantee.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
