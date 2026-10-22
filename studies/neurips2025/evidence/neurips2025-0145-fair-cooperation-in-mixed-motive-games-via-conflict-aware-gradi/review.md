# Fair Cooperation in Mixed-Motive Games via Conflict-Aware Gradient Adjustment



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Bounded smooth counterexamples refute finite-step protected improvement, universal fairness convergence and the simultaneous-update extension. The reported empirical gains are not themselves disproved.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: Orthogonal projection does not preserve an objective after a positive finite step

Assessment: supported; impact: major



Source: Theorem 3.1, PDF p. 5; Theorem B.2, PDF p. 14.



### Source claim (paraphrase)

Paraphrase: Theorem 3.1, p. 5, and its restatement as Theorem B.2, p. 14, assert that differentiable \(L\)-smooth individual and collective objectives both do not decrease under the FCGrad update for sufficiently small \(\eta>0\). The conflict-case proof uses \(b^\top g=0\) to infer preservation of the collective objective.



### Analysis

At \((0,0)\), take bounded \(1\)-smooth objectives \(I(x,y)=\sin x+\sin y\) and \(C(x,y)=1-\sin x+\cos y\). Their gradients are \((1,1)\) and \((-1,0)\); conflict projection leaves direction \((0,1)\), orthogonal to \(\nabla C\). Nevertheless \(C(0,\eta)=1+\cos\eta<2=C(0,0)\) for every sufficiently small \(\eta>0\). A zero directional derivative does not ensure a nonnegative finite-step change.



### Finding and scope

The theorem's finite-step protection is false under its smoothness assumptions. The example leaves observed empirical gains unadjudicated.



### Proposed correction

The existing direction supports first-order protection only: smoothness gives \(C(\theta+\eta g)-C(\theta)\geq-L\eta^2\|g\|^2/2\). A separate proposed common-ascent modification applies only to noncollinear conflicting gradients: for \(q=a^\top b<0\), let \(h=a-qb/\|b\|^2\), \(m=\|h\|^2>0\), and \(d=h+mb/[2(-q)]\). Then \(a^\top d=m/2>0\), \(b^\top d>0\); a sufficiently small step improves both fixed-agent objectives. This changes the algorithm and does not establish fairness convergence or simultaneous-agent improvement.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 2: Recurrent conflicts can leave a nonzero value gap forever

Assessment: supported; impact: major



Source: Theorem 3.2, PDF p. 5; Theorem B.5, PDF p. 16.



### Source claim (paraphrase)

Paraphrase: Theorem 3.2, p. 5, and Theorem B.5, p. 16, assume \(L\)-smooth values, \(\delta_t=V_{\rm ind}(\theta_t)-V_{\rm col}(\theta_t)\), positive steps satisfying

\[\eta_t\leq|\delta_t|/L,\qquad \sum_t\eta_t=\infty,\qquad \sum_t\eta_t^2<\infty,\]



### Analysis

Let \(I(\theta)=\sin\theta\), \(C(\theta)=1-\sin\theta\), and \(\theta_0=0\). Their opposing gradients \(1,-1\) project to zero, so every iterate remains zero and the value gap stays \(-1\). Steps \(\eta_t=1/(t+1)\) satisfy the upper bound, divergent sum and square-summable condition with \(L=1\). Conflict recurs forever without progress toward equal values.



### Finding and scope

The universal fairness-convergence conclusion requires a nondegeneracy or progress assumption absent from the stated theorem.



## Problem 3: Local guarantees do not imply individual improvement under simultaneous multi-agent updates

Assessment: supported; impact: major



Source: Paragraph following Theorem 3.1 and Section 3.1 single-agent parameters, PDF p. 5.



### Source claim (paraphrase)

The paragraph immediately after Theorem 3.1, p. 5, extends the single-agent result to all agents when all use FCGrad. The mathematical objects in Section 3.1 are gradients with respect to the parameters of one agent.



### Analysis

Take returns \(R_1=\sin\theta_1-3\sin\theta_2\) and \(R_2=3\sin\theta_1+4\sin\theta_2\), with collective return \((R_1+R_2)/2\). At zero, with the allowed mixing weight \(\beta=1/2\), the nonconflict FCGrad directions are \(1.5\) and \(2.25\). Each own-coordinate update improves its local objectives, but their simultaneous effect on \(R_1\) has derivative \(1.5-3(2.25)=-5.25\). The single-agent argument leaves these cross-agent terms uncontrolled.



### Finding and scope

The stated simultaneous-update extension does not follow and fails on this bounded smooth game. A separate multi-agent guarantee would need additional assumptions.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
