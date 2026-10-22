# Bridging Equivariant GNNs and Spherical CNNs for Structured Physical Domains



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Archived preprocessing breaks rotation and sample/state invariants; released split/evaluation paths can overlap and the drag MSE logger broadcasts across samples. These are local release findings, not reproduced physical benchmarks.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The released mesh encoder violates rotation rules before its equivariant blocks

Assessment: supported; impact: minor



Source: Introduction, PDF p. 2; Section 3, PDF p. 4; Section 4, PDF pp. 5–6; Appendix G.1.2, PDF pp. 26–27.



### Source claim (paraphrase)

Paraphrase: The introduction, p. 2, describes an end-to-end \(SO(3)\)-equivariant mapping. Section 3, p. 4, bases that property on each component being equivariant. Section 4, pp. 5-6, and Appendix G.1.2, pp. 26-27, use Equiformer v2 to encode meshes into harmonic features before spherical decoding. The public README makes the corresponding architectural claim.

Two concrete operations in the pinned mesh path fail the prerequisites of that composition argument. They are grouped here because they invalidate the same proposed implementation guarantee; repairing either one alone leaves the other unresolved.



### Analysis

A nonzero edge \((1,-1,0)\) is removed by the released coordinate-sum test, but a rotation can give it nonzero coordinate sum and retain it. Separately, axis-bin lookups populate \(\ell=0\) scalar slots with coordinate-dependent values that change under rotation. Thus the released preprocessing violates the prerequisites of the equivariant-block composition argument. This identifies a release-level failure of the claimed implementation contract, not the historical experiment path.

For the nondegenerate triangle \[(0,0,0),(1,-1,0),(0,0,1)\], a quarter-turn about the last axis changes an edge coordinate sum from \(0\) to \(-2\), with unchanged edge length. Separately, scalar initialization \(E_{q(x)}+E_{q(y)}+E_{q(z)}\), with admissible \(E_j=j^2\), changes from \(14827\) at \((1,0,0)\) to \(9874\) at its half-turn image \((-1,0,0)\), contrary to the degree-zero rotation rule.



### Finding and scope

The inspected release is not justified as end-to-end equivariant by the stated component argument. Its use in the published runs and the effect on benchmark accuracy are unestablished.



### Proposed correction

Use a rotation-invariant nonzero-edge norm predicate and initialize scalar channels from invariant quantities such as \(\|p\|_2\). These repairs address the exhibited intermediate rules, without proving full-model equivariance.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 2: Released split procedures do not produce an independent evaluation set

Assessment: supported; impact: minor



Source: Section 5.1, Figures 3–4, PDF pp. 7–9; Table 1, PDF p. 6; Appendix J.1, PDF p. 31.



### Source claim (paraphrase)

Paraphrase: Section 5.1 and Figures 3-4, pp. 7-9, assess generalization to unseen geometries. Appendix J.1, p. 31, separates radar train/validation material from test material. Table 1, p. 6, reports prediction MSE averaged over three seeds. These uses require a clear separation between examples used for model selection and the final test examples.

The public launcher, scripts/train.py, lines 17-21, seeds the global generators once and then constructs separate train, validation, and test dataset objects. The release contains two distinct split problems: independently regenerated drag partitions and radar validation selected directly from the test file.



### Analysis

Independent random repartitioning of the same source on train/validation/test construction does not produce complementary partitions and can overlap identities. The radar configurations are stronger counterevidence: validation and test explicitly use the same retained file. Neither observation identifies all historical table-producing splits.

The radar configuration samples validation from test_radar.nc and tests on that entire file. Thus \(V\subseteq T\) and \(V\cap T=V\), independently of seed. Radar train/test overlap is not inferred.



### Finding and scope

The released split construction does not guarantee independent held-out evaluation. The historical table-producing partitions are not identified, so no numerical leakage effect or corrected performance estimate is asserted.



### Proposed correction

Save and reuse one identity manifest; draw radar validation from training material and preserve the test file for final evaluation. Respect shared-geometry groups as well as rows.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 3: The drag MSE logger broadcasts predictions across the batch

Assessment: supported; impact: minor



Source: Table 1, PDF p. 6; released g2s/lightning/drag.py, lines 44–46 and 59–94.



### Source claim (paraphrase)

