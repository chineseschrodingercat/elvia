# Distribution Learning Meets Graph Structure Sampling



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The stated forecaster, exact graph sampler and displayed hardness construction each fail on explicit finite examples. Range scaling, labelled deletion and a different packing argument can restore narrower guarantees; the final iid learning order is not declared false.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Unscaled exponential-weights rate violates the stated regret bound

Assessment: supported; impact: major



Source: Official supplement, Algorithm 2, Lemma A.14 and Lemma B.6



### Source claim (paraphrase)

Algorithm 2 uses raw-loss exponent \(-\eta\ell\) and \(\eta=\sqrt{8\log N/T}\), while Lemma A.14 claims regret proportional to an arbitrary loss range.



### Analysis

Take \(N=2,T=100,\tau=2^{-20}\), experts \((1-\tau,\tau)\) and \((\tau,1-\tau)\), and alternating outcomes. Put \(a=-\log(1-\tau),b=-\log\tau\). The exact expected regret is \[\frac{T}{2}(b-a)\left(\frac{1}{1+e^{-\eta(b-a)}}-\frac12\right)=321.05863.\] The printed bound is \(b\sqrt{T\log2/2}=81.61184\). All expert masses are positive and losses lie in \([0,b]\). The lemma permits any sequence; the example does not address the final iid learner directly. B.6 additionally conditions an iid online-to-batch argument on a sample-dependent regret event, which need not preserve independence.



### Finding and scope

The operative regret lemma and its proof route to proper learning are invalid as written. This does not falsify the final iid PAC order for a corrected learner.



### Proposed correction

For loss width \(R\), the potential bound is \(\log N/\eta+\eta TR^2/8\). Scale the rate by the actual width. Apply the corrected expected regret against a fixed population expert, then Markov to the nonnegative excess KL; this avoids event-conditioned independence.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Parallel-bundle deletion gives the wrong exact tree law

Assessment: supported; impact: major



Source: Official supplement, Definition D.11, Algorithm 8 and Claims D.16–D.17



### Source claim (paraphrase)

The sampler claims product-weight arborescences, but deletion removes every parallel edge while the acceptance branch records one selected original edge.



### Analysis

Use the unit-weight complete bidirected graph on \(\{1,2,3\}\), root \(1\), edge order \(12,13,21,23,31,32\). The three rooted trees are \[\{12,13\},\{12,23\},\{13,32\}\], each target probability \(1/3\). Accepting \(12\) has probability \(2/3\); contraction makes \(13\) and \(23\) parallel. Bundle deletion of the next \(13\) leaves zero partition function, so that branch necessarily records \(13\). The resulting law is \((2/3,0,1/3)\), not uniform. Parallel arcs arise internally even from a simple initial graph.



### Finding and scope

The stated deletion convention invalidates the exact sampling guarantee, including the complete-graph application. The matrix-tree identity survives.



### Proposed correction

Delete one persistently labelled arc. The partition identity \(Z(G)=Z(G\setminus e)+w(e)Z(G/e)\), with preserved parallel labels and positive partition function, proves correct conditional recursion by induction.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: The displayed hardness family admits a zero-sample estimator

Assessment: supported; impact: major



Source: Official supplement, Lemma E.5, Claim E.6 and proof of Theorem E.1



### Source claim (paraphrase)

The specified three-bit family is claimed to require \(\Omega(1/\varepsilon)\) samples for KL error \(\varepsilon\), allowing an arbitrary pmf output.



### Analysis

Each \(P_i\) gives its two common states mass \((1-\varepsilon/2)/2\), and two private exceptional states mass \(\varepsilon/4\). The known mixture \(Q=(P_1+P_2+P_3)/3\) gives each exceptional state mass \(\varepsilon/12\); therefore \(\mathrm{KL}(P_i\|Q)=(\varepsilon/2)\log3<\varepsilon\) for all targets without samples. Pairwise squared Hellinger distance is \(\varepsilon/2\), not the claimed much larger separation. A proper-output restriction would exclude this mixture, but E.5 states none. Independence of target blocks also does not force an arbitrary learner to output only within-block edges or independent errors.



### Finding and scope

This construction and block proof do not establish the stated lower bound. The overall minimax order is not refuted; different product-distribution packings can establish it.



### Proposed correction

The proposed replacement uses a Hamming-separated family of product Bernoulli laws with coordinate perturbation squared \(32\varepsilon/n\), Hellinger separation and Fano’s information argument, yielding \(\Omega(n/\varepsilon)\) for sufficiently large \(n\) and small \(\varepsilon\). It does not restore every structural claim of E.6.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
