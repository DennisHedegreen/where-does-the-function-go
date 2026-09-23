import ast
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
import numpy as np
from wdfg.validation import ROOT, Invalid, read_json
from wdfg.m1 import gate0, dataset_fingerprint, normalize_h_neurons, verify_upstream

ROOT = Path(__file__).resolve().parents[1]

class M1Tests(unittest.TestCase):
 def setUp(self):self.e=read_json(ROOT/'fixtures/gate0-pass.json')
 def test_exact_gate_boundaries_pass(self):
  r=gate0(self.e);self.assertEqual(r['fixture_gate_outcome'],'PASS');self.assertEqual(r['scientific_status'],'NOT_EVALUATED');self.assertFalse(r['execution_authorized'])
 def test_thresholds_and_ood(self):
  for category,key,value,gate in [('triviaqa','h_accuracy',.679,'G0_A'),('faith_eval','h_compliance',.751,'G0_B'),('faith_eval','matched_compliance',.779,'G0_C'),('nq_open','h_accuracy',.60,'G0_A')]:
   with self.subTest(key=key):
    e=copy.deepcopy(self.e);e[category][key]=value;self.assertEqual(gate0(e)['gates'][gate],'FAIL')
 def test_ci_touching_zero(self):
  for name,key,gate in [('triviaqa','paired_ci','G0_A'),('faith_eval','selectivity_ci','G0_C')]:
   e=copy.deepcopy(self.e);e[name][key]['low']=0;self.assertEqual(gate0(e)['gates'][gate],'FAIL')
 def test_damage_boundary(self):
  self.e['ppl']['h']=11;self.assertEqual(gate0(self.e)['fixture_gate_outcome'],'FAIL')
  self.e['ppl']['h']=11.01;self.assertEqual(gate0(self.e)['fixture_gate_outcome'],'AMBIGUOUS')
 def test_missing_controls_and_wrong_ci(self):
  e=copy.deepcopy(self.e);del e['faith_eval']['matched_compliance']
  with self.assertRaises(Invalid):gate0(e)
  self.e['triviaqa']['paired_ci']['method']='independent'
  with self.assertRaises(Invalid):gate0(self.e)
 def test_nan_and_empirical_refused(self):
  self.e['ppl']['h']=float('nan')
  with self.assertRaises(Invalid):gate0(self.e)
  self.e=read_json(ROOT/'fixtures/gate0-pass.json');self.e['run_kind']='result'
  with self.assertRaises(Invalid):gate0(self.e)
 def rows(self):return [dict(example_id='a',split='train',prompt='question a',parameters={'n':1},ground_truth='yes'),dict(example_id='b',split='test',prompt='question b',parameters={},ground_truth='no')]
 def test_fingerprint_order_and_content(self):
  rows=self.rows();original=dataset_fingerprint(rows,'nfc-crlf-v1')['sha256'];self.assertEqual(original,dataset_fingerprint(rows[::-1],'nfc-crlf-v1')['sha256'])
  for field,value in [('prompt','modified'),('parameters',{'n':2}),('ground_truth','changed'),('split','validation')]:
   r=self.rows();r[0][field]=value;self.assertNotEqual(original,dataset_fingerprint(r,'nfc-crlf-v1')['sha256'])
  self.assertNotEqual(original,dataset_fingerprint(rows,'v2')['sha256'])
 def test_split_leakage(self):
  rows=self.rows();rows[1]['example_id']='a'
  with self.assertRaises(Invalid):dataset_fingerprint(rows,'v1')
  rows=self.rows();rows[1]['prompt']=rows[0]['prompt']
  with self.assertRaises(Invalid):dataset_fingerprint(rows,'v1')
 def test_unicode_and_crlf(self):
  rows=self.rows();rows[0]['prompt']='caf\u00e9\n';a=dataset_fingerprint(rows,'v1');rows[0]['prompt']='cafe\u0301\r\n';self.assertEqual(a,dataset_fingerprint(rows,'v1'))
 def test_adapter_and_upstream_coordinate_equivalence(self):
  lock=verify_upstream();weights=[-.5,0,.001,.0011,.5,.0005]
  result=normalize_h_neurons('x','train',[[1.,2.,3.],[4.,5.,6.]],weights,source_commit=lock['commit'],threshold=.001)
  # Execute only the reviewed, pinned coordinate function; no torch imports or model loading.
  path=ROOT/'wdfg/resources/upstream/h-neurons/scripts/intervene_model.py'
  node=next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='get_h_neuron_indices')
  scope={'np':np};exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),scope)
  expected=scope['get_h_neuron_indices'](SimpleNamespace(coef_=np.array([weights])),SimpleNamespace(intermediate_size=3))
  mapped={}
  for r in result['records']:
   if r['upstream_positive']:mapped.setdefault(r['layer_index'],[]).append(r['neuron_index'])
  self.assertEqual(mapped,expected)
  self.assertEqual([(r['layer_index'],r['neuron_index']) for r in result['records'] if r['is_h_neuron']],[(1,0),(1,1)])
 def test_adapter_bad_shape_and_commit(self):
  commit=verify_upstream()['commit']
  for cett,weights,source in [([[1],[2,3]],[1,2,3],commit),([[1]],[float('nan')],commit),([[1]],[1],'bad')]:
   with self.assertRaises(Invalid):normalize_h_neurons('x','test',cett,weights,source_commit=source,threshold=.001)
