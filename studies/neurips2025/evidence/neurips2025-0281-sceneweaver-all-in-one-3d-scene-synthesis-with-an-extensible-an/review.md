# SceneWeaver: All-in-One 3D Scene Synthesis with an Extensible and Self-Reflective Agent



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The release can encode unavailable physical measurements as zero and misindex intermediate physics histories. Final-only aggregation can remain correct; zero counted collisions has a narrower, previously explained geometric scope.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Unavailable physics is encoded as zero violations

Assessment: supported; impact: minor



Source: Sections 3.2/4.1; Pipeline/app/evaluation.py, eval_scene, lines 68–97



### Source claim (paraphrase)

Physical feedback is intended to measure collision and boundary violations, but the missing-file branch fills those fields with numeric zeros.



### Analysis

When the expected per-iteration physics file is absent, eval_scene assigns zero to OOB Objects and BBL objects and Unknown only to object count. No geometry has been examined, so neither zero is a measured empty violation set. The native present-file schema contains lists, so the fallback also changes type. The valid present-file branch preserves actual measurements; the defect is restricted to missing data.



### Finding and scope

The current release can feed unmeasured zeros into agent feedback. Whether any published scene used this fallback is unknown.



### Proposed correction

Fail explicitly on the missing record, or use null plus an unavailable status handled by every consumer. This establishes that successful measurements came from actual records, without proving recovery or retry behavior.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Historical exports reuse terminal physics for every iteration

Assessment: supported; impact: minor



Source: Pipeline/app/evaluation.py and standalone evaluation.py, statistic_traj



### Source claim (paraphrase)

Each exported iteration combines its action and perceptual score with physics loaded using the terminal index.



### Analysis

For iterations \(0,1,2\), suppose native physics records have object counts \((3,5,7)\) and collision counts \((2,1,0)\). The loop reads the terminal file each time, exporting \((7,7,7)\) and \((0,0,0)\) under distinct iteration labels. This is not a terminal-only schema because action/perception remain iteration-specific. Crucially, the terminal-only final aggregator reads the correct final entry, and direct current feedback uses its own index.



### Finding and scope

The historical trajectory is misindexed; this alone does not change a final-only physical metric or prove different generated scenes.



### Proposed correction

Use the loop index for both the existence check and physics read, retaining the terminal index only in the complete export filename.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: Zero counted collisions has a bounded geometric meaning

Assessment: not_issue; impact: minor



Source: Section 4.2 and Table 3; Pipeline/evaluation geometry predicates; author public issue replies



### Source claim (paraphrase)

The physical metric excludes selected objects and uses positive penetration/volume thresholds rather than testing every mesh component for any overlap.



### Analysis

A positive overlap depth \(0.0005\,\mathrm m\) fails a strict \(d>0.001\,\mathrm m\) predicate. A watertight intersection volume \(10^{-5}\,\mathrm m^3\) fails the \(10^{-4}\,\mathrm m^3\) threshold even if depth passes. Rugs and internal components of composite assets can be excluded; prior author replies explain that choice. The boundary predicate uses a buffered floor footprint rather than full three-dimensional enclosure.



### Finding and scope

These are legitimate metric conventions requiring a scoped interpretation, not a newly established benchmark error or a proof of dynamic stability.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
