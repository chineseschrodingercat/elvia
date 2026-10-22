# Private Zeroth-Order Optimization with Public Data



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The latest paper retains the PAZO-M step-size counterexample and the nonvanishing fixed-perturbation obstruction to its asymptotic PAZO-S claim. Local proof and release discrepancies remain scoped separately. The historical PAZO-M public-norm scaling defect is absent from the current author repository; original experimental provenance and empirical effects remain unresolved.



## Scope

Claim-focused reading of the identified paper and author-released materials. The arguments below distinguish mathematical contradictions, version-specific implementation defects and unresolved empirical consequences. No author code was executed in this revision.



## Problem 1: PAZO-M step size allows an exact nonstationary two-cycle

Assessment: supported; impact: major



Source: Official PDF: Theorem 4.1, p. 6; Theorem B.3, p. 16; proof condition before Eq. (11), p. 18.



### Source claim (paraphrase)

Theorem 4.1/Theorem B.3 assert a finite-time stationarity bound for the prescribed PAZO-M step size without the restriction later used in the proof.



### Analysis

Choose \(d=q=b=b'=1\), identical public/private per-record losses \(f(x)=1-\cos x\), \(L=M=1\), \(\alpha=0.9\), \(\lambda=10^{-6}\), and zero gradient-variance, similarity and injected-noise parameters. The objective is smooth, Lipschitz, bounded below and bounded in \([0,2]\). Clipping is inactive because the threshold is \(1+\sqrt2\) while the scalar directional derivative has magnitude at most one.

The prescribed step is \(\eta=2.75\). For \(u\in\{-1,1\}\), using \(\operatorname{sinc}(\lambda)=\sin\lambda/\lambda\), the two-point estimator is \(\operatorname{sinc}(\lambda)\sin x\), so the exact recurrence is \(x_{t+1}=x_t-a\sin x_t\), with \(a=\eta[\alpha+(1-\alpha)\operatorname{sinc}(\lambda)]\in(2.7,2.75)\). A nonzero root \(a\sin x_0=2x_0\) lies in \((\pi/3,\pi/2)\); hence \(x_t=(-1)^t x_0\) and \(|\nabla f(x_t)|^2>3/4\).

At \(T=1000\), the complete surviving right side of Theorem B.3 is \(\frac{16(1-\cos x_0)(1-\alpha)}{T(2-\alpha)^2}+\frac{2\lambda(1-\alpha)}{2-\alpha}+\frac{\lambda^2(1-\alpha)}4+\frac{\alpha\lambda}2<0.001324\). It cannot bound a left side greater than \(3/4\). In particular, the proof condition \(\alpha L\eta<1\) fails: its value is \(2.475\).



### Finding and scope

The finite-time theorem is false on its stated domain. This is an analytic cycle, not an empirical training failure. The distinct bounded-loss Theorem B.6 already restricts \(\alpha<2/3\) and is not refuted by this example.



### Proposed correction

State and enforce \(\alpha L\eta<1\), or cap the step and rederive the bound. With \(s=\sqrt d\), the prescribed step satisfies this condition when \(\alpha<(4s-1-\sqrt{4s^2+1})/(3s-2)\); \(0<\alpha<2/3\) suffices uniformly in dimension. This repairs the exhibited obstruction without recertifying every intermediate line.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: PAZO-S selection invalidates unconditional moment substitutions

Assessment: supported; impact: minor



Source: Official PDF: Theorem B.5 proof, pp. 23-24 (selected batch moments and accepted Gaussian perturbation).



### Source claim (paraphrase)

Theorem B.5's proof treats a privately selected public-gradient candidate as if its pre-selection moments and zero-mean perturbation were unchanged.



### Analysis

Let \(f(x)=\sqrt{1+x^2}\) and public per-example loss \(f(x)+\zeta x\), with \(\Pr(\zeta=0.2)=0.01\) and \(\Pr(\zeta=-0.2/99)=0.99\). At \(x=1\), step \(1/4\), three public candidates and exact private comparisons, both candidate positions are positive; minimizing private loss selects the largest \(\zeta\). Thus \(\mathbb E\zeta=0\), but \(\mathbb E\zeta_I=0.00398\), and the selected second moment is about \(2.9502\) times the unselected \(0.0004040404\).

Zero-mean Gaussian perturbations also become biased under acceptance. For one exact public gradient, put \(y=1-1/(4\sqrt2)>0\), \(Z\sim N(0,\epsilon_p^2)\), and \(\eta=1/4\). Acceptance occurs exactly when \(0<Z<2y/\eta\), so \(\mathbb E[Z\mathbf1_A]=\epsilon_p[\phi(0)-\phi(2y/(\eta\epsilon_p))]>0\), where \(\phi\) is the standard-normal density.



### Finding and scope

These are counterexamples to the proof's moment substitutions. They do not by themselves refute the complete finite-time inequality, because a different descent argument could exploit selection.



### Proposed correction

A selection-safe bound uses \(\mathbb E\|\zeta_I\|^2\le\sum_{j=1}^k\mathbb E\|\zeta_j\|^2\le k\sigma_2^2/b'\). With \(\eta=1/(4L)\), smoothness then yields \(\frac1T\sum_t\mathbb E\|\nabla f(x_t)\|^2\le8L\Delta_f/T+(\gamma+\sqrt{k\sigma_2^2/b'}+\sqrt d\,\epsilon_p)^2\). This conservative replacement does not certify the paper's sharper dependence.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: Fixed PAZO-S perturbations do not give a vanishing asymptotic error

