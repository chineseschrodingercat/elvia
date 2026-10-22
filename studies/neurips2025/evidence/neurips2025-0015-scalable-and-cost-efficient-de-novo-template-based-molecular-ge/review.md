# Scalable and Cost-Efficient de Novo Template-Based Molecular Generation



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Independent minima of route cost and reaction count can form an impossible route certificate, a core structural error. Other released bookkeeping, soft-guidance, diagnostics and reporting issues are Minor where effects on central experimental results are unknown. The concrete monotone cost recurrence and disclosed matched forward-trajectory budgets remain valid.



## Scope

Full original concerns, current proceedings methods and implicated experiment/appendix passages, and current pinned dynamic-library, environment, guidance, metric and configuration source read. Counterexamples are direct dataflow/algebra checks; no author or prior verifier program was executed.



## Problem 1: Dynamic minima combine incompatible routes

Assessment: supported; impact: major



Source: Current paper, Section 3.4, p. 6, Appendix B.1, p. 17; author rgfn/gfns/reaction_gfn/dynamic_library/reaction_dynamic_library.py, lines 112–118 and 173–208.



### Source claim (paraphrase)

Independent stored minima determine a realizable dynamic fragment route.



### Analysis

The current on_end_sampling independently minimizes reaction count and cost for each SMILES; retrieve_all_additional_fragments exports the minimum count together with the independently selected cost. Consider two discovered certificates for one intermediate: \((k,c)=(1,100)\) and \((2,10)\), both within the four-reaction budget. These nonnegative costs can arise in the abstract positive-yield model with unit yields. The stored pair becomes \((1,10)\), which neither discovered route realizes. ReactionEnv uses the exported count for tree budgets and PathCostProxy uses the exported cost, so a continuation can inherit a cheap cost requiring a longer subtree while passing with the shorter count. This is an exact invariant failure of the released dynamic-library representation; it is not a claim that a particular real molecule or a known proportion of paper samples has such routes.



### Finding and scope

The dynamic-library representation can destroy the coupling needed for the core cost/feasibility claim. This does not quantify how often published samples use such conflicting routes.



### Proposed correction

Store one consistent route with its count/cost, or maintain nondominated route certificates and expand them consistently.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: Backward budgets omit fragment-subtree reactions

Assessment: supported; impact: minor



Source: Author reaction_env.py, lines 307–333; policies/cost_biased_backward_policy.py, lines 90–117, and policies/decomposability_guided_backward_policy.py, lines 79–105, under rgfn/gfns/reaction_gfn/.



### Source claim (paraphrase)

Backward cost models receive the remaining reaction budget.



### Analysis

The current environment subtracts the reaction itself and all side-fragment subtree reaction counts. Both current predictor-query branches instead pass state.num_reactions minus one. For product count \(3\) with one side fragment requiring \(1\) reaction, the environment’s precursor count is \(3-1-1=1\), whereas the model query receives \(2\). The discrepancy disappears for original fragments with zero subtree counts. It is a local state-budget mismatch; its effect on published scores is unmeasured.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: Cache keys and Boolean writes lose known information

Assessment: supported; impact: minor



Source: Author rgfn/gfns/reaction_gfn/policies/guidance_models/cost_models.py, lines 55–80; decomposable_models.py, lines 55–80; proxies/path_cost_proxy.py cache definition.



### Source claim (paraphrase)

Cache lookup and override paths use known reachability/cost information consistently.



### Analysis

The current cost branch now converts Molecule objects to SMILES before querying its string-keyed cache; the old cost-key mismatch is fixed and is not alleged as current. The decomposability branch still tests the unnormalized incoming object keys against a string-keyed dictionary. Even with a string-key cache hit, its chained Boolean assignment modifies an advanced-indexed temporary, rather than the original prediction. Thus a known reachable entry predicted as \(0.1\) remains \(0.1\), instead of being forced to \(1\). Its non-default override branch writes the cached cost itself into the probability: cost \(7\) would produce output \(7\), outside \([0,1]\). These current source defects are separate from historical experiment provenance.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

The current cost cache normalizes Molecule keys; the separate decomposability key/index/override paths remain unresolved. No author adoption of this review is inferred.



## Problem 4: Zero penalty does not bound memory

Assessment: supported; impact: minor



Source: Paper pp. 6, 17; rgfn/shared/policies/exploitation_penalty_helper.py



### Source claim (paraphrase)

Decay of the exploitation penalty bounds the count-table memory.



### Analysis

The penalty can decay to zero while molecule counts continue to be inserted/updated. Vanishing numerical contribution does not stop dictionary growth.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 5: Finite-temperature guidance does not hard-discard parents

Assessment: supported; impact: minor



Source: Current paper, Eqs. (9)–(11), p. 5, and Appendix J.1, p. 26; author policies/decomposability_guided_backward_policy.py, lines 100–115, and objectives/rgfn_trajectory_filter.py under rgfn/gfns/reaction_gfn/.



