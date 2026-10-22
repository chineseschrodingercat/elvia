# Modeling Neural Activity with Conditionally Linear Dynamical Systems



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current preliminary public M-step uses static residual covariances for a condition-varying returned model and omits noise covariance in selected GP mean/bias regressions. Exact realizable Gaussian posterior examples contradict those updates; the paper’s Sylvester equation remains correct.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: Static residuals do not fit the returned conditional model

Assessment: supported; impact: minor



Source: models.py, m_step, lines 657–735; paper Eq.(6)



### Source claim (paraphrase)

The code estimates noise covariance from a static coefficient, then returns different condition-dependent GP coefficients. In the active emission-GP branch its static coefficient is discarded.



### Analysis

Use two scalar times, independent standard-normal states, conditions \(0,1\), basis \(\phi(u)=\cos(\pi u)\), current emission coefficient \(w=1\), noise \(q=0.01\), observations \((1,-1)\). Exact Gaussian conditioning gives both posterior means \(m=100/101\), variance \(v=1/101\), and \(s=m^2+v\). The covariance-aware update is \(w_+=2m/(2s+q)\approx0.9948773666\). Static cross-statistics cancel, so the code returns variance \(1\). The actual returned coefficient’s expected residual is \(e=1-2w_+m+w_+^2s\approx0.01002399949\). For fixed coefficient, objective \(\log R+e/R\) has derivative \((R-e)/R^2\), nonzero at the returned \(R=1\), and unique minimizer \(R=e\). These are realizable E-step moments, not arbitrary statistics.



### Finding and scope

The returned emission block is not an exact conditional noise maximizer. The code’s explicit TODO already acknowledges static dynamics statistics; no priority claim or universal full-iteration failure is made.



### Proposed correction

Compute each new covariance from the expected residual of the actually selected conditional coefficients, including posterior variance/cross-covariance. With positive definite residual sum \(S\), minimizing \(n\log\det\Sigma+\operatorname{tr}(\Sigma^{-1}S)\) gives \(\Sigma=S/n\). Coupled coefficient updates still need a coherent common-objective schedule.

The current repository explicitly flags static dynamics covariance statistics as a TODO. No completed author correction is established for the broader returned-model residual mismatch.



## Problem 2: The GP bias/mean normal equation omits noise covariance

Assessment: supported; impact: minor



Source: models.py, fit_gplinear_regression, lines 663–670; bias/initial-mean calls, lines 690 and 715; Eq.(6)



### Source claim (paraphrase)

With a unit Gaussian weight prior and general noise covariance, the correct normal equation is \(GW+W\Sigma=B\). The helper instead solves \((G+I)W=B\).



### Analysis

Use scalar dynamics \(A=0\), one constant bias basis, current bias zero, initial variance \(1\), dynamics variance \(Q=4\), observation variance \(1\), emissions \(1\), observations \((0,1.25)\). Exact posterior means are \((0,1)\) and variances \((1/2,0.8)\). Holding dynamics fixed gives bias statistics \(G=B=1\). The helper returns \(0.5\); the covariance-aware update is \(1/(1+4)=0.2\). Its expected objective \(J(b)=[(1-b)^2+0.8]/8+b^2/2\) has derivative \((b-1)/4+b\), equal to \(0.375\) at \(0.5\) and zero uniquely at \(0.2\). No whitening or changed prior is supplied in that call.



### Finding and scope

The helper is correct for identity covariance, but does not generally implement the paper’s MAP update. The initial-mean branch has the same omission; its coupled covariance update is not certified by this local fix.



### Proposed correction

Solve \(GW+W\Sigma=B\), using the relevant dynamics or initial covariance. For \(G\succeq0,\Sigma\succ0\), the Kronecker-sum eigenvalues are positive, proving a unique conditional minimizer. Preserve actual residuals and coupled-block ordering.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.
