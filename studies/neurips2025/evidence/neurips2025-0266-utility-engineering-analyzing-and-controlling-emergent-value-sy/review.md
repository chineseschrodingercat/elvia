# Utility Engineering: Analyzing and Controlling Emergent Value Systems in AIs



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Local representation, instrumentality-statistic and mechanism-identification claims require qualification. The exchange-rate calculation remains a quantity-dependent summary; empirical scale correlations are not re-estimated.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Representation conditions omit consistency of indifference

Assessment: supported; impact: minor



Source: Section 3, PDF p.4; Appendix A.1, p.16; cycle diagnostic in generate_figures.ipynb



### Source claim (paraphrase)

The paper says complete pairwise strict preference/indifference classifications and transitivity of strict preference suffice for a real utility representation.



### Analysis

Take \(A\sim B,B\sim C,A\succ C\), with symmetric indifference and the reverse strict edge. Every pair is classified, and no two-edge strict chain exists, so the printed strict-transitivity condition holds. A scalar representation would require \(U(A)=U(B)=U(C)\), contradicting \(U(A)>U(C)\). Counting only strict cycles and one-tie patterns does not detect this two-tie inconsistency.



### Finding and scope

The stated finite representation criterion omits a substantive tie-consistency condition. A deliberately narrower cycle statistic remains well-defined, and its empirical values are not shown to be miscomputed.



### Proposed correction

Use complete transitive weak preference. On a finite set, its indifference classes form a total order and can be assigned real ranks.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: History rewards differ from shared terminal-state rewards

Assessment: supported; impact: minor



Source: Appendix D.1, PDF p.20; evaluate_instrumental_values.py, extract_partial_sequences



### Source claim (paraphrase)

The description uses two starts and two shared terminal states, but the implementation represents trajectory prefixes and assigns a reward to each terminal history.



### Analysis

Rollouts \[(s_1,t_1),(s_1,t_2),(s_2,t_1),(s_2,t_2)\] become six options: two start prefixes and four start-terminal histories. Let both starts transition equally to both terminals, and utilities be \(+1\) for every history starting at \(s_1\), \(-1\) for those starting at \(s_2\). At discount one, independent history-terminal rewards fit all six utilities with zero loss. Shared terminal-state rewards instead force both start values to equal \((r_1+r_2)/2\), which cannot equal both \(+1\) and \(-1\).



### Finding and scope

A perfect history-space fit does not establish the stated shared-terminal-state instrumentality interpretation. The observed model-level correlations are not recalculated or shown spurious.



### Proposed correction

Either describe a prefix-tree/history-reward target or use one reward per original terminal state with appropriately elicited state utilities.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: Soft Bellman fitting does not yield an exact value function

Assessment: supported; impact: minor



Source: Appendix D.1, PDF p.20; evaluate_instrumental_values.py, optimize_reward_function



### Source claim (paraphrase)

The optimizer independently fits reward R and value V, forms \(W=R+\gamma PV\), penalizes \(\|W-V\|^2+0.1\|W-U\|^2\), and reports mismatch to W as a best-fit value-function loss.



### Analysis

For two identical start/two-terminal blocks, set normalized utilities \(U=(a,b,b)\), \(a=\sqrt2,b=-1/\sqrt2\), and \(\gamma=0.99\). Symmetry reduces the objective to \(2(r-v)^2+0.1[(\gamma v-a)^2+2(r-b)^2]\). Its exact minimizer is \(v=[2b+1.1\gamma a]/[2+1.1\gamma^2]\approx0.04089035\), \(r=(v+0.1b)/1.1\approx-0.02710939\). Reported start surrogate \(\gamma v\approx0.04048145\) differs from the actual value of its returned terminal reward, \(\gamma r\approx-0.02683829\). This persists at the exact optimum, independently of numerical convergence.



### Finding and scope

The statistic is an approximate Bellman surrogate rather than an exact value-function fit. Correcting it changes the statistic’s definition; the direction of correlation changes is unknown.



### Proposed correction

Parameterize two-step values directly as \(Br\), or in a suitable discounted finite model as \((I-\gamma P)^{-1}Er\), and optimize the declared fitting loss on those exact values.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 4: Order averaging does not identify an indifference mechanism

Assessment: supported; impact: minor



Source: Appendix K, PDF pp.35–36; Figure 39



### Source claim (paraphrase)

Improved utility fit after averaging response orders is interpreted as strong evidence of a learned strategy for expressing indifference.



### Analysis

Let latent utility difference be d and a first-position response bias be c. Choose the first option when \(d+c>0\) in one order and \(-d+c>0\) in the reverse order. With \(c=2\), both indifference \(d=0\) and strict preference \(d=1\) produce first-option responses in both orders. Outcome-normalized averaging gives probability \(1/2\) in either case, so those observations cannot distinguish the mechanisms.



### Finding and scope

Order normalization can improve predictive fit without identifying why the conflicting responses occur. This does not refute the fitted probabilities or separate probing/intervention experiments.



### Proposed correction

Describe operational order-normalized ties and require a discriminating model or intervention before attributing the internal indifference mechanism.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 5: Reciprocal exchange rates are quantity-dependent summaries

Assessment: not_issue; impact: minor



Source: Appendix E.1, PDF p.22; two_way_geometric_exchange_rate



### Source claim (paraphrase)

Country/entity comparisons summarize log-utility indifference rates using a reciprocal geometric aggregate.



### Analysis

For \(U_i(N)=a_i\log N+b_i\), equality \(U_i(M)=U_j(N)\) gives \(M/N=e^{(b_j-b_i)/a_i}N^{a_j/a_i-1}\). It is constant only for equal slopes. With slopes \(1,2\), zero intercepts and quantity grid \(\{1,4\}\), forward ratios are \(1,4\), while the two-way geometric aggregate is \(2^{3/4}\). Reciprocity of a summary does not make it a universal per-unit indifference ratio.



### Finding and scope

This qualifies the interpretation of a valid quantity-dependent index. It does not establish incorrect numerical evaluation of that index; related prompt-framing concerns were previously discussed publicly.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
