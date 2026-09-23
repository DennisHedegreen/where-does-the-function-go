# M1 source review — 2026-09-22

Official upstream: https://github.com/thunlp/H-Neurons
Pinned commit: `53aff9e0b4cb6f83d3285cd46006b2e001dae30a`.
A read-only shallow clone was inspected. Selected unmodified source files and MIT license are retained under upstream/h-neurons; per-file SHA-256 in upstream/h-neurons.lock.json. No upstream model, API or training program was executed. Upstream's bundled dataset/examples were downloaded with the clone to /tmp, but were not imported as WDFG scientific data.

## Observed implementation contract

- classifier.py flattens each per-example [layer, neuron] NumPy activation matrix in row-major order. `f` answer records have positive label 1; `t` answer records label 0. In 3-vs-1, both t/f non-answer records receive label 0.
- LogisticRegression is configured from penalty/C/solver arguments, with max_iter=1000 and random_state=42. CLI defaults include l1, C=1 and liblinear; these are not a complete experimental freeze.
- README describes a C search optimizing held-out classifier accuracy plus downstream TriviaQA performance. Exact grid and split-selection procedure are not specified in the retained code. Do not replace this with C=1.
- No StandardScaler is present in classifier.py. CETT extraction has its own normalization: absolute intermediate activation, optionally weight-column norm, divided by down-projection output norm plus 1e-8, aggregated over selected tokens. Runtime tolerance is inherited from an unpinned scikit-learn version. requirements.txt does not pin versions.
- Upstream coordinate selection uses positive weights (>0); protocol adds coefficient sensitivity thresholds. Adapter preserves both flags, using >threshold for the latter. Confirm this strict comparator against the original experimental configuration before empirical use; no threshold-boundary result is claimed here.
- README recommends activation modulation; intervene_model.py also includes an in-place weight-scaling helper. That helper is **not** the WDFG persistent mask and is not invoked. M2 must implement the paper's down_proj input hook.
- The all_except_answer_tokens code concatenates all prefix/suffix tokens around the answer, including prompt context despite a nearby output-only comment; missing answer regions also need explicit handling. Do not silently fix/reinterpret this during replication. Freeze the exact feature-construction rule with source comparison before P1.
- Source loader silently skips missing activation files. A result-bearing WDFG adapter must instead audit completeness and eligibility. Current adapter normalizes supplied JSON matrices only; it is not a complete upstream runner.

## Validated now

Coordinate mapping and positive-weight selection agree with the exact pinned upstream function on a synthetic matrix, including zero/negative and protocol-boundary weights. Protocol-threshold selection, finite values and shape checks have separate tests. This is format/function equivalence only, not CETT or classifier-training equivalence.

Pure Gate 0 scoring enforces the four published comparisons with decimal arithmetic at the boundaries. Confidence intervals must declare paired methods; actual resampling is deferred until a frozen statistical design exists. Exactly 10% damage fails strict <10% without asserting the unspecified ambiguous boundary interpretation. >10% is damage-confounded/AMBIGUOUS.

## Still open before P1

C grid and source selection procedure; scikit-learn/runtime pins and tolerance; model/tokenizer revisions; dataset licenses/releases, sampling/eligibility and exact feature-region behavior; real source-generated activation/classifier fixtures; complete model and data provenance; paired statistical estimators and sample denominators. M1 does not close these by inference.