### Source claim (paraphrase)

Finite-temperature guidance strictly discards unreachable parents.



### Analysis

For finite scores and finite temperature, softmax assigns every candidate strictly positive probability. A lower feasibility score can discourage an invalid parent but cannot hard-discard it; an explicit support mask/filter is required for that stronger claim.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 6: The general Bellman recurrence needs monotonicity

Assessment: supported; impact: minor



Source: Paper pp. 4



### Source claim (paraphrase)

The general path-cost recursion can be evaluated using minimum prefixes.



### Analysis

The current general framework allows transition cost to depend on accumulated prefix cost, then moves the minimum inside that transition. If two prefixes reaching the same state cost \(1\) and \(2\), and the continuation is \(C(x)=(x-2)^2\), the true completed minimum is \(0\), whereas applying the continuation only to the cheapest prefix gives \(1\). All costs are nonnegative. Nondecreasing dependence on prefix cost and a sufficient state restore the finite minimum interchange. The concrete synthesis recurrence \(C^S(x)=(x+c)/y\), with \(y>0\), is strictly increasing and therefore is not refuted by this general-framework counterexample.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 7: Tree probability does not identify chemical-space cardinality

Assessment: supported; impact: minor



Source: Paper pp. 6



### Source claim (paraphrase)

The sampled-tree fraction identifies the increase in distinct chemical-space size.



### Analysis

A sampled nondecomposable fraction \(43\%\) corresponds to a sampled probability ratio \(43/57\simeq75.44\%\). Distinct molecules can have unequal numbers and probabilities of synthesis trees, so that ratio does not imply \(75\%\) more distinct molecules in chemical space.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 8: Universal gains and repeated values need reconciliation

Assessment: supported; impact: minor



Source: Paper pp. 6–8, 27, 26



### Source claim (paraphrase)

Every component uniformly improves metrics and repeated table values agree.



### Analysis

Some ablations improve individual displayed metrics. Identically described LARGE-C and RxnFlow-SMALL results differ across tables. Raw run provenance is needed to choose the historical values.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 9: Conditioning and policy scales are incompletely specified

Assessment: supported; impact: minor



Source: Current paper, pp. 4–5 and Appendices A.3, B.1 and E, pp. 16–19; author configs/envs/settings/medium.gin and large.gin, policies/cost_biased_backward_policy.py, and policies/guidance_models/cost_models.py.



### Source claim (paraphrase)

The printed model inputs and policy scale fully describe the implementation.



### Analysis

Official MEDIUM/LARGE use fixed \(75\%\) yield; cost networks also receive reaction counts; policy scores divide by cost standard deviation beyond the printed temperature. These affect the actual model and scoring rule.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 10: Diagnostic and unused-branch defects are local

Assessment: supported; impact: minor



Source: Author guidance_models/decomposable_models.py, lines 151–188 and 205–215; guidance_models/cost_models.py, cost-correlation metric; current paper Appendix A.3.2.



### Source claim (paraphrase)

The auxiliary accuracy/correlation measures have the stated definitions.



### Analysis

The current decomposability predictor applies sigmoid and then computes accuracy using a zero threshold. Since \(\operatorname{sigmoid}(z)>0\) for every finite logit, all such predictions count as positive. Probabilities \((0.1,0.8,0.3,0.9)\) with labels \((0,1,0,1)\) give \(50\%\) under that rule, versus \(100\%\) at threshold \(1/2\). The cost diagnostic still computes Pearson correlation with np.corrcoef while naming it Spearman. The older inverse-cost class with a misspelled attribute is absent from the current guidance_models module and is historical only. Negative examples are capped by the number collected, so the stated negative fraction is a target when supply is insufficient. None of these observations independently establishes that the final mode/scaffold counts are wrong.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

The old inverse-cost branch is absent in the current release. Current diagnostic threshold/correlation defects remain; no integrated correction was executed.



## Problem 11: Mode limits and run manifests remain unresolved

Assessment: needs_evidence; impact: needs_evidence



Source: configs/rgfn_seh_proxy.gin; trainer/metrics/reaction_metrics.py, lines 451-452; official PDF: main mode-count table, Appendix B, Appendix J.2.3/Figure 15, p. 28, and compute-resource checklist, p. 33.



### Source claim (paraphrase)

Public mode limits and run configuration explain the reported counts.



### Analysis

The current sEH configuration still caps modes at \(5000\), and its greedy metric stops at that cap, whereas the paper reports values such as \(37714\). An unrecorded override or offline evaluator could reconcile this; a fabricated-result conclusion does not follow. The greedy, reward-ordered mode set also need not be maximum-cardinality, and its exact similarity boundary needs consistent specification. The paper discloses matched forward-trajectory totals and incomplete resource tracking. Its cost-change experiment continues training without resetting parameters; that does not establish that all networks except the cost predictor were frozen. Per-run configurations, uncertainty units and the exact frozen-parameter policy remain necessary for stronger reconstruction/attribution claims.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



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
