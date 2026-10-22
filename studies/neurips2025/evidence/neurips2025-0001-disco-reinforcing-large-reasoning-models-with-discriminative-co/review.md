# DisCO: Reinforcing Large Reasoning Models with Discriminative Constrained Optimization



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The latest paper and finite-group implementation retain difficulty-dependent inclusion and the false automatic-monotonicity inference from a lower bound. The historical L-ratio dispatcher failure is fixed in the current author release. Other bounded mathematical, manifest and reporting concerns persist; published training outcomes have not been reconstructed.



## Scope

Claim-focused reading of the identified paper and author-released materials. The arguments below distinguish mathematical contradictions, version-specific implementation defects and unresolved empirical consequences. No author code was executed in this revision.



## Problem 1: finite squared-hinge penalties and exact feasibility

Assessment: supported; impact: minor



Source: Paper pp. 1-2, 6, Eqs. (8)-(9); its cited penalty-theory source arXiv:2410.03955v4, pp. 8-10, Assumptions 1-4 and Theorem 1.



### Source claim (paraphrase)

The discussion following Eq. (\(9\)) relates a finite squared-hinge KL penalty to the constrained KKT system, while the abstract/introduction describe trust-region enforcement.



### Analysis

At a feasible point, the gradient of \(\beta[D(\theta)-\delta]_+^2\) is zero. An active constrained optimum with a positive KKT multiplier can nevertheless have a nonzero objective gradient, so it need not be stationary for this finite penalty. For \(\pi_{\rm old}=(1/2,1/2)\), \(\pi_\theta=(\operatorname{sigmoid}\theta,1-\operatorname{sigmoid}\theta)\), \(J(\theta)=\theta\), and \(D(\theta)=\log\cosh(\theta/2)\), the constrained maximum is \(\theta_*=2\operatorname{arcosh}(e^\delta)\). At \(\delta=10^{-4}\) and \(\beta=1000\), \(\theta_*\simeq0.02828474\), whereas the penalized stationary maximum has \(\theta\simeq0.25371689\) and \(D\simeq0.00802504>\delta\). The bounded objective \(J(\theta)=2\tanh(\theta/2)\) similarly permits \(D\simeq0.00794101\).



### Finding and scope

Finite penalization alone does not imply exact hard feasibility. The cited penalty theorem concerns approximate KKT conditions with tolerance-dependent assumptions and schedules; that theorem is not refuted. Special instances can have exactly feasible penalized optima, so a literal existential claim that this can happen is also not refuted.



### Proposed correction

State approximate stationarity/feasibility and the required assumptions. If exact feasibility is intended, provide an appropriate constrained-update argument. For the scalar example, \(\theta_*=2\operatorname{arcosh}(e^\delta)\) and \(\lambda_*=2/\tanh(\theta_*/2)\).

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: finite groups retain difficulty-dependent selection

Assessment: supported; impact: major



Source: paper pages: 1 7 8 19; paper equations: 7 10; code: verl/verl/trainer/ppo/core_algos.py:289-314,377-400,470-503,571-602 verl/verl/trainer/config/ppo_trainer.yaml:159-166 scripts/train/run_disco_logL_1.5b_8k.sh



### Source claim (paraphrase)

The abstract and Table 1 describe complete removal of difficulty bias. The released loss excludes groups containing only one reward class and divides by the original question count.



### Analysis

Let a question have success probability \(p\), and let \(K\sim\operatorname{Binomial}(n,p)\) be its number of correct responses. A mixed group is included with probability \(h_n(p)=1-p^n-(1-p)^n\). Since excluded groups contribute zero but the denominator remains the original question count, the expected finite-group contribution retains this difficulty-dependent factor. A question with one correct and one incorrect possible outcome already yields this construction for the full DRO objective. For \(n=8\), \(h_8(0.01)\simeq0.0772553\) and \(h_8(1/2)=0.9921875\); the relative inclusion weight is about \(0.0778636\). The cited configuration disables dynamic filtering, and the rejection-sampling flag defaults to false.



### Finding and scope

The finite fixed-group implementation does not completely remove difficulty-dependent question selection. The population decomposition correctly removes its explicit \(\sqrt{p(1-p)}\) factor, and the method can still provide useful practical reweighting.



### Proposed correction

Restrict the claim to the population normalization and available mixed groups, or specify a justified question-level sampling/inclusion correction. Dividing by the number of valid groups alone does not equalize original-question inclusion.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: a lower bound does not ensure monotonic improvement

Assessment: supported; impact: major



Source: Current arXiv v5, Eqs.(7),(10), PDF pp.5,7, and paragraph following Eq.(10)



### Source claim (paraphrase)

The paragraph following Eq. (\(10\)) infers that increasing the lower bound \(J_2\le J_1\) automatically increases \(J_1\).



### Analysis

