# Recognition through Reasoning: Reinforcing Image Geo-localization with Large Vision-Language Models



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Current release rewards differ in denominator, geographic matching, probability extraction and component weights. Overall/scene table reconciliation remains conditional on run and denominator identity; published model improvements were not reproduced.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: The released visual reward computes tag recall rather than predicted-entity precision

Assessment: supported; impact: minor



Source: Equation (2); examples/train/grpo/globe/plugin.py, GeoVisalEntityMatching2ORM



### Source claim (paraphrase)

The paper averages matching scores over entities extracted from predicted reasoning; the release divides by grounded image-tag count.



### Analysis

Let grounded tags be road and tree. An explanation containing those alone gets reward \(1\) under both rules. Add three unmatched entities dragon, spaceship and ocean. The paper’s predicted-entity mean becomes \(2/5=.4\), while the source still finds both grounded tags and returns \(2/2=1\). This difference does not rely on substring behavior; partial lexical matching is expressly allowed. Recall can legitimately encourage coverage but does not penalize additional ungrounded entities as the precision-like formula does.



### Finding and scope

The release changes the stated visual-hallucination training signal. Actual hallucination frequency and published model effects remain unmeasured.



### Proposed correction

Specify the predicted-entity extractor and matching rule, then average over those extracted entities with an explicit empty-set convention; alternatively identify the release as tag recall and qualify its interpretation.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Country substrings can reward a wrong geographic answer

Assessment: supported; impact: minor



Source: Equation (3); plugin.py, GeoLocAccuracyV2ORM; eval.py matcher



### Source claim (paraphrase)

The geographic reward must be zero for a wrong country, but the approximate matcher accepts sufficiently long substrings.



### Analysis

For true Niger/Niamey and predicted Nigeria/Kaduna, niger is contained in nigeria and length ratio \(5/7\ge.7\); the country gate passes and the city gate fails, returning \(.2\) instead of \(0\). Exact aliases are useful, but Niger and Nigeria are different countries. This source predicate need not be the geocoding/distance pipeline behind published threshold metrics.



### Finding and scope

The current reward and string evaluator can conflate distinct countries. No distance-threshold accuracy change is established.



### Proposed correction

Compare canonical geographic identifiers after a versioned alias map, retaining genuine aliases while separating distinct countries.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: Truncated first-token probabilities do not identify localizability probability

Assessment: supported; impact: minor



Source: Equation (1); plugin.py, GeoLocatablityORM



### Source claim (paraphrase)

The release renormalizes hard-coded yes/no spellings found only among the top \(5\) first-token log probabilities.



### Analysis

A valid distribution on yes, maybe, perhaps, unknown, uncertain, other, no with probabilities \[(.30,.15,.14,.13,.12,.10,.06)\] includes yes but omits no from the top five. The source returns essentially \(1\); unconditional positive mass is \(.30\), while even the complete binary-renormalized value is \(.30/(.30+.06)=5/6\). Missing mass cannot be treated as zero. If both full class masses and all accepted spellings are included, binary renormalization is a valid special case.



### Finding and scope

The probability extraction is not generally the stated positive-class probability. Server-specific incidence and reward calibration remain unresolved; no API request was made.



### Proposed correction

Define the target probability and score complete fixed-label sequences, then use stable normalization of their full log likelihoods. Explicitly handle alternative tokenization and avoid top-k omissions as true zeros.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 4: Released reward weights reverse preferences relative to the paper

Assessment: supported; impact: minor



Source: Equation (4); Appendix Table 11; train_all_rewards.sh



### Source claim (paraphrase)

The paper uses localizability/visual/geographic weights \((.2,.5,1)\); the launcher assigns \((.5,.2,1)\) by name and adds format reward.



### Analysis

With equal format/geographic contributions, response reward triples \(A=(.9,0,0)\) and \(B=(.1,1,0)\) have paper totals \(.18,.52\), but released totals \(.45,.25\). Ordering reverses; subtracting group means and dividing by positive standard deviation preserves that reversal, so GRPO normalization cannot absorb the mismatch as a common scale. A later release configuration could differ from the historical experiment, but those configurations are not equivalent.



### Finding and scope

The launcher implements a different objective; the exact checkpoint-generating configuration remains unidentified.



### Proposed correction

Use an explicit named weight map matching the intended objective and disclose any fourth format term; reconcile actual training provenance before evaluating changes.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 5: Overall and scene-specific tables need run/denominator reconciliation

Assessment: needs_evidence; impact: needs_evidence



Source: Tables 1, 2 and 7; public author reply in repository issue 3



### Source claim (paraphrase)

The declared test set partitions \(12000\) images into \(2096\) indoor, \(1092\) nature and \(8812\) urban examples; matching scene and overall metrics should share a weighted counting identity.



### Analysis

At \(200\,\mathrm{km}\), GLOBE’s scene percentages \(64.71,81.40,74.76\) yield weighted overall \(73.60884\%\), while Table 2 gives \(73.83\%\). The \(.22116\)-point difference exceeds the conservative \(.010\)-point two-decimal rounding allowance. Different runs, separately selected best results, valid-geocode subsets or denominators can break the common-evaluation premise. The author’s prior issue reply discusses best-run selection and geocoding service changes for an external reproduction, but does not map these particular cells to runs. A common average across the same runs and fixed denominators would still obey linearity.



### Finding and scope

The tables are incompatible under one common evaluation, but different run/subset provenance could reconcile them. No replacement overall score or fabricated-data allegation is supported.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
