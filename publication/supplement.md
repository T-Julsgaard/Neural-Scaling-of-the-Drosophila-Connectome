# Technical supplement

### Bounded participation calibration and memory retention

Thomas Julsgaard

Report date 16 September 2026 · Production completed 21 September 2026

## S1 Anatomical extraction and model equations

The main report's references [1–10] also apply here. Larval Supplementary Table 1 [1] is a 387 × 387 contact matrix with presynaptic rows and postsynaptic columns. The retained left projection contains 40 PNs and 73 mature KCs. Of 110 left KCs, 37 are labeled young and are excluded; 27 young cells have no input from the selected PNs. Duplicate display labels are not used as identifiers. Fourteen label mismatches elsewhere in the full matrix do not license treating the entire matrix as an aligned whole-network adjacency. The selected mature subset contains 365 positive edges and 2,188 contacts. Each KC column is normalized to sum to one.

The adult extraction uses the non-cropped traced-neuron adjacency export for hemibrain v1.1 [2,3]. Monoglomerular PN IDs come from the compensation repository [4]. Filters retain type exactly KCg-m, region CA(R), positive contacts and connected endpoints; duplicate rows are summed and numeric body IDs sorted. Zero-input KCs and zero-output PNs are excluded. The author's positional KC exclusion list is not applied without its original ordering. Unknown residual incompleteness remains a limitation. The resulting 104 × 590 projection contains 4,878 edges and 85,151 contacts. Source release, paper publication year and download date are distinct metadata.

**Encoder.** Let P denote the column-normalized input projection and θ the offset vector. Compute z = uP − θ, select the K largest entries with fixed tie priorities, and assign xⱼ = 10/K to winners and zero otherwise. Hence Σxⱼ = 10 and Σxⱼ² = 100/K. With baseline winner frequencies p₀, target frequency is pₜ = (1 − α)p₀ + αK/N. Let s be the median of positive standard deviations of pre-offset drives. Each of 100 steps sets θ ← Π[θ + 0.5s(p − pₜ)], where Π projects onto the intersection of zero-sum offsets and coordinate bounds ±0.25s. Separate 4,096-observation fit and validation pools precede rewarded development. Offsets are then frozen.

**Learner.** Initialize both output vectors at 0.1. For observed outcome y and feature vector x, error is e = y − x·(w⁺ − w⁻). Updates are w⁺ ← max(0,w⁺ + ηxe) and w⁻ ← max(0,w⁻ − ηxe). Without clipping, the signed difference changes by 2ηxe. An old signed feature difference d changes margin by 2ηe(d·x). This algebra explains why activity overlap alone cannot determine whether an individual update helps an old distinction; it is not a new mechanism or an identified mediator of the calibration null.

Initial Eq. 8 implementation validation used Bennett et al. [9,10], repository revision 7ec52afb9bd7bb748d94d60dea9f483645a2ce8e. The later generic delta learner is a separate selected arm. The readout decomposition w = max(w,0) − max(−w,0) can express any signed linear vector when no upper bound is imposed; clipping can nevertheless change the optimization trajectory.

<!-- PAGE -->
## S2 Calibration assays and statistical specification

The larval persistent-memory task uses 40-coordinate synthetic cues with ten active coordinates, shared cores of two or six coordinates, clipped Gaussian observation noise SD 0.1, and stochastic preferred/nonpreferred outcomes with probabilities 0.8/0.2. Adult cues use 26 of 104 active coordinates with five or sixteen shared coordinates. Weights persist across pairs. Primary evaluation uses sixteen high-similarity pairs and 128 presentations per pair. Supporting larval loads are 2, 4, 8 and 16; adult loads are 4 and 16. The fixed-total-exposure regime distributes 512 presentations across pairs. Reversal flips every other association; read-only probes never update weights.

Eight development blocks select one global setting per method. The larval sparse learning-rate grid is (0.01/3) × 2ʲ for j = −4, −3, −2, −1, 0, 1, followed by 0.01 and 0.015. Temperatures are 0.1 and 0.2. Ordinary tuning uses K ∈ {4,6}; calibrated and shuffled-offset methods use K6 and α ∈ {0.25,0.5}. Adult K values are 32 and 48, and sparse rates are multiplied by eight. Direct/oracle arms use sixteen geometrically spaced rates across the larval endpoints and both temperatures; adult direct rates additionally scale by 10/26. Candidate count is 32 per method, but three null/sham replicas multiply simulation costs.

