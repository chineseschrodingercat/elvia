# Distil-E2D: Distilling Image-to-Depth Priors for Event-Based Monocular Depth Estimation



Preliminary assessment: No Issue Found

Independent scientific review: pending. Author adoption: not requested.



No substantive error was established in the inspected temporal interpolation, alignment confidence and bounded confidence reparameterization. Implementation and benchmark reproduction remain unavailable.



## Scope

Fresh reading of the cited original-PDF formulas and direct algebra. Temporal weights \(\max(0,1-|b-\tau|)\) sum to \(1\) for \(\tau\in[0,B-1]\). For positive depths, \(\exp(-|\log p-\log g|)=\min(p/g,g/p)\in(0,1]\). The confidence reparameterization \(0.1+0.9w\in[0.1,1]\) follows from the supplementâ€™s sigmoid condition. No author program or model was executed.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.

- The named author repository did not resolve in the inspected access records and live head cache; code validity masks, data preprocessing and empirical results remain unverified.
