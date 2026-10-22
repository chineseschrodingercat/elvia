# Predictive Coding Enhances Meta-RL To Achieve Interpretable Bayes-Optimal Belief Representation Under Partial Observability



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The released fixed-window Gittins reference is near-optimal rather than exactly finite-horizon optimal, and its output comparison statistic is undiscounted. The posterior-count representation itself is not refuted.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The Gittins reference is not exactly optimal for the finite \(40\)-pull task

Assessment: supported; impact: minor



Source: Section 5, Figure 2, PDF p. 6; Appendix A.2, PDF p. 14.



### Source claim (paraphrase)

Paraphrase: Section 5, PDF p. 6, identifies the Gittins-index solution as the Bayes-optimal reference for the two-armed Bernoulli experiment, including Figure 2. Appendix A.2, p. 14, specifies the independent \(\operatorname{Beta}(1,1)\) priors, episode length \(40\), and discount \(0.95\), and uses the same optimality characterization.

In the released code, utils/bayes_optimal_agents.py, class BernoulliGittinsAgent, stores one fixed lookahead_window. get_action chooses the larger cached index. update changes the posterior counts and recomputes that arm’s index, but does not reduce the lookahead as the episode approaches its deadline. The performance path supplies lookahead \(40\); a state-machine reference path requests one auxiliary transition and can use lookahead 41.



### Analysis

With one action remaining, information has no future value, so the optimal action maximizes the current posterior mean. A fixed-window index can still favor an exploratory arm with a smaller mean, unlike a remaining-horizon Bellman policy. The released policy never reduces its lookahead with the remaining episode length. This establishes the optimality qualification without relying on a rerun or treating the small historical value gap as a new experiment.

A positively reachable \(39\)-pull history with first reward one and subsequent rewards zero has counts \((s_1,f_1,s_2,f_2)=(1,25,0,13)\), hence posteriors \(\operatorname{Beta}(2,26)\) and \(\operatorname{Beta}(1,14)\). The historical calculation for this unchanged release gives indices \(0.08984375<0.09765625\), selecting arm two. With one pull left, the means are \(1/14>1/15\), so the conditional loss is exactly \(1/210\). The ordered history has prior probability \(B(2,26)B(1,14)=1/9828>0\). This historical reachability/index calculation was not executed again; the current source still keeps the same fixed lookahead.



### Finding and scope

The exact-reference characterization requires correction; the unchanged source supports retaining the narrower approximate-reference interpretation. The historical prior-averaged discounted gap is approximately 0.001359, rather than evidence of a large behavioral reversal.



### Proposed correction

Use a remaining-horizon Bellman reference or describe the fixed-window Gittins baseline as near-optimal for this finite task. The four Beta posterior counts remain sufficient statistics.

A local correction or qualification is proposed where specified; author adoption is not established.

The existing reference-policy or metric-definition proposal remains relevant to the current author source; no author adoption is established.



## Problem 2: The released bandit output metric is an undiscounted statistic

Assessment: supported; impact: minor



Source: Appendix A.4, PDF p. 18 (separate supplement p. 5); Appendix A.2, PDF p. 14.



### Source claim (paraphrase)

Paraphrase: Appendix A.4, PDF p. 18 / supplementary PDF p. 5, describes output dissimilarity \(D_o\) in terms of expected-return differences. The Bernoulli task’s stated performance objective uses \(\gamma=0.95\), Appendix A.2/p. 14.

This finding is a verified implementation/metric-scope mismatch, not a claim that an aggregate return statistic is inherently invalid. In utils/state_machine_analysis.py, get_output_dissimilarity (lines 1250-1361), the stationary-bandit branch obtains each arm’s expected immediate rewards from the sampled task parameters, sums the differences with no discount weights, takes an absolute value per episode, and averages across episodes. It cannot be interpreted as the difference of the discounted task returns without further qualification.



### Analysis

For arm rewards \(0.9\) and \(0.1\), choosing the better arm for the first \(20\) rather than the last \(20\) actions gives the same undiscounted arm counts. With \(\gamma=0.95\), the discounted-return difference is \(0.8(1-0.95^{20})^2/(1-0.95)\approx6.584645\). A count-only output statistic cannot represent that discounted objective.



### Finding and scope

Supported metric-scope mismatch; no revised trained-agent return is inferred.



### Proposed correction

Either label the statistic as an undiscounted reward-sum comparison or multiply each per-step expected-reward difference by the task discount before summing. This remains a comparison along evaluated reference histories, not necessarily an on-policy return difference.

The existing reference-policy or metric-definition proposal remains relevant to the current author source; no author adoption is established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
