# VAGEN: Reinforcing World Model Reasoning for Multi-Turn VLM Agents



Preliminary assessment: No Issue Found

Independent scientific review: pending. Author adoption: not requested.



The three supplied concerns concern the legacy VAGEN implementation. In the current author default branch, Navigation uses separate scene collections, Sokoban no longer builds both sets from the same valid-seed prefix, and FrozenLake passes the reset seed into map construction. Historical benchmark remediation is not independently reproduced.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: Current Navigation separates the task collections used by the legacy split

Assessment: not_issue; impact: no_issue_found



Source: Current author commit e34bbcee3c48f03833270550151eb6646267fa3b; examples/train/navigation/train_navigation_base_common.yaml and val_navigation_base_common.yaml; vagen/envs/navigation/navigation_env.py, lines 99–105 and 154–170



### Source claim (paraphrase)

The legacy example reused one \(60\)-task collection under the seed-to-index rule \(s\bmod60\); separate seed labels could therefore identify the same task. This was previously discussed in author issues 62 and 67.



### Analysis

The current default branch instead selects base_train/common_sense_train for training and base/common_sense for evaluation. Reading all corresponding JSON task records gives \(1200\) training and \(60\) evaluation tasks per category, with zero identical task records and zero overlapping scene identifiers within either category or across the combined categories. Modulo selection now acts on the separately chosen collections, so it does not establish the old cross-split identity.



### Finding and scope

The legacy overlap mechanism is fixed in these current configurations. No trained-model evaluation or correction of the old reported scores is claimed.



## Problem 2: Current Sokoban configuration no longer uses the same valid-seed prefix

Assessment: not_issue; impact: no_issue_found



Source: Current author commit e34bbcee3c48f03833270550151eb6646267fa3b; examples/train/sokoban/train_sokoban_wm_think.yaml and val_sokoban_wm_think.yaml; vagen/envs/sokoban/patch_sokoban_env.py, lines 12–51 and 119–169



### Source claim (paraphrase)

The legacy generator returned \(V[:10000]\) and \(V[:128]\) from one ordered valid list, proving test-prefix inclusion. Author issue 106 had already identified this historical defect.



### Analysis

The current inspected configurations use training seeds \([1,10000]\) and evaluation seeds \([10001,10256]\), with direct seeded reset rather than the old duplicated-prefix utility. The current reset also has an explicit optional canonical-room hash partition and a deterministic retry rule. Consequently the former common-prefix proof no longer applies. The inspected example leaves the optional room partition at its default; disjoint seed ranges alone do not prove that every generated board is distinct.



### Finding and scope

The supplied prefix defect is absent from the current path. Exhaustive board uniqueness or symmetry separation is not certified, and no new board-overlap result is inferred without generation evidence.



## Problem 3: Current FrozenLake constructs the map from the reset seed

Assessment: not_issue; impact: no_issue_found



Source: Current author commit e34bbcee3c48f03833270550151eb6646267fa3b; vagen/envs/frozenlake/frozenlake_env.py, lines 91–124



### Source claim (paraphrase)

The legacy constructor generated a map from an unspecified seed before reset, so recording reset seed \(s\) did not determine the map \(G(U)\).



### Analysis

Current reset calls _create_gym_env with the reset seed, whose map-generation call explicitly forwards that seed, then constructs and resets the Gym environment with that description. The relevant order is now \(G(s)\) followed by environment reset. An explicit configured description remains an intentional fixed-map special case. This static source trace removes the former late-seeding mechanism without executing a simulator.



### Finding and scope

The old reset-seed propagation defect is fixed in current source. Cross-worker reproducibility, full service behavior and original experimental maps were not replayed.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.

- The latest implementation fixes do not independently establish re-evaluated historical benchmark scores.

- Current Sokoban seed ranges were inspected statically; no exhaustive canonical-board generation or uniqueness check was run.
