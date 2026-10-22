# MISA: Memory-Efficient LLMs Optimization with Module-wise Importance Sampling



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The unnormalized module-versus-layer objective ordering is reversed, and practical budget rejection can permanently exclude a nonstationary module. Separate release EMA and dense-backward accounting defects remain bounded findings.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Unnormalized module rewards do not dominate layer rewards

Assessment: supported; impact: major



Source: arXiv v3, Proposition 2, PDF p.6; conference Eqs.(2),(5), PDF pp.4–5



### Source claim (paraphrase)

The comparison maximizes expected squared module/layer gradient gain minus \(\eta^{-1}\) KL to its respective uniform distribution and asserts module-wise objective superiority.



### Analysis

Take two layers, each containing two scalar modules with gradient \(1\), and \(\eta=1\). Each layer gain is \(2\); each module gain is \(1\). Uniform distributions make the KL penalties zero, so the optimized values are \(V_{\rm layer}=2\), \(V_{\rm module}=1\). More generally the log-sum-exp variational identity and \(a_{ij}\le S_i=\sum_j a_{ij}\) imply \(V_{\rm module}(\eta)\le V_{\rm layer}(\eta)\), reversing the claimed weak ordering. These gradients are realizable in the globally smooth lower-bounded objective \(\sum_{\ell=1}^4(1-\cos\theta_\ell)\) at \(\theta_\ell=\pi/2\).



### Finding and scope

The unnormalized superiority argument is false; it compares different amounts of updated work. The softmax optimizer itself remains valid.



### Proposed correction

For equal module-count cost, use layer gain \(S_i/K\). Mapping \(q_{ij}=p_i/K\) preserves both this normalized gain and the KL, proving \(K^{-1}V_{\rm layer}(\eta/K)\le V_{\rm module}(\eta)\le V_{\rm layer}(\eta)\). This does not normalize unequal FLOPs or memory.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: Positive sampling weights need not give positive inclusion

Assessment: supported; impact: major



Source: arXiv v3, Algorithm 1, PDF p.7; analytical algorithm and convergence appendix; weighted_sample_without_replacement



### Source claim (paraphrase)

The practical method rejects selections above a parameter budget, while the analytical method samples a module directly and uses different inherited/maximal second moments.



### Analysis

Use modules with \(3\) and \(1\) parameters out of \(4\), budget fraction \(\delta=1/2\), and objective \(f=1-\cos\theta_1\), initialized at \(\theta_1=\pi/2\) in the larger module. That module’s ratio \(3/4>1/2\) never fits; the smaller module has zero gradient. All updates leave \(\|\nabla f\|^2=1\), despite global smoothness, bounded deterministic unbiased gradient and zero noise variance. Positive nominal probabilities and least-recently-used preferences cannot overcome a hard size exclusion.



### Finding and scope

An unrestricted convergence transfer to the practical budgeted sampler fails. This example does not contradict the analytical algorithm under its own direct-sampling assumptions or identify an excluded block in the reported LLM runs.



### Proposed correction

Every optimized block must fit, with suitable actual inclusion bounds and optimizer hypotheses, or the target must be restricted to movable parameters. No sufficient replacement practical convergence theorem is established.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: Repeated bias correction distorts the historical score

Assessment: supported; impact: minor



Source: block_coordinate_optimizer.py, lines 195–220 and 283–294; gradient-indicator equation



### Source claim (paraphrase)

The stored recurrence divides its already corrected EMA by \(1-\beta^t\) again at each observation.



### Analysis

For unit observations and \(\beta=0.8\), the source recurrence gives \(G_1=1\), \(G_2=1/(1-0.8^2)=25/9\), rather than the constant readout \(1\). Two equally strong modules with one and two observations then receive capped squared logits \(1\) and \(5\), hence probabilities approximately \(0.0179862\) and \(0.9820138\). Raw norm smoothing followed by squaring also differs from smoothing squared size-normalized gradients; modules with \(1\) and \(4\) unit-gradient parameters have raw norms \(1,2\) but equal size-normalized norms.



### Finding and scope

The inspected release’s indicator depends on observation count and an unmatched statistic. Its training effect and historical run correspondence remain unestablished.



### Proposed correction

Store raw \(M_t=\beta M_{t-1}+(1-\beta)x_t\) and compute separate readout \(M_t/(1-\beta^t)\). For constant \(x_t=x\), induction gives readout exactly \(x\). Reconcile the chosen score statistic separately.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 4: Backward FLOPs omit input-gradient products

Assessment: supported; impact: minor



Source: arXiv v3, Appendix F, PDF pp.42–45; conference Appendix G, PDF pp.41–43



### Source claim (paraphrase)

The dense-product convention yields printed quadratic coefficients \(34\) for full backward and \(10\) for frozen backward, in units \(bsh^2\).



### Analysis

For FFN input width \(h\) and hidden width \(4h\), propagating through the first projection requires \(\nabla Z=(\nabla Z_1\odot{\bf1})W_1^\top\), costing \(8bsh^2\). Q/K/V input gradients contribute another \(6bsh^2\). These products remain necessary in frozen layers above trainable parameters. Adding the missing \(14\) gives full/frozen coefficients \(48\) and \(24\), retaining the source’s other operation conventions. Input gradients may legitimately be pruned below the earliest active layer.



### Finding and scope

Absolute dense-backward counts are incomplete. The qualitative budget threshold can survive the same simplified comparison model; hardware runtime and all graph-pruning cases were not measured.



### Proposed correction

Include the explicit missing dense products; the resulting counts are \(48bsh^2+8bs^2h+2bas^2+14bsh\) and \(24bsh^2+8bs^2h+2bas^2+14bsh\) under the stated model.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
