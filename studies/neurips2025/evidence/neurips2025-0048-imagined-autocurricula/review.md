# Imagined Autocurricula



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The latest paper still gives two inequivalent replay procedures and two different curriculum priority functions. Exact small witnesses show an actor-gradient sign reversal for stored-action replay and a priority-ranking reversal for accumulated versus plain positive TD errors. These are Minor written-method inconsistencies; the actual training path remains unverified.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Initial-condition replay and stored-action replay are different actor updates

Assessment: supported; impact: minor



Source: Sections 2.4 and 3.3, PDF pp. 4–5; Appendix C, Algorithm 2, PDF p. 19.



### Source claim (paraphrase)

The body says current-policy rollouts restart from sampled contexts; Algorithm 2 instead loads a saved trajectory and updates its stored actions without behavior correction.



### Analysis

In a one-step bandit, let rewards be \(1,0\), current good-action probability \(0.2\), replay good-action probability \(0.9\), and action-independent critic baseline \(2\). The true current-policy logit gradient is \(0.2(0.8)=0.16\). Reusing stored actions instead gives \(0.9(0.8)(-1)+0.1(-0.2)(-2)=-0.68\). An action-independent baseline cancels under on-policy sampling; it need not cancel under the replay law. Terminal masking permits this one-step case within a longer maximum imagination horizon.



### Finding and scope

The two written algorithms are not generally equivalent. The witness does not show that the actual experiments used old actions or encountered this state; original implementation/logs are needed for that determination.



### Proposed correction

Make the pseudocode match initial-context replay with fresh current-policy actions, or specify and justify the off-policy alternative. No performance-preserving drop-in repair is established.

The freshly retrieved proceedings and latest target arXiv v2 retain the conflicting body and Algorithm 2 descriptions. The current author project page still says Code (coming soon); no released implementation was available to decide the historical execution path.



## Problem 2: Accumulated positive TD residuals and their mean reverse rankings

Assessment: supported; impact: minor



Source: Eq. (7), PDF p. 5; Appendix C, Algorithm 2, PDF p. 19; horizon interpretation, PDF pp. 8 and 20.



### Source claim (paraphrase)

Eq.(7) sums future discounted positive TD residuals for every starting position; Algorithm 2 takes their plain mean.



### Analysis

For horizon \(H=5\), \(q=0.985\cdot0.95=0.93575\), and positive TD residual vectors \(A=(0.9,0,0,0,0)\), \(B=(0,0,0.75,0,0)\), plain means are \(0.18,0.15\). The accumulated future-residual score instead gives \(0.18\) and \(0.15(1+q+q^2)=0.421706709375\), reversing their ranking. Binary terminal rewards and value estimates in \([0,1]\) can realize these vectors; the witness does not require illegal reward timing.



### Finding and scope

The priorities are different functions, even at equal horizon; endpoint indexing cannot resolve the reversed ordering. A horizon trend under the accumulated form can partly reflect its position weights, rather than independently demonstrating difficulty.



### Proposed correction

Specify which of the two priority functions is intended. Changing horizon normalization also changes the curriculum; no benchmark-equivalent substitution is asserted.

The freshly retrieved proceedings and latest target arXiv v2 retain the conflicting body and Algorithm 2 descriptions. The current author project page still says Code (coming soon); no released implementation was available to decide the historical execution path.



## Limits

- No world model, policy or old verifier was executed. The current author project page still lists code as forthcoming. The mathematical witnesses distinguish the written procedures but do not identify which procedure generated the reported training results.
