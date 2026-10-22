# Consistency of Physics-Informed Neural Networks for Second-Order Elliptic Equations



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The unsquared error rate and unrestricted point-anchor coercivity have explicit mathematical counterexamples. Other kernel arguments contain recoverable proof gaps or estimates requiring additional assumptions. Qualitative consistency is not generally disproved.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: The unsquared error rate is too fast

Assessment: supported; impact: major



Source: Theorem 3.12, PDF p.7, Eq.(20); Appendix E, PDF pp.28–29



### Source claim (paraphrase)

Theorem 3.12 claims both loss and unsquared \(L^2\) error are \(O(R_N)\), where \(R_N=N^{-(1-3\alpha)/2}\sqrt{\log N}+N^{-\alpha}\) and stopping time is of order \(N^\alpha\).



### Analysis

On \((0,1)\), let \(\phi_j=\sqrt2\sin(\pi jx)\), kernel \(K(x,y)=1+xy+\sum_je^{-j^2}\phi_j(x)\phi_j(y)\), and solution \(u^*=\sum_je^{-j^2/2}\phi_j/j\). The kernel and forcing are smooth and \(\|u^*\|_H^2=\sum_jj^{-2}<\infty\). For the Laplacian with zero endpoint data, mode decay is \(e^{-2\mu_jt}\), \(\mu_j=e^{-j^2}(\pi j)^4\). At \(t_j=(2\mu_j)^{-1}\), error is at least \(e^{-1}e^{-j^2/2}/j\), so \(t_j\|v_{t_j}-u^*\|_2\to\infty\). Bounded residual features give empirical mean-square perturbation \(O(t^2/N)\) by the contraction-semigroup identity. Taking \(\alpha=1/10\), \(N_j=\lceil t_j^{10}\rceil\), makes that perturbation negligible relative to the mode lower bound, while \(R_{N_j}=O(t_j^{-1})\). The unsquared empirical rate therefore also fails along this subsequence.



### Finding and scope

The quantitative norm rate is contradicted under smooth, noiseless, uniformly sampled admissible data. The construction remains consistent and does not reject qualitative convergence.



### Proposed correction

The stated loss-to-error argument yields \(\|\hat u_T-u^*\|_2^2=O(R_N)\), equivalently norm \(O(R_N^{1/2})\). A stronger norm rate requires an additional source condition or argument.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: The RKHS embedding is used in the wrong direction

Assessment: supported; impact: minor



Source: Lemma E.2, PDF p.28, Eqs.(142)–(144); Corollary A.7, PDF p.19



### Source claim (paraphrase)

Corollary A.7 bounds \(\|u\|_{C^2}\) by \(C\|u\|_H\), whereas Eq.(142) needs the converse.



### Analysis

The functions \(h_j=e^{-j^2/2}\sqrt2\sin(\pi jx)\) have RKHS norm \(1\) and \(C^2\) norm tending to zero. Thus the invoked reverse inequality is unavailable. However, along the intended population flow, \(d\|v-u^*\|_H^2/dt=-4\mathcal L(v)\); integration and monotone loss recover \(\mathcal L(v_t)\leq\|u^*\|_H^2/(4t)\).



### Finding and scope

The written proof step fails, while its loss conclusion has an independent energy proof.



## Problem 3: Polynomial Gaussian features need not be sub-exponential

Assessment: supported; impact: minor



Source: Assumption 5.2, PDF p.8; Lemma F.8, PDF p.32, Eqs.(175)–(179)



### Source claim (paraphrase)

Lemma F.8 invokes generic sub-exponential tails from polynomial growth under Assumption 5.2’s smooth activation bounds.



### Analysis

The allowed activation \(\sigma(z)=z^3+\sin z\) makes a positive feature product grow as the sixth power of a Gaussian variable. Its positive exponential moments diverge, so the asserted generic sub-exponential premise is false. Polynomial growth alone cannot justify that Bernstein application.



### Finding and scope

The concentration proof needs another argument. This does not independently establish failure of the claimed kernel-value convergence rate.



### Proposed correction

Truncate Gaussian parameters at a multiple of \(\sqrt{\log m}\), apply concentration to independent bounded truncated features, then control the tail event and bias. Complete highest-derivative control under only \(C^3\) regularity remains unresolved.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 4: The Gaussian linear-map estimate hides width dependence

Assessment: supported; impact: minor



Source: Appendix F.3, PDF p.42, Eqs.(263)–(269); Theorem F.15



### Source claim (paraphrase)

Equation (267) bounds the norm of the map \(\varphi(x)=\sum_{p\ne q}a_pb_qx_{pq}\) by a universal multiple of \(\log N\), independent of layer width.



### Analysis

Its derivative operator norm squared is \((\sum_pa_p^2)(\sum_qb_q^2)-\sum_pa_p^2b_p^2\). For independent standard Gaussian coordinates and width \(m\), the norm divided by \(m\) tends to \(1\). A universal width-independent threshold cannot hold over unrestricted widths. Coordinatewise maximum conventions also require a dimension dependence.



### Finding and scope

The cited deep-network proof estimate fails. No counterexample to the full deep-network theorem follows from this item alone.



## Problem 5: Point anchoring does not give unrestricted high-dimensional coercivity

Assessment: supported; impact: major



Source: Section 5.1, PDF p.9, Eqs.(25)–(28); Theorem 5.9



### Source claim (paraphrase)

Section 5.1 transfers the loss-to-\(L^2\) conclusions to \(\mathcal L_M(u)=|u(p)|^2+\|\Delta u-f\|_2^2\) on tori without a dimension restriction.



### Analysis

For normalized \(\mathbb T^d\), \(d\geq4\), let \(S_R=\sum_{0<\|k\|_\infty\leq R}|k|^{-4}\) and \(u_R=1-S_R^{-1}\sum|k|^{-4}e^{ik\cdot x}\). These smooth real functions satisfy \(u_R(0)=0\), \(\|\Delta u_R\|_2^2=1/S_R\to0\), yet their constant Fourier coefficient is \(1\), and \(\|u_R\|_2\to1\). Thus vanishing anchored loss need not control solution error. This is not an assertion about the particular zero-initialized trajectory for zero forcing.



### Finding and scope

The unrestricted coercivity transfer is false even for smooth functions. Low-dimensional point anchoring is not contradicted.



### Proposed correction

Restrict this point-evaluation argument to dimensions where \(H^2\) controls point values, such as \(d\leq3\), or replace the point anchor by a specified mean gauge. The latter changes the loss but controls the constant mode in every fixed dimension.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 6: Equal Laplacian frequencies need not share a torus-kernel eigenvalue

Assessment: supported; impact: minor



Source: Appendix H, PDF p.49, argument before Eq.(349)



### Source claim (paraphrase)

Appendix H treats a torus inner-product NTK as scalar on each full Laplacian eigenspace.



### Analysis

Translation invariance diagonalizes Fourier modes but does not impose rotational symmetry on a product torus. The admissible sinusoidal NTK gives distinct eigenvalues to \((5,0)\) and \((4,3)\), approximately \(0.000192508\) and \(0.0000418808\), although both have squared frequency \(25\). Positive-series bounds separate these values; simultaneous diagonalization itself survives.



### Finding and scope

The common-eigenvalue identification is too strong. The underlying finite-mode approximation can be indexed more carefully.



### Proposed correction

Use \(K(x,y)=\sum_{k\in\mathbb Z^d}\lambda_ke^{ik\cdot(x-y)}\). State positivity for the modes needed by the approximation, rather than equating all \(\lambda_k\) at the same \(|k|^2\).

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
