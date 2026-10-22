# Towards Syn-to-Real IQA: A Novel Perspective on Reshaping Synthetic Data Distributions



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The latest author preprint retains the unequal-cluster generalization bound and the reversed explanation of fixed-cluster downsampling. A complete admissible construction violates the bound on every draw, so Major remains warranted. The current released cross-database script also selects epochs using target-test labels; its effect on the published scores remains unestablished.



## Scope

Read the complete original concern statements, then directly compared the latest author preprint with the final proceedings at the theorem, proof, downsampling algorithm and evaluation protocol. Fresh pinned author-source files were inspected statically and compared byte-for-byte with the earlier release; no author program was executed.



## Problem 1: Unequal clusters invalidate the risk bound

Assessment: supported; impact: major



Source: Latest arXiv v1, Section 3.1, p. 4; Theorem 3.1/Eq. (1), p. 5; Appendix C, pp. 14 and 16, especially Eq. (3).



### Source claim (paraphrase)

Theorem 3.1 promises a simultaneous high-probability bound for the empirical risk averaged over all samples from \(m\) independent centers and their local redundant samples. It permits unequal cluster sizes \(k_i\), but its redundancy term depends only on \(\eta=m^{-1}\sum_i k_i^{-1}\), without controlling the largest sample weight \(k_i/n\).



### Analysis

Take a singleton hypothesis class containing \(f_0(x)=0\), with \(L^1\) loss, and independent centers with deterministic labels \(Y=Z\), where \(Z\) is Bernoulli with probability \(1/2\). Set \(m=1000\), \(k_1=10^9\), \(k_i=1\) otherwise, and \(\delta=0.05\). The local distribution for each center is its own point mass, so redundant samples are exact copies and conditionally independent given that center. Their supports lie in the true support, labels are noise-free and losses lie in \([0,1]\). An additional independent continuous input coordinate makes center coordinates almost surely distinct if desired.

The true risk is \(R(f_0)=1/2\); the singleton constant-predictor Rademacher complexity is zero. With \(S=\sum_{i=2}^{1000}Z_i\), the actual sample-weighted risk and its uniform lower deviation satisfy \[R_{\rm emp}(f_0)=\frac{10^9 Z_1+S}{10^9+999},\qquad |R-R_{\rm emp}|\ge\frac12-\frac{999}{10^9+999}=0.499999001000998.\] This holds for every possible \(Z_1\) and \(0\le S\le999\).

Yet \(\eta=0.999000000001\), and the claimed upper bound is \[\sqrt{\frac{2\log40}{1000}}+\sqrt{\frac{0.999000000001\log40}{8000}}+\frac{2\log40}{3000}=0.10981586563536902.\] Its success probability is therefore \(0\), rather than at least \(0.95\). Even an alternative absolute-loss-class complexity of at most \(1/\sqrt{1000}\) would not close this gap.

The current Appendix C replaces the actual weighting \(\sum_i(k_i/n)\bar\ell_i\) with an approximately equal-center average. It also bounds cluster-mean variance by \(1/(4k_i)\); unconditional exact copies still have variance \(1/4\). Conditioning on the center can reduce that variance, but does not remove unequal center weights. Equal cluster sizes eliminate this particular weighting mismatch; they do not by themselves supply the missing local-distribution and uniform-control argument.



### Finding and scope

The latest Theorem 3.1 is false in its stated unequal-cluster generality, and its current proof cannot establish the claimed algorithmic guarantee. This finding does not show that distribution reshaping harms real IQA accuracy.



### Proposed correction

A narrower finite-class replacement explicitly records both missing terms. For \(|\mathcal F|=M\), bounded losses, independent centers, \(w_i=k_i/n\), center losses \(\ell_i(f)\), and cluster means \(\bar\ell_i(f)\), define \[T(w)=\tfrac12\sum_i|w_i-1/m|,\qquad B_f=\sum_iw_i|\bar\ell_i(f)-\ell_i(f)|.\] Then with probability at least \(1-\delta\), simultaneously over the finite class, \[|R(f)-R_{\rm emp}(f)|\le\sqrt{\frac{\log(2M/\delta)}{2m}}+T(w)+B_f.\]

Triangle inequality separates the independent-center mean error, the reweighting error and the within-cluster deviation. Since losses lie in \([0,1]\) and the signed weight differences sum to zero, reweighting is bounded by \(T(w)\). Two-sided Hoeffding and a union bound give the first term. This allows arbitrary within-cluster dependence; it adds a finite-class assumption and does not restore the unrestricted original theorem or prove either algorithm improves risk.

The current preprint and inspected author-release paths retain the implicated statements or behavior. The bounded proposed corrections are not established as adopted or empirically validated.



