# Synthetic CETT and token-region audit — 2026-09-23

Scope: local preparation only. No model download, paid runtime, empirical claim or public release. Pinned upstream remains unmodified at 53aff9e0b4cb6f83d3285cd46006b2e001dae30a. Tests execute selected exact AST definitions/location loop from its hash-verified extract_activations.py without importing Transformers or running main.

## Confirmed

- CETT uses down_proj inputs, absolute values (default), per-column weight norms (default), and division by the down_proj output norm plus 1e-8. The helper matches the pinned arithmetic exactly on float32 and bfloat16 synthetic tensors, all four flag combinations and batch-one squeeze. A tiny linear layer separately exercises actual upstream hooks, weight-column norms and clear().
- Feature tensors are [layer, token, neuron]. Mean/max aggregate the token axis.
- Source answer matching normalizes leading-space markers, then uses the first exact decoded-token-list match. Empty or unmatched answers return None. This is tested with a synthetic tokenizer, not evidence that Llama token boundaries are correct.
- Source output range excludes the final token by assumption; answer search can nevertheless match that token. Input/output boundaries depend on the user-only chat template length and remain unverified for the real tokenizer.
- all_except_answer_tokens concatenates the full prefix and suffix, including prompt and terminal token. Its comment says within output, but the executable code does not. The helper deliberately preserves full-sequence complement for comparison; no alternate scientific definition is silently selected.

## Reproduced defect

For all_except_answer_tokens with no answer match, the pinned loop does not assign selected_cett or skip aggregation. Without a prior selection this is an unbound-variable error inside main (NameError in the isolated loop test); with a previous selection it silently reuses that tensor, potentially from another sample. The exact loop test demonstrates both cases. The new comparison helper rejects missing, empty and out-of-bounds regions and empty complements. This is an explicit defensive divergence, not upstream equivalence for invalid inputs.

## Evidence and limits

Seven new tests; 61 tests total pass. One initial assertion required float32-appropriate tolerance (2.400000095 vs 2.4); the tensor formula equivalence comparisons remain exact. Tiny synthetic values do not prove numerical safety on a real model, multi-device ordering, batched extraction, or actual tokenization. No empirical extractor/runner is declared ready.

Next bounded task: add a source-example eligibility and token-region preflight contract that records missing/ambiguous matches, prompt/EOS assumptions and explicit exclusion reasons before extraction; preserve cohort denominators and split identities. Real tokenizer/model revisions, C-grid, dataset pins and statistical estimator remain open.
