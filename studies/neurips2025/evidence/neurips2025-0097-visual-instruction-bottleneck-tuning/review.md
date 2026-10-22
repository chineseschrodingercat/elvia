# Visual Instruction Bottleneck Tuning



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The actual interpolated decoder law is not controlled by the auxiliary KL, so the claimed common-latent information-bottleneck lower bound fails. Public KL/routing bugs and deletion of a valid bound’s residual term have separate scopes.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: The released Gaussian KL halves the log-variance term

Assessment: supported; impact: minor



Source: Appendix A.2, PDF p.28, Eq.(8); vittle_llama.py, lines 252–289; repository issue #1



### Source claim (paraphrase)

The paper’s Gaussian KL is correct, but `vib_kld_loss` and `vib_kld_loss_lp` use half the required additive log-variance ratio.



### Analysis

At zero means, posterior variance \(1/2\), prior variance \(1\), the release returns \(-0.0767132\) instead of \(0.0965736\), within its clamps. At matching log variance \(s=0\), its derivative is \(1/4\) instead of zero; the fixed-prior minimum shifts to variance \(1/2\). The learned-prior mismatch was already raised in repository issue #1 on 28 January 2026.



### Finding and scope

The later release computes neither the stated KL values nor gradients. Original checkpoint training is not identified.



### Proposed correction

Use \(\tfrac12[\log(v_p/v_q)-1+(v_q+(m_q-m_p)^2)/v_p]\), with consistent coordinate reduction.

Repository issue #1 already identifies the learned-prior coefficient mismatch; no author adoption of this correction is established.



## Problem 2: Sequence length does not identify modality positions

Assessment: supported; impact: minor



Source: Section 3.3, PDF p.5; Appendix A.2, PDF pp.28–29; vittle_arch.py packing and vittle_llama.py, lines 312–334 and 439–490



### Source claim (paraphrase)

The public packing path replaces image sentinels in place, while the bottleneck route infers a visual prefix from total-length subtraction.



### Analysis

IDs \([1,2,\mathrm{image},3,4]\) expanded with visual rows \([101,102,103]\) become \([1,2,101,102,103,3,4]\). True visual indices are \(\{2,3,4\}\), but the inferred count \(7-5=2\) selects prefix \(\{0,1\}\), both text. Replacing one sentinel increases length by \(n-1\), not \(n\), even when the image is first. Embedding-only input sets the inferred visual count to zero in the inspected branch.



### Finding and scope

The public route does not implement the intended modality split. Full intended-version generation behavior and benchmark effects are unmeasured.



### Proposed correction

Carry an explicit visual-token mask through expansion, padding, truncation and cached generation; exclude padding separately.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: The skip contribution breaks the common-latent lower bound

Assessment: supported; impact: major



Source: Eqs.(2)–(5), PDF p.4; Section 3.3 and footnote 2, PDF p.5; Implication paragraph, PDF p.6; Appendix D, PDF p.38



### Source claim (paraphrase)

Section 3.2 introduces Eq.(4) as a variational IB lower bound and Eq.(5) as its empirical estimate. The implemented likelihood receives \(\hat Z=(1-\alpha)c(X)+\alpha\tilde Z\), while the KL regularizes unmixed \(\tilde Z\). Footnote 2 and Appendix D explicitly acknowledge the different laws, yet the p.6 Implication paragraph still says that Vittle maximizes the variational IB lower bound.



### Analysis

Let \(X=\pm2\) equally, label \(Y\) constant, \(c(X)=X\), and \(\tilde Z\mid X\sim\mathcal N(0,1)\) matching its prior independently of \(X\). At \(\alpha=1/2\), the mixed objective is zero for a decoder assigning the sole label probability one. Yet \(\hat Z\mid X=\pm2\sim\mathcal N(\pm1,1/4)\), so \(I(X;\hat Z)>0\), while \(I(Y;\hat Z)=0\). The actual information-bottleneck value is \(-\beta I(X;\hat Z)<0\), so zero is above rather than below it. A finite-softmax likelihood arbitrarily close to zero preserves the strict contradiction.



### Finding and scope

The stated auxiliary-KL objective is not a general lower bound for the representation actually decoded. A useful auxiliary regularizer remains a different interpretation.



### Proposed correction

Use the same mixed law \(\mathcal N((1-\alpha)c+\alpha\mu,\alpha^2\operatorname{diag}\sigma^2)\) in likelihood and KL to an input-independent prior, with any modality-factorization assumptions explicit.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 4: Conditional independence does not eliminate input-shift residuals

Assessment: supported; impact: minor



Source: Proposition 3.2 and interpretation after Eq.(7), PDF p.6; Appendix E.2, PDF pp.39–41



### Source claim (paraphrase)

After Proposition 3.2, the interpretation drops \(\Delta_{X\mid Z}\) because model output is conditionally independent of input given the representation.



### Analysis

Let domain \(P\) concentrate on input \(a\), and \(Q\) be uniform on \(b,c\). Use one label kernel: a fair label at \(a\), label zero at \(b\), label one at \(c\). Let latents be domain-identical and input-independent, and model output a fair independent label. Conditional independence holds; all retained latent-divergence and marginal entropy-gap terms are zero. True mutual information changes from zero to \(\log2\), so EMID is \(\log2\). The residual is \(2\log2\); retaining it leaves the full proposition uncontradicted. Lowering model entropy can also enlarge an absolute gap to a fixed fair-target entropy.



### Finding and scope

Only the deletion/monotonic interpretation fails; the full printed bound survives this example.



### Proposed correction

Retain the residual unless conditional input laws agree across domains on the relevant representation fibres. Keep entropy terms as absolute gaps rather than assuming lower model entropy always improves them.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.

- The April 2026 public code postdates the conference; the exact historical checkpoint-training program is not established.