## Problem 2: Fixed-cluster downsampling increases eta

Assessment: supported; impact: minor



Source: Latest arXiv v1, discussion after Theorem 3.1, p. 5; Section 3.3.2, p. 6; Algorithm 3 and the following explanation, p. 7.



### Source claim (paraphrase)

DRCDown is explicitly motivated as decreasing \(\eta=m^{-1}\sum_i1/k_i\), thereby lowering the third term of Theorem 3.1.



### Analysis

Within one fixed collection of nonempty clusters, deletion gives \(1\le k_i^{\prime}\le k_i\), so \[\eta^{\prime}-\eta=\frac1m\sum_i\left(\frac1{k_i^{\prime}}-\frac1{k_i}\right)\ge0,\] strictly if any cluster loses samples. For example, two clusters of size \(100\) with \(T_u=20\) are both reduced by Algorithm 3 to size \(50\); \(\eta\) rises from \(0.01\) to \(0.02\), increasing the displayed square-root term at fixed \(m,\delta\).

Reallocating a fixed total number of samples to balance cluster sizes is a different operation: Jensen gives \(\eta\ge m/n\) at fixed \(m,n\). Actual deletion decreases \(n\). Re-extracting features can also redefine the cluster set, but needs a separate analysis and does not reverse the fixed-cluster calculation.



### Finding and scope

The current monotonicity explanation has the wrong direction for the stated quantity and deletion rule. This corrects the theoretical motivation without demonstrating that downsampling lowers real accuracy or overturning the reported empirical improvements.



### Proposed correction

Remove the claim that this fixed-cluster deletion lowers the defined \(\eta\). Any theory for reweighting or changing clusters must state the changed quantity and assumptions; empirical benefit alone does not prove the printed monotonicity.

The current preprint and inspected author-release paths retain the implicated statements or behavior. The bounded proposed corrections are not established as adopted or empirically validated.



## Problem 3: Released epoch selection uses target-test labels

Assessment: supported; impact: minor



Source: Li-aobo/SynDR-IQA, current commit b8e53fe2c937265a00cefb15abb1b3fae7c47fdd: train_test_IQA_cross.py, main(), lines 30–67; BaseIQASolver.py, test(), lines 75–100; latest paper Section 4.1, p. 7.



### Source claim (paraphrase)

The paper describes source-database training and target-database testing. The actual released cross-database script computes target-test correlation at every epoch and retains the best target-test epoch.



### Analysis

In main(), test_data is built from config.test_db at line 33. Each epoch calls solver.test(test_data) at line 43; lines 44–46 update best_srcc and the corresponding best_plcc when target-test SRCC improves. Lines 52–62 optionally save the selected checkpoint, and lines 66–67 print the best cross-database metrics. In test(), lines 95–98 average patch predictions and ground-truth scores and compute Spearman and Pearson correlations. Thus target labels participate in the selection \[\widehat k=\arg\max_k\widehat\rho_{\rm test}(f_k).\]

A concrete dependence check needs no training: candidate score vectors \((0,1,2,3)\), \((0,2,1,3)\), and \((3,2,1,0)\) have SRCCs \((1,0.8,-1)\) against labels \((0,1,2,3)\), but \((0.8,1,-0.8)\) against labels \((0,2,1,3)\). The positive-best selection therefore switches from the first candidate to the second when only target labels change. These are transparent score comparisons, not new executions of the author function or actual benchmark outputs.

The current head is the same December 2025 commit, and the freshly fetched operative files are byte-identical to the earlier author release. This confirms the released behavior persists, but does not establish that the paper tables were generated with that path. The README names a different entry point that is absent at this pinned URL; no behavior is inferred for that unavailable file.



### Finding and scope

The inspected released path uses the target set for model selection, so its maximum cannot be interpreted as performance on an untouched target-test set. The historical table attribution and the magnitude of any score bias remain unresolved; no corrected SRCC or PLCC is asserted.



### Proposed correction

Select epochs on source or independent validation data, or predeclare the epoch, then evaluate the frozen model on held-out target data. An allowed labeled-target validation design requires a separate target test set and an explicit task description. No corrected benchmark evaluation was run.

The current preprint and inspected author-release paths retain the implicated statements or behavior. The bounded proposed corrections are not established as adopted or empirically validated.



## Limits

- Independent scientific adjudication remains pending.

- The exact script and selection rule used for the historical paper tables are not established by the repository head alone.

- No author code, IQA model training, benchmark evaluation or verifier program was executed.

- The risk counterexample is a legal clustered-data construction, not an estimate of real IQA performance.

- The README names a cross-database entry point that returned HTTP 404 at the pinned current commit; the finding is restricted to the actual released script inspected below.
