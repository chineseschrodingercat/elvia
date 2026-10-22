# Provably Efficient Multi-Task Meta Bandit Learning via Shared Representations



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The central source-regret and representation-estimation proofs use unjustified probabilistic steps. Target confidence, potential and excitation arguments also have explicit local failures. Separate released-notebook discrepancies do not establish that published figure rankings are false.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Optimizing Gaussian candidates does not preserve centering

Assessment: supported; impact: major



Source: Theorem 4.3 and Remark 4.4, PDF pp.5â€“6; Appendix D, PDF pp.19â€“21



### Source claim (paraphrase)

The regret proof treats oracle rewards as centered Gaussian martingale increments, and the task-scaling remark suppresses the largest singular value.



### Analysis

For independent candidates \(Z_1,Z_2\sim N(0,1)\) and parameter \(1\), the exploratory first candidate is centered but the oracle is \(\max(Z_1,Z_2)=(Z_1+Z_2+|Z_1-Z_2|)/2\), with mean \(1/\sqrt{\pi}\). Thus exploration regret has positive drift \(N_1/\sqrt{\pi}\), and the asserted martingale implication fails. On \(Z_1<0\), even the preceding pointwise inequality \(\max(Z_1,Z_2)-Z_1\le\max(Z_1,Z_2)\) fails. Separately, rank-one task weights all equal to \(1\) satisfy bounded task norms and incoherence but give \(\sigma_{\max}^{\star}=\sqrt T\); the retained spectral factor cannot be absorbed into a task-independent constant.



### Finding and scope

The central proof steps and simplified task dependence are unsupported. This contextual candidate example isolates selection bias; it is not claimed to instantiate every source-budget premise or to disprove every possible corrected regret theorem.



### Proposed correction

Under an added bounded-action model, valid starting bounds are \(R_{\rm explore}\le2LuTN_1\) and \(R_{\rm commit}\le2L(N-N_1)\sum_t\|\widehat\theta_t-\theta_t^\star\|\). A coherent candidate-generation model and a new regret analysis are still required.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: A fitted representation cannot be pulled outside the same-sample expectation

Assessment: supported; impact: major



Source: Algorithm 1, PDF p.4; Lemma C.1, PDF p.17



### Source claim (paraphrase)

The proof substitutes \(\mathbb E[\widehat B^\top xx^\top\widehat B]=I\) and independent Gaussian reduced-design summands although the same samples fit \(\widehat B\).



### Analysis

Let \(d=8,r=N_1=T=1,\theta^\star=e_1\), zero noise and \(x\sim N(0,I)\). The algorithm retains the lone observation \(y=x_1\) and obtains \(\widehat B=\operatorname{sign}(x_1)x/\|x\|\). Consequently \((\widehat B^\top x)^2=\|x\|^2\) has expectation \(8\), rather than \(1\). An independent fresh \(x^\prime\), conditional on the fitted basis, does have expectation \(1\).



### Finding and scope

The displayed expectation/independence justification is invalid. The small diagnostic does not meet Theorem 4.1â€™s high-sample conditions and is not a complete theorem counterexample; a dependence-aware proof remains necessary.



### Proposed correction

Independent representation-fitting and regression blocks justify the conditional Gaussian calculation, but change sample accounting. Preserving sample reuse requires a uniform or dependence-aware concentration argument.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: The rank-one confidence simplification drops a logarithmic coefficient

Assessment: supported; impact: major



Source: Theorem 5.1, PDF p.7; Appendix E, PDF p.24



### Source claim (paraphrase)

The determinant radius squared contains \(\sigma^2[\log(\det V_n/\lambda^r)+2\log(1/\delta)]\), while the simplification has \(r\log(1/\delta)\).



### Analysis

At \(r=1\), grant a known representation \(e_1\) in \(d=100\), \(x_m=e_1,\theta^\star=0,\lambda=L=\sigma=1,n=1000,S=0,\delta=10^{-12}\). Independent unit Gaussian noise gives design-norm error \(\sqrt{1000/1001}|Z|\). The printed radius \(\sqrt{\log(1001/10^{-12})}=5.877055\) has exact two-sided failure probability \(4.10284256\times10^{-9}\), exceeding \(\delta+2d^{-10}\approx10^{-12}\). This tests the conditional target calculation, bypassing rather than authenticating source-learning premises.



### Finding and scope

The rank-one simplification is not a valid confidence bound on its stated conditional domain. For ranks at least two, the displayed coefficient comparison alone is not an objection; the determinant form remains the proper starting point.



### Proposed correction

Preserve \(2\log(1/\delta)\); the trace bound gives noise radius \[\sigma\sqrt{r\log(1+nL^2/(r\lambda))+2\log(1/\delta)}\]. Retain the stated representation-bias terms and recheck dependent regret results. The compact-expression issue may be inherited from the cited OFUL result; no priority claim is made.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 4: The untruncated potential inequality needs a size condition

Assessment: supported; impact: major



Source: Appendix F, Eqs.(12)â€“(13), PDF p.25; Section 5 assumptions



### Source claim (paraphrase)

The proof uses \(\sum_m x_m^\top\overline V_{m-1}^{-1}x_m\le2\log(\det\overline V_N/\lambda^d)\) for unrestricted \(\lambda>0,L>0\).



### Analysis

