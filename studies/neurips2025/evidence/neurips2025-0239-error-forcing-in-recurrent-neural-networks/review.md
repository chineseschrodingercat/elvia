# Error Forcing in Recurrent Neural Networks



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current release has a stricter-than-described XOR stopping threshold, a sine-task output-dimension mismatch and a bias inconsistency in teacher forcing. Mathematical checks also restrict the Bayesian objective bridge, the uncertainty-aware appendix and the parameter-to-activity direction argument. The basic error-feedback projection and reported empirical advantages are not refuted.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: A state Kalman gain is not the fresh process-noise posterior

Assessment: supported; impact: minor



Source: Appendix B.4, Eqs.(57)–(64), PDF p.21



### Source claim (paraphrase)

The appendix claims a filtered posterior for new process noise \(\epsilon_t\), but uses inherited state covariance plus new noise in its gain numerator.



### Analysis

In a linear Gaussian step, let inherited uncertainty be \(P\), process covariance \(Q\), transition Jacobian \(J\), readout \(W\) and observation covariance \(R\). State prior covariance is \(P^-=JPJ^\top+Q\), but \(\operatorname{Cov}(\epsilon_t,y_t)=QW^\top\), not \(P^-W^\top\). For independent scalar inherited state \(N(0,3)\), fresh noise \(N(0,1)\), identity transition/readout and observation noise \(N(0,2)\), observe \(y=1\). The printed state gain gives mean \(2/3\) and covariance \(4/3\). Direct Gaussian conditioning gives the process-noise posterior mean \(1/6\) and variance \(5/6\). The example is exactly linear, so EKF linearization cannot explain the difference.



### Finding and scope

The formulas can describe a state correction, but not the stated posterior of fresh generative process noise when inherited uncertainty is nonzero. If inherited uncertainty vanishes, the gain reduces to the valid greedy formula in Eq.(49). The main deterministic EF mechanism does not require this extension.



### Proposed correction

For the process-noise interpretation, write \(S=WP^-W^\top+R\) and use posterior mean \(QW^\top S^{-1}(y-W\bar r)\), covariance \(Q-QW^\top S^{-1}WQ\). Alternatively rename the inferred quantity as a state correction; that does not derive a posterior for fresh process noise. Reconstructing the full state posterior requires additional covariance information.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: The displayed M-step and experimental loss use different current outputs

Assessment: supported; impact: minor



Source: Section 2.3, PDF pp.4–5; Appendix B.3, Eqs.(51),(55)–(56), p.20; RNN_cells.py, lines 85–109; train.py, line 159



### Source claim (paraphrase)

The likelihood in Eq.(56) decodes the state after its inferred current correction. The printed deterministic EF mechanism and current source evaluate the present output before correcting the state.



### Analysis

Hold an inferred correction \(\epsilon^*\) fixed during the parameter step. The two current losses are \[L_{\rm pre}(\theta)=\tfrac12\|Wr_\theta-y^*\|^2,\qquad L_{\rm post}(\theta;\epsilon^*)=\tfrac12\|W(r_\theta+\epsilon^*)-y^*\|^2.\] Stopping gradients through \(\epsilon^*\) does not equate these residuals.

Take a one-step model \(r_\theta=\theta\in\mathbb R^2\), \(W=\operatorname{diag}(1,2)\), \(y^*=(1,1)^\top\), \(\theta_{\rm old}=0\), and \(Q=R=I\). Equation (49) gives \(\epsilon^*=(1/2,2/5)^\top\). At the old parameter, \[\nabla_\theta L_{\rm pre}=(-1,-2)^\top,\qquad \nabla_\theta L_{\rm post}=(-1/2,-2/5)^\top.\] The vectors are not collinear, so a scalar learning rate or MSE normalization cannot identify the updates. The implementation returns the unchanged pre-correction output, which train.py uses in the loss.

In the full-row-rank deterministic projection limit with forcing strength \(1\), the corrected output equals its target; its current post-correction residual vanishes, while the pre-correction residual need not. This limiting diagnostic does not claim a finite Gaussian likelihood at zero observation variance.



### Finding and scope

The displayed surrogate does not directly derive the particular experimental pre-correction output loss. The authors acknowledge greedy and approximate inference and describe related stochastic/deterministic mechanisms; the finding is an objective-level gap, rather than a disproof of every Bayesian interpretation or of EF’s observed learning behavior.



### Proposed correction

Retain the experimental algorithm while explicitly distinguishing its pre-correction loss from the related corrected-output Bayesian surrogate. Optimizing the latter defines a different algorithm whose performance and full-forcing behavior require separate assessment.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: Parameter descent does not generally follow the direct activity gradient

Assessment: supported; impact: minor



Source: Appendix A.1, after Eq.(35), PDF p.17; Eq.(36), p.18



### Source claim (paraphrase)

The text infers that activity changes induced by synaptic parameter updates follow the direction of the direct activity-space loss gradient.



### Analysis