Paraphrase: Table 1, p. 6, reports mean squared prediction errors for mesh-to-sphere tasks. The corresponding public drag module logs {stage}/mse_error in g2s/lightning/drag.py, lines 44-46 and \(59\)-94.

The source trace is important because the bug is not in every loss calculation. Mesh2Drag.forward, g2s/models/geometry_2_sphere.py, lines 187-197, returns a spherical harmonic evaluation for one direction per sample. In the linked EquiHarmony implementation, SphericalHarmonics.forward, lines 85-98, that path returns shape \((B,1,1,1)\) for one output channel. The dataset target is reshaped to \((1,)\), so batch collation gives \((B,1)\). The logger subtracts the two tensors without aligning their shapes.



### Analysis

Prediction shape \((2,1,1,1)\) and target shape \((2,1)\) broadcast into all cross-sample differences. For perfect paired values \((-1,1)\), the resulting differences are \((0,-2,2,0)\), whose mean square is \(2\), while paired MSE is \(0\). This is a logger shape mismatch, separate from the correctly aligned loss paths.

The configured training loss squeezes both tensors and checkpoint selection monitors that loss; this does not establish an all-pairs training objective or identify the metric exported to Table 1.



### Finding and scope

A perfect-prediction witness disproves the logger, while the aligned training loss and unknown table-export path bound its demonstrated impact.



### Proposed correction

Reshape predictions and targets to the same sample-feature shape and assert equal dimensions before subtraction. For scalar targets, a common shape \((B,1)\) produces the intended mean of corresponding squared errors.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 4: Repeated access overwrites the stored physical flight conditions

Assessment: supported; impact: minor



Source: Appendix J.2, PDF p. 31; released DragDataset.__getitem__, lines 114–117.



### Source claim (paraphrase)

Appendix J.2, p. 31, defines the drag samples using geometry, flight conditions, and a drag coefficient at the supplied orientation. In the public DragDataset.__getitem__, lines 114-117, the first three floating-point fields are converted with torch.from_numpy(self.float_data[idx][:\(3\)]), then each resulting tensor element is normalized by an in-place assignment.

The issue is functional preprocessing state, not a manuscript spelling error: from_numpy shares the NumPy slice’s storage. Assigning normalized values through that tensor overwrites the dataset’s original physical values. A later access therefore normalizes values that have already been normalized.



### Analysis

torch.from_numpy shares storage with the source slice. The first in-place normalization maps midpoint physical conditions to stored values \((0,0,0)\); the next access treats those normalized zeros as physical inputs and normalizes them again. The sample therefore depends on how often it has been accessed, rather than being a fixed preprocessing function.

For physical values \((25,250500000,0.25)\), first access stores normalized zeros. A second access then gives \((-1,-1-2/499,-1)\), instead of unchanged zeros. Fresh nonpersistent worker copies can prevent accumulation across epochs.



### Finding and scope

Repeated access mutates one stored sample; actual exposure depends on worker and access lifecycles.



### Proposed correction

Copy the source slice or clone its tensor before in-place normalization.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 5: A mesh with no padding is reduced to an empty vertex array

Assessment: supported; impact: minor



Source: Released g2s/datasets/mesh_dataset.py, MeshXarrayDataset._unpad_mesh_data, lines 211–224.



### Source claim (paraphrase)

The radar mesh path uses MeshXarrayDataset._unpad_mesh_data, g2s/datasets/mesh_dataset.py, lines 211-224. The helper requires a two-dimensional array with three columns and uses a configured sentinel, normally \(-10\), to identify placeholder rows before mesh reconstruction. Its explicit assumption is that a real mesh row does not have the sentinel in all three coordinates.



### Analysis

With no padding rows, num_placeholders is \(0\), and the released slice input[:-num_placeholders] becomes input[:\(0\)], an empty array. A valid unpadded triangle is erased. Appending one sentinel row gives a positive count and correctly restores the triangle, explaining why ordinary padded examples can pass.



### Finding and scope

The no-padding boundary empties a valid mesh; its incidence in the evaluated dataset is unknown.



### Proposed correction

Retain non-sentinel rows directly, preserve unchanged data when padding is disabled, and reject all-padding meshes before downstream geometry.

A local correction or qualification is proposed where specified; author adoption is not established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