| Study and selected method | K | Strength | Rate η | Temperature |
|---|---:|---:|---:|---:|
| Larval ordinary | 6 | 0 | 0.006666667 | 0.1 |
| Larval calibrated | 6 | 0.25 | 0.006666667 | 0.1 |
| Larval optimized sham | 6 | 0.5 | 0.006666667 | 0.1 |
| Adult ordinary | 32 | 0 | 0.013333333 | 0.1 |
| Adult calibrated | 48 | 0.5 | 0.026666667 | 0.1 |
| Adult optimized sham | 48 | 0.5 | 0.026666667 | 0.1 |

The main paired contrast is calibrated minus ordinary final mean preferred-choice probability. Original 98.333333% block-bootstrap intervals cover the three primary comparisons; the practical band is ±3 percentage points. Guardrails cover new learning, reversal, unchanged associations after reversal and within-sequence worst-pair probability against three comparators. Each one-sided lower bound uses α = 0.05/12 and must exceed −3 points. Nine of twelve pass in both studies; all worst-pair tests remain unestablished. There is no global multiplicity adjustment across the research sequence.

The selected larval offset bound is 0.052509 and 49.32% of offsets saturate. The exact-multiset sham was added after development but before confirmation, preserving the selected calibrated offsets while shuffling their assignments. Its retention contrast was −0.75 [−1.91, 0.33] points (descriptive 95%). In the adult study, optimized and exact-multiset shams coincide; these are one control, not independent evidence. Similarly, larval ordinary tuning selects the same setting as the K6 reference.

Adult adequacy requires ordinary acquisition lower 95% bound above 80%, oracle acquisition and retention lower bounds above 95%, and ordinary retention interval wholly between 55% and 95%. The gate passed, with ordinary retention interval [92.94,94.89]%. No confirmation-driven extension or retuning occurred.

<!-- PAGE -->
## S3 Supplied model compensation reference

EXP-009 adapts the supplied model associated with Figure 4B2, c = 1, of Abdelrahman et al. [4]. The pinned code revision is 9f3f7e9e85117febef1ad32e3152c830570f74d3. Original GPL-3.0 notices remain with the source. This study uses one saved calibrated MAT instance with 24 PN inputs, 2,000 graded KCs, pseudo-feedforward APL inhibition and two readouts containing 4,000 learned weights per arm. It does not regenerate the authors' twenty-model ensemble or validate the joint compensation optimizer.

The inherited sensory chain is explicit. The supplied hallem_olsen table contains PN rates already transformed from the odor responses underlying Hallem and Carlson [S1], using the type of ORN-to-PN transformation described by Olsen, Bhandawat and Wilson [S2]. The empirical noise lookup is inherited through getPNStdevBhandawat and the sensory variability work of Bhandawat et al. [S3]. We do not reprocess the original physiological recordings or apply the PN transformation a second time.

Each new task resamples 100 synthetic odors independently from 24 empirical PN marginals across the first 110 supplied rows. Balanced random labels, independent random readout initialization, fifteen noisy training observations and fifteen independent noisy probes per odor are paired between arms. The recovered affine PN scale is frozen. KC responses implement the supplied rectified excitation-minus-inhibition-minus-threshold equation. Training-only maximum response scales each arm; test responses may exceed one. Wrong-valence output weights undergo multiplicative exponential depression with learning rate divided by mean training activity. Accumulated sufficient statistics reproduce the exact product of per-odor factors. The endpoint averages correct-valence probability rather than sampled correctness.

| Inherited or changed component | Status and implication |
|---|---|
| Projection and fitted thresholds | Supplied state retained; upstream fit cost unknown |
| Compensated excitation | Saved 5× gain; inspected script says 4.5×; discrepancy preserved |
| Fresh tasks | Resampled empirical marginals rather than recovered original histogram odors |
| Training noise | Every training trial noisy rather than a clean first trial |
| Response scaling | Training-only maximum replaces use of all-trial extrema |
| Rate choice | Four development blocks; identical ten-rate opportunity per arm |
| Equations | SI 3, 20 and 21 checked against author-runtime arithmetic |

The ten rates are 10 raised to exponents −5, −4, −3, −2.75, −2.5, −2.25, −2, −1, 0 and 1. Selected rates were 0.001 and 0.00177828. The +8.58 [8.13,9.03]-point effect uses a 50,000-draw paired percentile bootstrap across 24 fresh blocks. Maximum author-runtime discrepancy was 1.17 × 10⁻¹⁵ against tolerance 10⁻¹⁰. Those checks support arithmetic, not an exact published-panel replication or threshold-only causality. The source's published twenty-model means and our new block means are not pooled. Historical preservation scanning finished after confirmation; the scientific source and selected settings were frozen before their relevant stages.

<!-- PAGE -->
## S4 Readout diagnostics and access accounting