The witness has one question and three one-token outputs with rewards \(r(o_1)=1\), \(r(o_2)=r(o_3)=0\). Under the fixed old policy \((0.4,0.3,0.3)\), the conditional positive law is a point mass on \(o_1\), and the conditional negative law assigns \(1/2\) to each of \(o_2,o_3\). With the paper’s log-likelihood score \(s_\theta(o_i)=\log\pi_i\), Eqs.(7) and (10) reduce exactly to \[J_1(\pi)=\log\pi_1-\tfrac12(\log\pi_2+\log\pi_3),\] \[J_2(\pi)=\log\pi_1-\tau\log\{(\pi_2^{1/\tau}+\pi_3^{1/\tau})/2\}.\] The trust-region quantity is \(D_{\rm KL}(\pi_{\rm old}\|\pi)=\sum_i\pi_{{\rm old},i}\log(\pi_{{\rm old},i}/\pi_i)\).

Write \(J_1=J_2+G\), where \(G\ge0\). An increase in \(J_2\) can be outweighed by a decrease in \(G\). A policy-level example uses reference probabilities \((0.4,0.3,0.3)\), temperature \(\tau=10\), and candidate policies \(A=(0.4,0.305,0.295)\) and \[B=(0.4000318,0.2999841,0.2999841)\]. Substitution in the paper's objectives gives \(J_2(B)-J_2(A)\simeq7.481517\times10^{-6}>0\), but \(J_1(B)-J_1(A)\simeq-6.409938\times10^{-6}<0\). Their KL values are approximately \(8.334491\times10^{-5}\) and \(2.106713\times10^{-9}\), both below \(\delta=10^{-4}\).



### Finding and scope

The asserted monotonic implication is false even within the stated KL region. The lower bound and the entropic DRO variational identity can remain correct; practical superiority is a separate empirical question.



### Proposed correction

Remove automatic monotonicity, or supply a touching-minorizer, gap-control or acceptance condition that actually controls \(J_1\).

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: Relative objective/penalty signs in Algorithm 1

Assessment: supported; impact: minor



Source: paper pages: 19; algorithm lines: 9 10 11; code: verl/verl/trainer/ppo/core_algos.py



### Source claim (paraphrase)

Algorithm 1 defines \(G_1\) as the objective gradient and \(G_2\) as the positive penalty gradient, then supplies \(G_1+G_2\) to the optimizer.



### Analysis

Descent on \(-J_2+P\) requires \(-G_1+G_2\); ascent requires \(G_1-G_2\). Adding both gradients gives the wrong relative sign under either convention. The author-released loss minimizes the negative objective plus the positive penalty, so its relative sign is correct.



### Finding and scope

Following pseudocode can give wrong direction; this does not establish wrong public loss or wrong reported training. Actual public objective/penalty relative sign is correct.



### Proposed correction

For a descent optimizer, write \(-G_1+G_2\) and state the convention.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 5: The historical L-ratio dispatcher defect is fixed

Assessment: not_issue; impact: no_issue_found



Source: Author repository Optimization-AI/DisCO, commit 8bdd94eb49a58cd09e68af5392302ba83acf63b2; verl/verl/workers/actor/dp_actor.py, lines 286–296; verl/verl/trainer/ppo/core_algos.py, compute_policy_loss_disco_Lratio



### Source claim (paraphrase)

The original supplemental release routed the full L-ratio branch to a basic loss function that did not accept its tau argument.



### Analysis

In current author commit 8bdd94eb49a58cd09e68af5392302ba83acf63b2, dp_actor.py, lines 286–296, calls compute_policy_loss_disco_Lratio, whose signature accepts tau. Reading the current call and signature clears the particular dispatch failure. The older supplemental call remains a historical version fact, and no author program was executed in this check.



### Finding and scope

This specific failure is absent from the current author release. Historical experiment provenance and adoption of any external audit remain unestablished.



## Problem 6: Printed and implemented penalty gradients differ by a factor of two

Assessment: supported; impact: minor



Source: paper pages: 6 19; paper equations: 9; code: verl/verl/trainer/ppo/core_algos.py:318-321,406-409,506-509,604-607



### Source claim (paraphrase)

Eq. (\(9\)) uses \(\beta[D-\delta]_+^2\), whose gradient is \(2\beta[D-\delta]_+\nabla D\).



### Analysis

In each cited implementation branch, the detached coefficient gives only \(\beta[D-\delta]_+\nabla D\). Detachment removes the coefficient derivative, making this the gradient of \((\beta/2)[D-\delta]_+^2\).



### Finding and scope

Numerical beta setting is not an exact Eq \(9\) reproduction; retuning can absorb factor, so less severe than sign error. Penalty direction is correct; beta is tunable.



### Proposed correction

Use a consistent \(\beta/2\) convention or double the detached coefficient. Differentiating \(\beta\max(D-\delta,0)^2\) directly gives the printed gradient.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 7: AMC benchmark year differs from the released evaluation manifest

Assessment: supported; impact: minor



Source: paper pages: 7 8 9 18; paper tables: 2 3 4 5; data: deepscaler/deepscaler/data/test/amc.json datasets/deepscaler/data/amc.parquet; code: deepscaler/deepscaler/data/utils.py scripts/data/deepscaler_dataset.py scripts/eval/eval_model_8k.sh



### Source claim (paraphrase)

Task setting/table headers identify AMC 2023.



### Analysis

