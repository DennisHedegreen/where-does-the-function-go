# Protocol-to-code contract

Source anchors refer to labels in sources/protocol/sections/body.tex; original appendix remains under sources/protocol/appendices/. Full source governs details omitted here.

## P1: replication before novelty

Anchors: identification---pilot-lock; controls---pilot-lock; gate-0---pilot-gono-go-rule; sparse-probe-stability.

Use the pinned official H-Neurons pipeline, including CETT answer-token features, sparse L1 probe solver, regularization grid, scaling, tolerance and software versions. Never substitute a convenient fixed C. Identification: TriviaQA; OOD NQ-Open/BioASQ; NonExist diagnostic. Deterministic eligible sample: 400 where available, otherwise all; sampling seed 42; replication generation seeds 314 and 2718 in addition to 42 where applicable. Coefficient thresholds 0.0005/0.001/0.002, primary 0.001. Report at least ten refits where feasible, selection frequencies/Jaccard and causal-mask reproducibility; no invented Jaccard gate.

Controls: baseline, sham, matched-count random, same-layer non-H, contribution-matched non-H, alpha=0.5 H suppression, alpha=0 hard suppression, fixed held-out LM corpus for perplexity. Identical instrumentation across conditions.

Gate 0 is a compute-screening gate, not proof of mechanism identity:
- A: held-out TriviaQA advantage ≥0.08 with paired 95% CI excluding zero; advantage positive on NQ-Open and BioASQ.
- B: FaithEval Counterfactual Context compliance reduction ≥0.05 versus baseline.
- C: reduction exceeds contribution-matched non-H by ≥0.03, stratified bootstrap 95% CI excluding zero.
- D: relative perplexity increase <0.10. Damage-confounded findings cannot pass.

Store inputs, effect directions, denominators, per-seed results and intervals. Missing evidence yields unresolved/incomplete validation, never a pass. Separate software/data-integrity failure from scientific gate failure. Numerical comparisons use proportions, not ambiguous percent units.

## P2: persistent mask and conditional backup

Anchors: pilot-b0---persistent-mask-integrity; experiment-c-distinguishing-redundancy-from-reconstitution; conditional-backup-discovery; conditional-backup-equivalence.

Mask the input of each selected Llama MLP down_proj (post activation-gate multiplication). Do not zero weight entries as a substitute. Validate architecture, layer/index bounds, tensor broadcasting, dtype/device, identity equivalence, targeted zeros (absolute tolerance ≤1e-7), and persistence across training and checkpoint reload. torch.compile disabled for pilot. Any bypass makes the mask audit fail.

Create immutable pre-adaptation t0 records under the persistent H mask: candidate locus/group/direction ID, predictive signal, marginal and conditional causal effects, contribution statistics and matched rank. Bind to model revision, mask hash, dataset/split hash and run ID. Development overwrite creates a new explicitly non-result-bearing record; never destroys the only baseline.

CoAx conditional co-ablation must validate against the reference GPT-2-small IOI backup-recovery benchmark, with acceptance tolerance frozen in advance. For target-model bounded pools, predefine selection/grouping and expansion sizes, then report classification sensitivity. A successful reference replication does not prove completeness of the target pool.

B0-A near-null requires paired conditional causal risk difference 90% CI wholly inside [-delta,+delta], delta=min(0.02,0.20*abs(R1 loss)); ≥80% power under the paired design; candidate-pool expansion support. Inadequate power or unstable pool classification leaves B0 unresolved. No ordinary independent-samples t-test for paired binary outcomes. Freeze design before observing adaptation. Weak/strong boundaries are not supplied as invented numeric defaults.

B0-B: non-negligible limited backup → potential adaptive amplification. B0-C: strong existing backup → self-repair. R0 selective initial contribution; R1 loss before adaptation; R2 recovery relative to masked no-training controls; R3 change relative to the same candidate's t0 baseline; R4 selective causal dependence beyond matched controls. Strong near-null reconstitution requires B0-A plus R0–R4 and cross-seed replication. Preserve the evidence matrix even when no label is available.

## P3: recoverability

Anchors: counterfactual-i0b-minimum-one-token; recoverability-precision-analysis; held-out-causal-intervention.

Store exact pre-stop token prefix, prompt/token IDs, natural trajectory, EOS ID/probability, top-1 token, logits hash when retained and residual pointer. Recompute integrity before continuation; top-1 must match and EOS difference meet the explicitly frozen tolerance. Appendix's 1e-4 is suggested, not silently accepted as frozen. Integrity failures are excluded and counted.

Four distinct regime IDs must exist in config, schema, CLI, artifacts and scoring:
- I0: natural support from exact prefix, EOS allowed; immediate EOS is non-rescue.
- I0b: suppress EOS exactly one generated token, then restore it; other settings match I0.
- I1: forced compute for a configured window; secondary.
- I2: versioned procedural recheck instruction, no new facts; robustness.

Never pool regime outcomes. Seeds derive from example/regime/k identity, independent of worker order. Record parse failures separately; use last post-continuation FINAL parse. Separate discovery, tuning and confirmatory causal-test splits.

K is open. Simulate 8/16/32; select smallest meeting held-out mean NLL Monte Carlo SE ≤0.01 and <20% change in estimated SE when doubling K; extend grid if necessary. Freeze simulation, assumptions and K before P3. Primary score: held-out continuation-level Bernoulli or hierarchical/binomial NLL/deviance, account for example dependence; include difficulty covariates and out-of-band validation. K=8 is not an implicit default.

## Downstream work

H↔J controls must include contribution-matched non-H, random same-layer, norm/effect and isotropic residual-direction controls with matched norm; reverse tests include random-J/non-J/shuffle. J-lens is downstream of frozen trajectory collection; J screen remains open.

Experiment G/C2C is optional and separate. Freeze a learned fuser trained on disjoint data; compare receiver-only, text and cache communication, shuffled/wrong-source controls. Receiver B's success does not establish source A's recoverability; KV cache is not equated to J-space.

Main adaptation requires Gate 0, mask audit, throughput/memory benchmark and external technical review addressing adaptation breadth, then explicit hyperparameter freeze. LoRA-only smoke results retain COMPENSATION-IN-PERMITTED-SUBSPACE status. CPU fixture passes establish software behavior only.