EXP-010 uses 24 fresh pair-memory blocks, averaging native and calibrated K6 within block. Old accuracy covers the first fifteen pairs, with 64 independent SD 0.1-noise observations per pair and half credit for ties. Chosen-only offline fitting uses precisely the archived chosen observations and stochastic ±1 outcomes. Full offline and full online use the same 4,096 observations/outcomes; full online updates cue zero then cue one, with the second update using the already changed weights. Chosen online performs 2,048 updates, full online 4,096, and ten-pass replay 40,960. Online η = 1/150 is fixed. Six development blocks select ridge penalties from {10⁻⁶,10⁻⁴,0.01,0.1}; fitting never uses evaluation observations or labels.

Ridge solves (XᵀX + λI)w = Xᵀy, with independent augmented least-squares validation and enforced relative normal-equation residual below 10⁻⁹. Its stored-history access, objective and solver differ from online learning. Primary gaps and forgetting use paired Student-t intervals across 24 blocks. The prediction requires mean recovery ≥80% and lower 95% bounds above five points for both the gap and acquisition loss. The same conjunction is frozen for EXP-011; the recovery requirement is not a confidence-bound condition.

In EXP-011, component strengths are uniform on [0.6,1], two nuisance coordinates have strengths uniform on [0.1,0.3], and clipped Gaussian noise has SD 0.05. Each phase has 128 balanced training samples; fresh probes number 512 per context and noise level. Context order, channel permutation and output polarity vary by block. All four logical combinations are trained. Polynomial features consist of a constant, forty linear terms and all 820 pair products including squares, giving 861 dimensions. Direct and polynomial scaling uses all 256 training inputs and matches mean squared norm 100/6, with unlabeled future-context lookahead but no held-out leakage.

The rate grid is {1/2400,1/600,1/150,2/75}; ridge uses the same four penalties as EXP-010. Six development blocks maximize mean final performance across contexts; earliest candidate wins ties. Twenty-four fresh blocks remain fixed. Selected blocked η = 1/2400 for every representation. Native ridge λ = 0.01; calibrated λ = 10⁻⁶. Both native/calibrated shuffled rates are 2/75, local10 rates 1/2400, and replay10 rates 1/600. Full per-representation selections are retained in the compact evidence.

| C schedule | Unique examples | Updates | Historical access | Native/calibrated old / new % |
|---|---:|---:|---|---:|
| Blocked | 256 | 256 | Current example | 51.73 / 97.48 |
| Shuffled | 256 | 256 | Both contexts together | 90.14 / 95.79 |
| Local10 | 256 | 2,560 | Current context | 25.66 / 99.91 |
| Replay10 | 256 | 2,560 | Both contexts revisited | 86.60 / 98.28 |

This table uses separately selected rates; the main Figure 3 instead fixes η = 1/150. Its old/new paired contrasts are +56.68 [46.97,66.39] and −0.89 [−1.44,−0.33] points. All schedule contrasts are descriptive 95% intervals. Stored-data access and order change together, and simulator storage is not a streaming-memory benchmark.

<!-- PAGE -->
## S5 Resources and supporting experiments

Parameter counts are separate from the number of examples, update count and tuning opportunity. Larval sparse online models store 146 reward-learned scalars, adult models 1,180. Calibration adds 73 or 590 stored offsets, with one centering constraint. Direct online inputs use 80 or 208 reward-learned scalars. In XOR, quadratic online features use 1,722 readout scalars; offline fits one signed vector of the corresponding dimension. The supplied-model compensation reference uses 4,000 output weights per arm plus 2,000 inherited fitted thresholds and global fitted quantities. Inherited calibration expense is unknown, not zero.

| Study | Confirmation blocks | Summed worker wall s | CPU s | Peak worker memory |
|---|---:|---:|---:|---:|
| Larval calibration EXP-007 | 32 | 1,886.21 | 1,809.16 | 70.35 MB |
| Adult calibration EXP-008 | 24 | 2,529.66 | 2,442.20 | 169.03 MB |
| Supplied-model reference EXP-009 | 24 | 12.72 | 11.30 | 171.94 MiB |
| Pair-memory diagnostic EXP-010 | 24 | 301.77 | 293.88 | 126.08 MiB |
| XOR transfer EXP-011 | 24 | 109.35 | 68.22 | 76.82 MiB |

Units follow the original reports; MB and MiB are not silently conflated. The table excludes report production, scientific replay/audit and source preparation. Summed worker time is not elapsed campaign time, and aggregate block timing is not a per-method benchmark. New larval/adult calibration took 22.06/75.53 wall seconds separately. Historical runs used local CPU computation, with no GPU or paid-compute inference supported by these figures.

