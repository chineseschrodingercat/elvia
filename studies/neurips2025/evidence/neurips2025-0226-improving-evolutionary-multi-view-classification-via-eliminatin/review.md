# Improving Evolutionary Multi-View Classification via Eliminating Individual Fitness Bias



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The ranking table correlates individual identifiers rather than aligned ranks; corrected coefficients show high agreement. The HSIC ground cost can favor disagreement. Current teacher alignment and test-label selection introduce narrower release/protocol defects.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: Rank correlations were computed on identifiers

Assessment: supported; impact: major



Source: Table 3 and ranking interpretation, p.9; Tables 4 and 7



### Source claim (paraphrase)

Table 3 lists the same \(15\) individual IDs in descending order, but reports Pearson/Spearman \(0.2143\) and Kendall \(0.1429\) as nearly uncorrelated rankings.



### Analysis

The orderings are \[a=(4,15,5,7,1,8,13,10,11,2,14,6,12,3,9)\] and \[b=(4,15,5,7,8,13,2,11,1,10,12,6,14,9,3)\]. Inverting them to ranks keyed by common ID gives squared displacement sum \(42\). Spearman is \(1-6(42)/(15(15^2-1))=0.925\), also Pearson of rank vectors. The \(11\) discordant and \(94\) concordant pairs give Kendall \(83/105\approx0.790476\), retaining the reported reversal count. Correlating the arbitrary ID arrays directly reproduces \(3/14,3/14,1/7\). Their numerical distances have no ranking meaning.



### Finding and scope

The rankings have substantial agreement. Real reversals remain, and this calculation does not establish which ordering is closer to independently optimal performance.



### Proposed correction

Invert both orderings to common-ID ranks and report approximately \(0.9250,0.9250,0.7905\). Retain reversals and revise the near-zero-correlation interpretation.

A proposed correction is described; author adoption is not established.



## Problem 2: HSIC transport can favor teacher disagreement

Assessment: supported; impact: major



Source: Section 3, Eqs.(1)–(5); code/HSIC/HSIC.py; code/new_loss.py



### Source claim (paraphrase)

The loss minimizes transport cost using HSIC inner-product similarity directly, charging greater association more.



### Analysis

Use three teacher groups with logit columns \(x_1=(5,2\log0.9,2\log0.1)\), \(x_2=(-1,2,-1)/\sqrt2\), \(x_3=\sqrt{3/2}(-1,0,1)\). Unique argmax coordinates give the required class groups. The latter vectors are centered orthogonal with squared norm \(3\), so their HSIC submatrix is \(I_2\). At temperature \(2\), teacher non-target distribution is \(p=(0.9,0.1)\). Matching it requires diagonal coupling mass at least \(0.8\), hence cost \(0.8\); swapped student \((0.1,0.9)\) admits zero-cost off-diagonal coupling. Swapping those logits preserves target probability and target-category loss, so the distillation component prefers disagreement by \(0.8\beta\), \(\beta>0\).



### Finding and scope

This contradicts the intended guidance component, not the full fusion objective. Appendix datasets using KL instead of HSIC are excluded.



### Proposed correction

For \(F_i=HK_iH/C\), use \(d_{ij}=\|F_i-F_j\|_F=\sqrt{M_{ii}+M_{jj}-2M_{ij}}\), a metric on distinct representations and a pseudometric when they coincide. Matching then costs zero and swapping \(0.8\sqrt2\). Full retraining remains unvalidated.

A proposed correction is described; author adoption is not established.



## Problem 3: Teacher alignment can fail by view and sample

Assessment: supported; impact: minor



Source: code/train_tree_youtube.py, loss loop around lines 65–78; code/new_loss.py, separated-loss entry



### Source claim (paraphrase)

Stored lambdas share a late-bound view index; each batch also gathers a prefix of the full teacher array from batch size alone.



### Analysis

After constructing views \(0,1\), both lambdas can use final index \(1\). Independently, a batch with sample IDs \((2,3)\) gathers teacher rows \((0,1)\), despite compatible shapes. A single view and full-batch original-order training are passing special cases; the released minibatch path has neither guarantee.



### Finding and scope

The current path need not distill from the same view/sample. Historical checkpoint and table effects remain unknown.



### Proposed correction

Bind each view/teacher/cost at construction. Carry stable sample IDs or aligned teacher batches through joint shuffling; do not gather a global prefix again.

A proposed correction is described; author adoption is not established.



## Problem 4: YouTubeFace test labels enter selection

Assessment: supported; impact: minor



Source: Section 4 evaluation protocol; code/train_tree_youtube.py, lines 34–37 and 91–107; code/gen_offspring_tree.py



### Source claim (paraphrase)

Test labels are passed as validation labels; maximum validation accuracy selects checkpoints and evolutionary fitness.



### Analysis

The dependency reaches the returned architecture even without test gradients. Two independent one-example test scores with success probability \(1/2\) each have expected score \(1/2\), but their selected maximum has expectation \(3/4\). This illustrates selection optimism, not its size here. Outer test folds do not remove within-fold selection dependence. Other datasets explicitly have validation splits and are not automatically implicated.



### Finding and scope

The released selected-test score is not untouched evaluation. An unpublished independent final test could alter the historical conclusion.



### Proposed correction

Use inner validation for teachers, checkpoints and evolutionary fitness within each outer training split. Freeze selection before outer-test evaluation; corrected scores require re-evaluation.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.
