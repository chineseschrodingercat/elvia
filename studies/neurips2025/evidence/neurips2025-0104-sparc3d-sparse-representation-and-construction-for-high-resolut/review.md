# Sparc3D: Sparse Representation and Construction for High-Resolution 3D Shapes Modeling



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The unsigned hole-filling angle needs an explicit admissible-ear restriction, and the paper's own table limits the claim of universal remeshing superiority.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The unsigned angle score does not by itself identify a convex ear

Assessment: supported; impact: minor



Source: Section 3.3, Hole Filling, Eq. (8), PDF p. 6.



### Source claim (paraphrase)

Section 3.3, Hole filling, PDF p. 6, Eq. (8), specifies the score

\[ A_i=\operatorname{atan2}\!\left( \|d_{i-1\to i}\times d_{i\to i+1}\|_2, -d_{i-1\to i}\cdot d_{i\to i+1}\right). \]



### Analysis

The counterclockwise polygon with vertices \[(0,0),(10,0),(10,10),(5.5,10),(5,1),(4.5,10),(0,10)\] has a narrow reflex notch. The cross-product norm removes the orientation sign, so a reflex vertex can receive the smallest unsigned angle even though the proposed ear lies outside the polygon. Uniform scaling preserves the counterexample, including for small holes.

At the notch vertex \((5,1)\), incoming and outgoing vectors \((-0.5,-9)\) and \((-0.5,9)\) have signed cross product \(-9\) and negative dot product \(-80.75\). Its unique minimum score is \(\operatorname{atan2}(9,80.75)\approx6.35966^\circ\), while the triangle centroid \((5,7)\) lies in the excluded notch. The written unrestricted selection therefore chooses an exterior triangle. An implicit standard ear-admissibility guard would reject it, so this does not prove a defect in unavailable code.



### Finding and scope

The unrestricted written angle rule fails on a simple planar boundary. Whether the actual hole-filling implementation already applies a valid-ear guard remains unresolved.



### Proposed correction

Restrict candidate ears using a planar convexity and interior-admissibility test before ranking their angles. This local proposal does not establish a triangulation guarantee for arbitrary nonplanar boundaries.

A local correction or qualification is proposed where specified; author adoption is not established.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 2: The reported remeshing results do not establish dominance on every metric

Assessment: supported; impact: minor



Source: Section 4.2, Table 1, PDF p. 7.



### Source claim (paraphrase)

Section 4.2, PDF p. 7, describes Table 1 as superiority across every dataset and metric. Table 1 marks Absolute Normal Consistency as a quantity to maximize.



### Analysis

Table 1 reports Objaverse Absolute Normal Consistency \(75.77\) for Dora and \(75.35\) for Sparc3D at resolution \(512\); at resolution \(1024\), the corresponding entries are \(75.04\) and \(74.98\). Since the metric is maximized, both comparisons contradict dominance on every dataset/metric. The table also supports improvements on other metrics and datasets; no significance or practical-importance claim is made for these small deficits.



### Finding and scope

Supported wording correction bounded to the displayed comparisons.



### Proposed correction

State that Chamfer distance and F1 improve on all tested datasets, while Objaverse normal consistency is slightly lower than Dora at both matched resolutions.

A local correction or qualification is proposed where specified; author adoption is not established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
