# Where Does the Function Go?

Pre-results research software for testing whether a language-model function can recover under a persistent constraint, and how to distinguish existing backup routes from training-dependent change.

**Status: experimental scaffolding. The research hypothesis has not been tested by this repository.** The CPU fixture suite covers M0–M3 and synthetic source-intake audits. A passing fixture is not successful H-Neuron replication, a real Gate 0 pass, a validated CoAx benchmark, or evidence of functional reconstitution.

By Dennis Hedegreen, Hedegreen Research.

- [Companion article — Article 200](https://hedegreenresearch.com/articles/where-does-the-function-go/)
- [Working paper — Camelot MI-001 v0.8, frozen scientific baseline](https://hedegreenresearch.com/assets/camelot/reports/model-internals/where-does-the-function-go/model-internals__intl__2026-09__i001__v0-8__draft.pdf)
- [Current paper — v0.9 documentation revision](https://hedegreenresearch.com/assets/camelot/reports/model-internals/where-does-the-function-go/model-internals__intl__2026-09__i001__v0-9__draft.pdf)
- [Protocol and unresolved decisions](protocol/README.md)
- [Methods and implementation limits](docs/METHOD.md)
- [RunPod preparation](docs/RUNPOD.md)

## What is implemented

| Component | Tested locally | Still required for research |
|---|---|---|
| M0 provenance | Pinned source hashes, configuration validation, fixture/result separation | Full empirical run manifests and runtime lock |
| M1 source adapter | Layer-major output normalization, upstream coordinate-function agreement, split checks, Gate 0 rules | Full CETT/probe replication and frozen statistical estimators |
| M2 persistent mask | Gated-MLP input hook, gradient behavior, checkpoint reload, write-once t0 | Target Llama architecture/runtime and real phenotype checks |
| M3 backup audit | Paired-count effects, supplied interval/power checks, nested pools, conservative label logic | CoAx reference replication, actual power/CI estimation and candidate-pool design |

The CPU suite contains **68 tests**. No model weights or benchmark datasets are included. Commands do not launch training, call a judge API, start a cloud machine, or purchase compute.

## Source-intake audits

The local preparation layer now checks complete activation-file intake and layer-major feature order against the pinned upstream loader. Missing files fail instead of silently shrinking the cohort. Synthetic CETT tests exercise upstream hooks and arithmetic in float32/bfloat16. An exact source-loop test reproduces stale-data reuse when a complementary answer region is missing; our helper rejects that case.

The provisional eligibility preflight retains exclusion reasons and per-split denominators, rejects ID/prompt leakage, and flags repeated or out-of-output matches. It accepts synthetic data only. These helpers are Python APIs, not a complete empirical extraction command.

- [CETT and token-region audit](docs/CETT-REGION-AUDIT.md)
- [Provisional eligibility contract](docs/ELIGIBILITY-CONTRACT.md)
- [Observed model/dataset revisions and open access questions](docs/REGISTRY-REVIEW.md)

Observed registry revisions do not imply approved dataset choices or authenticated model access. RunPod has not been provisioned or validated.

## Quick start — CPU fixtures

Python 3.12 is the tested environment. Run from a clean checkout:

```bash
git clone https://github.com/DennisHedegreen/where-does-the-function-go.git
cd where-does-the-function-go
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-cpu.txt
python -m pip install --no-deps .
python -m unittest discover -s tests -v
```

PyTorch in `requirements-cpu.txt` is explicitly CPU-only. These pins describe the fixture environment; they are not a validated CUDA environment for the full experiment. For provenance/Gate 0/backup validators alone, installing this package supplies jsonschema; NumPy is needed for activation intake/source-equivalence tests and PyTorch for M2 and CETT helpers.

```bash
wdfg verify-package protocol
wdfg verify-upstream
wdfg validate-config configs/fixture-p1.json --package protocol
wdfg gate0-fixture fixtures/gate0-pass.json
wdfg fingerprint-dataset fixtures/dataset.json --preprocessing-version nfc-crlf-v1
wdfg backup-fixture fixtures/backup-near-null.json
```

Exit code 0 means the requested validation completed; 2 means invalid input. Read the JSON: `scientific_status: NOT_EVALUATED` and `execution_authorized: false` remain explicit. A fixture outcome of PASS does not authorize an empirical run.

## Research question and decision boundary

The protocol separates an initial selective causal effect, phenotype loss under a persistent mask, training-dependent recovery, replacement change relative to time zero, and selective dependence on the replacement (R0–R4). A conditional backup audit (B0) constrains the interpretation. Recovery alone cannot establish a newly reconstituted function.

The strongest proposed interpretation additionally requires powered near-null time-zero evidence, pool-expansion sensitivity and cross-seed replication. Weak/strong backup cutoffs and several experimental choices remain open. See the frozen [implementation contract](protocol/PROTOCOL_CONTRACT.md) and [freeze register](protocol/FREEZE_REGISTER.md).

## Next research gate

Resolve upstream H-Neuron configuration and source-generated fixtures, model/tokenizer and dataset revisions, judging/answer-token provenance, confidence-interval and power methods, then perform a bounded hardware/runtime benchmark. RunPod is the planned execution platform; this repository has not yet been validated there.

## Reproducibility and contributions

[Source review](M1-SOURCE-REVIEW.md) records the pinned H-Neurons commit and discrepancies. The archived protocol subset has a deliberately separate manifest from the original private editorial handoff; its paper PDF is unchanged. Historical local receipts are not shipped as public validation evidence.

Use issues for reproducible bugs or methodological criticism. Include the commit, environment, command and smallest non-sensitive fixture. Changes to scientific thresholds require a versioned protocol decision before result-bearing runs, not a quiet patch after seeing outcomes. See [CONTRIBUTING.md](CONTRIBUTING.md).

Original code and new repository documentation: MIT. Upstream excerpts retain their MIT notices. Archived paper/article sources retain their original rights; see [NOTICE.md](NOTICE.md). See [CITATION.cff](CITATION.cff) for the software citation.
