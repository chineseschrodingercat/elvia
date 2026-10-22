# Bifrost-1: Bridging Multimodal LLMs and Diffusion Models with Patch-level CLIP Latents



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The fresh-training release constructs generation modules with default initialization instead of copying the loaded pretrained branch. Later trained-checkpoint loading can overwrite those values.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: New generation modules are not initialized as parameter copies

Assessment: supported; impact: minor



Source: Figure 2 and Section 3.2, PDF p.4; Appendix A, PDF p.17; submitted constructor and train_fsdp.py



### Source claim (paraphrase)

Figure 2, Section 3.2 and Appendix A specify copies of pretrained attention, MLP and normalization parameters. The constructor instead creates new modules after loading the base model.



### Analysis

`add_vision_attention` creates new linear projections; analogous MLP/norm methods create new state, while copy operations appear only in comments. A loaded four-dimensional query projection with every weight \(2\) and bias \(1\) maps the first basis vector to \((3,3,3,3)\); a newly initialized projection does not read those values. The fresh training path has no intervening copy pass. Inference and resumed training can separately load learned generation weights, which is a critical countercontrol.



### Finding and scope

The fresh recipe does not implement the stated copy initialization. It does not show that inference uses random generation weights or that original checkpoints began incorrectly.



### Proposed correction

Create independent copies of the intended loaded modules before optimizer creation, preserving equal initial values and distinct storage. Do not overwrite an explicitly loaded trained generation checkpoint with a fresh copy.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
