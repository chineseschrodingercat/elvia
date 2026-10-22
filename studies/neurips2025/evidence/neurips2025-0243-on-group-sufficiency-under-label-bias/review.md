# On Group Sufficiency Under Label Bias



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The central sufficiency decomposition uses an invalid fixed marginal noise channel; multiclass conditioning and finite-sample bounds also have exact counterexamples. Additional objective/representation discrepancies and current release defects are separated from unverified benchmark effects.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: A fixed marginal channel does not invert score-conditional noise

Assessment: supported; impact: major



Source: Definition 3.4, PDF p.4; Theorem 4.1 Eq.(1), p.5; Appendix A.4 Eq.(10), p.19



### Source claim (paraphrase)

The proof uses \(\widetilde\pi(s)=T^\top\pi(s)\), with \(T=\sum_gP(G=g)T^g\), after removing group conditioning.



### Analysis

Let groups be uniform; two binary scores \(s_a=(1/3,2/3),s_b=(2/3,1/3)\) have \(P(s_a\mid G=0)=3/4\), \(P(s_a\mid G=1)=1/4\). Let \(Y\) be uniform independent of score/group, \(T^0=I\), \(T^1=\begin{pmatrix}3/4&1/4\\0&1\end{pmatrix}\). Noise is generated conditional on \((Y,G)\), all channels are invertible, and even \(Y\perp G\), so the unconditional channel really is the paper’s mixture. True group/marginal posteriors are all \((1/2,1/2)\), gap zero. Noisy marginal posteriors are \((15/32,17/32)\), \((13/32,19/32)\). Applying the fixed marginal inverse gives \((15/28,13/28)\), \((13/28,15/28)\), producing claimed normalized gap \(1/28\), not zero. Actual marginalized channel weights are \(P(G\mid Y,S)\), which need not be constant.



### Finding and scope

The central decomposition is false even in binary classification with every inverse and positive group-score cell. Uniform common channels remain a valid special case; no claim is made that every regularized model becomes less fair.



### Proposed correction

Use \(\pi(s)=\sum_hP(G=h\mid S=s)((T^h)^\top)^{-1}\widetilde\pi_h(s)\). This follows by total probability and the valid groupwise inverse. If retaining the coordinate metric, condition every posterior vector on the same scalar coordinate before inversion.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: Coordinate-conditioned and full-score sufficiency are different

Assessment: supported; impact: major



Source: Definitions 3.1–3.2, PDF p.4; Proposition 5.1, p.5; Appendix A.4 Eq.(9), p.19; A.7, p.21



### Source claim (paraphrase)

The metric conditions class \(k\) on scalar \(S_k\), while the theorem controls conditional independence and information given the full vector \(S\).



### Analysis

Use uniform groups and score weights \(3/4,1/4\) as above, \(s_a=(1/3,1/6,1/2),s_b=(1/3,1/2,1/6)\). Let label posteriors given these scores be \((3/4,1/8,1/8)\), \((1/4,3/8,3/8)\), independent of group given score, with identity noise. Thus \(I(Y;G\mid S)=0\) and full-vector gap zero. But \(S_1=1/3\) is constant: class-one group probabilities are \(5/8,3/8\), marginal \(1/2\), discrepancy \(1/8\). Other coordinates distinguish the scores, giving coordinate \(p=1\) gap \(1/24>0\), while the stated information upper bound is zero. Binary coordinates determine the full vector, so the explicit binary lemma is not refuted.



### Finding and scope

The literal multiclass metric/guarantee identification fails, including its uniform-noise interpretation. No calibration assumption in the statement excludes this interior-simplex example.



### Proposed correction

Either use full-vector gap \(D_{g,1}=K^{-1}E[\|\pi_g(S)-\pi(S)\|_1\mid G=g]\), for which Pinsker gives \(\sqrt2\,K^{-1}\sqrt{I/P(G=g)}\), or retain coordinate information \(I_k=I(1_{\{Y=k\}};G\mid S_k)\) and bound the coordinate gap by \[K^{-1}\sum_k\sqrt{I_k/(2P(G=g))}\]. These control different targets.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: The information-bound constant does not extend unchanged above one

Assessment: supported; impact: minor



Source: Proposition 5.1, PDF p.5; Appendix A.7 extension claim, p.21



### Source claim (paraphrase)

The \(p=1\) constant \(\sqrt2/K\) and square-root exponent are extended without restriction to the \(p\)-gap.



### Analysis

At constant score, equal groups, identity noise, take \(K=3\) posteriors \((0.9,0.05,0.05)\), \((0.05,0.9,0.05)\), marginal \((0.475,0.475,0.05)\). Scalar/full conditioning agree. The \(p=2\) normalized gap is \(\sqrt{2(0.425)^2/3}=0.3470110469\); information is \(0.9\log(0.9/0.475)+0.05\log(0.05/0.475)=0.4626073734\). The printed overall bound is \(0.3206269461\), too small.



