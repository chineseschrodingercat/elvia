# Multi-dataset Joint Pre-training of Emotional EEG Enables Generalizable Affective Computing



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Current CDA code interleaves channels before covariance, deletes variances and uses an unsquared distance. The evaluator selects checkpoints on final evaluation subjects. Fixed DEAP labels remain conditional on unavailable preprocessing/order information; no published accuracy is recomputed.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: The released CDA objective is a different tensor operation

Assessment: supported; impact: minor



Source: Eqs.(1)–(4), pp.4–5; src/loss/CDA_loss.py, lines 11–48; src/model/MultiModel_PL.py, lines 199–203



### Source claim (paraphrase)

Temporal covariance should be \(HH^{\top}/(T-1)\). The code permutes \((B,d,C,T)\) to \((B,d,T,C)\), reshapes back without undoing the interleaving, zeros the diagonal and uses unsquared Frobenius distance.



### Analysis

For centered \(H=[(-1,0,1);(-2,0,2)]\), correct covariance is \(\left(\begin{smallmatrix}1&2\\2&4\end{smallmatrix}\right)\). The permute/reshape instead forms rows \((-1,-2,0),(0,1,2)\), yielding \(\left(\begin{smallmatrix}5/2&-1\\-1&5/2\end{smallmatrix}\right)\), then returns diagonal-zero matrix with cross-entry \(-1\), not \(2\), and eigenvalues \(1,-1\). Even otherwise correct diagonal deletion makes \(I_2\) and \(4I_2\) identical despite squared distance \(18\). Separately, a valid covariance difference \(D=[(0,2);(2,0)]\) contributes \(\log(1+\sqrt8)\), not the paper’s \(\log9\). No constant coefficient adjustment equates the two powers generally.



### Finding and scope

The current path does not implement the written covariance/centroid objective. It could define another regularizer, but the interleaving is not a covariance convention; experimental effects remain unknown.



### Proposed correction

Retain centered channel/time ordering, compute \(HH^{\top}/(T-1)\) for \(T>1\), preserve diagonals and sum squared centroid differences. The matrix identity proves correspondence; new pretraining and ablations would assess effects.

A proposed correction is described; author adoption is not established.



## Problem 2: Checkpoint choice uses final evaluation subjects

Assessment: supported; impact: minor



Source: Section 3.3; train_mlp_full.py, lines 39–51 and 92–140



### Source claim (paraphrase)

The subjects labeled test determine maximum validation-accuracy checkpoint selection and are reused for final predictions.



### Analysis

The same loader enters training validation, best-model selection and final scoring. Exclusion from gradient updates does not remove this dependency. For four independent fair test labels and fixed constant-zero/constant-one candidates, selecting the better test accuracy has expectation \(11/16\), while each fixed candidate has expectation \(1/2\). This is a selection illustration, not estimated inflation here. A separate unpublished final-test implementation could change historical attribution.



### Finding and scope

The released score is test-dependent selection accuracy rather than untouched-subject performance. No claim that every published table used this script is made.



### Proposed correction

Use subject-level development data for selection and untouched outer test subjects for final reporting, or fix an epoch before seeing those outcomes.

A proposed correction is described; author adoption is not established.



## Problem 3: DEAP labels require an unavailable ordering contract

Assessment: needs_evidence; impact: needs_evidence



Source: Section 3.1 and Appendix E.8; src/data/io_utils.py, lines 421–465; train_mlp_full.py, lines 68–71



### Source claim (paraphrase)

The paper defines participant-rating median splits, but the loader returns \(20\) zeros then \(20\) ones for every subject and evaluation tiles one label vector.



### Analysis

Two subjects with first/last half ratings \((1,9)\) and \((9,1)\) both have median \(5\), yet complementary correct labels. A single tiled vector cannot match both; this is a valid protocol witness, not actual DEAP data. The code may depend on per-subject label-sorted preprocessing or shared stimulus labels, but the required original trial permutations and affective dimension are unavailable. Subject-specific sorting must also preserve correct stimulus pairing.



### Finding and scope

The released route alone does not specify the rating-based task. Without actual preprocessing/labels, wrong published DEAP accuracy is not established.



### Proposed correction

Recover subject/trial/dimension-indexed labels and any permutations, with explicit median/tie rules and stimulus-aligned pairing. No numerical correction is established.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.