Assessment: supported; impact: major



Source: Official PDF: Eq. (6) and asymptotic paragraph, p. 7; Theorem B.5 and its asymptotic sentence, p. 23.



### Source claim (paraphrase)

The asymptotic paragraph after Eq. (\(6\))/Theorem B.5 claims an \(O(\gamma^2+\sigma_2^2/b')\) error from \(T\to\infty\) and \(\epsilon_p\le d^{-1/2}\), dropping terms retained in the finite-time display.



### Analysis

A fixed positive perturbation does not vanish. Take \(d=k=b=b'=1\), identical losses \(f=f'=1-\cos x\), \(\eta=1/4\), \(\epsilon_p=1\), clipping threshold \(C=2\) and private-noise multiplier \(\sigma\ge1\). Here \(\gamma=\sigma_2=0\). The baseline candidate is \(y=x-\eta\sin x\), and its perturbed competitor is \(y+W\), with \(W\sim N(0,1/16)\).

Since each true loss is in \([0,2]\), the perturbed candidate is accepted with conditional probability at least \(\Phi(-1/(2\sigma))\ge\Phi(-1/2)>0\). On every interval of length \(\pi\), the set where \(\sin^2(y+w)\ge1/2\) has measure \(\pi/2\). The Gaussian density is uniformly positive on \([-\pi/2,\pi/2]\). Therefore \(\mathbb E[|\nabla f(x_{t+1})|^2\mid x_t]\ge\frac12\Phi(-1/2)\frac\pi2\,\frac{\phi(2\pi)}{1/4}\simeq1.0345190\times10^{-9}>0\), uniformly in \(x_t\).



### Finding and scope

The asymptotic zero-error conclusion is false when its right side is zero. The finite-time theorem retaining \(+1/2\) is not disproved by this example.



### Proposed correction

Retain the \(d\epsilon_p^2\) contribution and selection-safe variance terms. A vanishing perturbation floor requires, for example, \(\epsilon_p=O((dT)^{-1/2})\), or no perturbation.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: Conditioning on no clipping destroys the isotropy identity

Assessment: supported; impact: minor



Source: Official PDF: Theorem B.7, pp. 30-33; terms T1, p. 31, and T4, p. 32.



### Source claim (paraphrase)

Theorem B.7's proof uses an unconditional isotropy/projection identity after conditioning on the directional queries not clipping.



### Analysis

The no-clipping event depends on the sampled direction. For \(G=I_2\), \(g=e_1\), \(u\) uniform on the radius-\(\sqrt2\) circle and \(Q=\{|u_1|\le1\}\), direct angular integration gives \(\Pr(Q)=1/2\) and \(\mathbb E[uu^\top\mid Q]=\operatorname{diag}(1-2/\pi,1+2/\pi)\). Consequently \(\mathbb E[GG^\top g-(g^\top Gu)Gu\mid Q]=(2/\pi)e_1\ne0\). The threshold illustrates the conditioning error; it is not asserted to be the optimized threshold in Theorem B.7.



### Finding and scope

Conditional isotropy needs a separate proof or a clipping-bias remainder. The full optimized convergence rate has not been disproved.



### Proposed correction

Work unconditionally. If \(Y^c\) is the clipped estimator, \(Y\) the unclipped estimator and \(p_t=\Pr(Q_t^c\mid\text{past})\), use \(\|\mathbb E(Y^c-Y)\|\le Mk p_t\) and \(\mathbb E\|Y^c\|^2\le2\mathbb E\|Y\|^2+2M^2k^2p_t\), then retain and bound the tail terms. The available replacement restricts to one direction and orthonormal \(G\).

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 5: The smoothing variable in Lemma B.2 must be a ball draw

Assessment: supported; impact: minor



Source: Official PDF: Lemma B.2(3), p. 15; ball-smoothing definition, p. 3.



### Source claim (paraphrase)

Lemma B.2 uses sphere smoothing in a formula requiring ball smoothing.



### Analysis

In dimension one, sphere smoothing of \(f(x)=\sin x\) gives gradient \(\cos(\lambda)\cos x\). The mean symmetric two-point estimator is \(\operatorname{sinc}(\lambda)\cos x\). These differ for general \(\lambda\), whereas uniform ball smoothing gives the required estimator identity.



### Finding and scope

Local correctable error, not evidence that every smoothing argument fails.



### Proposed correction

Use the uniform ball expectation, consistent with the main-text definition.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 6: Serial PAZO-S stores aliased candidate dictionaries

Assessment: supported; impact: minor



Source: Official supplement and pinned pinned author GitHub source: experiments/pazo-s.py, lines 159-179; GitHub mnli/pazo-s.py, lines 199-218, and experiments/pazo-s.py, line 77.



### Source claim (paraphrase)

Serial PAZO-S is intended to compare \(k\) public-gradient candidates and retain the privately selected one.



### Analysis

tmp_g is allocated outside the candidate loop and appended repeatedly; all candidate entries are the same dictionary. The serial file also references pre_trained whereas shared configuration uses pretrain.



### Finding and scope

The exercised serial helper collapses \(k\)-way public selection to the last candidate. Which published runs used these files remains unresolved; no table accuracy is invented or assumed to have been reproduced.



### Proposed correction

Allocate a fresh dictionary in each iteration and store detached cloned gradients, handling None consistently. Correct the pre_trained attribute reference. Add a real k-distinct-gradient regression fixture.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 7: MNLI vectorized PAZO-S uses candidate parameters as gradients

Assessment: supported; impact: minor



Source: Official supplement and pinned pinned author GitHub source: mnli/pazo-s_vec.py, lines 150-164.



### Source claim (paraphrase)

The vectorized candidate-selection branch should update the parameters corresponding to the candidate it evaluates.



### Analysis

The winning candidate variable best_g_noise contains parameters \(\theta-\eta(g+z)\), but the source assigns that value to p.grad before optimizer.step(). It therefore uses a candidate position as a gradient; that update does not generally equal the candidate evaluated by the private comparison.



### Finding and scope

The parameter actually updated differs from the candidate whose private loss won the selection. Defect is file-specific and present in both audited versions.



### Proposed correction

Represent candidate gradient and candidate parameters separately. Assign g+z to p.grad and evaluate the candidate consistent with the actual optimizer; if assigning parameters directly, reconcile momentum and weight-decay state.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 8: The implemented sampler is not the accountant's mechanism

Assessment: supported; impact: minor



Source: Official PDF: Section 3.4, pp. 5-6. pinned author GitHub source: trainers/model_base.py, lines 149-251; privacy_analysis/compute_privacy_sgm.py, lines 8-51; privacy_analysis/rdp_accountant.py, lines 355-399.



### Source claim (paraphrase)

The reported differential-privacy accounting is used with the author-released training sampler.



### Analysis

The author's fixed-size DataLoader uses shuffled epochs and drops the last incomplete batch. Its compute_rdp helper instead accounts for a sampled Gaussian mixture at \(q=b/n\). Epoch reshuffling is not that sampling mechanism; even independent fresh fixed-size batches would be a different rule. The code contains a separate without-replacement helper but does not use it on this path.



### Finding and scope

The displayed accounting does not establish the released loop's stated budgets. This is a certification-scope gap, not a proved numerical privacy violation. Counting all nominal epoch steps is conservative relative to dropping incomplete batches.



### Proposed correction

Use independent Poisson inclusion with fixed public expected-batch normalization and explicit empty-batch behavior, or supply a matching reshuffling accountant and adjacency analysis. Recompute budgets and handle PAZO-S's adaptive final query/shared batch explicitly.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 9: Private-derived preprocessing and diagnostics expand the privacy boundary

Assessment: supported; impact: minor



Source: Official PDF: Appendix C.1, p. 34. pinned author GitHub source: data/generate_imdb_vocab10k.py, lines 36-56 and 85-124; experiments/pazo-s.py, lines 148-153.



### Source claim (paraphrase)

The privacy interpretation must specify which preprocessing-dependent models and diagnostic outputs are released.



### Analysis

Deterministic top-token vocabulary is built from private training text, saved, and used for all datasets. Training code writes raw private accuracy and candidate diagnostics; data preparation prints decoded private examples.



### Finding and scope

The stated scalar mechanism does not protect the whole raw-record preprocessing/output pipeline. Conditional DP for fixed preprocessed examples is a narrower possible claim.



### Proposed correction

Fix a public tokenizer independently of protected records, or privately construct it with composed budget. Define the released object; privatize or exclude raw private diagnostics and data artifacts. Address private model selection and multiple released runs where applicable.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 10: The historical PAZO-M public-norm scaling has been corrected

Assessment: not_issue; impact: no_issue_found



Source: Official PDF: Algorithm 1, p. 4; Appendix A, p. 14; implementation disclosure, p. 34. Supplement and pinned author GitHub source: experiments/pazo-m.py, lines 85-90; mnli/pazo-m.py, lines 126-131.



### Source claim (paraphrase)

The older conference supplement scaled Gaussian search directions by the public-gradient norm. The latest author repository uses a different dimension-dependent scale.



### Analysis

The older public-norm rule has conditional mean \((\|g_{\rm pub}\|^2/d)\nabla f\), whereas the checked current author release uses \(Z/d^{1/4}\) in experiments/pazo-m.py and the corresponding MNLI implementation. Freshly retrieved current files confirm that the historical norm-dependent scaling is absent. This comparison identifies a code revision; it does not identify the revision used by the published runs.



### Finding and scope

The particular historical scaling defect is cleared as a current-source allegation. The current implementation and the original experimental provenance must remain separate.



## Problem 11: Fixed seeds and test-based stopping do not establish significance

Assessment: supported; impact: minor



Source: Official PDF: Appendix C.2, p. 34, and statistical-significance checklist, p. 43. pinned author GitHub source: experiments/pazo-s_vec.py, lines 62-92; mnli/pazo-s.py, lines 86-116.



### Source claim (paraphrase)

The paper uses fixed-seed and hyperparameter stability observations to discuss significance.



### Analysis

Paper acknowledges seed \(0\) and no error bars but claims significance from fixed seed and hyperparameter stability. Several code paths use test_accu for patience-based stopping.



### Finding and scope

Small reported advantages, especially \(0.2\) percentage points on Tiny-ImageNet at \(\varepsilon=0.1\), have no established statistical significance. Magnitude of selection bias is not quantified.



### Proposed correction

Use multiple independent seeds, paired per-seed comparisons and uncertainty; choose configurations/stopping on a validation split and evaluate once on a separate final holdout. Label existing results single-seed measurements.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 12: Data construction and model initialization are not reconciled

Assessment: supported; impact: minor



Source: Official PDF: experimental setup, pp. 7-8; Appendix C.1 and Table 3, pp. 34-35. pinned author GitHub source: data/generate_imdb_vocab10k.py, lines 72-75; data/generate_mnli_snli.py, lines 57-108 and 271-273; trainers/model_base.py, lines 84-89.



### Source claim (paraphrase)

The stated public-data sizes and model initialization describe the settings behind the reported tables.



### Analysis

Paper says \(2000\) public IMDB examples; generator selects \(1000\) with unspecified shuffle seed. Few-shot MNLI/SNLI script chooses first qualifying records and uses first \(1000\) dev_matched examples as test. Tiny model descriptions include pretrained ViT-small, random initialization, and code vit_tiny plus warmup weights.



### Finding and scope

An exact independent reproduction cannot identify the original setup solely from these artifacts. Public-only baseline and public warm-start disclosure are present and are not flagged as missing.



### Proposed correction

Publish exact split/index hashes, preprocessing seeds, model architecture identifier and initialization/checkpoint hashes per result. Reconcile paper text with the actual run recipe.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 13: The IMDB speedup ratio and timing interpretation

Assessment: supported; impact: minor



Source: Official PDF: Section 5.3, pp. 9-10; Tables 8-9, pp. 36-37. pinned author GitHub source: experiments/pazo-s.py, lines 138-145.



### Source claim (paraphrase)

The paper reports an IMDB speedup of up to fifteen times the comparison baseline.



### Analysis

IMDB largest baseline \(0.252\) seconds divided by fastest PAZO \(0.019\) is \(13.263\), not \(15\). Rounding cannot bridge the difference. Timing covers \(20\) iterations and does not specify explicit accelerator synchronization/warmup in the measurement code.



### Finding and scope

CIFAR up-to-\(16\times\) relative to GEP is supported by the table; not all runtime claims fail. No GPU performance reproduction was conducted.



### Proposed correction

Correct the IMDB ratio or publish the missing underlying timing that justifies it. Name the baseline for each speedup. Report synchronized repeated timings, warmup/compile treatment and end-to-end time to matched utility. Measure actual peak memory for memory claims.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.