AMC JSON has \(83\) rows: \(43\) source URLs dated \(2022\) and \(40\) dated 2023. Parquet has same \(83\) problems in same order. Loader/preprocessor/eval path contains no year filter; relevant files unchanged in pinned GitHub.



### Finding and scope

Supplied pipeline differs from named benchmark; external comparisons are ambiguous. Artifacts alone do not establish whether tables used \(83\) questions or undocumented \(40\)-question subset.



### Proposed correction

Publish actual table evaluation manifest. Supply/filter \(40\)-question \(2023\) split or relabel mixed-year results.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 8: MATH500 overlaps and duplicate training pairs

Assessment: supported; impact: minor



Source: paper pages: 7; data: deepscaler/deepscaler/data/train/deepscaler.json deepscaler/deepscaler/data/test/math.json datasets/deepscaler/data/train.parquet datasets/deepscaler/data/math.parquet



### Source claim (paraphrase)

Paper describes about \(40.3\) thousand unique pairs; delivered train/test files should identify benchmark separation.



### Analysis

The author-released MATH test indices \(80,285,412\) match training indices \(7202,7141,6976\) after Unicode NFKC normalization, whitespace normalization and case folding; the corresponding answers \(501,440,406\) agree. The first pair is also identical before normalization. JSON and Parquet problem orders agree. There are \(40\,315\) training rows but only \(39\,616\) raw unique problem-answer pairs, \(39\,387\) raw unique problems and \(39\,097\) normalized unique problems. The other five released test sets have no exact normalized match under this narrow comparison.



### Finding and scope

These are concrete overlaps in the delivered data, with no semantic/fuzzy matching claim. Even attributing all three MATH answers to overlap changes an individual six-set macro-score by at most \(0.1\) percentage point; this does not explain the full reported improvement.



### Proposed correction

Correct counts; publish deduplicated/decontaminated manifests. Report sensitivity excluding \(3\) affected MATH questions; use clean future training release. Retraining is required to estimate causal effect of changing training data.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 9: Checkpoint selection and uncertainty: unresolved empirical scope

Assessment: supported; impact: minor



Source: paper pages: 7 8 9 10 24 25; code: scripts/train/run_disco_logL_1.5b_8k.sh scripts/eval/eval_model_8k.sh



### Source claim (paraphrase)

Paper reports best performance and significant superiority without a complete selection manifest or uncertainty intervals.



### Analysis

The paper evaluates every \(200\) steps and reports best performance, without a fully specified independent checkpoint-selection rule. Its checklist openly reports no error bars. Averaging \(16\) correctness samples estimates pass@\(1\), rather than pass@\(16\), and does not measure training-seed variability. Dynamic sampling is disabled for all compared methods, which is disclosed. The fixed \(0.001\) KL ablation does not establish failure of every tuned regularizer.



### Finding and scope

Multiple models, six benchmarks and a second training dataset provide useful reported evidence. Checkpoint attribution and statistical robustness remain unresolved; no corrected effect size is supplied.



### Proposed correction

Publish table/checkpoint/seed/config/dataset manifests and selection protocol. Compute paired question-level intervals from saved outputs; estimate training-seed uncertainty separately. Scope DAPO and stability comparisons to tested conditions.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 10: Proposition 1's sign-dependent monotonicity

Assessment: supported; impact: minor



Source: paper pages: 4 18 19; paper equations: 3 4 5



### Source claim (paraphrase)

Proposition 1 assumes f nondecreasing in x and remark says assumptions hold for GRPO.



### Analysis

For a negative reward \(y=-1\), the clipped branch is \(f(x,-1)=-\max(x,1-\varepsilon)\), which is nonincreasing. At \(\varepsilon=0.2\), \(f(1,-1)=-1\) and \(f(1.1,-1)=-1.1\), contradicting the claimed nondecreasing condition. The population decomposition itself does not require that extra condition.



### Finding and scope

Correct the sign-dependent assumption; the decomposition identity is not refuted.



### Proposed correction

Remove extra monotonicity of f for all y; retain branchwise assumptions or state sign-dependent monotonicity.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 11: Dr. GRPO's relative question weighting

Assessment: supported; impact: minor



Source: paper pages: 4 5 20 21; paper figures: 1; paper equations: 19



### Source claim (paraphrase)

The text interprets \(p(1-p)\) as mitigating question imbalance relative to \(\sqrt{p(1-p)}\).



### Analysis

After normalizing both weights to one at \(p=1/2\), \(r_{\rm GRPO}(p)=2\sqrt{p(1-p)}\) and \(r_{\rm Dr}(p)=4p(1-p)=r_{\rm GRPO}(p)^2\). At \(p=0.01\), these are approximately \(0.1989975\) and \(0.0396\). Under the displayed relative-weight criterion, the latter attenuates extreme questions more strongly.



### Finding and scope

The interpretation of the relative weights is reversed. This does not determine empirical performance, and an overall gradient-scale change can be absorbed into the learning rate.



### Proposed correction

Distinguish absolute scale from relative weighting and other definitions of bias; correct mitigation sentence under displayed criterion.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.
