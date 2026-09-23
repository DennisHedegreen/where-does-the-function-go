# Source-example preflight — 2026-09-23

Implementation: wdfg/eligibility.py. This is a provisional synthetic-only contract, not an approved empirical selection policy. It does not tokenize, load models or authorize execution.

Input preserves example ID, split, prompt, individual decoded full-sequence tokens, annotated answer tokens, declared half-open output bounds and explicit boundary-verification state. Duplicate IDs or NFC/CRLF-normalized prompt overlap across splits block the whole cohort. Invalid structural data also block it.

Every structurally valid example remains in the receipt, including exclusions. Per-split and total declared/eligible/excluded denominators are retained. Empty answers, missing matches, ambiguous matches, matches outside output, invalid output bounds and unverified bounds have explicit reason codes. Matches and input fingerprints are retained; only a unique in-range match with verified bounds receives a selected region. Leading-space markers follow pinned upstream normalization. Search extends to sequence end to expose the upstream terminal-token discrepancy.

Differences from upstream are explicit: repeated in-output matches are flagged instead of silently selecting the first; out-of-output matches are rejected. These provisional rules must be reviewed before any empirical cohort freeze. The caller-supplied boundary flag is not proof of real tokenizer verification. No eligibility count is a research result.

Seven new regression tests cover retained denominators, ambiguity, terminal/cross-boundary matches, missing/empty/unverified regions, identity/leakage, provenance hashes, malformed input and empirical refusal. All 68 tests pass locally.

Next: read-only model/tokenizer and dataset registry inspection to establish actual revisions, access conditions and source configurations. Do not download model weights or provision a Pod. Revisit remaining C-grid/runtime choices before declaring a runnable P1 plan.
