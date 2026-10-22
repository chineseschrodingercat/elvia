# Know Thyself by Knowing Others: Learning Neuron Identity from Population Context



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current revision retains a counterexample to universal zero-shot superiority, released split/count discrepancies and minor repeated-result/documentation inconsistencies. The old global SEM-checklist contradiction is absent. Core contrastive and permutation arguments remain valid; fully untouched-animal development and biological attribution remain bounded evidence questions. The strict assessment is Minor.



## Scope

Full original concerns, fresh current arXiv methods/results/appendices and eleven current pinned author files read. Recounted the released IBL identifiers and inspected split, loss and evaluation contracts without author-code execution.



## Problem 1: Universal zero-shot superiority is false

Assessment: supported; impact: minor



Source: Paper pp. 7, 1–2



### Source claim (paraphrase)

NuCLR exceeds every baseline in all zero-shot tasks.



### Analysis

Current Table 1 reports inductive zero-shot Bugeon E/I macro F1 \(0.6738\pm0.0563\) for NuCLR and \(0.7463\pm0.0095\) for LOLCAT. The mean difference is \(-0.0725\), or \(-7.25\) percentage points. The same page still says NuCLR consistently outperforms all baselines in zero-shot settings. LOLCAT uses a different training paradigm, but is explicitly included in that comparison. This refutes the universal wording while preserving the other reported wins; these aggregates alone do not support a new significance calculation.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: Development does not fully hold out the target animal

Assessment: needs_evidence; impact: needs_evidence



Source: Current paper, hyperparameter search Section B.4, p. 19, and Bugeon Section D.4, pp. 21–22; author configs/data/val_dataset/bugeon_val_dev.yaml and configs/data/bugeon_inductive.yaml.



### Source claim (paraphrase)

Development and testing completely separate the target animal.



### Analysis

The current development configuration includes SB028 recording sb028_20191106, while inductive testing includes sb028_20191107, sb028_20191108, sb028_20191112 and sb028_20191113. Final pretraining explicitly excludes all five. Thus recording sets are disjoint but model-development and test animals are not completely disjoint. Section B.4 says calcium-imaging hyperparameters were tuned on the Bugeon development set, and D.4 discloses one development recording from every subject. This limits a fully untouched-animal interpretation; it does not contradict the narrower final-pretraining exclusion or establish test-label supervised fitting or a quantified F1 bias.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: IBL counts and split ratios differ

Assessment: supported; impact: minor



Source: Current paper, Section D.2, p. 21; author IBL training/development/test YAMLs and preprocess/ibl_bwm/create_transductive_splits.py, lines 59–70.



### Source claim (paraphrase)

Public configurations reproduce the reported IBL counts and split ratios.



### Analysis

The current text reports total/train-development/development/test recording counts \((439,346,91,93)\). Removing probe suffixes from the current released YAML identifiers gives \((455,362,90,93)\). The development records are included in pretraining, while pretraining and final-test record IDs remain disjoint. A larger metadata universe is not itself an error; the inclusion/version mapping is missing. The split script reserves \(20\%\) for testing and then \(1/8\) of the remainder for validation, giving \(70/10/20\%\) train/validation/test, whereas reserving \(20\%\) of the training fold as described gives \(64/16/20\%\), apart from integer rounding. Historical production settings are not established by current code alone.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: Current uncertainty labels distinguish seed SD from figure SEM

Assessment: not_issue; impact: no_issue_found



Source: Current paper, Table 1, p. 7; Table 2, p. 8; Figure 3, p. 15; current arXiv revision omits the older conference checklist.



### Source claim (paraphrase)

The current tables and figure identify their uncertainty summaries.



### Analysis

The current tables explicitly use standard deviations across training seeds, while Figure 3 explicitly uses standard error across three seeds. Different summaries in distinct identified displays are compatible. The older conference checklist claimed SEM throughout, but that checklist is absent from this current arXiv revision. For \(n\) independent seeds, \(\mathrm{SEM}=\mathrm{SD}/\sqrt n\); neither quantity estimates animal-sampling uncertainty. The single held-out Bugeon animal and three held-out Steinmetz animals still bound the scope of population-level generalization.



### Finding and scope

The older contradictory checklist statement is not a current-source error. Seed variability and animal-level uncertainty remain different quantities; no numerical error is inferred from using clearly labeled summaries.



## Problem 5: Population context does not isolate neuron-specific identity

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 5, 7, 20–21



### Source claim (paraphrase)

Context gains establish the proposed neuron-specific identity interpretation.



### Analysis

Recording, genotype and other population variables can predict labels. Improved prediction from context does not establish that the gain primarily reflects neuron-specific identity without discriminating controls.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 6: Baseline adaptation limits attribution

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 22–23, 16–17; eval_scripts/single_split_eval.py; multi_split_eval.py



### Source claim (paraphrase)

The comparisons isolate superiority of the method itself.



### Analysis

Disclosed differences in adaptation and tuning budgets mean that system comparisons do not isolate intrinsic method superiority under fully matched information and compute.



### Finding and scope

The disclosed system comparisons do not isolate every architectural cause. No deliberately weakened baseline or invalid final standardization is established.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 7: Minor repeated results and documentation differ

Assessment: supported; impact: minor



Source: Current paper, Table 1, p. 7, Table 5 and Section A.5, p. 17; author src/distributed.py attribution. Older asset checklist is absent from the current revision.



### Source claim (paraphrase)

Repeated result entries and asset descriptions are mutually consistent.



### Analysis

NeuPRINT Allen transductive zero-shot macro F1 remains \(0.4020\pm0.0238\) in current Table 1 and \(0.3999\pm0.0312\) in Table 5, both described as five-seed summaries without identifying different seed sets. The difference is small and does not overturn the large NuCLR lead, but requires run identification. Section A.5 retains an incomplete sentence about temporal versus spatial attention complexity. The old asset-checklist contradiction no longer appears because this arXiv revision omits the checklist; the author source still openly attributes its distributed helper to I-JEPA. No license violation is established.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- No new author-code execution, training, empirical replication or contact.

- Historical verification outputs were inspected but not rerun.

- Missing run provenance and unresolved empirical interpretations remain explicit.
