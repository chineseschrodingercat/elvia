# Online Portfolio Selection with ML Predictions



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The fractional-betting lemma puts a zero-growth threshold below one half when the stated formula places it above one half. A ranking notebook also misgroups asset-major rows as date queries. RAM’s geometric-mean floor remains distinct from BCRP universality.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: The fractional-trust threshold lies in the wrong interval

Assessment: supported; impact: minor



Source: Lemma A.1(3), PDF pp.20–21; Section 2, PDF p.5



### Source claim (paraphrase)

Lemma A.1(3) places the zero-growth forecast error \(\epsilon^*(\lambda)\) in \((0,1/2)\) for its stated fractional-trust range.



### Analysis

At \(\lambda=1/2\), correct and incorrect predictions give wealth factors \(13/8\) and \(7/8\). Chance-level expected log growth is \(\tfrac12\log(91/64)>0\). Since growth decreases linearly in the prediction-error probability, the root is \(\log(13/8)/[\log(13/8)-\log(7/8)]\approx0.78429\), above \(1/2\). More generally the interior range \(1/3<\lambda<1\) has its root in \((1/2,1)\).



### Finding and scope

The below-chance fragility interpretation of this lemma is incorrect. The RAM guarantee is a separate statement.



### Proposed correction

Use the actual logarithmic root and distinguish the endpoints \(\lambda=1/3\) and \(\lambda=1\). Fractional trust can retain positive growth at chance-level forecasts in this two-asset example.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Ranking groups do not match the row order

Assessment: supported; impact: minor



Source: Section 3, PDF pp.9–10, Table 4; official notebook cells 34–35



### Source claim (paraphrase)

The official notebook’s `prepare_long` and `build_lgb_dataset`, cell 34, are intended to form one cross-sectional ranking query per date.



### Analysis

The melt operation yields asset-major rows, but the supplied group sizes assume contiguous same-date rows. In a complete panel of three assets and four dates, the first size-three query contains the first asset on dates one through three rather than three assets on one date. Labels, features and weights therefore enter the wrong query grouping.



### Finding and scope

The notebook’s ranking interface is inconsistent. The published wealth values are not recalculated or directly contradicted.



### Proposed correction

Sort the entire feature/label/weight table by date before splitting arrays and constructing consecutive query groups. This repairs membership without claiming recovered investment performance.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: The geometric-mean floor does not imply BCRP universality

Assessment: not_issue; impact: no_issue_found



Source: Theorem 2.1, PDF p.6; introduction/discussion protection interpretation



### Source claim (paraphrase)

Theorem 2.1 supplies \(S_n^{\mathrm{RAM}}\geq(\prod_{i,j}x_j(i))^{1/m}\).



### Analysis

With constant two-asset returns \((2,1/2)\) and consistently wrong ranks, the stated RAM behavior cycles to wealth \(1\) at even horizons, whereas the best constant rebalanced portfolio attains \(2^n\). This separates the geometric-mean comparator from a sublinear log-regret guarantee against BCRP.



### Finding and scope

Theorem 2.1 remains valid in this example. It should be interpreted with its proved comparator.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
