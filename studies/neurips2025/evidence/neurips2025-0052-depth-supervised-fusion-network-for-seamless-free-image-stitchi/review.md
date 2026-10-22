# Depth-Supervised Fusion Network for Seamless-Free Image Stitching



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The public training paths pass RGB tensors to a depth loss, convert decoder branches to frozen deployment modules during training, and divide by zero on constant depth maps. The correspondence of these paths to the published experiments is unresolved.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Depth-loss inputs are warped RGB tensors

Assessment: supported; impact: minor



Source: Section 3.1, PDF p.5, Eqs.(8)–(9); Warp/newCodes/train.py, lines 78–115



### Source claim (paraphrase)

Section 3.1, Eqs.(8)–(9), defines an alignment loss on the estimated depth maps. The released transformation trainer instead passes the RGB warp outputs into that discrepancy.



### Analysis

Equal depth maps under identity geometry should give identical compared depth tensors and zero residual. The traced RGB arguments can differ despite those equal depths; the finite identity-geometry example yields \(7/3\) rather than \(0\). This follows from the input dataflow and does not require a trained model.



### Finding and scope

The released loss call mixes modalities. It does not identify which historical training program produced the paper’s tables.



### Proposed correction

Warp the depth maps and validity masks with the already predicted transformations, then compare those depth outputs. For equal nonconstant maps under identity geometry, each residual vanishes directly.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Deployment conversion freezes replacement decoder modules during training

Assessment: supported; impact: minor



Source: Section 3.2, PDF pp.5–6, Eq.(14); Fusion/newCodes/network.py, build_model and RepConvN.fuse_convs; Fusion/newCodes/train.py, lines 42–48, 77 and 105



### Source claim (paraphrase)

Section 3.2 describes optimizing the fusion-mask network. `Fusion/newCodes/train.py` constructs its optimizer before `build_model` invokes deployment conversion inside the training loop.



### Analysis

The conversion replaces branch parameters with frozen convolution modules. The optimizer retains the old parameter objects, while the replacements are not trainable. Backpropagation therefore cannot perform the intended decoder-branch updates. This concerns the decoder path, rather than a blanket prohibition on branch fusion in the separate transformation estimator.



### Finding and scope

The public fusion trainer does not preserve the intended trainable decoder parameterization. The historical experimental path remains unidentified.



### Proposed correction

Use the unconverted decoder during training and convert an evaluation copy after optimization. Training a fused architecture is a different recipe and requires trainable replacement parameters and a matching optimizer.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: Constant depth maps make min–max normalization undefined

Assessment: supported; impact: minor



Source: Section 3.1, PDF p.5; Warp/newCodes/loss.py, lines 134–165



### Source claim (paraphrase)

`Warp/newCodes/loss.py`, lines 134–165, normalizes with pooled minimum \(m\), maximum \(M\), and denominator \(M-m\).



### Analysis

For equal constant maps, \(M=m\), so both normalized maps contain \(0/0\). This boundary is finite and nonempty; it is the normalizer, rather than the underlying geometric comparison, that is undefined.



### Finding and scope

The public loss requires a constant-map convention. The frequency of this boundary in the reported training data is unknown.



### Proposed correction

Use a documented positive floor \(s=\max(M-m,\epsilon)\), \(\epsilon>0\), or explicitly map equal constant inputs to zero residual. The floor must suit the representation and precision.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
