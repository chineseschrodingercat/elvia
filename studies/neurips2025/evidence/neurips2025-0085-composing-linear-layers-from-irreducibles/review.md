# Composing Linear Layers from Irreducibles



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The full Clifford-action determinant loses orientation information, and two release differentiation/boundary paths need correction. The implemented even-rotor forward family is not shown to contain the forbidden reflection.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Full-action orientation does not identify the spin image

Assessment: supported; impact: minor



Source: Appendix B, Property 3, pp. 27–28.



### Source claim (paraphrase)

Property 3 characterizes the spin image using grade preservation and positive determinant on the entire Clifford algebra.



### Analysis

In \(\mathrm{Cl}(2)\), conjugation by \(g=e_1\) has matrix \(\operatorname{diag}(1,1,-1,-1)\) in the scalar/vector/bivector basis. It preserves grades and has full determinant \(+1\), but its grade-one block has determinant \(-1\), a reflection unavailable to a \(\mathrm{Spin}(2)\) rotor. More generally the full exterior lift has determinant \((\det R)^{2^{n-1}}\), losing the sign for \(n\geq2\).



### Finding and scope

The characterization is too broad. The actual even-rotor forward parameterization is not shown to realize that reflection.



### Proposed correction

Impose \(\det(N_g|_{\mathrm{Cl}^1})=1\) on the grade-one action, together with the stated orthogonality and grade conditions.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Detached decomposition omits fixed-point dependence

Assessment: supported; impact: minor



Source: Section 4.1, PDF pp.5–6; Appendix B, Theorems 2–3; rotor_layer.py, Rotor._update_rotors, lines 164–180



### Source claim (paraphrase)

The release solves a decomposition without gradient tracking, then reruns with detached warm-start vectors.



### Analysis

For bivector \(b=1.2e_{12}+0.6e_{34}+he_{13}\), the selected matrix entry’s recomputed exponential derivative is approximately \(-0.23271515\), whereas the released backward path gives \(-0.22552789\). Recomputed forward finite differences support the former. Detaching spectral/fixed-point state omits its parameter dependence.



### Finding and scope

The backward rule is not the derivative of the recomputed rotor map on this control. Surrogate-gradient training may still be useful.



### Proposed correction

Track the relevant decomposition iterations or supply a valid implicit derivative under stated nondegeneracy conditions. A local differentiable-iteration control does not prove stability at all spectral collisions.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: Zero simple components need an exponential limit and stable shape

Assessment: supported; impact: minor



Source: Eq.(5), PDF p.5; current author README prescribed torch_ga_fix submission branch at 376a48bfeeba2e76ef42abee6fe516a349d8d3bb, torch_ga/torch_ga.py, exp_simple_batched



### Source claim (paraphrase)

The author README prescribes the torch_ga_fix submission branch. Its current exp_simple_batched divides a component by its norm before multiplying by sine and squeezes a singleton dimension.



### Analysis

A zero component therefore gives \(0/0\) instead of the identity exponential. Even nonzero simple input \(e_{12}\) in \(\mathrm{Cl}(4)\) leaves a zero second component after decomposition, so zero input is not the only boundary. A singleton batch can additionally lose the axis needed by concatenation.

The dependency’s separate default-main branch contains another API with an explicit zero-angle branch. That is opposing evidence against a claim covering every dependency version; it does not remove the defect from the current author-prescribed submission branch.



### Finding and scope

The helper is undefined on legitimate simple-component inputs. Random dense-training incidence is unknown.



### Proposed correction

Use \(\exp(b)=\cos q+\operatorname{sinc}(q/\pi)b\), \(q=\|b\|\), with normalized sinc value \(1\) at zero, and preserve the batch axis.

The currently prescribed submission branch retains the defect. A different default-main implementation has zero-angle handling, but its integration into the paper release was not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
