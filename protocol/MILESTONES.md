# Bounded implementation sequence

These M labels are engineering milestones defined by handoff v0.2. P1–P4 remain the paper's empirical stages. No M milestone has been implemented by creating this handoff.

| Milestone | Deliverable | Local acceptance | Does not establish |
|---|---|---|---|
| M0 | Dedicated implementation room, README, dependency strategy, source/manifest verification, schema skeleton and configuration validator | Snapshot verification; missing scientific values rejected; fixture vs empirical mode enforced | Replication, source-adapter equivalence or model capability |
| M1 | Pinned H-Neurons adapter contract, split/fingerprint logic, normalized output fixtures, pure Gate 0 evaluator | Deterministic fixtures, correct effect units/signs, boundaries, missing-evidence rejection | Real H-Neuron replication or Gate 0 PASS |
| M2 | Persistent-mask implementation and t0 artifact writer | Small CPU architecture fixture: identity, intended zeros, gradient path, train/reload persistence, immutable baseline | Compatibility with untested 8B runtime or scientific phenotype loss |
| M3 | Conditional backup/power/pool-expansion audit plumbing and receipts | Paired synthetic fixtures, low-power unresolved state, immutable t0/pool IDs and fail-closed claim classifier | B0-A in the target model or successful CoAx benchmark |

Each milestone has its own reviewable changes and receipt. Do not bundle P3, C2C, training or deployment into M0. Benchmark physical feasibility separately; synthetic CPU evidence is always non-result-bearing.

## First build instruction: M0

Use the existing ecosystem without reorganizing public/editorial paths. Create a dedicated implementation directory only after checking for an existing owner. Keep this work pack as protocol provenance. A standalone clean git checkout is appropriate for later result-bearing runs because the broad Hedegreen workspace contains unrelated work; never clean/reset it to satisfy the paper's clean-tree criterion.

Implement source-manifest verification, config schema and run-manifest schema with explicit run_kind = fixture | pilot | result, protocol digest and open-freeze status. Test missing inputs, tampered artifacts and rejected escalation from fixtures to results. Add a minimal CLI that validates configuration and provenance without loading models or running inference. Report what is runnable, what was tested and the exact remaining scientific freezes. Stop at the M0 receipt.

## Empirical stages later

P1 real replication + selective Gate 0 → P2 real persistent mask/t0 + conditional backup validation → P3 separately gated recoverability collection/analysis. P4 short adaptation throughput/memory benchmark only after Gate 0/B0 prerequisites. Main adaptation follows external technical review, explicit freeze and resource decision. Optional C2C follows its own controls. No estimated GPU-hours are invented here.
