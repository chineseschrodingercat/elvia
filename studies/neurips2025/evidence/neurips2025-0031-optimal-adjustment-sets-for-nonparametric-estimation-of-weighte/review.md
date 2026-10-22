# Optimal Adjustment Sets for Nonparametric Estimation of Weighted Controlled Direct Effect



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The universal O-set variance-optimality theorem has a positive-support counterexample, and the paper's half-residual AIPW formula fails the intended bias cancellation. These core estimation errors determine Major. ASIA support restrictions and necessity wording remain bounded corrections; not every influence-function component is invalid.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: The O-set need not minimize asymptotic variance

Assessment: supported; impact: major



Source: Current arXiv v4 Theorem 4.3 and Definitions 4.1–4.2, PDF pp.6–7; Appendix C.5 proof



### Source claim (paraphrase)

Theorem 4.3 says all non-treatment parents of Y form a universally variance-optimal allowed adjustment set.



### Analysis

Use the DAG \(A\to B\to W\to Y\), \(A\to Y\), \(E\to W\). Let \(A,E\) be independent Bernoulli-\(1/2\), \(\Pr(B=1\mid A)=1/4+A/2\), and \(\Pr(W=1\mid B,E)=1/20\) when \(B=E\), \(19/20\) otherwise. Let \(Y=AW+\epsilon\), with independent noise variance \(1/100\). All sixteen discrete cells have positive probability, the stated adjustment conditions hold, and WCDE is \(1/2\).

The mediator set is \(M=\{B,W\}\); choose \(Z_1=\{B\}\), \(Z_2=\{E\}\). The only mediated path is blocked by \(B\), and fixing \(A,B\) gives \(\mathbb E[Y\mid do(A=a,B=b)]=a/2\). Condition C3 requires only \(W\perp A\mid B\), which holds; it does not require \(W\perp E\mid B\). For \(O=\{W\}\), the contrast influence function is \(2(2A-1)\epsilon+W-1/2\). For \(Z\), it is \[\frac{A}{\pi(B)}(W-q(B,E)+\epsilon)-\frac{1-A}{1-\pi(B)}\epsilon,\qquad\pi(0)=1/4,\quad\pi(1)=3/4.\] These give the variances below directly.

Substituting these probabilities and regressions into the paper's unrestricted-observation influence function gives asymptotic variance \(29/100\) for \(O=\{W\}\) and \(9/50\) for \(Z=\{B,E\}\). Since \(9/50<29/100\), the asserted universally optimal O-set is not optimal. These are the paper-defined variances, not a comparison to a graph-model efficient bound.



### Finding and scope

The universal optimal-adjustment theorem is false under its own admissibility and positivity conditions; the influence-function identity itself is not refuted.



### Proposed correction

Restrict or re-establish the optimality theorem. No general replacement optimal set is proved; the reported influence function itself remains a valid retained component.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: The estimator halves the residual correction

Assessment: supported; impact: major



Source: Paper Eq. (5.1), p. 9; author asia.py, lines 205-212, and parallel released estimator implementations.



### Source claim (paraphrase)

Eq.5.1 is presented as an influence-function-based AIPW construction.



### Analysis

Eq. (\(5.1\))'s outer \(1/2\) multiplies one inverse-probability residual term and two marginal regression terms. It therefore equals a plug-in estimate plus half the required residual correction. With correct weights and limiting regression \(\nu\), its limit is \((T_{\rm true}+T_\nu)/2\), not generally \(T_{\rm true}\). In the explicit positive-support case with \(T_{\rm true}=1/2\) and \(T_\nu=0\), this is \(1/4\). Correct nuisance regression can hide the bias.



### Finding and scope

The printed AIPW formula does not retain the full residual correction, so its stated nuisance-robustness interpretation fails. Published finite-sample scores were not recalculated.



### Proposed correction

Double the residual correction inside the overall one-half factor. This algebra restores that cancellation identity; flexible-nuisance regularity/normality needs additional conditions.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: Four ASIA comparisons lack structural positivity

Assessment: supported; impact: minor



Source: Paper Table 3, pp. 9-10; author-released asia.bif, either and lung conditional probability tables.



### Source claim (paraphrase)

Table 3 uses seven adjustment sets to compare nonparametric regular-estimator efficiency.



### Analysis

The author's ASIA CPT forces either \(=1\) whenever lung \(=1\). Thus \(\Pr(\mathrm{either}=0,\mathrm{lung}=1)=0\), although \(\Pr(\mathrm{lung}=1)=11/200>0\). Four compared adjustment sets containing lung require unsupported outcome cells. Extrapolation does not supply nonparametric overlap; the three sets without lung retain support, and the supported O-set effect remains \(3/8\).



### Finding and scope

Four ASIA adjustment comparisons lack the required outcome-cell support. The supported comparisons and the O-set effect remain valid controls.



### Proposed correction

Exclude unsupported sets from the nonparametric efficiency comparison or label the extra outcome-extrapolation model; full table reruns remain undone.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: C3 necessity must distinguish means from contrasts

Assessment: supported; impact: minor



Source: Lemma 2.6, p.4; Appendix B.1, pp.27–28; CDE counterevidence pp.24–25.



### Source claim (paraphrase)

Lemma 2.6 calls the adjustment conditions both sufficient and necessary for WCDE.



### Analysis

In the graph \(A\to B\to W\to Y\), \(C\to W\), \(C\to Y\), with no direct \(A\to Y\), condition C3 fails for \(Z_1=\{B\},Z_2=\{C\}\). Yet \(Y\perp A\mid B,C\), so the standardized treatment contrast is zero, matching the controlled direct effect for every Markov law on that graph. Two treatment-specific means can be misidentified while their difference cancels. The authors already discuss this distinction for CDE.



### Finding and scope

The claimed necessity condition is too strong for a contrast whose two mean-identification errors cancel. Its sufficiency and nonzero-effect applications are not refuted.



### Proposed correction

Narrow the necessity claim to its correctly established target/domain. No new complete necessary-and-sufficient adjustment criterion is provided.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- No new author-code execution, model spending, training, author contact or complete benchmark replication.

- Historical numerical results are retained evidence rather than current reruns.

- Local counterexamples do not invalidate every empirical result; missing historical run attribution remains unresolved.