### Finding and scope

The unrestricted extension is false; the corrected full-vector \(p=1\) proposition survives. Experiments explicitly using \(p=1\) are not refuted by this extension issue.



### Proposed correction

For full-vector gaps, \(1\le p\le2\) admits factor \[2^{1/p-1/2}K^{-1/p}\sqrt{I/P(G=g)}\]; \(p\ge2\) admits \(K^{-1/p}(I/P(G=g))^{1/p}\). Positive/negative probability-difference masses both equal TV, so \(\|P-Q\|_p^p\le2\,TV^p\); Pinsker and Jensen prove the stated bounds. Coordinate conditioning still needs its separate repair.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 4: Inverse-noise concentration cannot be uniform over conditioning

Assessment: supported; impact: major



Source: Lemma A.6, PDF p.23; Eq.(8), p.6



### Source claim (paraphrase)

The oracle estimator is noise-inverted, but its radius \[3\sqrt2\log(1/\epsilon)\sqrt{\log(6/\delta)/n}\] has no inverse-channel factor.



### Analysis

At constant score and uniform groups, let true class-one probabilities be \(3/4,1/4\), so all relevant probabilities exceed \(\epsilon=0.1\). Use symmetric invertible channel \(T_\eta=\begin{pmatrix}1/2+\eta&1/2-\eta\\1/2-\eta&1/2+\eta\end{pmatrix}\), \(\eta=10^{-4}\). The exact oracle summand is \(m\pm d\), \(m=\tfrac12\log(3/4)\), \(d=\log3/(4\eta)\), with plus probability \(q=1/2+\eta/2\). Hence \(\widehat I_n=m+d(2B/n-1)\), \(B\sim\mathrm{Bin}(n,q)\). At \(n=100,\delta=0.05\), claimed radius \(2.1374991968\) passes only \(B=50\); failure is \(1-\binom{100}{50}q^{50}(1-q)^{50}=0.9204108024\), not at most \(0.05\). Distinct channels \(T_\eta,T_{2\eta}\) also give probability-one failure at \(n=1\).



### Finding and scope

The finite-sample guarantee is false. The proof concentrates a different clean-label plug-in variable. Oracle backward correction can remain unbiased; clipping changes bias and does not prove the unclipped theorem.



### Proposed correction

Let \(M=\max_g\|(T^g)^{-1}\|_\infty\), \(L=\log(1/\epsilon)\). The actual summand has magnitude at most \(ML\), so Hoeffding gives radius \(ML\sqrt{2\log(2/\delta)/n}\). Preserve the group-probability factor when translating it to a sufficiency bound; nearly singular channels can make it uninformative.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 5: The shared forward-corrected head need not learn the marginal

Assessment: supported; impact: major



Source: Section 5, Eqs.(6)–(8), PDF p.6; oracle premise in Lemma A.5



### Source claim (paraphrase)

The group-agnostic head uses group-specific forward correction, then is treated as the clean marginal posterior.



### Analysis

At constant score, equal groups and class-one probabilities \(0.8,0.2\), take \(T^0=I\), \(T^1=\begin{pmatrix}.75&.25\\.25&.75\end{pmatrix}\). Required marginal is \(h=0.5\), but population risk is \(R(h)=\tfrac12 CE(.8,h)+\tfrac12 CE(.35,.25+.5h)\). Its derivative at \(0.5\) is exactly \(-0.45\), and its unique strictly convex optimum is approximately \(0.6911801733\). An intercept head represents either constant, so this is neither capacity nor optimization failure. Equal clean group posteriors or identical channels are valid exceptions.



### Finding and scope

The proposed population objective does not generally justify the oracle marginal premise. Conditional unbiasedness with genuine oracle heads remains valid; usefulness of heuristic gradients is not refuted.



### Proposed correction

Backward-corrected cross entropy satisfies \[E[[(T^G)^{-1}(-\log h(S))]_{\widetilde Y}]=E[-\log h_Y(S)]\], giving the desired representable population minimizer. Its finite-sample variance/negative losses need separate care. Alternatively mix estimated clean group posteriors with score-conditional group weights.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 6: Uncentered logits condition on extra information

Assessment: supported; impact: major



Source: Last paragraph, PDF pp.6–7; Algorithm 1, p.7; probability-score target in Definition 3.1



### Source claim (paraphrase)

The implemented/stated heads use raw logits, although sufficiency is defined for their softmax probability score.



### Analysis