For \(r=f(\theta)\), Jacobian \(J_\theta\) and \(g_r=\nabla_rL\), the chain rule yields \(\nabla_\theta L=J_\theta^\top g_r\). A parameter step therefore gives \[\Delta r=-\eta J_\theta J_\theta^\top g_r+O(\eta^2),\] which need not be parallel to \(-g_r\). For the exact linear example \(r(\theta)=(\theta,\theta)^\top\), \(W=(1,0)\), target \(1\), and \(L=(Wr-1)^2/2\), at \(\theta=0\) the activity gradient is \((-1,0)^\top\). Parameter descent produces \((\eta,\eta)^\top\), while direct activity descent produces \((\eta,0)^\top\). These vectors are not parallel. Sequence losses can introduce additional cross-time Jacobian terms.



### Finding and scope

The asserted directional identification is false. The formula \(W^\top(Wr-y^*)\) remains the correct direct activity gradient, and the transpose-feedback intervention can still be compared empirically with pseudoinverse feedback.



### Proposed correction

Retain the Jacobian-mediated displacement above and describe Eq.(36) as a direct activity intervention. Collinearity requires additional structure, such as \(g_r\) being an eigenvector of \(J_\theta J_\theta^\top\).

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 4: The XOR convergence threshold is overwritten

Assessment: supported; impact: minor



Source: Section 3.1, PDF p.6; Appendix D, p.23; train.py, lines 134–135,267–270



### Source claim (paraphrase)

The paper counts delayed-XOR convergence after MSE below \(0.1\) for ten consecutive epochs. The source first assigns that threshold for MDXOR, then immediately overwrites it with \(0.01\) unless the task is Cue.



### Analysis

For task MDXOR, the second conditional assignment has a false Cue test and sets \(0.01\). Ten consecutive validation losses \(0.05\) satisfy the paper’s criterion but fail the release’s criterion. This follows by direct case analysis of the two assignments and stopping branch; no training execution is needed.



### Finding and scope

The current released outcome definition is ten times stricter than the stated XOR threshold. Effects on published percentages cannot be quantified without the original histories and producing revision.



### Proposed correction

Use one task-to-threshold assignment with \(0.1\) for both MDXOR and Cue, and \(0.01\) for the remaining task, then assess affected convergence histories under the intended definition.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 5: The sine-task configuration has one output for two target channels

Assessment: supported; impact: minor



Source: Section 3.1, PDF pp.6–7; Appendix D, p.23; train_single.py, line 60; tasks/all.py, lines 146–152; RNN_cells.py, lines 89–107



### Source claim (paraphrase)

The task uses two phase-shifted waveforms and the task source constructs two channels, while the common configuration sets \(n_{\rm out}=1\), including for Cos.



### Analysis

For batch size \(2\) and recurrent dimension \(50\), predicted output has shape \(2\times1\), while the target slice is \(2\times2\). Subtraction broadcasts to a \(2\times2\) error. The one-output pseudoinverse has shape \(1\times50\), so feedback attempts \((2\times2)(1\times50)\), with incompatible inner dimensions. Teacher forcing has the same target-product mismatch. Even if feedback were skipped, a broadcast scalar output would be a different task from two independently decoded phase-shifted targets.



### Finding and scope

This configuration cannot implement the declared two-output sine task. The finding concerns the matched current release, rather than proof that the published experiments used this configuration.



### Proposed correction

Set the sine task’s output dimension to \(2\), while retaining \(1\) for the scalar tasks. Error then has shape \(B\times2\) and feedback matrix \(2\times N\). This checks the local dimensions, not successful end-to-end training.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 6: A trainable output bias is omitted from the teacher-forcing target

Assessment: supported; impact: minor



Source: Eq.(2), PDF p.2; train_single.py, line 75; RNN_cells.py, lines 41,46–47,89,104; train.py, line 107



### Source claim (paraphrase)

The configuration requests a frozen output bias, but b_out is created as a trainable parameter and omitted from the flag-setting loop. Decoding adds that bias, while the teacher state still uses \(W^+y^*\).



### Analysis

Under a linear effective readout \(y=Wr+b\), choose scalar \(W=1,b=1/2,y^*=1\) and full forcing. The released teacher target is \(r=1\), decoding to \(3/2\); the correct state for that affine readout is \(r=1/2\), decoding to \(1\). The error-forcing branch uses the actual output residual and retains the correct bias dependence. Zero-initialized bias is a countercontrol, but its requested training flag is not applied and the optimizer receives it. A ridge of \(10^{-7}\) in the inverse cannot explain the order-one mismatch.



### Finding and scope

The release does not enforce its requested frozen bias, and a nonzero bias changes the correct teacher-forcing target. No claim is made about how far the bias moved in historical runs; effective output scaling must also be handled consistently.



### Proposed correction

Honor the frozen zero-bias flag, or subtract the output bias in the teacher target and use the same effective linear readout and scaling as decoding.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