Earlier experiments are supporting context. EXP-003 excluded its proposed five-point organization advantage under the tested growth procedures. EXP-004 separated active count from population growth under a fixed 32-feature readout: K4→K6 improved retention by +5.37 [3.89,6.97] points, while N73→N110 reduced it by −5.03 [−7.27,−2.86] (98.333333% intervals, 32 blocks). These interventions do not establish a general scaling relation. Structural-perturbation work by Xie and Ocker [S4] is related context, not a reproduced implementation.

EXP-005 retained a tuned K6−K4 advantage of +3.78 [2.39,5.27] points after update-scale controls (98.75%, 32 blocks). Its lower bound does not establish a benefit greater than three points. The tuned and slow-matched contrasts coincide and are not independent replications. More repeatable noisy responses and broader participation are candidates rather than uniquely established mediators.

EXP-006's persistent-memory assay gave K6 78.74% retention versus K4 71.14%, a +7.60 [4.68,10.43]-point effect at sixteen similar pairs (98.75%, 32 blocks). Immediate K6 acquisition was 98.65%; the loss of old associations therefore coexisted with successful initial learning. Direct input retained 85.88% with fewer learned weights. Mean-based certification extended through eight tested pairs for K6 and sixteen for direct input, not to every individual memory. No biological memory capacity follows from those thresholds.

<!-- PAGE -->
## S6 Provenance and reproducibility boundaries

The accompanying input manifest records SHA-256 values for the exact compact evidence used in the figures. Source-number CSVs preserve numerical precision, keys, endpoints, independent units and original interval levels. Numerical checks recompute paired B/C intervals from all saved confirmation summaries, rather than subtracting independent confidence limits. Primary calibration bootstrap intervals are retained from the original analyses; no new scientific samples are created. The report build does not rerun training, alter selections or extend any confirmation sample.

The source archive and raw NPZ simulations remain local. For adult anatomy, the exact export is exported-traced-adjacencies-v1.1.tar.gz with SHA-256 7ac603698db356c72c20712d82b07f9da74e19c5adfec218c84b12f1d0c07409. The monoglomerular annotation has SHA-256 fe3b9b46b694a4c0690527fc5f113c50f2461e07e4198bb9c3aa8f37b87ee1fb at the pinned revision in S3. The package includes a provenance record and acquisition links, rather than redistributing upstream bulk data. Exact current source and artifact hashes, schema checks and known historical snapshot differences are recorded separately from scientific interpretation.

No independent scientific reviewer has evaluated this report. Earlier equation checks and deterministic replays were automated self-audits. A used a supplied fitted network whose regeneration is unresolved. B/C source freezes and block records are local prospective records; C preservation excluded older bulk archives from its scoped reread. Historical, subsequently edited prose hashes describe their original snapshot, not necessarily the current bytes. The versioned record checker preserves the legacy checker and does not label checksum agreement as scientific replication.

Literature verification is targeted rather than systematic. The report uses published primary anatomical and modeling sources and the inspected preprint versions for related continual-learning work. Fly-CL v2, dated 2 March 2026, supersedes the earlier draft's v1 citation for the method description; the arXiv record identifies ICLR 2026 acceptance. Publisher access to some older sources was intermittent, and Robins is used only for the established rehearsal precedent with full-method access limitations disclosed. The archived source audit supports the detailed compensation implementation mapping. Citation completeness does not independently validate the computational measurements.

## Supplementary references

[S1] Hallem EA, Carlson JR. Coding of odors by a receptor repertoire. *Cell*. 2006;125:143–160. [doi:10.1016/j.cell.2006.01.050](https://doi.org/10.1016/j.cell.2006.01.050).

[S2] Olsen SR, Bhandawat V, Wilson RI. Divisive normalization in olfactory population codes. *Neuron*. 2010;66:287–299. [doi:10.1016/j.neuron.2010.04.009](https://doi.org/10.1016/j.neuron.2010.04.009).

[S3] Bhandawat V, Olsen SR, Gouwens NW, Schlief ML, Wilson RI. Sensory processing in the Drosophila antennal lobe increases reliability and separability of ensemble odor representations. *Nature Neuroscience*. 2007;10:1474–1482. [Author publication record](https://wilson.hms.harvard.edu/publications/sensory-processing-drosophila-antennal-lobe-increases-reliability-and).

[S4] Xie K, Ocker GK. The Impact of Structural Changes on Learning Capacity in the Fly Olfactory Neural Circuit. *arXiv preprint*. 2025. [arXiv:2509.19351v1](https://arxiv.org/abs/2509.19351v1).
