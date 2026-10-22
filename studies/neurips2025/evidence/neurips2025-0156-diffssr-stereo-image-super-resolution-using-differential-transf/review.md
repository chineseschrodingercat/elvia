# DIFFSSR: Stereo Image Super-resolution Using Differential Transformer



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The official release has an augmentation API mismatch, a latent duplicate-left export path and conflicting training settings. These are bounded release/provenance findings; the separate validation path correctly splits stereo views.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Vertical-flip flag binds to the flow argument

Assessment: supported; impact: minor



Source: Section 4.1, PDF p.6; stereosr_image_dataset.py, lines 65–70; BasicSR 1.3.5 transforms.py, augment



### Source claim (paraphrase)

The caller expects four augmented images and passes its vertical-flip Boolean as the fourth positional argument.



### Analysis

The pinned signature is augment(imgs, hflip, rotation, flows, return_status). The flags bind flows to True. With rotation disabled and a sampled false horizontal flip, the dependency returns the pair consisting of the four-image list and that flow value. The caller unpacks two outer values into four variables and must fail. Valid scale-four image pairs of spatial sizes \(256\times256\) and \(64\times64\) do not alter this contract. Other random branches may fail earlier while manipulating the Boolean as flow.



### Finding and scope

The released caller/dependency combination has a sufficient loader failure. It does not establish that no privately patched training environment existed.



### Proposed correction

Use a shared explicit horizontal/vertical image transformation returning four images. Moving the vertical flag into the dependency’s rotation argument would also enable transpose behavior and is not equivalent.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: Standalone export selects the left channels twice

Assessment: supported; impact: minor



Source: inference_swinfirssr.py, lines 62–77; SwinFIRSSRModel validation, lines 45–46



### Source claim (paraphrase)

Both standalone output branches spatially crop the same six-channel tensor and select the same first three channels.



### Analysis

For stereo RGB levels \((0.1,0.2,0.3)\) and \((0.7,0.8,0.9)\), both branches export BGR \((0.3,0.2,0.1)\), whereas the right branch should export \((0.9,0.8,0.7)\). The indexing discards channels \(3\)–\(5\). The script also references a local image variable before assignment, so this is a latent defect after that earlier blocker. The separate model-validation path correctly splits at channel \(3\).



### Finding and scope

This export path loses the right view when views differ. The correct validation path prevents inferring that published stereo averages necessarily used duplicate left images.



### Proposed correction

Split the six-channel output into channels \(0\)–\(2\) and \(3\)–\(5\) before spatial cropping and color conversion.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: The release does not identify the narrated training protocol

Assessment: supported; impact: minor



Source: Sections 4.1 and 4.3.1, PDF pp.6,9; training YAML lines 78–83; diffssr_arch.py, line 256



### Source claim (paraphrase)

The paper describes \(500{,}000\) iterations with cosine decay and selects window \(3\); the release uses \(800{,}000\) iterations, MultiStepLR and window \(5\).



### Analysis

The first released milestone is \(600{,}000\), so it has not fired by the paper’s endpoint \(500{,}000\), where the stated cosine decay would be complete. The main stereo scores agree with the window-\(5\) ablation row, which supports an alternative run interpretation but does not identify every checkpoint. The paper also studies test-time window changes. Per-GPU batch size and global batch size are not silently equated.



### Finding and scope

The artifact mismatch is established, but the exact historical experiment recipe remains unresolved.



### Proposed correction

Associate each checkpoint/table row with its actual configuration, dependencies, seed, duration and training/test window. Do not replace these with a guessed recipe.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
