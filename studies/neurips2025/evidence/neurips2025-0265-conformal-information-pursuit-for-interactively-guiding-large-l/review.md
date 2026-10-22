# Conformal Information Pursuit for Interactively Guiding Large Language Models



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The stopping equivalence is overstated. Released scoring, conditional sampling and calibration ranks differ from the stated objectives or general finite-sample rule, with explicit scope controls.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Stable sets and low query dispersion do not imply zero information

Assessment: supported; impact: minor



Source: Remark 1, current arXiv v2 PDF p.6; Appendix G.10, p.38



### Source claim (paraphrase)

The paper calls IP and set-size-stability stopping criteria equivalent and uses low dispersion of candidate postquery entropies as a practical stopping diagnostic.



### Analysis

Let \(Y=X\) be a bit with \(P(Y=0)=0.9\), and let an uninformative predictor always return \((0.95,0.05)\), producing singleton set \(\{0\}\). At \(\alpha=0.1,N=100\), coverage \(0.9\) lies within the stated two-sided range. A query revealing Y leaves that predictor’s set size unchanged but gains \(h_b(0.1)\approx0.468996\) bits. Separately, for a fair bit, candidate queries Y and its complement both have zero postquery entropy and zero dispersion, while each gains one bit.



### Finding and scope

Neither stable conformal-set size nor equal candidate entropy scores certifies informational sufficiency. The paper explicitly leaves adaptive error control open, and this finding does not claim poor empirical stopping performance.



### Proposed correction

Describe the stopping tests as heuristics. An exact no-information condition compares current entropy with the answer-weighted expected postquery entropy; a finite-sample stopping guarantee needs additional estimation control.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Released query score differs from log mean set size

Assessment: supported; impact: minor



Source: Section 3.2, Eqs.(9)–(11), PDF p.5; src/20q/20q_conformal_closed_binary.py, lines 190–203



### Source claim (paraphrase)

The displayed C-IP rule minimizes log expected prediction-set size; the release instead computes a conditional mean-log Fano-style score and uses estimation batch size where calibration size belongs.



### Analysis

With four included-label samples and set sizes \(A=(1,1,1,9)\), \(B=(2,2,2,2)\), the displayed mean-size objective prefers B because \(\log_2 3>\log_2 2\). The release at \(\alpha=0.1,n=4\) gives \(h_b(0.1)+1.1\operatorname{mean}\log_2 S\), with scores approximately \(1.340725\) and \(1.568996\), preferring A. These sets are realizable by normalized thresholded probability vectors. The alternate population Fano bound is legitimate; it simply differs from the displayed method. The coefficient uses \(n=4\) instead of calibration \(N=100\).



### Finding and scope

The implementation can reverse query rankings relative to the stated surrogate. Its alternative bound is not itself a false information-theoretic theorem, and the resulting change in benchmark query traces is not measured.



### Proposed correction

Implement log of mean size with the stated calibration parameter, or explicitly document the different conditional-log objective and justify its estimator, including empty groups.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: Prior answer weights do not estimate the history-conditional objective

Assessment: supported; impact: minor



Source: Eq.(2), PDF p.3; C-IP rule p.6; src/20q/20q_entropy_closed_binary.py, sample_data and estimate_entropy



### Source claim (paraphrase)

The desired next-answer expectation is conditional on the observed history, but the release samples unconditional labels and then appends their answers to that history.



### Analysis

Let Y be uniform on \(20\) labels and history restrict it to \(H=\{0,1,2,3,4,5\}\). Query A is true for label zero or labels at least six; query B is true for \[\{0,1,2,6,7,8,9,10,11,12\}\]. Both answers remain possible after history. Exact posterior entropies give conditional scores \(H_A=(5/6)\log_2 5\approx1.93494\), \(H_B=\log_2 3\approx1.58496\), so B is preferred. Prior weights instead give \(\widetilde H_A=(5/20)\log_2 5\approx0.580482\) and the same B score, selecting A. Correct inner posteriors cannot fix incorrect outer answer probabilities.



### Finding and scope

The released IP expectation can rank the less informative query first even with an oracle posterior. The first query and history-independent answers are valid special cases; the exact numeric example is not claimed to characterize the full C-IP inclusion/exclusion score.



### Proposed correction

Sample from the history-conditional law or apply justified likelihood importance weights. General free-text histories require an explicitly validated conditional sampler.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 4: Calibration quantile lacks the general finite-sample adjustment

Assessment: supported; impact: minor



Source: Eq.(4), Section 3.1; src/20q/20q_conformal_thresholds_closed_binary.py, lines 162–175



### Source claim (paraphrase)

The release uses the higher empirical quantile at \(1-\alpha\), whose calibration rank differs from the split-conformal finite-sample rank.



### Analysis

For \(N=21,\alpha=0.1\), the code rank is \(\lceil20(0.9)\rceil+1=19\), while the required rank is \(\lceil22(0.9)\rceil=20\). Permute \(22\) distinct valid scores \(s_j=-j/23\), represented by two-label probabilities \((-s_j,1+s_j)\) with true label zero. Exchangeability makes the held-out rank uniform, so the release covers \(19/22<0.9\), while the corrected rank covers \(20/22\). For \(N=50,\alpha=0.01\), the required unavailable rank needs an infinite threshold rather than the largest observed score. The reported \(N=100,200\) settings on the inspected level grid happen to satisfy the rank inequality.



### Finding and scope

The quantile is not generally valid under the advertised exchangeable-score domain. This arithmetic defect does not explain every reported undercoverage curve or resolve adaptive-history exchangeability.



### Proposed correction

Use rank \(\lceil(N+1)(1-\alpha)\rceil\), returning an infinite threshold if it exceeds N, and include scores non-strictly at the threshold.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
