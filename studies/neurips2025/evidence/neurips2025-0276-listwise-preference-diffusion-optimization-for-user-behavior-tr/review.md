# Listwise Preference Diffusion Optimization for User Behavior Trajectories Prediction



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The central ELBO bridge changes the likelihood being bounded and uses incompatible endpoint measures. Separate release defects affect NDCG direction, weighted ranking loss, sample aggregation and sampler settings; no corrected benchmark is inferred.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: The NDCG helper rewards worse positions within the cutoff

Assessment: supported; impact: minor



Source: Section 5.1; calculate_hit metric helper and descending top-k call



### Source claim (paraphrase)

The release transforms zero-based relevant-item position into cutoff minus position before logarithmic discounting.



### Analysis

At cutoff \(K=5\), the best-ranked relevant item receives \(1/\log_2 6\), while the fifth-ranked receives \(1\). Standard single-relevant-item NDCG gives the reverse. The source requests descending sorted scores, so ascending order cannot explain the transformation. Repeating these positions across a trajectory preserves the reversal under the geometric mean.



### Finding and scope

The release does not compute conventional NDCG. HR is unaffected by this rank transformation; effects on published relative rankings require actual predictions and table lineage.



### Proposed correction

Use one-based rank \(r\) and discount \(1/\log_2(r+1)\), with zero for misses; recompute saved predictions and any affected validation selection.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Multiplicative logit masking does not implement Soft-ListMLE

Assessment: supported; impact: minor



Source: Equation (9); model/LPDO.py, list_preference_loss, lines 264–272



### Source claim (paraphrase)

The formula weights exponentiated scores of previously selected items by \(\gamma\); the active release multiplies their logits by \(\gamma\).



### Analysis

Use candidates \(A,B\), non-repeating target \((A,B)\), and identical score rows \((\log4,0)\). The first loss is \(\log(5/4)\) for both rules. At the second position the printed loss is \(\log(1+4\gamma)\), versus released \(\log(1+4^\gamma)\). At \(\gamma=0\) these are \(0\) and \(\log2\); at \(\gamma=1\) they agree. Score-shift invariance also holds for weighted probabilities but fails for multiplicatively masked logits.



### Finding and scope

The active surrogate differs even in the original tied-score, non-repeating domain. This does not establish poorer empirical predictions.



### Proposed correction

For non-repeating targets, add \(\log m_i\) to logits, with \(\log0=-\infty\), instead of multiplying by \(m_i\). Repeated targets require an explicit normalized sequential rule.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: The softened expression needs an explicit sample-space convention

Assessment: not_issue; impact: minor



Source: Equation (9) and Section 4.3 likelihood interpretation



### Source claim (paraphrase)

The softened ListMLE factors are used as a likelihood, without fully specifying how repeated trajectories receive mass.



### Analysis

For two candidates with scores \((\log4,0)\) and \(\gamma=0.3\), the two permutation weights are \(4/11\) and \(8/43\), totaling \(260/473<1\). However a repeat-capable sequential model with numerator weight \(\gamma\) on already selected items is normalized and retains both non-repeating path values. A permutation-mass deficit alone therefore does not refute every likelihood interpretation.



### Finding and scope

The repeated-outcome numerator and sample space need specification. A coherent extension exists, so this is a scoped clarification rather than an established impossibility.



## Problem 4: The central ELBO derivation interchanges marginal and shared-chain likelihoods

Assessment: supported; impact: major



Source: Sections 4.3–4.4, Eqs. (12)–(15); Appendix B.2 and Appendix C



### Source claim (paraphrase)

The derivation replaces a sum of item-chain joint log densities with only one chain log density, then identifies a shared-chain joint bound with a sum of marginal log-likelihoods.



### Analysis

For a normalized chain density \(P(x)\) and normalized emissions \(r_j\), the product rule gives \[\sum_{j=1}^k\log[P(x)r_j(i_j\mid x)]=k\log P(x)+\sum_j\log r_j(i_j\mid x).\] A shared-chain joint has coefficient one, but its marginal is \(\int P\prod_jr_j\), not the product of separate marginal integrals. With \(X\sim N(0,1)\), \(r(A\mid x)=e^{-x^2/2}\), trajectory \((A,A)\) has joint negative log-likelihood \((\log3)/2\), versus summed marginal negative log-likelihood \(\log2\). The exact joint posterior \(N(0,1/3)\) makes the one-chain variational bound equal \((\log3)/2<\log2\), so it cannot bound both objectives as asserted. Appendix B.2 also uses a point-mass embedding against a continuous kernel, yielding infinite endpoint KL, and labels conditionals over different variables a KL without a common measure.



### Finding and scope

The claimed tight variational derivation does not establish the stated objective. The heuristic loss can remain useful; no accuracy result is inferred false.



### Proposed correction

Specify a normalized sequence emission and choose either a shared-chain joint ELBO or separate marginal ELBOs with the appropriate repeated chain terms. Treat deterministic embedding endpoints with a compatible reconstruction likelihood or nondegenerate variational model.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 5: Unequal evaluation batches receive equal weight

Assessment: supported; impact: minor



Source: Equation (20); main.py, evaluate aggregation



### Source claim (paraphrase)

The evaluator averages batch means rather than all user-level values.



### Analysis

Three complete-match indicators \((0,0,1)\), partitioned into batches of sizes \((2,1)\), produce \((0+1)/2=1/2\), although the dataset fraction is \(1/3\). The same predictions in one batch give \(1/3\). Equal-size batches are a valid special case. Sequence negative log-likelihood is also averaged this way; per-item log perplexity would additionally divide sequence NLL by fixed trajectory length.



### Finding and scope

The released metrics can depend on evaluation partition. Corrected tables cannot be reconstructed from aggregate means alone.



### Proposed correction

Accumulate sample numerators and counts, or weight each batch mean by its actual size before sequence aggregation.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 6: Released loss weights and sampling settings differ from the description

Assessment: supported; impact: minor



Source: Equation (16), experimental setup; model/LPDO.py, p_losses and sample; main.py sampler construction



### Source claim (paraphrase)

The code swaps ranking/reconstruction coefficients, scales linear noise endpoints by \(1000/T\), and iterates all configured diffusion steps.



### Analysis

The release computes \(\lambda L_{\rm rank}+(1-\lambda)L_{\rm MSE}+L_{\rm reg}\), while Eq. (16) assigns \(\lambda\) to reconstruction. They differ unless \(\lambda=1/2\) or component values coincide. With \(T=50\) and requested endpoints \(0.0001,0.02\), the source uses \(0.002,0.4\). Its sample loop calls the denoiser at every step, with no distinct one-step inference setting on the documented path.



### Finding and scope

The documented release cannot be assumed to reproduce the printed objective, numerical schedule or advertised one-step cost. The historical configuration behind each timing row is unresolved.



### Proposed correction

Identify the experimental source/configuration and reconcile the description. A separate consistent inference schedule is needed; setting the global training-step argument to one is not a validated one-step sampler repair.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
