# Uncovering a Universal Abstract Algorithm for Modular Addition in Neural Networks



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



An explicit admissible modulus refutes the finite random-frequency margin theorem, which determines Major. The remaining map-direction, quotient-coset, projection and empirical-scope findings are local corrections or unresolved interpretations; they do not establish that all observed network mechanisms fail.



## Scope

Claim-focused reading of the identified paper and author-released materials. The arguments below distinguish mathematical contradictions, version-specific implementation defects and unresolved empirical consequences. No author code was executed in this revision.



## Problem 1: The finite random-frequency bound fails at an admissible modulus

Assessment: supported; impact: major



Source: Theorem 4.7, p. 6; Theorem C.1 and proof, Appendix C, pp. 22-24.



### Source claim (paraphrase)

Theorem 4.7/Theorem C.1 claim minimum incorrect-answer margin exceeding \(\delta m'\) with probability at least \(\rho\) when \(m\) distinct uniformly sampled half-spectrum frequencies exceed \([2\log n-2\log(2-2\rho)]/[\log(\pi/\delta)-1]\). No prime/coprime or large-modulus restriction appears in the operative statement.



### Analysis

Take \(n=6\), \(m=m'=1\), \(\delta=0.001\), \(\rho=0.9\), and inputs \(i=j=0\). The stated frequency-count threshold is approximately \(0.964539<1\), so its premise holds. Frequencies \(1,2,3\) are equally likely. Frequency \(1\) has minimum incorrect margin \(1/2\); frequency \(2\) ties the correct answer at displacement \(3\), and frequency \(3\) ties it at displacement \(2\). Success probability is exactly \(1/3<0.9\), contradicting the claimed guarantee.

The main text samples uniformly from \(\{1,\ldots,n/2\}\), while Appendix C uses \(\{1,\ldots,n-1\}\). The witness also defeats the latter convention: at \(n=6\), only frequencies \(1,5\) avoid a tied incorrect answer, giving success probability \(2/5<0.9\). Thus the sampling-domain discrepancy does not rescue either stated finite guarantee. The appendix explicitly calls its Taylor/volume/Stirling argument a heuristic and says a rigorous proof needs more precise bounds; that is important counterevidence against treating it as a rigorous finite-grid argument, but does not make the main theorem’s unconditional probability statement true.



### Finding and scope

The theorem is false on its stated finite-spectrum domain. This does not deny successful prime-modulus networks or prove any claim about training universality.



### Proposed correction

A replacement concentration statement must account for the finite frequency population, coprimality and confidence conditions. No claim of corrected training convergence is made.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: The frequency-normalizing function map is reversed

Assessment: supported; impact: minor



Source: Definition 4.2, p. 4; supplementary plots_multilayer.py, lines 628-635.



### Source claim (paraphrase)

Definition 4.2 (p. 4) uses the inverse frequency to normalize the sinusoid, but prints the map in the direction \(g(dx)=h(x)\).



### Analysis

For a coprime frequency, write \(d=f^{-1}\pmod n\) and \(h(x)=\cos(2\pi fx/n)\). The printed definition is \[
g(dx)=h(x),\qquad\text{equivalently}\qquad g(x)=h(d^{-1}x).
\] This multiplies the frequency by \(f\), producing \(f^2\bmod n\); it does not generally normalize the frequency to one. The correct reparameterization is \[
g(x)=h(dx)=\cos(2\pi x/n).
\] Equivalently, when moving an old sample at index a to a new plotting location, set the new index to f a mod n. Function composition and moving array entries use opposite-looking maps, which likely explains the printed reversal. For the concrete case \(n=7,f=2,d=4\), the printed definition produces frequency four, whose real-FFT representative is three, rather than frequency one. The maximum discrepancy from the frequency-one sequence is approximately 1.52446. The corrected definition agrees to numerical precision. The author-supplied plotting code assigns new indices \(a_{\rm new}=fa\bmod n\) and \(b_{\rm new}=fb\bmod n\). That is consistent with the corrected reindexing when the frequency is coprime to the modulus. This is evidence that a written inverse error need not have corrupted the displayed prime-modulus plots. For composite moduli and a noncoprime frequency, multiplication by f on all n indices is not a permutation: it repeats destinations and leaves others unused. A general implementation must operate on the quotient or explicitly aggregate equivalent indices. A bijective prime-modulus check is insufficient to certify the composite-modulus plotting path.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Use \(g(x)=h(dx)\) for the function reparameterization and distinguish it from moving array indices.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: An approximate coset needs the full quotient preimage

Assessment: supported; impact: minor



Source: Definitions 4.1-4.3, p. 4; Appendix A.2.1; Appendix B, p. 22.



### Source claim (paraphrase)

Definitions \(4.1\)-\(-4.3\) and Appendix B move between a quotient cycle and supports in the original cyclic group.



### Analysis

Definition 4.3 writes a progression in quotient vertices without the full preimage that lifts it to the original cyclic group. At \(n=66,f=11\), the exact phase-zero fiber is \[\{0,6,12,18,24,30,36,42,48,54,60\}\], whereas the literal minimal progression contains \(-1,0,1\pmod{66}\). Positive minimum radii also exclude the radius-zero case needed for exact fibers.

Set \(g=\gcd(n,f)\), \(q=n/g\), quotient map \(\pi:C_n\to C_q\) and \(d=(f/g)^{-1}\pmod q\). A consistent object is \(\pi^{-1}\{\pi(c)+jd\pmod q:-r_-\le j\le r_+\}\), with nonnegative radii. Appendix B's inverse must similarly be taken modulo \(q\), not \(n\): at \(n=12,f=8\), \(f/g=2\) has an inverse modulo three but not twelve.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Define approximate cosets as full preimages of quotient arcs with nonnegative radii, allowing radius zero.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: Positive hidden activation does not guarantee positive evidence for the answer

Assessment: supported; impact: minor



Source: simple-neuron model, pp. 3-4; Theorem 4.4, p. 4; Appendix B, pp. 21-22.



### Source claim (paraphrase)

Theorem 4.4 and its surrounding interpretation relate a simple neuron's approximate-coset activation to a correct-output support.



### Analysis

A hidden neuron's activation is a function of the input pair \((a,b)\). Its outgoing weights form a different function of the candidate answer \(c\). The theorem describes activation on an approximate coset containing the correct answer, but its proof does not fully specify the relation between these two domains or show that positive ReLU activation guarantees positive output evidence at the correct answer. Consider the paper's own simple-neuron parameterization with \(n=12\), frequency one, phases \(s_A=s_B=0\), and positive amplitude one. Take \(a=b=2\). The input preactivation is \[
\cos(\pi/3)+\cos(\pi/3)=1,
\] so ReLU is positive. The correct answer is \(c=4\), but its outgoing weight is \[
\cos(2\pi\cdot4/12)=\cos(2\pi/3)=-\tfrac12.
\] The neuron's contribution to the correct logit is therefore \(-1/2\). The correct answer is outside the positive support of that outgoing sinusoid despite positive hidden activation. Positive activation alone does not prove the strong answer-support interpretation used in parts of the discussion. This construction does not refute successful addition by a complete phase-balanced cluster. Other neurons can compensate, and the aggregate cosine construction in Appendix C is a different object. Nor does it rule out calling a sufficiently large quotient arc an approximate coset containing the answer. It shows why the theorem needs an explicit, nonvacuous statement: which support is a set over inputs, which is over outputs, what radius is allowed, and what quantitative relationship is guaranteed? The last step of Appendix B says that later ReLU layers preserve linear combinations of approximate cosets because ReLU removes negative elements. For a signed sum of overlapping components, thresholding may create a different union of intervals or supports. It is not automatically the same linear combination. Conversely, if arbitrary linear combinations of all singleton indicators are allowed, every function on a finite domain has such an expansion, and the claim provides no mechanism-specific restriction. A useful theorem must define the basis, coefficients, closure property, and sparsity or geometry that make the statement informative.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Separate input activation support from output-logit support and state a quantitative cluster-level relationship if required.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 5: The projection sign is wrong and coordinate bounds do not exclude a representation

Assessment: supported; impact: minor



Source: Appendix D, pp. 24-25.



### Source claim (paraphrase)

Appendix D projects a standard rotation with a negative sine component, then identifies the result with a phase difference; it also discusses weights beyond \([-1,1]\).



### Analysis

The appendix uses the usual planar rotation acting on (\(1\), \(0\)) but writes a projection vector with components \((\alpha\cos\phi,-\alpha\sin\phi)\). Their dot product equals \[
\alpha\{\cos\phi\cos\theta-\sin\phi\sin\theta\}
=\alpha\cos(\theta+\phi).
\] The following expression instead uses the plus sign appropriate for \(\alpha\cos(\theta-\phi)\). At \(\theta=\pi/3,\phi=\pi/6\), the written vector gives zero whereas the claimed phase-difference expression gives approximately 0.8660254. Change the second projection component to \(+\alpha\sin\phi\), or explicitly reverse the rotation convention. State the convention once and use it consistently. The separate observation that learned scalar weights can exceed the interval \([-1,1]\) cannot by itself exclude a group representation. That interval describes entries of a normalized planar rotation matrix in an orthonormal basis. A representation in \(\operatorname{GL}(V)\), as defined in Appendix A, may be written in another basis. For example, conjugate the \(90\)-degree rotation by \(S=\operatorname{diag}(2,1)\). The resulting generator is \[
S\begin{pmatrix}0&-1\\1&0\end{pmatrix}S^{-1}
=\begin{pmatrix}0&-2\\1/2&0\end{pmatrix}.
\] Its fourth power is the identity, so it gives a valid representation of the cyclic group of order four, although one entry has magnitude two. Embeddings and readouts derived from a representation may also include scaling and projection; the resulting readout arrays need not themselves be group homomorphisms. A raw coordinate-range observation only rules out a particular normalized parameterization. Appendix D already introduces scaled projections and acknowledges compatibility with the representation hypothesis. That acknowledgment should also constrain any broader exclusion suggested by the section's heading or discussion. This criticism does not establish that the prior group-composition interpretation is universal. It concerns the specific argument used to exclude it here. A stronger comparison would test whether a common change of basis and readout makes the learned operators approximately satisfy the relevant group law, then quantify the residual. The paper can still argue that the coset description is more explanatory in particular networks, but coordinate magnitudes alone do not settle that comparison.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Correct the projection sign and use basis-invariant criteria when discussing group representations.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 6: The reported logarithmic fits are valid finite empirical evidence

Assessment: not_issue; impact: no_issue_found



Source: Paper Figure 3, p. 6; Appendix E experiment settings; author-released make_figure_logn_scaling_plot.py.



### Source claim (paraphrase)

Figure 3 fits frequency counts against log modulus from author-supplied aggregate data while experiment settings also change.



### Analysis

The author-supplied finite aggregate values yield slopes on log modulus of \(1.174595\) (Clock), \(1.189408\) (Pizza), and \(0.726435\) (MLP), with \(R^2\) approximately \(0.989\)–0.990. Those fits are not an error. Width, training fractions and other settings vary with modulus; a finite strong fit does not establish an asymptotic necessary law or a training-independent mechanism.



### Finding and scope

The supplied finite fits are reproduced by their stated arrays and can support an empirical trend. They do not independently prove an asymptotic or necessary law; this boundary is a clarification, not a separate current calculation error. The formal finite guarantee is addressed separately.



## Problem 7: The mechanism evidence is conditioned on successful models and a detector

Assessment: needs_evidence; impact: needs_evidence



Source: introduction, pp. 1-2; results and discussion, pp. 7-10; Appendix E.5, p. 28; Appendices G.4-G.5 and G.9.



### Source claim (paraphrase)

The introduction and conclusion discuss universality while Appendix E.5 selects successful models and Appendix G describes approximation and manual circuit-classifier adjustments.



### Analysis

Appendix E.5 selects models that achieve at least \(99.9999\%\) final accuracy and drops neurons below the stated activation threshold. Appendix G also presents unsuccessful or atypical cases and describes approximations in the circuit detector, including manual adjustment for some runs. These are useful disclosures. They mean the analyzed population is conditioned on successful training and on the operational definition of a usable neuron or circuit. The evidence should therefore be described as common structure observed across the evaluated successful models. It does not establish the same structure in all optimization outcomes, all hyperparameter regimes, all architectures, or all functions performed by all neurons. Calling limitations open questions does not remove this selection boundary. The circuit detector is part of the measurement process. To use its outputs as evidence for a universal mechanism, report its criteria before classifying models, the amount of manual tuning, the rate of ambiguous/unclassified neurons, and sensitivity to thresholds. A blinded validation set of hand-inspected neurons or small circuits would help separate a robust phenomenon from flexibility in the classifier. The appendix's acknowledgment that its approximation is not fully accurate should remain visible in the main claim. Theorem 4.7 assumes sinusoidal components and analyzes their combined logits. It does not prove that training converges to this family. Theorem 4.4 likewise starts from the simple-neuron assumption. Empirical support for that assumption and a conditional theorem are complementary, but together they do not turn a restricted model family into an unconditional theorem about all neural networks. The extension from cyclic groups to a universal abstract mechanism covering other groups also needs its own statement and evidence. Existing coset observations in another task motivate that extension; they do not by themselves prove an exhaustive classification of mechanisms across group families. A useful next paper could specify the proposed abstraction as an explicit algorithm with inputs, intermediate state, decoder, approximation error, and falsifiable exclusions.



### Finding and scope

The available material identifies a scope or evidence gap; it does not prove that the reported empirical effect is false.



### Proposed correction

State the successful-model selection and detector criteria, including manual adjustments and unclassified cases.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 8: Redundancy and margin formation do not yet define an error-correcting code

Assessment: needs_evidence; impact: needs_evidence



Source: Appendix G.9.3 and related discussion.



### Source claim (paraphrase)

Appendix G.9.3 interprets redundant components in error-correction terms.



### Analysis

Redundant components can improve margins or reduce loss without constituting an established error-correcting code. A coding claim requires the encoded object, codeword map, error channel, distance notion, and decoder to be specified. The relevant statement is then whether the decoder recovers the answer under a defined number or distribution of perturbations. For this paper, one concrete route would encode an answer by its vector of selected phase or cosine features, define corruption at the feature or cluster level, and test a stated decoder under random and adversarial feature changes. Measure minimum separation over answers and compare it with the corruption radius. Ablating redundant neurons and observing performance changes is useful but does not alone establish such a code or its correction capability. The current evidence supports redundancy and aggregate margin formation. Present the coding interpretation as a hypothesis unless the additional operational definitions and tests are supplied.



### Finding and scope

The available material identifies a scope or evidence gap; it does not prove that the reported empirical effect is false.



### Proposed correction

Treat error-correction as a hypothesis unless a code, channel, distance and decoder are defined and tested.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 9: Figure variables, toy readout and factor-count conventions need explicit definitions

Assessment: supported; impact: minor



Source: Official PDF: Figure 12, p. 22; Appendix A.2.2; coset-type/factor-count and half-frequency discussions.



### Source claim (paraphrase)

Figure 12, Appendix A.2.2 and related discussion use margin, frequency-count, toy-logit and factor-count descriptions that require distinct definitions.



### Analysis

Figure 12, p. 22, fixes modulus \(59\) and varies the number of frequency components over a small range, while its caption invokes growth with \(\log n\). Those variables are different. The plotted average margin also differs from the minimum margin over all incorrect outputs used in Theorem 4.7. An average can be positive while an incorrect output still ties the correct one. Relabel the independent variable and identify whether the plotted statistic is an average, a minimum, or a success probability. Appendix A.2.2 has a repeated component label in its toy discussion and does not fully specify the readout needed to reconstruct the listed toy logits. Under a direct literal cosine readout, the displayed values do not follow without additional scaling or indicator choices. This is a request for an executable toy specification, not a claim that the intended toy mechanism is impossible. The discussion of a number of coset types growing logarithmically uses a large-modulus example without defining exactly what counts as a type. Classical CRT decomposes into pairwise coprime prime-power factors, whose count differs from counting prime factors with multiplicity or a chosen hierarchy of subproblems. State the counting convention before using the example as complexity evidence. References to a half-frequency response should distinguish a continuous interpolation used to visualize a finite sequence from a character frequency of the finite cyclic group. Every function on a finite cycle has an expansion in its integer-indexed discrete Fourier basis. Observing a shape that resembles a half-frequency sinusoid under one plotting convention does not contradict that fact. Any claimed failure of an earlier mechanism must use that mechanism's actual assumptions and quantitative predictions.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Define figure variables, readout normalization, minimum-versus-average margins and factor-count conventions.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.
