# Freeze register for implementation

“Fixed” here means stated in the published protocol, not empirically validated. Full original register is in sources/protocol/appendices/freeze_register.tex.

| Item | Current status / action | Required before |
|---|---|---|
| Article v1.1 / paper v0.8 | Snapshot + SHA captured; public state untouched | M0 |
| H identification/causal phenotype, thresholds and Gate 0 | Carry published values exactly; test units/boundaries | P1 |
| Model/tokenizer revision, upstream H-Neurons commit and complete probe pipeline | Resolve and pin; do not invent SHA | Result-bearing P1 |
| Dataset releases, eligibility, licenses, normalization, splits | Inspect and freeze fingerprints; no train/test overlap | Result-bearing P1 |
| Runtime/lockfile, deterministic tolerance, model hook compatibility | Verify on actual selected implementation | Result-bearing P1/P2 |
| CoAx source commit, reference fixture, acceptance tolerance | Open; pin then predeclare tolerance | Reference benchmark |
| Candidate-pool selection/expansion sizes, effect estimator, multiplicity policy | Open; define and freeze before target audit | Result-bearing B0 |
| B0 delta rule / paired CI / ≥80% power | Published rule fixed; estimator/power implementation and design assumptions require review | B0-A claim |
| B0 weak/strong cutoffs | Open; do not auto-label B/C using invented values | B0-B/C classification |
| Mask ≤1e-7 integrity | Published; verify inference, training and reload | P2/adaptation |
| I0/I0b/I1/I2 | Four distinct regimes fixed; version procedural instruction and decoding config | P3 |
| K and planned sample size / rescue-rate simulation | Open; simulate with explicit assumptions and freeze | P3 |
| Pre-stop tolerance, token budget B and decoding details | Must be explicitly set and justified | P3 |
| J screen | REVIEW-REOPENED | J-space claim |
| Optimizer/LR/tokens/checkpoint counts/seeds/parameter-freezing policy | MAIN-RUN-TBD after benchmark and external review | Main adaptation |
| R2/R3/R4 numeric thresholds | MAIN-RUN-TBD; freeze before outcome observation | Main adaptation |
| C2C architecture/fuser/data splits/control details | Deferred optional Experiment G | C2C run |

Any changed scientific choice needs date, reason, previous value, new value, affected stages, protocol version and human decision. No default values may fill scientific nulls. Hardware availability and actual cost are not established by this document.
