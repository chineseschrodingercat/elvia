# Iterative Tool Usage Exploration for Multimodal Agents via Step-wise Preference Tuning



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Alternative preference candidates execute in one mutable environment, so rejected actions can change the observations and continuing state attached to the selected history. The finding concerns release data construction; historical training impact is unresolved.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Rejected alternatives mutate the selected continuation

Assessment: supported; impact: minor



Source: Algorithm 1, lines 6–9, PDF p.5; DPOAgent.step, lines 180–381



### Source claim (paraphrase)

Candidates should execute from the same pre-step history and continue only the selected branch.



### Analysis

Start with counter \(0\) and empty trail. Candidate A adds \(1\) and appends selected; B adds \(100\) and appends rejected; C prints the counter. The inspected sequential shared-state calls yield observations \(1,101,101\). If A is chosen, its recorded observation is \(1\), but the environment remains at \(101\) with B’s rejected trail entry. Independent branches give \(1,100,0\) and commit counter \(1\). Reordering to C,B,A makes the selected A observe \(101\), showing context contamination rather than merely a stale display. Redefining a helper in B similarly changes the shared custom-tool namespace. Adding two read-only candidates preserves the defect at the paper’s count \(5\).



### Finding and scope

The release violates common-context comparison and selected-state continuation for admissible stateful actions. Pure independent actions can avoid it. Published evaluation disables this sampling path; training-data prevalence and benchmark effect are unestablished.



### Proposed correction

Fork the entire relevant execution environment for each candidate and commit only the selected branch. Deep-copying value state repairs the counter/list witness, but does not automatically isolate tool objects, closures, files or external effects.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: The public constructor ignores an explicit candidate-count override

Assessment: not_issue; impact: minor



Source: create_agent sampling_size construction; Section 4.5 experimental candidate count



### Source claim (paraphrase)

The constructor exposes a formal candidate-count argument but reads the effective value from extra keyword arguments with a default.



### Analysis

A bound formal argument is removed from the extra-keyword dictionary, so looking it up there uses the default \(5\) even after an explicit different request. The paper itself uses \(5\), so this does not challenge its reported setting.



### Finding and scope

This is a minor API observation; no distinct scientific failure is established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
