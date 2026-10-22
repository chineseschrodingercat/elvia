# Two Experts Are All You Need for Steering Thinking: Reinforcing Reasoning in MoE Models Without Additional Training



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



A released evaluation script pools distinct nonempty steering configurations in one output path. Scientific nPMI and disclosed renormalization checks do not establish a paper error.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Distinct steering configurations append to an indistinguishable output file

Assessment: supported; impact: minor



Source: Official RICE intervention.py, run, lines 35–43, 50–54 and 106–114



### Source claim (paraphrase)

For nonempty selected-expert settings, the evaluation function overwrites its configuration-specific filename component with normal, although it still passes the actual steering multiplier and expert set to the model.



### Analysis

Fix dataset, sampling arguments and output directory, and choose expert string 29:126;39:182 with \(\beta=4\) and then \(\beta=64\). Both valid settings enter the same nonempty branch, assign the identical filename component normal, and open that path in append mode. Each record stores only data identifier, problem and response, so the two interventions cannot be distinguished from those records. Separate output directories or external manifests can avoid the pooling; a single isolated invocation does not mix settings.



### Finding and scope

The official release loses intervention provenance when those settings share an output directory. The source trace establishes the collision without model execution; it does not establish that any published accuracy was computed from mixed outputs.



### Proposed correction

Keep the steering/expert component for nonempty configurations and use normal only for the baseline; store intervention metadata with each output. The proposed filename change addresses this collision but not complete run identity.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