Let uniform \(G\) determine logits \(Z=(0,0)\) or \((1,1)\), and label probabilities \(0.8,0.2\). Identity noise meets the assumptions. Score \(S=(0.5,0.5)\) is constant, with probability-score CMI \(0.1927447570\) and normalized gap \(0.3\). Yet \(G\) is determined by \(Z\), so \(I(Y;G\mid Z)=0\). Linear affine log-odds heads represent the two true posteriors, so the ideal logit regularizer can vanish without a capacity defect.



### Finding and scope

Zero logit-conditioned CMI does not certify sufficiency of the reported probability score. A logit target can be intentional, but is a different guarantee.



### Proposed correction

Use probability scores or centered logits \(Z^\circ=Z-K^{-1}(\mathbf1^\top Z)\mathbf1\). For finite logits, \(Z^\circ_k=\log S_k-K^{-1}\sum_j\log S_j\), so the two representations determine one another and condition on the same information. Other objective/metric issues remain.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 7: The default CMI path softmaxes auxiliary outputs twice

Assessment: supported; impact: minor



Source: algorithms.py, MI_Forward.calc_loss lines 223–252 and _backward_ce lines 170–185; Eq.(8), PDF p.6



### Source claim (paraphrase)

calc_loss first converts head logits to probabilities, then the entropy helper softmaxes those probabilities again.



### Analysis

With exact marginal head \((0.5,0.5)\), exact group heads \((0.8,0.2)\), \((0.2,0.8)\), equal groups, identity noise and batch counts \(8:2,2:8\), true information is \(0.1927447570\). A second softmax maps \(0.8\) to \(r=e^{.8}/(e^{.8}+e^{.2})=0.6456563062\). The resulting entropy difference is \(\log2+.8\log r+.2\log(1-r)=0.1356592301\). Both values lie within the optional clipping range. Existing MI_Forward2 passes raw logits and avoids this extra transform, but the inspected default/registry chooses MI_Forward.



### Finding and scope

The post-publication default release differs from the displayed entropy estimator. Historical experiment code, learned-head accuracy and model-ranking effect remain unestablished.



### Proposed correction

Use the existing raw-logit convention consistently for both heads, or a helper explicitly accepting probabilities without another softmax. This local correction does not solve population-head or representation issues.

The author repository already contains the corrective raw-logit MI_Forward2 variant; adoption in the inspected default/registry is not established.



## Problem 8: Inverse-column softmax corrupts identity-channel pseudo-labels

Assessment: supported; impact: minor



Source: MC baseline, PDF p.8; algorithms.py, MC._sample_clean_labels lines 833–846; calibration-label path in train.py



### Source claim (paraphrase)

The MC baseline softmaxes a column of the inverse channel and samples it as a pseudo-clean label distribution.



### Analysis

For \(T^g=I_K\), the inverse column is \(e_j\), so the correct observed label is retained only with probability \(e/(e+K-1)\). Expected flips are \(1/(e+1)=0.2689414214\) for binary labels and \(13/(e+13)=0.8270624068\) at \(K=14\), despite zero noise. General inverses need not be stochastic: symmetric \(0.75/0.25\) noise has inverse entries \(1.5,-0.5\). Row normalization does not remove negatives, and softmax supplies no inverse-noise justification.



### Finding and scope

The released baseline uses an altered label process even for noiseless groups. No comparison-ranking change or failure of multicalibration itself is established.



### Proposed correction

Identity channels must preserve labels. General resampling needs a Bayes posterior proportional to \(\pi_i(x,g)T^g_{ij}\), with an explicitly estimated clean prior/posterior; signed inverse weights can instead correct expectations without pretending to be sampling probabilities. No universal pseudo-label repair is certified.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 9: Nonzero noise can preserve a balanced calibrated posterior

Assessment: supported; impact: minor



Source: Text immediately following Theorem A.2, PDF p.18



### Source claim (paraphrase)

The text infers strictly positive true-label calibration error of the noisy Bayes score whenever noise is nonzero.



### Analysis

Let \(Y\) be independent of input with probability \(1/2\), and use symmetric channel \(\begin{pmatrix}.8&.2\\.2&.8\end{pmatrix}\), determinant \(0.6\). The noisy Bayes score remains \((.5,.5)\), exactly calibrated to true labels. More generally binary flip rates \(a,b\) give \(q=b+(1-a-b)p\), discrepancy \(|b-(a+b)p|\), zero at the fixed posterior \(p=b/(a+b)\). A reverse-triangle lower bound that may be negative cannot imply strict positivity.



### Finding and scope

The local inevitability statement requires qualification. It does not refute the consistently conditioned reverse-triangle inequality or the possibility that label bias harms calibration.



### Proposed correction

State positivity only when the score law gives positive mass away from the channel’s fixed posterior; preserve the balanced symmetric-noise exception.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
