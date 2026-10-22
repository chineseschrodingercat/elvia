# Accurate and Efficient Low-Rank Model Merging in Core Space



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Repeated cached DARE calls alter their own task inputs. Separately, a lossless common isometry cannot itself improve matched positive-rank subspace alignment; the plotted rank/null-space conventions remain unresolved. Lossless core reconstruction is retained.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: DARE overwrites the cached task cores

Assessment: supported; impact: minor



Source: task_merger.py, MatrixPerLayerMerger.get_core_matrices/get_dare_delta_w; released validation-search loop



### Source claim (paraphrase)

The cached M_list is returned and its entries are replaced by masked/rescaled tensors during each trial.



### Analysis

For retained entry \(x\), pruning probability \(p=1/2\), and binary mask \(z\), the first call gives \(2zx\). Resetting the seed repeats \(z\), but the mutated cache makes the second output \(2z(2zx)=4zx\), twice the first. A fresh object gives \(2zx\) again. In general \(j\) repeated same-mask calls give \(zx/(1-p)^j\); removed entries cannot be recovered by a later lower-pruning trial. First isolated calls, \(p=0\), fresh merger objects and non-mutating/full-space paths are countercontrols.



### Finding and scope

Repeated cached hyperparameter trials or final reconstruction can depend on earlier trials. The exact reported cells affected and changed accuracy remain unestablished.



### Proposed correction

Keep cached cores unchanged and build a local masked/rescaled list, retaining the first-call arithmetic and random stream. Re-run affected searches before replacing benchmark results.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: A lossless common coordinate map preserves matched SAR

Assessment: supported; impact: minor



Source: Section 5.2/Figure 5, latest PDF p.10; common-basis construction, pp.4–5



### Source claim (paraphrase)

The text attributes higher core-space SAR to the shared basis filtering task-specific noise.



### Analysis

For exact \(X=UM_XV^\top,Y=UM_YV^\top\), \(U^\top U=V^\top V=I\), and corresponding positive-singular-value subspaces, a compact SVD gives \(P_{Y,k}=U\widetilde U_k\widetilde U_k^\top U^\top\). Isometry preserves Frobenius numerator and denominator, hence \(\|P_{Y,k}X\|_F/\|X\|_F=\|\widetilde U_k\widetilde U_k^\top M_X\|_F/\|M_X\|_F\). Tied blocks require consistent transport. If \(k\) exceeds rank, arbitrary null completion changes SAR: \(X=\operatorname{diag}(0,1,0)\), \(Y=\operatorname{diag}(1,0,0)\), \(k=2\) gives \(1\) with completion \((e_1,e_2)\), but \(0\) with \((e_1,e_3)\).



### Finding and scope

The lossless coordinate change cannot itself remove represented task components or increase matched intrinsic alignment. Different rank budgets/null completions can explain changed diagnostics; the plotted numbers are not declared false, and nonlinear core merging can still change performance.



### Proposed correction

State exact rank/tie/null-space conventions and distinguish coordinate isometry from subsequent nonlinear merging. A changed diagnostic requires an explicit extra operation or selection rule.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
