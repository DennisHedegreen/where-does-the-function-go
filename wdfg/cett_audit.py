"""Synthetic CETT comparison helpers; not a frozen empirical extractor."""
import torch
from .validation import Invalid


def cett(activations, output_norms, weight_norms, *, use_abs=True, use_mag=True):
    """Declared shapes: [layers,tokens,neurons], [layers,tokens,1], [layers,neurons]."""
    if activations.ndim != 3 or any(n == 0 for n in activations.shape):
        raise Invalid('Nonempty layer/token/neuron tensor required')
    layers, tokens, neurons = activations.shape
    if output_norms.shape != (layers, tokens, 1) or weight_norms.shape != (layers, neurons):
        raise Invalid('CETT shape mismatch')
    tensors = (activations, output_norms, weight_norms)
    if any(not t.is_floating_point() or not torch.isfinite(t).all() for t in tensors):
        raise Invalid('Finite floating tensors required')
    if any(t.device != activations.device or t.dtype != activations.dtype for t in tensors):
        raise Invalid('Explicit common dtype/device required')
    if (output_norms < 0).any() or (weight_norms < 0).any():
        raise Invalid('Norms cannot be negative')
    values = activations.abs() if use_abs else activations
    if use_mag:
        values = values * weight_norms[:, None, :]
    result = values / (output_norms + 1e-8)
    if not torch.isfinite(result).all():
        raise Invalid('Nonfinite CETT output')
    return result


def aggregate_region(values, region, *, complement=False, method='mean'):
    """Complement deliberately means full sequence, as implemented upstream.

    Missing/empty regions are rejected instead of skipped or reusing stale values.
    Tokenizer-dependent region discovery is NOT reimplemented here.
    """
    if values.ndim != 3 or not torch.isfinite(values).all():
        raise Invalid('Finite layer/token/neuron tensor required')
    if method not in ('mean', 'max'):
        raise Invalid('Unknown aggregation')
    if (not isinstance(region, (tuple, list)) or len(region) != 2
            or any(type(n) is not int for n in region)):
        raise Invalid('Explicit token region required')
    start, end = region
    if not 0 <= start < end <= values.shape[1]:
        raise Invalid('Empty or out-of-range token region')
    selected = torch.cat((values[:, :start, :], values[:, end:, :]), dim=1) if complement else values[:, start:end, :]
    if selected.shape[1] == 0:
        raise Invalid('Empty complementary region')
    return selected.mean(dim=1) if method == 'mean' else selected.max(dim=1).values
