# Solver-Free Decision-Focused Learning for Linear Optimization Problems



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Three release-level discrepancies affect neighbor masking, relaxed-solution data flow and runtime measurement. The adjacent-vertex theorem survives, with a separate zero-margin tie qualification.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Value-based padding deletes a real zero neighbor

Assessment: supported; impact: minor



Source: Eq.(4), PDF p.4; methods/lava.py, LAVA.forward, lines 13–21; dataset_augmented.py, slack projection



### Source claim (paraphrase)

LAVA sums truncated adjacent-vertex objective gaps. The release treats an all-zero projected vertex as padding.



### Analysis

Consider minimization on \(0\leq x\leq1\), represented by \(x+s=1\), with true cost \(-x\). The true optimum is \((1,0)\), whose genuine neighbor \((0,1)\) projects to \(x=0\) after slack removal. Predicted cost \(\hat c=1\) selects \(x=0\) with true regret \(1\). The real neighbor gap is \(1\), but the value-based padding test deletes it, yielding zero loss and zero gradient. Separately, mapping gaps below \(-\varepsilon\) to zero differs from the printed clamp: for \(\varepsilon=1/10\), gaps \(-1/5,-1/20\) violate scalar convexity since the midpoint maps to \(0>-1/40\). Their ordinary derivatives nevertheless agree away from the threshold.



### Finding and scope

The zero-neighbor mask changes the defined surrogate and its gradients on an allowed projected LP. The threshold-to-zero scalar difference alone does not establish different updates away from the kink. Proposition 4.1 remains intact.



### Proposed correction

Carry an explicit neighbor-validity mask or count independent of coordinates, and clamp real gaps at \(-\varepsilon\) to match Eq.(4).

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Integer-solution cache and filtering corrupt relaxed neighborhoods

Assessment: supported; impact: minor



Source: Section 5.3, PDF p.8; data/dataset_augmented.py, lines 72–90



### Source claim (paraphrase)

The knapsack workflow trains against relaxed optima, but caches neighbors by the integer optimum and removes neighbors equal to that integer solution.



### Analysis

For \(3x+2y\leq4\), \(x,y\in\{0,1\}\), use costs \((4,3)\) then \((5,3)\). Both integer optima are \(I=(1,0)\); relaxed optima are respectively \(A=(2/3,1)\) and \(B=(1,1/2)\). Their neighbor sets are \(N(A)=\{B,(0,1)\}\) and \(N(B)=\{I,A\}\). Reusing the cache under key \(I\) supplies stale neighbors at \(B\). With predicted maximization cost \(q=(-1,-3)\), stale gaps are \(0,-1/2\), so the release returns no update, while the omitted actual neighbor \(I\) has gap \(3/2\). Even without a cache collision, filtering by the integer solution deletes \(I\). The selected integer decision is the origin, with true regret \(5\) under the second cost.



### Finding and scope

Both data-flow defects are concrete for the supported knapsack/relaxation interface. Their occurrence and effect in the original benchmark arrays are not established.



### Proposed correction

Key by the actual relaxed vertex and constraint identity, or disable caching. Remove a self-neighbor only against that same relaxed label; retain all genuine adjacent vertices.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: Training-time accumulator excludes most training work

Assessment: supported; impact: minor



Source: Section 5.1, PDF pp.7–8; utils/train_model.py, lines 43–44 and 66–103



### Source claim (paraphrase)

The paper describes training time including adjacent-vertex precomputation and actual training, excluding validation, and uses a \(600\)-second budget. The release times only the loss evaluation.



### Analysis

The prediction the regressor forward call precedes the timer; elapsed time is added before zero_grad, backward and optimizer.step. Hence an iteration records approximately \(t_{\rm loss}\), rather than \(t_{\rm pred}+t_{\rm loss}+t_{\rm back}+t_{\rm opt}\). These omitted operations are training, not validation. Precomputation is separately included.



### Finding and scope

The release timing definition does not match the stated protocol. It cannot recover a corrected speedup or establish that the archived commit generated the published plots.



### Proposed correction

Time the complete prediction, loss, backward and optimizer step with a monotonic clock; add precomputation and consistently exclude validation. Remeasure the affected runtime comparisons if this path generated them.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 4: Zero-margin optimality leaves solver ties unresolved

Assessment: not_issue; impact: minor



Source: Proposition 4.1 and sentence preceding Eq.(4), PDF p.4



### Source claim (paraphrase)

Making a labeled vertex predicted-cost optimal is described as giving zero regret, whereas the regret evaluates one selected optimizer.



### Analysis

For the unit square with true cost \((1,1)\), true optimum \((0,0)\), and nonzero predicted cost \((1,0)\), both \((0,0)\) and \((0,1)\) are predicted optima. The adjacent-vertex zero-margin loss is zero, but a solver may choose \((0,1)\), with true regret \(1\). Positive strict adjacent margins instead give a unique optimum, and the experiments use \(\varepsilon=0.1\).



### Finding and scope

This is a tie-handling qualification of a zero-margin interpretation, not a refutation of Proposition 4.1 or the positive-margin method. Tie-independent zero regret requires every predicted optimizer to be a true optimizer.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
