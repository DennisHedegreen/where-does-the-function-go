"""Persistent down-projection input masking and write-once fixture t0 records."""
import hashlib
import json
import os
from pathlib import Path
import torch
from .m1 import canonical, fingerprint
from .validation import Invalid, read_json

class PersistentMask:
    """Hooks are reconstructed from a manifest; buffers alone are not hooks."""
    def __init__(self, model, coordinates):
        self.model = model
        self.handles = []
        self.targets = []
        self.calls = {}
        self.coordinates = {}
        try:
            layers = model.model.layers
        except AttributeError as exc:
            raise Invalid('Expected model.model.layers') from exc
        # Validate the complete specification before changing any module.
        plan = []
        for layer, indices in sorted(coordinates.items()):
            if type(layer) is not int or not 0 <= layer < len(layers):
                raise Invalid('Layer outside model contract')
            mlp = layers[layer].mlp
            if not all(isinstance(getattr(mlp, name, None), torch.nn.Linear) for name in ('gate_proj','up_proj','down_proj')):
                raise Invalid('Expected gated MLP linear projections')
            width = mlp.down_proj.in_features
            if mlp.gate_proj.out_features != width or mlp.up_proj.out_features != width:
                raise Invalid('Inconsistent intermediate dimensions')
            if not isinstance(indices,list) or any(type(i) is not int or not 0 <= i < width for i in indices) or len(set(indices)) != len(indices):
                raise Invalid('Invalid or duplicate neuron coordinates')
            if hasattr(mlp.down_proj, '_wdfg_mask'):
                raise Invalid('Mask already installed')
            plan.append((layer, sorted(indices), mlp.down_proj))
        if not plan: raise Invalid('Explicit layer specification required, including identity controls')
        for layer, indices, target in plan:
            self.coordinates[layer] = indices
            mask = torch.ones(target.in_features, device=target.weight.device, dtype=target.weight.dtype)
            mask[indices] = 0
            target.register_buffer('_wdfg_mask', mask, persistent=True)
            self.calls[layer] = 0
            def hook(module, args, layer=layer, indices=indices):
                if len(args)!=1 or args[0].shape[-1] != module.in_features:
                    raise Invalid('Invalid down_proj input shape')
                self.assert_integrity()
                masked = args[0] * module._wdfg_mask
                if not torch.isfinite(masked).all(): raise Invalid('Non-finite masked activation')
                if indices and torch.any(masked[..., indices].detach().abs() > 1e-7):
                    raise Invalid('Mask activation audit failed')
                self.calls[layer] += 1
                return (masked,)
            handle = target.register_forward_pre_hook(hook)
            self.targets.append((layer, target, handle))
            self.handles.append(handle)

    def assert_integrity(self):
        for layer, target, handle in self.targets:
            expected = torch.ones_like(target._wdfg_mask)
            expected[self.coordinates[layer]] = 0
            if not torch.equal(target._wdfg_mask, expected):
                raise Invalid('Mask buffer changed')
            if handle.id not in target._forward_pre_hooks:
                raise Invalid('Persistent mask hook missing')

    def forward(self, *args, **kwargs):
        self.assert_integrity()
        before = self.calls.copy()
        output = self.model(*args, **kwargs)
        if any(self.calls[layer] == before[layer] for layer in before):
            raise Invalid('Target layer was bypassed')
        return output

    def save(self, path):
        self.assert_integrity()
        # No pickle object graphs are supplied: tensors + primitive specification only.
        payload = {'schema':'wdfg.mask-checkpoint/1','coordinates':self.coordinates,
                   'state_dict':self.model.state_dict()}
        with open(path,'xb') as f:
            torch.save(payload,f)
            f.flush(); os.fsync(f.fileno())

    @classmethod
    def restore(cls, fresh_model, path):
        payload = torch.load(path, map_location='cpu', weights_only=True)
        if payload.get('schema') != 'wdfg.mask-checkpoint/1': raise Invalid('Wrong checkpoint schema')
        controller = cls(fresh_model, payload['coordinates'])
        fresh_model.load_state_dict(payload['state_dict'], strict=True)
        controller.assert_integrity()
        return controller


def write_t0(path, *, records, lineage, development_parent=None):
    """Exclusive-create JSON; no overwrite flag. Development uses a new filename."""
    required = {'model_revision','mask_sha256','dataset_sha256','protocol_sha256','run_id'}
    if set(lineage)!=required or any(not isinstance(v,str) or not v.strip() for v in lineage.values()):
        raise Invalid('Complete t0 lineage required')
    for key in ('mask_sha256','dataset_sha256','protocol_sha256'):
        if len(lineage[key])!=64 or any(c not in '0123456789abcdef' for c in lineage[key]):
            raise Invalid('Invalid lineage digest')
    if not isinstance(records,list) or not records: raise Invalid('t0 records required')
    ids=[]
    fields={'candidate_id','predictive_score','marginal_effect','conditional_effect','contribution','matched_rank'}
    for r in records:
        if set(r)!=fields or not isinstance(r['candidate_id'],str) or not r['candidate_id']:
            raise Invalid('Invalid t0 candidate record')
        for k in fields-{'candidate_id','matched_rank'}:
            if type(r[k]) not in (int,float) or not __import__('math').isfinite(r[k]):raise Invalid('Finite t0 metrics required')
        if type(r['matched_rank']) is not int or r['matched_rank']<1:raise Invalid('Positive candidate rank required')
        ids.append(r['candidate_id'])
    if len(set(ids))!=len(ids):raise Invalid('Duplicate t0 candidate')
    payload={'schema':'wdfg.t0/1','run_kind':'fixture','scientific_status':'NOT_EVALUATED',
             'lineage':lineage,'records':sorted(records,key=lambda r:r['candidate_id']),
             'development_parent':development_parent}
    envelope={'payload':payload,'sha256':fingerprint(payload)}
    raw=canonical(envelope)+b'\n'
    with open(path,'xb') as f:
        f.write(raw); f.flush(); os.fsync(f.fileno())
    return envelope['sha256']

def verify_t0(path, expected_sha256):
    envelope=read_json(path)
    actual=fingerprint(envelope['payload'])
    if actual!=expected_sha256 or envelope['sha256']!=expected_sha256:
        raise Invalid('t0 digest mismatch')
    return envelope['payload']
