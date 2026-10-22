# Continuous Concepts Removal in Text-to-image Diffusion Models



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The public routine fixes one calibration prompt per call, compares denoisers at different states, and cannot independently initialize original teacher and previous-stage student. Its removal loss and final genetic selection also differ from the paper. These are release-to-method discrepancies, with original experiment effects unresolved.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: One fixed prompt does not cover the calibration set within a training call

Assessment: supported; impact: minor



Source: Sections 4.1–4.3, PDF pp.4–7; train-scripts/train-ccrt.py, lines 127–133 and 192–199



### Source claim (paraphrase)

The calibration-set procedure is implemented by choosing one random entity before the training loop and repeatedly reusing it.



### Analysis

For two non-target prompts with student responses \((\theta_1,\theta_2)\) and zero teacher responses, set removal loss \(\mu|\theta_2-1|\), \(\mu=1/200\), and preservation weight \(\lambda=1/100\). Fixing the first prompt minimizes \(\mu|\theta_2-1|+\lambda\theta_1^2\) at \((0,1)\). Uniform full-set preservation instead adds \(\lambda(\theta_1^2+\theta_2^2)/2\), whose minimizer is \((0,1/2)\). Randomizing a single anchor across calls is not the same adaptive trajectory as resampling within a call.



### Finding and scope

The release provides single-anchor training, not within-call set coverage. An external anchor schedule could be intentional; Eq.(4) alone does not specify a sampling law.



### Proposed correction

If empirical-set preservation is intended, resample the calibration prompt each step or use a minibatch average. Otherwise document single-anchor training and its schedule. The usual conditional expectation of a sampled fixed-state gradient then equals the empirical-set gradient.

A proposed correction is described; author adoption is not established.



## Problem 2: Common starting noise does not give a common latent argument

Assessment: supported; impact: minor



Source: Section 4.1, Eq.(4), PDF p.4; train-scripts/train-ccrt.py, lines 214–225; ldm/models/diffusion/ddim.py, lines 239–259



### Source claim (paraphrase)

Eq.(4) compares teacher and student at one \(x_t\). The release independently samples their latent states before comparing predictions.



### Analysis

A valid zero-noise DDIM step with cumulative coefficients \(\alpha=1/5\), \(\alpha_{\rm next}=4/5\) has form \(z_{\rm next}=2z-b\epsilon(z)\), \(b=3/\sqrt5\). Start both at \(z=1\), use teacher \(\epsilon_*(z)=z\), and student \(\epsilon_\theta(z)=kz\), \(k=2/b-1\). Their states become \(z_*=2-b\) and \(z_\theta=b\). The cross-state residual is \(kb-(2-b)=0\), but the common-teacher-state squared residual is \((k-1)^2(2-b)^2\approx0.112422373>0\).



### Finding and scope

The implemented zero discrepancy need not mean zero common-input discrepancy. A trajectory-level objective may still be useful but is a different objective.



### Proposed correction

Choose and disclose one latent-sampling rule, then evaluate both denoisers on exactly the same latent, time and prompt. Freeze the teacher and treat sampling consistently with the intended gradients.

A proposed correction is described; author adoption is not established.



## Problem 3: One checkpoint path cannot specify both later-stage initializations

Assessment: supported; impact: minor



Source: Section 4.1, PDF pp.4–5; Section 4.3, p.7; train-scripts/train-ccrt.py, get_models, lines 99–106



### Source claim (paraphrase)

A later stage requires original teacher \(\theta_0\) and student initialized at \(\theta_{i-1}\). Both public loader calls instead receive the same checkpoint path.



### Analysis

For \(\theta_{i-1}\ne\theta_0\), no single supplied path realizes the required ordered pair. Loading the previous model moves the teacher; loading the original restarts the student. The objectives differ concretely: retained responses \(f_i=i\delta\), \(\delta=0.1\), have previous-stage discrepancy \(0.01\), but original-reference discrepancy \(0.25\) at stage \(5\). This is an exact reference distinction, not a claimed observed model trajectory.



### Finding and scope

The release cannot independently express the described continuous original-teacher procedure. An unpublished wrapper or different generating revision could resolve historical correspondence.



### Proposed correction

Expose separate original-teacher and student-initialization checkpoint arguments and retain their identities in each stage record. They may coincide at the first stage.

A proposed correction is described; author adoption is not established.



## Problem 4: The released squared removal loss differs from the stated absolute norm

Assessment: supported; impact: minor



Source: Section 4.1, Eq.(3), PDF p.4; train-scripts/train-ccrt.py, lines 185 and 225–229



### Source claim (paraphrase)

The paper explicitly uses the residual \(\ell_1\) norm; the public routine instantiates MSELoss for both removal and alignment.



### Analysis

For a scalar removal target \(1\), retained target zero and \(\lambda=1/100\), the paper-form objective is \(J_1(x)=|x-1|+x^2/100\), uniquely minimized at \(1\). The squared version \(J_2(x)=(x-1)^2+x^2/100\) is minimized at \(100/101\). At that point \(J_1=201/10201>1/100=J_1(1)\). Scalar dimension removes any mean-versus-sum explanation.



### Finding and scope

The two losses can optimize different solutions. Which loss produced each original experiment is unresolved.



### Proposed correction

Use the stated absolute norm with an explicit reduction convention, or document the squared objective and identify its generating runs. Changing the norm also changes relative weighting in higher dimensions.

A proposed correction is described; author adoption is not established.



## Problem 5: The returned genetic population need not be a scored elitist union

Assessment: supported; impact: minor



Source: Section 4.2, Algorithm 1, PDF p.6, lines 11–13; eval-scripts/generate-entity.py, lines 233–299



### Source claim (paraphrase)

The paper selects the best members of the parent/offspring union. The release scores and truncates before variation, then may terminate after unscored replacements.



### Analysis

Let \(k=2\) and fitnesses \(F(a)=3\), \(F(b)=2\), \(F(c)=1\), \(F(d)=0\). In an allowed no-crossover realization, initial scoring retains \((a,b)\); mutation removes \(a\) and creates \(d\). Population size is still \(2\), so the loop exits and returns \((b,d)\) without evaluating \(d\). Elitist union selection from unchanged parents and that offspring instead returns \((a,b)\). This traces an allowed control-flow realization, not its frequency in default runs.



### Finding and scope

The public finalization does not enforce the declared selection property. It does not establish global genetic-search failure or quantify generated-prompt quality.



### Proposed correction

Keep unchanged parent records, score every new genotype, and apply \(\operatorname{Top}_k(E_j\cup O_j;F)\) after variation on every return path. Its finite union-selection property follows directly from ordering the compared scores.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.

- The release is not established as the exact code that generated every original diffusion checkpoint or reported table.
