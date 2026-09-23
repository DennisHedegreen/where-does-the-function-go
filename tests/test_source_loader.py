import ast
import json
import os
from pathlib import Path
import tempfile
import unittest

import numpy as np

from wdfg.source_loader import load_activations
from wdfg.validation import ROOT, Invalid
from wdfg.m1 import verify_upstream


class SourceLoaderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.answer = self.root / 'answer'
        self.other = self.root / 'other'
        self.answer.mkdir(); self.other.mkdir()
        self.ids = {'f': [2, 1], 't': [3]}
        self.ids_path = self.root / 'ids.json'
        self.ids_path.write_text(json.dumps(self.ids))
        for region, offset in [(self.answer, 0), (self.other, 100)]:
            for i in [1, 2, 3]:
                np.save(region / f'act_{i}.npy', np.asfortranarray(np.arange(6).reshape(2, 3) + i * 10 + offset))

    def load(self, mode='3-vs-1'):
        return load_activations(self.ids, self.answer, self.other, mode=mode, expected_shape=(2, 3))

    def upstream(self, mode):
        verify_upstream()
        path = ROOT / 'upstream/h-neurons/scripts/classifier.py'
        node = next(n for n in ast.parse(path.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'load_data')
        scope = {'np': np, 'os': os, 'json': json, 'tqdm': lambda rows, **kw: rows}
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), scope)
        return scope['load_data'](self.ids_path, self.answer, self.other, mode)

    def test_exact_pinned_source_equivalence_both_modes(self):
        for mode in ['1-vs-1', '3-vs-1']:
            with self.subTest(mode=mode):
                x, y, receipt = self.load(mode)
                sx, sy = self.upstream(mode)
                np.testing.assert_array_equal(x, sx)
                np.testing.assert_array_equal(y, sy)
                self.assertEqual(x[0].tolist(), [20, 21, 22, 23, 24, 25])
                self.assertEqual(receipt['scientific_status'], 'NOT_EVALUATED')
        self.assertEqual(y.tolist(), [1, 1, 0, 0, 0, 0])
        self.assertEqual([(r['region'], r['example_id']) for r in receipt['records']],
                         [('answer', '2'), ('answer', '1'), ('answer', '3'), ('other', '3'), ('other', '2'), ('other', '1')])

    def test_missing_files_refused_where_upstream_silently_shrinks(self):
        (self.answer / 'act_2.npy').unlink()
        (self.other / 'act_3.npy').unlink()
        self.assertEqual(len(self.upstream('3-vs-1')[0]), 4)
        with self.assertRaisesRegex(Invalid, 'answer/act_2.npy.*other/act_3.npy'):
            self.load()

    def test_shape_nonfinite_and_object_refused(self):
        for matrix in [np.zeros((3, 2)), np.full((2, 3), np.nan), np.ones((2, 3), dtype=object), np.ones((2, 3), dtype=complex)]:
            np.save(self.answer / 'act_2.npy', matrix)
            with self.assertRaises(Invalid): self.load()

    def test_duplicate_overlap_and_path_ids_refused(self):
        for ids in [{'f': [2, '2'], 't': [3]}, {'f': [2], 't': [2]}, {'f': ['../2'], 't': [3]}, {'f': [], 't': [3]}]:
            self.ids = ids
            with self.assertRaises(Invalid): self.load()

    def test_mode_and_region_alias_refused(self):
        with self.assertRaises(Invalid): self.load('typo')
        with self.assertRaises(Invalid):
            load_activations(self.ids, self.answer, self.answer, mode='3-vs-1', expected_shape=(2, 3))
        with self.assertRaises(Invalid):
            load_activations(self.ids, self.answer, mode='3-vs-1', expected_shape=(2, 3))

    def test_receipt_binds_content_order_and_mode(self):
        original = self.load()[2]['audit_sha256']
        self.assertEqual(original, self.load()[2]['audit_sha256'])
        np.save(self.answer / 'act_2.npy', np.ones((2, 3)))
        changed = self.load()[2]['audit_sha256']
        self.assertNotEqual(original, changed)
        self.ids['f'].reverse()
        self.assertNotEqual(changed, self.load()[2]['audit_sha256'])
        self.assertNotEqual(self.load()[2]['audit_sha256'], self.load('1-vs-1')[2]['audit_sha256'])

    def test_symlink_escape_refused(self):
        path = self.answer / 'act_2.npy'
        path.unlink(); path.symlink_to(self.other / 'act_2.npy')
        with self.assertRaises(Invalid): self.load()
