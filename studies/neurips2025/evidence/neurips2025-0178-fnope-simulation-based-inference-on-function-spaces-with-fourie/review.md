# FNOPE: Simulation-based inference on function spaces with Fourier Neural Operators



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Current author-main code still uses an observed-range histogram for the stated full-interval calibration metric and repeats the final seed in a log-probability aggregation loop. The older supplementâ€™s Gaussian covariance mismatch is already absent from the current author release.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: The implemented histogram is not the full-interval EoD

Assessment: supported; impact: minor



Source: Appendix S2.2, PDF p.16; current evaluation_utils.py, run_sbc_save_results



### Source claim (paraphrase)

The paper defines \(E=\int_0^1|F(\alpha)-\alpha|\,d\alpha\). Current code chooses its histogram range from observed ranks and averages boundary errors.



### Analysis

Take ten normalized ranks, five \(0.49\) and five \(0.51\). The empirical CDF is \(0\), then \(1/2\), then \(1\). Exact integration gives \(0.12005+0.00005+0.00005+0.12005=0.2402\). With thirty bins over the observed interval \([0.49,0.51]\), the released boundary mean is approximately \(0.0361290\); refining bins approaches \(0.005\), omitting both major tails. The exact input can arise as ranks \(49,51\) among \(100\) posterior samples.



### Finding and scope

The current computation does not generally evaluate or converge to the specified metric. It does not prove any published posterior is miscalibrated or any model ranking reverses.



### Proposed correction

Integrate the actual empirical CDF over breakpoints including \(0,1\). On each constant-CDF interval use antiderivative \(\tfrac12(\alpha-c)|\alpha-c|\), retaining all tails and repeated ranks.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: The current author release already uses a consistent Gaussian base law

Assessment: not_issue; impact: minor



Source: Current base_distributions.py covariance paths; historical official supplement



### Source claim (paraphrase)

The older supplement used training covariance \(c(K+\delta I)\) and generation covariance \(cK+\delta I\). The current author-main code uses the latter consistently.



### Analysis

The historical difference was \(\delta(1-c)I\), nonzero for \(c\ne1\). Fresh current source places jitter outside the scalar normalization in construction, training sampling and distribution creation, so the two Gaussian covariance formulas now coincide for each fixed supported position set. The README directs publication reproduction to a separate branch because baseline-library dependencies changed; historical experiment provenance remains distinct.



### Finding and scope

The old supplement discrepancy is not a current error. Current covariance-law consistency does not itself certify posterior or numerical-ODE accuracy.



## Problem 3: The current plotting loop still repeats the final seed

Assessment: supported; impact: minor



Source: Current plot_results_Darcy.ipynb, code cell 6; three-run evaluation statement, PDF p.5



### Source claim (paraphrase)

The log-probability loop iterates over nn but selects every row with the previous loopâ€™s final index mm.



### Analysis

For the supplied FNOPE fixed-grid group at \(3000\) simulations, seeds \(47843,62747,28204\) have ten-value means \[-0.767076994,-0.391124436,0.285954272\]. Repeating the final row returns \(0.285954272\); averaging all three returns \(-0.2907490527\), difference \(0.5767033247\). Equal run lengths and finite values make the intended mean unambiguous. The current notebook still contains the mismatched index; the values are recalculations of author CSV data, not new density estimates.



### Finding and scope

The released aggregation does not implement the stated three-run mean. Whether that precise notebook generated the published figure, or changes a ranking, remains unestablished.



### Proposed correction

Select the row indexed by the current log-probability loop and recompute mean/uncertainty at the intended independent-run level. No trained model rerun or corrected ranking is claimed.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
