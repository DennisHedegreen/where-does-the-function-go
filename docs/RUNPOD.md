# RunPod: preparation and bounded smoke test

RunPod is the planned model-execution platform. No Pod has been launched or tested for this project. The complete empirical P1 pipeline is not yet executable; do not rent a long-running GPU merely to run the CPU fixtures.

## Before provisioning

Resolve model access and exact revision, dataset versions/licenses, source probe settings, judging method, and the remaining protocol freezes. Choose a CUDA image and GPU only after checking compatibility with the frozen runtime. Record its image digest, GPU, driver, CUDA and PyTorch versions. No GPU-hour or cost estimate is yet established.

Eight billion parameters at two bytes each imply roughly 16 GB of weights alone, before caches/activations/runtime. This arithmetic is not a VRAM guarantee or disk-size recommendation. Measure actual one-batch memory, time and artifact growth before selecting the full run size. Quantizing the model changes the experimental configuration and cannot silently replace the selected model.

## Storage

Keep the checkout and research artifacts under the configured persistent storage mount, ordinarily `/workspace`. Container disk is temporary. Volume disk is tied to the Pod; a network volume persists independently. Verify which storage was selected before stopping or terminating a Pod, and keep an independent copy of critical results. Official documentation: https://docs.runpod.io/pods/storage/types and https://docs.runpod.io/pods/manage-pods (checked 2026-09-23).

## Once a Pod has been deliberately provisioned

```bash
cd /workspace
git clone https://github.com/DennisHedegreen/where-does-the-function-go.git
cd where-does-the-function-go
git rev-parse HEAD
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-cpu.txt
python -m pip install --no-deps .
python -m unittest discover -s tests -v
wdfg verify-package protocol
```

This runs **CPU fixture validation only**, even on a GPU Pod. Use a separate environment for the future CUDA experiment; do not install this CPU torch pin over the chosen CUDA runtime. Never place access tokens in committed config files or logs.

## Future empirical smoke test checklist

The following is a plan, not an existing runnable command: verify source/data/model hashes; load the exact model; audit identity and mask behavior on one batch; measure peak GPU memory, throughput and output size; record failures and the runtime; export a receipt. Only then size the predeclared P1 run. No placeholder command pretends that this runner exists.
