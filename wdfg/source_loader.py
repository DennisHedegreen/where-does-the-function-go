"""Strict activation intake audit; no classifier fitting or empirical gate scoring."""
import hashlib
import io
import re
from pathlib import Path

import numpy as np

from .m1 import fingerprint, verify_upstream
from .validation import Invalid


def load_activations(id_map, answer_dir, other_dir=None, *, mode, expected_shape):
    """Return source-ordered features plus an auditable completeness receipt.

    Require every declared file. Unlike upstream, never silently reduce the cohort.
    IDs must be unique across f/t. Repeated question IDs across answer/other regions
    are intentional. expected_shape is the explicitly declared (layers, neurons).
    """
    source = verify_upstream()
    if mode not in ('1-vs-1', '3-vs-1'):
        raise Invalid('Unknown classification mode')
    if (not isinstance(expected_shape, (list, tuple)) or len(expected_shape) != 2
            or any(type(n) is not int or n <= 0 for n in expected_shape)):
        raise Invalid('Explicit positive layer/neuron shape required')
    if not isinstance(id_map, dict) or set(id_map) != {'f', 't'}:
        raise Invalid('Exactly f/t ID lists required')
    seen = set()
    for group in ('f', 't'):
        if not isinstance(id_map[group], list) or not id_map[group]:
            raise Invalid('Both label groups must be nonempty lists')
        for raw in id_map[group]:
            if type(raw) not in (str, int) or not re.fullmatch(r'[A-Za-z0-9_-]+', str(raw)):
                raise Invalid('Unsafe or invalid example ID')
            qid = str(raw)
            if qid in seen:
                raise Invalid('Duplicate or overlapping example ID')
            seen.add(qid)
    if mode == '3-vs-1' and other_dir is None:
        raise Invalid('Other-token directory required')
    groups = [('answer', 'f', 1, answer_dir), ('answer', 't', 0, answer_dir)]
    if mode == '3-vs-1':
        if Path(answer_dir).resolve() == Path(other_dir).resolve():
            raise Invalid('Answer and other-token directories must differ')
        groups += [('other', 't', 0, other_dir), ('other', 'f', 0, other_dir)]
    rows, labels, records, missing = [], [], [], []
    for region, group, label, directory in groups:
        root = Path(directory).resolve()
        for raw in id_map[group]:
            qid = str(raw)
            path = root / f'act_{qid}.npy'
            if not path.resolve().is_relative_to(root):
                raise Invalid('Activation path escapes its directory')
            if not path.is_file():
                missing.append(f'{region}/{path.name}')
                continue
            data = path.read_bytes()
            try:
                matrix = np.load(io.BytesIO(data), allow_pickle=False)
            except (ValueError, OSError, EOFError) as exc:
                raise Invalid(f'Unreadable activation: {region}/{path.name}') from exc
            if not isinstance(matrix, np.ndarray):
                matrix.close()
                raise Invalid('Expected NPY matrix, not archive')
            if (matrix.shape != tuple(expected_shape) or matrix.dtype.kind not in 'fiu'
                    or not np.isfinite(matrix).all()):
                raise Invalid(f'Invalid activation shape/type/value: {region}/{path.name}')
            rows.append(matrix.flatten(order='C'))
            labels.append(label)
            records.append({'example_id': qid, 'region': region, 'label': label,
                            'sha256': hashlib.sha256(data).hexdigest(), 'dtype': str(matrix.dtype)})
    if missing:
        raise Invalid('Missing declared activations: ' + ', '.join(missing))
    receipt = {'mode': mode, 'shape': list(expected_shape), 'feature_order': 'layer-major-C',
               'source_commit': source['commit'], 'records': records,
               'rows': len(records), 'scientific_status': 'NOT_EVALUATED',
               'execution_authorized': False}
    receipt['audit_sha256'] = fingerprint(receipt)
    return np.array(rows), np.array(labels), receipt