With \(d=3,N=1,\lambda=1,x_1=(1000,0,0)^\top,L=1000\), the left side is \(10^6\), but the right side is \(2\log(1000001)=27.6310231\). The generally valid inequality truncates each quadratic form at \(1\). Dropping truncation is justified, for example, by \(\lambda\ge L^2\), which is absent here.



### Finding and scope

This deterministic step used in the target-regret proof is false on its stated domain; it does not by itself disprove every asymptotic rate under a normalized-action convention.



### Proposed correction

Impose the needed size condition, or keep \(a=L^2/\lambda\) and factor \(c(a)=a/\log(1+a)\). Since \(q/\log(1+q)\) increases, \(\sum q_m\le c(a)\log(\det\overline V_N/\lambda^d)\). Propagate the factor through a valid conditional confidence argument.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 5: Target sample count does not ensure excitation

Assessment: supported; impact: major



Source: Theorem G.1 and Algorithm 3, PDF pp.25â€“26; source-only Assumption 3.1



### Source claim (paraphrase)

The target regression theorem uses an ordinary reduced-design inverse and only a target sample-count lower bound; its Gaussian action assumption is explicitly for source tasks.



### Analysis

Grant \(\widehat B=B^\star=e_1\in\mathbb R^2,\theta^\star=e_1\), zero target noise and target observations \(x_m=e_2\). For every sample count, \(\Phi\widehat B=0,Y=0\). The displayed pseudoinverse estimate is zero, with error \(1\), versus claimed bound \(1.12(0.01)=0.0112\). Greedy collection from ordered actions \(\{e_2,e_1\}\) with zero initial estimate and a first-index tie rule can remain unexcited throughout.



### Finding and scope

The target-design argument omits identification/excitation. This known-representation construction isolates the target obstruction, without claiming a full source-process counterexample.



### Proposed correction

Add a justified target design condition such as \(\lambda_{\min}(\widehat B^\top\Phi^\top\Phi\widehat B)\ge\gamma N_2>0\), together with appropriate conditional noise and representation-residual assumptions. No complete repaired theorem is established.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 6: The released generator uses variance as a standard deviation

Assessment: supported; impact: minor



Source: Section 6, PDF pp.8â€“9; original Representation_Learning/Synthetic/Algorithm and Transfer_Learning/Synthetic/Algorithm notebooks



### Source claim (paraphrase)

The source notebook sets \(\sigma=10^{-3}\) and calls normal with scale \(\sigma^2\); the transfer notebook sets \(\sigma=10^{-1}\) and does the same.



### Analysis

Normal scale is standard deviation, so the actual variance is \(\sigma^4\): respectively \(10^{-12}\) and \(10^{-4}\), versus paper variances \(10^{-6}\) and \(10^{-2}\). This follows directly from \(\eta=\sigma^2Z\). Other notebooks using scale \(\sigma\) are countercontrols; the defect is not universal.



### Finding and scope

These settings instantiate different noise levels. Actual historical figure provenance and ranking changes remain unestablished.



### Proposed correction

When \(\sigma\) denotes standard deviation, pass scale \(\sigma\). Recompute affected comparisons before attributing performance at the stated variance.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 7: The MoM comparison mixes decision clocks and action domains

Assessment: supported; impact: minor



Source: Section 6.2, PDF p.9; Figure 1(a), p.10; synthetic source notebook, cell 7



### Source claim (paraphrase)

The comparison is described over \(200\) rounds, but the MoM branch has \(45\) initial, \(2\times45\) basis-direction and \(110\) commitment actions.



### Analysis

The literal total is \(245\), yielding \(246\) cumulative entries with the initial zero. Truncation to \(201\) entries retains only \(65\) commitment actions, while context indices \(45\)â€“\(89\) are reused in both basis loops. Probes \(\sqrt{\lambda_0}\widehat B_{:,k}\) also need not belong to the finite candidate set: \((e_1+e_2)/\sqrt2\notin\{e_1,e_2\}\). The notebook explicitly calls the baseline infinite-action, which supports an intentional variant but does not establish a common comparison protocol.



### Finding and scope

The released comparison lacks a single common clock/action domain. No claim is made that the original continuous-action MoM method is erroneous or a published ranking reverses.



### Proposed correction

Use one decision clock and explicitly align feasible sets and comparators. A changed benchmark requires new runs; array truncation alone does not repair it.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 8: The MovieLens projector includes the full ambient basis

Assessment: supported; impact: minor



Source: Transfer_Learning/Movielens/Algorithm notebook, cells 9 and 11; subspace distance definition, PDF p.3



### Source claim (paraphrase)

For a \(5\times100\) rank-one task matrix, the notebook uses all economy-SVD left vectors in \(I-UU^\top\).



### Analysis

Repeat \((1,1,1,1,1)^\top/\sqrt5\) as all columns and take \(\widehat B=(1,-1,0,0,0)^\top/\sqrt2\). The true subspace distance is \(1\). Economy SVD nevertheless returns a square orthogonal \(U\), so \(UU^\top=I_5\) and the coded distance is zero for every estimate. The quantity enters the confidence radius; at \(n=100,L=S=\lambda=1\), erasing a unit error removes \(21\) from its bias term.



### Finding and scope

The local geometric measurement and radius change are established. A changed selected action or published MovieLens figure is not established; the notebook settings differ from the figure.



### Proposed correction

Use the intended signal-rank basis \(U_{:,1:r}\), then compute distance to that subspace. This fixes the projector, without certifying other confidence assumptions.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
