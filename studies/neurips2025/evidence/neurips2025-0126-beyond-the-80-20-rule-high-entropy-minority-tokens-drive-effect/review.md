# Beyond the 80/20 Rule: High-Entropy Minority Tokens Drive Effective Reinforcement Learning for LLM Reasoning



Preliminary assessment: No Issue Found

Independent scientific review: pending. Author adoption: not requested.



Both reported concerns are historical release defects already fixed in the current author code: actor-level configuration delivery and Boolean eligibility filtering. No current issue is established by these witnesses.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The historical recipe placed entropy_top_ratio outside the actor configuration

Assessment: not_issue; impact: no_issue_found



Source: Eq. (2); current actor recipe, actor configuration declaration and dp_actor.py lines 440–461.



### Source claim (paraphrase)

Eq. (2) selects response tokens using ratio \(\rho=0.2\). The historical recipe supplies that setting through actor_rollout_ref.model.entropy_top_ratio, but verl/workers/fsdp_workers.py, lines 785–789, constructs the actor from the separate actor configuration branch. In verl/workers/actor/dp_actor.py, line 440, the actor looks up entropy_top_ratio in its own configuration and bypasses the helper when the setting is absent.



### Analysis

The historical recipe places entropy_top_ratio equal to \(0.2\) in the model branch, but the worker constructs its actor from the actor branch and the actor looks up the key there. That lookup yields None and bypasses high-entropy selection in favor of the full-response mask. The authors' subsequent fix moves both the setting and its structured declaration into the actor configuration.

At the current head, the recipe explicitly sets actor_rollout_ref.actor.entropy_top_ratio to \(0.2\), the actor dataclass/YAML declares the field, and the worker passes the actor branch. The historical missing-key lookup no longer applies.



### Finding and scope

The known configuration-delivery concern is already corrected in the current release. The author statement that published runs were unaffected is recorded as attribution, without independent recovery of their experiment provenance.



## Problem 2: An integer response mask was interpreted as index positions

Assessment: not_issue; impact: no_issue_found



Source: Current verl/trainer/ppo/core_algos.py, get_global_entropy_top_mask, lines 53–87.



### Source claim (paraphrase)

Historical verl/trainer/ppo/core_algos.py, get_global_entropy_top_mask, lines 53–87, flattens the response mask and uses it directly to index the flattened entropy tensor. The declared mask marks eligible response tokens, but an integer-valued mask has integer-index rather than Boolean-mask semantics. The author correction explicitly converts it to Boolean first.



### Analysis

For entropy values \((0.9,0.1)\) and an integer mask \((1,0)\), integer indexing gathers positions one and zero, yielding \((0.1,0.9)\), rather than the eligible singleton \((0.9)\). Subsequent selection can therefore map to the wrong token. The existing Boolean conversion changes the operation to eligibility filtering, as required.

Current line 68 explicitly converts the flattened mask to Boolean. For the same witness it filters the eligible singleton \((0.9)\) and maps its selected index back to the first position, yielding \((1,0)\). No integer-index ambiguity remains.



### Finding and scope

The current Boolean conversion removes the historical indexing witness. This does not certify arbitrary rounding boundaries, distributed execution or complete training.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
