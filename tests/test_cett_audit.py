import ast
from types import SimpleNamespace
from typing import List, Dict, Optional, Tuple
import unittest
import torch
from wdfg.validation import ROOT, Invalid
from wdfg.m1 import verify_upstream
from wdfg.cett_audit import cett, aggregate_region


class CETTAuditTests(unittest.TestCase):
    def setUp(self):
        verify_upstream()
        self.path = ROOT / 'upstream/h-neurons/scripts/extract_activations.py'
        self.tree = ast.parse(self.path.read_text())
        nodes = [n for n in self.tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name in ('CETTManager', 'get_region_indices')]
        self.scope = dict(torch=torch, List=List, Dict=Dict, Optional=Optional, Tuple=Tuple)
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(self.path), 'exec'), self.scope)

    def test_exact_formula_flags_and_batch_one_squeeze(self):
        for dtype in [torch.float32, torch.bfloat16]:
            a = torch.arange(-12, 12, dtype=dtype).reshape(2, 3, 4)
            norms = torch.tensor([0, 2, 4, 1, 3, 5], dtype=dtype).reshape(2, 3, 1)
            weights = torch.arange(1, 9, dtype=dtype).reshape(2, 4)
            for absolute in [False, True]:
                for magnitude in [False, True]:
                    manager = object.__new__(self.scope['CETTManager'])
                    manager.model = SimpleNamespace(device='cpu')
                    manager.activations = [row.unsqueeze(0) for row in a]
                    manager.output_norms = [row.unsqueeze(0) for row in norms]
                    manager.weight_norms = weights
                    expected = manager.get_cett_tensor(absolute, magnitude)
                    torch.testing.assert_close(cett(a, norms, weights, use_abs=absolute, use_mag=magnitude), expected, rtol=0, atol=0)

    def test_hook_inputs_column_norms_and_clear(self):
        class Model(torch.nn.Module):
            device = 'cpu'
            def __init__(self):
                super().__init__()
                self.down_proj = torch.nn.Linear(3, 2, bias=False)
            def forward(self, x): return self.down_proj(x)
        model = Model()
        manager = self.scope['CETTManager'](model)
        x = torch.tensor([[[-1., 2., 3.], [2., -2., 1.]]])
        y = model(x)
        expected = cett(x, y.norm(dim=-1, keepdim=True), model.down_proj.weight.norm(dim=0).unsqueeze(0))
        torch.testing.assert_close(manager.get_cett_tensor(), expected)
        manager.clear()
        self.assertEqual(manager.activations, [])
        self.assertEqual(manager.output_norms, [])
        for hook in manager.hooks: hook.remove()

    def region(self, tokens, answer):
        class Tokenizer:
            def decode(self, ids): return tokens[int(ids[0])]
            def apply_chat_template(self, *args, **kw): return torch.zeros((1, 3), dtype=torch.long)
        return self.scope['get_region_indices'](torch.arange(len(tokens)).unsqueeze(0), Tokenizer(), 'Q', 'unused', answer)

    def test_regions_first_match_normalization_and_boundaries(self):
        tokens = ['<s>', 'Q', '<assistant>', ' yes', ' yes', '</s>']
        regions = self.region(tokens, ['Ġyes'])
        self.assertEqual(regions, {'input': (0, 2), 'output': (3, 5), 'answer_tokens': (3, 4)})
        self.assertEqual(self.region(tokens, ['▁yes'])['answer_tokens'], (3, 4))
        self.assertIsNone(self.region(tokens, ['yes'])['answer_tokens'])
        self.assertIsNone(self.region(tokens, [])['answer_tokens'])
        # Source search includes EOS even though output slice excludes it.
        self.assertEqual(self.region(tokens, ['</s>'])['answer_tokens'], (5, 6))

    def test_complement_includes_prompt_and_eos(self):
        values = torch.tensor([[[100.], [200.], [300.], [4.], [5.], [600.]]])
        self.assertEqual(aggregate_region(values, (3, 4), complement=True).item(), 241.)
        self.assertEqual(aggregate_region(values, (3, 4), complement=True, method='max').item(), 600.)
        self.assertEqual(aggregate_region(values, (3, 5)).item(), 4.5)

    def test_exact_upstream_region_loop_missing_answer_stale_reuse(self):
        # Execute the unmodified location loop, not model/tokenizer/network code.
        main = next(n for n in self.tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
        loop = next(n for n in ast.walk(main) if isinstance(n, ast.For) and isinstance(n.target, ast.Name) and n.target.id == 'loc' and any(isinstance(k, ast.Assign) for k in n.body))
        def run(regions, previous=None):
            saved = []
            scope = dict(torch=torch, args=SimpleNamespace(locations=['all_except_answer_tokens'], method='mean', output_root='unused'), regions=regions, cett_full=torch.arange(6.).reshape(1, 6, 1), qid='fixture', os=SimpleNamespace(path=SimpleNamespace(join=lambda *x: '/'.join(x))), np=SimpleNamespace(save=lambda path, value: saved.append(value)))
            if previous is not None: scope['selected_cett'] = previous
            exec(compile(ast.Module(body=[loop], type_ignores=[]), str(self.path), 'exec'), scope)
            return saved[0]
        self.assertAlmostEqual(float(run({'answer_tokens': (3, 4)})[0, 0]), 2.4, places=6)
        with self.assertRaises(NameError): run({'answer_tokens': None})
        # Same upstream scope retains a preceding sample/location's selected tensor.
        self.assertEqual(float(run({'answer_tokens': None}, torch.full((1, 2, 1), 99.))[0, 0]), 99.)
        with self.assertRaises(Invalid): aggregate_region(torch.ones(1, 6, 1), None, complement=True)

    def test_invalid_regions_and_empty_complement(self):
        for region, complement in [(None, False), ((1, 1), False), ((0, 7), False), ((0, 6), True)]:
            with self.assertRaises(Invalid): aggregate_region(torch.ones(1, 6, 1), region, complement=complement)

    def test_invalid_cett_norms_shape_and_values(self):
        a = torch.ones(2, 3, 4); w = torch.ones(2, 4)
        for norms in [torch.ones(2, 3, 2), -torch.ones(2, 3, 1), torch.full((2, 3, 1), float('nan'))]:
            with self.assertRaises(Invalid): cett(a, norms, w)
