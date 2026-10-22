# SGCD: Stain-Guided CycleDiffusion for Unsupervised Domain Adaptation of Histopathology Image Classification



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The later public SGCD release uses target labels for selection and has missing optimizer updates, disabled guidance, an inconsistent sampler and wrong cycle routing. These are separate release defects, without proof that the original AUC tables used this code.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Target class labels determine adaptation-sample selection

Assessment: supported; impact: minor



Source: Introduction and Section 4.3, PDF pp.1 and 7; main.py, lines 61–84 and 129



### Source claim (paraphrase)

`main.py` constructs the target training `CoordDataset` with class balancing enabled; the loader obtains labels from filename prefixes before downsampling.



### Analysis

Changing only those target class annotations can therefore change which image identities enter adaptation, even if minibatch labels are later discarded. In the balanced-subset operation, label information has already affected the training input. An externally predeclared curator subset would be a different protocol.



### Finding and scope

The release is not strictly label-blind target adaptation. Accuracy advantage, patient leakage and historical split preprocessing are not established.



### Proposed correction

Use all eligible target training images or a selection rule independent of their class annotations. Identify any external subset manifest explicitly.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Target-test AUC selects saved checkpoints

Assessment: supported; impact: minor



Source: Section 5, PDF pp.7–9; main.py, lines 130–135 and 552–559



### Source claim (paraphrase)

The release repeatedly evaluates the dataset explicitly opened in testing mode and saves model components when its AUC improves.



### Analysis

For fixed scores \((0.1,0.9,0.6,0.7)\) and \((0.1,0.2,0.3,0.4)\), labels \((0,0,1,1)\) give AUCs \((0.5,1)\); reversing labels gives \((0.5,0)\). The selected epoch changes with test labels while predictions are fixed. This is model selection rather than logging alone.



### Finding and scope

The release uses test outcomes in selection. Its historical optimism or effect on reported AUC is unknown.



### Proposed correction

Select by an independently declared validation rule or prespecified epoch, then evaluate on untouched final test data. A labeled target validation set changes the supervision protocol.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: The classifier branch backpropagates without stepping its optimizer

Assessment: supported; impact: minor



Source: Section 4.3, Eq.(9), PDF p.7; main.py, lines 373–388 and 521–543



### Source claim (paraphrase)

Section 4.3 specifies classifier optimization. The classifier branch calls backward, but the only optimizer step in the surrounding loop is inside the diffusion branch.



### Analysis

For \(L(w)=w^2/2\) at \(w=1\), backward creates gradient \(1\) but leaves the parameter unchanged; SGD at rate \(0.1\) would give \(0.9\). The diffusion optimizer owns different parameters and cannot substitute. Batch-normalization buffers may still change.



### Finding and scope

The public classifier branch omits parameter optimization, not every possible change in its function.



### Proposed correction

Use a persistent classifier optimizer, matching scheduler and explicit intended trainable parameter set; clear gradients, backpropagate and step in that phase.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 4: Guidance is bypassed and its dormant derivative is incomplete

Assessment: supported; impact: minor



Source: Section 4.1, Eq.(3), PDF p.5; Algorithm 2, PDF p.15; main.py, lines 278–321



### Source claim (paraphrase)

The reverse function sets `guide` false internally; its dormant routine returns a normalized residual without the clean-estimator Jacobian and ignores its locally zeroed cutoff scale.



### Analysis

With \(A_t=1/4\), denoiser \(\epsilon(x)=2x/\sqrt3\) and reference \(1\), the clean estimate is \(2x-\sqrt3\epsilon(x)=0\). The norm of its difference from the reference is constant, so its derivative is zero. The dormant normalized residual is instead \(-1\). This occurs away from the norm’s nondifferentiable boundary.



### Finding and scope

The release neither applies requested guidance nor computes the stated full derivative if merely enabled.



### Proposed correction

Honor the guidance flag and cutoff, and differentiate through the declared clean-image estimator, or explicitly specify and evaluate a different approximation.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 5: The custom sampler doubles variance and mismatches time indices

Assessment: supported; impact: minor



Source: Eq.(2), PDF p.3; Algorithm 2, PDF p.15; main.py, lines 259–274, 318–319 and 596



### Source claim (paraphrase)

The custom reverse step combines a deterministic direction with an unreduced additional noise variance; its loop skips ten indices while the step uses the immediate preceding index.



### Analysis

For a point-mass clean distribution and exact denoiser with \(A_t=0.64\), \(A_s=0.81\), the step gives \(x_s=\sqrt{0.19}\epsilon+\sqrt{0.19}z\) for independent standard normals, hence variance \(0.38\) instead of \(0.19\). A loop at times \((30,20,10,0)\) first transitions using index \(29\), then treats that output as time \(20\). The final \(T=5\) setting never reaches a clean endpoint under that stride.



### Finding and scope

The released kernel and time sequence are inconsistent. No full image-quality effect is measured.



### Proposed correction

Choose an actual destination \(s<t\) and a consistent DDIM variance, direction and endpoint convention. For example, use \(\sigma^2=\eta^2(1-A_s)(1-A_t/A_s)/(1-A_t)\) and direction variance \(1-A_s-\sigma^2\).

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 6: The target round trip selects the target model twice

Assessment: supported; impact: minor



Source: Section 4.1, Eqs.(5),(7), PDF p.6; main.py, lines 499–507



### Source claim (paraphrase)

The claimed target-to-source-to-target cycle needs source reverse dynamics followed by target reverse dynamics; the target branch passes `model_T` to both calls.



### Analysis

Even deterministic inverse maps show the consequence: with \(D_S(x)=2x\), \(D_T(x)=x/2\), the intended composition sends \(1\) to \(1\); the selected double-target composition sends it to \(1/4\). The source arguments establish the selector error independently of this illustration.



### Finding and scope

The public route is not the stated two-domain cycle. Numerically identical models could hide the difference as a special case.



### Proposed correction

Pass the source model to the first target-cycle reverse call and the target model to reconstruction. Reconcile guidance, sampling and optimization separately.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.

- The inspected public release dates to February 2026, after the conference; correspondence to the original private experimental program is not established.
