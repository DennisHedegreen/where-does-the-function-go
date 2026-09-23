# Implementation boundaries

The software is scaffolding for the published pre-results protocol. It does not establish any model's capacities or any result about consciousness.

The source baseline is Article 200 v1.1 and Camelot MI-001 v0.8. v0.8 corrected a figure layout; scientific requirements are the v0.7 protocol. Later repository-link revisions should not silently change that baseline.

## M1

`normalize_h_neurons` accepts a reviewed JSON export of layer-major CETT values and flattened classifier weights. It preserves both the upstream positive-weight flag and the protocol sensitivity-threshold flag. Tests compare the pinned upstream coordinate function, loader and CETT/token-region functions on synthetic fixtures; no full classifier-training or model extraction run has occurred. No arbitrary pickle model is loaded. `dataset_fingerprint` preserves whitespace except CRLF normalization, applies Unicode NFC, sorts by example ID, and includes split, labels, parameters and preprocessing version. It detects exact ID/prompt leakage, not semantic duplicates.

Gate 0 fixture inputs contain supplied paired intervals; M1 does not estimate them. The scorer checks 8 pp identification advantage, 5 pp causal phenotype reduction, 3 pp selectivity and strictly less than 10% relative perplexity damage. All are screening rules from the protocol, not proof of the hypothesis.

## M2

`PersistentMask` applies a fixed buffer at the input to down_proj. Use its audited `forward` entry point. It verifies hook presence, selected-layer execution and unchanged mask buffers. Save/restore rebuilds hooks before strict tensor loading. It does not support or claim compatibility with torch.compile, distributed/quantized models or arbitrary hooks that later alter activations.

`write_t0` refuses an existing file and returns a digest to retain separately. `verify_t0` checks against that digest. The filesystem owner can still change files; this is write-once application behavior plus tamper detection, not tamper-proof storage. Local fixture checkpoints use PyTorch tensors/primitives with weights_only=True; they are not canonical scientific serialization.

## M3

The paired risk difference is calculated from paired binary counts. Confidence intervals and power are supplied fixture receipts, not computed or empirically verified. Margin: min(0.02, 0.20 × R1 loss); the 90% interval must lie strictly inside it and declared power must be at least 80%. Nested predeclared pools and reference-validation declarations are checked. This is not a CoAx implementation. Every output remains fixture/NOT_EVALUATED.

Current source uncertainties include the exact upstream C grid, sklearn/tolerance/runtime pins, feature-region interpretation, source loader's missing-file behavior, model/data access and exact statistical estimators. The pilot appendix says 300 examples while the amended main text says 400; the handoff explicitly follows the main text (400 eligible per set where available). No empirical run is allowed by fixture checks.

## Source-intake preparation

`source_loader.load_activations` requires explicit layer/neuron shape and all declared NPY files. It preserves upstream row/label order in both modes while rejecting unsafe IDs, duplicate IDs, region-directory aliasing, nonfinite values and shape mismatches. Receipts bind file bytes, ordering and source commit; they are not empirical gates.

`cett_audit` compares the pinned arithmetic and full-sequence complement semantics. `eligibility.preflight` uses a provisional unique-match policy rather than upstream first-match selection and accepts synthetic inputs only. Caller-declared token boundaries are not independent tokenizer verification. See the dedicated audit documents for failures reproduced in the original code and remaining limitations.
